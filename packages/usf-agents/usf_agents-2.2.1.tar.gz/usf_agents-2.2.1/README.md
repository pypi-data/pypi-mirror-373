# USF Agents SDK (Python)

Production-grade, OpenAI-compatible Agents SDK for planning, tool execution, and multi‑agent orchestration on the official USF Agent APIs.

- Three-stage lifecycle: plan → tool_calls → final_answer
- Explicit, developer-controlled tool execution (no hidden side effects)
- Single-agent and multi-agent orchestration (manager/sub-agents, agent-as-tool)
- Strict sequencing safety (utilities to avoid message order errors)
- Graph workflows, tracing, and visualization
- Extensive configuration, sane defaults, and type hints


Quick run (macOS/Linux)
- Ensure Python 3.9+
- pip install usf-agents
- export USF_API_KEY="YOUR_KEY"
- python -m usf_agents.examples.manager_dynamic_orchestrator

Windows PowerShell
- $env:USF_API_KEY="YOUR_KEY"; python -m usf_agents.examples.manager_dynamic_orchestrator


## Table of Contents

- Features
- Installation
- Requirements
- Quickstart (progressive, runnable)
  0) Plain LLM (no tools)
  1) Minimal agent (backstory + goal)
  2) Agent without tools (plan → final)
  3) Agent with tools (strict tool loop via SafeSeqRunner)
  4) Multi-agents (manager + sub-agent)
- Cookbook (directly runnable end-to-end)
  - Incident Response Orchestrator
  - Product Launch Orchestrator
  - Data Science Orchestrator
  - Manager Dynamic Orchestrator
- Core Concepts
- Sequencing Safety (sanitize_parent_context, validate_next_step, SafeSeqRunner)
- Configuration Reference (all knobs and defaults)
- Graph Orchestration and Tracing
- Testing
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

From source (editable):
```bash
git clone https://github.com/apt-team-018/usf-agents-sdk-python.git
cd usf-agents-sdk-python/python
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```


## Requirements

- Python 3.9+
- A valid USF API key (set USF_API_KEY environment variable for examples)


## Quickstart (progressive, all runnable)

Below examples use USF_API_KEY from your environment.

For Windows PowerShell replace `export` with `$env:USF_API_KEY="YOUR_KEY";`
For Windows cmd use `set USF_API_KEY=YOUR_KEY && python ...`

0) Plain LLM (no tools; simplest)
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

1) Minimal agent (only backstory + goal)
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

2) Agent without tools (observe plan → final, no tool_calls)
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

3) Agent with tools (strict tool loop using SafeSeqRunner)
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

4) Multi‑agents (manager + sub-agent as tool)
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


## Cookbook (ready-to-run end-to-end)

All examples require USF_API_KEY set.

macOS/Linux
- Incident: `USF_API_KEY=YOUR_KEY python -m usf_agents.examples.incident_response_orchestrator`
- Product:  `USF_API_KEY=YOUR_KEY python -m usf_agents.examples.product_launch_orchestrator`
- Data:     `USF_API_KEY=YOUR_KEY python -m usf_agents.examples.data_science_orchestrator`
- Manager:  `USF_API_KEY=YOUR_KEY python -m usf_agents.examples.manager_dynamic_orchestrator`

Windows PowerShell
- `$env:USF_API_KEY="YOUR_KEY"; python -m usf_agents.examples.incident_response_orchestrator`
- (repeat with other modules)

Windows cmd
- `set USF_API_KEY=YOUR_KEY && python -m usf_agents.examples.incident_response_orchestrator`

1) Incident Response Orchestrator
- Path: `usf_agents/examples/incident_response_orchestrator.py`
- Orchestrates logs → root cause → remediation → stakeholder comms
- Uses sanitize_parent_context, validate_next_step, and sub-agent execute_as_tool_until_final

2) Product Launch Orchestrator
- Path: `usf_agents/examples/product_launch_orchestrator.py`
- Requirements → plan → risk → comms

3) Data Science Orchestrator
- Path: `usf_agents/examples/data_science_orchestrator.py`
- Fetch (simulated) → EDA → baseline model code → report
- Note: If your environment restricts external fetch, provide a local CSV or add a synthetic dataset toggle in code.

4) Manager Dynamic Orchestrator
- Path: `usf_agents/examples/manager_dynamic_orchestrator.py`
- Planner coordinates calculator, researcher, coder, writer


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
- base_url: str = 'https://api.us.inc/usf/v1'
- model: str = 'usf-mini'
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
  - api_key, base_url, model, introduction, knowledge_cutoff, temperature, stop, debug, ...
- tool_calling: Dict[str, Any]
  - api_key, base_url, model, introduction, knowledge_cutoff, temperature, stop, debug, ...
- final_response: Dict[str, Any]
  - api_key, base_url, model, temperature, stop, date_time_override, debug, ...
  - response_format (json_object|json_schema), max_tokens, top_p, presence_penalty, frequency_penalty, logit_bias, seed, user, stream_options

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


## Testing

Run tests (no external network required for tests)
```bash
pytest -q
```

Run examples (require USF_API_KEY)
```bash
USF_API_KEY=YOUR_KEY python -m usf_agents.examples.incident_response_orchestrator
USF_API_KEY=YOUR_KEY python -m usf_agents.examples.product_launch_orchestrator
USF_API_KEY=YOUR_KEY python -m usf_agents.examples.manager_dynamic_orchestrator
USF_API_KEY=YOUR_KEY python -m usf_agents.examples.data_science_orchestrator
```


## Troubleshooting

Message sequencing errors
- Symptom: assistant apologizes or upstream rejects sequence after tool_calls
- Fix: after assistant tool_calls, append only role:'tool' messages with matching tool_call_id, then call run() again
- Use run_until_final and validate_next_step; sanitize parent context for sub-agent calls

API key / network errors
- Verify USF_API_KEY is set, endpoint base_url, connectivity

Missing tools on later runs
- Always pass the full tools surface when calling run(); wrappers auto-compose their tools in this SDK

Data Science example cannot fetch S3
- Supply a local CSV or adjust the example to a synthetic dataset toggle for offline runs


## Contributing

Contributions are welcome. Please open an issue or PR on GitHub.


## License

See LICENSE file. Copyright © 2025 UltraSafe AI.
