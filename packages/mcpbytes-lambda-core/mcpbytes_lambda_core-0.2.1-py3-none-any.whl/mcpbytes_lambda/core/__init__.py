"""
mcpbytes-lambda • Core

Transport-agnostic MCP (Model Context Protocol) core for AWS Lambda tools.
Provides the protocol engine, tool/prompt registries, decorators, JSON-Schema
generation from type hints, and error types—without any HTTP/API-Gateway coupling.
"""

from .server import MCPServer
from .types import (
    TextContent,
    ToolResult,
    MCPToolError,
    MCPProtocolError,
    Tool,
    Prompt,
    PromptArgument,
)
from .decorators import tool, prompt
from .adapter import TransportAdapter
from .exceptions import (
    TransportError,
    InvalidRequestError,
    UnsupportedMediaTypeError,
    NotAcceptableError,
    AuthenticationError,
)

__version__ = "0.1.0"
__all__ = [
    "MCPServer",
    "TransportAdapter",
    "TextContent",
    "ToolResult",
    "MCPToolError",
    "MCPProtocolError",
    "Tool",
    "Prompt",
    "PromptArgument",
    "tool",
    "prompt",
    "TransportError",
    "InvalidRequestError",
    "UnsupportedMediaTypeError",
    "NotAcceptableError",
    "AuthenticationError",
]
