from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request

from app.agent.agent import StardewAgent
from app.api.agent.schemas import ChatRequest, ChatResponse
from app.api.dependencies import get_current_user
from app.core.security.rate_limiter import limiter

router = APIRouter()


@router.post("/chat")
@limiter.limit("10/minute")
async def chat(
    request: Request,
    body: ChatRequest,
    _current_user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> ChatResponse:
    agent = StardewAgent()
    response = agent.chat(body.message)
    return ChatResponse(response=response)
