import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler  # type: ignore[attr-defined, unused-ignore]
from slowapi.errors import RateLimitExceeded

from app.api.agent.router import router as agent_router
from app.api.auth.router import router as auth_router
from app.api.users.router import router as users_router
from app.core.security.rate_limiter import limiter

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Stardew Valley AI API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(users_router, prefix="/users")
app.include_router(auth_router, prefix="/auth")
app.include_router(agent_router, prefix="/agent")
