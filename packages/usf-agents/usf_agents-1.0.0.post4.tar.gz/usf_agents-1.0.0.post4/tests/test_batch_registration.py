import asyncio
import json
import types
import pytest

from usf_agents.multi_agent.base import ManagerAgent
from usf_agents.runtime.decorators import tool


@tool(name="mul", alias="mul_alias", description="Multiply two ints")
def calc_mul(a: int, b: int) -> int:
    """
    Multiply two ints.
    Args:
        a (int): First operand
        b (int): Second operand
    """
    return a * b


def calc_add(a: int, b: int) -> int:
    """
    Add two ints.
    Args:
        a (int): First operand
        b (int): Second operand
    """
    return a + b


def bad_no_doc(a: int) -> int:
    # no docstring and no decorator schema -> should raise when registering
    return a


@pytest.mark.asyncio
async def test_add_function_tools_batch_success(monkeypatch):
    mgr = ManagerAgent({"id": "mgr", "usf_config": {"api_key": "DUMMY", "model": "usf-mini"}})
    # Register both via batch (decorator metadata on calc_mul, docstring parsing on calc_add)
    mgr.add_function_tools([calc_mul, calc_add])

    names = [(t.get("function") or {}).get("name") for t in mgr.list_tools()]
    # alias used for mul
    assert "mul_alias" in names
    assert "calc_add" in names

    # Stub run -> plan -> tool_calls -> final
    async def fake_run(messages, options=None):
        has_results = any(m.get("role") == "tool" for m in messages)
        if not has_results:
            yield {"type": "plan", "content": "plan", "tool_choice": {"type": "function"}}
            yield {
                "type": "tool_calls",
                "tool_calls": [
                    {"id": "1", "type": "function", "function": {"name": "mul_alias", "arguments": json.dumps({"a": 2, "b": 3})}},
                    {"id": "2", "type": "function", "function": {"name": "calc_add", "arguments": json.dumps({"a": 4, "b": 5})}},
                ],
            }
        else:
            yield {"type": "final_answer", "content": "done"}

    monkeypatch.setattr(mgr.usf, "run", fake_run)

    final = await mgr.run_auto([{"role": "user", "content": "batch"}], mode="auto")
    assert final == "done"


@pytest.mark.asyncio
async def test_add_function_tools_raises_on_missing_schema_and_docstring():
    mgr = ManagerAgent({"id": "mgr", "usf_config": {"api_key": "DUMMY", "model": "usf-mini"}})
    with pytest.raises(Exception) as ei:
        mgr.add_function_tools([bad_no_doc])
    assert "no explicit schema" in str(ei.value) or "parseable docstring" in str(ei.value)


@pytest.mark.asyncio
async def test_add_function_tools_from_module_with_filter(monkeypatch):
    # Create transient module with two functions
    m = types.ModuleType("mytools_mod")

    @tool(name="greet", alias="hello", description="Greet a user")
    def greet(name: str) -> str:
        """
        Greets.
        Args:
            name (str): Person to greet
        """
        return f"Hello {name}!"

    def ignore_me(x: int) -> int:
        """
        Args:
            x (int): number
        """
        return x

    setattr(m, "greet", greet)
    setattr(m, "ignore_me", ignore_me)

    mgr = ManagerAgent({"id": "mgr", "usf_config": {"api_key": "DUMMY", "model": "usf-mini"}})

    # Filter: only include functions that have decorator metadata (i.e., __usf_tool__)
    def only_decorated(fn):
        return hasattr(fn, "__usf_tool__")

    mgr.add_function_tools_from_module(m, filter=only_decorated)
    names = [(t.get("function") or {}).get("name") for t in mgr.list_tools()]
    assert "hello" in names
    assert "ignore_me" not in names

    # Stub run → greet
    async def fake_run(messages, options=None):
        if not any(m.get("role") == "tool" for m in messages):
            yield {"type": "plan", "content": "plan", "tool_choice": {"type": "function"}}
            yield {"type": "tool_calls", "tool_calls": [{"id": "1", "type": "function", "function": {"name": "hello", "arguments": json.dumps({"name": "USF"})}}]}
        else:
            yield {"type": "final_answer", "content": "done"}

    monkeypatch.setattr(mgr.usf, "run", fake_run)
    final = await mgr.run_auto([{"role": "user", "content": "use hello"}], mode="auto")
    assert final == "done"
