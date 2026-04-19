## MODIFIED Requirements

### Requirement: Agent answers Stardew Valley questions
The system SHALL expose a conversational agent that accepts a user message and returns an AI-generated answer about Stardew Valley, using `langchain.agents.create_agent` (non-deprecated) with `OpenRouterManager.llm` and the `get_stardew_info` tool.

#### Scenario: User asks a game question
- **WHEN** a POST request is sent to `/agent/chat` with `{"message": "How do I befriend Penny?"}`
- **THEN** the system returns a 200 response with `{"response": "<AI-generated answer about Penny>"}` that incorporates information from the Stardew Valley tool

#### Scenario: Agent invokes the stardew info tool
- **WHEN** the LLM determines it needs game information to answer the question
- **THEN** the agent SHALL call the `get_stardew_info` tool with a relevant query string and incorporate the result into its response

#### Scenario: Missing message field
- **WHEN** a POST request is sent to `/agent/chat` without a `message` field
- **THEN** the system SHALL return a 422 Unprocessable Entity response
