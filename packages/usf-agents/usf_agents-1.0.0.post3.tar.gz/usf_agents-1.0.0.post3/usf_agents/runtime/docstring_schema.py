import re
from typing import Any, Dict, List, Optional

# Optional YAML support
try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore[attr-defined]


class DocstringParseError(Exception):
    pass


_GOOGLE_ARGS_HEADERS = ("Args:", "Arguments:", "Parameters:")
_NUMPY_PARAMS_HEADERS = ("Parameters",)


def json_type_from_str(t: str) -> str:
    """
    Map common type strings (case-insensitive) to JSON Schema primitive types.
    Unknown maps to 'string'.
    """
    t_norm = (t or "").strip().lower()
    # remove trailing qualifiers like ", optional"
    t_norm = t_norm.split(",")[0].strip()
    # remove typing wrappers like List[int], Sequence[str], Dict[str, Any], Tuple[int, int]
    if t_norm.startswith("list") or t_norm.startswith("tuple") or t_norm.startswith("sequence"):
        return "array"
    if t_norm.startswith("dict") or t_norm.startswith("mapping"):
        return "object"
    if t_norm in ("str", "string", "text"):
        return "string"
    if t_norm in ("int", "float", "number", "double", "decimal"):
        return "number"
    if t_norm in ("bool", "boolean"):
        return "boolean"
    if t_norm in ("object",):
        return "object"
    if t_norm in ("array",):
        return "array"
    return "string"


def _first_line_summary(doc: str) -> str:
    for line in (doc or "").strip().splitlines():
        s = line.strip()
        if s:
            return s
    return ""


def _split_sections(doc: str) -> List[str]:
    # Normalize line endings and ensure consistent indentation handling
    return (doc or "").splitlines()


def _find_yaml_blocks(doc: str) -> List[str]:
    """
    Find triple-fenced code blocks that might contain YAML (```yaml ... ``` or ```yml ... ``` or ``` ... ```).
    Returns list of block contents (inside fences).
    """
    blocks: List[str] = []
    pattern = re.compile(r"```(?:yaml|yml)?\s*([\s\S]*?)```", re.IGNORECASE)
    for m in pattern.finditer(doc or ""):
        blocks.append(m.group(1).strip())
    return blocks


def parse_openapi_yaml_block(doc: str) -> Optional[Dict[str, Any]]:
    """
    If a YAML code block exists and can be parsed into an OpenAI-compatible schema, return it.
    Expected minimal shape:
      description: ...
      parameters:
        type: object
        properties:
          arg:
            type: string|number|boolean|object|array
            description: ...
        required: [arg1, arg2]
    If yaml is not available or parsing fails/shape invalid, return None.
    """
    blocks = _find_yaml_blocks(doc or "")
    if not blocks:
        return None
    if yaml is None:  # pragma: no cover
        return None

    for raw in blocks:
        try:
            data = yaml.safe_load(raw)  # type: ignore[attr-defined]
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        desc = data.get("description") or _first_line_summary(doc)
        params = data.get("parameters") or {}
        if not isinstance(params, dict):
            continue
        ptype = params.get("type")
        props = params.get("properties")
        req = params.get("required", [])
        if ptype == "object" and isinstance(props, dict) and isinstance(req, (list, tuple)):
            # Basic normalization pass: ensure required is a list of strings
            required = [str(x) for x in req]
            return {
                "description": str(desc or ""),
                "parameters": {
                    "type": "object",
                    "properties": dict(props),
                    "required": required
                }
            }
    return None


def _parse_google_args_section(lines: List[str], start_idx: int) -> Dict[str, Any]:
    """
    Parse Google-style 'Args:' or 'Arguments:' or 'Parameters:' section into schema.
    Expected item lines:
      name (type[, optional]): description...
    Continuation lines (indented) are appended to description.
    """
    properties: Dict[str, Any] = {}
    required: List[str] = []
    i = start_idx + 1

    # regex: foo (int[, optional]): description
    item_re = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)\s*:\s*(.*)$")

    current_name: Optional[str] = None
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        # A new top-level section header ends this block
        if line.strip().endswith(":") and line.strip() not in ("optional:",):
            # heuristic: another section header like 'Returns:' or 'Raises:'
            # stop if indentation is 0 or very small
            if not line.startswith(" ") and not line.startswith("\t"):
                break

        m = item_re.match(line)
        if m:
            # finalize previous item
            current_name = m.group(1)
            type_part = m.group(2) or ""
            desc_part = m.group(3) or ""
            is_optional = ("optional" in type_part.lower()) or ("optional" in desc_part.lower())
            jtype = json_type_from_str(type_part)

            properties[current_name] = {"type": jtype}
            # Add description if present
            if desc_part:
                properties[current_name]["description"] = desc_part.strip()

            if not is_optional:
                required.append(current_name)
        else:
            # continuation of previous description (indented)
            if current_name and (line.startswith(" ") or line.startswith("\t")):
                prev_desc = properties[current_name].get("description", "")
                joiner = "\n" if prev_desc else ""
                properties[current_name]["description"] = f"{prev_desc}{joiner}{line.strip()}"
            else:
                # another kind of line; if it looks like a new header (e.g., 'Returns:'), end parsing
                if line.strip().endswith(":") and not (line.startswith(" ") or line.startswith("\t")):
                    break
        i += 1

    return {
        "type": "object",
        "properties": properties,
        "required": required
    }


