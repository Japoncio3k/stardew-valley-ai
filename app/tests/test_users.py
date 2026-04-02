from fastapi.testclient import TestClient

from app.mock import db
from app.tests.conftest import VALID_USER


def test_register_user_success(client: TestClient) -> None:
    response = client.post("/users/", json=VALID_USER)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == VALID_USER["username"]
    assert data["email"] == VALID_USER["email"]
    assert "id" in data
    # User stored in mock DB
    assert VALID_USER["email"] in db.users


def test_register_user_email_already_registered(client: TestClient) -> None:
    client.post("/users/", json=VALID_USER)
    response = client.post("/users/", json=VALID_USER)
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


def test_register_user_missing_required_field(client: TestClient) -> None:
    response = client.post("/users/", json={"username": "testuser", "email": "test@example.com"})
    assert response.status_code == 422


def test_register_user_invalid_email_format(client: TestClient) -> None:
    payload = {**VALID_USER, "email": "not-an-email"}
    response = client.post("/users/", json=payload)
    assert response.status_code == 422


def test_register_user_password_too_short(client: TestClient) -> None:
    payload = {**VALID_USER, "password": "Ab1!"}
    response = client.post("/users/", json=payload)
    assert response.status_code == 422


def test_register_user_password_missing_uppercase(client: TestClient) -> None:
    payload = {**VALID_USER, "password": "str0ng!pass"}
    response = client.post("/users/", json=payload)
    assert response.status_code == 422


def test_register_user_password_missing_lowercase(client: TestClient) -> None:
    payload = {**VALID_USER, "password": "STR0NG!PASS"}
    response = client.post("/users/", json=payload)
    assert response.status_code == 422


def test_register_user_password_missing_digit(client: TestClient) -> None:
    payload = {**VALID_USER, "password": "Strongpass!"}
    response = client.post("/users/", json=payload)
    assert response.status_code == 422


def test_register_user_password_missing_special_char(client: TestClient) -> None:
    payload = {**VALID_USER, "password": "Str0ngPass"}
    response = client.post("/users/", json=payload)
    assert response.status_code == 422


def test_register_user_username_too_short(client: TestClient) -> None:
    payload = {**VALID_USER, "username": "ab"}
    response = client.post("/users/", json=payload)
    assert response.status_code == 422


def test_register_user_username_invalid_characters(client: TestClient) -> None:
    payload = {**VALID_USER, "username": "invalid-user!"}
    response = client.post("/users/", json=payload)
    assert response.status_code == 422


def test_register_user_response_does_not_include_password(client: TestClient) -> None:
    response = client.post("/users/", json=VALID_USER)
    assert response.status_code == 201
    data = response.json()
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_user_rate_limit(client: TestClient) -> None:
    # Make 10 successful-ish requests with different emails to hit the rate limit
    # The 11th should return 429
    for i in range(10):
        payload = {
            "username": f"user{i:03d}",
            "email": f"user{i:03d}@example.com",
            "password": "Str0ng!Pass",
        }
        client.post("/users/", json=payload)

    payload = {
        "username": "user999",
        "email": "user999@example.com",
        "password": "Str0ng!Pass",
    }
    response = client.post("/users/", json=payload)
    assert response.status_code == 429
