"""
Unit tests for mcpbytes_lambda.core.decorators module.
"""

import pytest
import asyncio
from typing import Dict, Any, List
from mcpbytes_lambda.core.decorators import tool, prompt, _convert_to_tool_result, _extract_description
from mcpbytes_lambda.core.types import ToolResult, TextContent, MCPToolError


class TestToolDecorator:
    """Test @tool decorator functionality."""
    
    def test_basic_tool_decoration(self):
        """Test basic tool decoration."""
        @tool(name="test.tool", description="A test tool")
        def test_func(name: str) -> ToolResult:
            return ToolResult(content=[TextContent(text=f"Hello, {name}!")])
        
        # Check that tool definition is attached
        assert hasattr(test_func, "_mcp_tool")
        tool_def = test_func._mcp_tool
        assert tool_def.name == "test.tool"
        assert tool_def.description == "A test tool"
        assert tool_def.function == test_func
    
    def test_tool_with_defaults(self):
        """Test tool decoration with default values."""
        @tool()
        def simple_func(value: int) -> str:
            """A simple function."""
            return f"Value: {value}"
        
        tool_def = simple_func._mcp_tool
        assert tool_def.name == "simple.func"  # Converted from function name
        assert tool_def.description == "A simple function."  # From docstring
    
    def test_tool_schema_generation(self):
        """Test that tool decorator generates proper schema."""
        @tool()
        def math_add(a: float, b: float) -> ToolResult:
            """Add two numbers."""
            return ToolResult(content=[TextContent(text=str(a + b))])
        
        tool_def = math_add._mcp_tool
        schema = tool_def.schema
        
        assert schema["type"] == "object"
        assert "a" in schema["properties"]
        assert "b" in schema["properties"]
        assert schema["properties"]["a"]["type"] == "number"
        assert schema["properties"]["b"]["type"] == "number"
        assert "a" in schema["required"]
        assert "b" in schema["required"]
    
    def test_tool_annotations(self):
        """Test tool annotations creation."""
        @tool(read_only=True, idempotent=True, title="Math Tool")
        def read_only_tool(value: int) -> str:
            return str(value)
        
        tool_def = read_only_tool._mcp_tool
        annotations = tool_def.annotations
        
        assert annotations.title == "Math Tool"
        assert annotations.readOnlyHint is True
        assert annotations.idempotentHint is True
        assert annotations.destructiveHint is False
    
    def test_structured_output_tool(self):
        """Test tool with structured output enabled."""
        @tool(structured_output=True)
        def structured_tool(name: str) -> Dict[str, Any]:
            """Return structured data."""
            return {"name": name, "processed": True}
        
        tool_def = structured_tool._mcp_tool
        assert tool_def.output_schema is not None
        assert tool_def.output_schema["type"] == "object"
    
    def test_tool_execution_sync(self):
        """Test synchronous tool execution."""
        @tool()
        def sync_tool(message: str) -> ToolResult:
            return ToolResult(content=[TextContent(text=f"Sync: {message}")])
        
        result = sync_tool(message="test")
        assert isinstance(result, ToolResult)
        assert result.content[0].text == "Sync: test"
        assert result.isError is False
    
    def test_tool_execution_async(self):
        """Test asynchronous tool execution."""
        @tool()
        async def async_tool(message: str) -> ToolResult:
            await asyncio.sleep(0.001)  # Simulate async work
            return ToolResult(content=[TextContent(text=f"Async: {message}")])
        
        # Test async execution
        result = asyncio.run(async_tool(message="test"))
        assert isinstance(result, ToolResult)
        assert result.content[0].text == "Async: test"
    
    def test_tool_parameter_validation(self):
        """Test tool parameter validation."""
        @tool()
        def validated_tool(name: str, age: int) -> ToolResult:
            return ToolResult(content=[TextContent(text=f"{name} is {age}")])
        
        # Valid parameters
        result = validated_tool(name="John", age=30)
        assert not result.isError
        
        # Invalid parameters should be caught by validation
        # Note: This tests the validation logic in the wrapper
        result = validated_tool(name="John", age="invalid")
        assert result.isError
        assert "Parameter validation failed" in result.content[0].text
    
    def test_tool_error_handling(self):
        """Test tool error handling."""
        @tool()
        def error_tool(should_fail: bool) -> ToolResult:
            if should_fail:
                raise MCPToolError("Tool failed intentionally")
            return ToolResult(content=[TextContent(text="Success")])
        
        # Successful execution
        result = error_tool(should_fail=False)
        assert not result.isError
        
        # Error execution
        result = error_tool(should_fail=True)
        assert result.isError
        assert "Tool failed intentionally" in result.content[0].text
    
    def test_tool_unexpected_error_handling(self):
        """Test handling of unexpected errors."""
        @tool()
        def buggy_tool() -> ToolResult:
            raise ValueError("Unexpected error")
        
        result = buggy_tool()
        assert result.isError
        # Should contain generic error message in production mode
        assert "error" in result.content[0].text.lower()


