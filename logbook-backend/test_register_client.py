from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

response = client.post(
    "/api/auth/register",
    json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    }
)
print("Status Code:", response.status_code)
print("Response Body:", response.text)
