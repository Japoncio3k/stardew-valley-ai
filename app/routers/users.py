from fastapi import APIRouter, HTTPException, Request

from app.schemas.user import UserCreate, UserResponse
from app.security.rate_limiter import limiter
from app.services import user_service

router = APIRouter()


@router.post("/", status_code=201)
@limiter.limit("10/minute")
async def register_user(request: Request, body: UserCreate) -> UserResponse:
    if user_service.get_user_by_email(body.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    user = user_service.create_user(body.username, body.email, body.password)
    return UserResponse(id=user["id"], username=user["username"], email=user["email"])
