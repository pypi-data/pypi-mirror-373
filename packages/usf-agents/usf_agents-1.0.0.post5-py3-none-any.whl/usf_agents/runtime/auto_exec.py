import json
from typing import List, Dict, Any, Callable, Awaitable, Optional

from ..types import Message, Tool, ToolCall
from ..usfAgent import USFAgent
from ..trace.trace import record_event


_ALLOWED_MODES = {"disable", "auto", "agent", "tool"}


def _validate_unique_names(tools: List[Tool]) -> None:
    names: List[str] = []
    for t in tools or []:
        try:
            fn = (t.get('function') or {}).get('name')  # type: ignore[attr-defined]
        except Exception:
            fn = None
        if fn:
            names.append(fn)
    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        raise Exception(f"Tool Name Collision: duplicate tool names in provided tools: {dupes}")


def _tool_map(tools: List[Tool]) -> Dict[str, Tool]:
    m: Dict[str, Tool] = {}
    for t in tools or []:
        try:
            fn = (t.get('function') or {}).get('name')  # type: ignore[attr-defined]
        except Exception:
            fn = None
        if fn:
            m[fn] = t
    return m


def _is_agent_tool(tool: Optional[Tool]) -> bool:
    if not isinstance(tool, dict):
        return False
    kind = tool.get('x_kind')
    if kind == 'agent':
        return True
    # Fallback heuristic when metadata missing: name prefix "agent_"
    try:
        name = (tool.get('function') or {}).get('name')
    except Exception:
        name = None
    return bool(name and name.startswith('agent_'))


