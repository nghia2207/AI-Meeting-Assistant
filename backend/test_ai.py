"""Test AI Services - Chạy trực tiếp để debug"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
from dotenv import load_dotenv
load_dotenv()

# Test Gemini
print("=== TESTING GEMINI ===")
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.5-flash')

    test_text = """Cuoc hop hom nay thao luan ve du an ABC.
Anh Minh se hoan thanh phan UI truoc ngay 25.
Chi Lan phu trach tich hop API."""

    prompt = f"""Tu noi dung cuoc hop duoi day, hay trich xuat tat ca cac cong viec.
Tra ve JSON array voi cac truong: taskName, assignee, deadline.

Noi dung:
{test_text}

JSON:"""

    response = model.generate_content(prompt)
    print(f"Response: {response.text}")
    print("=== GEMINI SUCCESS ===")
except Exception as e:
    print(f"=== GEMINI ERROR: {e} ===")

# Test Whisper
print("\n=== TESTING WHISPER ===")
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    print("=== WHISPER SUCCESS ===")
except Exception as e:
    print(f"=== WHISPER ERROR: {e} ===")