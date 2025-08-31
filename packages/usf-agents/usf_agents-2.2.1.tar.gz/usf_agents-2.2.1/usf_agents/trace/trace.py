from typing import List, Dict, Any, Optional
import time
import uuid

from ..types.multi_agent import Trace, TraceEvent


class TraceRecorder:
    """
    In-memory trace recorder for a single run. Use TraceStore to retrieve by run_id.
    """
    def __init__(self):
        self._run_id: Optional[str] = None
        self._events: List[TraceEvent] = []
        self._status: str = 'running'
        self._started_at: float = 0.0
        self._ended_at: Optional[float] = None

    def start(self, run_id: Optional[str] = None) -> str:
        self._run_id = run_id or str(uuid.uuid4())
        self._events = []
        self._status = 'running'
        self._started_at = time.time()
        self._ended_at = None
        return self._run_id

    def record(self, event: TraceEvent) -> None:
        if not self._run_id:
            self.start()
        # Ensure required fields
        ev: TraceEvent = {
            'id': event.get('id') or str(uuid.uuid4()),
            'ts': event.get('ts') or time.time(),
            'kind': event.get('kind', 'message'),
            'agent_id': event.get('agent_id'),
            'node_id': event.get('node_id'),
            'input': event.get('input'),
            'output': event.get('output'),
            'error': event.get('error'),
            'meta': event.get('meta')
        }
        self._events.append(ev)

    def end(self, status: str = 'succeeded') -> None:
        self._status = status
        self._ended_at = time.time()

    def snapshot(self) -> Trace:
        return {
            'run_id': self._run_id or '',
            'events': list(self._events),
            'status': self._status,  # type: ignore
            'started_at': self._started_at,
            'ended_at': self._ended_at
        }


class TraceStore:
    """
    Simple in-memory store mapping run_id -> Trace.
    """
    def __init__(self):
        self._traces: Dict[str, Trace] = {}

    def put(self, trace: Trace) -> None:
        self._traces[trace['run_id']] = trace

    def get(self, run_id: str) -> Optional[Trace]:
        return self._traces.get(run_id)
