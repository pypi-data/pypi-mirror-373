# USF Agents SDK (Python)

Production-grade, OpenAI-compatible Agents SDK for planning, tool execution, and multi‑agent orchestration on the official USF Agent APIs.

This release focuses on a simpler, more powerful developer experience:
- Define tool schemas from docstrings (Google/NumPy) or an optional YAML block — no verbose JSON required.
- Use the lightweight @tool decorator for defaults (name/alias/description) and optionally provide the full schema there too.
- Register tools in one line, batch-register multiple functions, or discover from a module.
- Compose sub-agents with a single call and auto-execute to a final answer with robust policies.

Contents
- Features
- Configuration Reference
- Installation
- Requirements
- Quickstart (copy/paste runnable)
- Tool Definitions Made Simple (Docstrings, YAML, @tool, strictness, explicit schema)
- Auto Execution Modes
- Multi-Agent in Fewer Lines
- Registry Option (alternate flow)
- Advanced Cookbook (end-to-end)
- Migration Notes (breaking changes)
- Troubleshooting / FAQ
- Contributing / License

--------------------------------------------------------------------------------

## Features

- Docstring-driven tool schemas
  - Precedence: YAML block (OpenAPI-like) → Google-style Args → NumPy-style Parameters
  - Required-parameter equality with signature automatically enforced
- @tool decorator
  - Provide defaults (name, alias, description)
  - Optionally provide the full OpenAI tool schema on the decorator
- Batch registration of tools
  - add_function_tools([...])
  - add_function_tools_from_module(module, filter=...)
- One-call auto execution (plan → tool_calls → final) with policy modes
  - disable | auto | agent | tool
- Multi-agent (manager + sub-agents) in one or two lines each
- Per-agent tool name uniqueness validation
- Strong sequencing safety utilities (unchanged)
- Tracing, workflows, and visualization (unchanged)

--------------------------------------------------------------------------------

## Configuration Reference

