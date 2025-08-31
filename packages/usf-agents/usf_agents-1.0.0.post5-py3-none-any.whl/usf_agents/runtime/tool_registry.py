import asyncio
import json
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

from ..types import Message, Tool, ToolCall
from ..types import ToolExample  # type: ignore


class ToolRegistry:
    """
    Lightweight in-memory registry for custom tools.

    - Register Python callables as tools with OpenAI-compatible schema.
    - Optional example-based validation: if provided, all examples must pass or registration fails.
    - Supports aliasing.
    - Provides a default async router() that dispatches ToolCall to the registered callable.
    """

    def __init__(self) -> None:
        self._funcs: Dict[str, Callable[..., Any]] = {}     # name -> callable
        self._aliases: Dict[str, str] = {}                  # alias -> canonical name
        self._tools: Dict[str, Tool] = {}                   # canonical name -> Tool dict (with metadata)

    def _resolve_name(self, name_or_alias: str) -> str:
        return self._aliases.get(name_or_alias, name_or_alias)

    def _assert_unique_name(self, name: str) -> None:
        if name in self._funcs or name in self._aliases:
            raise Exception(f"ToolRegistry Error: name '{name}' already registered")

    def _assert_unique_alias(self, alias: str) -> None:
        if alias in self._funcs or alias in self._aliases:
            raise Exception(f"ToolRegistry Error: alias '{alias}' already registered")

    async def _maybe_await(self, value: Any) -> Any:
        if asyncio.iscoroutine(value):
            return await value
        return value

    async def _run_example(self, name: str, func: Callable[..., Any], ex: ToolExample) -> None:
        """
        Execute one example and enforce expectations:
        - If 'expect_status' present and the result is a mapping with 'status' or similar, validate it.
        - If 'expect' present, shallow-compare equality.
        Any failure raises with a detailed error payload.
        """
        args = ex.get("args", {}) if isinstance(ex, dict) else {}
        try:
            result = await self._maybe_await(func(**args))
        except Exception as e:
            raise Exception(json.dumps({
                "tool_name": name,
                "example_name": ex.get("name"),
                "error": f"exception during example execution: {e}"
            })) from e

        # Validate status if provided
        if "expect_status" in ex:
            status = None
            if isinstance(result, dict):
                # Common shapes: {'status': 200} or HTTP-like {'status_code': 200}
                status = result.get("status", result.get("status_code"))
            if status != ex["expect_status"]:
                raise Exception(json.dumps({
                    "tool_name": name,
                    "example_name": ex.get("name"),
                    "error": f"expect_status={ex['expect_status']} but got {status}"
                }))

        # Validate value if provided (shallow equality)
        if "expect" in ex:
            if result != ex["expect"]:
                raise Exception(json.dumps({
                    "tool_name": name,
                    "example_name": ex.get("name"),
                    "error": f"expect={ex['expect']} but got {result}"
                }))

    def _build_tool(self, final_name: str, schema: Dict[str, Any], alias: Optional[str]) -> Tool:
        """
        Build an OpenAI-compatible tool dict augmented with metadata that marks it as custom.
        """
        description = schema.get("description", f"Custom tool {final_name}")
        parameters = schema.get("parameters") or {
            "type": "object",
            "properties": {},
            "required": []
        }
        tool: Tool = {
            "type": "function",
            "function": {
                "name": final_name,
                "description": description,
                "parameters": parameters
            }  # type: ignore
        }
        # Attach metadata (ignored by OpenAI schema)
        # mypy/TypedDict won't accept extra keys, but at runtime dict is fine.
        tool["x_kind"] = "custom"       # type: ignore
        tool["x_alias"] = alias         # type: ignore
        return tool

    async def _validate_examples(self, name: str, func: Callable[..., Any], examples: Optional[List[ToolExample]]) -> None:
        if not examples:
            return
        for ex in examples:
            await self._run_example(name, func, ex)

    def register_function(
        self,
        name: str,
        func: Callable[..., Any],
        schema: Dict[str, Any],
        alias: Optional[str] = None,
        examples: Optional[List[ToolExample]] = None
    ) -> Tool:
        """
        Register a custom Python function as a tool.

        - Names must be unique.
        - If alias is provided, it must also be unique.
        - If examples are supplied, all must pass or registration fails and nothing is registered.
        """
        if not isinstance(name, str) or not name:
            raise Exception("ToolRegistry Error: name must be a non-empty string")
        if not callable(func):
            raise Exception("ToolRegistry Error: func must be callable")

        self._assert_unique_name(name)
        if alias:
            self._assert_unique_alias(alias)

        # Validate examples first (fail-fast)
        async def _validate_all() -> None:
            await self._validate_examples(name, func, examples)

        # Determine if an event loop is already running
        running_loop = None
        try:
            running_loop = asyncio.get_running_loop()
        except RuntimeError:
            running_loop = None

        if examples:
            if running_loop and running_loop.is_running():
                # Running loop present: perform synchronous validation for sync functions.
                for ex in examples:
                    args = ex.get("args", {}) if isinstance(ex, dict) else {}
                    try:
                        res = func(**args)
                    except Exception as e:
                        raise Exception(json.dumps({
                            "tool_name": name,
                            "example_name": ex.get("name"),
                            "error": f"exception during example execution: {e}"
                        })) from e

                    if asyncio.iscoroutine(res):
                        # Cannot await here without breaking the running loop contract.
                        raise Exception(json.dumps({
                            "tool_name": name,
                            "example_name": ex.get("name"),
                            "error": "async example cannot be validated synchronously inside a running loop; register with async helper or validate externally"
                        }))

                    # Validate status if provided
                    if "expect_status" in ex:
                        status = None
                        if isinstance(res, dict):
                            status = res.get("status", res.get("status_code"))
                        if status != ex["expect_status"]:
                            raise Exception(json.dumps({
                                "tool_name": name,
                                "example_name": ex.get("name"),
                                "error": f"expect_status={ex['expect_status']} but got {status}"
                            }))

                    # Validate value if provided (shallow equality)
                    if "expect" in ex:
                        if res != ex["expect"]:
                            raise Exception(json.dumps({
                                "tool_name": name,
                                "example_name": ex.get("name"),
                                "error": f"expect={ex['expect']} but got {res}"
                            }))
            else:
                # No running loop: run full async validation (supports async functions)
                asyncio.run(_validate_all())

        # Build and store tool
        display_name = alias or name
        tool = self._build_tool(display_name, schema, alias)
        self._funcs[name] = func
        self._tools[name] = tool
        if alias:
            self._aliases[alias] = name
        return tool

    def alias(self, tool_name: str, alias: str) -> None:
        """
        Add an alias for an existing tool.
        """
        canonical = self._resolve_name(tool_name)
        if canonical not in self._funcs:
            raise Exception(f"ToolRegistry Error: tool '{tool_name}' not found")
        self._assert_unique_alias(alias)
        self._aliases[alias] = canonical

    def get_tool(self, name_or_alias: str) -> Tool:
        canonical = self._resolve_name(name_or_alias)
        tool = self._tools.get(canonical)
        if not tool:
            raise Exception(f"ToolRegistry Error: tool '{name_or_alias}' not found")
        return tool

    def list_tools(self) -> List[Tool]:
        return [self._tools[k] for k in sorted(self._tools.keys())]

    def to_openai_tools(self) -> List[Tool]:
        return self.list_tools()

    def router(self) -> Callable[[ToolCall, List[Message]], Awaitable[Dict[str, Any]]]:
        """
        Return an async dispatcher that:
        - Parses ToolCall.function.arguments
        - Resolves name via alias map
        - Invokes the registered callable
        - Wraps the result into a {'success': bool, 'content': Any, 'error': Optional[str]} payload
        """
        async def _dispatch(tc: ToolCall, current_msgs: List[Message]) -> Dict[str, Any]:
            try:
                fn = (tc.get("function") or {}).get("name")  # type: ignore[attr-defined]
            except Exception:
                fn = None
            if not fn:
                return {"success": False, "error": "missing function name"}

            canonical = self._resolve_name(fn)
            func = self._funcs.get(canonical)
            if not func:
                return {"success": False, "error": f"tool '{fn}' not registered"}

            raw_args = (tc.get("function") or {}).get("arguments")  # type: ignore[attr-defined]
            try:
                args = json.loads(raw_args or "{}")
            except Exception:
                args = {}

            try:
                result = func(**args) if isinstance(args, dict) else func(args)
                if asyncio.iscoroutine(result):
                    result = await result
                return {"success": True, "content": result}
            except Exception as e:
                return {"success": False, "error": str(e)}

        return _dispatch