class TestPromptDecorator:
    """Test @prompt decorator functionality."""
    
    def test_basic_prompt_decoration(self):
        """Test basic prompt decoration."""
        @prompt(name="test.prompt", description="A test prompt")
        def test_prompt(name: str) -> str:
            return f"Hello, {name}!"
        
        # Check that prompt definition is attached
        assert hasattr(test_prompt, "_mcp_prompt")
        prompt_def = test_prompt._mcp_prompt
        assert prompt_def.name == "test.prompt"
        assert prompt_def.description == "A test prompt"
    
    def test_prompt_with_defaults(self):
        """Test prompt decoration with default values."""
        @prompt()
        def greeting_prompt(name: str) -> str:
            """Generate a greeting."""
            return f"Hello, {name}!"
        
        prompt_def = greeting_prompt._mcp_prompt
        assert prompt_def.name == "greeting_prompt"
        assert prompt_def.description == "Generate a greeting."
    
    def test_prompt_argument_extraction(self):
        """Test prompt argument extraction."""
        @prompt()
        def complex_prompt(name: str, style: str = "formal", count: int = 1) -> str:
            return f"Hello {name}" * count
        
        prompt_def = complex_prompt._mcp_prompt
        args = prompt_def.arguments
        
        assert len(args) == 3
        
        name_arg = next(arg for arg in args if arg.name == "name")
        assert name_arg.required is True
        
        style_arg = next(arg for arg in args if arg.name == "style")
        assert style_arg.required is False
        
        count_arg = next(arg for arg in args if arg.name == "count")
        assert count_arg.required is False
    
    def test_prompt_execution(self):
        """Test prompt execution."""
        @prompt()
        def simple_prompt(name: str) -> str:
            return f"Hello, {name}!"
        
        result = simple_prompt(name="World")
        
        # Should return MCP-formatted response
        assert isinstance(result, dict)
        assert "messages" in result
        assert len(result["messages"]) == 1
        assert result["messages"][0]["role"] == "user"
        assert result["messages"][0]["content"][0]["type"] == "text"
        assert "Hello, World!" in result["messages"][0]["content"][0]["text"]
    
    def test_prompt_error_handling(self):
        """Test prompt error handling."""
        @prompt()
        def error_prompt() -> str:
            raise ValueError("Prompt failed")
        
        result = error_prompt()
        
        # Should return error in MCP format
        assert isinstance(result, dict)
        assert "error" in result["description"].lower()
        assert "messages" in result