Global config for USFAgent (defaults in parentheses)
- api_key: str (required)
- model: str = 'usf-mini'
- provider: Optional[str] = None (planning/tool-calling/final_response; one of: openrouter, openai, claude, huggingface-inference, groq; for final_response it's only needed for custom providers/models)
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
- debug: bool = False

Example (global + stage overrides)
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import os, asyncio
from usf_agents import USFAgent

async def main():
    agent = USFAgent({
        "api_key": os.getenv("USF_API_KEY"),
        "model": "usf-mini",
        "backstory": "Power user of the system.",
        "goal": "Concise, accurate answers.",
        "temp_memory": {"enabled": True, "max_length": 5, "auto_trim": True},
        "max_loops": 10,
        "planning": {
            "model": "usf-mini",
            "introduction": "You are planning the steps to solve the task.",
            "knowledge_cutoff": "15 January 2025",
            "debug": True
        },
        "tool_calling": {
            "provider": "",
            "model": "usf-mini",
            "debug": True
        },
        "final_response": {
            "model": "usf-mini",
            "temperature": 0.5,
            "max_tokens": 512,
            "top_p": 1.0
        }
    })

    async for chunk in agent.run("Say hello world"):
        if chunk["type"] == "final_answer":
            print("Final:", chunk["content"]); break

asyncio.run(main())
# PY
```

Stage configs (optional, override fallbacks)
- planning: Dict[str, Any]
  - Supports: api_key, provider, model, introduction, knowledge_cutoff, temperature, stop, debug, ...
- tool_calling: Dict[str, Any]
  - Supports: api_key, provider, model, introduction, knowledge_cutoff, temperature, stop, debug, ...
- final_response: Dict[str, Any]
  - Supports: api_key, provider, model, temperature, stop, date_time_override, debug, final_instruction_mode, final_instruction_text, final_instruction_append, disable_final_instruction, ...
  - Also passes through OpenAI Chat Completions params via extra kwargs:
    response_format, max_tokens, top_p, presence_penalty, frequency_penalty,
    logit_bias, seed, user, stream_options
  - Note: Do not include "tools" in final_response; tools are not used in the final stage.

Provider usage (planning/tool-calling/final_response)
- Default engine is "usf-mini" when no provider is specified.
- For planning/tool_calling, set provider to one of: openrouter, openai, claude, huggingface-inference, groq.
- For final_response, provider is optional and typically only needed for custom providers/models. When provided, the SDK resolves the OpenAI-compatible base_url via https://api.us.inc/usf/v1/usf-agent/get-base-url (using your USF apiKey) and routes the call accordingly.
- If provider is omitted for final_response, the default USF endpoint is used (or an explicitly supplied base_url).
- Resolver errors (status: 0 or HTTP errors) are surfaced unchanged to help developers debug quickly.

Example (provider on planning/tool_calling/final_response)
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import os, asyncio
from usf_agents import USFAgent

async def main():
    agent = USFAgent({
        "api_key": os.getenv("USF_API_KEY"),
        "planning": {"provider": "openai", "model": "gpt-4o-mini"},
        "tool_calling": {"provider": "claude", "model": "claude-sonnet-4"},
        "final_response": {"provider": "groq", "model": "meta-llama/llama-4-maverick-17b-128e-instruct"},
    })
    async for chunk in agent.run("Plan then answer without tools"):
        if chunk["type"] == "final_answer":
            print("Final:", chunk["content"]); break

asyncio.run(main())
# PY
```

Per-run options (passed to agent.run(messages, options))
- tools: List[Tool] (OpenAI function tool format)
- planning/tool_calling/final_response: per-call overrides
- temperature, stop, date_time_override, debug, max_loops
- skip_planning_if_no_tools: bool (default False). When True and effective tools == [], the agent skips the planning phase and directly generates a final answer via the LLM. Managers with sub-agents will not skip because sub-agents are exposed as tools (tools != []).

Example (per-run overrides; no tools to ensure final output)
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import os, asyncio
from usf_agents import USFAgent

async def main():
    agent = USFAgent({"api_key": os.getenv("USF_API_KEY")})
    opts = {
      "temperature": 0.2,
      "max_loops": 5,
      "final_response": {
        "date_time_override": {
          "enabled": True,
          "date": "08/31/2025",
          "time": "07:00:00 AM",
          "timezone": "UTC"
        }
      }
    }
    async for chunk in agent.run("Reply with the current date/time string from system context.", opts):
        if chunk["type"] == "final_answer":
            print("Final:", chunk["content"]); break

asyncio.run(main())
# PY
```

## Skip planning when no tools (opt-in per agent)

Default behavior
- Planning is enabled by default for all agents (skip_planning_if_no_tools defaults to False).
- No inheritance: a manager’s setting does not propagate to sub-agents automatically. Sub-agents must opt-in explicitly if desired.
- Important: If an agent has sub-agents, those sub-agents are exposed as tools, so planning will not be skipped since tools != [].

Usage
- Per-agent (standalone):
```python
agent = USFAgent({
  "api_key": "...",
  "skip_planning_if_no_tools": True  # only skips when there are no tools
})
```

- Per-run override:
```python
async for chunk in agent.run("Explain Kafka", {"skip_planning_if_no_tools": True}):
    if chunk["type"] == "final_answer":
        print("Final:", chunk["content"]); break
```

- Sub-agent explicit opt-in (no inheritance from manager):
```python
from usf_agents.multi_agent.base import ManagerAgent, SubAgent

api_key = "..."
mgr = ManagerAgent({"id":"mgr","agent_type":"manager","usf_config":{"api_key": api_key}})

# Either explicit SubAgent with own usf_config
writer = SubAgent({
  "id":"writer",
  "agent_type":"sub",
  "context_mode":"NONE",
  "description":"Write short summaries.",
  "usf_config":{"api_key": api_key, "skip_planning_if_no_tools": True}
})
mgr.add_sub_agent(writer, {"description": writer.description, "parameters":{"type":"object","properties":{"task":{"type":"string"}},"required":["task"]}}, alias="agent_writer")

# Or via add_sub_agent_simple overrides (opt-in per sub)
mgr.add_sub_agent_simple(
  id="writer2",
  alias="agent_writer2",
  context_mode="NONE",
  description="Write short summaries.",
  usf_overrides={"skip_planning_if_no_tools": True}
)
```

Notes
- Managers with sub-agents: planning will not be skipped because the composed tool list includes sub-agents (tools != []).
- Standalone managers without sub-agents or native tools can skip if explicitly enabled.

Date/time override (final response stage)
- final_response.date_time_override: { enabled: bool, date: 'MM/DD/YYYY', time: 'HH:MM:SS AM/PM', timezone: 'IANA or label' }

Example (snippet)
```python
opts = {
  "final_response": {
    "date_time_override": {
      "enabled": True,
      "date": "12/31/2025",
      "time": "11:59:59 PM",
      "timezone": "America/Los_Angeles"
    }
  }
}
```

Tool schema (OpenAI function-call compatible)
- Tool = {'type': 'function','function': {'name': str,'description': str,'parameters': JSONSchema}}

Example
```python
tool = {
  "type": "function",
  "function": {
    "name": "http_get",
    "description": "Fetch a URL",
    "parameters": {
      "type": "object",
      "properties": {"url": {"type": "string", "description": "URL to fetch"}},
      "required": ["url"]
    }
  }
}
```

Tool call format (from assistant)
- {'id': '...', 'type': 'function', 'function': {'name': '...', 'arguments': JSON-string}}

Tool result message (from developer)
- {'role': 'tool','tool_call_id': '...', 'name': 'tool_name','content': JSON-string}

Example (manual loop, conceptual)
```python
assistant_tool_calls = {
  "role": "assistant",
  "tool_calls": [
    {"id": "call_1", "type": "function", "function": {"name": "http_get", "arguments": "{\"url\":\"https://example.com\"}"}}
  ],
  "type": "tool_calls"
}
tool_result = {
  "role": "tool",
  "tool_call_id": "call_1",
  "name": "http_get",
  "content": "{\"status\":200,\"body\":\"ok\"}"
}
# Append both to messages before calling agent.run() again.
```

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
- list_tools() -> List[Tool] (native + sub-agents as tools)
- delegate(sub_id, task, policy='inherit_manager_policy', context_param=None, calling_context=None, options=None)
- SubAgent.execute_as_tool(tool_call, calling_context, context_param=None, options=None)
- SubAgent.execute_as_tool_until_final(tool_call, calling_context, context_param=None, options=None)

Example (compose and delegate)
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import os, asyncio
from usf_agents.multi_agent.base import ManagerAgent, SubAgent

async def main():
    api_key = os.getenv("USF_API_KEY")
    mgr = ManagerAgent({"id":"mgr","name":"Manager","agent_type":"manager","usf_config":{"api_key":api_key}})

    calc = SubAgent({
      "id":"calc","name":"Calculator","agent_type":"sub","context_mode":"NONE",
      "description":"Numeric computations: sum/avg/min/max. Example: task='compute', input={'expression':'25*4'}",
      "usf_config":{"api_key": api_key}
    })
    writer = SubAgent({
      "id":"writer","name":"Writer","agent_type":"sub","context_mode":"ALWAYS_FULL",
      "description":"Write short summaries.",
      "usf_config":{"api_key": api_key}
    })
    mgr.add_sub_agent(calc, {"description": calc.description, "parameters":{"type":"object","properties":{"task":{"type":"string"}},"required":["task"]}}, alias="agent_calc")
    mgr.add_sub_agent(writer, {"description": writer.description, "parameters":{"type":"object","properties":{"task":{"type":"string"}},"required":["task"]}}, alias="agent_writer")

    # List tools exposed by manager (includes sub-agents as tools)
    tools = mgr.list_tools()
    print("Tools:", [t["function"]["name"] for t in tools])

    # Delegate a task explicitly
    res = await mgr.delegate("calc", {"task":"compute","input":{"expression":"12*7"}})
    print("Delegate:", res["success"], res.get("content",""))

asyncio.run(main())
# PY
```

Context shaping utilities
- sanitize_parent_context(msgs): keep only user and final-answer assistant messages for delegation
- shape_context_for_mode(mode, task, calling_agent_msgs=None, context_param=None) -> List[Message]

Example
```python
from usf_agents.multi_agent.context import sanitize_parent_context, shape_context_for_mode
clean = sanitize_parent_context([
  {"role":"user","content":"Hi"},
  {"role":"assistant","content":"Plan ...","type":"agent_plan","plan":"..."},
  {"role":"assistant","content":"Final answer here"}
])
msgs = shape_context_for_mode("CONTEXT_PARAM", {"task":"write","input":{"topic":"X"}}, calling_agent_msgs=clean, context_param={"audience":"exec"})
```

Sequencing helpers
- validate_next_step(messages) -> raises if invalid to call run()
- run_until_final(agent, messages, tools, tool_router, max_loops=20) -> str

Example
```python
from usf_agents.runtime.validate import validate_next_step
from usf_agents.runtime.safe_seq import run_until_final
# validate_next_step(messages) before calling agent.run()
# run_until_final(...) drives plan -> tool_calls -> tool results -> final
```

Auto tracing and visualization (no graph spec)

You do not need to define any WorkflowGraph. Tracing is OFF by default. Enable it per call by passing trace=True to run_task, which returns a (result, trace) tuple. Render visuals from the trace.

APIs
- Visualizers (trace-only):
  - from usf_agents.trace.visualize import (
    to_mermaid_trace, to_graphviz_trace, to_json_trace, final_node,
    mermaid_png_base64, mermaid_svg_base64, mermaid_png_data_uri, mermaid_svg_data_uri
)

Example: run an agent to a final answer and render the exact trajectory (one flag)
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import os, asyncio
from usf_agents.multi_agent.base import SubAgent
from usf_agents.trace.visualize import to_mermaid_trace, to_graphviz_trace, to_json_trace, final_node

async def main():
    api_key = os.getenv("USF_API_KEY")
    writer = SubAgent({
        "id":"writer","agent_type":"sub","context_mode":"NONE",
        "description":"Write short summaries",
        "usf_config":{"api_key": api_key}
    })

    # Tracing OFF by default. Enable per call with trace=True (returns result, trace)
    result, trace = await writer.run_task({"task":"write","input":{"topic":"teamwork"}}, trace=True)

    print("Final:", result.get("content",""))
    print("Final node:", final_node(trace))                 # last node that produced a final
    print("Mermaid:\\n", to_mermaid_trace(trace))           # paste into https://mermaid.live
    print("Graphviz DOT:\\n", to_graphviz_trace(trace))     # optional: dot -Tpng graph.dot -o graph.png
    print("Trace JSON:\\n", to_json_trace(trace))

    # Optional: inline images in Jupyter Notebook (no files; requires internet for mermaid.ink)
    try:
        from IPython.display import Image, SVG, display
        import base64
        # PNG
        png_b64 = mermaid_png_base64(trace)
        print("PNG base64 (first 100):", (png_b64 or "")[:100], "...")
        png_data_uri = mermaid_png_data_uri(trace)
        print("PNG data URI (first 120):", (png_data_uri or "")[:120], "...")
        if png_b64:
            display(Image(data=base64.b64decode(png_b64)))
        # SVG
        svg_b64 = mermaid_svg_base64(trace)
        print("SVG base64 (first 100):", (svg_b64 or "")[:100], "...")
        svg_data_uri = mermaid_svg_data_uri(trace)
        print("SVG data URI (first 120):", (svg_data_uri or "")[:120], "...")
        if svg_b64:
            svg_xml = base64.b64decode(svg_b64).decode("utf-8", errors="ignore")
            display(SVG(data=svg_xml))
    except Exception:
        # Safe no-op outside notebooks or without IPython
        pass

asyncio.run(main())
# PY
```

How to view the visuals
- Mermaid: copy the printed diagram text into https://mermaid.live to render.
- Graphviz (optional local rendering):
  - Save the DOT text to a file, e.g., graph.dot
  - macOS: brew install graphviz
  - dot -Tpng graph.dot -o graph.png

Export Mermaid diagram as base64 image (no files)
- In-memory only. These helpers fetch rendered images from mermaid.ink and return base64 strings or data URIs (requires internet).
```python
# After you have `trace` from run_task(..., trace=True)
from usf_agents.trace.visualize import (
  mermaid_png_base64, mermaid_png_data_uri,
  mermaid_svg_base64, mermaid_svg_data_uri,
)

png_b64 = mermaid_png_base64(trace)               # base64-encoded PNG
print("PNG base64 (first 100):", png_b64[:100], "...")

png_data_uri = mermaid_png_data_uri(trace)        # data:image/png;base64,...
print("PNG data URI (first 120):", png_data_uri[:120], "...")

svg_b64 = mermaid_svg_base64(trace)               # base64-encoded SVG
print("SVG base64 (first 100):", svg_b64[:100], "...")

svg_data_uri = mermaid_svg_data_uri(trace)        # data:image/svg+xml;base64,...
print("SVG data URI (first 120):", svg_data_uri[:120], "...")
```

Notes
- Tracing is opt-in and extremely lightweight. When trace=False (default), there is no tracing and no overhead.
- The diagram is built purely from runtime events (delegations, tool calls/results, final). No manual graph spec or tool executors required.
--------------------------------------------------------------------------------

## Installation

```bash
pip install usf-agents
```

## Requirements

- Python 3.9+
- USF API key: set environment variable USF_API_KEY

--------------------------------------------------------------------------------

## Quickstart (minimal and runnable)

All code below assumes your environment has USF_API_KEY set.

Windows PowerShell: $env:USF_API_KEY="YOUR_KEY"  
Windows cmd: set USF_API_KEY=YOUR_KEY && python ...

1) Plain LLM (no tools)
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import os
import asyncio
from usf_agents import USFAgent

async def main():
    agent = USFAgent(
        {
            "api_key": os.getenv("USF_API_KEY"),
            "model": "usf-mini",
        }
    )
    async for chunk in agent.run("Hello, what's the capital of France?"):
        if chunk["type"] == "final_answer":
            print("Final:", chunk["content"])
            break

asyncio.run(main())
# PY
```

2) ManagerAgent, no tools (planning → final)
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import os
import asyncio
from usf_agents.multi_agent.base import ManagerAgent

