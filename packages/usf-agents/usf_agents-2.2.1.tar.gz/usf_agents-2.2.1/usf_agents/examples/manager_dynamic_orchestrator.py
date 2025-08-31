import os
import json
import asyncio
from typing import Dict, List, Any

from usf_agents import SubAgent, ManagerAgent


"""
Dynamic, planner-driven complex orchestration example.

- A ManagerAgent exposes multiple SubAgents as tools
- The LLM planner decides which "tools" (sub-agents) to call, in what order
- We execute tool_calls by invoking the appropriate SubAgent with proper context policy
- We continue the plan → tool_calls → tool_results loop until a final answer is produced

Requirements to run:
- Set USF_API_KEY env var, or this script will try a fallback value for demo (NOT recommended).
- Ensure internet connectivity for USF API access.

Run:
  USF_API_KEY=YOUR_KEY python -m usf_agents.examples.manager_dynamic_orchestrator
"""


def build_manager_and_subagents(api_key: str):
    # Sub-agents with chosen context policies
    calculator = SubAgent({
        'id': 'calc',
        'name': 'Calculator',
        'agent_type': 'sub',
        'context_mode': 'NONE',  # No parent transcript
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })

    researcher = SubAgent({
        'id': 'research',
        'name': 'Researcher',
        'agent_type': 'sub',
        'context_mode': 'AGENT_DECIDED',  # Receives full transcript if provided
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })

    coder = SubAgent({
        'id': 'coder',
        'name': 'Code Assistant',
        'agent_type': 'sub',
        'context_mode': 'CONTEXT_PARAM',  # Lightweight explicit context only
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })

    writer = SubAgent({
        'id': 'writer',
        'name': 'Writer',
        'agent_type': 'sub',
        'context_mode': 'ALWAYS_FULL',  # Always receives full transcript
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })

    manager = ManagerAgent({
        'id': 'mgr',
        'name': 'Dynamic Orchestrator',
        'agent_type': 'manager',
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })

    # Provide schemas and stable tool names (aliases) to the manager
    # We'll map these tool names to sub-agents below for execution routing
    manager.add_sub_agent(calculator, {
        'description': 'Calculator for numeric computations',
        'parameters': {
            'type': 'object',
            'properties': {
                'task': {'type': 'string'},
                'input': {'type': 'object'},
                'context_param': {'type': 'object'}
            },
            'required': ['task']
        }
    }, alias='agent_calc')

    manager.add_sub_agent(researcher, {
        'description': 'Researcher for market/knowledge queries',
        'parameters': {
            'type': 'object',
            'properties': {
                'task': {'type': 'string'},
                'input': {'type': 'object'},
                'context_param': {'type': 'object'}
            },
            'required': ['task']
        }
    }, alias='agent_research')

    manager.add_sub_agent(coder, {
        'description': 'Coder for generating concise code snippets',
        'parameters': {
            'type': 'object',
            'properties': {
                'task': {'type': 'string'},
                'input': {'type': 'object'},
                'context_param': {'type': 'object'}
            },
            'required': ['task']
        }
    }, alias='agent_coder')

    manager.add_sub_agent(writer, {
        'description': 'Writer to compose a final executive summary',
        'parameters': {
            'type': 'object',
            'properties': {
                'task': {'type': 'string'},
                'input': {'type': 'object'},
                'context_param': {'type': 'object'}
            },
            'required': ['task']
        }
    }, alias='agent_writer')

    # Name -> SubAgent mapping for tool execution
    tool_to_agent = {
        'agent_calc': calculator,
        'agent_research': researcher,
        'agent_coder': coder,
        'agent_writer': writer
    }

    return manager, tool_to_agent


def build_complex_requirement() -> str:
    return (
        "For the product 'UltraWidget':\n"
        "- Calculate the total manufacturing cost given parts [12.5, 19.9, 4.6]\n"
        "- Research two key market trends in 2025 relevant to consumer electronics\n"
        "- Generate Python code for a function total_cost(prices: list[float]) -> float\n"
        "- Finally, write a concise executive report combining all results for an executive"
    )


