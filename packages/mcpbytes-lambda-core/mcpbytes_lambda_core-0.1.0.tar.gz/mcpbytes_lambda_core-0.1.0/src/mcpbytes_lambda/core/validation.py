"""
mcpbytes-lambda • Core Validation

JSON Schema generation from Python type hints + lightweight parameter validation.
Transport-agnostic (no HTTP/Lambda assumptions). Minimal MCP 2025-06-18 additions.
"""

from __future__ import annotations

import inspect
from dataclasses import fields, is_dataclass, MISSING
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from .types import ToolAnnotations, PromptArgument


# ---------- Python → JSON Schema ----------

def python_type_to_json_schema(python_type: type) -> Dict[str, Any]:
    """
    Convert a Python type hint into a JSON Schema fragment.
    Handles primitives, containers, Optional/Union, dataclasses, and basic literals.
    """
    # NoneType
    if python_type is type(None):  # noqa: E721
        return {"type": "null"}

    # Any type (MCP 2025-06-18: needed for structured output)
    if python_type is Any:
        return {}

    # Primitives
    if python_type is str:
        return {"type": "string"}
    if python_type is int:
        return {"type": "integer"}
    if python_type is float:
        return {"type": "number"}
    if python_type is bool:
        return {"type": "boolean"}

    origin = get_origin(python_type)
    args = get_args(python_type)

    # Optional[T] == Union[T, None]
    if origin is Union:
        # Optional[T]
        if len(args) == 2 and type(None) in args:  # noqa: E721
            non_none = args[0] if args[1] is type(None) else args[1]  # noqa: E721
            return python_type_to_json_schema(non_none)
        # General Union
        return {"anyOf": [python_type_to_json_schema(a) for a in args]}

    # List[T]
    if origin in (list, List):
        return {
            "type": "array",
            "items": python_type_to_json_schema(args[0]) if args else {},
        }

    # Dict[K, V] (restrict to string keys for schema clarity)
    if origin in (dict, Dict):
        value_schema = python_type_to_json_schema(args[1]) if len(args) >= 2 else {}
        return {"type": "object", "additionalProperties": value_schema}

    # Tuples -> array with items
    if origin in (tuple,):
        if args and args[-1] is Ellipsis:
            # Tuple[T, ...]
            return {"type": "array", "items": python_type_to_json_schema(args[0])}
        return {"type": "array", "prefixItems": [python_type_to_json_schema(a) for a in args]}

    # Dataclasses
    if is_dataclass(python_type):
        return dataclass_to_json_schema(python_type)

    # typing.Literal support (if present)
    try:
        from typing import Literal  # type: ignore
        if origin is Literal:
            lits = list(args)
            # Derive a type if all literals share one primitive type
            lit_types = set(type(v) for v in lits)
            schema: Dict[str, Any] = {"enum": lits}
            if len(lit_types) == 1:
                t = lit_types.pop()
                if t is str:
                    schema["type"] = "string"
                elif t is int:
                    schema["type"] = "integer"
                elif t is float:
                    schema["type"] = "number"
                elif t is bool:
                    schema["type"] = "boolean"
            return schema
    except Exception:
        pass

    # Fallback (MCP 2025-06-18: graceful for complex types)
    return {"type": "object"}


def dataclass_to_json_schema(dataclass_type: type) -> Dict[str, Any]:
    """Convert a dataclass to a JSON Schema object."""
    properties: Dict[str, Any] = {}
    required: List[str] = []

    try:
        for f in fields(dataclass_type):
            properties[f.name] = python_type_to_json_schema(f.type)
            # Required if no default and no default_factory
            if f.default is MISSING and f.default_factory is MISSING:
                required.append(f.name)
    except Exception:
        # MCP 2025-06-18: graceful fallback for problematic dataclasses
        return {"type": "object"}

    schema: Dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return schema


# ---------- Docstring helpers ----------

def extract_param_description(func: callable, param_name: str) -> str:
    """
    Pull a short description for a parameter from the function docstring.
    Supports Google-style Args: and Sphinx-style :param name: blocks.
    """
    if not func.__doc__:
        return ""

    doc = func.__doc__.strip()
    lines = doc.split("\n")

    for i, line in enumerate(lines):
        s = line.strip()
        # Google style section
        if s.lower().startswith(("args:", "parameters:", "arguments:")):
            for j in range(i + 1, len(lines)):
                pl = lines[j].strip()
                if not pl:
                    continue
                if pl.startswith(f"{param_name}:") or pl.startswith(f"{param_name} "):
                    if ":" in pl:
                        return pl.split(":", 1)[1].strip()
                if pl.endswith(":") or pl.lower().startswith(("returns:", "yields:", "raises:")):
                    break
        # Sphinx style
        if s.startswith(f":param {param_name}:"):
            parts = s.split(":", 2)
            return parts[2].strip() if len(parts) > 2 else ""
    return ""