async def main():
    mgr = ManagerAgent(
        {
            "id": "mgr",
            "name": "Manager",
            "agent_type": "manager",
            "usf_config": {
                "api_key": os.getenv("USF_API_KEY"),
                "model": "usf-mini",
            },
        }
    )
    async for chunk in mgr.usf.run("Summarize the benefits of unit testing."):
        if chunk["type"] == "final_answer":
            print("Final:", chunk["content"])
            break

asyncio.run(main())
# PY
```

### Write good sub-agent descriptions

Provide a clear, scoped description on every SubAgent via the description field. This string is surfaced as the tool's function.description and helps the LLM pick the right tool when multiple tools are available.

Guidelines:
- Start with an action + domain: “Numeric computations…”, “Rapid web/knowledge lookup…”
- Clarify inputs/outputs briefly (align with task/input/context_param contract)
- Include one inline example matching the schema:
  - Example: task='compute', input={'expression': 'sum(prices)'}
- Avoid overlap between agents; make distinctions obvious and unambiguous

Bad:
- “General helper” or “Do analysis”

Good:
- “Generate/refactor code from specs with optional context_param snippets. Example: task='function', input={'signature': 'total_cost(prices: list[float]) -> float'}”

--------------------------------------------------------------------------------

## Tool Definitions Made Simple

Precedence for how a schema is determined (highest to lowest):
1) Schema passed to add_function_tool(..., schema=...)
2) Schema provided in the @tool decorator (schema=...)
3) Docstring parsing (YAML block → Google-style Args → NumPy-style Parameters)

Validation
- Always enforced: schema.required must equal the set of parameters with no default values in the function signature (excluding *args/**kwargs).
- Optional strict properties mode (strict=True) enforces exact equality between schema.properties keys and the function parameters.

A) Single function tool via Google-style docstring (no explicit schema)
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import os
import asyncio
from usf_agents.multi_agent.base import ManagerAgent

def calc(expression: str) -> int:
    """
    Evaluate a simple expression.
    Args:
        expression (str): A Python expression to evaluate.
    """
    return eval(expression)  # demo; use a safe evaluator in production

async def main():
    mgr = ManagerAgent(
        {
            "id": "mgr",
            "usf_config": {"api_key": os.getenv("USF_API_KEY"), "model": "usf-mini"},
        }
    )
    mgr.add_function_tool("calc", calc, alias="math_calc")
    final = await mgr.run_auto(
        [{"role": "user", "content": "Use math_calc to compute 25*4"}],
        mode="auto",
    )
    print("Final:", final)

asyncio.run(main())
# PY
```

