# Multi-Agent Orchestration Examples

This document shows how to use the new multi-agent orchestration layer built on top of `USFAgent`.

Contents:
- Sub-agent isolation and agent-as-tool delegation
- Context passing modes (NONE, AGENT_DECIDED, ALWAYS_FULL, CONTEXT_PARAM)
- Manager agent composing multiple sub-agents
- Graph execution with WorkflowGraph + ExecutionEngine
- Trace recording and visualization (Mermaid / Graphviz / JSON)

Prereqs:
- You must have valid API key(s) compatible with your configured base_url/model(s).

## 1) SubAgent as a Tool (Isolation preserved)

```python
import asyncio
from usf_agents import SubAgent, ManagerAgent

# Create sub-agents (fully isolated)
math_agent = SubAgent({
    'id': 'math',
    'name': 'Math Specialist',
    'agent_type': 'sub',
    'context_mode': 'NONE',  # No parent context passed by default
    'usf_config': {
        'api_key': 'YOUR_API_KEY',
        'model': 'usf-mini'
    }
})

code_agent = SubAgent({
    'id': 'coder',
    'name': 'Code Assistant',
    'agent_type': 'sub',
    'context_mode': 'CONTEXT_PARAM',  # Only lightweight context allowed
    'usf_config': {
        'api_key': 'YOUR_API_KEY',
        'model': 'usf-mini'
    }
})

# Create a manager agent
manager = ManagerAgent({
    'id': 'mgr',
    'name': 'Manager',
    'agent_type': 'manager',
    'usf_config': {
        'api_key': 'YOUR_API_KEY',
        'model': 'usf-mini'
    }
})

# Add sub-agents to manager with callable tool schemas
manager.add_sub_agent(math_agent, {
    'description': 'Delegate math tasks to the math agent',
    'parameters': {
        'type': 'object',
        'properties': {
            'task': {'type': 'string'},
            'input': {'type': 'object'},
            'context_param': {'type': 'object'}
        },
        'required': ['task']
    }
}, alias='math_tool')

manager.add_sub_agent(code_agent, {
    'description': 'Delegate coding tasks to the code agent',
    'parameters': {
        'type': 'object',
        'properties': {
            'task': {'type': 'string'},
            'input': {'type': 'object'},
            'context_param': {'type': 'object'}
        },
        'required': ['task']
    }
}, alias='coder_tool')

# Example: delegate a "task" to a sub-agent (no full parent transcript passed)
async def main():
    result = await manager.delegate(
        sub_id='math',
        task={'task': 'calculate', 'input': {'expression': '25 * 4'}},
        # policy omitted => inherit sub-agent policy (NONE)
    )
    print('Math result:', result)

    # Delegate with lightweight context to coder
    result2 = await manager.delegate(
        sub_id='coder',
        task={'task': 'generate_function', 'input': {'language': 'python', 'spec': 'sum two numbers a and b'}},
        policy='CONTEXT_PARAM',
        context_param={'style': 'concise'}
    )
    print('Code result:', result2)

asyncio.run(main())
```

## 2) Context Modes

- `NONE`: sub-agent only receives the new TaskPayload as a fresh user message.
- `AGENT_DECIDED`: if calling agent provides prior messages, behaves like `ALWAYS_FULL`, else `NONE`.
- `ALWAYS_FULL`: pass complete calling agent messages (OpenAI format) + a final TaskPayload message.
- `CONTEXT_PARAM`: pass only a compact system message derived from `context_param` + TaskPayload message.

You can set a sub-agent default via `context_mode` and override per-call using `manager.delegate(..., policy=...)`.

## 3) Direct Graph Execution

```python
import asyncio
from usf_agents import SubAgent, ManagerAgent, AgentRegistry, WorkflowGraph, ExecutionEngine, TraceRecorder, to_mermaid

# Two agents, used as nodes in a graph
a = SubAgent({
    'id': 'A',
    'name': 'Agent A',
    'agent_type': 'sub',
    'context_mode': 'NONE',
    'usf_config': {'api_key': 'YOUR_API_KEY', 'model': 'usf-mini'}
})

b = SubAgent({
    'id': 'B',
    'name': 'Agent B',
    'agent_type': 'sub',
    'context_mode': 'CONTEXT_PARAM',
    'usf_config': {'api_key': 'YOUR_API_KEY', 'model': 'usf-mini'}
})

# Registry
reg = AgentRegistry()
reg.add_agent(a)
reg.add_agent(b)

# Graph spec: A -> B (if A succeeds)
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

async def run():
    inputs = {
        'nodeA': {'task': 'greet', 'input': {'name': 'Alice'}},   # TaskPayload for A
        'nodeB': {'task': 'followup', 'input': {'topic': 'status'}, 'metadata': {'ref': 'A->B'}}  # TaskPayload for B
    }
    outputs = await engine.run(entry_nodes=['nodeA'], inputs=inputs, max_steps=20)
    print('Outputs:', outputs)

    trace = recorder.snapshot()
    print('Mermaid:\n', to_mermaid(spec, trace))

asyncio.run(run())
```

## 4) Agent-as-Tool Adapter (advanced)

Use `make_agent_tool` and `handle_agent_tool_call` to create and handle agent-tools integrated into a classic tool-calling loop.

```python
import asyncio, json
from usf_agents import SubAgent
from usf_agents.multi_agent import make_agent_tool, handle_agent_tool_call

sub = SubAgent({
    'id': 'worker',
    'name': 'Worker',
    'agent_type': 'sub',
    'context_mode': 'AGENT_DECIDED',
    'usf_config': {'api_key': 'YOUR_API_KEY', 'model': 'usf-mini'}
})

tool_def = make_agent_tool(sub, {
    'description': 'Invoke worker sub-agent'
})

# tool_call is a dict in OpenAI style, for demonstration:
tool_call = {
  'id': 'call_1',
  'type': 'function',
  'function': {
    'name': tool_def['function']['name'],
    'arguments': json.dumps({'task': 'do_work', 'input': {'x': 1}})
  }
}

async def run():
    # No calling_context messages provided here; policy is AGENT_DECIDED
    res = await handle_agent_tool_call(sub, tool_call, calling_context=None, mode='AGENT_DECIDED')
    print(res)

asyncio.run(run())
```

Notes:
- Sub-agents never expose their internal tools or memory.
- Context is explicit per the 4-mode policy.
- For direct USFAgent-style loops, feed `ManagerAgent.list_tools()` to the manager’s planning stage.
