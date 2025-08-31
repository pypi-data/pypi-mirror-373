# USF Agents SDK (Python)

Production-grade, OpenAI-compatible Agents SDK for planning, tool execution, and multi‑agent orchestration on the official USF Agent APIs.

- Three-stage lifecycle: plan → agent / tool calls → plan ... → plan → final answer
- Explicit, developer-controlled tool execution (no hidden side effects)
- Single-agent and multi-agent orchestration (manager/sub-agents, agent-as-tool)
- Strict sequencing safety (utilities to avoid message order errors)
- Graph workflows, tracing, and visualization
- Extensive configuration, sane defaults, and type hints


## Table of Contents

- Features
- Installation
- Requirements
- Quickstart (progressive, runnable)
  1. Plain LLM (no tools)
  2. Minimal agent (backstory + goal)
  3. Agent without tools (plan → final)
  4. Agent with tools (strict tool loop via SafeSeqRunner)
  5. Multi-agents (manager + sub-agent)
- Cookbook (directly runnable end-to-end)
  - Incident Response Orchestrator
  - Product Launch Orchestrator
  - Data Science Orchestrator
  - Manager Dynamic Orchestrator
- Core Concepts
- Sequencing Safety (sanitize_parent_context, validate_next_step, SafeSeqRunner)
- Configuration Reference (all knobs and defaults)
- Graph Orchestration and Tracing
- Troubleshooting
- Contributing, License

## Features

- Agent lifecycle with planning, explicit tool execution, final response
- Multi-stage configuration and per-request overrides
- Agent-as-tool adapters (sub-agents exposed as tools)
- Context shaping modes for delegation (NONE, AGENT_DECIDED, ALWAYS_FULL, CONTEXT_PARAM)
- Arbitrary nesting (no fixed hierarchy: any agent may have sub-agents)
- Graph-style workflows (nodes: agents/tools; edges with conditions)
- Tracing (Mermaid/Graphviz/JSON)
- Memory (temporary, auto-trim)
- Streaming support
- Automatic UTC timestamp in final responses (with optional override)
- Strict message sequencing guards and helper runner


## Installation

```bash
pip install usf-agents
```


## Requirements

- Python 3.9+
- A valid USF API key (set USF_API_KEY environment variable for examples)


## Quickstart (progressive, all runnable)

Below examples use USF_API_KEY from your environment.

For Windows PowerShell replace `export` with `$env:USF_API_KEY="YOUR_KEY";`
For Windows cmd use `set USF_API_KEY=YOUR_KEY && python ...`

Custom engine with provider (planning/tool-calling)
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import asyncio, os
from usf_agents import USFAgent

async def main():
    agent = USFAgent({
        'api_key': os.getenv('USF_API_KEY'),
        'model': 'gpt-4o-mini',
        'provider': 'openai'  # allowed: openrouter | openai | claude | huggingface-inference | groq
    })
    async for chunk in agent.run("Briefly explain provider usage."):
        if chunk['type'] == 'final_answer':
            print('Final:', chunk['content'])
            break

asyncio.run(main())
# PY
```

1. Plain LLM (no tools; simplest)
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import asyncio, os
from usf_agents import USFAgent

async def main():
    agent = USFAgent({'api_key': os.getenv('USF_API_KEY'), 'model': 'usf-mini'})
    async for chunk in agent.run("Hello, what's the capital of France?"):
        if chunk['type'] == 'final_answer':
            print('Final:', chunk['content'])
            break

asyncio.run(main())
# PY
```

2. Minimal agent (only backstory + goal)
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import asyncio, os
from usf_agents import USFAgent

async def main():
    agent = USFAgent({
        'api_key': os.getenv('USF_API_KEY'),
        'backstory': 'I am a senior product manager at a mobile app startup.',
        'goal': 'Provide concise, actionable guidance for product decisions.'
    })
    async for chunk in agent.run("How can I improve onboarding conversion?"):
        if chunk['type'] == 'final_answer':
            print('Final:', chunk['content'])
            break

asyncio.run(main())
# PY
```

3. Agent without tools (observe plan → final, no tool_calls)
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import asyncio, os
from usf_agents import USFAgent

async def main():
    agent = USFAgent({'api_key': os.getenv('USF_API_KEY'), 'model': 'usf-mini'})

    messages = [{'role': 'user', 'content': 'Summarize the benefits of unit testing.'}]
    async for chunk in agent.run(messages):
        if chunk['type'] == 'plan':
            print('Plan:', chunk.get('plan') or chunk.get('content'))
        elif chunk['type'] == 'final_answer':
            print('Final:', chunk['content'])
            break

asyncio.run(main())
# PY
```