B) NumPy-style docstring (no explicit schema)
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import os
import asyncio
from usf_agents.multi_agent.base import ManagerAgent

def greet(name: str) -> str:
    """
    Greet a user.

    Parameters
    ----------
    name : str
        Person to greet.
    """
    return f"Hello {name}!"

async def main():
    mgr = ManagerAgent(
        {
            "id": "mgr",
            "usf_config": {"api_key": os.getenv("USF_API_KEY"), "model": "usf-mini"},
        }
    )
    mgr.add_function_tool("greet", greet, alias="hello")
    final = await mgr.run_auto(
        [{"role": "user", "content": "Use hello for \"USF\""}],
        mode="auto",
    )
    print("Final:", final)

asyncio.run(main())
# PY
```

C) YAML block in docstring (takes precedence; no explicit schema)
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import os
import asyncio
from usf_agents.multi_agent.base import ManagerAgent

def http_get(url: str) -> dict:
    """
    Perform GET.

    ```yaml
    description: Simple HTTP GET (demo)
    parameters:
      type: object
      properties:
        url:
          type: string
          description: URL to fetch
      required: [url]
    ```
    Args:
        url (str): URL to fetch.  # Fallback for environments without PyYAML
    """
    return {"status": 200, "body": "ok"}

async def main():
    mgr = ManagerAgent(
        {
            "id": "mgr",
            "usf_config": {"api_key": os.getenv("USF_API_KEY"), "model": "usf-mini"},
        }
    )
    mgr.add_function_tool("http_get", http_get)
    final = await mgr.run_auto(
        [{"role": "user", "content": "Call http_get with https://example.com"}],
        mode="auto",
    )
    print("Final:", final)

asyncio.run(main())
# PY
```

