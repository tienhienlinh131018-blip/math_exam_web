import requests

url = "http://127.0.0.1:5000/api/generate"
# Note: Since the endpoint has `if not session.get('logged_in'): return jsonify({'error': 'Unauthorized'}), 401`, 
# we need to login first.
session = requests.Session()
login_res = session.post("http://127.0.0.1:5000/login", data={"username": "admin", "password": "admin123"})
print("Login status:", login_res.status_code)

res = session.post(url, json={
    "grade": "3",
    "semester": "1",
    "chapter": "Ôn tập và bổ sung",
    "lesson": "Ôn tập các số đến 1000",
    "test_type": "lesson",
    "count": 3
})

print("Status:", res.status_code)
print("Response:", res.text)