4. Agent with tools (strict tool loop using SafeSeqRunner)
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import asyncio, os, json
from usf_agents import USFAgent
from usf_agents.runtime.safe_seq import run_until_final

# Define a simple calculator tool
tools = [{
    'type': 'function',
    'function': {
        'name': 'calc',
        'description': 'Evaluate a simple math expression',
        'parameters': {
            'type': 'object',
            'properties': {'expression': {'type': 'string'}},
            'required': ['expression']
        }
    }
}]

# Tool router (strict: immediately resolve tool_calls)
async def tool_router(tool_call, current_msgs):
    fn = tool_call['function']['name']
    args = json.loads(tool_call['function']['arguments'])
    if fn == 'calc':
        result = eval(args['expression'])  # use a safe math lib in production
        return {'success': True, 'result': result}
    return {'success': False, 'error': f'Unknown tool {fn}'}

async def main():
    agent = USFAgent({'api_key': os.getenv('USF_API_KEY')})
    messages = [{'role': 'user', 'content': 'Use calc to compute 25*4 and return the result.'}]
    final = await run_until_final(agent, messages, tools, tool_router)
    print('Final:', final)

asyncio.run(main())
# PY
```

5. Multi‑agents (manager + sub-agent as tool)
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import asyncio, os
from usf_agents import SubAgent, ManagerAgent

async def main():
    api_key = os.getenv('USF_API_KEY')
    worker = SubAgent({
        'id': 'worker', 'name': 'Worker', 'agent_type': 'sub',
        'context_mode': 'NONE',
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })
    manager = ManagerAgent({
        'id': 'mgr', 'name': 'Manager', 'agent_type': 'manager',
        'usf_config': {'api_key': api_key, 'model': 'usf-mini'}
    })
    manager.add_sub_agent(worker, {
        'description': 'Delegate small tasks',
        'parameters': {'type':'object','properties':{'task':{'type':'string'},'input':{'type':'object'}},'required':['task']}
    }, alias='agent_worker')

    # Ask manager to plan and call sub-agent tool
    messages = [{'role': 'user', 'content': 'Delegate to worker to draft a haiku about teamwork.'}]
    async for chunk in manager.usf.run(messages, {'tools': manager.list_tools()}):
        if chunk['type'] == 'plan':
            messages.append({'role': 'assistant','content': chunk.get('plan') or chunk.get('content'),'type':'agent_plan'})
        elif chunk['type'] == 'tool_calls':
            # Execute sub-agent tool immediately (minimal adapter)
            messages.append({'role': 'assistant','content': '', 'tool_calls': chunk['tool_calls']})
            for tc in chunk['tool_calls']:
                # Invoke sub-agent via manager.delegate
                res = await manager.delegate(sub_id='worker', task={'task':'draft','input':{'style':'haiku','topic':'teamwork'}})
                messages.append({'role':'tool','tool_call_id': tc['id'],'name': tc['function']['name'],'content': str(res)})
            break
        elif chunk['type'] == 'final_answer':
            print('Final:', chunk['content'])
            break

asyncio.run(main())
# PY
```

## Cookbook (directly runnable end-to-end)

These examples are fully inlined so you can copy/paste them directly into a Jupyter notebook without needing access to the examples/ directory after installing from PyPI.

Notebook setup (run once per notebook session)
```python
# Install the SDK and prepare asyncio for notebooks
%pip install -q usf-agents nest_asyncio

import os, asyncio, nest_asyncio
nest_asyncio.apply()

# Set your API key for notebook runs
os.environ['USF_API_KEY'] = "YOUR_USF_API_KEY"
```

Notes
- In notebooks, prefer top-level await: await main()
- If you run these as standalone scripts instead, replace the last line with: asyncio.run(main())
- All examples require the USF_API_KEY environment variable to be set (no fallbacks are used here).

### Incident Response Orchestrator

What it does
- Dynamically analyzes incident logs, researches likely root causes, suggests remediations, and drafts stakeholder comms using sub-agents as tools.
- Demonstrates sanitize_parent_context and validate_next_step guardrails in the planning loop.

