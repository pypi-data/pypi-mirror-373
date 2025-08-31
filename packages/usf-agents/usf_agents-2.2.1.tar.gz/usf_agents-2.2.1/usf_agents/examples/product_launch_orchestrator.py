import os
import json
import asyncio
from typing import Dict, List, Any

from usf_agents import SubAgent, ManagerAgent


"""
Product Launch Orchestrator (Dynamic, Planner-Driven)

Given a single product launch brief, the manager dynamically coordinates:
- RequirementsExtractor (ALWAYS_FULL): extract actionable requirements/constraints
- Planner               (NONE): build rough timeline/cost (no transcript leakage)
- RiskResearcher        (AGENT_DECIDED): identify top risks and mitigation
- Writer                (ALWAYS_FULL): produce launch email + internal briefing

Run:
  USF_API_KEY=YOUR_KEY python -m usf_agents.examples.product_launch_orchestrator
"""


def build_manager_and_subagents(api_key: str):
    req = SubAgent({
        'id': 'requirements',
        'name': 'Requirements Extractor',
        'agent_type': 'sub',
        'context_mode': 'ALWAYS_FULL',
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })
    planner = SubAgent({
        'id': 'planner',
        'name': 'Timeline & Cost Planner',
        'agent_type': 'sub',
        'context_mode': 'NONE',
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })
    risk = SubAgent({
        'id': 'risk',
        'name': 'Risk Researcher',
        'agent_type': 'sub',
        'context_mode': 'AGENT_DECIDED',
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })
    writer = SubAgent({
        'id': 'writer',
        'name': 'Comms Writer',
        'agent_type': 'sub',
        'context_mode': 'ALWAYS_FULL',
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })

    manager = ManagerAgent({
        'id': 'pl_mgr',
        'name': 'Launch Orchestrator',
        'agent_type': 'manager',
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })

    manager.add_sub_agent(req, {
        'description': 'Extract requirements/constraints from brief',
        'parameters': {
            'type': 'object',
            'properties': {'task': {'type': 'string'}, 'input': {'type': 'object'}, 'context_param': {'type': 'object'}},
            'required': ['task']
        }
    }, alias='agent_requirements')

    manager.add_sub_agent(planner, {
        'description': 'Build rough timeline and cost plan',
        'parameters': {
            'type': 'object',
            'properties': {'task': {'type': 'string'}, 'input': {'type': 'object'}, 'context_param': {'type': 'object'}},
            'required': ['task']
        }
    }, alias='agent_planner')

    manager.add_sub_agent(risk, {
        'description': 'Identify top risks and mitigation',
        'parameters': {
            'type': 'object',
            'properties': {'task': {'type': 'string'}, 'input': {'type': 'object'}, 'context_param': {'type': 'object'}},
            'required': ['task']
        }
    }, alias='agent_risk')

    manager.add_sub_agent(writer, {
        'description': 'Produce launch email and internal briefing',
        'parameters': {
            'type': 'object',
            'properties': {'task': {'type': 'string'}, 'input': {'type': 'object'}, 'context_param': {'type': 'object'}},
            'required': ['task']
        }
    }, alias='agent_writer')

    tool_to_agent = {
        'agent_requirements': req,
        'agent_planner': planner,
        'agent_risk': risk,
        'agent_writer': writer
    }
    return manager, tool_to_agent


def launch_brief() -> str:
    return (
        "Launch Brief for 'UltraWidget Pro':\n"
        "- Target date window: Q4 2025 (preferred November)\n"
        "- Regions: NA, EU\n"
        "- Channels: e-commerce + retail partners\n"
        "- Constraints: budget <= $250k for launch, ensure PCI compliance for checkout, prepare localized content for EN/FR/DE\n"
        "- Ask: Extract requirements, build a timeline/cost plan, research top 3 risks with mitigations, "
        "and produce a launch email draft + internal briefing summary."
    )


async def run_launch_orchestrator(api_key: str) -> Dict[str, Any]:
    manager, tool_to_agent = build_manager_and_subagents(api_key)

    messages: List[Dict[str, Any]] = [
        {'role': 'user', 'content': launch_brief()}
    ]

    final_answer = ''
    max_rounds = 12
    round_idx = 0

    print("Starting Product Launch orchestration...")
    print("Tools:", [t['function']['name'] for t in manager.list_tools()])

    while round_idx < max_rounds:
        round_idx += 1
        print(f"\n--- Planning Round {round_idx} ---")
        final_received = False

        async for result in manager.usf.run(messages, {'tools': manager.list_tools()}):
            rtype = result.get('type')

            if rtype == 'plan':
                plan_text = result.get('plan') or result.get('content') or ''
                print("Plan:", plan_text[:600])
                messages.append({'role': 'assistant', 'content': plan_text, 'type': 'agent_plan'})

            elif rtype == 'tool_calls':
                tool_calls = result.get('tool_calls', [])
                print("Tool calls:", [tc['function']['name'] for tc in tool_calls])
                messages.append({'role': 'assistant', 'content': '', 'tool_calls': tool_calls})

                for tool_call in tool_calls:
                    alias = (tool_call.get('function') or {}).get('name')
                    sub = tool_to_agent.get(alias)
                    if not sub:
                        messages.append({
                            'role': 'tool',
                            'tool_call_id': tool_call.get('id'),
                            'name': alias,
                            'content': json.dumps({'error': f'Unknown tool {alias}'})
                        })
                        print(f"Unknown tool: {alias}")
                        continue

                    calling_context = messages
                    context_param = None
                    if sub.context_mode == 'CONTEXT_PARAM':
                        context_param = {'style': 'concise', 'format': 'email/briefing'}

                    res = await sub.execute_as_tool(
                        tool_call=tool_call,
                        calling_context=calling_context,
                        context_param=context_param
                    )
                    messages.append({
                        'role': 'tool',
                        'tool_call_id': tool_call.get('id'),
                        'name': alias,
                        'content': json.dumps({
                            'success': res.get('success'),
                            'content': res.get('content'),
                            'error': res.get('error')
                        }, ensure_ascii=False)
                    })
                    print(f"Executed {alias}: success={res.get('success')}")

                break

            elif rtype == 'final_answer':
                final_answer = result.get('content', '')
                print("\n--- Final Answer ---")
                print(final_answer)
                final_received = True
                break

        if final_received:
            break

    return {'final_answer': final_answer, 'messages_len': len(messages)}


async def main():
    api_key = os.getenv('USF_API_KEY') or "0546a8c6-12a5-4ebf-9b0a-e6ef35de6ac1"
    if not api_key or api_key.strip() == "":
        raise RuntimeError("USF_API_KEY is required")

    res = await run_launch_orchestrator(api_key)
    print("\nConversation length:", res['messages_len'])


if __name__ == '__main__':
    asyncio.run(main())
