## Context

The project is a FastAPI application with an existing auth/users API. A `common/utils/open_router_manager.py` singleton wraps LangChain's `ChatOpenAI` against the OpenRouter gateway. An `app/agent/` folder exists but is empty. The goal is to introduce a conversational agent that uses LLM tool-calling to look up Stardew Valley game information.

## Goals / Non-Goals

**Goals:**
- Implement a stateless chat endpoint (`POST /agent/chat`) that accepts a user message and returns an AI response
- Agent uses LangChain tool-calling so the LLM can invoke a `get_stardew_info` tool when it needs game knowledge
- Mock datasource returns random plausible data for any Stardew Valley query
- Follow existing project layering: datasource → use case → agent → router

**Non-Goals:**
- Persistent conversation history / multi-turn memory across requests
- Real Stardew Valley data API integration
- Streaming responses

## Decisions

### 1. LangChain `create_react_agent` with tool binding
Use LangChain's agent framework (`langgraph` or `create_react_agent`) bound to the existing `OpenRouterManager.llm`. The tool is a plain Python function decorated with `@tool` that calls the use case.

**Alternative considered**: Plain prompt + manual tool parsing. Rejected — LangChain tool-calling is already in the dependency tree and handles the parse/retry loop automatically.

### 2. Stateless per-request agent invocation
Each `POST /agent/chat` invocation creates a fresh agent executor run with only the current message. No session state is stored.

**Alternative considered**: In-memory conversation history keyed by session. Out of scope per proposal.

### 3. Layering
```
Router (app/api/agent/router.py)
  └─ Agent (app/agent/agent.py)          ← LangChain agent orchestration only
       └─ Tools (app/agent/tools.py)     ← @tool adapter layer (LangChain ↔ use cases)
            └─ Use Case (app/data/stardew/use_case.py)
                 └─ Datasource (app/data/stardew/datasource.py)  ← mock data
```

`tools.py` is the boundary between LangChain's calling convention and the use case layer. Keeping it separate allows tools to be unit-tested without instantiating the full agent, and makes it easy to add new tools without touching agent orchestration logic.

### 4. Mock datasource strategy
The datasource accepts a free-text `query` string and returns a random selection from a pre-defined pool of Stardew Valley facts/categories. This keeps the mock realistic without a real API.

## Risks / Trade-offs

- [OpenRouterManager is a singleton initialized at import time] → Mitigation: defer instantiation inside the agent function; wrap in try/except for missing env vars in test environments.
- [Mock responses may not match the user's query] → Acceptable for MVP; the LLM wraps the mock data in a coherent natural-language answer.
- [No conversation history] → Users must repeat context each turn; acceptable per Non-Goals.

## Migration Plan

1. Add new files (no existing files deleted)
2. Register `/agent` router in `app/api/main.py`
3. No database migrations required
4. Rollback: remove router registration and new files
