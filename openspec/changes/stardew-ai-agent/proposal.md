## Why

The application needs a conversational AI agent that can answer user questions about Stardew Valley, leveraging the existing OpenRouterManager LLM infrastructure and providing a clean, extensible architecture for game knowledge retrieval.

## What Changes

- New `app/agent/` module with a conversational agent using LangChain and OpenRouterManager
- New `app/data/stardew/` datasource with mock Stardew Valley data retrieval
- New `app/data/stardew/` use case for fetching Stardew Valley information
- New FastAPI router at `/agent/chat` to expose the agent via HTTP
- Agent uses a tool-calling pattern: LLM decides when to call the Stardew info retrieval tool

## Capabilities

### New Capabilities
- `stardew-agent`: Conversational agent that answers Stardew Valley questions using LLM + tool calling
- `stardew-datasource`: Datasource layer that retrieves Stardew Valley game information (mocked)

### Modified Capabilities
<!-- None -->

## Impact

- **New files**: `app/agent/agent.py`, `app/data/stardew/datasource.py`, `app/data/stardew/use_case.py`, `app/api/agent/router.py`
- **Modified**: `app/api/main.py` to register the new agent router
- **Dependencies**: LangChain (already present via OpenRouterManager), FastAPI (existing)
- **No breaking changes**
