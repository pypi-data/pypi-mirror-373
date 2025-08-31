import asyncio
import json
import os
import types
import pytest

from usf_agents.multi_agent.base import ManagerAgent, SubAgent
from usf_agents.runtime.decorators import tool
from usf_agents.runtime.tool_registry import ToolRegistry
from usf_agents.runtime.auto_exec import run_auto

try:
    import yaml  # type: ignore
    HAS_YAML = True
except Exception:
    HAS_YAML = False


# Helper fake run for custom tools (one or more tool calls), then final
async def _fake_run_with_calls(messages, calls, *, include_plan=True):
    has_results = any(m.get("role") == "tool" for m in messages)
    if not has_results:
        if include_plan:
            yield {"type": "plan", "content": "plan", "tool_choice": {"type": "function"}}
        yield {"type": "tool_calls", "tool_calls": calls}
    else:
        yield {"type": "final_answer", "content": "done"}


@pytest.mark.asyncio
async def test_google_docstring_example(monkeypatch):
    def calc(expression: str) -> int:
        """
        Evaluate a simple expression.
        Args:
            expression (str): A Python expression to evaluate.
        """
        return eval(expression)

    mgr = ManagerAgent({'id': 'mgr','usf_config': {'api_key': 'DUMMY','model': 'usf-mini'}})
    mgr.add_function_tool("calc", calc, alias="math_calc")

    tool_calls = [{"id": "1","type":"function","function":{"name":"math_calc","arguments": json.dumps({"expression":"2+3"})}}]
    monkeypatch.setattr(mgr.usf, "run", lambda msgs, opts=None: _fake_run_with_calls(msgs, tool_calls))
    final = await mgr.run_auto([{'role':'user','content':'Use math_calc to compute 2+3'}], mode='auto')
    assert final == "done"


@pytest.mark.asyncio
async def test_numpy_docstring_example(monkeypatch):
    def greet(name: str) -> str:
        """
        Greet a user.

        Parameters
        ----------
        name : str
            Person to greet.
        """
        return f"Hello {name}!"

    mgr = ManagerAgent({'id': 'mgr','usf_config': {'api_key': 'DUMMY','model': 'usf-mini'}})
    mgr.add_function_tool("greet", greet, alias="hello")

    calls = [{"id": "1","type":"function","function":{"name":"hello","arguments": json.dumps({"name":"USF"})}}]
    monkeypatch.setattr(mgr.usf, "run", lambda msgs, opts=None: _fake_run_with_calls(msgs, calls))
    final = await mgr.run_auto([{'role':'user','content':'Use hello for "USF"'}], mode='auto')
    assert final == "done"


