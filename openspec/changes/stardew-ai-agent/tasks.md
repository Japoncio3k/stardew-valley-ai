## 1. Datasource Layer

- [x] 1.1 Create `app/data/stardew/` directory with `__init__.py`
- [x] 1.2 Implement `app/data/stardew/datasource.py` with `StardewDatasource` class that accepts a query string and returns mocked Stardew Valley game info (characters, crops, fishing, mines, etc.)
- [x] 1.3 Implement `app/data/stardew/use_case.py` with `GetStardewInfoUseCase` that calls the datasource and returns a human-readable string

## 2. Agent Implementation

- [x] 2.1 Implement `app/agent/tools.py` with the `get_stardew_info` LangChain `@tool` function that calls `GetStardewInfoUseCase`
- [x] 2.2 Implement `app/agent/agent.py` with a `StardewAgent` class that imports tools from `tools.py`, binds them to `OpenRouterManager.llm`, and runs the LangChain agent
- [x] 2.3 Wire the agent with a system prompt in Brazilian Portuguese (pt-BR) that instructs it to answer Stardew Valley questions

## 3. API Router

- [x] 3.1 Create `app/api/agent/` directory with `__init__.py`
- [x] 3.2 Implement `app/api/agent/router.py` with `POST /chat` endpoint that accepts `{"message": str}` and returns `{"response": str}`
- [x] 3.3 Add request/response Pydantic schemas in the router file

## 4. Registration

- [x] 4.1 Register the agent router in `app/api/main.py` under the `/agent` prefix