D) @tool decorator with defaults (name/alias/description) and docstring schema
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import os
import asyncio
from usf_agents.multi_agent.base import ManagerAgent
from usf_agents.runtime.decorators import tool

@tool(name="calc_sum", alias="sum_tool", description="Sum a list of integers")
def calc_sum(numbers: list[int]) -> int:
    """
    Sum integers.
    Args:
        numbers (list[int]): Values to add up.
    """
    return sum(numbers)

async def main():
    mgr = ManagerAgent(
        {
            "id": "mgr",
            "usf_config": {"api_key": os.getenv("USF_API_KEY"), "model": "usf-mini"},
        }
    )
    mgr.add_function_tool("calc_sum", calc_sum)  # decorator defaults used
    final = await mgr.run_auto(
        [{"role": "user", "content": "Use sum_tool to sum 10,20,30"}],
        mode="auto",
    )
    print("Final:", final)

asyncio.run(main())
# PY
```

E) @tool decorator with an explicit schema in the decorator (no explicit schema passed to add_function_tool)
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import os
import asyncio
from usf_agents.multi_agent.base import ManagerAgent
from usf_agents.runtime.decorators import tool

@tool(
    name="calc_sum",
    alias="sum_tool",
    description="Sum a list of integers",
    schema={
        "description": "Sum integers",
        "parameters": {
            "type": "object",
            "properties": {"numbers": {"type": "array", "description": "List of ints"}},
            "required": ["numbers"],
        },
    },
)
def calc_sum(numbers: list[int]) -> int:
    return sum(numbers)

async def main():
    mgr = ManagerAgent(
        {
            "id": "mgr",
            "usf_config": {"api_key": os.getenv("USF_API_KEY"), "model": "usf-mini"},
        }
    )
    # No schema passed here; decorator schema used and validated
    mgr.add_function_tool("calc_sum", calc_sum)
    final = await mgr.run_auto(
        [{"role": "user", "content": "Use sum_tool to sum 1..5"}],
        mode="auto",
    )
    print("Final:", final)

asyncio.run(main())
# PY
```

F) Explicit JSON schema passed to add_function_tool (overrides decorator/docstrings)
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import os
import asyncio
from usf_agents.multi_agent.base import ManagerAgent

def calc(expression: str) -> int:
    return eval(expression)

async def main():
    mgr = ManagerAgent(
        {
            "id": "mgr",
            "usf_config": {"api_key": os.getenv("USF_API_KEY"), "model": "usf-mini"},
        }
    )
    mgr.add_function_tool(
        "calc",
        calc,
        alias="math_calc",
        schema={
            "description": "Evaluate math expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Python expression"}
                },
                "required": ["expression"],
            },
        },
        strict=False,  # set True to require properties set equality too
    )
    final = await mgr.run_auto(
        [{"role": "user", "content": "Use math_calc to compute 9*9"}],
        mode="auto",
    )
    print("Final:", final)

asyncio.run(main())
# PY
```

G) Type mapping example (string/number/boolean/object/array) via explicit schema
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import os
import asyncio
from usf_agents.multi_agent.base import ManagerAgent

def demo(a: str, n: int, flag: bool, cfg: dict, items: list) -> dict:
    return {"ok": True}

async def main():
    mgr = ManagerAgent(
        {
            "id": "mgr",
            "usf_config": {"api_key": os.getenv("USF_API_KEY"), "model": "usf-mini"},
        }
    )
    mgr.add_function_tool(
        "demo",
        demo,
        schema={
            "description": "Type mapping demo",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "string", "description": "string input"},
                    "n": {"type": "number", "description": "numeric input"},
                    "flag": {"type": "boolean", "description": "boolean toggle"},
                    "cfg": {"type": "object", "description": "config object"},
                    "items": {"type": "array", "description": "list of items"},
                },
                "required": ["a", "n", "flag", "cfg", "items"],
            },
        },
        strict=True,
    )
    final = await mgr.run_auto(
        [{"role": "user", "content": "Call demo with required fields"}],
        mode="auto",
    )
    print("Final:", final)

asyncio.run(main())
# PY
```

--------------------------------------------------------------------------------

## Auto Execution Modes

Summary
- disable: do not auto-run tools; return the assistant’s first tool_calls payload to the caller for manual handling.
- auto (default): auto-run both agent tools (sub-agents) and custom tools until final (or max_loops).
- agent: auto-run only agent tools; custom tool requests are returned to the caller as pending tool_calls.
- tool: auto-run only custom tools; agent tool requests are returned as pending tool_calls.

## Final Response Instruction Controls (overwrite/append/disable)

By default, the SDK appends a safety/UX instruction block to the last planning message before generating the final answer. You can fully control this behavior:

- default: keep the built-in instruction block unchanged
- append: insert your additional guidance just before </IMPORTANT> (prefixed with a "\n---\n" separator)
- overwrite: replace the entire block with your own text
- disable: add no instruction at all (takes precedence if disable_final_instruction is True)

