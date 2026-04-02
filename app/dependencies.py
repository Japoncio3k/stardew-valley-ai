from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.security.jwt import decode_token

security = HTTPBearer()


def get_client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    request: Request,
) -> dict[str, Any]:
    token = credentials.credentials
    ip = get_client_ip(request)
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    if payload.get("ip") != ip:
        raise HTTPException(status_code=401, detail="Token IP mismatch")
    return payload
