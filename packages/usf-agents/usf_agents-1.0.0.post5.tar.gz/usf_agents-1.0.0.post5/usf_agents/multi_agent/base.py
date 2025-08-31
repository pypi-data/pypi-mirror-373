import json
import inspect
from typing import List, Dict, Any, Optional, AsyncGenerator, Union, Callable

from ..usfAgent import USFAgent
from ..types import Message, RunOptions, AgentResult, Tool, ToolCall
from ..types.multi_agent import (
    AgentId,
    AgentSpec,
    ContextMode,
    TaskPayload,
    ToolCallExecutionResult,
)
from .context import shape_context_for_mode, to_openai_messages_from_task, sanitize_parent_context
from ..trace.trace import record_event, AutoTrace, TraceRecorder


def _collect_final_answer(agent: USFAgent, messages: List[Message], options: Optional[RunOptions] = None) -> Dict[str, Any]:
    """
    Helper to run the USFAgent and collect either final_answer or first tool_calls requirement.
    Returns:
      {
        'status': 'final' | 'tool_calls' | 'error',
        'content': Optional[str],
        'tool_calls': Optional[List[Dict[str, Any]]],
        'raw_chunks': List[Dict[str, Any]]  # plan/tool_calls/final chunks as yielded
      }
    """
    # The run() is async generator; we need to consume it synchronously from async context
    # This helper is intended to be awaited by wrapper methods.
    raise RuntimeError("This helper must be awaited via _acollect_final_answer")


async def _acollect_final_answer(agent: USFAgent, messages: List[Message], options: Optional[RunOptions] = None) -> Dict[str, Any]:
    raw_chunks: List[Dict[str, Any]] = []
    async for chunk in agent.run(messages, options or {}):
        raw_chunks.append(chunk)
        if chunk.get('type') == 'tool_calls':
            return {
                'status': 'tool_calls',
                'content': None,
                'tool_calls': chunk.get('tool_calls'),
                'raw_chunks': raw_chunks
            }
        if chunk.get('type') == 'final_answer':
            return {
                'status': 'final',
                'content': chunk.get('content', ''),
                'tool_calls': None,
                'raw_chunks': raw_chunks
            }
    # If nothing decisive was returned
    return {
        'status': 'error',
        'content': None,
        'tool_calls': None,
        'raw_chunks': raw_chunks
    }


def _merge_tools(existing: Optional[List[Tool]], extra: Optional[List[Tool]]) -> List[Tool]:
    """
    Merge two tool lists, de-duplicating by function.name when available.
    """
    existing = list(existing or [])
    extra = list(extra or [])
    seen = set()
    merged: List[Tool] = []

    def name_of(t: Tool) -> str:
        if isinstance(t, dict):
            fn = (t.get('function') or {}).get('name')
            if fn:
                return fn
        # Fallback: stable string key
        try:
            return json.dumps(t, sort_keys=True)
        except Exception:
            return str(t)

    for t in existing + extra:
        key = name_of(t)
        if key not in seen:
            seen.add(key)
            merged.append(t)
    return merged


