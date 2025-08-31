import os
import json
import asyncio
from typing import Dict, List, Any

from usf_agents import SubAgent, ManagerAgent
from usf_agents.multi_agent.context import sanitize_parent_context
from usf_agents.runtime.validate import validate_next_step


"""
Incident Response Orchestrator (Dynamic, Planner-Driven)

Given a single incident report (logs + context), the manager dynamically coordinates:
- LogAnalyzer       (AGENT_DECIDED): summarize anomalies and extract signals
- RootCauseResearch (ALWAYS_FULL): investigate likely causes and hypotheses
- Remediator        (CONTEXT_PARAM): synthesize remediation script/config/steps
- CommsWriter       (ALWAYS_FULL): craft stakeholder update/post-mortem summary

The LLM planner decides which tools to call and in what order, until a final answer is produced.
Run:
  USF_API_KEY=YOUR_KEY python -m usf_agents.examples.incident_response_orchestrator
"""


def build_manager_and_subagents(api_key: str):
    log_analyzer = SubAgent({
        'id': 'logs',
        'name': 'Log Analyzer',
        'agent_type': 'sub',
        'context_mode': 'AGENT_DECIDED',
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })
    root_cause = SubAgent({
        'id': 'rootcause',
        'name': 'Root Cause Researcher',
        'agent_type': 'sub',
        'context_mode': 'ALWAYS_FULL',
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })
    remediator = SubAgent({
        'id': 'remediate',
        'name': 'Remediator',
        'agent_type': 'sub',
        'context_mode': 'CONTEXT_PARAM',
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })
    comms = SubAgent({
        'id': 'comms',
        'name': 'Comms Writer',
        'agent_type': 'sub',
        'context_mode': 'ALWAYS_FULL',
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })

    manager = ManagerAgent({
        'id': 'ir_mgr',
        'name': 'Incident Orchestrator',
        'agent_type': 'manager',
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })

    # Register as tools with stable aliases
    manager.add_sub_agent(log_analyzer, {
        'description': 'Analyze incident logs and extract anomalies',
        'parameters': {
            'type': 'object',
            'properties': {
                'task': {'type': 'string'},
                'input': {'type': 'object'},
                'context_param': {'type': 'object'}
            },
            'required': ['task']
        }
    }, alias='agent_logs')

    manager.add_sub_agent(root_cause, {
        'description': 'Investigate likely root causes and hypotheses',
        'parameters': {
            'type': 'object',
            'properties': {
                'task': {'type': 'string'},
                'input': {'type': 'object'},
                'context_param': {'type': 'object'}
            },
            'required': ['task']
        }
    }, alias='agent_rootcause')

    manager.add_sub_agent(remediator, {
        'description': 'Generate remediation steps/scripts/config patches',
        'parameters': {
            'type': 'object',
            'properties': {
                'task': {'type': 'string'},
                'input': {'type': 'object'},
                'context_param': {'type': 'object'}
            },
            'required': ['task']
        }
    }, alias='agent_remediate')

    manager.add_sub_agent(comms, {
        'description': 'Craft stakeholder/post-mortem communications',
        'parameters': {
            'type': 'object',
            'properties': {
                'task': {'type': 'string'},
                'input': {'type': 'object'},
                'context_param': {'type': 'object'}
            },
            'required': ['task']
        }
    }, alias='agent_comms')

    tool_to_agent = {
        'agent_logs': log_analyzer,
        'agent_rootcause': root_cause,
        'agent_remediate': remediator,
        'agent_comms': comms
    }
    return manager, tool_to_agent


def incident_requirement() -> str:
    # Simulated logs/context in a single user message
    return (
        "SEV-1 Incident Report: Service outage on checkout API.\n"
        "- Start: 09:14 UTC; End: ongoing\n"
        "- Error spikes: 500/502 between 09:14-09:20 UTC\n"
        "- Log excerpts:\n"
        "  09:14:03Z ERROR db_pool exhausted connections: timeout acquiring\n"
        "  09:14:05Z WARN  upstream latency > 2s for payment-gateway\n"
        "  09:15:10Z ERROR sql: deadlock detected on orders table\n"
        "  09:16:40Z ERROR redis timeout for session store shard-2\n"
        "- Deployment: v2025.08.29-rc1 rolled to 30% at 09:12 UTC\n"
        "- Request: analyze logs, identify probable root causes, suggest remediation, "
        "and draft a stakeholder update."
    )


async def run_ir_orchestrator(api_key: str) -> Dict[str, Any]:
    manager, tool_to_agent = build_manager_and_subagents(api_key)

    messages: List[Dict[str, Any]] = [
        {'role': 'user', 'content': incident_requirement()}
    ]

    final_answer = ''
    max_rounds = 20
    round_idx = 0

    print("Starting Incident Response orchestration...")
    print("Tools:", [t['function']['name'] for t in manager.list_tools()])

    while round_idx < max_rounds:
        round_idx += 1
        print(f"\n--- Planning Round {round_idx} ---")
        final_received = False

        # Guardrail: ensure correct sequencing before each run
        validate_next_step(messages)
        async for result in manager.usf.run(messages, {'tools': manager.list_tools()}):
            rtype = result.get('type')

            if rtype == 'plan':
                plan_text = result.get('plan') or result.get('content') or ''
                print("Plan:", plan_text[:600])
                messages.append({
                    'role': 'assistant',
                    'content': plan_text,
                    'type': 'agent_plan'
                })

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

                    # Strictly sanitize parent context before delegating to sub-agent
                    calling_context = sanitize_parent_context(messages)

                    context_param = None
                    if sub.context_mode == 'CONTEXT_PARAM':
                        context_param = {'env': 'prod', 'style': 'actionable'}

                    # Let the sub-agent run its own tool loop until final
                    res = await sub.execute_as_tool_until_final(
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

    res = await run_ir_orchestrator(api_key)
    print("\nConversation length:", res['messages_len'])


if __name__ == '__main__':
    asyncio.run(main())
