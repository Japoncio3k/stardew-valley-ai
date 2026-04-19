## Context

The `app/api/agent/` module was declared in `main.py` but never implemented, causing an `ImportError` at startup. The agent logic already exists in `app/agent/agent.py` (`StardewAgent`). The auth infrastructure (`get_current_user` dependency, JWT validation, brute-force protection) is complete and reusable.

## Goals / Non-Goals

**Goals:**
- Create the `app/api/agent/` module (router, schemas, `__init__.py`) so the app starts without errors
- Protect `POST /agent/chat` with JWT bearer auth using the existing `get_current_user` dependency
- Apply per-IP rate limiting consistent with other endpoints

**Non-Goals:**
- Changing `StardewAgent` internals or the underlying LangChain implementation
- Adding conversation history or session state
- Streaming responses

## Decisions

### Use existing `get_current_user` dependency for auth
The dependency already handles bearer token extraction, JWT validation, IP binding, and returns the decoded user payload. Reusing it keeps auth consistent across all endpoints.
- Alternative: custom middleware — rejected, adds unnecessary complexity and bypasses the per-endpoint dependency pattern already established.

### Single `POST /agent/chat` endpoint
A single endpoint accepting `{ "message": "..." }` and returning `{ "response": "..." }` is sufficient for the current stateless agent.
- Alternative: REST-style `/agent/messages` resource — rejected, doesn't fit a stateless Q&A agent pattern.

### Rate limit: 10 requests/minute per IP
Consistent with the `/auth/refresh` limit. The agent calls an LLM (cost-sensitive), so rate limiting is important.
- Alternative: per-user limiting — deferred; IP-based is simpler and sufficient for now.

## Risks / Trade-offs

- [StardewAgent is not thread-safe if it holds mutable state] → Mitigation: instantiate `StardewAgent` per request (cheap, stateless).
- [LLM latency may cause timeouts] → Mitigation: out of scope for this change; handled at infrastructure level.

## Migration Plan

No migration needed. The module is new; `main.py` already imports it, so once the files exist the app will start normally.
