from typing import Dict, Set, List, Optional

from ..types.multi_agent import AgentId
from .base import BaseAgentWrapper


class AgentRegistry:
    """
    In-memory registry for agents and their relationships.
    - Non-exclusive: any agent can be a child (sub-agent) of multiple parents.
    - No enforced hierarchy: forms an arbitrary directed graph.
    """

    def __init__(self):
        self._agents: Dict[AgentId, BaseAgentWrapper] = {}
        self._children: Dict[AgentId, Set[AgentId]] = {}
        self._parents: Dict[AgentId, Set[AgentId]] = {}

    def add_agent(self, agent: BaseAgentWrapper) -> None:
        if not agent or not agent.id:
            raise Exception("AgentRegistry Error: agent with valid id is required")
        self._agents[agent.id] = agent
        # Initialize relation sets to avoid KeyErrors later
        self._children.setdefault(agent.id, set())
        self._parents.setdefault(agent.id, set())

    def get(self, agent_id: AgentId) -> BaseAgentWrapper:
        if agent_id not in self._agents:
            raise KeyError(f"AgentRegistry Error: agent '{agent_id}' not found")
        return self._agents[agent_id]

    def has(self, agent_id: AgentId) -> bool:
        return agent_id in self._agents

    def add_relation(self, parent: AgentId, child: AgentId) -> None:
        """
        Declare 'child' as a sub-agent of 'parent'. This does not restrict the child
        from having other parents; no hierarchy is enforced.
        """
        if parent not in self._agents:
            raise KeyError(f"AgentRegistry Error: parent '{parent}' not registered")
        if child not in self._agents:
            raise KeyError(f"AgentRegistry Error: child '{child}' not registered")

        self._children.setdefault(parent, set()).add(child)
        self._parents.setdefault(child, set()).add(parent)

    def neighbors(self, agent_id: AgentId) -> List[AgentId]:
        """
        Return all direct children (outgoing neighbors) of an agent.
        """
        return list(self._children.get(agent_id, set()))

    def get_children(self, parent: AgentId) -> List[AgentId]:
        return list(self._children.get(parent, set()))

    def get_parents(self, child: AgentId) -> List[AgentId]:
        return list(self._parents.get(child, set()))

    def all_agents(self) -> List[AgentId]:
        return list(self._agents.keys())
