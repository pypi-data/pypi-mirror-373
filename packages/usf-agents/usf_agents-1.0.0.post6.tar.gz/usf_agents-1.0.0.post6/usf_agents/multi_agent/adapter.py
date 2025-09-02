import json
from typing import Dict, Any, Optional, List, TYPE_CHECKING

from ..types import Tool, ToolCall, Message, RunOptions
from ..types.multi_agent import (
    ContextMode,
    TaskPayload,
    ToolCallExecutionResult,
)

if TYPE_CHECKING:
    from .base import SubAgent  # for type hints only


def make_agent_tool(sub_agent: 'SubAgent', schema: Dict[str, Any], alias: Optional[str] = None) -> Tool:
    """
    Generate an OpenAI-compatible tool definition that invokes a SubAgent.
    The tool does not expose the sub-agent's internal tools or memory.
    """
    tool_name = alias or f"agent_{sub_agent.id}"
    return {
        'type': 'function',
        'function': {
            'name': tool_name,
            'description': schema.get('description', f"Invoke sub-agent {sub_agent.name} ({sub_agent.id})"),
            'parameters': schema.get('parameters', {
                'type': 'object',
                'properties': {
                    'task': {'type': 'string', 'description': 'Task name/description'},
                    'additional_context': {'type': 'object', 'description': 'Lightweight context object'}
                },
                'required': ['task']
            })
        },
        # metadata to distinguish agent tools at runtime (ignored by OpenAI schema)
        'x_kind': 'agent',
        'x_agent_id': getattr(sub_agent, 'id', None),
        'x_alias': alias,
        'x_exec': getattr(sub_agent, 'execute_as_tool_until_final', None)
    }


async def handle_agent_tool_call(
    sub_agent: 'SubAgent',
    tool_call: ToolCall,
    calling_context: Optional[List[Message]],
    mode: ContextMode,
    context_param: Optional[Dict[str, Any]] = None,
    options: Optional[RunOptions] = None
) -> ToolCallExecutionResult:
    """
    Execute a SubAgent when invoked via tool-calls coming from a manager agent.
    This handles argument parsing, context shaping, and returns a normalized result.
    """
    try:
        func = tool_call.get('function') or {}
        tool_name = func.get('name') or f"agent_{sub_agent.id}"
        raw_args = func.get('arguments') or '{}'
        try:
            args = json.loads(raw_args)
        except Exception:
            args = {'task': str(raw_args)}

        task: TaskPayload = {
            'task': args.get('task') or 'task',
            'input': {},
            'metadata': args.get('metadata') or {}
        }

        # Allow explicit context_param override at call-time (mapped from additional_context in public schema)
        call_context_param = context_param if context_param is not None else args.get('additional_context')

        # Temporarily override policy if mode is provided explicitly
        # We do not mutate sub_agent.context_mode, only use for this call.
        from .context import shape_context_for_mode
        shaped_messages = shape_context_for_mode(
            mode,
            task,
            calling_agent_msgs=calling_context,
            context_param=call_context_param
        )

        # Use the underlying USFAgent to run with shaped messages
        from .base import _acollect_final_answer
        collected = await _acollect_final_answer(sub_agent.usf, shaped_messages, options)

        if collected['status'] == 'final':
            return {
                'success': True,
                'content': collected.get('content') or '',
                'error': None,
                'tool_name': tool_name,
                'raw': collected
            }
        if collected['status'] == 'tool_calls':
            return {
                'success': False,
                'content': '',
                'error': 'Sub-agent requested tool_calls; external execution required.',
                'tool_name': tool_name,
                'raw': collected
            }
        return {
            'success': False,
            'content': '',
            'error': 'Sub-agent returned no final content.',
            'tool_name': tool_name,
            'raw': collected
        }
    except Exception as e:
        return {
            'success': False,
            'content': '',
            'error': f'handle_agent_tool_call error: {e}',
            'tool_name': tool_call.get('function', {}).get('name', f"agent_{sub_agent.id}"),
            'raw': None
        }
