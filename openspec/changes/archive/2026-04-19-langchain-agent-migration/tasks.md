## 1. Update Agent Implementation

- [x] 1.1 In `app/agent/agent.py`, replace `from langgraph.prebuilt import create_react_agent` with `from langchain.agents import create_agent` and remove the `SystemMessage` import
- [x] 1.2 Replace `llm.bind_tools(_TOOLS)` + `create_react_agent(llm_with_tools, tools=_TOOLS)` with `create_agent(llm, tools=_TOOLS, system_prompt=SYSTEM_PROMPT)`
- [x] 1.3 Update the `chat` method to pass only `HumanMessage(content=message)` (no `SystemMessage`) since the system prompt is now part of the graph

## 2. Verify

- [x] 2.1 Run `pytest tests/agent/ -v` and confirm all 19 tests pass
- [x] 2.2 Run `ruff check app/agent/` and confirm no lint errors
