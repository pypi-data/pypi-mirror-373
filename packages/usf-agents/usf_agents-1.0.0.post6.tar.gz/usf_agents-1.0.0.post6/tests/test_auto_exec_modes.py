import json
import pytest

from usf_agents.runtime.auto_exec import run_with_auto_execution


class StubAgent:
    """
    Minimal stub for USFAgent.run that emits:
    - If no tool results yet: plan -> tool_calls
    - If any tool result present in messages: final_answer
    """
    def __init__(self, tool_calls):
        self.tool_calls = tool_calls

    async def run(self, messages, options=None):
        # If any tool result exists, yield final and stop
        if any(m.get('role') == 'tool' for m in messages):
            yield {'type': 'final_answer', 'content': 'done'}
            return

        # Otherwise yield plan then tool_calls
        yield {
            'type': 'plan',
            'content': 'plan',
            'plan': 'plan',
            'final_decision': '',
            'agent_status': 'running',
            'tool_choice': {'type': 'function'}
        }
        yield {
            'type': 'tool_calls',
            'tool_calls': self.tool_calls
        }


@pytest.mark.asyncio
async def test_auto_exec_disable_returns_pending_on_custom():
    # One custom tool requested
    tool_calls = [{
        'id': '1',
        'type': 'function',
        'function': {'name': 'calc', 'arguments': json.dumps({'expression': '2+3'})}
    }]
    agent = StubAgent(tool_calls)
    tools = [{
        'type': 'function',
        'function': {
            'name': 'calc',
            'description': 'custom calc',
            'parameters': {'type': 'object', 'properties': {'expression': {'type': 'string'}}, 'required': ['expression']}
        },
        'x_kind': 'custom'
    }]

    async def router(tc, current_msgs):
        return {'success': True, 'content': 5}

    messages = [{'role': 'user', 'content': 'use calc'}]
    pending = await run_with_auto_execution(agent, messages, tools, router, mode='disable')
    assert isinstance(pending, dict) and pending.get('status') == 'tool_calls'
    assert isinstance(pending.get('tool_calls'), list)


@pytest.mark.asyncio
async def test_auto_exec_disable_returns_pending_on_agent():
    tool_calls = [{
        'id': '1',
        'type': 'function',
        'function': {'name': 'agent_worker', 'arguments': json.dumps({'task': 'do'})}
    }]
    agent = StubAgent(tool_calls)
    tools = [{
        'type': 'function',
        'function': {
            'name': 'agent_worker',
            'description': 'agent tool',
            'parameters': {'type': 'object', 'properties': {'task': {'type': 'string'}}, 'required': ['task']}
        },
        'x_kind': 'agent',
        'x_exec': lambda tc, current, context_param=None, options=None: {'success': True, 'content': 'ok'}
    }]

    async def router(tc, current_msgs):
        return {'success': True, 'content': 'ignored'}

    messages = [{'role': 'user', 'content': 'call agent'}]
    pending = await run_with_auto_execution(agent, messages, tools, router, mode='disable')
    assert isinstance(pending, dict) and pending.get('status') == 'tool_calls'


@pytest.mark.asyncio
async def test_auto_exec_auto_runs_custom_and_agent_to_final():
    tool_calls = [
        {'id': '1', 'type': 'function', 'function': {'name': 'calc', 'arguments': json.dumps({'expression': '2+3'})}},
        {'id': '2', 'type': 'function', 'function': {'name': 'agent_worker', 'arguments': json.dumps({'task': 'do'})}},
    ]
    agent = StubAgent(tool_calls)
    tools = [
        {
            'type': 'function',
            'function': {
                'name': 'calc',
                'description': 'custom calc',
                'parameters': {'type': 'object', 'properties': {'expression': {'type': 'string'}}, 'required': ['expression']}
            },
            'x_kind': 'custom'
        },
        {
            'type': 'function',
            'function': {
                'name': 'agent_worker',
                'description': 'agent tool',
                'parameters': {'type': 'object', 'properties': {'task': {'type': 'string'}}, 'required': ['task']}
            },
            'x_kind': 'agent',
            'x_exec': lambda tc, current, context_param=None, options=None: {'success': True, 'content': 'agent_ok'}
        }
    ]

    async def router(tc, current_msgs):
        fn = (tc.get('function') or {}).get('name')
        if fn == 'calc':
            return {'success': True, 'content': 5}
        return {'success': False, 'error': 'unexpected'}

    messages = [{'role': 'user', 'content': 'mix'}]
    final = await run_with_auto_execution(agent, messages, tools, router, mode='auto')
    assert isinstance(final, str) and final == 'done'


