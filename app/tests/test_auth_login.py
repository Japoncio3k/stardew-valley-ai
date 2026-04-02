from fastapi.testclient import TestClient

from app.mock import db
from app.tests.conftest import VALID_USER


def _register(client: TestClient) -> None:
    client.post("/users/", json=VALID_USER)


def test_login_valid_credentials(client: TestClient) -> None:
    _register(client)
    response = client.post("/auth/login", json={"email": VALID_USER["email"], "password": VALID_USER["password"]})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_email_not_registered(client: TestClient) -> None:
    response = client.post("/auth/login", json={"email": "notregistered@example.com", "password": "Str0ng!Pass"})
    assert response.status_code == 401
    assert "credential" in response.json()["detail"].lower() or "invalid" in response.json()["detail"].lower()


def test_login_wrong_password(client: TestClient) -> None:
    _register(client)
    response = client.post("/auth/login", json={"email": VALID_USER["email"], "password": "Wrong!Pass1"})
    assert response.status_code == 401


def test_login_missing_required_field(client: TestClient) -> None:
    response = client.post("/auth/login", json={"email": VALID_USER["email"]})
    assert response.status_code == 422


def test_login_account_locked(client: TestClient) -> None:
    from app.main import app

    _register(client)
    # Trigger 5 failed attempts to lock the IP
    for _ in range(5):
        client.post("/auth/login", json={"email": VALID_USER["email"], "password": "WrongPass!1"})

    # Reset the rate limiter so we can verify the 423 response (the 6th request
    # would be rate-limited otherwise, since the login limit is 5/minute)
    limiter = app.state.limiter
    if hasattr(limiter, "_storage") and hasattr(limiter._storage, "reset"):
        limiter._storage.reset()

    # Now the IP should be locked
    response = client.post("/auth/login", json={"email": VALID_USER["email"], "password": VALID_USER["password"]})
    assert response.status_code == 423
    assert "locked" in response.json()["detail"].lower()


def test_login_failed_attempts_reach_threshold(client: TestClient) -> None:
    _register(client)
    for _ in range(5):
        client.post("/auth/login", json={"email": VALID_USER["email"], "password": "WrongPass!1"})

    ip = "testclient"
    record = db.brute_force.get(ip)
    assert record is not None
    assert record.get("locked_until") is not None


def test_login_success_resets_failed_attempts(client: TestClient) -> None:
    _register(client)
    # Do a couple of failed attempts
    for _ in range(2):
        client.post("/auth/login", json={"email": VALID_USER["email"], "password": "WrongPass!1"})

    # Successful login
    response = client.post("/auth/login", json={"email": VALID_USER["email"], "password": VALID_USER["password"]})
    assert response.status_code == 200

    ip = "testclient"
    record = db.brute_force.get(ip)
    assert record is None or record.get("failed_attempts") == 0


def test_login_response_does_not_include_password(client: TestClient) -> None:
    _register(client)
    response = client.post("/auth/login", json={"email": VALID_USER["email"], "password": VALID_USER["password"]})
    assert response.status_code == 200
    data = response.json()
    assert "password" not in data
    assert "hashed_password" not in data


def test_login_rate_limit(client: TestClient) -> None:
    _register(client)
    # Make 5 requests
    for _ in range(5):
        client.post("/auth/login", json={"email": VALID_USER["email"], "password": VALID_USER["password"]})

    # 6th request should be rate limited
    response = client.post("/auth/login", json={"email": VALID_USER["email"], "password": VALID_USER["password"]})
    assert response.status_code == 429
