import requests
import json

base_url = "http://localhost:8000"

print("1. Registering user...")
res = requests.post(f"{base_url}/api/auth/register", json={
    "email": "test-ai-token@example.com",
    "username": "testaitoken",
    "password": "password123"
})
if res.status_code == 400:
    print("User already exists, trying to login...")
    res = requests.post(f"{base_url}/api/auth/login", json={
        "email": "test-ai-token@example.com",
        "password": "password123"
    })

data = res.json()
token = data.get("access_token")
print("Token:", token)

print("2. Testing /api/auth/me...")
me_res = requests.get(f"{base_url}/api/auth/me", headers={"Authorization": f"Bearer {token}"})
print("Me status:", me_res.status_code)
print("Me response:", me_res.text)

print("3. Testing /api/ai/query...")
ai_res = requests.post(f"{base_url}/api/ai/query", headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, json={
    "question": "test",
    "experiments": []
})
print("AI status:", ai_res.status_code)
print("AI response:", ai_res.text)
