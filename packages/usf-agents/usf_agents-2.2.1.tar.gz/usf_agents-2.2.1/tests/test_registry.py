import asyncio
import pytest

from usf_agents.multi_agent.registry import AgentRegistry
from usf_agents.multi_agent.base import SubAgent, ManagerAgent


def make_agent(agent_id: str, agent_type: str = 'sub'):
    spec = {
        'id': agent_id,
        'name': f'Agent {agent_id}',
        'agent_type': agent_type,
        'context_mode': 'NONE',
        'usf_config': {
            'api_key': 'DUMMY_KEY',  # Replace with real key for integration tests
            'model': 'usf-mini'
        }
    }
    if agent_type == 'manager':
        return ManagerAgent(spec)
    return SubAgent(spec)


def test_registry_add_and_get():
    reg = AgentRegistry()
    a = make_agent('A')
    b = make_agent('B', agent_type='manager')

    reg.add_agent(a)
    reg.add_agent(b)

    assert reg.has('A')
    assert reg.has('B')

    assert reg.get('A').id == 'A'
    assert reg.get('B').id == 'B'

    with pytest.raises(KeyError):
        reg.get('C')


def test_relations_non_exclusive():
    reg = AgentRegistry()
    a = make_agent('A', agent_type='manager')
    b = make_agent('B')
    c = make_agent('C')

    reg.add_agent(a)
    reg.add_agent(b)
    reg.add_agent(c)

    reg.add_relation('A', 'B')
    reg.add_relation('A', 'C')
    # C is also child of B (non-exclusive)
    reg.add_relation('B', 'C')

    assert set(reg.get_children('A')) == {'B', 'C'}
    assert set(reg.get_children('B')) == {'C'}
    assert set(reg.get_parents('C')) == {'A', 'B'}
    assert reg.get_parents('B') == ['A'] or set(reg.get_parents('B')) == {'A'}


def test_all_agents():
    reg = AgentRegistry()
    for i in range(3):
        reg.add_agent(make_agent(f'X{i}'))
    assert set(reg.all_agents()) == {'X0', 'X1', 'X2'}
