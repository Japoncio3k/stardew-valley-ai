### Requirement: Authenticated chat endpoint
The system SHALL expose a `POST /agent/chat` endpoint that accepts a user message and returns a response from the Stardew Valley AI agent. The endpoint SHALL require a valid JWT access token supplied as a Bearer token in the `Authorization` header.

#### Scenario: Successful chat with valid token
- **WHEN** an authenticated user sends `POST /agent/chat` with `{"message": "Where can I find Penny?"}` and a valid `Authorization: Bearer <token>` header
- **THEN** the system returns HTTP 200 with `{"response": "<agent answer>"}`

#### Scenario: Request without token is rejected
- **WHEN** a client sends `POST /agent/chat` without an `Authorization` header
- **THEN** the system returns HTTP 403

#### Scenario: Request with invalid or expired token is rejected
- **WHEN** a client sends `POST /agent/chat` with an invalid or expired bearer token
- **THEN** the system returns HTTP 401

### Requirement: Rate limiting on chat endpoint
The system SHALL limit requests to `POST /agent/chat` to 10 requests per minute per IP address.

#### Scenario: Rate limit exceeded
- **WHEN** a client sends more than 10 requests to `POST /agent/chat` within one minute
- **THEN** the system returns HTTP 429 for subsequent requests within that window

### Requirement: Empty message rejection
The system SHALL reject chat requests where the `message` field is empty or whitespace-only.

#### Scenario: Empty message returns 422
- **WHEN** an authenticated user sends `POST /agent/chat` with `{"message": ""}`
- **THEN** the system returns HTTP 422 with a validation error
