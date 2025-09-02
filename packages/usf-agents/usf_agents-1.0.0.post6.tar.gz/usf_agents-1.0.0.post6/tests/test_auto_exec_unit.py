import asyncio
import json
import pytest

from usf_agents.runtime.auto_exec import (
    _validate_unique_names,
    _tool_map,
    _is_agent_tool,
    run_with_auto_execution,
)


def make_tool(name: str, kind: str = "custom", exec_fn=None):
    tool = {
        "type": "function",
        "function": {
            "name": name,
            "description": f"{kind} tool",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
        "x_kind": kind,
    }
    if exec_fn is not None:
        tool["x_exec"] = exec_fn
    return tool


class FakeAgent:
    """
    Simulates a USFAgent-like interface for auto-exec tests, avoiding network calls.
    Behavior:
      - On first run when no tool results present: emits plan + tool_calls, then stops.
      - On subsequent run when tool results are present: emits final_answer.
    Configurable: tool_calls list injected via constructor.
    """
    def __init__(self, tool_calls):
        self.tool_calls = tool_calls

    async def run(self, messages, options=None):
        has_tool_results = any(m.get("role") == "tool" for m in messages)
        if not has_tool_results:
            # emit a plan
            yield {
                "type": "plan",
                "content": "plan",
                "plan": "plan",
                "agent_status": "running",
                "tool_choice": {"type": "function"},
            }
            # request tool calls
            yield {
                "type": "tool_calls",
                "tool_calls": self.tool_calls,
                "agent_status": "running",
            }
        else:
            # after results are appended, return final
            yield {"type": "final_answer", "content": "done"}


@pytest.mark.asyncio
async def test_validate_unique_names_raises_on_dupes():
    tools = [make_tool("a"), make_tool("a")]
    with pytest.raises(Exception) as ei:
        _validate_unique_names(tools)
    assert "duplicate tool names" in str(ei.value)


@pytest.mark.asyncio
async def test_tool_map_basic():
    tools = [make_tool("x"), make_tool("y")]
    m = _tool_map(tools)
    assert set(m.keys()) == {"x", "y"}


@pytest.mark.asyncio
async def test_is_agent_tool_metadata_and_prefix():
    t_agent = make_tool("agent_worker", kind="agent")
    t_custom = make_tool("calc", kind="custom")
    assert _is_agent_tool(t_agent) is True
    assert _is_agent_tool(t_custom) is False
    # Fallback by prefix when metadata missing
    t_prefix = {
        "type": "function",
        "function": {"name": "agent_prefixed", "description": "", "parameters": {"type": "object", "properties": {}, "required": []}}
    }
    assert _is_agent_tool(t_prefix) is True


@pytest.mark.asyncio
async def test_mode_disable_returns_pending_tool_calls():
    tc = [{"id": "1", "type": "function", "function": {"name": "calc", "arguments": "{}"}}]
    agent = FakeAgent(tc)
    tools = [make_tool("calc", kind="custom")]
    async def router(tool_call, current_msgs):
        return {"success": True, "content": 42}
    result = await run_with_auto_execution(agent, [{"role": "user", "content": "x"}], tools, router, mode="disable")
    assert isinstance(result, dict) and result.get("status") == "tool_calls"
    assert result.get("tool_calls")


@pytest.mark.asyncio
async def test_mode_auto_executes_agent_and_custom():
    # Two tool calls: one agent, one custom
    tcs = [
        {"id": "1", "type": "function", "function": {"name": "agent_worker", "arguments": "{}"}},
        {"id": "2", "type": "function", "function": {"name": "calc", "arguments": json.dumps({"expression": "2+3"})}},
    ]
    agent = FakeAgent(tcs)

    async def agent_exec(tc, current_msgs, context_param=None, options=None):
        # simulate agent executing internally to final and producing output content
        return {"success": True, "content": "agent-done", "error": None}

    tools = [
        make_tool("agent_worker", kind="agent", exec_fn=agent_exec),
        make_tool("calc", kind="custom"),
    ]

    async def router(tool_call, current_msgs):
        # Evaluate expression from arguments safely for test purposes
        args = json.loads((tool_call.get("function") or {}).get("arguments") or "{}")
        expr = args.get("expression", "0")
        return {"success": True, "content": eval(expr)}  # test-only

    final = await run_with_auto_execution(agent, [{"role": "user", "content": "x"}], tools, router, mode="auto")
    assert isinstance(final, str) and final == "done"


@pytest.mark.asyncio
async def test_mode_agent_pauses_on_custom():
    # Mix of agent + custom, but mode=agent should pause on custom
    tcs = [
        {"id": "1", "type": "function", "function": {"name": "agent_worker", "arguments": "{}"}},
        {"id": "2", "type": "function", "function": {"name": "calc", "arguments": "{}"}},
    ]
    agent = FakeAgent(tcs)

    async def agent_exec(tc, current_msgs, context_param=None, options=None):
        return {"success": True, "content": "ok", "error": None}

    tools = [
        make_tool("agent_worker", kind="agent", exec_fn=agent_exec),
        make_tool("calc", kind="custom"),
    ]

    async def router(tool_call, current_msgs):
        return {"success": True, "content": 1}

    result = await run_with_auto_execution(agent, [{"role": "user", "content": "x"}], tools, router, mode="agent")
    assert isinstance(result, dict) and result.get("status") == "tool_calls"


@pytest.mark.asyncio
async def test_mode_tool_pauses_on_agent():
    tcs = [
        {"id": "1", "type": "function", "function": {"name": "agent_worker", "arguments": "{}"}},
    ]
    agent = FakeAgent(tcs)
    tools = [make_tool("agent_worker", kind="agent", exec_fn=lambda *args, **kwargs: None)]

    async def router(tool_call, current_msgs):
        return {"success": True, "content": 1}

    result = await run_with_auto_execution(agent, [{"role": "user", "content": "x"}], tools, router, mode="tool")
    assert isinstance(result, dict) and result.get("status") == "tool_calls"
