## Why

The agent API router (`app/api/agent/`) was never implemented, causing a runtime import error in `main.py`. The endpoint needs to be built from scratch with authentication so only logged-in users can interact with the Stardew Valley AI agent.

## What Changes

- Create `app/api/agent/router.py` with a `POST /agent/chat` endpoint
- Create `app/api/agent/schemas.py` for request/response models
- Protect the endpoint with JWT bearer authentication using the existing `get_current_user` dependency
- Apply rate limiting to the agent endpoint
- Wire the router to the existing `StardewAgent` in `app/agent/agent.py`

## Capabilities

### New Capabilities

- `agent-chat`: Authenticated chat endpoint that accepts a user message and returns a response from the Stardew Valley AI agent

### Modified Capabilities

<!-- No existing spec-level behavior changes -->

## Impact

- **app/api/agent/**: New module (router.py, schemas.py, __init__.py)
- **app/api/main.py**: Already imports `agent_router` — will work once module is created
- **app/agent/agent.py**: Consumed as-is by the new router (no changes required)
- **Dependencies**: Reuses existing `app/api/dependencies.get_current_user` for auth, `app/core/security/rate_limiter` for rate limiting