@pytest.mark.asyncio
@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not installed")
async def test_yaml_docstring_example(monkeypatch):
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
        """
        return {"status": 200, "body": "ok"}

    mgr = ManagerAgent({'id':'mgr','usf_config': {'api_key': 'DUMMY','model':'usf-mini'}})
    mgr.add_function_tool("http_get", http_get)

    calls = [{"id": "1","type":"function","function":{"name":"http_get","arguments": json.dumps({"url":"https://example.com"})}}]
    monkeypatch.setattr(mgr.usf, "run", lambda msgs, opts=None: _fake_run_with_calls(msgs, calls))
    final = await mgr.run_auto([{'role':'user','content':'Call http_get with https://example.com'}], mode='auto')
    assert final == "done"


@pytest.mark.asyncio
async def test_decorator_defaults_example(monkeypatch):
    @tool(name="calc_sum", alias="sum_tool", description="Sum a list of integers")
    def calc_sum(numbers: list[int]) -> int:
        """
        Sum integers.
        Args:
            numbers (list[int]): Values to add up.
        """
        return sum(numbers)

    mgr = ManagerAgent({'id':'mgr','usf_config': {'api_key': 'DUMMY','model':'usf-mini'}})
    mgr.add_function_tool("calc_sum", calc_sum)

    calls = [{"id": "1","type":"function","function":{"name":"sum_tool","arguments": json.dumps({"numbers":[10,20,30]})}}]
    monkeypatch.setattr(mgr.usf, "run", lambda msgs, opts=None: _fake_run_with_calls(msgs, calls))
    final = await mgr.run_auto([{'role':'user','content':'Use sum_tool to sum 10,20,30'}], mode='auto')
    assert final == "done"


@pytest.mark.asyncio
async def test_decorator_schema_example(monkeypatch):
    @tool(
        name="calc_sum",
        alias="sum_tool",
        description="Sum a list of integers",
        schema={
            "description": "Sum integers",
            "parameters": {
                "type": "object",
                "properties": {"numbers": {"type": "array", "description": "List of ints"}},
                "required": ["numbers"]
            }
        }
    )
    def calc_sum(numbers: list[int]) -> int:
        return sum(numbers)

    mgr = ManagerAgent({'id':'mgr','usf_config': {'api_key': 'DUMMY','model':'usf-mini'}})
    mgr.add_function_tool("calc_sum", calc_sum)

    calls = [{"id": "1","type":"function","function":{"name":"sum_tool","arguments": json.dumps({"numbers":[1,2,3,4,5]})}}]
    monkeypatch.setattr(mgr.usf, "run", lambda msgs, opts=None: _fake_run_with_calls(msgs, calls))
    final = await mgr.run_auto([{'role':'user','content':'Use sum_tool to sum 1..5'}], mode='auto')
    assert final == "done"


@pytest.mark.asyncio
async def test_explicit_schema_add_function_tool_example(monkeypatch):
    def calc(expression: str) -> int:
        return eval(expression)

    mgr = ManagerAgent({'id':'mgr','usf_config': {'api_key': 'DUMMY','model':'usf-mini'}})
    mgr.add_function_tool(
        "calc",
        calc,
        alias="math_calc",
        schema={
            "description": "Evaluate math expression",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string", "description": "Python expression"}},
                "required": ["expression"]
            }
        },
        strict=False
    )

    calls = [{"id": "1","type":"function","function":{"name":"math_calc","arguments": json.dumps({"expression":"9*9"})}}]
    monkeypatch.setattr(mgr.usf, "run", lambda msgs, opts=None: _fake_run_with_calls(msgs, calls))
    final = await mgr.run_auto([{'role':'user','content':'Use math_calc to compute 9*9'}], mode='auto')
    assert final == "done"


@pytest.mark.asyncio
async def test_type_mapping_explicit_schema_strict_true(monkeypatch):
    def demo(a: str, n: int, flag: bool, cfg: dict, items: list) -> dict:
        return {"ok": True}

    mgr = ManagerAgent({'id':'mgr','usf_config': {'api_key': 'DUMMY','model':'usf-mini'}})
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
                    "items": {"type": "array", "description": "list of items"}
                },
                "required": ["a", "n", "flag", "cfg", "items"]
            }
        },
        strict=True
    )

    calls = [{"id":"1","type":"function","function":{"name":"demo","arguments": json.dumps({"a":"x","n":1,"flag":True,"cfg":{},"items":[]})}}]
    monkeypatch.setattr(mgr.usf, "run", lambda msgs, opts=None: _fake_run_with_calls(msgs, calls))
    final = await mgr.run_auto([{'role':'user','content':'Call demo with required fields'}], mode='auto')
    assert final == "done"


@pytest.mark.asyncio
async def test_multi_agent_add_sub_agent_simple_example(monkeypatch):
    mgr = ManagerAgent({'id':'mgr','name':'Manager','agent_type':'manager','usf_config': {'api_key':'DUMMY','model':'usf-mini'}})
    mgr.add_sub_agent_simple(id='writer', alias='agent_writer', context_mode='NONE', description='Draft short outputs')

    # Stub sub-agent execute to avoid deeper loops
    async def stub_exec(self, tool_call, calling_context, context_param=None, options=None):
        return {"success": True, "content": "ok", "error": None}

    monkeypatch.setattr(SubAgent, "execute_as_tool_until_final", stub_exec, raising=True)

    calls = [{"id":"1","type":"function","function":{"name":"agent_writer","arguments": "{}"}}]
    # Stub planner to request the agent tool
    monkeypatch.setattr(mgr.usf, "run", lambda msgs, opts=None: _fake_run_with_calls(msgs, calls))
    final = await mgr.run_auto([{'role':'user','content':'Ask agent_writer to write a haiku'}], mode='auto')
    assert final == "done"


@pytest.mark.asyncio
async def test_batch_add_sub_agents_example(monkeypatch):
    mgr = ManagerAgent({'id':'mgr','usf_config': {'api_key':'DUMMY','model':'usf-mini'}})
    mgr.add_sub_agents([
        {'id':'logs', 'alias':'agent_logs', 'context_mode':'AGENT_DECIDED', 'description':'Analyze logs'},
        {'id':'remediate', 'alias':'agent_remediate', 'context_mode':'CONTEXT_PARAM', 'description':'Suggest fixes'}
    ])

    async def stub_exec(self, tool_call, calling_context, context_param=None, options=None):
        return {"success": True, "content": "ok", "error": None}

    monkeypatch.setattr(SubAgent, "execute_as_tool_until_final", stub_exec, raising=True)

    calls = [{"id":"1","type":"function","function":{"name":"agent_logs","arguments": "{}"}}]
    monkeypatch.setattr(mgr.usf, "run", lambda msgs, opts=None: _fake_run_with_calls(msgs, calls))
    final = await mgr.run_auto([{'role':'user','content':'use agent_logs'}], mode='auto')
    assert final == "done"


@pytest.mark.asyncio
async def test_registry_option_example(monkeypatch):
    def calc(expression: str) -> int:
        return eval(expression)

    registry = ToolRegistry()
    registry.register_function(
        name='calc',
        func=calc,
        schema={'description':'calc','parameters':{'type':'object','properties':{'expression':{'type':'string'}},'required':['expression']}},
        examples=[{'name':'smoke','args':{'expression':'2+3'},'expect':5}]
    )

    class StubAgent:
        async def run(self, messages, options=None):
            has_results = any(m.get("role") == "tool" for m in messages)
            if not has_results:
                yield {"type": "plan", "content": "plan", "tool_choice": {"type": "function"}}
                yield {"type": "tool_calls", "tool_calls": [{"id":"1","type":"function","function":{"name":"calc","arguments": json.dumps({"expression":"25*4"})}}]}
            else:
                yield {"type": "final_answer", "content": "done"}

    agent = StubAgent()
    final = await run_auto(agent, [{'role':'user','content':'Use calc to compute 25*4'}], registry=registry, mode='auto')
    assert final == "done"
