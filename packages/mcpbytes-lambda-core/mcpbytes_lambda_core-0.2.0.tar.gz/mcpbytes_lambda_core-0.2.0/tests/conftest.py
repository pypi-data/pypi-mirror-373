"""
Shared pytest fixtures for mcpbytes-lambda-core tests.
"""

import pytest
from typing import Dict, Any
from mcpbytes_lambda.core.types import TextContent, ToolResult
from mcpbytes_lambda.core.adapter import TransportAdapter


class MockTransportAdapter:
    """Mock transport adapter for testing."""
    
    def to_core_request(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Convert mock event to JSON-RPC payload."""
        return event.get("body", {})
    
    def from_core_response(self, rpc_response: Dict[str, Any]) -> Dict[str, Any]:
        """Convert JSON-RPC response to mock transport response."""
        return {
            "statusCode": 200,
            "body": rpc_response
        }


@pytest.fixture
def mock_adapter():
    """Provide a mock transport adapter."""
    return MockTransportAdapter()


@pytest.fixture
def sample_text_content():
    """Provide a sample TextContent instance."""
    return TextContent(text="Hello, world!")


@pytest.fixture
def sample_tool_result():
    """Provide a sample ToolResult instance."""
    return ToolResult(
        content=[TextContent(text="Test result")],
        isError=False
    )


@pytest.fixture
def sample_jsonrpc_request():
    """Provide a sample JSON-RPC request."""
    return {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": "test-1"
    }


@pytest.fixture
def sample_tool_function():
    """Provide a simple tool function for testing."""
    def add_numbers(a: float, b: float) -> ToolResult:
        """Add two numbers."""
        result = a + b
        return ToolResult(
            content=[TextContent(text=f"{a} + {b} = {result}")],
            isError=False
        )
    return add_numbers


@pytest.fixture
def sample_prompt_function():
    """Provide a simple prompt function for testing."""
    from mcpbytes_lambda.core.decorators import prompt
    
    @prompt()
    def greeting_prompt(name: str) -> str:
        """Generate a greeting prompt."""
        return f"Hello, {name}! How can I help you today?"
    return greeting_prompt
