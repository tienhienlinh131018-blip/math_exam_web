import os
from google import genai

api_key = "YOUR_API_KEY_HERE"
client = genai.Client(api_key=api_key)

models_to_test = ['gemini-2.5-flash', 'gemini-3-flash-preview', 'gemini-flash-latest']

for model in models_to_test:
    try:
        print(f"Testing {model}...")
        response = client.models.generate_content(
            model=model,
            contents='Chào bạn'
        )
        print("Response:", response.text[:50])
    except Exception as e:
        print(f"Error {model}:", str(e))