Code (copy/paste into a notebook cell)
```python
import os
import json
import asyncio
from typing import Dict, List, Any

from usf_agents import SubAgent, ManagerAgent
from usf_agents.multi_agent.context import sanitize_parent_context
from usf_agents.runtime.validate import validate_next_step

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

    manager.add_sub_agent(log_analyzer, {
        'description': 'Analyze incident logs and extract anomalies',
        'parameters': {'type': 'object','properties': {'task': {'type': 'string'},'input': {'type': 'object'},'context_param': {'type': 'object'}},'required': ['task']}
    }, alias='agent_logs')

    manager.add_sub_agent(root_cause, {
        'description': 'Investigate likely root causes and hypotheses',
        'parameters': {'type': 'object','properties': {'task': {'type': 'string'},'input': {'type': 'object'},'context_param': {'type': 'object'}},'required': ['task']}
    }, alias='agent_rootcause')

    manager.add_sub_agent(remediator, {
        'description': 'Generate remediation steps/scripts/config patches',
        'parameters': {'type': 'object','properties': {'task': {'type': 'string'},'input': {'type': 'object'},'context_param': {'type': 'object'}},'required': ['task']}
    }, alias='agent_remediate')

    manager.add_sub_agent(comms, {
        'description': 'Craft stakeholder/post-mortem communications',
        'parameters': {'type': 'object','properties': {'task': {'type': 'string'},'input': {'type': 'object'},'context_param': {'type': 'object'}},'required': ['task']}
    }, alias='agent_comms')

    tool_to_agent = {
        'agent_logs': log_analyzer,
        'agent_rootcause': root_cause,
        'agent_remediate': remediator,
        'agent_comms': comms
    }
    return manager, tool_to_agent

def incident_requirement() -> str:
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
    messages: List[Dict[str, Any]] = [{'role': 'user', 'content': incident_requirement()}]
    final_answer = ''
    max_rounds = 20
    round_idx = 0

    print("Starting Incident Response orchestration...")
    print("Tools:", [t['function']['name'] for t in manager.list_tools()])

    while round_idx < max_rounds:
        round_idx += 1
        print(f"\n--- Planning Round {round_idx} ---")
        final_received = False

        validate_next_step(messages)
        async for result in manager.usf.run(messages, {'tools': manager.list_tools()}):
            rtype = result.get('type')

            if rtype == 'plan':
                plan_text = result.get('plan') or result.get('content') or ''
                print("Plan:", plan_text[:600])
                messages.append({'role': 'assistant','content': plan_text,'type': 'agent_plan'})

            elif rtype == 'tool_calls':
                tool_calls = result.get('tool_calls', [])
                print("Tool calls:", [tc['function']['name'] for tc in tool_calls])
                messages.append({'role': 'assistant', 'content': '', 'tool_calls': tool_calls})

                for tool_call in tool_calls:
                    alias = (tool_call.get('function') or {}).get('name')
                    sub = tool_to_agent.get(alias)
                    if not sub:
                        messages.append({'role': 'tool','tool_call_id': tool_call.get('id'),'name': alias,'content': json.dumps({'error': f'Unknown tool {alias}'})})
                        print(f"Unknown tool: {alias}")
                        continue

                    calling_context = sanitize_parent_context(messages)
                    context_param = None
                    if sub.context_mode == 'CONTEXT_PARAM':
                        context_param = {'env': 'prod', 'style': 'actionable'}

                    res = await sub.execute_as_tool_until_final(tool_call, calling_context, context_param=context_param)
                    messages.append({'role': 'tool','tool_call_id': tool_call.get('id'),'name': alias,'content': json.dumps({'success': res.get('success'),'content': res.get('content'),'error': res.get('error')}, ensure_ascii=False)})
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
    api_key = os.environ.get('USF_API_KEY')
    if not api_key:
        raise RuntimeError("USF_API_KEY is required")
    res = await run_ir_orchestrator(api_key)
    print("\nConversation length:", res['messages_len'])
```

Run (notebook)
```python
await main()
```

---

### Product Launch Orchestrator

What it does
- Extracts requirements from a launch brief, plans timeline/cost, researches risks, and drafts comms via multiple sub-agents.

