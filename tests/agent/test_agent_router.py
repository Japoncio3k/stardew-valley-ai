from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.mock import db
from tests.conftest import VALID_USER


@pytest.fixture
def client() -> TestClient:
    db.users.clear()
    db.refresh_tokens.clear()
    db.brute_force.clear()
    limiter = app.state.limiter
    if hasattr(limiter, "_storage") and hasattr(limiter._storage, "reset"):
        limiter._storage.reset()
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def _get_token(client: TestClient) -> str:
    client.post("/users/", json=VALID_USER)
    resp = client.post("/auth/login", json={"email": VALID_USER["email"], "password": VALID_USER["password"]})
    return resp.json()["access_token"]


def test_chat_authenticated_returns_200(client: TestClient) -> None:
    token = _get_token(client)
    with patch("app.api.agent.router.StardewAgent") as MockAgent:
        MockAgent.return_value.chat.return_value = "Penny mora em Pelican Town."
        response = client.post(
            "/agent/chat",
            json={"message": "Quem é a Penny?"},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    assert response.json() == {"response": "Penny mora em Pelican Town."}


def test_chat_unauthenticated_returns_401(client: TestClient) -> None:
    response = client.post("/agent/chat", json={"message": "Quem é a Penny?"})
    assert response.status_code == 401


def test_chat_empty_message_returns_422(client: TestClient) -> None:
    token = _get_token(client)
    response = client.post(
        "/agent/chat",
        json={"message": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_chat_whitespace_message_returns_422(client: TestClient) -> None:
    token = _get_token(client)
    response = client.post(
        "/agent/chat",
        json={"message": "   "},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_chat_invalid_token_returns_401(client: TestClient) -> None:
    response = client.post(
        "/agent/chat",
        json={"message": "Quem é a Penny?"},
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status_code == 401