def _locate_google_args_header(lines: List[str]) -> Optional[int]:
    for idx, line in enumerate(lines):
        s = line.strip()
        if s in _GOOGLE_ARGS_HEADERS:
            return idx
    return None


def _parse_numpy_parameters_block(lines: List[str], header_idx: int) -> Dict[str, Any]:
    """
    Parse NumPy-style 'Parameters' section:
      Parameters
      ----------
      name : type[, optional]
          description...
    """
    properties: Dict[str, Any] = {}
    required: List[str] = []

    i = header_idx + 1

    # Skip possible underline of dashes
    if i < len(lines) and re.match(r"^\s*-{3,}\s*$", lines[i]):
        i += 1

    name_type_re = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([^,]+)(?:,\s*optional)?\s*$")

    current_name: Optional[str] = None
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        # New header likely ends the block
        if line.strip().endswith(":") and not (line.startswith(" ") or line.startswith("\t")):
            break

        m = name_type_re.match(line)
        if m:
            current_name = m.group(1)
            type_part = m.group(2) or ""
            is_optional = ("optional" in line.lower())
            jtype = json_type_from_str(type_part)
            properties[current_name] = {"type": jtype}
            if not is_optional:
                required.append(current_name)
        else:
            # Continuation description
            if current_name and (line.startswith(" ") or line.startswith("\t")):
                prev_desc = properties[current_name].get("description", "")
                joiner = "\n" if prev_desc else ""
                properties[current_name]["description"] = f"{prev_desc}{joiner}{line.strip()}"
            else:
                # If it's a new section header (e.g. Returns), stop
                if line.strip().endswith(":") and not (line.startswith(" ") or line.startswith("\t")):
                    break

        i += 1

    return {
        "type": "object",
        "properties": properties,
        "required": required
    }


def parse_google_or_numpy(doc: str) -> Optional[Dict[str, Any]]:
    """
    Attempt to parse Google-style 'Args:' (or 'Arguments:' / 'Parameters:') or NumPy-style 'Parameters' blocks.
    Returns a schema dict or None.
    """
    if not doc:
        return None
    lines = _split_sections(doc)

    # Google-style first
    g_idx = _locate_google_args_header(lines)
    if g_idx is not None:
        schema = _parse_google_args_section(lines, g_idx)
        # Only valid if we captured at least one property
        if schema.get("properties"):
            return {
                "description": _first_line_summary(doc),
                "parameters": schema
            }

    # NumPy-style
    # Locate a 'Parameters' header (line equals 'Parameters' and next line is dashed underline or not strictly required)
    for idx, line in enumerate(lines):
        if line.strip() in _NUMPY_PARAMS_HEADERS:
            schema = _parse_numpy_parameters_block(lines, idx)
            if schema.get("properties"):
                return {
                    "description": _first_line_summary(doc),
                    "parameters": schema
                }

    return None


def parse_docstring_to_schema(func: Any) -> Optional[Dict[str, Any]]:
    """
    Parse function docstring into an OpenAI-compatible tool schema.
    Precedence:
      1) YAML code block (OpenAPI-like) if present and valid
      2) Google-style Args / NumPy Parameters sections
    Returns schema dict or None if parsing fails or docstring missing.
    """
    doc = getattr(func, "__doc__", None)
    if not doc:
        return None

    # 1) YAML block precedence
    schema = parse_openapi_yaml_block(doc)
    if schema and isinstance(schema, dict):
        # ensure types in properties are normalized if possible
        params = schema.get("parameters") or {}
        props = (params or {}).get("properties") or {}
        if isinstance(props, dict):
            for k, v in list(props.items()):
                if isinstance(v, dict) and "type" in v:
                    v["type"] = json_type_from_str(str(v.get("type", "")))
        return schema

    # 2) Google / NumPy parsing
    schema = parse_google_or_numpy(doc)
    if schema:
        return schema

    return None
