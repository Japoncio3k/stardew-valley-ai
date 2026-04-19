## Why

`app/agent/agent.py` uses `create_react_agent` from `langgraph.prebuilt`, which Pylance flags as deprecated. The replacement is `create_agent` from `langchain.agents`, which offers a cleaner API with native `system_prompt` support and implicit tool binding.

## What Changes

- Replace `from langgraph.prebuilt import create_react_agent` with `from langchain.agents import create_agent` in `app/agent/agent.py`
- Remove manual `llm.bind_tools()` call — `create_agent` handles tool binding internally
- Pass `system_prompt` directly to `create_agent` instead of prepending a `SystemMessage` to the messages list
- Update the `chat` method invocation to match the new graph's input/output contract

## Capabilities

### New Capabilities
<!-- None — this is an internal refactor with no behavior change -->

### Modified Capabilities
- `stardew-agent`: Implementation updated to use non-deprecated `create_agent`; external behavior (endpoint, response format) unchanged

## Impact

- **Modified**: `app/agent/agent.py` only
- **No API contract changes**: `POST /agent/chat` request/response schema unchanged
- **No test changes required**: router and tool tests remain valid; agent unit tests (if any) may need import update