async def run_dynamic_orchestration(api_key: str) -> Dict[str, Any]:
    manager, tool_to_agent = build_manager_and_subagents(api_key)

    # Single user requirement that includes multiple sub-queries
    user_requirement = build_complex_requirement()

    # Initialize conversation
    messages: List[Dict[str, Any]] = [
        {'role': 'user', 'content': user_requirement}
    ]

    # Simple run loop until final answer
    final_answer: str = ''
    max_rounds = 12
    round_idx = 0

    print("Starting dynamic orchestration with LLM planner...")
    print("Tools available to manager:", [t['function']['name'] for t in manager.list_tools()])

    while round_idx < max_rounds:
        round_idx += 1
        print(f"\n--- Planning Round {round_idx} ---")
        final_received = False

        async for result in manager.usf.run(messages, {'tools': manager.list_tools()}):
            rtype = result.get('type')
            if rtype == 'plan':
                # Record the plan content
                plan_text = result.get('plan') or result.get('content') or ''
                print("Plan:", plan_text[:500])
                messages.append({
                    'role': 'assistant',
                    'content': plan_text,
                    'type': 'agent_plan'
                })

            elif rtype == 'tool_calls':
                tool_calls = result.get('tool_calls', [])
                print("Tool calls:", [tc['function']['name'] for tc in tool_calls])

                # Add tool call message to conversation
                messages.append({
                    'role': 'assistant',
                    'content': '',
                    'tool_calls': tool_calls
                })

                # Execute each tool call by delegating to the mapped SubAgent
                for tool_call in tool_calls:
                    func = tool_call.get('function', {})
                    tool_name = func.get('name')
                    sub = tool_to_agent.get(tool_name)

                    if not sub:
                        # Unknown tool request; return an error tool result
                        tool_result = {
                            'role': 'tool',
                            'tool_call_id': tool_call.get('id'),
                            'name': tool_name,
                            'content': json.dumps({'error': f'Unknown tool {tool_name}'})
                        }
                        messages.append(tool_result)
                        print(f"Unknown tool requested: {tool_name}")
                        continue

                    # Provide calling context and/or context_param based on the sub-agent policy
                    # - AGENT_DECIDED / ALWAYS_FULL benefit from passing transcript
                    # - CONTEXT_PARAM expects a small explicit context only
                    calling_context = messages  # safe to pass; sub-agent policy controls actual shaping
                    context_param = None
                    if sub.context_mode == 'CONTEXT_PARAM':
                        context_param = {'style': 'concise', 'language': 'python'}

                    res = await sub.execute_as_tool(
                        tool_call=tool_call,
                        calling_context=calling_context,
                        context_param=context_param
                    )

                    # Convert SubAgent result to a tool message for the LLM
                    content_payload = {
                        'success': res.get('success'),
                        'content': res.get('content'),
                        'error': res.get('error')
                    }
                    tool_result = {
                        'role': 'tool',
                        'tool_call_id': tool_call.get('id'),
                        'name': tool_name,
                        'content': json.dumps(content_payload, ensure_ascii=False)
                    }
                    messages.append(tool_result)
                    print(f"Executed {tool_name}: success={res.get('success')}")

                # Break to continue planning with tool results
                break

            elif rtype == 'final_answer':
                final_answer = result.get('content', '')
                print("\n--- Final Answer ---")
                print(final_answer)
                final_received = True
                break

        if final_received:
            break

    return {
        'final_answer': final_answer,
        'messages_len': len(messages)
    }


async def main():
    api_key = os.getenv('USF_API_KEY') or "0546a8c6-12a5-4ebf-9b0a-e6ef35de6ac1"
    if not api_key or api_key.strip() == "":
        raise RuntimeError("USF_API_KEY is required to run the dynamic orchestrator example.")

    result = await run_dynamic_orchestration(api_key)
    print("\nConversation length:", result['messages_len'])


if __name__ == '__main__':
    asyncio.run(main())
