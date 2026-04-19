## 1. Module Scaffold

- [x] 1.1 Create `app/api/agent/__init__.py`
- [x] 1.2 Create `app/api/agent/schemas.py` with `ChatRequest` (message: non-empty str) and `ChatResponse` (response: str)

## 2. Router Implementation

- [x] 2.1 Create `app/api/agent/router.py` with `POST /chat` endpoint
- [x] 2.2 Apply `get_current_user` dependency to protect the endpoint
- [x] 2.3 Apply `@limiter.limit("10/minute")` rate limiting to the endpoint
- [x] 2.4 Instantiate `StardewAgent` per request and call `agent.chat(message)`

## 3. Validation

- [x] 3.1 Add `min_length=1` and strip-whitespace validator to `ChatRequest.message`

## 4. Tests

- [x] 4.1 Write test for successful authenticated chat (HTTP 200)
- [x] 4.2 Write test for unauthenticated request (HTTP 403)
- [x] 4.3 Write test for empty message (HTTP 422)
