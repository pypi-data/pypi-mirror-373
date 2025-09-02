from typing import Any, Callable, Optional, Dict


def tool(
    name: Optional[str] = None,
    alias: Optional[str] = None,
    description: Optional[str] = None,
    schema: Optional[Dict[str, Any]] = None
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Lightweight decorator to attach USF tool metadata to a function.

    Usage:
        @tool  # metadata optional; docstring will be parsed for schema
        def calc_sum(numbers: list[int]) -> int:
            \"\"\"
            Calculate the sum of a list of integers.

            Args:
                numbers (list[int]): A list of integers to add together.
            \"\"\"
            return sum(numbers)

        @tool(name="calc_sum", alias="sum_tool", description="Sum a list of integers")
        def calc_sum(numbers: list[int]) -> int:
            ...

        # You can also provide an explicit OpenAI-compatible schema in the decorator
        @tool(
            name="calc_sum",
            alias="sum_tool",
            description="Sum a list of integers",
            schema={
                "description": "Sum integers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "numbers": {"type": "array", "description": "List of ints"}
                    },
                    "required": ["numbers"]
                }
            }
        )
        def calc_sum(numbers: list[int]) -> int:
            return sum(numbers)

    Notes:
    - This decorator does NOT register the function as a tool. Use ManagerAgent.add_function_tool(...)
      or batch sugar APIs to register.
    - Precedence when registering:
        1) Schema argument passed to add_function_tool(..., schema=...) takes priority.
        2) Decorator-provided schema (this decorator's 'schema' argument), if present.
        3) Docstring parsing (YAML → Google → NumPy).
    - Name, alias, and description provided here act as defaults. Explicit arguments passed to
      add_function_tool take precedence.
    """
    meta: Dict[str, Any] = {}
    if name is not None:
        meta["name"] = name
    if alias is not None:
        meta["alias"] = alias
    if description is not None:
        meta["description"] = description
    if schema is not None:
        meta["schema"] = schema

    def _wrap(func: Callable[..., Any]) -> Callable[..., Any]:
        # Attach metadata without altering the callable behavior
        setattr(func, "__usf_tool__", meta)
        return func

    return _wrap
