"""
Unit tests for mcpbytes_lambda.core.types module.
"""

import pytest
from mcpbytes_lambda.core.types import (
    TextContent,
    ResourceLinkContent,
    ToolResult,
    ToolAnnotations,
    Tool,
    Prompt,
    PromptArgument,
    RPCRequest,
    ToolDefinition,
    PromptDefinition,
    MCPToolError,
    MCPProtocolError,
    MCPErrorCodes,
    MCPProtocolVersions,
)


class TestTextContent:
    """Test TextContent dataclass."""
    
    def test_default_creation(self):
        """Test creating TextContent with defaults."""
        content = TextContent()
        assert content.type == "text"
        assert content.text == ""
        assert content.annotations is None
        assert content._meta is None
    
    def test_with_text(self):
        """Test creating TextContent with text."""
        content = TextContent(text="Hello, world!")
        assert content.type == "text"
        assert content.text == "Hello, world!"
    
    def test_with_annotations(self):
        """Test creating TextContent with annotations."""
        annotations = {"highlight": True}
        content = TextContent(text="Test", annotations=annotations)
        assert content.annotations == annotations


class TestResourceLinkContent:
    """Test ResourceLinkContent dataclass."""
    
    def test_default_creation(self):
        """Test creating ResourceLinkContent with defaults."""
        content = ResourceLinkContent()
        assert content.type == "resource"
        assert content.uri == ""
        assert content.name is None
    
    def test_with_uri(self):
        """Test creating ResourceLinkContent with URI."""
        content = ResourceLinkContent(uri="https://example.com/resource")
        assert content.uri == "https://example.com/resource"


class TestToolResult:
    """Test ToolResult dataclass."""
    
    def test_creation_with_content(self, sample_text_content):
        """Test creating ToolResult with content."""
        result = ToolResult(content=[sample_text_content])
        assert len(result.content) == 1
        assert result.content[0] == sample_text_content
        assert result.isError is False
        assert result.structuredContent is None
    
    def test_error_result(self):
        """Test creating error ToolResult."""
        content = TextContent(text="Error occurred")
        result = ToolResult(content=[content], isError=True)
        assert result.isError is True
    
    def test_structured_content(self):
        """Test ToolResult with structured content."""
        structured_data = {"key": "value", "number": 42}
        result = ToolResult(
            content=[TextContent(text="Structured result")],
            structuredContent=structured_data
        )
        assert result.structuredContent == structured_data


class TestToolAnnotations:
    """Test ToolAnnotations dataclass."""
    
    def test_default_creation(self):
        """Test creating ToolAnnotations with defaults."""
        annotations = ToolAnnotations()
        assert annotations.title is None
        assert annotations.readOnlyHint is False
        assert annotations.destructiveHint is False
        assert annotations.idempotentHint is False
        assert annotations.openWorldHint is True
    
    def test_with_values(self):
        """Test creating ToolAnnotations with specific values."""
        annotations = ToolAnnotations(
            title="Test Tool",
            readOnlyHint=True,
            idempotentHint=True
        )
        assert annotations.title == "Test Tool"
        assert annotations.readOnlyHint is True
        assert annotations.idempotentHint is True


class TestTool:
    """Test Tool dataclass."""
    
    def test_creation(self):
        """Test creating Tool."""
        tool = Tool(name="test.tool", description="A test tool")
        assert tool.name == "test.tool"
        assert tool.description == "A test tool"
        assert tool.inputSchema == {"type": "object"}
        assert tool.outputSchema is None
    
    def test_with_schemas(self):
        """Test creating Tool with schemas."""
        input_schema = {"type": "object", "properties": {"param": {"type": "string"}}}
        output_schema = {"type": "object", "properties": {"result": {"type": "string"}}}
        
        tool = Tool(
            name="test.tool",
            inputSchema=input_schema,
            outputSchema=output_schema
        )
        assert tool.inputSchema == input_schema
        assert tool.outputSchema == output_schema


