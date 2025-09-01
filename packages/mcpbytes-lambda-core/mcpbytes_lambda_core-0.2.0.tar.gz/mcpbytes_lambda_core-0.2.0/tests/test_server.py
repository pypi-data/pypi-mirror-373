"""
Unit tests for mcpbytes_lambda.core.server module.
"""

import pytest
from mcpbytes_lambda.core.server import MCPServer
from mcpbytes_lambda.core.types import ToolResult, TextContent, ToolDefinition, PromptDefinition


@pytest.fixture
def server():
    """Provide MCPServer instance."""
    return MCPServer(name="test-server", version="1.0.0", description="Test server")


class TestMCPServer:
    """Test MCPServer class."""
    
    def test_server_initialization(self):
        """Test server initialization."""
        server = MCPServer(name="test-server", version="1.0.0")
        
        assert server.name == "test-server"
        assert server.version == "1.0.0"
        assert server.description == "MCP Server: test-server"  # Default description
        assert isinstance(server._tools, dict)
        assert isinstance(server._prompts, dict)
        assert len(server._tools) == 0
        assert len(server._prompts) == 0
    
    def test_server_initialization_with_description(self):
        """Test server initialization with custom description."""
        server = MCPServer(
            name="custom-server",
            version="2.0.0",
            description="A custom server"
        )
        
        assert server.description == "A custom server"
    
    def test_server_initialization_with_log_level(self):
        """Test server initialization with custom log level."""
        server = MCPServer(name="test-server", log_level="DEBUG")
        
        # Logger should be configured (we can't easily test the level without accessing internals)
        assert server._logger is not None


class TestToolRegistration:
    """Test tool registration via decorators."""
    
    def test_tool_registration_basic(self, server):
        """Test basic tool registration."""
        @server.tool(name="test.tool", description="A test tool")
        def test_func(value: int) -> ToolResult:
            return ToolResult(content=[TextContent(text=f"Value: {value}")])
        
        # Check tool is registered
        tools = server.list_tools()
        assert "test.tool" in tools
        assert tools["test.tool"].name == "test.tool"
        assert tools["test.tool"].description == "A test tool"
        assert tools["test.tool"].function == test_func
    
    def test_tool_registration_with_defaults(self, server):
        """Test tool registration with default values."""
        @server.tool()
        def simple_tool(message: str) -> str:
            """A simple tool."""
            return f"Echo: {message}"
        
        tools = server.list_tools()
        assert "simple.tool" in tools  # Name derived from function name
        assert tools["simple.tool"].description == "A simple tool."  # From docstring
    
    def test_tool_registration_with_annotations(self, server):
        """Test tool registration with annotations."""
        @server.tool(read_only=True, idempotent=True, title="Read Tool")
        def read_tool(data: str) -> str:
            return data
        
        tools = server.list_tools()
        tool_def = tools["read.tool"]
        
        assert tool_def.annotations.title == "Read Tool"
        assert tool_def.annotations.readOnlyHint is True
        assert tool_def.annotations.idempotentHint is True
    
    def test_tool_registration_structured_output(self, server):
        """Test tool registration with structured output."""
        @server.tool(structured_output=True)
        def structured_tool(name: str) -> dict:
            """Return structured data."""
            return {"name": name, "processed": True}
        
        tools = server.list_tools()
        tool_def = tools["structured.tool"]
        
        assert tool_def.output_schema is not None
        assert tool_def.output_schema["type"] == "object"
    
    def test_multiple_tool_registration(self, server):
        """Test registering multiple tools."""
        @server.tool()
        def tool_one(value: int) -> str:
            return str(value)
        
        @server.tool()
        def tool_two(message: str) -> str:
            return message.upper()
        
        tools = server.list_tools()
        assert len(tools) == 2
        assert "tool.one" in tools
        assert "tool.two" in tools


class TestPromptRegistration:
    """Test prompt registration via decorators."""
    
    def test_prompt_registration_basic(self, server):
        """Test basic prompt registration."""
        @server.prompt(name="test.prompt", description="A test prompt")
        def test_prompt(name: str) -> str:
            return f"Hello, {name}!"
        
        # Check prompt is registered
        prompts = server.list_prompts()
        assert "test.prompt" in prompts
        assert prompts["test.prompt"].name == "test.prompt"
        assert prompts["test.prompt"].description == "A test prompt"
        assert prompts["test.prompt"].function == test_prompt
    
    def test_prompt_registration_with_defaults(self, server):
        """Test prompt registration with default values."""
        @server.prompt()
        def greeting_prompt(name: str) -> str:
            """Generate a greeting."""
            return f"Hello, {name}!"
        
        prompts = server.list_prompts()
        assert "greeting_prompt" in prompts
        assert prompts["greeting_prompt"].description == "Generate a greeting."
    
    def test_multiple_prompt_registration(self, server):
        """Test registering multiple prompts."""
        @server.prompt()
        def prompt_one(name: str) -> str:
            return f"Hi, {name}"
        
        @server.prompt()
        def prompt_two(topic: str) -> str:
            return f"Let's talk about {topic}"
        
        prompts = server.list_prompts()
        assert len(prompts) == 2
        assert "prompt_one" in prompts
        assert "prompt_two" in prompts


