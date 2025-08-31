import asyncio
import json
import pytest

from usf_agents.multi_agent.registry import AgentRegistry
from usf_agents.graph.workflow import WorkflowGraph, ExecutionEngine
from usf_agents.trace.trace import TraceRecorder
from usf_agents.trace.visualize import to_mermaid
from usf_agents.multi_agent.base import _acollect_final_answer, SubAgent
from usf_agents.multi_agent.adapter import make_agent_tool, handle_agent_tool_call


class FakeWrapper:
    """
    Minimal wrapper double with the shape expected by ExecutionEngine:
    - id
    - async run_task(task) -> collected dict with 'status' and optional 'content'
    """
    def __init__(self, agent_id: str, result_content: str = "ok"):
        self.id = agent_id
        self._content = result_content

    async def run_task(self, task, calling_agent_msgs=None, context_param=None, options=None):
        # Simulate a successful 'final' result
        return {'status': 'final', 'content': f"{self._content}:{task.get('task')}"}


@pytest.mark.asyncio
async def test_workflow_execution_two_agents_success_path():
    # Registry with two fake agents
    reg = AgentRegistry()
    fa = FakeWrapper("A", result_content="helloA")
    fb = FakeWrapper("B", result_content="helloB")
    reg.add_agent(fa)
    reg.add_agent(fb)

    # Graph: nodeA -> nodeB if nodeA succeeds
    spec = {
        'nodes': [
            {'id': 'nodeA', 'type': 'agent', 'ref': 'A'},
            {'id': 'nodeB', 'type': 'agent', 'ref': 'B'}
        ],
        'edges': [
            {'source': 'nodeA', 'target': 'nodeB', 'condition': 'last.success == true'}
        ]
    }
    graph = WorkflowGraph(spec)
    recorder = TraceRecorder()
    engine = ExecutionEngine(graph, reg, recorder)

    inputs = {
        'nodeA': {'task': 'greet', 'input': {'name': 'Alice'}},
        'nodeB': {'task': 'follow', 'input': {'topic': 'status'}}
    }

    outputs = await engine.run(entry_nodes=['nodeA'], inputs=inputs, max_steps=10)
    assert 'nodeA' in outputs
    assert 'nodeB' in outputs
    assert outputs['nodeA']['success'] is True
    assert outputs['nodeB']['success'] is True
    assert outputs['nodeA']['content'].startswith('helloA:')
    assert outputs['nodeB']['content'].startswith('helloB:')

    # Trace should contain visited nodes
    trace = recorder.snapshot()
    visited = [ev.get('node_id') for ev in trace['events'] if ev.get('node_id')]
    assert 'nodeA' in visited and 'nodeB' in visited

    # Mermaid should annotate visited nodes
    diagram = to_mermaid(spec, trace)
    assert 'nodeA' in diagram and 'nodeB' in diagram
    assert 'visited' in diagram


@pytest.mark.asyncio
async def test_agent_tool_adapter_with_monkeypatched_collect(monkeypatch):
    # Monkeypatch the _acollect_final_answer used by adapter to avoid network
    async def fake_collect(agent, messages, options=None):
        return {'status': 'final', 'content': 'adapter-ok'}

    monkeypatch.setattr("usf_agents.multi_agent.base._acollect_final_answer", fake_collect)

    # Create a SubAgent with dummy config (no network since we patched collect)
    sa = SubAgent({
        'id': 'worker',
        'name': 'Worker',
        'agent_type': 'sub',
        'context_mode': 'AGENT_DECIDED',
        'usf_config': {'api_key': 'DUMMY', 'model': 'usf-mini'}
    })

    tool_def = make_agent_tool(sa, {'description': 'Invoke worker'})
    tool_call = {
        'id': 'call_1',
        'type': 'function',
        'function': {
            'name': tool_def['function']['name'],
            'arguments': json.dumps({'task': 'do_work', 'input': {'x': 1}})
        }
    }

    res = await handle_agent_tool_call(sa, tool_call, calling_context=None, mode='AGENT_DECIDED')
    assert res['success'] is True
    assert res['content'] == 'adapter-ok'
    assert res['tool_name'] == tool_def['function']['name']
