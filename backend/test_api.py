"""Test API Keys - Debug"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=== CHECKING API KEYS ===")
print(f"OPENAI_API_KEY exists: {bool(os.getenv('OPENAI_API_KEY'))}")
print(f"GEMINI_API_KEY exists: {bool(os.getenv('GEMINI_API_KEY'))}")

# Test Gemini - list models
print("\n=== LIST GEMINI MODELS ===")
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

    for m in genai.list_models():
        print(f"- {m.name}")
        if 'generateContent' in m.supported_generation_methods:
            print(f"  Supports generateContent")
            break
except Exception as e:
    print(f"Error: {e}")

# Test OpenAI
print("\n=== TEST OPENAI ===")
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    # Just try to list models
    models = client.models.list()
    print(f"OpenAI connected, {len(models.data)} models available")
except Exception as e:
    print(f"OpenAI Error: {e}")