from typing import List, Dict, Any, Optional
import time
import uuid
from contextvars import ContextVar

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


# ========== Ultra-light global tracer (opt-in, no-op when disabled) ==========

_current_recorder: ContextVar[Optional[TraceRecorder]] = ContextVar("_current_recorder", default=None)


def set_current_recorder(recorder: Optional[TraceRecorder]) -> None:
    """
    Set the current TraceRecorder for auto-tracing. Pass None to disable.
    """
    _current_recorder.set(recorder)


def get_current_recorder() -> Optional[TraceRecorder]:
    """
    Retrieve the current TraceRecorder if auto-tracing is enabled.
    """
    try:
        return _current_recorder.get()
    except Exception:
        return None


def record_event(event: Dict[str, Any]) -> None:
    """
    Lightweight event emission. No-op when no recorder is active.
    """
    rec = get_current_recorder()
    if rec is None:
        return
    try:
        rec.record(event)
    except Exception:
        # Never let tracing break user flows
        pass


class AutoTrace:
    """
    Context manager to enable auto-tracing with minimal overhead.

    Usage:
        from usf_agents.trace.trace import AutoTrace, TraceRecorder
        with AutoTrace(TraceRecorder()) as rec:
            ... run agents ...
        # rec.snapshot() contains full trace
    """
    def __init__(self, recorder: Optional[TraceRecorder] = None):
        self._recorder = recorder or TraceRecorder()
        self._token = None
        self._run_id: Optional[str] = None

    def __enter__(self) -> TraceRecorder:
        self._run_id = self._recorder.start()
        # Save token to restore previous recorder on exit
        self._token = _current_recorder.set(self._recorder)
        return self._recorder

    def __exit__(self, exc_type, exc, tb):
        try:
            status = 'succeeded' if exc_type is None else 'failed'
            self._recorder.end(status=status)
        finally:
            # Restore previous recorder (if any)
            if self._token is not None:
                _current_recorder.reset(self._token)
