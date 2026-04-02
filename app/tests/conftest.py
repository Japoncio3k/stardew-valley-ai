from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.mock import db

VALID_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "Str0ng!Pass",
}


@pytest.fixture
def client() -> Generator[TestClient]:
    db.users.clear()
    db.refresh_tokens.clear()
    db.brute_force.clear()
    # Reset rate limiter storage between tests
    limiter = app.state.limiter
    if hasattr(limiter, "_storage") and hasattr(limiter._storage, "reset"):
        limiter._storage.reset()
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
