from typing import TypedDict, Literal, Optional, List, Dict, Any, Union

# Basic aliases
AgentId = str

# Context passing/inheritance policy for sub-agents
ContextMode = Literal['NONE', 'AGENT_DECIDED', 'ALWAYS_FULL', 'CONTEXT_PARAM']

# Node kinds for workflow graphs
NodeType = Literal['agent', 'tool']


class TaskPayload(TypedDict, total=False):
    """
    High-level payload for invoking a sub-agent as a tool (task-first pattern).
    """
    task: str  # Task name/description/instruction
    input: Dict[str, Any]  # Structured inputs for the sub-agent
    context_param: Optional[Dict[str, Any]]  # Lightweight context when using CONTEXT_PARAM mode
    metadata: Optional[Dict[str, Any]]  # Correlation IDs, run IDs, custom info


class AgentSpec(TypedDict, total=False):
    """
    Public specification for registering an agent in the registry/orchestrator.
    """
    id: AgentId
    name: str
    agent_type: Literal['manager', 'sub', 'generic']
    backstory: Optional[str]
    goal: Optional[str]
    context_mode: ContextMode  # Default policy for this agent when acting as sub-agent
    usf_config: 'USFAgentConfig'  # Reuse existing config typing from types package
    tools: Optional[List['Tool']]  # Native external tools (manager/generic agents only)


class WorkflowNode(TypedDict, total=False):
    """
    A workflow node that references either an agent or a tool.
    """
    id: str
    type: NodeType
    ref: Union[AgentId, str]  # AgentId for agents; tool name for tools
    config: Optional[Dict[str, Any]]  # Per-node overrides (e.g., model, temperature)


class AgentEdge(TypedDict, total=False):
    """
    Directed edge between two nodes with an optional condition expression.
    """
    source: str  # node id
    target: str  # node id
    condition: Optional[str]  # Expression evaluated against run context (e.g., "last.result.success == true")


class WorkflowGraphSpec(TypedDict):
    """
    Graph specification (nodes + edges) that can be validated and executed.
    """
    nodes: List[WorkflowNode]
    edges: List[AgentEdge]


class RouteMessage(TypedDict, total=False):
    """
    Routing envelope for direct or parent-mediated communication between agents.
    """
    from_agent: AgentId
    to_agent: AgentId
    payload: Union['TaskPayload', List['Message']]  # Either a task payload or OpenAI-format messages
    route_via: Literal['direct', 'parent']  # Explicit route choice
    parent_id: Optional[AgentId]  # Applicable when route_via='parent'


class ToolCallExecutionResult(TypedDict, total=False):
    """
    Normalized result for sub-agent-as-tool execution.
    """
    success: bool
    content: str  # Summarized result or response text intended for inclusion in conversation
    error: Optional[str]
    tool_name: str
    raw: Any  # Raw tool/sub-agent response (kept internal and private)


class TraceEvent(TypedDict, total=False):
    """
    A single event in an execution trace to enable transparency and debugging.
    """
    id: str
    ts: float
    kind: Literal[
        'plan',
        'tool_call',
        'tool_result',
        'delegate',
        'message',
        'final',
        'error',
        'decision',
        'route'
    ]
    agent_id: Optional[AgentId]
    node_id: Optional[str]
    input: Optional[Any]
    output: Optional[Any]
    error: Optional[str]
    meta: Optional[Dict[str, Any]]


class Trace(TypedDict, total=False):
    """
    Complete trace artifact for a single workflow/agent run.
    """
    run_id: str
    events: List[TraceEvent]
    status: Literal['running', 'succeeded', 'failed', 'partial']
    started_at: float
    ended_at: Optional[float]


__all__ = [
    'AgentId',
    'ContextMode',
    'NodeType',
    'TaskPayload',
    'AgentSpec',
    'WorkflowNode',
    'AgentEdge',
    'WorkflowGraphSpec',
    'RouteMessage',
    'ToolCallExecutionResult',
    'TraceEvent',
    'Trace'
]
