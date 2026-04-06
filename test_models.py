import requests
api_key = "AIzaSyBPbJVwkThTqbn5pjcmKdtOLdR_dbUlj5Q"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)
models = response.json().get('models', [])
for m in models:
    if 'flash' in m['name']:
        print(m['name'])