@pytest.mark.asyncio
async def test_auto_exec_agent_mode_auto_runs_agent_only():
    tool_calls = [
        {'id': '1', 'type': 'function', 'function': {'name': 'agent_worker', 'arguments': json.dumps({'task': 'go'})}},
        {'id': '2', 'type': 'function', 'function': {'name': 'calc', 'arguments': json.dumps({'expression': '1+1'})}},
    ]
    agent = StubAgent(tool_calls)
    tools = [
        {
            'type': 'function',
            'function': {'name': 'agent_worker', 'description': 'agent', 'parameters': {'type': 'object', 'properties': {'task': {'type': 'string'}}, 'required': ['task']}},
            'x_kind': 'agent',
            'x_exec': lambda tc, current, context_param=None, options=None: {'success': True, 'content': 'ok'}
        },
        {
            'type': 'function',
            'function': {'name': 'calc', 'description': 'custom', 'parameters': {'type': 'object', 'properties': {'expression': {'type': 'string'}}, 'required': ['expression']}},
            'x_kind': 'custom'
        }
    ]

    async def router(tc, current_msgs):
        return {'success': True, 'content': 2}

    messages = [{'role': 'user', 'content': 'agent only'}]
    pending = await run_with_auto_execution(agent, messages, tools, router, mode='agent')
    # Custom tool present while in agent-only mode -> pending tool_calls returned
    assert isinstance(pending, dict) and pending.get('status') == 'tool_calls'


@pytest.mark.asyncio
async def test_auto_exec_tool_mode_auto_runs_custom_only():
    tool_calls = [
        {'id': '1', 'type': 'function', 'function': {'name': 'calc', 'arguments': json.dumps({'expression': '7-2'})}},
        {'id': '2', 'type': 'function', 'function': {'name': 'agent_worker', 'arguments': json.dumps({'task': 'go'})}},
    ]
    agent = StubAgent(tool_calls)
    tools = [
        {
            'type': 'function',
            'function': {'name': 'calc', 'description': 'custom', 'parameters': {'type': 'object', 'properties': {'expression': {'type': 'string'}}, 'required': ['expression']}},
            'x_kind': 'custom'
        },
        {
            'type': 'function',
            'function': {'name': 'agent_worker', 'description': 'agent', 'parameters': {'type': 'object', 'properties': {'task': {'type': 'string'}}, 'required': ['task']}},
            'x_kind': 'agent',
            'x_exec': lambda tc, current, context_param=None, options=None: {'success': True, 'content': 'ok'}
        }
    ]

    async def router(tc, current_msgs):
        return {'success': True, 'content': 5}

    messages = [{'role': 'user', 'content': 'custom only'}]
    pending = await run_with_auto_execution(agent, messages, tools, router, mode='tool')
    # Agent tool present while in tool-only mode -> pending tool_calls returned
    assert isinstance(pending, dict) and pending.get('status') == 'tool_calls'


@pytest.mark.asyncio
async def test_auto_exec_duplicate_tools_raises():
    tool_calls = [{'id': '1', 'type': 'function', 'function': {'name': 'dup', 'arguments': '{}'}}]
    agent = StubAgent(tool_calls)
    tools = [
        {'type': 'function', 'function': {'name': 'dup', 'description': 'a', 'parameters': {'type': 'object', 'properties': {}, 'required': []}}},
        {'type': 'function', 'function': {'name': 'dup', 'description': 'b', 'parameters': {'type': 'object', 'properties': {}, 'required': []}}}
    ]

    async def router(tc, current_msgs):
        return {'success': True, 'content': 'ok'}

    messages = [{'role': 'user', 'content': 'dup'}]
    with pytest.raises(Exception) as ei:
        await run_with_auto_execution(agent, messages, tools, router, mode='auto')
    assert 'Tool Name Collision' in str(ei.value)