Code
```python
import os
import json
import asyncio
from typing import Dict, List, Any
from usf_agents import SubAgent, ManagerAgent

def build_manager_and_subagents(api_key: str):
    req = SubAgent({'id': 'requirements','name': 'Requirements Extractor','agent_type': 'sub','context_mode': 'ALWAYS_FULL','usf_config': {'api_key': api_key, 'model': 'usf-mini'}})
    planner = SubAgent({'id': 'planner','name': 'Timeline & Cost Planner','agent_type': 'sub','context_mode': 'NONE','usf_config': {'api_key': api_key, 'model': 'usf-mini'}})
    risk = SubAgent({'id': 'risk','name': 'Risk Researcher','agent_type': 'sub','context_mode': 'AGENT_DECIDED','usf_config': {'api_key': api_key, 'model': 'usf-mini'}})
    writer = SubAgent({'id': 'writer','name': 'Comms Writer','agent_type': 'sub','context_mode': 'ALWAYS_FULL','usf_config': {'api_key': api_key, 'model': 'usf-mini'}})

    manager = ManagerAgent({'id': 'pl_mgr','name': 'Launch Orchestrator','agent_type': 'manager','usf_config': {'api_key': api_key, 'model': 'usf-mini'}})

    manager.add_sub_agent(req, {'description': 'Extract requirements/constraints from brief','parameters': {'type': 'object','properties': {'task': {'type': 'string'},'input': {'type': 'object'},'context_param': {'type': 'object'}},'required': ['task']}} ,alias='agent_requirements')
    manager.add_sub_agent(planner, {'description': 'Build rough timeline and cost plan','parameters': {'type': 'object','properties': {'task': {'type': 'string'},'input': {'type': 'object'},'context_param': {'type': 'object'}},'required': ['task']}} ,alias='agent_planner')
    manager.add_sub_agent(risk, {'description': 'Identify top risks and mitigation','parameters': {'type': 'object','properties': {'task': {'type': 'string'},'input': {'type': 'object'},'context_param': {'type': 'object'}},'required': ['task']}} ,alias='agent_risk')
    manager.add_sub_agent(writer, {'description': 'Produce launch email and internal briefing','parameters': {'type': 'object','properties': {'task': {'type': 'string'},'input': {'type': 'object'},'context_param': {'type': 'object'}},'required': ['task']}} ,alias='agent_writer')

    return manager, {'agent_requirements': req,'agent_planner': planner,'agent_risk': risk,'agent_writer': writer}

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
    messages: List[Dict[str, Any]] = [{'role': 'user', 'content': launch_brief()}]
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
                        messages.append({'role': 'tool','tool_call_id': tool_call.get('id'),'name': alias,'content': json.dumps({'error': f'Unknown tool {alias}'})})
                        print(f"Unknown tool: {alias}")
                        continue

                    calling_context = messages
                    context_param = None
                    if sub.context_mode == 'CONTEXT_PARAM':
                        context_param = {'style': 'concise', 'format': 'email/briefing'}

                    res = await sub.execute_as_tool(tool_call, calling_context, context_param=context_param)
                    messages.append({'role': 'tool','tool_call_id': tool_call.get('id'),'name': alias,'content': json.dumps({'success': res.get('success'),'content': res.get('content'),'error': res.get('error')}, ensure_ascii=False)})
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
    api_key = os.environ.get('USF_API_KEY')
    if not api_key:
        raise RuntimeError("USF_API_KEY is required")
    res = await run_launch_orchestrator(api_key)
    print("\nConversation length:", res['messages_len'])
```

Run (notebook)
```python
await main()
```

---

### Data Science Orchestrator

What it does
- Fetch/load dataset (simulated), perform EDA, generate baseline model code, and compose a concise report.