async def run_with_auto_execution(
    agent: USFAgent,
    messages: List[Message],
    tools: List[Tool],
    tool_router: Callable[[ToolCall, List[Message]], Awaitable[Dict[str, Any]]],
    mode: str = "auto",
    max_loops: int = 20
) -> Any:
    """
    Policy-driven orchestration that can auto-execute agent tools and/or custom tools.

    Modes:
      - "disable": Do not auto-run any tools. Returns {'status':'tool_calls', 'tool_calls': [...]} on first tool request.
      - "auto": Auto-run both agent tools and custom tools until final answer (or max_loops).
      - "agent": Auto-run only agent tools; if a custom tool is requested, return pending tool_calls to caller.
      - "tool": Auto-run only custom tools; if an agent tool is requested, return pending tool_calls to caller.

    Returns:
      - Final answer content (str) when a final answer is produced.
      - Or a dict {'status':'tool_calls', 'tool_calls': [...]} if execution is paused based on the mode.
    """
    if mode not in _ALLOWED_MODES:
        raise Exception(f"auto_exec Error: invalid mode '{mode}'. Allowed: {sorted(_ALLOWED_MODES)}")

    _validate_unique_names(tools)
    tmap = _tool_map(tools)

    current: List[Message] = list(messages or [])
    loops = 0

    while loops < max_loops:
        loops += 1
        final_received = False

        async for chunk in agent.run(current, {'tools': tools, 'max_loops': max_loops}):
            ctype = chunk.get('type')

            if ctype == 'plan':
                # preserve plan context
                plan_text = chunk.get('content') or chunk.get('plan') or ''
                current.append({
                    'role': 'assistant',
                    'content': plan_text,
                    'plan': chunk.get('plan'),
                    'final_decision': chunk.get('final_decision'),
                    'agent_status': chunk.get('agent_status'),
                    'tool_choice': chunk.get('tool_choice'),
                    'type': chunk.get('type')
                })
                # Trace: plan event (no-op when tracing disabled)
                try:
                    record_event({'kind': 'plan', 'input': {'content': plan_text}})
                except Exception:
                    pass

            elif ctype == 'tool_calls':
                tool_calls = chunk.get('tool_calls', [])
                # Append assistant tool_calls envelope before results
                current.append({
                    'role': 'assistant',
                    'content': '',
                    'tool_calls': tool_calls,
                    'type': 'tool_calls'
                })
                # Trace: tool_call event
                try:
                    record_event({'kind': 'tool_call', 'input': tool_calls})
                except Exception:
                    pass

                # If disabled, return pending immediately
                if mode == 'disable':
                    return {'status': 'tool_calls', 'tool_calls': tool_calls}

                # Execute each tool_call following policy
                for tc in tool_calls:
                    fn_name = (tc.get('function') or {}).get('name')
                    tool_def = tmap.get(fn_name)
                    is_agent = _is_agent_tool(tool_def)

                    # Decide whether to auto-execute this tool_call under current mode
                    allow_agent = (mode in {'auto', 'agent'})
                    allow_custom = (mode in {'auto', 'tool'})

                    if is_agent:
                        if not allow_agent:
                            # Pause and let caller handle manually
                            return {'status': 'tool_calls', 'tool_calls': tool_calls}

                        # Agent tool auto-execution path: try to use bound x_exec if available
                        exec_fn = None
                        if isinstance(tool_def, dict):
                            exec_fn = tool_def.get('x_exec')  # type: ignore[assignment]

                        if callable(exec_fn):
                            try:
                                # x_exec signature matches SubAgent.execute_as_tool_until_final
                                result = await exec_fn(tc, current, None, {'max_loops': max_loops})  # type: ignore[misc]
                                payload = {
                                    'success': bool(result.get('success')),
                                    'content': result.get('content'),
                                    'error': result.get('error')
                                }
                            except Exception as e:
                                payload = {'success': False, 'error': f'agent tool exec error: {e}'}
                        else:
                            # Fallback: append a placeholder error; developer can provide execution hook if needed
                            payload = {'success': False, 'error': 'agent tool has no execution hook (x_exec) available'}

                        current.append({
                            'role': 'tool',
                            'tool_call_id': tc.get('id'),
                            'name': fn_name,
                            'content': json.dumps(payload, ensure_ascii=False)
                        })
                        # Trace: tool_result event
                        try:
                            record_event({'kind': 'tool_result', 'output': {'name': fn_name, 'payload': payload}})
                        except Exception:
                            pass

                    else:
                        if not allow_custom:
                            return {'status': 'tool_calls', 'tool_calls': tool_calls}

                        # Custom tool: defer to provided router
                        try:
                            payload = await tool_router(tc, current)
                        except Exception as e:
                            payload = {'success': False, 'error': f'custom tool exec error: {e}'}

                        current.append({
                            'role': 'tool',
                            'tool_call_id': tc.get('id'),
                            'name': fn_name,
                            'content': json.dumps(payload, ensure_ascii=False)
                        })
                        # Trace: tool_result event
                        try:
                            record_event({'kind': 'tool_result', 'output': {'name': fn_name, 'payload': payload}})
                        except Exception:
                            pass

                # Re-enter agent.run with the appended tool results
                break

            elif ctype == 'final_answer':
                final_received = True
                # Trace: final event
                try:
                    record_event({'kind': 'final', 'output': chunk.get('content', '')})
                except Exception:
                    pass
                return chunk.get('content', '')

        if final_received:
            break

    # No final answer produced
    return ''


async def run_auto(
    agent: USFAgent,
    messages: List[Message],
    *,
    registry: Optional[Any] = None,
    tools: Optional[List[Tool]] = None,
    router: Optional[Callable[[ToolCall, List[Message]], Awaitable[Dict[str, Any]]]] = None,
    mode: str = "auto",
    max_loops: int = 20
) -> Any:
    """
    Convenience façade for auto execution:
      - If a registry is provided, derive tools and router from it.
      - Otherwise, use provided tools and router.
      - Defaults to mode='auto'.
    """
    resolved_tools: List[Tool] = list(tools or [])
    resolved_router = router

    if registry is not None:
        # Duck-typed registry: expects to_openai_tools() and router()
        if not resolved_tools and hasattr(registry, "to_openai_tools"):
            resolved_tools = registry.to_openai_tools()
        if resolved_router is None and hasattr(registry, "router"):
            resolved_router = registry.router()

    if resolved_router is None:
        async def _noop_router(tc: ToolCall, current_msgs: List[Message]) -> Dict[str, Any]:
            return {"success": False, "error": "no router provided"}
        resolved_router = _noop_router

    return await run_with_auto_execution(
        agent,
        messages,
        resolved_tools,
        resolved_router,
        mode=mode,
        max_loops=max_loops
    )
