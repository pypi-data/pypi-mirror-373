import os
import json
import asyncio
from typing import Dict, List, Any

from usf_agents import SubAgent, ManagerAgent


"""
Data Science Workflow Orchestrator (Dynamic, Planner-Driven)

Given a single E2E DS request, the manager dynamically coordinates:
- DataFetcher  (CONTEXT_PARAM): retrieve/load a dataset (simulated by description/source)
- EDAAnalyzer  (AGENT_DECIDED): summarize stats, missing values/outliers, key findings
- ModelCoder   (CONTEXT_PARAM): generate baseline model training code
- ReportWriter (ALWAYS_FULL): produce a concise notebook-style report summary

Run:
  USF_API_KEY=YOUR_KEY python -m usf_agents.examples.data_science_orchestrator
"""


def build_manager_and_subagents(api_key: str):
    fetcher = SubAgent({
        'id': 'fetch',
        'name': 'Data Fetcher',
        'agent_type': 'sub',
        'context_mode': 'CONTEXT_PARAM',
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })
    eda = SubAgent({
        'id': 'eda',
        'name': 'EDA Analyzer',
        'agent_type': 'sub',
        'context_mode': 'AGENT_DECIDED',
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })
    coder = SubAgent({
        'id': 'model',
        'name': 'Model Coder',
        'agent_type': 'sub',
        'context_mode': 'CONTEXT_PARAM',
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })
    writer = SubAgent({
        'id': 'report',
        'name': 'Report Writer',
        'agent_type': 'sub',
        'context_mode': 'ALWAYS_FULL',
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })

    manager = ManagerAgent({
        'id': 'ds_mgr',
        'name': 'DS Orchestrator',
        'agent_type': 'manager',
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })

    manager.add_sub_agent(fetcher, {
        'description': 'Fetch or load dataset based on a described source',
        'parameters': {
            'type': 'object',
            'properties': {'task': {'type': 'string'}, 'input': {'type': 'object'}, 'context_param': {'type': 'object'}},
            'required': ['task']
        }
    }, alias='agent_fetch')

    manager.add_sub_agent(eda, {
        'description': 'Perform EDA: stats, missingness, outliers, key findings',
        'parameters': {
            'type': 'object',
            'properties': {'task': {'type': 'string'}, 'input': {'type': 'object'}, 'context_param': {'type': 'object'}},
            'required': ['task']
        }
    }, alias='agent_eda')

    manager.add_sub_agent(coder, {
        'description': 'Generate baseline model training code (e.g., sklearn)',
        'parameters': {
            'type': 'object',
            'properties': {'task': {'type': 'string'}, 'input': {'type': 'object'}, 'context_param': {'type': 'object'}},
            'required': ['task']
        }
    }, alias='agent_model')

    manager.add_sub_agent(writer, {
        'description': 'Compose a concise notebook-style DS report',
        'parameters': {
            'type': 'object',
            'properties': {'task': {'type': 'string'}, 'input': {'type': 'object'}, 'context_param': {'type': 'object'}},
            'required': ['task']
        }
    }, alias='agent_report')

    tool_to_agent = {
        'agent_fetch': fetcher,
        'agent_eda': eda,
        'agent_model': coder,
        'agent_report': writer
    }
    return manager, tool_to_agent


def ds_request() -> str:
    return (
        "Data Science Task: Build a quick prototype on a customer churn dataset.\n"
        "- Dataset source (simulated): S3 bucket path s3://acme-ds/churn/2025-08-01/churn.csv\n"
        "- Objective: binary classification (churn: 0/1)\n"
        "- Steps requested: fetch dataset, perform EDA (stats/missing/outliers), "
        "generate baseline model training code, and compose a concise summary report "
        "with key EDA findings and code pointers."
    )


async def run_ds_orchestrator(api_key: str) -> Dict[str, Any]:
    manager, tool_to_agent = build_manager_and_subagents(api_key)

    messages: List[Dict[str, Any]] = [
        {'role': 'user', 'content': ds_request()}
    ]

    final_answer = ''
    max_rounds = 12
    round_idx = 0

    print("Starting Data Science orchestration...")
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
                        # Provide minimal explicit context only
                        if alias == 'agent_fetch':
                            context_param = {'access': 'assumed', 'format': 'csv'}
                        elif alias == 'agent_model':
                            context_param = {'framework': 'sklearn', 'style': 'concise'}

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

    res = await run_ds_orchestrator(api_key)
    print("\nConversation length:", res['messages_len'])


if __name__ == '__main__':
    asyncio.run(main())