Code
```python
import os
import json
import asyncio
from typing import Dict, List, Any
from usf_agents import SubAgent, ManagerAgent

def build_manager_and_subagents(api_key: str):
    fetcher = SubAgent({'id': 'fetch','name': 'Data Fetcher','agent_type': 'sub','context_mode': 'CONTEXT_PARAM','usf_config': {'api_key': api_key, 'model': 'usf-mini'}})
    eda = SubAgent({'id': 'eda','name': 'EDA Analyzer','agent_type': 'sub','context_mode': 'AGENT_DECIDED','usf_config': {'api_key': api_key, 'model': 'usf-mini'}})
    coder = SubAgent({'id': 'model','name': 'Model Coder','agent_type': 'sub','context_mode': 'CONTEXT_PARAM','usf_config': {'api_key': api_key, 'model': 'usf-mini'}})
    writer = SubAgent({'id': 'report','name': 'Report Writer','agent_type': 'sub','context_mode': 'ALWAYS_FULL','usf_config': {'api_key': api_key, 'model': 'usf-mini'}})

    manager = ManagerAgent({'id': 'ds_mgr','name': 'DS Orchestrator','agent_type': 'manager','usf_config': {'api_key': api_key, 'model': 'usf-mini'}})

    manager.add_sub_agent(fetcher, {'description': 'Fetch or load dataset based on a described source','parameters': {'type': 'object','properties': {'task': {'type': 'string'},'input': {'type': 'object'},'context_param': {'type': 'object'}},'required': ['task']}} ,alias='agent_fetch')
    manager.add_sub_agent(eda, {'description': 'Perform EDA: stats, missingness, outliers, key findings','parameters': {'type': 'object','properties': {'task': {'type': 'string'},'input': {'type': 'object'},'context_param': {'type': 'object'}},'required': ['task']}} ,alias='agent_eda')
    manager.add_sub_agent(coder, {'description': 'Generate baseline model training code (e.g., sklearn)','parameters': {'type': 'object','properties': {'task': {'type': 'string'},'input': {'type': 'object'},'context_param': {'type': 'object'}},'required': ['task']}} ,alias='agent_model')
    manager.add_sub_agent(writer, {'description': 'Compose a concise notebook-style DS report','parameters': {'type': 'object','properties': {'task': {'type': 'string'},'input': {'type': 'object'},'context_param': {'type': 'object'}},'required': ['task']}} ,alias='agent_report')

    tool_to_agent = {'agent_fetch': fetcher,'agent_eda': eda,'agent_model': coder,'agent_report': writer}
    return manager, tool_to_agent

def ds_request() -> str:
    return (
        "Data Science Task: Build a quick prototype on a customer churn dataset.\n"
        "- Dataset source (simulated): S3 bucket path s3://acme-ds/churn/2025-08-01/churn.csv\n"
        "- Objective: binary classification (churn: 0/1)\n"
        "- Steps requested: fetch dataset, perform EDA (stats/missing/outliers), generate baseline model training code, and compose a concise summary report with key EDA findings and code pointers."
    )

async def run_ds_orchestrator(api_key: str) -> Dict[str, Any]:
    manager, tool_to_agent = build_manager_and_subagents(api_key)
    messages: List[Dict[str, Any]] = [{'role': 'user', 'content': ds_request()}]
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
                        messages.append({'role': 'tool','tool_call_id': tool_call.get('id'),'name': alias,'content': json.dumps({'error': f'Unknown tool {alias}'})})
                        print(f"Unknown tool: {alias}")
                        continue

                    calling_context = messages
                    context_param = None
                    if sub.context_mode == 'CONTEXT_PARAM':
                        if alias == 'agent_fetch':
                            context_param = {'access': 'assumed', 'format': 'csv'}
                        elif alias == 'agent_model':
                            context_param = {'framework': 'sklearn', 'style': 'concise'}

                    res = await sub.execute_as_tool(tool_call, calling_context, context_param=context_param)
                    messages.append({'role': 'tool','tool_call_id': tool_call.get('id'),'name': alias,'content': json.dumps({'success': res.get('success'),'content': res.get('content'),'error': res.get('error')}, ensure_ascii=False)})
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
    api_key = os.environ.get('USF_API_KEY')
    if not api_key:
        raise RuntimeError("USF_API_KEY is required")
    res = await run_ds_orchestrator(api_key)
    print("\nConversation length:", res['messages_len'])
```

Run (notebook)
```python
await main()
```

---

### Manager Dynamic Orchestrator

What it does
- Demonstrates a manager coordinating calculator/researcher/coder/writer sub-agents with different context policies.

