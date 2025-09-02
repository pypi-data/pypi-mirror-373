import pytest

from usf_agents.multi_agent.base import ManagerAgent, SubAgent


def make_native_tool(name: str, description: str = "native") -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    }


@pytest.mark.asyncio
async def test_tool_name_collision_within_manager_scope_raises():
    # Manager has a native tool named "calc"
    mgr = ManagerAgent({
        "id": "mgr1",
        "name": "Manager1",
        "agent_type": "manager",
        "usf_config": {"api_key": "DUMMY", "model": "usf-mini"},
        "tools": [make_native_tool("calc")]
    })
    # Sub-agent exposed with alias "calc" -> collision inside the same manager scope
    worker = SubAgent({
        "id": "w1",
        "name": "Worker1",
        "agent_type": "sub",
        "context_mode": "NONE",
        "usf_config": {"api_key": "DUMMY", "model": "usf-mini"}
    })
    mgr.add_sub_agent(worker, {"description": "worker tool"}, alias="calc")

    with pytest.raises(Exception) as ei:
        _ = mgr.list_tools()
    msg = str(ei.value)
    assert "Tool Name Collision" in msg
    assert "calc" in msg


@pytest.mark.asyncio
async def test_same_tool_names_allowed_across_isolated_agents():
    # Two separate managers can each have a tool named "calc" without conflict due to isolation.
    mgr_a = ManagerAgent({
        "id": "mgrA",
        "name": "ManagerA",
        "agent_type": "manager",
        "usf_config": {"api_key": "DUMMY", "model": "usf-mini"},
        "tools": [make_native_tool("calc")]
    })
    mgr_b = ManagerAgent({
        "id": "mgrB",
        "name": "ManagerB",
        "agent_type": "manager",
        "usf_config": {"api_key": "DUMMY", "model": "usf-mini"},
        "tools": [make_native_tool("calc")]
    })

    # Should not raise: each manager composes in its own scope
    tools_a = mgr_a.list_tools()
    tools_b = mgr_b.list_tools()
    assert any((t.get("function") or {}).get("name") == "calc" for t in tools_a)
    assert any((t.get("function") or {}).get("name") == "calc" for t in tools_b)
