import requests

try:
    response = requests.post(
        "http://localhost:8000/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
    )
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)
except Exception as e:
    print("Request failed:", e)
