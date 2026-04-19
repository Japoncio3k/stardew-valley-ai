## Context

`app/agent/agent.py` currently uses `langgraph.prebuilt.create_react_agent`, which is flagged as deprecated by Pylance. The installed `langchain` package exposes `langchain.agents.create_agent` as the canonical replacement. Confirmed at runtime: `create_agent` accepts `model`, `tools`, and `system_prompt` directly, returning a compiled `StateGraph` with the same invoke interface.

## Goals / Non-Goals

**Goals:**
- Eliminate the deprecated import with a drop-in replacement
- Simplify agent construction by using `create_agent`'s native `system_prompt` parameter
- Remove the manual `llm.bind_tools()` call

**Non-Goals:**
- Changing the external API (`POST /agent/chat`)
- Adding conversation memory or streaming
- Modifying `tools.py`, `datasource.py`, or `use_case.py`

## Decisions

### 1. Use `create_agent` with native `system_prompt`
`create_agent(model, tools, system_prompt=...)` replaces the three-step pattern of `bind_tools → create_react_agent → manual SystemMessage injection`. The system prompt is passed once at graph construction time, not per invocation.

**Before:**
```python
llm_with_tools = llm.bind_tools(_TOOLS)
self._graph = create_react_agent(llm_with_tools, tools=_TOOLS)
# and in chat():
messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=message)]
result = self._graph.invoke({"messages": messages})
```

**After:**
```python
self._graph = create_agent(llm, tools=_TOOLS, system_prompt=SYSTEM_PROMPT)
# and in chat():
result = self._graph.invoke({"messages": [HumanMessage(content=message)]})
```

### 2. No changes to invocation output parsing
`result["messages"][-1].content` remains valid — both APIs return the same `{"messages": [...]}` structure.

## Risks / Trade-offs

- [Behavioral difference between the two APIs] → Covered by existing tests; 19 tests verify the endpoint contract end-to-end with mocked agent.
- [Runtime import error if `langchain.agents.create_agent` not available] → Already verified at runtime before proposing this change.

## Migration Plan

1. Update `app/agent/agent.py`: swap import, remove `bind_tools`, pass `system_prompt` to `create_agent`, remove `SystemMessage` from `chat()`
2. Run `pytest tests/agent/` and `ruff check` to verify
3. No rollback needed — change is isolated to one file
