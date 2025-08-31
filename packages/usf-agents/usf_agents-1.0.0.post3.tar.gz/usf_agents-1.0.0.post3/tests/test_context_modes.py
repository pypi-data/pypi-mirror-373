import json
from usf_agents.multi_agent.context import shape_context_for_mode
from usf_agents.types import Message
from usf_agents.types.multi_agent import TaskPayload


def _mk_msgs(n=2):
    return [
        {'role': 'user', 'content': f'user-{i}'} for i in range(n)
    ] + [
        {'role': 'assistant', 'content': f'assistant-{i}'} for i in range(n)
    ]


def test_context_mode_none_ignores_calling_transcript():
    task: TaskPayload = {'task': 'do', 'input': {'x': 1}}
    calling = _mk_msgs()
    msgs = shape_context_for_mode('NONE', task, calling_agent_msgs=calling)
    assert isinstance(msgs, list)
    # Should only contain a single user message with the delegated task content
    assert len(msgs) == 1
    assert msgs[0]['role'] == 'user'
    assert msgs[0]['content'] == 'do'
    # Ensure no calling transcript leaked
    assert 'user-0' not in msgs[0]['content']
    assert 'assistant-0' not in msgs[0]['content']


def test_context_mode_always_full_includes_calling_transcript():
    task: TaskPayload = {'task': 'do', 'input': {'x': 2}}
    calling = _mk_msgs()
    msgs = shape_context_for_mode('ALWAYS_FULL', task, calling_agent_msgs=calling)
    # Should start with the calling transcript and end with a final user message encoding the task
    assert len(msgs) == len(calling) + 1
    assert msgs[-1]['role'] == 'user'
    assert msgs[-1]['content'] == 'do'
    # Ensure transcript preserved
    assert any(m.get('content') == 'user-0' for m in msgs)


def test_context_mode_context_param_has_system_and_task_user():
    task: TaskPayload = {'task': 'do', 'input': {'x': 3}}
    context_param = {'hints': ['alpha', 'beta']}
    msgs = shape_context_for_mode('CONTEXT_PARAM', task, context_param=context_param)
    # System + user messages
    assert len(msgs) == 2
    assert msgs[0]['role'] == 'system'
    assert 'Delegation context provided by caller:' in msgs[0]['content']
    assert 'alpha' in msgs[0]['content']
    assert msgs[1]['role'] == 'user'
    assert msgs[1]['content'] == 'do'


def test_context_mode_agent_decided_behaves_like_always_full_when_calling_present():
    task: TaskPayload = {'task': 'do', 'input': {'x': 4}}
    calling = _mk_msgs()
    msgs = shape_context_for_mode('AGENT_DECIDED', task, calling_agent_msgs=calling)
    # Should behave like ALWAYS_FULL since calling provided
    assert len(msgs) == len(calling) + 1
    assert msgs[-1]['role'] == 'user'
    assert any(m.get('content') == 'user-1' for m in msgs)


def test_context_mode_agent_decided_behaves_like_none_when_no_calling():
    task: TaskPayload = {'task': 'do', 'input': {'x': 5}}
    msgs = shape_context_for_mode('AGENT_DECIDED', task, calling_agent_msgs=None)
    assert len(msgs) == 1
    assert msgs[0]['role'] == 'user'
    assert msgs[0]['content'] == 'do'
