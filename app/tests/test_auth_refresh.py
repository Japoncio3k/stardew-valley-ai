from fastapi.testclient import TestClient

from app.tests.conftest import VALID_USER


def _register_and_login(client: TestClient) -> dict[str, str]:
    client.post("/users/", json=VALID_USER)
    response = client.post("/auth/login", json={"email": VALID_USER["email"], "password": VALID_USER["password"]})
    return response.json()  # type: ignore[no-any-return]


def test_refresh_valid_token(client: TestClient) -> None:
    tokens = _register_and_login(client)
    response = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_new_tokens_differ_from_old(client: TestClient) -> None:
    tokens = _register_and_login(client)
    response = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 200
    new_tokens = response.json()
    assert new_tokens["access_token"] != tokens["access_token"]
    assert new_tokens["refresh_token"] != tokens["refresh_token"]


def test_refresh_invalid_token(client: TestClient) -> None:
    response = client.post("/auth/refresh", json={"refresh_token": "this.is.notvalid"})
    assert response.status_code == 401


def test_refresh_malformed_token(client: TestClient) -> None:
    response = client.post("/auth/refresh", json={"refresh_token": "notajwtatall"})
    assert response.status_code == 401


def test_refresh_access_token_used_instead(client: TestClient) -> None:
    tokens = _register_and_login(client)
    # Use access token in place of refresh token
    response = client.post("/auth/refresh", json={"refresh_token": tokens["access_token"]})
    assert response.status_code == 401


def test_refresh_reuse_consumed_token(client: TestClient) -> None:
    tokens = _register_and_login(client)
    # First use — valid
    client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    # Second use — should be rejected (token was invalidated)
    response = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 401


def test_refresh_missing_token_field(client: TestClient) -> None:
    response = client.post("/auth/refresh", json={})
    assert response.status_code == 422


def test_refresh_rate_limit(client: TestClient) -> None:
    tokens = _register_and_login(client)
    # Exhaust rate limit — 10 requests
    for _ in range(10):
        client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    response = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 429
