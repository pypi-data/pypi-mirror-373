from typing import Dict, Set, List, Optional
import uuid
import time

from ..types import Message
from ..types.multi_agent import RouteMessage, AgentId
from .registry import AgentRegistry


class TTLGuardError(Exception):
    pass


class MessageBus:
    """
    Lightweight message/task routing between agents with direct or parent-mediated paths.
    Provides simple TTL/recursion guard helpers via hop tracking per run_id.
    """

    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        # Allowed direct communications
        self._direct: Dict[AgentId, Set[AgentId]] = {}
        # Parent links for mediated routing (advisory for enforcement/inspection)
        self._parents: Dict[AgentId, Set[AgentId]] = {}
        # Hop/cycle guard state per run_id
        self._hops: Dict[str, int] = {}

    def set_parent(self, agent_id: AgentId, parent_id: AgentId) -> None:
        self._parents.setdefault(agent_id, set()).add(parent_id)

    def enable_direct(self, agent_a: AgentId, agent_b: AgentId) -> None:
        self._direct.setdefault(agent_a, set()).add(agent_b)
        self._direct.setdefault(agent_b, set()).add(agent_a)

    def guard_ttl(self, run_id: str, max_hops: int) -> None:
        hops = self._hops.get(run_id, 0) + 1
        self._hops[run_id] = hops
        if hops > max_hops:
            raise TTLGuardError(f"TTL exceeded for run_id={run_id}: hops={hops} > max_hops={max_hops}")

    def reset_ttl(self, run_id: str) -> None:
        if run_id in self._hops:
            del self._hops[run_id]

    def can_direct(self, src: AgentId, dst: AgentId) -> bool:
        return dst in self._direct.get(src, set())

    def has_parent(self, agent_id: AgentId, parent_id: AgentId) -> bool:
        return parent_id in self._parents.get(agent_id, set())

    def send(self, route: RouteMessage) -> None:
        """
        Validate routing request. This function is a guard/registry-aware check.
        Actual execution/messaging is orchestrated elsewhere (e.g., workflow engine).
        """
        if not self.registry.has(route['from_agent']):
            raise KeyError(f"Bus Error: from_agent '{route['from_agent']}' not registered")
        if not self.registry.has(route['to_agent']):
            raise KeyError(f"Bus Error: to_agent '{route['to_agent']}' not registered")

        via = route.get('route_via', 'direct')
        if via == 'direct':
            if not self.can_direct(route['from_agent'], route['to_agent']):
                # Allow even if not explicitly enabled; system is permissive by default but warns
                # Developers can enforce strict mode by checking can_direct() beforehand
                pass
        elif via == 'parent':
            parent_id = route.get('parent_id')
            if not parent_id:
                raise ValueError("Bus Error: parent_id is required for parent-mediated routes")
            # Advisory: Ensure the declared parent relationship exists
            if not self.has_parent(route['to_agent'], parent_id):
                # Also allow permissively but warn in strict setups
                pass
        else:
            raise ValueError(f"Bus Error: unknown route_via '{via}'")

        # No message dispatch here. This is a validation gate to be used by orchestrators.
        return
