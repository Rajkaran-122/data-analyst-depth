import requests
import json
import io
import os
import sys

BASE_URL = "http://localhost:8000/api"

def print_step(msg):
    print(f"\n[{'='*40}]\n{msg}\n[{'='*40}]")

def register_user(name, email, password):
    r = requests.post(f"{BASE_URL}/auth/register", json={
        "name": name,
        "email": email,
        "password": password
    })
    if r.status_code == 201:
        return r.json()["access_token"]
    elif r.status_code == 409:
        # Already exists, just login
        r = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        return r.json()["access_token"]
    else:
        print(f"Failed to register/login {email}: {r.json()}")
        sys.exit(1)

def run_tests():
    # 1. Setup multi-user auth
    print_step("Setting up Test Users")
    token_a = register_user("User A", "userA@test.com", "TestUserA@123")
    token_b = register_user("User B", "userB@test.com", "TestUserB@123")
    
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    print("Tokens acquired successfully.")

    # 2. Upload dataset as User A
    print_step("Uploading Dataset as User A")
    csv_content = b"id,name,value\n1,Alpha,100\n2,Beta,\n3,Gamma,300"
    files = {'file': ('test_data.csv', csv_content, 'text/csv')}
    r = requests.post(f"{BASE_URL}/datasets", files=files, headers=headers_a)
    assert r.status_code == 200, f"Upload failed: {r.text}"
    
    dataset_data = r.json()["dataset"]
    ds_id = dataset_data["id"]
    print(f"Dataset '{dataset_data['name']}' uploaded successfully. ID: {ds_id}")
    
    # 3. Verify Advanced Schema (Null % and Sample Values)
    print_step("Verifying Advanced Schema Generation")
    columns = dataset_data["columns"]
    print(json.dumps(columns, indent=2))
    value_col = next(c for c in columns if c["name"] == "value")
    assert value_col["null_percentage"] > 0, "Null percentage was not calculated correctly"
    assert "100.0" in value_col["sample_values"], "Sample values are missing"
    print("Schema checks passed.")

    # 4. Multi-User Isolation Check (User B tries to access)
    print_step("Testing Multi-User Data Isolation")
    r = requests.get(f"{BASE_URL}/datasets/{ds_id}", headers=headers_b)
    assert r.status_code == 404, "User B should not be able to access User A's dataset!"
    
    r_list = requests.get(f"{BASE_URL}/datasets", headers=headers_b)
    assert len(r_list.json()["datasets"]) == 0, "User B should see 0 datasets"
    print("Data isolation working correctly.")

    # 5. Rename Workflow
    print_step("Testing Dataset Renaming")
    r = requests.patch(f"{BASE_URL}/datasets/{ds_id}", data={"name": "New Name Data"}, headers=headers_a)
    assert r.status_code == 200, "Rename failed"
    assert r.json()["dataset"]["name"] == "New Name Data", "Name was not updated"
    
    # Check duplicate name validation
    files = {'file': ('another.csv', b"a,b\n1,2", 'text/csv')}
    r2 = requests.post(f"{BASE_URL}/datasets", files=files, headers=headers_a)
    ds_id2 = r2.json()["dataset"]["id"]
    
    r3 = requests.patch(f"{BASE_URL}/datasets/{ds_id2}", data={"name": "New Name Data"}, headers=headers_a)
    assert r3.status_code == 409, "Should block renaming to an existing dataset name"
    print("Rename and collision detection working.")

    # 6. Preview rows limit
    print_step("Testing Preview Pagination")
    r = requests.get(f"{BASE_URL}/datasets/{ds_id}/preview?rows=2", headers=headers_a)
    assert r.status_code == 200, "Preview failed"
    preview_data = r.json()["preview"]
    assert len(preview_data) == 2, f"Expected 2 rows, got {len(preview_data)}"
    print("Preview limits working.")

    # 7. File Size Validation Check
    print_step("Testing 50MB Size Validation Limit")
    # Generates a pseudo 51MB string in memory
    large_content = b"a" * (51 * 1024 * 1024)
    files = {'file': ('large.csv', large_content, 'text/csv')}
    r = requests.post(f"{BASE_URL}/datasets", files=files, headers=headers_a)
    assert r.status_code == 400, f"Expected 400 Bad Request, got {r.status_code}"
    print(r.json()["detail"])
    print("Size limit caught successfully.")

    # 8. Deletion
    print_step("Testing Dataset Deletion")
    r = requests.delete(f"{BASE_URL}/datasets/{ds_id}", headers=headers_a)
    assert r.status_code == 200, "Deletion failed"
    r = requests.get(f"{BASE_URL}/datasets/{ds_id}", headers=headers_a)
    assert r.status_code == 404, "Dataset still exists after deletion"
    
    requests.delete(f"{BASE_URL}/datasets/{ds_id2}", headers=headers_a)
    print("Deletion working correctly.")

    print_step("All Tests Passed! ✅")

if __name__ == "__main__":
    run_tests()
