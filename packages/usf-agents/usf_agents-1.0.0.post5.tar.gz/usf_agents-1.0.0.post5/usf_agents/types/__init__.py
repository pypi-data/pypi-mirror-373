from typing import Dict, List, Any, Optional, Union, AsyncGenerator, TypedDict
from .multi_agent import (
    AgentId,
    ContextMode,
    NodeType,
    TaskPayload,
    AgentSpec,
    WorkflowNode,
    AgentEdge,
    WorkflowGraphSpec,
    RouteMessage,
    ToolCallExecutionResult,
    TraceEvent,
    Trace
)


class USFAgentConfig(TypedDict, total=False):
    # Required
    api_key: str
    
    # Optional global settings
    model: Optional[str]
    provider: Optional[str]
    introduction: Optional[str]
    knowledge_cutoff: Optional[str]
    stream: Optional[bool]
    max_loops: Optional[int]
    # Planning shortcuts
    skip_planning_if_no_tools: Optional[bool]
    
    # User context (applies to all stages)
    backstory: Optional[str]
    goal: Optional[str]
    
    # Stage-specific configurations
    planning: Optional['StageConfig']
    tool_calling: Optional['StageConfig']
    final_response: Optional['StageConfig']
    
    # Memory configuration
    temp_memory: Optional['TempMemoryConfig']


class StageConfig(TypedDict, total=False):
    api_key: Optional[str]
    model: Optional[str]
    provider: Optional[str]
    introduction: Optional[str]
    knowledge_cutoff: Optional[str]
    temperature: Optional[float]
    stop: Optional[List[str]]
    date_time_override: Optional['DateTimeOverride']
    # Allow any additional OpenAI parameters
    # Additional fields can be added dynamically


class DateTimeOverride(TypedDict):
    enabled: bool
    date: str
    time: str
    timezone: str


class TempMemoryConfig(TypedDict, total=False):
    enabled: Optional[bool]
    max_length: Optional[int]
    auto_trim: Optional[bool]


class Message(TypedDict, total=False):
    role: str  # 'system' | 'user' | 'assistant' | 'tool'
    content: str
    tool_calls: Optional[List['ToolCall']]
    tool_name: Optional[str]
    tool_call_id: Optional[str]
    name: Optional[str]
    type: Optional[str]
    plan: Optional[str]
    final_decision: Optional[str]
    agent_status: Optional[str]
    tool_choice: Optional[Any]


class Tool(TypedDict):
    type: str  # 'function'
    function: 'ToolFunction'


class ToolFunction(TypedDict):
    name: str
    description: str
    parameters: 'ToolParameters'


class ToolParameters(TypedDict, total=False):
    type: str
    properties: Dict[str, Any]
    required: Optional[List[str]]


class ToolCall(TypedDict):
    id: str
    type: str  # 'function'
    function: 'ToolCallFunction'


class ToolCallFunction(TypedDict):
    name: str
    arguments: str  # JSON string


class PlanningResult(TypedDict):
    plan: str
    tool_calls: List[ToolCall]


class ToolExecutionResult(TypedDict):
    tool_name: str
    tool_arguments: Dict[str, Any]
    result: str


class FinalResponse(TypedDict):
    content: str


class ToolExample(TypedDict, total=False):
    name: str
    args: Dict[str, Any]
    expect: Optional[Any]
    expect_status: Optional[int]
    timeout_ms: Optional[int]


class ToolRegistrationError(TypedDict, total=False):
    tool_name: str
    example_name: Optional[str]
    error: str


class RunOptions(TypedDict, total=False):
    tools: Optional[List[Tool]]
    planning: Optional[StageConfig]
    tool_calling: Optional[StageConfig]
    final_response: Optional[StageConfig]
    temperature: Optional[float]
    stop: Optional[List[str]]
    max_loops: Optional[int]
    skip_planning_if_no_tools: Optional[bool]
    date_time_override: Optional[DateTimeOverride]
    auto_execution: Optional[str]


class AgentResult(TypedDict, total=False):
    type: str  # 'plan' | 'tool_calls' | 'final_answer'
    content: Optional[str]
    plan: Optional[str]
    final_decision: Optional[str]
    agent_status: Optional[str]
    tool_choice: Optional[Any]
    tool_calls: Optional[List[ToolCall]]


# Export all types
__all__ = [
    'USFAgentConfig',
    'StageConfig', 
    'DateTimeOverride',
    'TempMemoryConfig',
    'Message',
    'Tool',
    'ToolFunction',
    'ToolParameters',
    'ToolCall',
    'ToolCallFunction',
    'PlanningResult',
    'ToolExecutionResult',
    'FinalResponse',
    'ToolExample',
    'ToolRegistrationError',
    'RunOptions',
    'AgentResult',
    # Multi-agent types
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