class TestIntrospection:
    """Test server introspection methods."""
    
    def test_list_tools_empty(self, server):
        """Test listing tools when none are registered."""
        tools = server.list_tools()
        assert isinstance(tools, dict)
        assert len(tools) == 0
    
    def test_list_prompts_empty(self, server):
        """Test listing prompts when none are registered."""
        prompts = server.list_prompts()
        assert isinstance(prompts, dict)
        assert len(prompts) == 0
    
    def test_list_tools_returns_copy(self, server):
        """Test that list_tools returns a copy, not the original dict."""
        @server.tool()
        def test_tool(value: int) -> str:
            return str(value)
        
        tools1 = server.list_tools()
        tools2 = server.list_tools()
        
        # Should be equal but not the same object
        assert tools1 == tools2
        assert tools1 is not tools2
        assert tools1 is not server._tools
    
    def test_list_prompts_returns_copy(self, server):
        """Test that list_prompts returns a copy, not the original dict."""
        @server.prompt()
        def test_prompt(name: str) -> str:
            return f"Hello, {name}"
        
        prompts1 = server.list_prompts()
        prompts2 = server.list_prompts()
        
        # Should be equal but not the same object
        assert prompts1 == prompts2
        assert prompts1 is not prompts2
        assert prompts1 is not server._prompts


class TestRequestHandling:
    """Test server request handling."""
    
    def test_handle_initialize_request(self, server, mock_adapter):
        """Test handling initialize request."""
        event = {
            "body": {
                "jsonrpc": "2.0",
                "method": "initialize",
                "id": "1",
                "params": {"protocolVersion": "2025-06-18"}
            }
        }
        
        response = server.handle(event, mock_adapter)
        
        assert response["statusCode"] == 200
        assert response["body"]["jsonrpc"] == "2.0"
        assert response["body"]["id"] == "1"
        assert "result" in response["body"]
        assert response["body"]["result"]["protocolVersion"] == "2025-06-18"
        assert response["body"]["result"]["serverInfo"]["name"] == "test-server"
    
    def test_handle_tools_list_request(self, server, mock_adapter):
        """Test handling tools/list request."""
        # Register a tool first
        @server.tool()
        def sample_tool(value: int) -> str:
            """A sample tool."""
            return str(value)
        
        event = {
            "body": {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": "2"
            }
        }
        
        response = server.handle(event, mock_adapter)
        
        assert response["statusCode"] == 200
        assert response["body"]["id"] == "2"
        assert "result" in response["body"]
        assert "tools" in response["body"]["result"]
        assert len(response["body"]["result"]["tools"]) == 1
        assert response["body"]["result"]["tools"][0]["name"] == "sample.tool"
    
    def test_handle_tools_call_request(self, server, mock_adapter):
        """Test handling tools/call request."""
        # Register a tool first
        @server.tool()
        def add_numbers(a: float, b: float) -> ToolResult:
            """Add two numbers."""
            result = a + b
            return ToolResult(content=[TextContent(text=f"{a} + {b} = {result}")])
        
        event = {
            "body": {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": "3",
                "params": {
                    "name": "add.numbers",
                    "arguments": {"a": 2.5, "b": 3.5}
                }
            }
        }
        
        response = server.handle(event, mock_adapter)
        
        assert response["statusCode"] == 200
        assert response["body"]["id"] == "3"
        assert "result" in response["body"]
        assert "content" in response["body"]["result"]
        assert response["body"]["result"]["isError"] is False
        assert "6.0" in response["body"]["result"]["content"][0]["text"]
    
    def test_handle_prompts_get_request(self, server, mock_adapter):
        """Test handling prompts/get request."""
        # Register a prompt first
        @server.prompt()
        def greeting_prompt(name: str) -> str:
            """Generate a greeting."""
            return f"Hello, {name}! How are you today?"
        
        event = {
            "body": {
                "jsonrpc": "2.0",
                "method": "prompts/get",
                "id": "4",
                "params": {
                    "name": "greeting_prompt",
                    "arguments": {"name": "Alice"}
                }
            }
        }
        
        response = server.handle(event, mock_adapter)
        
        assert response["statusCode"] == 200
        assert response["body"]["id"] == "4"
        assert "result" in response["body"]
        assert "messages" in response["body"]["result"]
    
    def test_handle_invalid_json_request(self, server, mock_adapter):
        """Test handling invalid JSON request."""
        event = {
            "body": '{"invalid": json}'  # Invalid JSON
        }
        
        response = server.handle(event, mock_adapter)
        
        assert response["statusCode"] == 200  # Adapter wraps it
        assert "error" in response["body"]
        assert response["body"]["error"]["code"] == -32700  # Parse error
    
    def test_handle_unknown_method_request(self, server, mock_adapter):
        """Test handling unknown method request."""
        event = {
            "body": {
                "jsonrpc": "2.0",
                "method": "unknown/method",
                "id": "5"
            }
        }
        
        response = server.handle(event, mock_adapter)
        
        assert response["statusCode"] == 200
        assert "error" in response["body"]
        assert response["body"]["error"]["code"] == -32601  # Method not found
        assert "Unknown method" in response["body"]["error"]["message"]
    
    def test_handle_with_headers(self, server, mock_adapter):
        """Test handling request with headers for version negotiation."""
        event = {
            "body": {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": "6"
            }
        }
        headers = {"mcp-protocol-version": "2025-03-26"}
        
        response = server.handle(event, mock_adapter, headers=headers)
        
        assert response["statusCode"] == 200
        assert "result" in response["body"]
    
    def test_handle_protocol_error(self, server, mock_adapter):
        """Test handling protocol-level errors."""
        event = {
            "body": {
                "jsonrpc": "1.0",  # Wrong version
                "method": "test",
                "id": "7"
            }
        }
        
        response = server.handle(event, mock_adapter)
        
        assert response["statusCode"] == 200
        assert "error" in response["body"]
        assert response["body"]["error"]["code"] == -32600  # Invalid request


