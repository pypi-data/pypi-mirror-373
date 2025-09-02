"""
mcpbytes-lambda • Core Protocol

Minimal, transport-agnostic MCP (Model Context Protocol) implementation:
- JSON-RPC 2.0 parsing and envelope construction
- MCP version negotiation and lifecycle management
- Core MCP method routing (initialize, tools/*, prompts/*)
- MCP 2025-06-18 compliant with structured output support

SECURITY MODEL:
- Transport Layer: Validates HTTP headers, auth format, request size
- Protocol Layer: Handles JSON-RPC parsing, routing, basic validation  
- Decorator Layer: Generates schemas, validates parameters against types
- Tool Layer: Business logic validation (developer responsibility)

This layer focuses on protocol correctness and performance. Input validation
is distributed across layers for optimal Lambda cold start performance.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional, Union, Iterable

from .types import (
    RPCRequest,
    MCPErrorCodes,
    MCPProtocolVersions,
    Tool,
    ToolAnnotations,
    ToolDefinition,
    PromptDefinition,
    ToolResult,
    TextContent,
    MCPProtocolError,
)

logger = logging.getLogger(__name__)


class MCPProtocol:
    """
    Lightweight MCP protocol handler optimized for AWS Lambda.
    
    Handles JSON-RPC parsing, MCP version negotiation, and core method routing.
    Designed for minimal overhead and fast cold starts. MCP 2025-06-18 compliant.
    """
    
    JSONRPC_VERSION = "2.0"

    def __init__(self, max_payload_size: int = 1_000_000):
        """
        Initialize protocol handler.
        
        Args:
            max_payload_size: Maximum JSON payload size in bytes (default: 1MB)
        """
        self.max_payload_size = max_payload_size

    # ---------- JSON-RPC parsing (payload pre-validated by transport) ----------

    def parse_payload(self, payload: Union[str, Dict[str, Any]]) -> RPCRequest:
        """
        Parse JSON-RPC 2.0 payload into RPCRequest.
        
        Transport adapters handle HTTP-level validation (headers, auth, encoding).
        This layer focuses on JSON-RPC compliance and basic structure validation.
        
        Args:
            payload: JSON-RPC payload as string or pre-parsed dict
            
        Returns:
            RPCRequest: Parsed and validated JSON-RPC request
            
        Raises:
            MCPProtocolError: For malformed JSON-RPC or oversized payloads
        """
        if isinstance(payload, str):
            # Basic size check to prevent memory exhaustion
            if len(payload) > self.max_payload_size:
                from .types import MCPErrorCodes
                raise MCPProtocolError(
                    MCPErrorCodes.INVALID_REQUEST, 
                    "Request payload too large"
                )
            
            try:
                data = json.loads(payload)
            except json.JSONDecodeError as e:
                logger.debug(f"JSON parse error: {e}")
                raise MCPProtocolError(MCPErrorCodes.PARSE_ERROR, "Invalid JSON")
        else:
            data = payload

        # MCP 2025-06-18: Batch requests explicitly not supported (removed from spec)
        if isinstance(data, list):
            raise MCPProtocolError(MCPErrorCodes.INVALID_REQUEST, "Batch requests not supported")

        if not isinstance(data, dict):
            raise MCPProtocolError(MCPErrorCodes.INVALID_REQUEST, "Invalid JSON-RPC envelope")

        method = data.get("method")
        if not isinstance(method, str):
            raise MCPProtocolError(MCPErrorCodes.INVALID_REQUEST, "Missing or invalid 'method'")

        # Validate JSON-RPC version
        jsonrpc_version = data.get("jsonrpc")
        if jsonrpc_version != "2.0":
            raise MCPProtocolError(MCPErrorCodes.INVALID_REQUEST, "JSON-RPC 2.0 required")

        return RPCRequest(
            method=method,
            id=data.get("id"),
            params=data.get("params", {}) or {},
        )

    # ---------- JSON-RPC envelope builders ----------

    def build_success(self, request_id: Union[str, int, None], result: Dict[str, Any]) -> Dict[str, Any]:
        """Build JSON-RPC 2.0 success response."""
        return {
            "jsonrpc": self.JSONRPC_VERSION,
            "id": request_id,
            "result": result,
        }

    def build_error(
        self,
        request_id: Union[str, int, None],
        code: int,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Build JSON-RPC 2.0 error response."""
        err = {"code": code, "message": message}
        if data is not None:
            err["data"] = data
        return {
            "jsonrpc": self.JSONRPC_VERSION,
            "id": request_id,
            "error": err,
        }

    # ---------- MCP version negotiation ----------

    def negotiate_version(self, method: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Optional[str]:
        """
        Negotiate MCP protocol version based on method, params, and headers.
        
        MCP version negotiation:
        - 'initialize': Use client's requested version if supported, else fallback to current
        - Other methods: Use header version if supported, else fallback
        
        Args:
            method: JSON-RPC method name
            params: JSON-RPC request parameters (for initialize method)
            headers: HTTP headers (case-insensitive dict from adapter)
            
        Returns:
            MCP version string or None if unsupported
        """
        if method == "initialize":
            # Extract client's requested protocol version from initialize params
            if params and isinstance(params, dict):
                requested_version = params.get("protocolVersion")
                if requested_version and requested_version in MCPProtocolVersions.SUPPORTED:
                    return requested_version
            # Fallback to current version if client's version unsupported or missing
            return MCPProtocolVersions.CURRENT

        headers = headers or {}
        version = headers.get("mcp-protocol-version")
        if not version:
            return MCPProtocolVersions.BACKCOMPAT

        version = version.strip()
        return version if version in MCPProtocolVersions.SUPPORTED else None

    # ---------- MCP lifecycle helpers ----------

    def create_initialize_result(
        self,
        server_name: str,
        server_version: str,
        negotiated_protocol_version: str,
        server_description: Optional[str] = None,
        has_tools: bool = False,
        has_prompts: bool = False,
        instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build MCP initialize response with server capabilities.
        
        Advertises available capabilities (tools, prompts) to the client.
        """
        capabilities: Dict[str, Any] = {}
        if has_tools:
            capabilities["tools"] = {"listChanged": False}
        if has_prompts:
            capabilities["prompts"] = {"listChanged": False}

        server_info: Dict[str, Any] = {"name": server_name, "version": server_version}
        if server_description:
            server_info["title"] = server_description

        result: Dict[str, Any] = {
            "protocolVersion": negotiated_protocol_version,
            "capabilities": capabilities,
            "serverInfo": server_info,
        }
        if instructions:
            result["instructions"] = instructions
        return result

    # ---------- Core MCP method routing ----------

    def route(
        self,
        req: RPCRequest,
        *,
        tools: Dict[str, ToolDefinition],
        prompts: Dict[str, PromptDefinition],
        server_name: str,
        server_version: str,
        server_description: Optional[str],
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Route MCP method calls to appropriate handlers.
        
        Supported methods:
        - initialize: Server capability negotiation
        - tools/list: List available tools with schemas
        - tools/call: Execute registered tool function
        - prompts/get: Execute registered prompt template
        
        SECURITY: This layer trusts that:
        - Transport has validated request format and auth
        - Decorators have sanitized function signatures  
        - Tool functions validate their own business logic
        
        Args:
            req: Parsed JSON-RPC request
            tools: Registry of available tools
            prompts: Registry of available prompts  
            server_name: Server identification
            server_version: Server version
            server_description: Optional server description
            headers: HTTP headers for version negotiation
            
        Returns:
            JSON-RPC response dict (success or error)
        """
        # MCP version compatibility check
        version = self.negotiate_version(req.method, params=req.params, headers=headers)
        if version is None:
            logger.warning(f"Unsupported MCP version for method: {req.method}")
            return self.build_error(
                req.id,
                MCPErrorCodes.INVALID_REQUEST,
                "Unsupported MCP protocol version",
            )

        try:
            # Route to method handlers
            if req.method == "initialize":
                return self.build_success(
                    req.id,
                    self.create_initialize_result(
                        server_name=server_name,
                        server_version=server_version,
                        negotiated_protocol_version=version,
                        server_description=server_description,
                        has_tools=bool(tools),
                        has_prompts=bool(prompts),
                    ),
                )

            if req.method == "tools/list":
                return self.build_success(
                    req.id,
                    {"tools": self._serialize_tools(tools.values())},
                )

            if req.method == "tools/call":
                return self._handle_tools_call(req, tools=tools)

            if req.method == "prompts/get":
                return self._handle_prompts_get(req, prompts=prompts)

            # Unknown method
            logger.info(f"Unknown method requested: {req.method}")
            return self.build_error(req.id, MCPErrorCodes.METHOD_NOT_FOUND, f"Unknown method: {req.method}")

        except MCPProtocolError as e:
            # Expected protocol errors - safe to expose message
            logger.info(f"Protocol error in {req.method}: {e.message}")
            return self.build_error(req.id, e.code, e.message, e.data)
        
        except Exception as e:
            # Unexpected errors - log details, return generic message  
            logger.error(f"Internal error in {req.method}: {e}", exc_info=True)
            return self.build_error(req.id, MCPErrorCodes.INTERNAL_ERROR, "Internal server error")

    # ---------- Method implementations ----------

    def _serialize_tools(self, defs: Iterable[ToolDefinition]) -> list[Dict[str, Any]]:
        """Convert ToolDefinition objects to MCP-compliant tool list with structured output support."""
        out: list[Dict[str, Any]] = []
        for d in defs:
            annotations: Optional[ToolAnnotations] = d.annotations
            ann = None
            if annotations:
                ann = {
                    "title": annotations.title,
                    "readOnlyHint": annotations.readOnlyHint,
                    "destructiveHint": annotations.destructiveHint,
                    "idempotentHint": annotations.idempotentHint,
                    "openWorldHint": annotations.openWorldHint,
                }
            
            # Build MCP Tool object with structured output schema (MCP 2025-06-18)
            tool = Tool(
                name=d.name,
                description=d.description,
                title=annotations.title if annotations and annotations.title else None,
                inputSchema=d.schema or {"type": "object"},
                outputSchema=getattr(d, 'output_schema', None),  # MCP 2025-06-18: Include output schema
                annotations=annotations,
            )
            
            # Convert to serializable dict
            obj = {
                "name": tool.name,
                "description": tool.description,
                "title": tool.title,
                "inputSchema": tool.inputSchema,
                "outputSchema": tool.outputSchema,  # MCP 2025-06-18: Output schema for structured tools
                "annotations": ann,
            }
            out.append(obj)
        return out

    def _handle_tools_call(self, req: RPCRequest, *, tools: Dict[str, ToolDefinition]) -> Dict[str, Any]:
        """
        Execute tool function with provided arguments.
        
        SECURITY: Relies on decorator layer for parameter validation.
        Tool functions should validate business logic constraints.
        """
        params = req.params or {}
        name = params.get("name")
        arguments = params.get("arguments", {}) or {}

        # Basic parameter structure validation
        if not isinstance(name, str):
            raise MCPProtocolError(MCPErrorCodes.INVALID_PARAMS, "Missing or invalid 'name' for tools/call")
        if not isinstance(arguments, dict):
            raise MCPProtocolError(MCPErrorCodes.INVALID_PARAMS, "'arguments' must be an object")

        # Look up registered tool
        tool = tools.get(name)
        if not tool:
            raise MCPProtocolError(MCPErrorCodes.METHOD_NOT_FOUND, f"Unknown tool: {name}")

        # Execute tool function - decorators handle parameter validation
        # Tool functions are responsible for business logic validation
        try:
            result = tool.function(**arguments)
            
            if hasattr(result, '__await__'):  # Check if it's a coroutine (faster than inspect)
                import asyncio
                result = asyncio.run(result)
                
        except TypeError as e:
            # Function signature mismatch - likely invalid arguments
            logger.warning(f"Tool {name} parameter error: {e}")
            raise MCPProtocolError(MCPErrorCodes.INVALID_PARAMS, "Invalid tool arguments")

        # Format result according to MCP specification
        if isinstance(result, ToolResult):
            payload = {
                "content": [self._content_to_dict(c) for c in result.content],
                "isError": result.isError,
            }
            # Only include structuredContent for 2025-06-18+ clients
            if result.structuredContent is not None:
                payload["structuredContent"] = result.structuredContent
            if result._meta is not None:
                payload["_meta"] = result._meta
        else:
            # Fallback for simple return types - decorators should normalize
            payload = {
                "content": [{"type": "text", "text": str(result)}],
                "isError": False,
            }

        return self.build_success(req.id, payload)

    def _handle_prompts_get(self, req: RPCRequest, *, prompts: Dict[str, PromptDefinition]) -> Dict[str, Any]:
        """Execute prompt template function."""
        params = req.params or {}
        name = params.get("name")
        arguments = params.get("arguments", {}) or {}

        if not isinstance(name, str):
            raise MCPProtocolError(MCPErrorCodes.INVALID_PARAMS, "Missing or invalid 'name' for prompts/get")
        if not isinstance(arguments, dict):
            raise MCPProtocolError(MCPErrorCodes.INVALID_PARAMS, "'arguments' must be an object")

        prompt = prompts.get(name)
        if not prompt:
            raise MCPProtocolError(MCPErrorCodes.METHOD_NOT_FOUND, f"Unknown prompt: {name}")

        # Execute prompt function - decorators build proper response format
        result_obj = prompt.function(**arguments)
        if not isinstance(result_obj, dict):
            raise MCPProtocolError(MCPErrorCodes.INTERNAL_ERROR, "Prompt returned invalid format")

        return self.build_success(req.id, result_obj)

    # ---------- Utilities ----------

    @staticmethod
    def _content_to_dict(c: TextContent) -> Dict[str, Any]:
        """Convert TextContent to MCP-compliant dict format."""
        out: Dict[str, Any] = {"type": c.type, "text": c.text}
        if c.annotations is not None:
            out["annotations"] = c.annotations
        if c._meta is not None:
            out["_meta"] = c._meta
        return out
