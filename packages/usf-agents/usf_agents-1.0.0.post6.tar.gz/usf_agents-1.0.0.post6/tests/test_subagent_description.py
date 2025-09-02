import pytest

from usf_agents.multi_agent.base import ManagerAgent, SubAgent


@pytest.mark.asyncio
async def test_subagent_description_from_spec_only():
    """
    When SubAgent has a spec['description'], the composed tool should use it as function.description.
    """
    mgr = ManagerAgent({
        "id": "mgr",
        "name": "Manager",
        "agent_type": "manager",
        "usf_config": {"api_key": "DUMMY", "model": "usf-mini"},
    })

    sub = SubAgent({
        "id": "worker",
        "name": "Worker",
        "agent_type": "sub",
        "context_mode": "NONE",
        "description": "Do precise numeric computations. Example: task='compute', input={'expression':'sum(prices)'}",
        "usf_config": {"api_key": "DUMMY", "model": "usf-mini"},
    })

    mgr.add_sub_agents(sub)
    tools = mgr.list_tools()
    fn = next((t.get("function") or {}) for t in tools if (t.get("function") or {}).get("name") == "agent_worker")
    assert fn.get("description") == "Do precise numeric computations. Example: task='compute', input={'expression':'sum(prices)'}"


@pytest.mark.asyncio
async def test_subagent_missing_description_raises():
    """
    If description is not set, composing tools should raise a clear error.
    Goal/backstory must not be used as a fallback for tool descriptions.
    """
    mgr = ManagerAgent({
        "id": "mgr",
        "name": "Manager",
        "agent_type": "manager",
        "usf_config": {"api_key": "DUMMY", "model": "usf-mini"},
    })

    sub = SubAgent({
        "id": "diag",
        "name": "Diagnostics",
        "agent_type": "sub",
        "context_mode": "NONE",
        "backstory": "Analyzes system internals deeply.",
        "goal": "Discover failure modes quickly.",
        "usf_config": {"api_key": "DUMMY", "model": "usf-mini"},
    })

    with pytest.raises(ValueError) as e:
        mgr.add_sub_agents(sub)
    assert "requires a description" in str(e.value) or "must define a description" in str(e.value)
