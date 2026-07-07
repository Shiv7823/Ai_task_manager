"""
Basic integration tests for AI Task Manager API.
Run with: pytest tests/ -v
Requires a running MySQL instance with credentials from .env
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ── Helpers ──────────────────────────────────────────────────────────────────

def register_and_login(username="testuser", password="testpass123"):
    client.post("/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": password
    })
    resp = client.post("/auth/login", data={"username": username, "password": password})
    return resp.json().get("access_token")

def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

# ── Auth Tests ────────────────────────────────────────────────────────────────

def test_register_success():
    resp = client.post("/auth/register", json={
        "username": "newuser1",
        "email": "newuser1@test.com",
        "password": "password123"
    })
    assert resp.status_code == 201
    assert resp.json()["username"] == "newuser1"

def test_register_duplicate_username():
    client.post("/auth/register", json={
        "username": "dupuser", "email": "dup1@test.com", "password": "pass123"
    })
    resp = client.post("/auth/register", json={
        "username": "dupuser", "email": "dup2@test.com", "password": "pass123"
    })
    assert resp.status_code == 400

def test_login_success():
    client.post("/auth/register", json={
        "username": "logintest", "email": "logintest@test.com", "password": "pass123"
    })
    resp = client.post("/auth/login", data={"username": "logintest", "password": "pass123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()

def test_login_invalid_credentials():
    resp = client.post("/auth/login", data={"username": "nobody", "password": "wrong"})
    assert resp.status_code == 401

# ── Task Tests ────────────────────────────────────────────────────────────────

def test_create_task():
    token = register_and_login("taskuser1", "pass123")
    resp = client.post("/tasks/", json={
        "title": "Write unit tests",
        "priority": "high",
        "status": "todo"
    }, headers=auth_headers(token))
    assert resp.status_code == 201
    assert resp.json()["title"] == "Write unit tests"

def test_list_tasks():
    token = register_and_login("taskuser2", "pass123")
    client.post("/tasks/", json={"title": "Task A"}, headers=auth_headers(token))
    client.post("/tasks/", json={"title": "Task B"}, headers=auth_headers(token))
    resp = client.get("/tasks/", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["total"] >= 2

def test_get_task_not_found():
    token = register_and_login("taskuser3", "pass123")
    resp = client.get("/tasks/99999", headers=auth_headers(token))
    assert resp.status_code == 404

def test_update_task():
    token = register_and_login("taskuser4", "pass123")
    create_resp = client.post("/tasks/", json={"title": "Old Title"}, headers=auth_headers(token))
    task_id = create_resp.json()["id"]
    resp = client.put(f"/tasks/{task_id}", json={"title": "Updated Title", "status": "in_progress"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"

def test_delete_task():
    token = register_and_login("taskuser5", "pass123")
    create_resp = client.post("/tasks/", json={"title": "To Delete"}, headers=auth_headers(token))
    task_id = create_resp.json()["id"]
    resp = client.delete(f"/tasks/{task_id}", headers=auth_headers(token))
    assert resp.status_code == 204

def test_unauthorized_access():
    resp = client.get("/tasks/")
    assert resp.status_code == 401

def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