class TestConvertToToolResult:
    """Test _convert_to_tool_result helper function."""
    
    def test_convert_tool_result(self):
        """Test converting existing ToolResult."""
        original = ToolResult(content=[TextContent(text="test")])
        result = _convert_to_tool_result(original)
        assert result is original  # Should return same instance
    
    def test_convert_string(self):
        """Test converting string to ToolResult."""
        result = _convert_to_tool_result("Hello, world!")
        assert isinstance(result, ToolResult)
        assert result.content[0].text == "Hello, world!"
        assert not result.isError
    
    def test_convert_dict_structured(self):
        """Test converting dict to ToolResult with structured content."""
        data = {"key": "value", "number": 42}
        result = _convert_to_tool_result(data)
        
        assert isinstance(result, ToolResult)
        assert result.structuredContent == data
        assert result.content[0].text == "Structured result"
    
    def test_convert_dict_tool_result_like(self):
        """Test converting dict that looks like ToolResult."""
        data = {
            "content": [{"type": "text", "text": "Test message"}],
            "isError": False
        }
        result = _convert_to_tool_result(data)
        
        assert isinstance(result, ToolResult)
        assert result.content[0].text == "Test message"
        assert not result.isError
    
    def test_convert_list(self):
        """Test converting list to ToolResult."""
        data = ["item1", "item2", TextContent(text="item3")]
        result = _convert_to_tool_result(data)
        
        assert isinstance(result, ToolResult)
        assert len(result.content) == 3
        assert result.content[0].text == "item1"
        assert result.content[2].text == "item3"
    
    def test_convert_other_types(self):
        """Test converting other types to ToolResult."""
        result = _convert_to_tool_result(42)
        assert isinstance(result, ToolResult)
        assert result.content[0].text == "42"


class TestExtractDescription:
    """Test _extract_description helper function."""
    
    def test_extract_from_docstring(self):
        """Test extracting description from docstring."""
        def func_with_docs():
            """This is a test function."""
            pass
        
        desc = _extract_description(func_with_docs)
        assert desc == "This is a test function."
    
    def test_extract_multiline_docstring(self):
        """Test extracting from multiline docstring."""
        def func_with_multiline_docs():
            """
            This is the first line.
            
            This is additional detail.
            """
            pass
        
        desc = _extract_description(func_with_multiline_docs)
        assert desc == "This is the first line."
    
    def test_no_docstring(self):
        """Test behavior with no docstring."""
        def func_without_docs():
            pass
        
        desc = _extract_description(func_without_docs)
        assert desc == "Tool: func_without_docs"
    
    def test_empty_docstring(self):
        """Test behavior with empty docstring."""
        def func_with_empty_docs():
            """"""
            pass
        
        desc = _extract_description(func_with_empty_docs)
        assert desc == "Tool: func_with_empty_docs"


class TestBackwardCompatibility:
    """Test backward compatibility features."""
    
    def test_old_attribute_names(self):
        """Test that old attribute names still work."""
        @tool()
        def compat_tool(value: int) -> str:
            return str(value)
        
        # Both new and old attribute names should exist
        assert hasattr(compat_tool, "_mcp_tool")
        assert hasattr(compat_tool, "_mcp_tool_definition")
        assert compat_tool._mcp_tool is compat_tool._mcp_tool_definition
        
        @prompt()
        def compat_prompt(name: str) -> str:
            return f"Hello, {name}"
        
        assert hasattr(compat_prompt, "_mcp_prompt")
        assert hasattr(compat_prompt, "_mcp_prompt_definition")
        assert compat_prompt._mcp_prompt is compat_prompt._mcp_prompt_definition


