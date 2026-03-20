"""Quick test script for auth endpoints."""
import requests
import json

BASE = "http://localhost:8000/api/auth"

def test_auth():
    print("=" * 60)
    print("TEST 1: Register a new user")
    print("=" * 60)
    r = requests.post(f"{BASE}/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "Test@12345"
    })
    print(f"Status: {r.status_code}")
    data = r.json()
    print(json.dumps(data, indent=2)[:500])
    
    if r.status_code == 201:
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]
    else:
        print("Registration failed, trying login instead...")
        r = requests.post(f"{BASE}/login", json={
            "email": "test@example.com",
            "password": "Test@12345"
        })
        print(f"Login Status: {r.status_code}")
        data = r.json()
        print(json.dumps(data, indent=2)[:500])
        access_token = data.get("access_token", "")
        refresh_token = data.get("refresh_token", "")

    print("\n" + "=" * 60)
    print("TEST 2: Login with admin account")
    print("=" * 60)
    r = requests.post(f"{BASE}/login", json={
        "email": "admin@dataanalyst.com",
        "password": "Admin@123"
    })
    print(f"Status: {r.status_code}")
    admin_data = r.json()
    print(json.dumps(admin_data, indent=2)[:500])
    admin_token = admin_data.get("access_token", "")

    print("\n" + "=" * 60)
    print("TEST 3: Get profile (GET /me)")
    print("=" * 60)
    r = requests.get(f"{BASE}/me", headers={"Authorization": f"Bearer {access_token}"})
    print(f"Status: {r.status_code}")
    print(json.dumps(r.json(), indent=2))

    print("\n" + "=" * 60)
    print("TEST 4: Admin list users")
    print("=" * 60)
    r = requests.get(f"{BASE}/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    print(f"Status: {r.status_code}")
    print(json.dumps(r.json(), indent=2)[:800])

    print("\n" + "=" * 60)
    print("TEST 5: Refresh token")
    print("=" * 60)
    r = requests.post(f"{BASE}/refresh", json={"refresh_token": refresh_token})
    print(f"Status: {r.status_code}")
    print(f"Got new tokens: {'access_token' in r.json()}")

    print("\n" + "=" * 60)
    print("TEST 6: Access without token (should fail)")
    print("=" * 60)
    r = requests.get(f"{BASE}/me")
    print(f"Status: {r.status_code} (expected 401)")
    print(json.dumps(r.json(), indent=2))

    print("\n" + "=" * 60)
    print("TEST 7: Logout")
    print("=" * 60)
    r = requests.post(f"{BASE}/logout", json={"refresh_token": refresh_token})
    print(f"Status: {r.status_code}")
    print(json.dumps(r.json(), indent=2))

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_auth()
