import asyncio
import json
import pytest

from usf_agents.multi_agent.base import ManagerAgent, SubAgent


def calc(expression: str) -> int:
    """
    Evaluate a simple expression.

    Args:
        expression (str): A Python expression to evaluate.
    """
    return eval(expression)


@pytest.mark.asyncio
async def test_add_function_tool_registers_and_composes():
    mgr = ManagerAgent({
        "id": "mgr",
        "name": "Manager",
        "agent_type": "manager",
        "usf_config": {"api_key": "DUMMY", "model": "usf-mini"},
    })
    mgr.add_function_tool("calc", calc, alias="math_calc")

    tools = mgr.list_tools()
    names = [(t.get("function") or {}).get("name") for t in tools]
    assert "math_calc" in names
    # metadata should mark it as custom
    tool = next(t for t in tools if (t.get("function") or {}).get("name") == "math_calc")
    assert tool.get("x_kind") == "custom"


@pytest.mark.asyncio
async def test_add_sub_agent_simple_composes_with_alias_and_metadata():
    mgr = ManagerAgent({
        "id": "mgr",
        "name": "Manager",
        "agent_type": "manager",
        "usf_config": {"api_key": "DUMMY", "model": "usf-mini"},
    })
    mgr.add_sub_agent_simple(id="worker", alias="agent_worker", context_mode="NONE", description="Drafts short outputs")

    tools = mgr.list_tools()
    names = [(t.get("function") or {}).get("name") for t in tools]
    assert "agent_worker" in names
    tool = next(t for t in tools if (t.get("function") or {}).get("name") == "agent_worker")
    assert tool.get("x_kind") == "agent"
    assert tool.get("x_agent_id") == "worker"


@pytest.mark.asyncio
async def test_run_auto_with_custom_tool_only(monkeypatch):
    """
    Validate that manager.run_auto(mode='auto') executes a custom tool and returns final.
    We fake the underlying agent.run to emit plan -> tool_calls -> (after tool results) final_answer.
    """
    mgr = ManagerAgent({
        "id": "mgr",
        "name": "Manager",
        "agent_type": "manager",
        "usf_config": {"api_key": "DUMMY", "model": "usf-mini"},
    })
    mgr.add_function_tool("calc", calc, alias="math_calc")

    # Fake USF agent.run to avoid network; switch to final after tool results exist
    async def fake_run(messages, options=None):
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
            # emit a tool call for our custom tool
            yield {
                "type": "tool_calls",
                "tool_calls": [{"id": "1", "type": "function", "function": {"name": "math_calc", "arguments": json.dumps({"expression": "2+3"})}}],
                "agent_status": "running",
            }
        else:
            yield {"type": "final_answer", "content": "done"}

    monkeypatch.setattr(mgr.usf, "run", fake_run)

    messages = [{"role": "user", "content": "Use math_calc to compute 2+3"}]
    final = await mgr.run_auto(messages, mode="auto")
    assert isinstance(final, str) and final == "done"


@pytest.mark.asyncio
async def test_run_auto_with_agent_tool(monkeypatch):
    """
    Validate that manager.run_auto(mode='auto') can auto-execute an agent tool by stubbing SubAgent.execute_as_tool_until_final.
    """
    mgr = ManagerAgent({
        "id": "mgr",
        "name": "Manager",
        "agent_type": "manager",
        "usf_config": {"api_key": "DUMMY", "model": "usf-mini"},
    })
    mgr.add_sub_agent_simple(id="worker", alias="agent_worker", context_mode="NONE", description="Drafts short outputs")

    # Stub SubAgent.execute_as_tool_until_final to avoid deeper loops
    async def stub_exec(self, tool_call, calling_context, context_param=None, options=None):
        return {"success": True, "content": "agent-ok", "error": None}

    monkeypatch.setattr(SubAgent, "execute_as_tool_until_final", stub_exec, raising=True)

    # Fake underlying USF agent.run to request the agent tool first, then final after results
    async def fake_run(messages, options=None):
        has_tool_results = any(m.get("role") == "tool" for m in messages)
        if not has_tool_results:
            yield {
                "type": "plan",
                "content": "plan",
                "plan": "plan",
                "agent_status": "running",
                "tool_choice": {"type": "function"},
            }
            yield {
                "type": "tool_calls",
                "tool_calls": [{"id": "1", "type": "function", "function": {"name": "agent_worker", "arguments": "{}"}}],
                "agent_status": "running",
            }
        else:
            yield {"type": "final_answer", "content": "done"}

    monkeypatch.setattr(mgr.usf, "run", fake_run)

    messages = [{"role": "user", "content": "Ask agent_worker to draft summary"}]
    final = await mgr.run_auto(messages, mode="auto")
    assert isinstance(final, str) and final == "done"
