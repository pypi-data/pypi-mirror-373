from typing import List, Dict, Any, Optional
import json

from ..types import Message  # OpenAI-format message type
from ..types import RunOptions  # For completeness if needed by callers
from ..types import Tool  # Type reference (not used here directly)

from ..types.multi_agent import (
    ContextMode,
    TaskPayload,
)


def _task_to_user_content(task: TaskPayload) -> str:
    """
    Format a TaskPayload into a concise user message string for delegated work.
    Only include the task instruction to avoid confusing synthetic JSON payloads.
    """
    task_name = task.get('task') or 'task'
    return str(task_name)


def to_openai_messages_from_task(
    task: TaskPayload,
    introduction: str = '',
    knowledge_cutoff: str = '',
    backstory: str = '',
    goal: str = '',
    date_time_override: Optional[Dict[str, Any]] = None
) -> List[Message]:
    """
    Construct minimal OpenAI-format messages from a TaskPayload for an agent acting
    as a main entry point (message-based flow). The final response stage will add
    system/date context. For planning/tool-calling we just need user intent.
    """
    content = _task_to_user_content(task)
    return [
        {'role': 'user', 'content': content}
    ]


def sanitize_parent_context(msgs: Optional[List[Message]]) -> List[Message]:
    """
    Strictly sanitize parent context before delegating to sub-agents.

    Keep:
      - role == 'user'
      - role == 'assistant' messages that are likely final answers:
          * no 'tool_calls'
          * no 'plan' field
          * type not in {'agent_plan', 'tool_calls'}

    Drop:
      - any role == 'tool'
      - any assistant with 'tool_calls'
      - assistant planning artifacts (e.g., type == 'agent_plan' or with 'plan' key)
    """
    if not msgs:
        return []

    clean: List[Message] = []
    for m in msgs:
        role = m.get('role')
        if role == 'user':
            clean.append(m)
            continue
        if role == 'tool':
            continue
        if role == 'assistant':
            if m.get('tool_calls'):
                continue
            mtype = m.get('type')
            if mtype in ('agent_plan', 'tool_calls'):
                continue
            if 'plan' in m:
                continue
            # Treat as final-answer-like assistant content
            clean.append(m)
            continue
        # Ignore other roles by default
    return clean


def shape_context_for_mode(
    mode: ContextMode,
    task: TaskPayload,
    calling_agent_msgs: Optional[List[Message]] = None,
    context_param: Optional[Dict[str, Any]] = None
) -> List[Message]:
    """
    Build OpenAI-format messages for sub-agent execution based on ContextMode.

    - NONE: do not pass caller transcript; only pass TaskPayload as a fresh user message.
    - AGENT_DECIDED: if caller messages are provided, treat as ALWAYS_FULL; else NONE.
      (Decision is expected to be made by the calling agent; this heuristic provides a sane default.)
    - ALWAYS_FULL: pass the full calling agent messages (as-is, in order), then append a final
      user message encoding the TaskPayload so the sub-agent knows the delegated objective.
    - CONTEXT_PARAM: do not pass full transcript; instead create a compact system context from
      context_param and a user message from TaskPayload.

    Privacy Guarantee:
    - This function never leaks sub-agent internal tools/memory; it only shapes caller→callee context.
    """
    messages: List[Message] = []

    if mode == 'NONE':
        # Fresh context with only the delegated task
        messages = [{'role': 'user', 'content': _task_to_user_content(task)}]
        return messages

    if mode == 'AGENT_DECIDED':
        # If caller provided messages, treat as ALWAYS_FULL; otherwise fallback to NONE
        if calling_agent_msgs and len(calling_agent_msgs) > 0:
            mode = 'ALWAYS_FULL'
        else:
            mode = 'NONE'
        return shape_context_for_mode(mode, task, calling_agent_msgs, context_param)

    if mode == 'ALWAYS_FULL':
        # Use caller transcript as-is, then append explicit delegation instruction
        base: List[Message] = list(calling_agent_msgs or [])
        base.append({'role': 'user', 'content': _task_to_user_content(task)})
        return base

    if mode == 'CONTEXT_PARAM':
        # Lightweight, explicit context only — no full transcript
        sys_parts = []
        if isinstance(context_param, dict) and context_param:
            sys_parts.append("Delegation context provided by caller:")
            try:
                sys_parts.append(json.dumps(context_param, ensure_ascii=False, separators=(',', ':')))
            except Exception:
                # Fallback to repr if JSON serialization fails
                sys_parts.append(repr(context_param))

        if sys_parts:
            messages.append({'role': 'system', 'content': '\n'.join(sys_parts)})

        messages.append({'role': 'user', 'content': _task_to_user_content(task)})
        return messages

    # Fallback safety: treat unknown modes as NONE
    return [{'role': 'user', 'content': _task_to_user_content(task)}]


def build_messages_for_final(
    messages: List[Message],
    introduction: str,
    knowledge_cutoff: str,
    backstory: str,
    goal: str,
    date_time_override: Optional[Dict[str, Any]]
) -> List[Message]:
    """
    Wrapper for final-response message shaping that leverages the existing
    process_messages_for_final_response pipeline to ensure consistency
    (introduction, knowledge cutoff, and timestamp injection).
    """
    from ..usfMessageHandler import process_messages_for_final_response  # Local import to avoid cycles
    return process_messages_for_final_response(
        messages=messages,
        date_time_override=date_time_override,
        backstory=backstory or '',
        goal=goal or '',
        introduction=introduction or '',
        knowledge_cutoff=knowledge_cutoff or ''
    )