class TestPrompt:
    """Test Prompt dataclass."""
    
    def test_creation(self):
        """Test creating Prompt."""
        prompt = Prompt(name="test.prompt", description="A test prompt")
        assert prompt.name == "test.prompt"
        assert prompt.description == "A test prompt"
        assert prompt.arguments is None
    
    def test_with_arguments(self):
        """Test creating Prompt with arguments."""
        arg = PromptArgument(name="name", required=True)
        prompt = Prompt(name="test.prompt", arguments=[arg])
        assert len(prompt.arguments) == 1
        assert prompt.arguments[0].name == "name"


class TestPromptArgument:
    """Test PromptArgument dataclass."""
    
    def test_creation(self):
        """Test creating PromptArgument."""
        arg = PromptArgument(name="test_arg")
        assert arg.name == "test_arg"
        assert arg.description is None
        assert arg.required is False
    
    def test_required_argument(self):
        """Test creating required PromptArgument."""
        arg = PromptArgument(name="required_arg", required=True)
        assert arg.required is True


class TestRPCRequest:
    """Test RPCRequest dataclass."""
    
    def test_creation(self):
        """Test creating RPCRequest."""
        request = RPCRequest(method="test.method", id="test-1")
        assert request.method == "test.method"
        assert request.id == "test-1"
        assert request.params == {}
    
    def test_with_params(self):
        """Test creating RPCRequest with parameters."""
        params = {"arg1": "value1", "arg2": 42}
        request = RPCRequest(method="test.method", id="test-1", params=params)
        assert request.params == params


class TestToolDefinition:
    """Test ToolDefinition dataclass."""
    
    def test_creation(self, sample_tool_function):
        """Test creating ToolDefinition."""
        schema = {"type": "object", "properties": {"a": {"type": "number"}}}
        definition = ToolDefinition(
            name="test.tool",
            description="Test tool",
            function=sample_tool_function,
            schema=schema
        )
        assert definition.name == "test.tool"
        assert definition.function == sample_tool_function
        assert definition.schema == schema
        assert definition.output_schema is None


class TestPromptDefinition:
    """Test PromptDefinition dataclass."""
    
    def test_creation(self, sample_prompt_function):
        """Test creating PromptDefinition."""
        definition = PromptDefinition(
            name="test.prompt",
            description="Test prompt",
            function=sample_prompt_function
        )
        assert definition.name == "test.prompt"
        assert definition.function == sample_prompt_function
        assert definition.arguments is None


class TestExceptions:
    """Test exception classes."""
    
    def test_mcp_tool_error(self):
        """Test MCPToolError exception."""
        error = MCPToolError("Tool failed")
        assert str(error) == "Tool failed"
        assert isinstance(error, Exception)
    
    def test_mcp_protocol_error(self):
        """Test MCPProtocolError exception."""
        error = MCPProtocolError(code=-32600, message="Invalid request")
        assert error.code == -32600
        assert error.message == "Invalid request"
        assert error.data is None
        assert str(error) == "Invalid request"
    
    def test_mcp_protocol_error_with_data(self):
        """Test MCPProtocolError with data."""
        data = {"details": "More info"}
        error = MCPProtocolError(code=-32600, message="Invalid request", data=data)
        assert error.data == data


class TestConstants:
    """Test constant values."""
    
    def test_error_codes(self):
        """Test MCPErrorCodes constants."""
        assert MCPErrorCodes.PARSE_ERROR == -32700
        assert MCPErrorCodes.INVALID_REQUEST == -32600
        assert MCPErrorCodes.METHOD_NOT_FOUND == -32601
        assert MCPErrorCodes.INVALID_PARAMS == -32602
        assert MCPErrorCodes.INTERNAL_ERROR == -32603
    
    def test_protocol_versions(self):
        """Test MCPProtocolVersions constants."""
        assert MCPProtocolVersions.CURRENT == "2025-06-18"
        assert MCPProtocolVersions.BACKCOMPAT == "2025-03-26"
        assert "2025-06-18" in MCPProtocolVersions.SUPPORTED
        assert "2025-03-26" in MCPProtocolVersions.SUPPORTED
        assert "2024-11-05" in MCPProtocolVersions.SUPPORTED
