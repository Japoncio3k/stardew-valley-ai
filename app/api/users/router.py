from fastapi import APIRouter, HTTPException, Request

from app.api.users import service as user_service
from app.api.users.schemas import UserCreate, UserResponse
from app.core.security.rate_limiter import limiter

router = APIRouter()


@router.post("/", status_code=201)
@limiter.limit("10/minute")
async def register_user(request: Request, body: UserCreate) -> UserResponse:
    if user_service.get_user_by_email(body.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    user = user_service.create_user(body.username, body.email, body.password)
    return UserResponse(id=user["id"], username=user["username"], email=user["email"])
