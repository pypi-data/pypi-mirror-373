"""
mcpbytes-lambda • Core Decorators

Transport-agnostic decorators for registering MCP tools and prompts.
- Auto-generates JSON Schema from type hints
- Validates parameters against the generated schema
- MCP 2025-06-18 compliant with structured output support
"""

import asyncio
import inspect
import os
from typing import Callable, Optional, Any, Dict
from functools import wraps

from .types import (
    ToolResult, TextContent, MCPToolError,
    ToolDefinition, PromptDefinition, ToolAnnotations
)
from .validation import (
    generate_tool_schema, extract_prompt_arguments,
    create_tool_annotations, validate_tool_parameters,
    python_type_to_json_schema,
    _is_type_compatible, _schema_type_label
)


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    title: Optional[str] = None,
    read_only: bool = False,
    destructive: bool = False,
    idempotent: bool = False,
    open_world: bool = True,
    structured_output: bool = False,
):
    """
    Decorator to register a function as an MCP tool.

    Automatically generates JSON Schema from type hints, validates parameters,
    and converts return values to ToolResult. MCP 2025-06-18 compliant.

    Args:
        name: Tool name (defaults to function name with dots)
        description: Tool description (defaults to first docstring line)
        title: Human-readable title for the tool
        read_only: Tool only reads data
        destructive: Tool can destroy data
        idempotent: Repeated calls safe
        open_world: Interacts with external systems
        structured_output: Enable structured output schema generation (MCP 2025-06-18)
    """
    def decorator(func: Callable) -> Callable:
        # Derive metadata
        tool_name = name or func.__name__.replace("_", ".")
        tool_description = description or _extract_description(func)
        tool_title = title or tool_name.replace(".", " ").title()

        # Schema + annotations
        schema = generate_tool_schema(func)
        annotations = create_tool_annotations(
            title=tool_title,
            read_only=read_only,
            destructive=destructive,
            idempotent=idempotent,
            open_world=open_world,
        )

        # MCP 2025-06-18: Generate output schema if structured output enabled
        output_schema = None
        if structured_output:
            sig = inspect.signature(func)
            if sig.return_annotation != inspect.Signature.empty:
                try:
                    output_schema = python_type_to_json_schema(sig.return_annotation)
                except Exception:
                    # Fallback if schema generation fails - don't break the tool
                    output_schema = {"type": "object"}

        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> ToolResult:
            """Async wrapper for tool execution with validation + error mapping."""
            try:
                # Validate parameters
                if schema:
                    validation_errors = validate_tool_parameters(schema, kwargs)
                    if validation_errors:
                        error_msg = "Parameter validation failed:\n" + "\n".join(validation_errors)
                        return ToolResult(
                            content=[TextContent(text=error_msg)],
                            isError=True
                        )

                # Execute (supports sync or async)
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)

                # Normalize to ToolResult with optional structured output schema
                return _convert_to_tool_result(result, output_schema=output_schema)

            except MCPToolError as e:
                # Business/domain error visible to the LLM
                return ToolResult(
                    content=[TextContent(text=f"<error>{str(e)}</error>")],
                    isError=True
                )
            except Exception as e:  # noqa: BLE001 - we intentionally catch to surface to LLM
                # Production-safe error messages
                from .types import EnvironmentVars
                if os.getenv(EnvironmentVars.MCP_DEBUG, "false").lower() == "true":
                    error_msg = f"<error>Unexpected error: {str(e)}</error>"  # Debug mode
                else:
                    error_msg = "<error>Tool execution failed</error>"  # Production mode
                return ToolResult(
                    content=[TextContent(text=error_msg)],
                    isError=True
                )

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> ToolResult:
            """Run the async wrapper from sync contexts safely."""
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # Running inside an event loop: create a task and wait
                return loop.run_until_complete(async_wrapper(*args, **kwargs))  # type: ignore[misc]
            else:
                return asyncio.run(async_wrapper(*args, **kwargs))

        # Choose wrapper based on original function type
        wrapper = async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

        # Attach tool definition metadata expected by the core server
        tool_def = ToolDefinition(
            name=tool_name,
            description=tool_description,
            function=wrapper,
            schema=schema,
            annotations=annotations,
            output_schema=output_schema,  # MCP 2025-06-18: Include output schema
        )
        # Preferred attribute
        setattr(wrapper, "_mcp_tool", tool_def)
        # Back-compat with older code that looked for _mcp_tool_definition
        setattr(wrapper, "_mcp_tool_definition", tool_def)

        return wrapper

    return decorator