Notes
- If </IMPORTANT> is not found during append, your text is appended at the end with the separator.
- When the instruction is present, “User Backstory” and “User Goal” (if provided) are appended after the block.
- These keys are handled internally and are not forwarded to the underlying OpenAI-compatible client.

Examples

Append additional guidance (inserted just before </IMPORTANT>)
```python
from usf_agents import USFAgent

agent = USFAgent({
  "api_key": "...",
  "final_response": {
    "final_instruction_mode": "append",
    "final_instruction_append": "Use a brief summary and clear next steps."
  }
})
```

Overwrite the instruction completely
```python
agent = USFAgent({
  "api_key": "...",
  "final_response": {
    "final_instruction_mode": "overwrite",
    "final_instruction_text": "<IMPORTANT>\nProvide a concise, complete answer without calling any services.\n</IMPORTANT>"
  }
})
```

Disable the instruction
```python
agent = USFAgent({
  "api_key": "...",
  "final_response": {
    "disable_final_instruction": True
    # or: "final_instruction_mode": "disable"
  }
})
```

--------------------------------------------------------------------------------

## Multi-Agent in Fewer Lines

Add sub-agents in one line and run end-to-end.
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import os
import asyncio
from usf_agents.multi_agent.base import ManagerAgent

async def main():
    mgr = ManagerAgent(
        {
            "id": "mgr",
            "name": "Manager",
            "agent_type": "manager",
            "usf_config": {
                "api_key": os.getenv("USF_API_KEY"),
                "model": "usf-mini",
            },
        }
    )
    # Sub-agent appears as tool "agent_writer"
    mgr.add_sub_agent_simple(
        id="writer",
        alias="agent_writer",
        context_mode="NONE",
        description="Draft short outputs",
    )
    final = await mgr.run_auto(
        [{"role": "user", "content": "Ask agent_writer to write a haiku about teamwork."}],
        mode="auto",
    )
    print("Final:", final)

asyncio.run(main())
# PY
```

Production-grade pattern: explicit SubAgent instances (cleaner structure)
```python
from usf_agents.multi_agent.base import SubAgent

api_key = os.getenv("USF_API_KEY")

# Model is optional; defaults to "usf-mini" if omitted
calculator = SubAgent(
    {
        "id": "calc",
        "name": "Calculator",
        "agent_type": "sub",
        "context_mode": "NONE",
        "description": "Perform numeric computations such as sum/avg/min/max. Example: expression='25*4'",
        "usf_config": {"api_key": api_key},
    }
)
researcher = SubAgent(
    {
        "id": "research",
        "name": "Researcher",
        "agent_type": "sub",
        "context_mode": "AGENT_DECIDED",
        "description": "Look up and synthesize knowledge from external sources. Example: topic='UltraWidget market trends'",
        "usf_config": {"api_key": api_key},
    }
)
coder = SubAgent(
    {
        "id": "coder",
        "name": "Code Assistant",
        "agent_type": "sub",
        "context_mode": "CONTEXT_PARAM",
        "description": "Generate or refactor code from specifications.",
        "usf_config": {"api_key": api_key},
    }
)
writer = SubAgent(
    {
        "id": "writer",
        "name": "Writer",
        "agent_type": "sub",
        "context_mode": "ALWAYS_FULL",
        "description": "Write polished summaries, briefs, or emails.",
        "usf_config": {"api_key": api_key},
    }
)

# Register any number in one call (varargs or list)
mgr.add_sub_agents(calculator, researcher, coder, writer)
# or
mgr.add_sub_agents([calculator, researcher])
```

Quick prototyping (dict specs) remains supported
```python
mgr.add_sub_agents([
    {'id':'logs', 'alias':'agent_logs', 'context_mode':'AGENT_DECIDED', 'description':'AAnalyze system/application logs for errors and anomalies.'}
])
```

--------------------------------------------------------------------------------

## Per-SubAgent Final-Response Instruction Controls

Sub-agents can use the same final-response instruction controls as top-level agents. By default, a sub-agent inherits the manager’s USF config. You can override per sub-agent in three ways:

- Explicit SubAgent with its own usf_config (full control)
- Via ManagerAgent.add_sub_agent_simple(..., usf_overrides={ ... })
- Via ManagerAgent.add_sub_agents([... dict spec with "usf_overrides": {...} ...])

Semantics
- default: keep the built-in instruction block unchanged
- append: insert your additional guidance just before </IMPORTANT> (prefixed with a "\n---\n" separator)
- overwrite: replace the entire block with your own text
- disable: add no instruction at all (takes precedence if disable_final_instruction is True)
- If </IMPORTANT> is not found during append, your text is appended at the end with the separator.
- When the instruction is present, “User Backstory” and “User Goal” (if provided) are appended after the block.

A) Explicit SubAgent with its own usf_config
```python
from usf_agents.multi_agent.base import ManagerAgent, SubAgent

api_key = os.getenv("USF_API_KEY")
mgr = ManagerAgent({
  "id": "mgr",
  "name": "Manager",
  "agent_type": "manager",
  "usf_config": {"api_key": api_key}
})

