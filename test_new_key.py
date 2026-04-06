import os
from google import genai

api_key = "AIzaSyBPbJVwkThTqbn5pjcmKdtOLdR_dbUlj5Q"

try:
    print("Testing gemini-1.5-flash...")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents='Chào bạn'
    )
    print("Response 1.5:", response.text[:50])
except Exception as e:
    print("Error 1.5:", str(e))

try:
    print("Testing gemini-2.0-flash...")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents='Chào bạn'
    )
    print("Response 2.0:", response.text[:50])
except Exception as e:
    print("Error 2.0:", str(e))