Code
```python
import os
import json
import asyncio
from typing import Dict, List, Any
from usf_agents import SubAgent, ManagerAgent

def build_manager_and_subagents(api_key: str):
    calculator = SubAgent({'id': 'calc','name': 'Calculator','agent_type': 'sub','context_mode': 'NONE','usf_config': {'api_key': api_key, 'model': 'usf-mini'}})
    researcher = SubAgent({'id': 'research','name': 'Researcher','agent_type': 'sub','context_mode': 'AGENT_DECIDED','usf_config': {'api_key': api_key, 'model': 'usf-mini'}})
    coder = SubAgent({'id': 'coder','name': 'Code Assistant','agent_type': 'sub','context_mode': 'CONTEXT_PARAM','usf_config': {'api_key': api_key, 'model': 'usf-mini'}})
    writer = SubAgent({'id': 'writer','name': 'Writer','agent_type': 'sub','context_mode': 'ALWAYS_FULL','usf_config': {'api_key': api_key, 'model': 'usf-mini'}})

    manager = ManagerAgent({'id': 'mgr','name': 'Dynamic Orchestrator','agent_type': 'manager','usf_config': {'api_key': api_key, 'model': 'usf-mini'}})

    manager.add_sub_agent(calculator, {'description': 'Calculator for numeric computations','parameters': {'type': 'object','properties': {'task': {'type': 'string'},'input': {'type': 'object'},'context_param': {'type': 'object'}},'required': ['task']}} ,alias='agent_calc')
    manager.add_sub_agent(researcher, {'description': 'Researcher for market/knowledge queries','parameters': {'type': 'object','properties': {'task': {'type': 'string'},'input': {'type': 'object'},'context_param': {'type': 'object'}},'required': ['task']}} ,alias='agent_research')
    manager.add_sub_agent(coder, {'description': 'Coder for generating concise code snippets','parameters': {'type': 'object','properties': {'task': {'type': 'string'},'input': {'type': 'object'},'context_param': {'type': 'object'}},'required': ['task']}} ,alias='agent_coder')
    manager.add_sub_agent(writer, {'description': 'Writer to compose a final executive summary','parameters': {'type': 'object','properties': {'task': {'type': 'string'},'input': {'type': 'object'},'context_param': {'type': 'object'}},'required': ['task']}} ,alias='agent_writer')

    return manager, {'agent_calc': calculator,'agent_research': researcher,'agent_coder': coder,'agent_writer': writer}

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
    messages: List[Dict[str, Any]] = [{'role': 'user', 'content': build_complex_requirement()}]
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
                plan_text = result.get('plan') or result.get('content') or ''
                print("Plan:", plan_text[:500])
                messages.append({'role': 'assistant','content': plan_text,'type': 'agent_plan'})

            elif rtype == 'tool_calls':
                tool_calls = result.get('tool_calls', [])
                print("Tool calls:", [tc['function']['name'] for tc in tool_calls])
                messages.append({'role': 'assistant','content': '','tool_calls': tool_calls})

                for tool_call in tool_calls:
                    func = tool_call.get('function', {})
                    tool_name = func.get('name')
                    sub = tool_to_agent.get(tool_name)

                    if not sub:
                        messages.append({'role': 'tool','tool_call_id': tool_call.get('id'),'name': tool_name,'content': json.dumps({'error': f'Unknown tool {tool_name}'})})
                        print(f"Unknown tool requested: {tool_name}")
                        continue

                    calling_context = messages
                    context_param = None
                    if sub.context_mode == 'CONTEXT_PARAM':
                        context_param = {'style': 'concise', 'language': 'python'}

                    res = await sub.execute_as_tool(tool_call, calling_context, context_param=context_param)
                    content_payload = {'success': res.get('success'),'content': res.get('content'),'error': res.get('error')}
                    messages.append({'role': 'tool','tool_call_id': tool_call.get('id'),'name': tool_name,'content': json.dumps(content_payload, ensure_ascii=False)})
                    print(f"Executed {tool_name}: success={res.get('success')}")
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
    api_key = os.environ.get('USF_API_KEY')
    if not api_key:
        raise RuntimeError("USF_API_KEY is required to run the dynamic orchestrator example.")
    result = await run_dynamic_orchestration(api_key)
    print("\nConversation length:", result['messages_len'])
```

Run (notebook)
```python
await main()
```

---

