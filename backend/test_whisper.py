"""Test Whisper - Debug proxies issue"""
import os
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

from dotenv import load_dotenv
load_dotenv()

print("=== TEST WHISPER ===")
try:
    from openai import OpenAI
    # Clear any proxy settings
    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        http_client=None
    )

    # Try transcription
    print("Client created successfully")

    # Test with a small audio file if exists
    import glob
    audio_files = glob.glob('/tmp/*.webm') + glob.glob('*.webm')
    if audio_files:
        print(f"Found audio file: {audio_files[0]}")
    else:
        print("No audio files found")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()