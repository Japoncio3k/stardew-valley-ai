from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.dependencies import get_client_ip
from app.schemas.token import LoginRequest, RefreshRequest, TokenResponse
from app.security.rate_limiter import limiter
from app.services import auth_service

router = APIRouter()


@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, body: LoginRequest) -> TokenResponse:
    ip = get_client_ip(request)

    # Check brute force lock before attempting login
    locked_until = auth_service.check_ip_locked(ip)
    if locked_until is not None:
        unlock_time = locked_until.isoformat()
        raise HTTPException(
            status_code=423,
            detail=f"Account temporarily locked. Try again after {unlock_time}",
        )

    tokens = auth_service.login(body.email, body.password, ip)
    if tokens is None:
        # Check again in case login itself caused a lock
        locked_until = auth_service.check_ip_locked(ip)
        if locked_until is not None:
            unlock_time = locked_until.isoformat()
            raise HTTPException(
                status_code=423,
                detail=f"Account temporarily locked. Try again after {unlock_time}",
            )
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return TokenResponse(**tokens)


@router.post("/logout")
async def logout(request: Request) -> dict[str, Any]:
    # Extract token manually (not using Depends to give 401 instead of 403 on missing header)
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

    token = auth_header[len("Bearer "):]
    ip = get_client_ip(request)

    success = auth_service.logout(token, ip)
    if not success:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return {"detail": "Logged out successfully"}


@router.post("/refresh")
@limiter.limit("10/minute")
async def refresh(request: Request, body: RefreshRequest) -> TokenResponse:
    ip = get_client_ip(request)
    tokens = auth_service.refresh(body.refresh_token, ip)
    if tokens is None:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    return TokenResponse(**tokens)
