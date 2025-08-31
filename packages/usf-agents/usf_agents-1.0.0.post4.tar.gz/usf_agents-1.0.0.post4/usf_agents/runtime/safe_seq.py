import json
from typing import List, Dict, Any, Callable, Awaitable, Optional

from ..types import Message, Tool, ToolCall
from ..usfAgent import USFAgent


async def run_until_final(
    agent: USFAgent,
    messages: List[Message],
    tools: List[Tool],
    tool_router: Callable[[ToolCall, List[Message]], Awaitable[Dict[str, Any]]],
    max_loops: int = 20
) -> str:
    """
    Drive a USFAgent run loop until a final answer is produced, enforcing strict sequencing.

    - Appends assistant 'plan' messages (to allow USFAgent to correlate tool results).
    - On 'tool_calls', appends the assistant tool_calls envelope, executes tools via tool_router,
      appends role:'tool' messages with exact tool_call_id, then re-enters run().
    - Returns the final answer content string.

    NOTE: Do not append any user/assistant content between assistant tool_calls and tool results.
    """
    current: List[Message] = list(messages or [])
    loops = 0

    while loops < max_loops:
        loops += 1
        final_received = False

        async for chunk in agent.run(current, {'tools': tools, 'max_loops': max_loops}):
            ctype = chunk.get('type')

            if ctype == 'plan':
                # Keep the plan message so USFAgent can continue its internal state with tool results.
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

            elif ctype == 'tool_calls':
                tool_calls = chunk.get('tool_calls', [])
                # Append assistant tool_calls envelope (required before tool results)
                current.append({
                    'role': 'assistant',
                    'content': '',
                    'tool_calls': tool_calls,
                    'type': 'tool_calls'
                })

                # Execute tools immediately and append tool results
                for tc in tool_calls:
                    payload = await tool_router(tc, current)
                    current.append({
                        'role': 'tool',
                        'tool_call_id': tc.get('id'),
                        'name': (tc.get('function') or {}).get('name'),
                        'content': json.dumps(payload, ensure_ascii=False)
                    })

                # Break to re-enter agent.run() with updated messages
                break

            elif ctype == 'final_answer':
                final_received = True
                return chunk.get('content', '')

        if final_received:
            break

    # If final not received, return empty string (caller may treat as error)
    return ''