class BaseAgentWrapper:
    """
    Composition wrapper over USFAgent that enforces isolation and provides
    unified entry points for message-based and task-based execution.
    """

    def __init__(self, spec: AgentSpec):
        if not spec or not isinstance(spec, dict):
            raise Exception("BaseAgentWrapper Error: spec is required")

        self.id: AgentId = spec.get('id') or ''
        self.name: str = spec.get('name') or self.id or 'agent'
        self.agent_type: str = spec.get('agent_type', 'generic')
        self.description: str = spec.get('description', '') or ''
        self.backstory: str = spec.get('backstory', '') or ''
        self.goal: str = spec.get('goal', '') or ''
        self.context_mode: ContextMode = spec.get('context_mode', 'NONE')  # default policy for sub usage

        usf_config = spec.get('usf_config') or {}
        # Ensure backstory/goal are present in agent config for consistent behavior
        usf_config = {
            **usf_config,
            'backstory': self.backstory,
            'goal': self.goal,
        }

        # Keep a copy for convenience (used by manager sugar to spawn sub-agents)
        self._usf_config = usf_config

        # Memory is isolated per wrapper by virtue of distinct USFAgent instance.
        self.usf = USFAgent(usf_config)

        # Allow manager/generic agents to have native tools (not sub-agents as tools)
        self._native_tools: List[Tool] = spec.get('tools', []) or []
        # Optional sub-agent entries (any agent can aggregate sub-agents)
        self._sub_entries: List[Dict[str, Any]] = []  # [{'sub': BaseAgentWrapper, 'schema': Dict, 'alias': Optional[str]}]

    async def run_messages(self, messages: List[Message], options: Optional[RunOptions] = None) -> AsyncGenerator[AgentResult, None]:
        """
        Direct entry for message-based usage (main entry points).
        Yields the underlying USFAgent chunks unmodified.
        """
        opts: RunOptions = dict(options or {})
        comp_tools = self._compose_tools()
        if comp_tools:
            opts['tools'] = _merge_tools(opts.get('tools'), comp_tools)

        async for chunk in self.usf.run(messages, opts):
            yield chunk  # pass-through preserving structure

    async def run_task(
        self,
        task: TaskPayload,
        calling_agent_msgs: Optional[List[Message]] = None,
        context_param: Optional[Dict[str, Any]] = None,
        options: Optional[RunOptions] = None,
        trace: bool = False
    ) -> Any:
        """
        Task-based entry (used for agent-as-tool flows or programmatic invocations).
        Shapes messages using current context_mode policy and executes the USFAgent.
        Returns a dict with either final content or a tool_calls request.
        """
        # Build messages based on this agent's default policy
        shaped_messages = shape_context_for_mode(
            self.context_mode,
            task,
            calling_agent_msgs=calling_agent_msgs,
            context_param=context_param
        )
        opts: RunOptions = dict(options or {})
        comp_tools = self._compose_tools()
        if comp_tools:
            opts['tools'] = _merge_tools(opts.get('tools'), comp_tools)

        # Optional: enable per-call tracing
        _trace_flag = bool(trace)
        _rec_cm = None
        _rec_inst = None
        if _trace_flag:
            try:
                _rec_cm = AutoTrace(TraceRecorder())
                _rec_inst = _rec_cm.__enter__()
            except Exception:
                _rec_cm = None
                _rec_inst = None

        # Trace: start of agent task (no-op when tracing disabled)
        try:
            record_event({
                'kind': 'message',
                'agent_id': self.id,
                'node_id': self.id,
                'input': {'task': (task or {}).get('task'), 'metadata': (task or {}).get('metadata')},
            })
        except Exception:
            pass

        result = await _acollect_final_answer(self.usf, shaped_messages, opts)

        # Trace: summarize outcome
        try:
            status = result.get('status')
            if status == 'final':
                record_event({
                    'kind': 'final',
                    'agent_id': self.id,
                    'node_id': self.id,
                    'output': result.get('content', '')
                })
            elif status == 'tool_calls':
                record_event({
                    'kind': 'tool_call',
                    'agent_id': self.id,
                    'node_id': self.id,
                    'input': result.get('tool_calls', [])
                })
        except Exception:
            pass

        # Ensure per-call tracer (if any) is closed
        if _rec_cm is not None:
            try:
                _rec_cm.__exit__(None, None, None)
            except Exception:
                pass

        if _trace_flag and _rec_inst is not None:
            return result, _rec_inst.snapshot()
        return result

    def get_public_tool(self) -> Optional[Tool]:
        """
        Default: no direct public tool surface. Subclasses may override.
        """
        return None

    def list_native_tools(self) -> List[Tool]:
        """
        Native external tools configured for this agent (excludes sub-agents).
        """
        return list(self._native_tools)

    @staticmethod
    def _merge_usf_config(base: Dict[str, Any], overrides: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Shallow-merge base USF config with overrides, deep-merging stage keys:
        planning, tool_calling, final_response.
        """
        if not overrides:
            return dict(base or {})
        merged: Dict[str, Any] = dict(base or {})
        for key, val in (overrides or {}).items():
            if key in ('planning', 'tool_calling', 'final_response'):
                base_stage = dict((merged.get(key) or {})) if isinstance(merged.get(key), dict) else {}
                if isinstance(val, dict):
                    base_stage.update(val)
                    merged[key] = base_stage
                else:
                    merged[key] = val
            else:
                merged[key] = val
        return merged

    def _compose_tools(self) -> List[Tool]:
        """
        Compose this agent's native tools + each registered sub-agent as a tool (agent-as-tool adapter).
        """
        tools: List[Tool] = []
        # Native tools first
        tools.extend(self.list_native_tools())

        # Avoid import cycle by importing adapter lazily
        try:
            from .adapter import make_agent_tool
        except Exception:
            make_agent_tool = None  # type: ignore

        for entry in self._sub_entries:
            sub = entry['sub']
            schema = entry.get('schema') or {}
            alias = entry.get('alias')
            if make_agent_tool:
                tools.append(make_agent_tool(sub, schema, alias=alias))
            else:
                # Fallback to sub's own public tool surface if available
                try:
                    tools.append(sub.get_public_tool(schema, alias=alias))  # type: ignore[attr-defined]
                except Exception:
                    tools.append({
                        'type': 'function',
                        'function': {
                            'name': alias or f"agent_{getattr(sub, 'id', 'sub')}",
                            'description': (getattr(sub, 'description', '') or f"Invoke sub-agent {getattr(sub, 'name', 'agent')} ({getattr(sub, 'id', '')})"),
                            'parameters': {
                                'type': 'object',
                                'properties': {
                                    'task': {'type': 'string'},
                                    'additional_context': {'type': 'object'}
                                },
                                'required': ['task']
                            }
                        }
                    })

        # Validate unique function names within this agent's composed tool surface
        names: List[str] = []
        for t in tools:
            try:
                fn = (t.get('function') or {}).get('name')  # type: ignore[attr-defined]
            except Exception:
                fn = None
            if fn:
                names.append(fn)
        dupes = sorted({n for n in names if names.count(n) > 1})
        if dupes:
            raise Exception(f"Tool Name Collision: duplicate tool names in agent '{self.id}': {dupes}")

        # Deduplicate by name for stability
        return _merge_tools([], tools)

    def add_sub_agent(self, sub: 'BaseAgentWrapper', tool_schema: Dict[str, Any], alias: Optional[str] = None) -> None:
        """
        Register a sub-agent with an associated tool schema. Available on any agent.
        """
        self._sub_entries.append({'sub': sub, 'schema': tool_schema or {}, 'alias': alias})

    def list_tools(self) -> List[Tool]:
        """
        Expose composed tools (native + sub-agents).
        """
        return self._compose_tools()


class SubAgent(BaseAgentWrapper):
    """
    SubAgent that can expose a tool surface for managers (agent-as-tool),
    while keeping its internals (tools, memory) fully private.
    """

    def get_public_tool(self, schema: Dict[str, Any], alias: Optional[str] = None) -> Tool:
        """
        Provide a callable OpenAI tool definition for this SubAgent. This is a light adapter;
        a richer AgentToolAdapter is provided in the adapter module.
        """
        tool_name = alias or f"agent_{self.id}"
        # Minimal tool schema; developers can pass richer JSON schema via `schema`.
        desc = schema.get('description') or (self.description if getattr(self, 'description', '') else None)
        if not desc:
            raise ValueError(f"SubAgent '{self.id}' must define a description for tool selection.")
        return {
            'type': 'function',
            'function': {
                'name': tool_name,
                'description': desc,
                'parameters': schema.get('parameters', {
                    'type': 'object',
                    'properties': {
                        'task': {'type': 'string', 'description': 'Task name/description'},
                        'additional_context': {'type': 'object', 'description': 'Lightweight context object'}
                    },
                    'required': ['task']
                })
            },
            # metadata to distinguish agent tools at runtime (ignored by OpenAI schema)
            'x_kind': 'agent',
            'x_agent_id': self.id,
            'x_alias': alias
        }

    async def execute_as_tool(
        self,
        tool_call: ToolCall,
        calling_context: Optional[List[Message]],
        context_param: Optional[Dict[str, Any]] = None,
        options: Optional[RunOptions] = None
    ) -> ToolCallExecutionResult:
        """
        Execute the sub-agent when invoked as a tool. Parses ToolCall arguments into TaskPayload,
        shapes context per this agent's context_mode, and returns a normalized tool result.
        """
        try:
            func = tool_call.get('function') or {}
            tool_name = func.get('name') or f"agent_{self.id}"
            raw_args = func.get('arguments') or '{}'
            try:
                args = json.loads(raw_args)
            except Exception:
                # Accept non-JSON args gracefully
                args = {'task': str(raw_args)}

            task: TaskPayload = {
                'task': args.get('task') or 'task',
                'input': {},
                'metadata': args.get('metadata') or {}
            }
            # Allow explicit context_param override at call-time (mapped from additional_context in public schema)
            call_context_param = context_param if context_param is not None else args.get('additional_context')

            clean_context = sanitize_parent_context(calling_context)
            shaped_messages = shape_context_for_mode(
                self.context_mode,
                task,
                calling_agent_msgs=clean_context,
                context_param=call_context_param
            )

            opts: RunOptions = dict(options or {})
            comp_tools = self._compose_tools()
            if comp_tools:
                opts['tools'] = _merge_tools(opts.get('tools'), comp_tools)

            # Trace: tool call (sub-agent as tool)
            try:
                record_event({
                    'kind': 'tool_call',
                    'agent_id': self.id,
                    'node_id': self.id,
                    'input': {'tool': tool_name}
                })
            except Exception:
                pass

            collected = await _acollect_final_answer(self.usf, shaped_messages, opts)

            # Trace: tool result / outcome
            try:
                if collected.get('status') == 'final':
                    record_event({
                        'kind': 'tool_result',
                        'agent_id': self.id,
                        'node_id': self.id,
                        'output': {'tool': tool_name, 'content': collected.get('content', '')}
                    })
                elif collected.get('status') == 'tool_calls':
                    record_event({
                        'kind': 'tool_result',
                        'agent_id': self.id,
                        'node_id': self.id,
                        'output': {'tool': tool_name, 'pending': True}
                    })
                else:
                    record_event({
                        'kind': 'error',
                        'agent_id': self.id,
                        'node_id': self.id,
                        'error': f"execute_as_tool produced no final content for {tool_name}"
                    })
            except Exception:
                pass

            if collected['status'] == 'final':
                return {
                    'success': True,
                    'content': collected.get('content') or '',
                    'error': None,
                    'tool_name': tool_name,
                    'raw': collected
                }
            if collected['status'] == 'tool_calls':
                # The sub-agent requested tools; return as not-final so the caller can handle execution
                return {
                    'success': False,
                    'content': '',
                    'error': 'Sub-agent requested tool_calls; external execution required.',
                    'tool_name': tool_name,
                    'raw': collected
                }
            return {
                'success': False,
                'content': '',
                'error': 'Sub-agent returned no final content.',
                'tool_name': tool_name,
                'raw': collected
            }
        except Exception as e:
            return {
                'success': False,
                'content': '',
                'error': f'execute_as_tool error: {e}',
                'tool_name': tool_call.get('function', {}).get('name', f"agent_{self.id}"),
                'raw': None
            }


    async def execute_as_tool_until_final(
        self,
        tool_call: ToolCall,
        calling_context: Optional[List[Message]],
        context_param: Optional[Dict[str, Any]] = None,
        options: Optional[RunOptions] = None
    ) -> ToolCallExecutionResult:
        """
        Execute the sub-agent as a tool and internally drive its tool loop until a final answer.
        Returns a normalized tool result with success=True and final content.
        """
        try:
            func = tool_call.get('function') or {}
            tool_name = func.get('name') or f"agent_{self.id}"
            raw_args = func.get('arguments') or '{}'
            try:
                args = json.loads(raw_args)
            except Exception:
                args = {'task': str(raw_args)}

            task: TaskPayload = {
                'task': args.get('task') or 'task',
                'input': {},
                'metadata': args.get('metadata') or {}
            }
            call_context_param = context_param if context_param is not None else args.get('additional_context')

            clean_context = sanitize_parent_context(calling_context)
            shaped_messages = shape_context_for_mode(
                self.context_mode,
                task,
                calling_agent_msgs=clean_context,
                context_param=call_context_param
            )

            # Compose tools available to this sub-agent (native + nested sub-agents)
            comp_tools = self._compose_tools()

            # Lazy import to avoid cycles
            from ..runtime.safe_seq import run_until_final

            # Default router: acknowledge tool execution; in real setups users provide executors
            async def _router(tc: ToolCall, current_msgs: List[Message]) -> Dict[str, Any]:
                fname = (tc.get('function') or {}).get('name')
                return {'success': True, 'content': f"{fname} executed"}

            # Trace: tool call (until final)
            try:
                record_event({
                    'kind': 'tool_call',
                    'agent_id': self.id,
                    'node_id': self.id,
                    'input': {'tool': tool_name, 'mode': 'until_final'}
                })
            except Exception:
                pass

            content = await run_until_final(
                self.usf,
                shaped_messages,
                comp_tools,
                _router,
                max_loops=(options or {}).get('max_loops', 20) if isinstance(options, dict) else 20
            )

            # Trace: tool result (final)
            try:
                record_event({
                    'kind': 'tool_result',
                    'agent_id': self.id,
                    'node_id': self.id,
                    'output': {'tool': tool_name, 'content': content}
                })
            except Exception:
                pass

            return {
                'success': True,
                'content': content or '',
                'error': None,
                'tool_name': tool_name,
                'raw': {'status': 'final', 'content': content}
            }
        except Exception as e:
            return {
                'success': False,
                'content': '',
                'error': f'execute_as_tool_until_final error: {e}',
                'tool_name': tool_call.get('function', {}).get('name', f"agent_{self.id}"),
                'raw': None
            }

class ManagerAgent(BaseAgentWrapper):
    """
    ManagerAgent that can aggregate native tools and sub-agents (as tools).
    This base implementation avoids hard dependency on adapter/registry modules to prevent cycles.
    """

    def __init__(self, spec: AgentSpec):
        super().__init__(spec)
        # Track sub-agents and their tool schemas for later tool list composition
        self._sub_entries: List[Dict[str, Any]] = []  # [{'sub': SubAgent, 'schema': Dict, 'alias': Optional[str]}]

        # Internal registry for custom function tools (sugar API)
        try:
            from ..runtime.tool_registry import ToolRegistry
            self._registry = ToolRegistry()
        except Exception:
            self._registry = None  # lazy-init fallback

    def _compose_tools(self) -> List[Tool]:
        """
        Compose manager's native tools + each sub-agent as a tool (agent-as-tool adapter).
        """
        tools: List[Tool] = []
        # Native tools first
        tools.extend(self.list_native_tools())

        # Avoid import cycle by importing adapter lazily
        try:
            from .adapter import make_agent_tool
        except Exception:
            make_agent_tool = None  # type: ignore

        for entry in self._sub_entries:
            sub = entry['sub']
            schema = entry.get('schema') or {}
            alias = entry.get('alias')
            if make_agent_tool:
                tools.append(make_agent_tool(sub, schema, alias=alias))
            else:
                # Fallback to sub's own public tool surface
                try:
                    tools.append(sub.get_public_tool(schema, alias=alias))
                except Exception:
                    tools.append({
                        'type': 'function',
                        'function': {
                            'name': alias or f"agent_{getattr(sub, 'id', 'sub')}",
                            'description': (getattr(sub, 'description', '') or f"Invoke sub-agent {getattr(sub, 'name', 'agent')} ({getattr(sub, 'id', '')})"),
                            'parameters': {
                                'type': 'object',
                                'properties': {
                                    'task': {'type': 'string'},
                                    'additional_context': {'type': 'object'}
                                },
                                'required': ['task']
                            }
                        }
                    })

        # Validate unique function names within this manager's composed tool surface
        names: List[str] = []
        for t in tools:
            try:
                fn = (t.get('function') or {}).get('name')  # type: ignore[attr-defined]
            except Exception:
                fn = None
            if fn:
                names.append(fn)
        dupes = sorted({n for n in names if names.count(n) > 1})
        if dupes:
            raise Exception(f"Tool Name Collision: duplicate tool names in manager '{self.id}': {dupes}")

        # Deduplicate by name for stability
        return _merge_tools([], tools)

    async def run_messages(self, messages: List[Message], options: Optional[RunOptions] = None) -> AsyncGenerator[AgentResult, None]:
        """
        Override to ensure the manager's USFAgent has access to native tools + sub-agent tools.
        """
        opts: RunOptions = dict(options or {})
        comp_tools = self._compose_tools()
        if comp_tools:
            opts['tools'] = _merge_tools(opts.get('tools'), comp_tools)

        async for chunk in self.usf.run(messages, opts):
            yield chunk

    async def run_task(
        self,
        task: TaskPayload,
        calling_agent_msgs: Optional[List[Message]] = None,
        context_param: Optional[Dict[str, Any]] = None,
        options: Optional[RunOptions] = None,
        trace: bool = False
    ) -> Any:
        """
        Override to attach manager's tool surface (native + sub-agents) to USFAgent execution.
        """
        shaped_messages = shape_context_for_mode(
            self.context_mode,
            task,
            calling_agent_msgs=calling_agent_msgs,
            context_param=context_param
        )
        opts: RunOptions = dict(options or {})
        comp_tools = self._compose_tools()
        if comp_tools:
            opts['tools'] = _merge_tools(opts.get('tools'), comp_tools)

        # Optional: enable per-call tracing
        _trace_flag = bool(trace)
        _rec_cm = None
        _rec_inst = None
        if _trace_flag:
            try:
                _rec_cm = AutoTrace(TraceRecorder())
                _rec_inst = _rec_cm.__enter__()
            except Exception:
                _rec_cm = None
                _rec_inst = None

        result = await _acollect_final_answer(self.usf, shaped_messages, opts)

        # Ensure per-call tracer (if any) is closed
        if _rec_cm is not None:
            try:
                _rec_cm.__exit__(None, None, None)
            except Exception:
                pass

        if _trace_flag and _rec_inst is not None:
            return result, _rec_inst.snapshot()
        return result

    def add_sub_agent(self, sub: BaseAgentWrapper, tool_schema: Dict[str, Any], alias: Optional[str] = None) -> None:
        """
        Register a sub-agent with an associated tool schema. Tool definition will be generated
        dynamically in list_tools to avoid circular imports with adapter.
        """
        self._sub_entries.append({'sub': sub, 'schema': tool_schema or {}, 'alias': alias})

    def list_tools(self) -> List[Tool]:
        """
        Expose manager's native tools + sub-agents as tools.
        """
        return self._compose_tools()

    # ========== Sugar APIs for simpler developer UX ==========

    @staticmethod
    def _validate_schema_matches_signature(func: Any, schema: Dict[str, Any], strict: bool = False) -> None:
        """
        Validate that schema 'required' exactly matches non-default parameters in the Python signature.
        When strict=True, also require that schema.properties keys equal the set of signature parameters
        (excluding *args/**kwargs).
        """
        try:
            sig = inspect.signature(func)
        except Exception:
            raise Exception("Schema Validation Error: unable to read function signature")

        # Collect function parameter names, excluding *args / **kwargs
        sig_params: List[str] = []
        required_sig: List[str] = []
        for pname, param in sig.parameters.items():
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            sig_params.append(pname)
            if param.default is inspect._empty:
                required_sig.append(pname)

        parameters = (schema or {}).get('parameters') or {}
        props = (parameters or {}).get('properties') or {}
        req = (parameters or {}).get('required') or []

        if not isinstance(props, dict):
            raise Exception("Schema Validation Error: parameters.properties must be an object")
        if not isinstance(req, list):
            raise Exception("Schema Validation Error: parameters.required must be a list")

        schema_props = list(props.keys())
        schema_req = [str(x) for x in req]

        # Required must match exactly
        missing_required = [p for p in required_sig if p not in schema_req]
        extra_required = [p for p in schema_req if p not in required_sig]
        if missing_required or extra_required:
            raise Exception(f"Schema Validation Error: required mismatch. Missing in schema: {missing_required}; Extra in schema: {extra_required}")

        if strict:
            missing_props = [p for p in sig_params if p not in schema_props]
            extra_props = [p for p in schema_props if p not in sig_params]
            if missing_props or extra_props:
                raise Exception(f"Schema Validation Error (strict properties): properties mismatch. Missing in schema: {missing_props}; Extra in schema: {extra_props}")

    @staticmethod
    def _infer_schema_from_func(func: Any, name: str, strict: bool = False) -> Dict[str, Any]:
        """
        Docstring-first schema inference.
        - If a YAML code block or Google/NumPy-style docstring is present, parse it.
        - Enforce required-parameter equality; if strict=True, enforce properties equality too.
        - Raise a clear error if neither explicit schema nor parseable docstring is available.
        """
        try:
            from ..runtime.docstring_schema import parse_docstring_to_schema  # local import to avoid cycles
        except Exception as e:
            raise Exception(f"Schema Inference Error: unable to import docstring parser: {e}")

        schema = None
        try:
            schema = parse_docstring_to_schema(func)
        except Exception as e:
            # Parser errors are non-fatal here; we will raise a unified error below if schema stays None
            schema = None

        if not schema:
            raise Exception(f"Tool Registration Error: no explicit schema and no parseable docstring for function '{name}'. Provide a JSON schema or a Google/NumPy-style docstring (YAML block takes precedence).")

        # Validate against signature
        ManagerAgent._validate_schema_matches_signature(func, schema, strict=strict)

        # Ensure description fallback
        if not schema.get('description'):
            schema['description'] = getattr(func, '__doc__', None) or f'Custom tool {name}'
        return schema

    def add_function_tool(
        self,
        name: str,
        func: Any,
        alias: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        examples: Optional[List[Dict[str, Any]]] = None,
        strict: bool = False
    ) -> None:
        """
        Register a Python function as a custom tool on this manager.
        - If schema is provided, enforce required-parameter equality (and properties equality when strict=True).
        - Otherwise, parse the function docstring (YAML block precedence, then Google/NumPy) to build schema and validate.
        - Enforced per-agent uniqueness at composition time (collisions raise).
        - Reads @tool decorator defaults for alias/description if explicit args not provided.
        """
        if self._registry is None:
            from ..runtime.tool_registry import ToolRegistry
            self._registry = ToolRegistry()

        # Read decorator metadata (if any)
        meta = getattr(func, "__usf_tool__", {}) if hasattr(func, "__usf_tool__") else {}
        # Apply defaults when not explicitly provided
        alias = alias or meta.get("alias")
        meta_desc = meta.get("description")

        if schema is not None:
            # If description missing in provided schema, use decorator description or function docstring
            if isinstance(schema, dict) and not schema.get("description"):
                schema["description"] = meta_desc or getattr(func, "__doc__", None) or f"Custom tool {name}"
            # Validate provided schema against function signature
            ManagerAgent._validate_schema_matches_signature(func, schema, strict=strict)
            final_schema = schema
        else:
            # Precedence: decorator-provided schema -> docstring parsing
            meta_schema = meta.get("schema") if isinstance(meta, dict) else None
            if isinstance(meta_schema, dict):
                # Fill missing description from decorator or docstring
                if not meta_schema.get("description"):
                    meta_schema["description"] = meta_desc or getattr(func, "__doc__", None) or f"Custom tool {name}"
                # Validate decorator-provided schema
                ManagerAgent._validate_schema_matches_signature(func, meta_schema, strict=strict)
                final_schema = meta_schema
            else:
                # Infer from docstring (and validate)
                final_schema = self._infer_schema_from_func(func, name, strict=strict)
                # Allow decorator description to override docstring-derived description if provided
                if meta_desc:
                    final_schema["description"] = meta_desc

        tool = self._registry.register_function(name=name, func=func, schema=final_schema, alias=alias, examples=examples)
        # Add to native tools so list_tools() exposes it without additional wiring
        self._native_tools.append(tool)  # type: ignore[arg-type]

    def add_sub_agent_simple(
        self,
        id: str,
        name: Optional[str] = None,
        context_mode: str = 'NONE',
        alias: Optional[str] = None,
        description: Optional[str] = None,
        usf_overrides: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Quickly construct a SubAgent using this manager's USF config and attach it as a tool.
        You can override the sub-agent's USF config (including final_response controls) via usf_overrides.
        Example:
            usf_overrides = {
              "final_response": {
                "final_instruction_mode": "append",
                "final_instruction_append": "Use bullets for steps."
              }
            }
        """
        # Merge manager's config with per-sub overrides (deep-merge for stage keys)
        merged_usf = self._merge_usf_config((self._usf_config or {}), usf_overrides)

        # Do not inherit skip_planning_if_no_tools from manager unless explicitly provided in usf_overrides
        overrides = usf_overrides or {}
        if overrides.get('skip_planning_if_no_tools') is None:
            # Remove top-level inherited flag
            merged_usf.pop('skip_planning_if_no_tools', None)
        # Also avoid inheriting planning-stage flag unless explicitly provided in overrides.planning
        if isinstance(merged_usf.get('planning'), dict):
            planning_overrides = overrides.get('planning') if isinstance(overrides.get('planning'), dict) else None
            if not (planning_overrides and (planning_overrides.get('skip_planning_if_no_tools') is not None)):
                merged_usf['planning'].pop('skip_planning_if_no_tools', None)

        sub = SubAgent({
            'id': id,
            'name': name or id,
            'agent_type': 'sub',
            'context_mode': context_mode,
            'usf_config': merged_usf
        })
        if not (description and str(description).strip()):
            raise ValueError(f"add_sub_agent_simple Error: description is required for SubAgent '{id}'")
        tool_schema = {
            'description': description,
            'parameters': {
                'type': 'object',
                'properties': {
                    'task': {'type': 'string'},
                    'additional_context': {'type': 'object'}
                },
                'required': ['task']
            }
        }
        self.add_sub_agent(sub, tool_schema, alias=alias)

    def add_sub_agents(self, *items: Any) -> None:
        """
        Batch add sub-agents with production-ready structure.

        Accepts:
        - SubAgent instances (recommended for production)
            mgr.add_sub_agents(calculator, researcher)
            mgr.add_sub_agents([calculator, researcher, coder, writer])
        - Dict specs (backward compatible quick form)
            mgr.add_sub_agents([{'id':'logs', 'alias':'agent_logs', 'context_mode':'AGENT_DECIDED', 'description':'Analyze logs'}, ...])

        For SubAgent instances, a minimal default tool schema is supplied (task/input/context_param).
        """
        # Normalize varargs and list inputs into a flat list
        flat: List[Any] = []
        for it in items or []:
            if isinstance(it, (list, tuple)):
                flat.extend(list(it))
            else:
                flat.append(it)

        for it in flat:
            # SubAgent or BaseAgentWrapper instance path
            if isinstance(it, BaseAgentWrapper):
                sub: BaseAgentWrapper = it
                # Require explicit description on SubAgent instances
                desc = (getattr(sub, 'description', '') or '')
                if not desc.strip():
                    raise ValueError(f"add_sub_agents Error: SubAgent '{getattr(sub, 'id', 'sub')}' requires a description (spec['description']).")
                # Default minimal tool schema; align with add_sub_agent_simple() parameters
                tool_schema = {
                    'description': desc,
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'task': {'type': 'string'},
                            'additional_context': {'type': 'object'}
                        },
                        'required': ['task']
                    }
                }
                self.add_sub_agent(sub, tool_schema, alias=None)
            # Dict spec path (backward compatible)
            elif isinstance(it, dict):
                self.add_sub_agent_simple(
                    id=it.get('id'),
                    name=it.get('name'),
                    context_mode=it.get('context_mode', 'NONE'),
                    alias=it.get('alias'),
                    description=it.get('description'),
                    usf_overrides=it.get('usf_overrides')
                )
            else:
                raise Exception(f"add_sub_agents Error: unsupported item type {type(it)}; expected SubAgent/BaseAgentWrapper or dict spec.")

    def add_function_tools(self, functions: List[Callable[..., Any]], *, strict: bool = False) -> None:
        """
        Batch register Python functions as custom tools on this manager.

        Naming and defaults:
        - Tool name defaults to decorator meta['name'] if present; otherwise function.__name__.
        - Alias defaults to decorator meta['alias'] if present.
        - Description is taken from provided schema (if any), else decorator meta['description'], else docstring summary.

        Strictness:
        - Enforces required-parameter equality always.
        - If strict=True, also enforces properties set equality with the function signature.
        """
        for func in functions or []:
            if not callable(func):
                raise Exception("add_function_tools Error: all items must be callables")
            meta = getattr(func, "__usf_tool__", {}) if hasattr(func, "__usf_tool__") else {}
            tool_name = meta.get("name") or getattr(func, "__name__", None)
            if not tool_name or not isinstance(tool_name, str):
                raise Exception("add_function_tools Error: unable to determine tool name (use @tool(name=...) or set __name__)")
            alias = meta.get("alias")
            # Delegate to single add_function_tool path (docstring parsing and validation happen there)
            self.add_function_tool(tool_name, func, alias=alias, schema=None, examples=None, strict=strict)

    def add_function_tools_from_module(
        self,
        module: Any,
        *,
        filter: Optional[Callable[[Callable[..., Any]], bool]] = None,
        strict: bool = False
    ) -> None:
        """
        Discover and batch add functions from a module.

        Selection:
        - Candidate functions are callables whose __module__ equals module.__name__.
        - If a filter callable is provided, it's applied to candidates.
        - Each candidate is registered via add_function_tool using:
            name = __usf_tool__['name'] if present else function.__name__
            alias = __usf_tool__['alias'] if present
        - Functions without parseable docstrings and without explicit schema will raise (by design).
        """
        if module is None or not hasattr(module, "__name__"):
            raise Exception("add_function_tools_from_module Error: invalid module")

        candidates: List[Callable[..., Any]] = []
        for attr in dir(module):
            obj = getattr(module, attr)
            # Include any callable attached to the module, regardless of obj.__module__
            # (helps with dynamically attached functions in tests or REPL).
            if callable(obj):
                candidates.append(obj)

        if filter:
            candidates = [fn for fn in candidates if filter(fn)]

        if not candidates:
            return

        for func in candidates:
            meta = getattr(func, "__usf_tool__", {}) if hasattr(func, "__usf_tool__") else {}
            tool_name = meta.get("name") or getattr(func, "__name__", None)
            if not tool_name or not isinstance(tool_name, str):
                raise Exception(f"add_function_tools_from_module Error: unable to determine tool name for '{func}' (use @tool(name=...))")
            alias = meta.get("alias")
            self.add_function_tool(tool_name, func, alias=alias, schema=None, examples=None, strict=strict)

    async def run_auto(self, messages: List[Message], mode: str = 'auto', max_loops: int = 20) -> Any:
        """
        One-call auto execution using the composed tools (native + sub-agents).
        Custom tools are dispatched via the internal registry router.
        """
        from ..runtime.auto_exec import run_with_auto_execution
        # Ensure registry exists even if no custom tools are present
        if self._registry is None:
            from ..runtime.tool_registry import ToolRegistry
            self._registry = ToolRegistry()

        tools = self.list_tools()
        router = self._registry.router() if self._registry else (lambda *args, **kwargs: {'success': False, 'error': 'no router'})
        return await run_with_auto_execution(self.usf, messages, tools, router, mode=mode, max_loops=max_loops)

    async def delegate(
        self,
        sub_id: AgentId,
        task: TaskPayload,
        policy: Union[ContextMode, str] = 'inherit_manager_policy',
        context_param: Optional[Dict[str, Any]] = None,
        calling_context: Optional[List[Message]] = None,
        options: Optional[RunOptions] = None
    ) -> ToolCallExecutionResult:
        """
        Delegate a TaskPayload to a registered sub-agent with a specific policy.
        If policy == 'inherit_manager_policy', uses sub.context_mode.
        Otherwise, uses the provided ContextMode value.
        """
        # Find sub-agent
        target: Optional[BaseAgentWrapper] = None
        for entry in self._sub_entries:
            if entry['sub'].id == sub_id:
                target = entry['sub']
                break

        if not target:
            return {
                'success': False,
                'content': '',
                'error': f'Sub-agent {sub_id} not found',
                'tool_name': f'agent:{sub_id}',
                'raw': None
            }

        # Determine mode
        if isinstance(policy, str) and policy == 'inherit_manager_policy':
            mode: ContextMode = target.context_mode
        else:
            mode = policy  # type: ignore

        clean_context = sanitize_parent_context(calling_context)
        shaped_messages = shape_context_for_mode(
            mode,
            task,
            calling_agent_msgs=clean_context,
            context_param=context_param
        )

        opts: RunOptions = dict(options or {})
        # Allow delegated-to agent to use its composed tools (native + its sub-agents)
        try:
            target_tools = target.list_tools()
        except Exception:
            target_tools = target.list_native_tools()
        if target_tools:
            opts['tools'] = _merge_tools(opts.get('tools'), target_tools)

        # Trace: delegation start
        try:
            record_event({
                'kind': 'delegate',
                'agent_id': self.id,
                'node_id': self.id,
                'input': {'to': sub_id, 'task': (task or {}).get('task')}
            })
        except Exception:
            pass

        collected = await _acollect_final_answer(target.usf, shaped_messages, opts)

        # Trace: delegation outcome (final/error/tool_calls)
        try:
            if collected.get('status') == 'final':
                record_event({
                    'kind': 'final',
                    'agent_id': sub_id,
                    'node_id': sub_id,
                    'output': collected.get('content', '')
                })
            elif collected.get('status') == 'tool_calls':
                record_event({
                    'kind': 'tool_call',
                    'agent_id': sub_id,
                    'node_id': sub_id,
                    'input': collected.get('tool_calls', [])
                })
            else:
                record_event({
                    'kind': 'error',
                    'agent_id': sub_id,
                    'node_id': sub_id,
                    'error': 'Delegation produced no final content.'
                })
        except Exception:
            pass

        if collected['status'] == 'final':
            return {
                'success': True,
                'content': collected.get('content') or '',
                'error': None,
                'tool_name': f'agent:{sub_id}',
                'raw': collected
            }
        if collected['status'] == 'tool_calls':
            return {
                'success': False,
                'content': '',
                'error': 'Sub-agent requested tool_calls; external execution required.',
                'tool_name': f'agent:{sub_id}',
                'raw': collected
            }
        return {
            'success': False,
            'content': '',
            'error': 'Delegation produced no final content.',
            'tool_name': f'agent:{sub_id}',
            'raw': collected
        }
