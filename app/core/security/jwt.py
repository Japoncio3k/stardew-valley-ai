import os
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import jwt

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 1
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(user_id: str, ip: str, refresh_jti: str) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": user_id,
        "exp": now + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS),
        "iat": now,
        "ip": ip,
        "jti": refresh_jti,  # jti in access token = refresh token's jti
        "type": "access",
    }
    result: str = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return result


def create_refresh_token(user_id: str, ip: str) -> tuple[str, str]:
    now = datetime.now(UTC)
    jti = str(uuid.uuid4())
    payload: dict[str, Any] = {
        "sub": user_id,
        "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": now,
        "jti": jti,
        "ip": ip,
        "type": "refresh",
    }
    token: str = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, jti


def decode_token(token: str) -> dict[str, Any]:
    # raises JWTError on invalid, ExpiredSignatureError on expired
    result: dict[str, Any] = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return result
