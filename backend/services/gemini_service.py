"""
Gemini Service - Summarization và Task Extraction với Google Gemini
"""
import google.generativeai as genai
import os
import re
import time
from dotenv import load_dotenv

# Load .env from backend directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))


def mask_sensitive_data(text):
    """
    Anonymize participant names in text before sending to AI
    Replaces common Vietnamese names with [Person 1], [Person 2], etc.
    """
    # Common Vietnamese name patterns
    vietnamese_names = [
        r'\bAnh\s+[A-ZÀÁẠẢÃÂẦẤẪẬẮẰẲẴẶÈÉẸẺẼÊỀẾỄỆÌÍỊỈĨÒÓỌỎÕÔỐỘỖỚỜỞỠỢÙÚỤỦŨƯỨỪỬỮỰỲÝỴỶỸ][a-zàáạảãâầấẫậắằẳẵặèéẹẻẽêềếễệìíịỉĩòóọỏõôốộỗớờởỡợùúụủũưừứừửữựỳýỵỷỹ]+\b',
        r'\bChị\s+[A-ZÀÁẠẢÃÂẦẤẪẬẮẰẲẴẶÈÉẸẺẼÊỀẾỄỆÌÍỊỈĨÒÓỌỎÕÔỐỘỖỚỜỞỠỢÙÚỤỦŨƯỨỪỬỮỰỲÝỴỶỸ][a-zàáạảãâầấẫậắằẳẵặèéẹẻẽêềếễệìíịỉĩòóọỏõôốộỗớờởỡợùúụủũưừứừửữựỳýỵỷỹ]+\b',
        r'\bÔng\s+[A-ZÀÁẠẢÃÂẦẤẪẬẮẰẲẴẶÈÉẸẺẼÊỀẾỄỆÌÍỊỈĨÒÓỌỎÕÔỐỘỖỚỜỞỠỢÙÚỤỦŨƯỨỪỬỮỰỲÝỴỶỸ][a-zàáạảãâầấẫậắằẳẵặèéẹẻẽêềếễệìíịỉĩòóọỏõôốộỗớờởỡợùúụủũưừứừửữựỳýỵỷỹ]+\b',
        r'\bBà\s+[A-ZÀÁẠẢÃÂẦẤẪẬẮẰẲẴẶÈÉẸẺẼÊỀẾỄỆÌÍỊỈĨÒÓỌỎÕÔỐỘỖỚỜỞỠỢÙÚỤỦŨƯỨỪỬỮỰỲÝỴỶỸ][a-zàáạảãâầấẫậắằẳẵặèéẹẻẽêềếễệìíịỉĩòóọỏõôốộỗớờởỡợùúụủũưừứừửữựỳýỵỷỹ]+\b',
    ]

    # Find all names and replace with [Person N]
    person_map = {}
    person_counter = 1

    for pattern in vietnamese_names:
        matches = re.finditer(pattern, text)
        for match in matches:
            name = match.group()
            if name not in person_map:
                person_map[name] = f"[Person {person_counter}]"
                person_counter += 1

    # Replace all names
    for name, masked in person_map.items():
        text = text.replace(name, masked)

    return text

class GeminiService:
    """Service để summarize và extract tasks bằng Gemini"""

    def __init__(self):
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def _call_with_retry(self, prompt, max_retries=3):
        """Call Gemini API with automatic retry on rate limit (free tier: 5 req/min)"""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response
            except Exception as e:
                error_str = str(e).lower()
                if 'rate' in error_str or 'quota' in error_str or '429' in error_str or 'resource_exhausted' in error_str:
                    wait_time = 15 * (attempt + 1)  # 15s, 30s, 45s
                    print(f'[Gemini] Rate limit hit, waiting {wait_time}s before retry ({attempt+1}/{max_retries})...')
                    time.sleep(wait_time)
                else:
                    raise e
        raise Exception('Gemini API rate limit exceeded after retries. Please wait 1 minute and try again.')

    def summarize(self, transcript, language='vi'):
        """
        Tạo summary từ transcript

        Args:
            transcript: Text đã transcribe
            language: Ngôn ngữ (mặc định: 'vi')

        Returns:
            summary: Summary text
        """
        try:
            prompt = f"""Bạn là một trợ lý AI chuyên tóm tắt nội dung cuộc họp.

Hãy tóm tắt nội dung cuộc họp sau đây thành một bản tóm tắt ngắn gọn, súc tích.
Trích xuất các điểm chính, quyết định quan trọng (nếu có).

Nội dung cuộc họp:
{transcript}

Bản tóm tắt (bằng {language}):"""

            response = self._call_with_retry(prompt)
            return response.text

        except Exception as e:
            print(f'Gemini summarize error: {e}')
            raise e

    def extract_tasks(self, transcript, language='vi'):
        """
        Trích xuất các công việc/action items từ transcript

        Args:
            transcript: Text đã transcribe
            language: Ngôn ngữ (mặc định: 'vi')

        Returns:
            tasks: List of tasks với format [{'taskName': str, 'assignee': str, 'deadline': str}]
        """
        try:
            prompt = f"""Bạn là một trợ lý AI chuyên trích xuất công việc từ nội dung cuộc họp.

Từ nội dung cuộc họp dưới đây, hãy trích xuất tất cả các công việc/action items được đề cập.
Trả về kết quả theo format JSON array với các trường:
- taskName: Tên công việc
- assignee: Người được giao (nếu có)
- deadline: Thời hạn (nếu có)

Nếu không có công việc nào, trả về empty array.

Nội dung cuộc họp:
{transcript}

Trả về JSON array:"""

            response = self._call_with_retry(prompt)

            # Parse JSON response
            import json
            try:
                text = response.text.strip()
                # Strip markdown code fences (```json ... ```)
                if text.startswith('```'):
                    lines = text.split('\n')
                    end = -1 if lines[-1].strip() == '```' else len(lines)
                    text = '\n'.join(lines[1:end]).strip()
                tasks = json.loads(text)
            except json.JSONDecodeError:
                # Fallback: extract JSON array from text
                json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                if json_match:
                    try:
                        tasks = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        tasks = []
                else:
                    tasks = []

            return tasks

        except Exception as e:
            print(f'Gemini extract tasks error: {e}')
            raise e

    def process_meeting(self, transcript, language='vi', mask_data=True):
        """
        Xử lý toàn bộ meeting: summarize + extract tasks

        Args:
            transcript: Text đã transcribe
            language: Ngôn ngữ (mặc định: 'vi')
            mask_data: Có mask dữ liệu nhạy cảm không (mặc định: True)

        Returns:
            dict: { 'summary': str, 'tasks': list }
        """
        try:
            # Apply data masking for privacy
            if mask_data:
                original_transcript = transcript
                transcript = mask_sensitive_data(transcript)
                print(f'[Data Masking] Replaced sensitive data in transcript')

            summary = self.summarize(transcript, language)

            # Small delay to avoid rate limit on free tier (5 req/min)
            print('[Gemini] Waiting 12s between API calls (free tier rate limit)...')
            time.sleep(12)

            tasks = self.extract_tasks(transcript, language)

            return {
                'summary': summary,
                'tasks': tasks
            }
        except Exception as e:
            print(f'Gemini process meeting error: {e}')
            raise e

# Singleton instance
_gemini_service = None

def get_gemini_service():
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service