writer = SubAgent({
  "id": "writer",
  "name": "Writer",
  "agent_type": "sub",
  "context_mode": "NONE",
  "description": "Draft short outputs",
  "usf_config": {
    "api_key": api_key,
    "final_response": {
      "final_instruction_mode": "disable"    # or "append"/"overwrite"
    }
  }
})
mgr.add_sub_agent(
  writer,
  {"description": writer.description, "parameters": {"type": "object", "properties": {"task": {"type": "string"}}, "required": ["task"]}},
  alias="agent_writer"
)
```

B) add_sub_agent_simple with per-sub overrides
```python
mgr.add_sub_agent_simple(
  id="writer",
  alias="agent_writer",
  context_mode="NONE",
  description="Draft short outputs",
  usf_overrides={
    "final_response": {
      "final_instruction_mode": "append",
      "final_instruction_append": "Use bullets for steps."
    }
  }
)
```

C) add_sub_agents with dict spec and usf_overrides
```python
mgr.add_sub_agents([
  {
    "id": "writer",
    "alias": "agent_writer",
    "context_mode": "NONE",
    "description": "Draft short outputs",
    "usf_overrides": {
      "final_response": {
        "final_instruction_mode": "overwrite",
        "final_instruction_text": "<IMPORTANT>\nProvide concise answers with a short summary.\n</IMPORTANT>"
      }
    }
  }
])
```

Note on merging
- usf_overrides are shallow-merged onto the manager’s base config with a targeted deep-merge of stage keys: planning, tool_calling, final_response. You can safely override only final_response without copying the entire config.
- These keys are handled internally and are not forwarded to the underlying OpenAI-compatible client.

## Registry Option (alternate flow)

Register tools with ToolRegistry and use run_auto façade.
```python
# run: USF_API_KEY=YOUR_KEY python - <<'PY'
import os
import asyncio
from usf_agents import USFAgent
from usf_agents.runtime.tool_registry import ToolRegistry
from usf_agents.runtime.auto_exec import run_auto

def calc(expression: str) -> int:
    return eval(expression)

