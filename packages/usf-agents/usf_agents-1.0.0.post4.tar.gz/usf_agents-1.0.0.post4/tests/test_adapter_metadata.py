import pytest

from usf_agents.multi_agent.base import SubAgent
from usf_agents.multi_agent.adapter import make_agent_tool


@pytest.mark.asyncio
async def test_make_agent_tool_includes_metadata_and_exec():
    sub = SubAgent({
        "id": "worker1",
        "name": "Worker One",
        "agent_type": "sub",
        "context_mode": "NONE",
        "usf_config": {"api_key": "DUMMY", "model": "usf-mini"}
    })

    tool = make_agent_tool(sub, {"description": "Do work"}, alias="agent_worker")
    # Base OpenAI function shape
    fn = tool.get("function") or {}
    assert fn.get("name") == "agent_worker"
    assert "parameters" in fn
    # Metadata
    assert tool.get("x_kind") == "agent"
    assert tool.get("x_agent_id") == "worker1"
    assert tool.get("x_alias") == "agent_worker"
    # Execution hook
    assert callable(tool.get("x_exec"))


@pytest.mark.asyncio
async def test_subagent_public_tool_includes_metadata_and_exec():
    sub = SubAgent({
        "id": "worker2",
        "name": "Worker Two",
        "agent_type": "sub",
        "context_mode": "NONE",
        "usf_config": {"api_key": "DUMMY", "model": "usf-mini"}
    })

    tool = sub.get_public_tool({"description": "Public tool"}, alias="agent_public")
    fn = tool.get("function") or {}
    assert fn.get("name") == "agent_public"
    assert tool.get("x_kind") == "agent"
    assert tool.get("x_agent_id") == "worker2"
    assert tool.get("x_alias") == "agent_public"
