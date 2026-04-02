from fastapi.testclient import TestClient

from app.mock import db
from app.tests.conftest import VALID_USER


def _register_and_login(client: TestClient) -> dict[str, str]:
    client.post("/users/", json=VALID_USER)
    response = client.post("/auth/login", json={"email": VALID_USER["email"], "password": VALID_USER["password"]})
    return response.json()  # type: ignore[no-any-return]


def test_logout_valid_access_token(client: TestClient) -> None:
    tokens = _register_and_login(client)
    response = client.post("/auth/logout", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert response.status_code == 200


def test_logout_refresh_token_removed_from_allowlist(client: TestClient) -> None:
    tokens = _register_and_login(client)
    # Confirm there's a refresh token in allowlist before logout
    assert len(db.refresh_tokens) > 0

    client.post("/auth/logout", headers={"Authorization": f"Bearer {tokens['access_token']}"})

    # After logout, the allowlist should be empty
    assert len(db.refresh_tokens) == 0


def test_logout_missing_authorization_header(client: TestClient) -> None:
    response = client.post("/auth/logout")
    assert response.status_code == 401


def test_logout_invalid_token(client: TestClient) -> None:
    response = client.post("/auth/logout", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401


def test_logout_malformed_authorization_header(client: TestClient) -> None:
    response = client.post("/auth/logout", headers={"Authorization": "NotBearer token"})
    assert response.status_code == 401


def test_logout_refresh_no_longer_valid_after_logout(client: TestClient) -> None:
    tokens = _register_and_login(client)

    # Logout
    client.post("/auth/logout", headers={"Authorization": f"Bearer {tokens['access_token']}"})

    # Attempt to refresh — should fail because the jti was removed from allowlist
    response = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 401