class TestStructuredOutputMCP2025:
    """Test MCP 2025-06-18 structured output compliance."""
    
    def test_structured_output_schema_generation(self):
        """Test tools with structured_output=True generate proper JSON schemas."""
        from typing import Optional
        
        @tool(structured_output=True)
        def complex_structured_tool(
            name: str, 
            age: int, 
            active: bool = True,
            metadata: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Return complex structured data."""
            return {
                "user": {"name": name, "age": age, "active": active},
                "metadata": metadata or {},
                "timestamp": "2025-06-18T12:00:00Z"
            }
        
        tool_def = complex_structured_tool._mcp_tool
        
        # Verify output schema is generated
        assert tool_def.output_schema is not None
        output_schema = tool_def.output_schema
        
        # Verify schema structure matches return type annotation
        assert output_schema["type"] == "object"
        # Dict[str, Any] correctly generates additionalProperties schema per MCP spec
        assert "additionalProperties" in output_schema
        
        # Test that input schema is still generated correctly
        input_schema = tool_def.schema
        assert input_schema["type"] == "object"
        assert "name" in input_schema["properties"]
        assert "age" in input_schema["properties"]
        assert "active" in input_schema["properties"]
        assert "metadata" in input_schema["properties"]
        
        # Required fields should be correctly identified
        assert "name" in input_schema["required"]
        assert "age" in input_schema["required"]
        assert "active" not in input_schema["required"]  # Has default
        assert "metadata" not in input_schema["required"]  # Optional
    
    def test_structured_output_runtime_validation(self):
        """Test structured output tools validate return data against schema."""
        @tool(structured_output=True)
        def validated_structured_tool(value: int) -> Dict[str, int]:
            """Return validated structured data."""
            if value < 0:
                # Return invalid structure to test validation
                return {"invalid": "not_an_int"}
            return {"result": value, "doubled": value * 2}
        
        tool_def = validated_structured_tool._mcp_tool
        
        # Valid return data should work
        result = validated_structured_tool(value=5)
        assert isinstance(result, ToolResult)
        assert not result.isError
        assert result.structuredContent == {"result": 5, "doubled": 10}
        
        # Invalid return data should be caught by validation
        result = validated_structured_tool(value=-1)
        assert isinstance(result, ToolResult)
        assert result.isError
        assert "validation" in result.content[0].text.lower()
    
    def test_structured_output_response_format(self):
        """Test structured output tools return data in structuredContent field."""
        @tool(structured_output=True)
        def response_format_tool(message: str) -> Dict[str, Any]:
            """Test MCP 2025-06-18 response format."""
            return {
                "message": message,
                "processed": True,
                "metadata": {
                    "version": "2025-06-18",
                    "type": "structured_response"
                }
            }
        
        result = response_format_tool(message="test")
        
        # Verify ToolResult structure
        assert isinstance(result, ToolResult)
        assert not result.isError
        
        # Verify structured content is present
        assert result.structuredContent is not None
        assert result.structuredContent["message"] == "test"
        assert result.structuredContent["processed"] is True
        assert result.structuredContent["metadata"]["version"] == "2025-06-18"
        
        # Verify backward compatibility - regular content should also be present
        assert len(result.content) > 0
        assert isinstance(result.content[0], TextContent)
        assert "Structured result" in result.content[0].text
        
        # Verify MCP 2025-06-18 compliance - both fields present
        assert hasattr(result, 'content')  # Traditional content
        assert hasattr(result, 'structuredContent')  # New structured content
    
    def test_structured_output_backward_compatibility(self):
        """Test backward compatibility with non-structured tools."""
        # Regular tool without structured output
        @tool()
        def regular_tool(name: str) -> ToolResult:
            return ToolResult(content=[TextContent(text=f"Hello, {name}!")])
        
        # Structured output tool
        @tool(structured_output=True)
        def structured_tool(name: str) -> Dict[str, str]:
            return {"greeting": f"Hello, {name}!", "type": "structured"}
        
        # Test regular tool works unchanged
        regular_result = regular_tool(name="World")
        assert isinstance(regular_result, ToolResult)
        assert not regular_result.isError
        assert regular_result.structuredContent is None
        assert regular_result.content[0].text == "Hello, World!"
        
        # Test structured tool works with new format
        structured_result = structured_tool(name="World")
        assert isinstance(structured_result, ToolResult)
        assert not structured_result.isError
        assert structured_result.structuredContent is not None
        assert structured_result.structuredContent["greeting"] == "Hello, World!"
        
        # Test mixed server compatibility - both tool types can coexist
        regular_def = regular_tool._mcp_tool
        structured_def = structured_tool._mcp_tool
        
        assert regular_def.output_schema is None
        assert structured_def.output_schema is not None
        
        # Both should have valid input schemas
        assert regular_def.schema is not None
        assert structured_def.schema is not None
        
        # Client should be able to handle both response formats
        # Regular tool: only content field populated
        assert regular_result.content is not None
        assert regular_result.structuredContent is None
        
        # Structured tool: both content and structuredContent populated
        assert structured_result.content is not None
        assert structured_result.structuredContent is not None
