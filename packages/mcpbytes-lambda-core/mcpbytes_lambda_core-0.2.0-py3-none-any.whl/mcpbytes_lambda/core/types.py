"""
mcpbytes-lambda • Core Types

Shared dataclasses and exceptions for the transport-agnostic MCP core.
These types model MCP 2025-06-18 content blocks, tool/prompt metadata,
JSON-RPC request parsing, and error surfaces.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Callable


# ========= MCP Content & Results =========

@dataclass
class TextContent:
    """Text content block as defined by MCP."""
    type: str = "text"
    text: str = ""
    annotations: Optional[Dict[str, Any]] = None
    _meta: Optional[Dict[str, Any]] = None


@dataclass
class ResourceLinkContent:
    """Resource link content block - MCP 2025-06-18."""
    type: str = "resource"
    uri: str = ""
    name: Optional[str] = None
    annotations: Optional[Dict[str, Any]] = None
    _meta: Optional[Dict[str, Any]] = None


@dataclass
class ImageContent:
    """Image content block - MCP 2025-06-18."""
    type: str = "image"
    data: str = ""  # base64 encoded image data
    mimeType: str = ""  # e.g., "image/png", "image/jpeg"
    annotations: Optional[Dict[str, Any]] = None
    _meta: Optional[Dict[str, Any]] = None


@dataclass
class AudioContent:
    """Audio content block - MCP 2025-06-18."""
    type: str = "audio"
    data: str = ""  # base64 encoded audio data
    mimeType: str = ""  # e.g., "audio/wav", "audio/mp3"
    annotations: Optional[Dict[str, Any]] = None
    _meta: Optional[Dict[str, Any]] = None


@dataclass
class EmbeddedResource:
    """Embedded resource content block - MCP 2025-06-18."""
    type: str = "resource"
    resource: Dict[str, Any] = field(default_factory=dict)  # Full resource object
    annotations: Optional[Dict[str, Any]] = None
    _meta: Optional[Dict[str, Any]] = None


@dataclass
class ToolResult:
    """
    MCP-compliant tool result with structured output support.

    The core/tool layer returns ToolResult; transport/adapters wrap it
    into JSON-RPC responses as needed. MCP 2025-06-18 compliant.
    """
    content: List[Union[TextContent, ResourceLinkContent, ImageContent, AudioContent, EmbeddedResource]]
    isError: bool = False
    structuredContent: Optional[Dict[str, Any]] = None
    _meta: Optional[Dict[str, Any]] = None


# ========= Public Tool/Prompt Metadata (surfaced via tools/list, prompts/get) =========

@dataclass
class ToolAnnotations:
    """
    MCP tool behavior hints for client optimization.
    
    These are advisory only - clients should not rely on them for security.
    Actual tool behavior is determined by implementation, not hints.
    """
    title: Optional[str] = None
    readOnlyHint: bool = False
    destructiveHint: bool = False
    idempotentHint: bool = False
    openWorldHint: bool = True


@dataclass
class Tool:
    """Public MCP Tool descriptor with MCP 2025-06-18 structured output support."""
    name: str
    description: Optional[str] = None
    title: Optional[str] = None
    inputSchema: Dict[str, Any] = field(default_factory=lambda: {"type": "object"})
    outputSchema: Optional[Dict[str, Any]] = None  # MCP 2025-06-18: Structured output schema
    annotations: Optional[ToolAnnotations] = None
    _meta: Optional[Dict[str, Any]] = None


@dataclass
class PromptArgument:
    """Argument descriptor for prompt templates."""
    name: str
    description: Optional[str] = None
    title: Optional[str] = None
    required: bool = False


@dataclass
class Prompt:
    """Public MCP Prompt descriptor."""
    name: str
    description: Optional[str] = None
    title: Optional[str] = None
    arguments: Optional[List[PromptArgument]] = None
    _meta: Optional[Dict[str, Any]] = None


# ========= Internal/Core Definitions =========

@dataclass
class RPCRequest:
    """Parsed JSON-RPC request used internally by the protocol router."""
    method: str
    id: Union[str, int, None]
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolDefinition:
    """Internal tool registration with structured output support."""
    name: str
    description: str
    function: Callable[..., Any]
    schema: Dict[str, Any]
    annotations: Optional[ToolAnnotations] = None
    output_schema: Optional[Dict[str, Any]] = None  # MCP 2025-06-18: For structured output


@dataclass
class PromptDefinition:
    """Internal prompt registration (function reference + args)."""
    name: str
    description: str
    function: Callable[..., Any]
    arguments: Optional[List[PromptArgument]] = None


# ========= Exceptions =========

class MCPToolError(Exception):
    """
    Tool-level errors that should be surfaced in-band to the LLM
    as ToolResult(isError=True), not as JSON-RPC protocol errors.
    """
    pass


class MCPProtocolError(Exception):
    """
    Protocol-level errors that map to JSON-RPC error objects.
    """
    def __init__(self, code: int, message: str, data: Optional[Dict[str, Any]] = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)


# ========= Constants =========

class MCPErrorCodes:
    """JSON-RPC error codes used by MCP."""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


class MCPProtocolVersions:
    """MCP protocol versions - updated for 2025-06-18."""
    CURRENT = "2025-06-18"  # Latest specification
    BACKCOMPAT = "2025-03-26"  # Previous major version
    SUPPORTED = {"2025-06-18", "2025-03-26", "2024-11-05"}  # Supported versions


class EnvironmentVars:
    """Core environment variables (transport-agnostic)."""
    MCP_DEBUG = "MCP_DEBUG"
    LOG_LEVEL = "LOG_LEVEL"
    MAX_PAYLOAD_SIZE = "MCP_MAX_PAYLOAD_SIZE"


class CoreDefaults:
    """Core default values (transport-agnostic)."""
    MAX_PAYLOAD_SIZE = 1_000_000
    LOG_LEVEL = "INFO"


# ========= Type Aliases =========

# MCP 2025-06-18: Extended content block support
ContentBlock = Union[TextContent, ResourceLinkContent, ImageContent, AudioContent, EmbeddedResource]

# Standard JSON value types
JSONValue = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]

# Tool function type for better type hints
ToolFunction = Callable[..., Union[str, ToolResult, List[ContentBlock]]]

# Prompt function type for better type hints  
PromptFunction = Callable[..., Union[str, Dict[str, Any]]]