async def main():
    agent = USFAgent(
        {
            "api_key": os.getenv("USF_API_KEY"),
            "model": "usf-mini",
        }
    )
    registry = ToolRegistry()
    registry.register_function(
        name="calc",
        func=calc,
        schema={
            "description": "calc",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
        examples=[{"name": "smoke", "args": {"expression": "2+3"}, "expect": 5}],
    )
    final = await run_auto(
        agent,
        [{"role": "user", "content": "Use calc to compute 25*4"}],
        registry=registry,
        mode="auto",
    )
    print("Final:", final)

asyncio.run(main())
# PY
```

--------------------------------------------------------------------------------

## Advanced Cookbook (end-to-end)

A) Incident Response Orchestrator (compressed)
```python
# Pseudo-runnable: fill USF_API_KEY and run in a cell/script
import os
import asyncio
from usf_agents.multi_agent.base import ManagerAgent, SubAgent

async def main():
    api_key = os.getenv("USF_API_KEY")
    mgr = ManagerAgent(
        {
            "id": "ir_mgr",
            "name": "Incident Orchestrator",
            "agent_type": "manager",
            "usf_config": {"api_key": api_key},
        }
    )

    logs = SubAgent(
        {
            "id": "logs",
            "name": "Logs Analyzer",
            "agent_type": "sub",
            "context_mode": "AGENT_DECIDED",
            "description": "Analyze system/application logs for errors and anomalies.",
            "usf_config": {"api_key": api_key},
        }
    )
    rootcause = SubAgent(
        {
            "id": "rootcause",
            "name": "Root Cause",
            "agent_type": "sub",
            "context_mode": "ALWAYS_FULL",
            "description": "Infer root cause from logs, metrics, and incident context.",
            "usf_config": {"api_key": api_key},
        }
    )
    remediate = SubAgent(
        {
            "id": "remediate",
            "name": "Remediate",
            "agent_type": "sub",
            "context_mode": "CONTEXT_PARAM",
            "description": "Suggest remediation steps for known issues.",
            "usf_config": {"api_key": api_key},
        }
    )
    comms = SubAgent(
        {
            "id": "comms",
            "name": "Comms",
            "agent_type": "sub",
            "context_mode": "ALWAYS_FULL",
            "description": "Draft stakeholder communications (incident reports, updates, notices).",
            "usf_config": {"api_key": api_key},
        }
    )

    mgr.add_sub_agents(logs, rootcause, remediate, comms)

    brief = (
        "SEV-1 Incident: summarize logs, root cause, remediations, "
        "and draft stakeholder update."
    )
    final = await mgr.run_auto([{"role": "user", "content": brief}], mode="auto")
    print("Final:", final)

# asyncio.run(main())
```

B) Product Launch Orchestrator (compressed)
```python
import os
import asyncio
from usf_agents.multi_agent.base import ManagerAgent, SubAgent

async def main():
    api_key = os.getenv("USF_API_KEY")
    mgr = ManagerAgent(
        {
            "id": "pl_mgr",
            "name": "Launch Orchestrator",
            "agent_type": "manager",
            "usf_config": {"api_key": api_key},
        }
    )

    req = SubAgent(
        {
            "id": "requirements",
            "name": "Requirements",
            "agent_type": "sub",
            "context_mode": "ALWAYS_FULL",
            "description": "Extract and clarify project or product requirements.",
            "usf_config": {"api_key": api_key},
        }
    )
    planner = SubAgent(
        {
            "id": "planner",
            "name": "Planner",
            "agent_type": "sub",
            "context_mode": "NONE",
            "description": "Plan project milestones, timelines, or resources.",
            "usf_config": {"api_key": api_key},
        }
    )
    risk = SubAgent(
        {
            "id": "risk",
            "name": "Risk",
            "agent_type": "sub",
            "context_mode": "AGENT_DECIDED",
            "description": "Identify risks and propose mitigations for projects.",
            "usf_config": {"api_key": api_key},
        }
    )
    writer = SubAgent(
        {
            "id": "writer",
            "name": "Writer",
            "agent_type": "sub",
            "context_mode": "ALWAYS_FULL",
            "description": "Produce clear summaries, briefs, and reports for stakeholders.",
            "usf_config": {"api_key": api_key},
        }
    )
    mgr.add_sub_agents(req, planner, risk, writer)

    ask = (
        "Extract constraints, plan timeline/cost, risks/mitigation, "
        "and craft launch email + internal brief."
    )
    final = await mgr.run_auto([{"role": "user", "content": ask}], mode="auto")
    print("Final:", final)
```

C) Data Science Orchestrator (compressed)
```python
import os
import asyncio
from usf_agents.multi_agent.base import ManagerAgent, SubAgent

async def main():
    api_key = os.getenv("USF_API_KEY")
    mgr = ManagerAgent(
        {
            "id": "ds_mgr",
            "name": "DS Orchestrator",
            "agent_type": "manager",
            "usf_config": {"api_key": api_key},
        }
    )

    fetch = SubAgent(
        {
            "id": "fetch",
            "name": "Data Fetcher",
            "agent_type": "sub",
            "context_mode": "CONTEXT_PARAM",
            "description": "Fetch datasets from sources given a query.",
            "usf_config": {"api_key": api_key},
        }
    )
    eda = SubAgent(
        {
            "id": "eda",
            "name": "EDA Analyzer",
            "agent_type": "sub",
            "context_mode": "AGENT_DECIDED",
            "description": "Perform exploratory data analysis on datasets.",
            "usf_config": {"api_key": api_key},
        }
    )
    model = SubAgent(
        {
            "id": "model",
            "name": "Model Coder",
            "agent_type": "sub",
            "context_mode": "CONTEXT_PARAM",
            "description": "Generate or refine ML model training and inference code.",
            "usf_config": {"api_key": api_key},
        }
    )
    report = SubAgent(
        {
            "id": "report",
            "name": "Report Writer",
            "agent_type": "sub",
            "context_mode": "ALWAYS_FULL",
            "description": "Write ML model training/inference code.",
            "usf_config": {"api_key": api_key},
        }
    )
    mgr.add_sub_agents(fetch, eda, model, report)

    req = "Churn dataset prototype: fetch, EDA, baseline code, concise report."
    final = await mgr.run_auto([{"role": "user", "content": req}], mode="auto")
    print("Final:", final)
```

D) Manager Dynamic Orchestrator (compressed)
```python
import os
import asyncio
from usf_agents.multi_agent.base import ManagerAgent, SubAgent

async def main():
    api_key = os.getenv("USF_API_KEY")
    mgr = ManagerAgent(
        {
            "id": "mgr",
            "name": "Dynamic Orchestrator",
            "agent_type": "manager",
            "usf_config": {"api_key": api_key},
        }
    )

    calculator = SubAgent(
        {
            "id": "calc",
            "name": "Calculator",
            "agent_type": "sub",
            "context_mode": "NONE",
            "description": "Numeric computations (sum/avg/min/max).}",
            "usf_config": {"api_key": api_key},
        }
    )
    researcher = SubAgent(
        {
            "id": "research",
            "name": "Researcher",
            "agent_type": "sub",
            "context_mode": "AGENT_DECIDED",
            "description": "Rapid web/knowledge lookup and synthesis.",
            "usf_config": {"api_key": api_key},
        }
    )
    coder = SubAgent(
        {
            "id": "coder",
            "name": "Code Assistant",
            "agent_type": "sub",
            "context_mode": "CONTEXT_PARAM",
            "description": "Generate/refactor code from specs with optional context_param snippets.",
            "usf_config": {"api_key": api_key},
        }
    )
    writer = SubAgent(
        {
            "id": "writer",
            "name": "Writer",
            "agent_type": "sub",
            "context_mode": "ALWAYS_FULL",
            "description": "Executive summaries, briefs, and emails.",
            "usf_config": {"api_key": api_key},
        }
    )
    mgr.add_sub_agents(calculator, researcher, coder, writer)

    task = (
        "For 'UltraWidget': compute total cost, research trends, generate Python function "
        "total_cost(prices: list[float]) -> float, and write an executive summary."
    )
    final = await mgr.run_auto([{"role": "user", "content": task}], mode="auto")
    print("Final:", final)
```

--------------------------------------------------------------------------------

## Troubleshooting / FAQ

- Error: “no explicit schema and no parseable docstring”
  - Add a Google/NumPy docstring or a YAML block, or pass schema explicitly to add_function_tool, or provide schema in the @tool decorator.
- Error: “required mismatch”
  - Ensure your schema.required equals the set of function parameters with no default values.
- Error with strict=True: “properties mismatch”
  - Ensure schema.parameters.properties keys match your function parameters exactly.
- YAML parsing
  - YAML blocks are optional. If PyYAML isn’t installed, YAML parsing is skipped and Google/NumPy parsing is attempted automatically.
- Tool name collisions
  - Per-agent tool names must be unique across native tools and sub-agents. Use aliases to disambiguate.

--------------------------------------------------------------------------------

## Contributing / License

License: USF Agents SDK License  
Copyright (c) 2025 UltraSafe AI Team

PERMITTED USE:
- Anyone may use this software for any purpose

RESTRICTED ACTIVITIES:
- No one may modify the code
- No one may use the code for commercial purposes
- No one may use the code to create competitive products

ATTRIBUTION:
- All copies of this software must retain this license notice
- Any use of this software must include attribution to UltraSafe AI Team