Optional: Multi-agent Patterns (bonus)
```python
import asyncio
from usf_agents import SubAgent, ManagerAgent

math_agent = SubAgent({'id': 'math','name': 'Math Specialist','agent_type': 'sub','context_mode': 'NONE','usf_config': {'api_key': os.environ['USF_API_KEY'],'model': 'usf-mini'}})
code_agent = SubAgent({'id': 'coder','name': 'Code Assistant','agent_type': 'sub','context_mode': 'CONTEXT_PARAM','usf_config': {'api_key': os.environ['USF_API_KEY'],'model': 'usf-mini'}})

manager = ManagerAgent({'id': 'mgr','name': 'Manager','agent_type': 'manager','usf_config': {'api_key': os.environ['USF_API_KEY'],'model': 'usf-mini'}})

manager.add_sub_agent(math_agent, {'description': 'Delegate math tasks','parameters': {'type': 'object','properties': {'task': {'type': 'string'},'input': {'type': 'object'},'context_param': {'type': 'object'}},'required': ['task']}} ,alias='math_tool')
manager.add_sub_agent(code_agent, {'description': 'Delegate coding tasks','parameters': {'type': 'object','properties': {'task': {'type': 'string'},'input': {'type': 'object'},'context_param': {'type': 'object'}},'required': ['task']}} ,alias='coder_tool')

async def main():
    r1 = await manager.delegate(sub_id='math', task={'task': 'calculate', 'input': {'expression': '25 * 4'}})
    print('Math result:', r1)
    r2 = await manager.delegate(sub_id='coder', task={'task': 'generate_function', 'input': {'language': 'python', 'spec': 'sum two numbers a and b'}}, policy='CONTEXT_PARAM', context_param={'style': 'concise'})
    print('Code result:', r2)
```

Run (notebook)
```python
await main()
```

## Core Concepts

USFAgent lifecycle
- You supply messages and optional tools.
- The agent plans its next step (plan).
- If tools are needed, the agent emits tool_calls (OpenAI function-call format).
- You must execute tool_calls and append role: "tool" results with exact tool_call_id.
- The loop repeats until a final_answer is emitted.

Multi-agent orchestration
- BaseAgentWrapper: isolation wrapper with USFAgent inside
- SubAgent: acts as an agent and exposes an agent-as-tool surface
- ManagerAgent: aggregates tools and sub-agents (sub-agents appear as tools)
- Any agent can have sub-agents (no hardcoded hierarchy)
- Context shaping modes:
  - NONE: pass only new task
  - AGENT_DECIDED: act like ALWAYS_FULL if parent messages are present, else NONE
  - ALWAYS_FULL: pass complete parent transcript
  - CONTEXT_PARAM: pass only a small explicit context object
- sanitize_parent_context(msgs): strictly keeps only user and final-answer assistant messages when delegating (prevents invalid message sequences from leaking into sub-agent threads)

Graph workflows and tracing
- WorkflowGraph nodes represent agents/tools; edges have optional conditions
- ExecutionEngine walks the graph and collects outputs
- TraceRecorder records events; visualize via Mermaid/Graphviz/JSON


## Sequencing Safety

Why it matters
- After assistant emits tool_calls, the next messages must be the tool results with matching tool_call_id. No user/assistant content may appear between.

Utilities
- sanitize_parent_context(msgs: List[Message]) -> List[Message]
  - Keeps only user and final assistant messages; removes plan/tool_calls/tool results
- validate_next_step(messages)
  - Raises if the last assistant message has tool_calls (prevents run() before appending tool results)
- run_until_final(agent, messages, tools, tool_router)
  - Enforces strict loop and returns final content

Sub-agent helper
- SubAgent.execute_as_tool_until_final(...)
  - Runs the sub-agent’s internal tool loop and returns success + final content


## Configuration Reference

Global config for USFAgent (defaults in parentheses)
- api_key: str (required)
- model: str = 'usf-mini'
- provider: Optional[str] = None  (planning/tool-calling only; one of: openrouter, openai, claude, huggingface-inference, groq)
- introduction: str = ''
- knowledge_cutoff: str = '15 January 2025'
- stream: bool = False
- max_loops: int = 20 (1..100)
- backstory: str = ''
- goal: str = ''
- temp_memory:
  - enabled: bool = False
  - max_length: int = 10
  - auto_trim: bool = True

Stage configs (optional, override fallbacks)
- planning: Dict[str, Any]
  - api_key, provider, model, introduction, knowledge_cutoff, temperature, stop, debug, ...
- tool_calling: Dict[str, Any]
  - api_key, provider, model, introduction, knowledge_cutoff, temperature, stop, debug, ...
- final_response: Dict[str, Any]
  - api_key, model, temperature, stop, date_time_override, debug, ...
  - response_format (json_object|json_schema), max_tokens, top_p, presence_penalty, frequency_penalty, logit_bias, seed, user, stream_options

