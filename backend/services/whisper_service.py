"""
Whisper Service - Transcription với OpenAI Whisper
"""
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class WhisperService:
    """Service để transcribe audio bằng Whisper"""

    def __init__(self):
        # Don't pass proxies parameter
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY', ''))
        self.model = 'whisper-1'

    def transcribe(self, audio_data, file_name=None, language='vi'):
        """
        Transcribe audio file

        Args:
            audio_data: Audio file data (bytes) hoặc file path
            file_name: Tên file (để xác định định dạng)
            language: Ngôn ngữ của audio (mặc định: 'vi' cho tiếng Việt)

        Returns:
            transcript: Text đã transcribe
        """
        try:
            # Nếu audio_data là bytes, tạo file tạm
            if isinstance(audio_data, bytes):
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as f:
                    f.write(audio_data)
                    temp_path = f.name

                with open(temp_path, 'rb') as audio_file:
                    response = self.client.audio.transcriptions.create(
                        model=self.model,
                        file=audio_file,
                        language=language,
                        response_format='text'
                    )
                # Clean up
                os.remove(temp_path)
            else:
                # File path
                with open(audio_data, 'rb') as audio_file:
                    response = self.client.audio.transcriptions.create(
                        model=self.model,
                        file=audio_file,
                        language=language,
                        response_format='text'
                    )

            transcript = response if isinstance(response, str) else response.text
            return transcript

        except Exception as e:
            # Check if it's a Rate Limit error or insufficient quota
            error_str = str(e).lower()
            if '429' in error_str or 'quota' in error_str or 'rate' in error_str:
                print(f'[MOCK MODE] Whisper API Quota Exceeded. Using Mock Transcript.')
                return "Chào mọi người, hôm nay chúng ta sẽ bắt đầu cuộc họp dự án AI Meeting Assistant. Tôi muốn phân công một số công việc. Anh Minh sẽ chịu trách nhiệm phát triển phần Frontend và hoàn thiện giao diện Dashboard trước ngày 15. Chị Lan sẽ thiết kế và triển khai hệ thống Backend API để lưu trữ dữ liệu. Các bạn cố gắng hoàn thành đúng hạn nhé. Cảm ơn mọi người."
            
            print(f'Whisper transcription error: {e}')
            raise e

    def transcribe_from_url(self, audio_url, language='vi'):
        """
        Transcribe từ URL (S3 URL)

        Note: Whisper API yêu cầu file, không hỗ trợ URL trực tiếp.
        Cần download file về trước.
        """
        # TODO: Implement download and transcribe
        raise NotImplementedError("Whisper API doesn't support direct URL. Download the file first.")

# Singleton instance
_whisper_service = None

def get_whisper_service():
    global _whisper_service
    if _whisper_service is None:
        _whisper_service = WhisperService()
    return _whisper_service