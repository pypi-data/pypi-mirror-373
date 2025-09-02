import asyncio
import json
import pytest

from usf_agents.runtime.tool_registry import ToolRegistry


def add(a: int, b: int) -> int:
    return a + b


def http_like_ok() -> dict:
    return {"status": 200, "body": {"ok": True}}


def http_like_bad() -> dict:
    return {"status": 500, "body": {"ok": False}}


@pytest.mark.asyncio
async def test_register_function_success_with_example_expect():
    reg = ToolRegistry()
    tool = reg.register_function(
        name="add",
        func=add,
        schema={
            "description": "Add two numbers",
            "parameters": {
                "type": "object",
                "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                "required": ["a", "b"],
            },
        },
        examples=[{"name": "smoke", "args": {"a": 2, "b": 3}, "expect": 5}],
    )
    assert (tool.get("function") or {}).get("name") == "add"
    assert tool.get("x_kind") == "custom"
    tools = reg.to_openai_tools()
    assert any((t.get("function") or {}).get("name") == "add" for t in tools)

    # Router should dispatch correctly
    router = reg.router()
    payload = await router(
        {"id": "1", "type": "function", "function": {"name": "add", "arguments": json.dumps({"a": 4, "b": 7})}},
        []
    )
    assert payload["success"] is True and payload["content"] == 11


@pytest.mark.asyncio
async def test_register_function_fail_fast_on_example_status_mismatch():
    reg = ToolRegistry()
    with pytest.raises(Exception) as ei:
        reg.register_function(
            name="ping",
            func=http_like_bad,
            schema={"description": "HTTP-like tool"},
            examples=[{"name": "status", "args": {}, "expect_status": 200}],
        )
    # Ensure error details are surfaced in the exception message
    msg = str(ei.value)
    assert "expect_status" in msg or "status" in msg


@pytest.mark.asyncio
async def test_alias_and_router_with_alias():
    reg = ToolRegistry()
    reg.register_function(
        name="http_ok",
        func=http_like_ok,
        schema={"description": "HTTP ok"},
        examples=[{"name": "status", "args": {}, "expect_status": 200}],
    )
    reg.alias("http_ok", "ok_alias")

    # Resolve via alias
    tool = reg.get_tool("ok_alias")
    assert (tool.get("function") or {}).get("name") == "http_ok"

    # Router should accept alias name in tool_call
    router = reg.router()
    payload = await router(
        {"id": "1", "type": "function", "function": {"name": "ok_alias", "arguments": "{}"}},
        []
    )
    assert payload["success"] is True
    assert isinstance(payload.get("content"), dict)
    assert payload["content"].get("status") == 200


@pytest.mark.asyncio
async def test_alias_conflict_raises():
    reg = ToolRegistry()
    reg.register_function(name="add", func=add, schema={"description": "Add"})
    # Attempt to alias to same name should raise
    with pytest.raises(Exception):
        reg.alias("add", "add")


@pytest.mark.asyncio
async def test_router_unknown_tool_returns_error():
    reg = ToolRegistry()
    router = reg.router()
    payload = await router({"id": "1", "type": "function", "function": {"name": "missing", "arguments": "{}"}}, [])
    assert payload["success"] is False
    assert "not registered" in payload["error"]