class TestServerCapabilities:
    """Test server capability advertisement."""
    
    def test_initialize_with_no_capabilities(self, mock_adapter):
        """Test initialize response when no tools/prompts are registered."""
        server = MCPServer(name="empty-server")
        
        event = {
            "body": {
                "jsonrpc": "2.0",
                "method": "initialize",
                "id": "1",
                "params": {"protocolVersion": "2025-06-18"}
            }
        }
        
        response = server.handle(event, mock_adapter)
        
        result = response["body"]["result"]
        assert result["capabilities"] == {}
    
    def test_initialize_with_tools_capability(self, mock_adapter):
        """Test initialize response when tools are registered."""
        server = MCPServer(name="tool-server")
        
        @server.tool()
        def test_tool(value: int) -> str:
            return str(value)
        
        event = {
            "body": {
                "jsonrpc": "2.0",
                "method": "initialize",
                "id": "1",
                "params": {"protocolVersion": "2025-06-18"}
            }
        }
        
        response = server.handle(event, mock_adapter)
        
        result = response["body"]["result"]
        assert "tools" in result["capabilities"]
        assert result["capabilities"]["tools"]["listChanged"] is False
    
    def test_initialize_with_prompts_capability(self, mock_adapter):
        """Test initialize response when prompts are registered."""
        server = MCPServer(name="prompt-server")
        
        @server.prompt()
        def test_prompt(name: str) -> str:
            return f"Hello, {name}"
        
        event = {
            "body": {
                "jsonrpc": "2.0",
                "method": "initialize",
                "id": "1",
                "params": {"protocolVersion": "2025-06-18"}
            }
        }
        
        response = server.handle(event, mock_adapter)
        
        result = response["body"]["result"]
        assert "prompts" in result["capabilities"]
        assert result["capabilities"]["prompts"]["listChanged"] is False
    
    def test_initialize_with_both_capabilities(self, mock_adapter):
        """Test initialize response when both tools and prompts are registered."""
        server = MCPServer(name="full-server")
        
        @server.tool()
        def test_tool(value: int) -> str:
            return str(value)
        
        @server.prompt()
        def test_prompt(name: str) -> str:
            return f"Hello, {name}"
        
        event = {
            "body": {
                "jsonrpc": "2.0",
                "method": "initialize",
                "id": "1",
                "params": {"protocolVersion": "2025-06-18"}
            }
        }
        
        response = server.handle(event, mock_adapter)
        
        result = response["body"]["result"]
        assert "tools" in result["capabilities"]
        assert "prompts" in result["capabilities"]


class TestErrorHandling:
    """Test server error handling."""
    
    def test_handle_adapter_conversion_error(self, server):
        """Test handling errors from adapter conversion."""
        class BadAdapter:
            def to_core_request(self, event):
                raise ValueError("Adapter error")
            
            def from_core_response(self, response):
                return {"statusCode": 500, "body": response}
        
        event = {"body": "test"}
        response = server.handle(event, BadAdapter())
        
        assert response["statusCode"] == 500
        assert "error" in response["body"]
        assert response["body"]["error"]["code"] == -32603  # Internal error
    
    def test_handle_tool_execution_error(self, server, mock_adapter):
        """Test handling tool execution errors."""
        @server.tool()
        def failing_tool() -> str:
            raise ValueError("Tool failed")
        
        event = {
            "body": {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": "1",
                "params": {
                    "name": "failing.tool",
                    "arguments": {}
                }
            }
        }
        
        response = server.handle(event, mock_adapter)
        
        assert response["statusCode"] == 200
        assert "result" in response["body"]
        assert response["body"]["result"]["isError"] is True
        # Error should be wrapped in ToolResult by decorator