Provider usage (planning/tool-calling):
- Default engine is "usf-mini" when no provider is specified.
- For custom/non-default engines, set provider to one of: openrouter, openai, claude, huggingface-inference, groq.
- Omit provider (or leave blank) for default or directly supported models.

Per-run options (passed to agent.run(messages, options))
- tools: List[Tool] (OpenAI function tool format)
- planning/tool_calling/final_response: per-call overrides
- temperature, stop, date_time_override, debug, max_loops

Date/time override (final response stage)
- final_response.date_time_override: { enabled: bool, date: 'MM/DD/YYYY', time: 'HH:MM:SS AM/PM', timezone: 'IANA or label' }

Tool schema (OpenAI function-call compatible)
- Tool = {'type': 'function','function': {'name': str,'description': str,'parameters': JSONSchema}}

Tool call format (from assistant)
- {'id': '...', 'type': 'function', 'function': {'name': '...', 'arguments': JSON-string}}

Tool result message (from developer)
- {'role': 'tool','tool_call_id': '...', 'name': 'tool_name','content': JSON-string}

Multi-agent AgentSpec (ManagerAgent/SubAgent)
- id: str
- name: str
- agent_type: 'manager'|'sub'|'generic'
- backstory: str (optional)
- goal: str (optional)
- context_mode: 'NONE'|'AGENT_DECIDED'|'ALWAYS_FULL'|'CONTEXT_PARAM'
- usf_config: USFAgent config (same shape as constructor)
- tools: List[Tool] (native tools for this wrapper, optional)

Manager/SubAgent APIs
- add_sub_agent(sub: BaseAgentWrapper, schema: Dict, alias: Optional[str]) -> None
- list_tools() -> List[Tool]  (native + sub-agents as tools)
- delegate(sub_id, task, policy='inherit_manager_policy', context_param=None, calling_context=None, options=None)
- SubAgent.execute_as_tool(tool_call, calling_context, context_param=None, options=None)
- SubAgent.execute_as_tool_until_final(tool_call, calling_context, context_param=None, options=None)

Context shaping utilities
- sanitize_parent_context(msgs): keep only user and final-answer assistant messages for delegation
- shape_context_for_mode(mode, task, calling_agent_msgs=None, context_param=None) -> List[Message]

Sequencing helpers
- validate_next_step(messages) -> raises if invalid to call run()
- run_until_final(agent, messages, tools, tool_router, max_loops=20) -> str


## Graph Orchestration and Tracing

WorkflowGraph spec
- nodes: [{ id: str, type: 'agent'|'tool', ref: AgentId|tool_name, config?: Dict }]
- edges: [{ source: str, target: str, condition?: str }]

ExecutionEngine.run(entry_nodes: List[str], inputs: Dict[str, Any], max_steps=200) -> Dict[node_id, summary]
- Execute agents by calling wrapper.run_task(TaskPayload)
- Tool nodes may use an optional tool_executor callback

Tracing
- TraceRecorder: start(), record(event), end(status), snapshot()
- Visualization: to_mermaid(graph_spec, trace), to_graphviz(graph_spec, trace), trace_to_json(trace)

## Troubleshooting

Message sequencing errors
- Symptom: assistant apologizes or upstream rejects sequence after tool_calls
- Fix: after assistant tool_calls, append only role:'tool' messages with matching tool_call_id, then call run() again
- Use run_until_final and validate_next_step; sanitize parent context for sub-agent calls

API key / network errors
- Verify USF_API_KEY is set; for planning/tool-calling set provider when using custom engines; ensure connectivity

Missing tools on later runs
- Always pass the full tools surface when calling run(); wrappers auto-compose their tools in this SDK

Data Science example cannot fetch S3
- Supply a local CSV or adjust the example to a synthetic dataset toggle for offline runs


## Contributing

Contributions are welcome. Please open an issue or PR on GitHub.


## License

**USF Agents SDK License**

Copyright (c) 2025 UltraSafe AI Team

**PERMITTED USE:**
- Anyone may use this software for any purpose

**RESTRICTED ACTIVITIES:**
- No one may modify the code
- No one may use the code for commercial purposes
- No one may use the code to create competitive products

**ATTRIBUTION:**
- All copies of this software must retain this license notice
- Any use of this software must include attribution to UltraSafe AI Team