def prompt(
    name: Optional[str] = None,
    description: Optional[str] = None,
    title: Optional[str] = None,
):
    """
    Decorator to register a function as an MCP prompt template.

    Extracts prompt arguments from the function signature and normalizes content
    into MCP-style content blocks for GetPromptResult.
    """
    def decorator(func: Callable) -> Callable:
        prompt_name = name or func.__name__
        prompt_description = description or _extract_description(func)
        prompt_title = title or prompt_name.replace("_", " ").title()

        arguments = extract_prompt_arguments(func)

        @wraps(func)
        def wrapper(*args, **kwargs) -> Dict[str, Any]:
            """Execute prompt function and format as MCP content blocks."""
            try:
                if asyncio.iscoroutinefunction(func):
                    content = asyncio.run(func(*args, **kwargs))
                else:
                    content = func(*args, **kwargs)

                # Normalize to content blocks
                if isinstance(content, str):
                    content_blocks = [{"type": "text", "text": content}]
                elif isinstance(content, list):
                    content_blocks = content  # assume blocks already
                else:
                    content_blocks = [{"type": "text", "text": str(content)}]

                return {
                    "description": prompt_description or prompt_title,
                    "messages": [{
                        "role": "user",
                        "content": content_blocks
                    }]
                }

            except Exception as e:  # noqa: BLE001
                return {
                    "description": f"Error in prompt {prompt_name}",
                    "messages": [{
                        "role": "user",
                        "content": [{"type": "text", "text": f"<error>Prompt error: {str(e)}</error>"}]
                    }]
                }

        prompt_def = PromptDefinition(
            name=prompt_name,
            description=prompt_description,
            function=wrapper,
            arguments=arguments,
        )
        setattr(wrapper, "_mcp_prompt", prompt_def)
        setattr(wrapper, "_mcp_prompt_definition", prompt_def)  # back-compat

        return wrapper

    return decorator


def _extract_description(func: Callable) -> str:
    """First non-empty docstring line or a default label."""
    if not func.__doc__:
        return f"Tool: {func.__name__}"
    for line in func.__doc__.strip().split("\n"):
        line = line.strip()
        if line:
            return line
    return f"Tool: {func.__name__}"


def _convert_to_tool_result(result: Any, output_schema: Optional[Dict[str, Any]] = None) -> ToolResult:
    """
    Normalize arbitrary return types into ToolResult with MCP specification compliance.
    
    Args:
        result: Function return value
        output_schema: Optional JSON schema for structured output validation
        
    Returns:
        ToolResult: MCP-compliant result
    """
    if isinstance(result, ToolResult):
        return result

    if isinstance(result, str):
        return ToolResult(content=[TextContent(text=result)], isError=False)

    if isinstance(result, dict):
        # If looks like ToolResult dict, convert fields
        if "content" in result and "isError" in result:
            content = result["content"]
            if isinstance(content, list):
                converted = []
                for item in content:
                    if isinstance(item, TextContent):
                        converted.append(item)
                    elif isinstance(item, dict) and item.get("type") == "text":
                        converted.append(TextContent(
                            text=item.get("text", ""),
                            annotations=item.get("annotations"),
                            _meta=item.get("_meta"),
                        ))
                    else:
                        converted.append(TextContent(text=str(item)))
                return ToolResult(
                    content=converted,
                    isError=bool(result.get("isError", False)),
                    structuredContent=result.get("structuredContent"),
                    _meta=result.get("_meta"),
                )
        
        # Validate structured output if schema provided
        if output_schema:
            validation_errors = _validate_structured_output(result, output_schema)
            if validation_errors:
                error_msg = "Structured output validation failed:\n" + "\n".join(validation_errors)
                return ToolResult(
                    content=[TextContent(text=error_msg)],
                    isError=True
                )
        
        # Otherwise treat as structured payload - MCP structured output
        return ToolResult(
            content=[TextContent(text="Structured result")],
            isError=False,
            structuredContent=result,
        )

    if isinstance(result, list):
        items = []
        for item in result:
            if isinstance(item, TextContent):
                items.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                items.append(TextContent(
                    text=item.get("text", ""),
                    annotations=item.get("annotations"),
                    _meta=item.get("_meta"),
                ))
            else:
                items.append(TextContent(text=str(item)))
        return ToolResult(content=items, isError=False)

    return ToolResult(content=[TextContent(text=str(result))], isError=False)


def _validate_structured_output(data: Dict[str, Any], schema: Dict[str, Any]) -> list[str]:
    """
    Basic validation of structured output against JSON schema.
    
    Args:
        data: The structured data to validate
        schema: JSON schema to validate against
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    # Basic type check
    if schema.get("type") == "object" and not isinstance(data, dict):
        errors.append(f"Expected object, got {type(data).__name__}")
        return errors
    
    # Check required properties
    required = schema.get("required", [])
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Check property types
    properties = schema.get("properties", {})
    for field, value in data.items():
        if field in properties:
            prop_schema = properties[field]
            prop_type = prop_schema.get("type")
            
            if prop_type == "string" and not isinstance(value, str):
                errors.append(f"Field '{field}' must be string, got {type(value).__name__}")
            elif prop_type == "integer" and not isinstance(value, int):
                errors.append(f"Field '{field}' must be integer, got {type(value).__name__}")
            elif prop_type == "number" and not isinstance(value, (int, float)):
                errors.append(f"Field '{field}' must be number, got {type(value).__name__}")
            elif prop_type == "boolean" and not isinstance(value, bool):
                errors.append(f"Field '{field}' must be boolean, got {type(value).__name__}")
            elif prop_type == "object" and not isinstance(value, dict):
                errors.append(f"Field '{field}' must be object, got {type(value).__name__}")
            elif prop_type == "array" and not isinstance(value, list):
                errors.append(f"Field '{field}' must be array, got {type(value).__name__}")
    
    # Check additionalProperties (Dict[str, T] schemas)
    additional_schema = schema.get("additionalProperties")
    if additional_schema and not properties:  # Only for Dict[str, T] case
        for field, value in data.items():
            if not _is_type_compatible(additional_schema, value):
                expected = _schema_type_label(additional_schema)
                errors.append(f"Field '{field}' must be {expected}, got {type(value).__name__}")
    
    return errors
