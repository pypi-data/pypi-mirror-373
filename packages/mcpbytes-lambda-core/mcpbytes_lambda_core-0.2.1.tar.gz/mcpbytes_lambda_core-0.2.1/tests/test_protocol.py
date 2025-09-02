"""
Unit tests for mcpbytes_lambda.core.protocol module.
"""

import pytest
import json
from mcpbytes_lambda.core.protocol import MCPProtocol
from mcpbytes_lambda.core.types import (
    RPCRequest,
    ToolDefinition,
    PromptDefinition,
    ToolResult,
    TextContent,
    MCPProtocolError,
    MCPErrorCodes,
    MCPProtocolVersions,
)


@pytest.fixture
def protocol():
    """Provide MCPProtocol instance."""
    return MCPProtocol()


@pytest.fixture
def sample_tools(sample_tool_function):
    """Provide sample tools registry."""
    tool_def = ToolDefinition(
        name="test.tool",
        description="A test tool",
        function=sample_tool_function,
        schema={"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}, "required": ["a", "b"]}
    )
    return {"test.tool": tool_def}


@pytest.fixture
def sample_prompts(sample_prompt_function):
    """Provide sample prompts registry."""
    prompt_def = PromptDefinition(
        name="test.prompt",
        description="A test prompt",
        function=sample_prompt_function
    )
    return {"test.prompt": prompt_def}


class TestMCPProtocol:
    """Test MCPProtocol class."""


class TestParsePayload:
    """Test parse_payload method."""
    
    def test_parse_valid_json_string(self, protocol):
        """Test parsing valid JSON string payload."""
        payload = '{"jsonrpc": "2.0", "method": "test", "id": "1"}'
        request = protocol.parse_payload(payload)
        
        assert isinstance(request, RPCRequest)
        assert request.method == "test"
        assert request.id == "1"
        assert request.params == {}
    
    def test_parse_dict_payload(self, protocol):
        """Test parsing dict payload."""
        payload = {"jsonrpc": "2.0", "method": "test", "id": "1", "params": {"key": "value"}}
        request = protocol.parse_payload(payload)
        
        assert request.method == "test"
        assert request.id == "1"
        assert request.params == {"key": "value"}
    
    def test_parse_invalid_json(self, protocol):
        """Test parsing invalid JSON."""
        with pytest.raises(MCPProtocolError) as exc_info:
            protocol.parse_payload('{"invalid": json}')
        
        assert exc_info.value.code == MCPErrorCodes.PARSE_ERROR
        assert "Invalid JSON" in exc_info.value.message
    
    def test_parse_oversized_payload(self, protocol):
        """Test parsing oversized payload."""
        large_payload = '{"jsonrpc": "2.0", "method": "test", "data": "' + "x" * 2000000 + '"}'
        
        with pytest.raises(MCPProtocolError) as exc_info:
            protocol.parse_payload(large_payload)
        
        assert exc_info.value.code == MCPErrorCodes.INVALID_REQUEST
        assert "payload too large" in exc_info.value.message
    
    def test_parse_batch_request_rejected(self, protocol):
        """Test that batch requests are rejected."""
        payload = [
            {"jsonrpc": "2.0", "method": "test1", "id": "1"},
            {"jsonrpc": "2.0", "method": "test2", "id": "2"}
        ]
        
        with pytest.raises(MCPProtocolError) as exc_info:
            protocol.parse_payload(payload)
        
        assert exc_info.value.code == MCPErrorCodes.INVALID_REQUEST
        assert "Batch requests not supported" in exc_info.value.message
    
    def test_parse_missing_method(self, protocol):
        """Test parsing request without method."""
        payload = {"jsonrpc": "2.0", "id": "1"}
        
        with pytest.raises(MCPProtocolError) as exc_info:
            protocol.parse_payload(payload)
        
        assert exc_info.value.code == MCPErrorCodes.INVALID_REQUEST
        assert "Missing or invalid 'method'" in exc_info.value.message
    
    def test_parse_wrong_jsonrpc_version(self, protocol):
        """Test parsing request with wrong JSON-RPC version."""
        payload = {"jsonrpc": "1.0", "method": "test", "id": "1"}
        
        with pytest.raises(MCPProtocolError) as exc_info:
            protocol.parse_payload(payload)
        
        assert exc_info.value.code == MCPErrorCodes.INVALID_REQUEST
        assert "JSON-RPC 2.0 required" in exc_info.value.message


class TestResponseBuilders:
    """Test response builder methods."""
    
    def test_build_success(self, protocol):
        """Test building success response."""
        result = {"data": "test"}
        response = protocol.build_success("test-id", result)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "test-id"
        assert response["result"] == result
    
    def test_build_error(self, protocol):
        """Test building error response."""
        response = protocol.build_error("test-id", -32600, "Invalid request")
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "test-id"
        assert response["error"]["code"] == -32600
        assert response["error"]["message"] == "Invalid request"
    
    def test_build_error_with_data(self, protocol):
        """Test building error response with additional data."""
        error_data = {"details": "More info"}
        response = protocol.build_error("test-id", -32600, "Invalid request", error_data)
        
        assert response["error"]["data"] == error_data


class TestVersionNegotiation:
    """Test MCP version negotiation."""
    
    def test_negotiate_initialize_with_supported_version(self, protocol):
        """Test version negotiation during initialize with supported version."""
        params = {"protocolVersion": "2025-03-26"}
        version = protocol.negotiate_version("initialize", params)
        
        assert version == "2025-03-26"
    
    def test_negotiate_initialize_with_unsupported_version(self, protocol):
        """Test version negotiation with unsupported version."""
        params = {"protocolVersion": "1.0.0"}
        version = protocol.negotiate_version("initialize", params)
        
        assert version == MCPProtocolVersions.CURRENT  # Fallback to current
    
    def test_negotiate_initialize_without_version(self, protocol):
        """Test version negotiation without specified version."""
        version = protocol.negotiate_version("initialize", {})
        
        assert version == MCPProtocolVersions.CURRENT
    
    def test_negotiate_other_method_with_header(self, protocol):
        """Test version negotiation for non-initialize method with header."""
        headers = {"mcp-protocol-version": "2025-03-26"}
        version = protocol.negotiate_version("tools/list", headers=headers)
        
        assert version == "2025-03-26"
    
    def test_negotiate_other_method_without_header(self, protocol):
        """Test version negotiation without header."""
        version = protocol.negotiate_version("tools/list")
        
        assert version == MCPProtocolVersions.BACKCOMPAT
    
    def test_negotiate_unsupported_header_version(self, protocol):
        """Test version negotiation with unsupported header version."""
        headers = {"mcp-protocol-version": "0.1.0"}
        version = protocol.negotiate_version("tools/list", headers=headers)
        
        assert version is None


class TestInitializeResponse:
    """Test initialize response creation."""
    
    def test_create_initialize_result_basic(self, protocol):
        """Test creating basic initialize result."""
        result = protocol.create_initialize_result(
            server_name="test-server",
            server_version="1.0.0",
            negotiated_protocol_version="2025-06-18"
        )
        
        assert result["protocolVersion"] == "2025-06-18"
        assert result["serverInfo"]["name"] == "test-server"
        assert result["serverInfo"]["version"] == "1.0.0"
        assert result["capabilities"] == {}
    
    def test_create_initialize_result_with_capabilities(self, protocol):
        """Test creating initialize result with capabilities."""
        result = protocol.create_initialize_result(
            server_name="test-server",
            server_version="1.0.0",
            negotiated_protocol_version="2025-06-18",
            has_tools=True,
            has_prompts=True
        )
        
        assert "tools" in result["capabilities"]
        assert "prompts" in result["capabilities"]
        assert result["capabilities"]["tools"]["listChanged"] is False
        assert result["capabilities"]["prompts"]["listChanged"] is False
    
    def test_create_initialize_result_with_description(self, protocol):
        """Test creating initialize result with server description."""
        result = protocol.create_initialize_result(
            server_name="test-server",
            server_version="1.0.0",
            negotiated_protocol_version="2025-06-18",
            server_description="A test server"
        )
        
        assert result["serverInfo"]["title"] == "A test server"


class TestMethodRouting:
    """Test MCP method routing."""
    
    def test_route_initialize(self, protocol, sample_tools, sample_prompts):
        """Test routing initialize method."""
        request = RPCRequest(method="initialize", id="1", params={"protocolVersion": "2025-06-18"})
        
        response = protocol.route(
            request,
            tools=sample_tools,
            prompts=sample_prompts,
            server_name="test-server",
            server_version="1.0.0",
            server_description="Test server"
        )
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "1"
        assert "result" in response
        assert response["result"]["protocolVersion"] == "2025-06-18"
        assert response["result"]["serverInfo"]["name"] == "test-server"
    
    def test_route_tools_list(self, protocol, sample_tools, sample_prompts):
        """Test routing tools/list method."""
        request = RPCRequest(method="tools/list", id="2")
        
        response = protocol.route(
            request,
            tools=sample_tools,
            prompts=sample_prompts,
            server_name="test-server",
            server_version="1.0.0",
            server_description="Test server"
        )
        
        assert response["id"] == "2"
        assert "result" in response
        assert "tools" in response["result"]
        assert len(response["result"]["tools"]) == 1
        assert response["result"]["tools"][0]["name"] == "test.tool"
    
    def test_route_tools_call(self, protocol, sample_tools, sample_prompts):
        """Test routing tools/call method."""
        request = RPCRequest(
            method="tools/call",
            id="3",
            params={"name": "test.tool", "arguments": {"a": 2.0, "b": 3.0}}
        )
        
        response = protocol.route(
            request,
            tools=sample_tools,
            prompts=sample_prompts,
            server_name="test-server",
            server_version="1.0.0",
            server_description="Test server"
        )
        
        assert response["id"] == "3"
        assert "result" in response
        assert "content" in response["result"]
        assert response["result"]["isError"] is False
    
    def test_route_tools_call_unknown_tool(self, protocol, sample_tools, sample_prompts):
        """Test routing tools/call with unknown tool."""
        request = RPCRequest(
            method="tools/call",
            id="4",
            params={"name": "unknown.tool", "arguments": {}}
        )
        
        response = protocol.route(
            request,
            tools=sample_tools,
            prompts=sample_prompts,
            server_name="test-server",
            server_version="1.0.0",
            server_description="Test server"
        )
        
        assert response["id"] == "4"
        assert "error" in response
        assert response["error"]["code"] == MCPErrorCodes.METHOD_NOT_FOUND
        assert "Unknown tool" in response["error"]["message"]
    
    def test_route_tools_call_invalid_params(self, protocol, sample_tools, sample_prompts):
        """Test routing tools/call with invalid parameters."""
        request = RPCRequest(
            method="tools/call",
            id="5",
            params={"name": "test.tool", "arguments": "invalid"}  # Should be dict
        )
        
        response = protocol.route(
            request,
            tools=sample_tools,
            prompts=sample_prompts,
            server_name="test-server",
            server_version="1.0.0",
            server_description="Test server"
        )
        
        assert response["id"] == "5"
        assert "error" in response
        assert response["error"]["code"] == MCPErrorCodes.INVALID_PARAMS
    
    def test_route_prompts_get(self, protocol, sample_tools, sample_prompts):
        """Test routing prompts/get method."""
        request = RPCRequest(
            method="prompts/get",
            id="6",
            params={"name": "test.prompt", "arguments": {"name": "World"}}
        )
        
        response = protocol.route(
            request,
            tools=sample_tools,
            prompts=sample_prompts,
            server_name="test-server",
            server_version="1.0.0",
            server_description="Test server"
        )
        
        assert response["id"] == "6"
        assert "result" in response
        # Should contain MCP-formatted prompt response
        assert isinstance(response["result"], dict)
    
    def test_route_unknown_method(self, protocol, sample_tools, sample_prompts):
        """Test routing unknown method."""
        request = RPCRequest(method="unknown/method", id="7")
        
        response = protocol.route(
            request,
            tools=sample_tools,
            prompts=sample_prompts,
            server_name="test-server",
            server_version="1.0.0",
            server_description="Test server"
        )
        
        assert response["id"] == "7"
        assert "error" in response
        assert response["error"]["code"] == MCPErrorCodes.METHOD_NOT_FOUND
        assert "Unknown method" in response["error"]["message"]
    
    def test_route_unsupported_version(self, protocol, sample_tools, sample_prompts):
        """Test routing with unsupported MCP version."""
        request = RPCRequest(method="tools/list", id="8")
        headers = {"mcp-protocol-version": "0.1.0"}
        
        response = protocol.route(
            request,
            tools=sample_tools,
            prompts=sample_prompts,
            server_name="test-server",
            server_version="1.0.0",
            server_description="Test server",
            headers=headers
        )
        
        assert response["id"] == "8"
        assert "error" in response
        assert response["error"]["code"] == MCPErrorCodes.INVALID_REQUEST
        assert "Unsupported MCP protocol version" in response["error"]["message"]


class TestToolSerialization:
    """Test tool serialization for tools/list."""
    
    def test_serialize_tools_basic(self, protocol, sample_tool_function):
        """Test basic tool serialization."""
        tool_def = ToolDefinition(
            name="test.tool",
            description="A test tool",
            function=sample_tool_function,
            schema={"type": "object", "properties": {"param": {"type": "string"}}}
        )
        
        serialized = protocol._serialize_tools([tool_def])
        
        assert len(serialized) == 1
        tool = serialized[0]
        assert tool["name"] == "test.tool"
        assert tool["description"] == "A test tool"
        assert tool["inputSchema"]["type"] == "object"
        assert tool["outputSchema"] is None
    
    def test_serialize_tools_with_annotations(self, protocol, sample_tool_function):
        """Test tool serialization with annotations."""
        from mcpbytes_lambda.core.types import ToolAnnotations
        
        annotations = ToolAnnotations(
            title="Test Tool",
            readOnlyHint=True,
            idempotentHint=True
        )
        
        tool_def = ToolDefinition(
            name="test.tool",
            description="A test tool",
            function=sample_tool_function,
            schema={"type": "object"},
            annotations=annotations
        )
        
        serialized = protocol._serialize_tools([tool_def])
        
        tool = serialized[0]
        assert tool["annotations"]["title"] == "Test Tool"
        assert tool["annotations"]["readOnlyHint"] is True
        assert tool["annotations"]["idempotentHint"] is True
        assert tool["annotations"]["destructiveHint"] is False
    
    def test_serialize_tools_with_output_schema(self, protocol, sample_tool_function):
        """Test tool serialization with output schema (MCP 2025-06-18)."""
        output_schema = {"type": "object", "properties": {"result": {"type": "string"}}}
        
        tool_def = ToolDefinition(
            name="structured.tool",
            description="A structured output tool",
            function=sample_tool_function,
            schema={"type": "object"},
            output_schema=output_schema
        )
        
        serialized = protocol._serialize_tools([tool_def])
        
        tool = serialized[0]
        assert tool["outputSchema"] == output_schema


class TestContentConversion:
    """Test content conversion utilities."""
    
    def test_content_to_dict(self, protocol):
        """Test converting TextContent to dict."""
        content = TextContent(text="Hello", annotations={"highlight": True})
        result = protocol._content_to_dict(content)
        
        assert result["type"] == "text"
        assert result["text"] == "Hello"
        assert result["annotations"] == {"highlight": True}
    
    def test_content_to_dict_minimal(self, protocol):
        """Test converting minimal TextContent to dict."""
        content = TextContent(text="Simple")
        result = protocol._content_to_dict(content)
        
        assert result["type"] == "text"
        assert result["text"] == "Simple"
        assert "annotations" not in result
        assert "_meta" not in result


class TestJSONRPCCompliance:
    """Test JSON-RPC 2.0 compliance for MCP specification."""
    
    def test_jsonrpc_error_codes_compliance(self, protocol):
        """Test standard JSON-RPC 2.0 error codes compliance."""
        # Test Parse Error (-32700)
        with pytest.raises(MCPProtocolError) as exc_info:
            protocol.parse_payload('{"invalid": json}')
        assert exc_info.value.code == -32700
        
        # Test Invalid Request (-32600)
        with pytest.raises(MCPProtocolError) as exc_info:
            protocol.parse_payload({"jsonrpc": "1.0", "method": "test"})
        assert exc_info.value.code == -32600
        
        # Test Method Not Found (-32601) via routing
        request = RPCRequest(method="nonexistent/method", id="test")
        response = protocol.route(
            request,
            tools={},
            prompts={},
            server_name="test",
            server_version="1.0.0",
            server_description=None
        )
        assert response["error"]["code"] == -32601
        
        # Test Invalid Params (-32602)
        request = RPCRequest(method="tools/call", id="test", params={"invalid": "structure"})
        response = protocol.route(
            request,
            tools={},
            prompts={},
            server_name="test",
            server_version="1.0.0",
            server_description=None
        )
        assert response["error"]["code"] == -32602
    
    def test_jsonrpc_response_format_compliance(self, protocol):
        """Test JSON-RPC 2.0 response format compliance."""
        # Test successful response format
        result = {"test": "data"}
        response = protocol.build_success("test-id", result)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "test-id"
        assert response["result"] == result
        assert "error" not in response
        
        # Test error response format
        error_response = protocol.build_error("error-id", -32600, "Invalid Request")
        
        assert error_response["jsonrpc"] == "2.0"
        assert error_response["id"] == "error-id"
        assert "result" not in error_response
        assert error_response["error"]["code"] == -32600
        assert error_response["error"]["message"] == "Invalid Request"
    
    def test_batch_request_rejection(self, protocol):
        """Test that MCP servers reject JSON-RPC batch requests."""
        # Single request should work
        single_request = {"jsonrpc": "2.0", "method": "tools/list", "id": "1"}
        parsed = protocol.parse_payload(single_request)
        assert parsed.method == "tools/list"
        
        # Batch request (array) should be rejected
        batch_request = [
            {"jsonrpc": "2.0", "method": "tools/list", "id": "1"},
            {"jsonrpc": "2.0", "method": "initialize", "id": "2"}
        ]
        
        with pytest.raises(MCPProtocolError) as exc_info:
            protocol.parse_payload(batch_request)
        
        assert exc_info.value.code == MCPErrorCodes.INVALID_REQUEST
        assert "Batch requests not supported" in exc_info.value.message


class TestMCPProtocolSpecific:
    """Test MCP protocol specific requirements."""
    
    def test_protocol_version_negotiation(self, protocol):
        """Test MCP protocol version negotiation compliance."""
        # Test initialize with supported version
        supported_version = "2025-06-18"
        params = {"protocolVersion": supported_version}
        negotiated = protocol.negotiate_version("initialize", params)
        assert negotiated == supported_version
        
        # Test initialize with unsupported version falls back
        params = {"protocolVersion": "1.0.0"}
        negotiated = protocol.negotiate_version("initialize", params)
        assert negotiated == MCPProtocolVersions.CURRENT
        
        # Test initialize without version uses current
        negotiated = protocol.negotiate_version("initialize", {})
        assert negotiated == MCPProtocolVersions.CURRENT
        
        # Test non-initialize method with version header
        headers = {"mcp-protocol-version": "2025-06-18"}
        negotiated = protocol.negotiate_version("tools/list", headers=headers)
        assert negotiated == "2025-06-18"
        
        # Test unsupported version in header returns None
        headers = {"mcp-protocol-version": "0.1.0"}
        negotiated = protocol.negotiate_version("tools/list", headers=headers)
        assert negotiated is None
    
    def test_mcp_method_routing(self, protocol, sample_tools, sample_prompts):
        """Test core MCP method routing compliance."""
        # Test initialize method
        request = RPCRequest(method="initialize", id="1", params={"protocolVersion": "2025-06-18"})
        response = protocol.route(
            request,
            tools=sample_tools,
            prompts=sample_prompts,
            server_name="test",
            server_version="1.0.0",
            server_description=None
        )
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "1"
        assert "result" in response
        assert response["result"]["protocolVersion"] == "2025-06-18"
        assert "serverInfo" in response["result"]
        assert "capabilities" in response["result"]
        
        # Test tools/list method
        request = RPCRequest(method="tools/list", id="2")
        response = protocol.route(
            request,
            tools=sample_tools,
            prompts=sample_prompts,
            server_name="test",
            server_version="1.0.0",
            server_description=None
        )
        
        assert response["id"] == "2"
        assert "result" in response
        assert "tools" in response["result"]
        
        # Test tools/call method
        request = RPCRequest(method="tools/call", id="3", params={"name": "test.tool", "arguments": {"a": 1, "b": 2}})
        response = protocol.route(
            request,
            tools=sample_tools,
            prompts=sample_prompts,
            server_name="test",
            server_version="1.0.0",
            server_description=None
        )
        
        assert response["id"] == "3"
        assert "result" in response
        
        # Test prompts/get method
        request = RPCRequest(method="prompts/get", id="4", params={"name": "test.prompt", "arguments": {}})
        response = protocol.route(
            request,
            tools=sample_tools,
            prompts=sample_prompts,
            server_name="test",
            server_version="1.0.0",
            server_description=None
        )
        
        assert response["id"] == "4"
        assert "result" in response
        
        # Test unknown method returns proper error
        request = RPCRequest(method="unknown/method", id="5")
        response = protocol.route(
            request,
            tools=sample_tools,
            prompts=sample_prompts,
            server_name="test",
            server_version="1.0.0",
            server_description=None
        )
        
        assert response["id"] == "5"
        assert "error" in response
        assert response["error"]["code"] == MCPErrorCodes.METHOD_NOT_FOUND
    
    def test_mcp_content_types(self, protocol):
        """Test MCP content types compliance."""
        from mcpbytes_lambda.core.types import (
            TextContent, ResourceLinkContent, ImageContent, 
            AudioContent, EmbeddedResource
        )
        
        # Test TextContent
        text_content = TextContent(text="Hello, world!")
        assert text_content.type == "text"
        assert text_content.text == "Hello, world!"
        
        # Test ResourceLinkContent  
        resource_content = ResourceLinkContent(uri="https://example.com", name="Example")
        assert resource_content.type == "resource"
        assert resource_content.uri == "https://example.com"
        assert resource_content.name == "Example"
        
        # Test ImageContent
        image_content = ImageContent(data="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==", mimeType="image/png")
        assert image_content.type == "image"
        assert image_content.mimeType == "image/png"
        
        # Test AudioContent
        audio_content = AudioContent(data="UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT", mimeType="audio/wav")
        assert audio_content.type == "audio"
        assert audio_content.mimeType == "audio/wav"
        
        # Test EmbeddedResource
        embedded_resource = EmbeddedResource(resource={"uri": "file://test.txt", "name": "Test File"})
        assert embedded_resource.type == "resource"
        assert embedded_resource.resource["uri"] == "file://test.txt"
        
        # Test ToolResult with all content types
        tool_result = ToolResult(content=[text_content, resource_content, image_content, audio_content, embedded_resource], isError=False)
        
        # Verify content types are preserved
        assert len(tool_result.content) == 5
        assert isinstance(tool_result.content[0], TextContent)
        assert isinstance(tool_result.content[1], ResourceLinkContent)
        assert isinstance(tool_result.content[2], ImageContent)
        assert isinstance(tool_result.content[3], AudioContent)
        assert isinstance(tool_result.content[4], EmbeddedResource)