# ---------- Schema builders used by decorators/server ----------

def generate_tool_schema(func: callable) -> Dict[str, Any]:
    """
    Build a JSON Schema 'object' for a tool's input parameters from the signature and type hints.
    """
    try:
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
    except Exception:
        # MCP 2025-06-18: graceful fallback if inspection fails
        return {"type": "object", "properties": {}}

    properties: Dict[str, Any] = {}
    required: List[str] = []

    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue

        hinted = type_hints.get(name, str)
        try:
            schema = python_type_to_json_schema(hinted)
        except Exception:
            # Fallback for problematic type hints
            schema = {"type": "string"}

        desc = extract_param_description(func, name)
        if desc:
            schema["description"] = desc

        properties[name] = schema

        if param.default is inspect.Parameter.empty:
            required.append(name)

    out: Dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        out["required"] = required
    return out


def extract_prompt_arguments(func: callable) -> List[PromptArgument]:
    """Create PromptArgument descriptors from a prompt function's parameters."""
    try:
        sig = inspect.signature(func)
    except Exception:
        return []

    args: List[PromptArgument] = []

    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue

        title = name.replace("_", " ").title()
        desc = extract_param_description(func, name) or f"The {title.lower()} parameter"
        required = param.default is inspect.Parameter.empty

        args.append(PromptArgument(
            name=name,
            title=title,
            description=desc,
            required=required,
        ))

    return args


def create_tool_annotations(
    title: Optional[str] = None,
    read_only: bool = False,
    destructive: bool = False,
    idempotent: bool = False,
    open_world: bool = True,
) -> ToolAnnotations:
    """Build ToolAnnotations with sensible defaults."""
    return ToolAnnotations(
        title=title,
        readOnlyHint=read_only,
        destructiveHint=destructive,
        idempotentHint=idempotent,
        openWorldHint=open_world,
    )


# ---------- Lightweight argument validation ----------

def validate_tool_parameters(schema: Dict[str, Any], arguments: Dict[str, Any]) -> List[str]:
    """
    Basic schema validation for tool 'arguments' payloads.
    Checks required fields and primitive type compatibility.

    This is intentionally lightweight to avoid heavy deps; callers can
    plug a full JSON Schema validator if needed.
    """
    errors: List[str] = []

    # Required fields
    for field in schema.get("required", []):
        if field not in arguments:
            errors.append(f"Missing required parameter: {field}")

    properties = schema.get("properties", {})

    for arg_name, arg_value in arguments.items():
        prop = properties.get(arg_name)
        if not prop:
            # Unknown fields are allowed (forward-compat)
            continue

        if not _is_type_compatible(prop, arg_value):
            expected = _schema_type_label(prop)
            actual = type(arg_value).__name__
            errors.append(f"Parameter '{arg_name}' must be {expected} (got {actual})")

    return errors


# ---------- helpers ----------

def _schema_type_label(prop: Dict[str, Any]) -> str:
    if "anyOf" in prop:
        return " or ".join(_schema_type_label(p) for p in prop["anyOf"])
    t = prop.get("type")
    if t is None:
        if "enum" in prop:
            return "one of the allowed values"
        return "a valid value"
    if t == "array":
        inner = _schema_type_label(prop.get("items", {}))
        return f"an array of {inner}"
    if t == "object":
        return "an object"
    return f"a {t}"


def _is_type_compatible(prop: Dict[str, Any], value: Any) -> bool:
    """Very small compatibility check for common JSON Schema fragments."""
    # anyOf
    if "anyOf" in prop:
        return any(_is_type_compatible(p, value) for p in prop["anyOf"])

    t = prop.get("type")

    # Enum
    if "enum" in prop:
        return value in set(prop["enum"])

    if t is None:
        # No explicit type → accept (could be refined)
        return True

    if t == "string":
        return isinstance(value, str)
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if t == "boolean":
        return isinstance(value, bool)
    if t == "array":
        if not isinstance(value, list):
            return False
        items_schema = prop.get("items")
        if not items_schema:
            return True
        return all(_is_type_compatible(items_schema, v) for v in value)
    if t == "object":
        return isinstance(value, dict)

    # Fallback accept
    return True