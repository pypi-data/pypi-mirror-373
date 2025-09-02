"""
mcpbytes-lambda • Core Server

Transport-agnostic MCP server:
- Holds tool/prompt registries
- Exposes ergonomic @tool / @prompt registration helpers
- Routes JSON-RPC requests via MCPProtocol
- Delegates event/HTTP shaping to a TransportAdapter
- MCP 2025-06-18 compliant with structured output support

This module has *no* dependency on API Gateway, ALB, or any HTTP envelope.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional

from .types import (
    ToolDefinition,
    PromptDefinition,
    MCPProtocolError,
)
from .protocol import MCPProtocol
from .adapter import TransportAdapter
from .decorators import tool as tool_decorator
from .decorators import prompt as prompt_decorator
from .exceptions import TransportError


class MCPServer:
    """
    Minimal, transport-agnostic MCP server core with MCP 2025-06-18 compliance.

    Example:
        # Default (1MB) - works across all transports
        mcp = MCPServer(name="extract-pdf", version="1.0.0")

        # API Gateway optimized (10MB)
        mcp = MCPServer(name="api-server", max_payload_size=10_000_000)

        # Stdio unlimited
        mcp = MCPServer(name="stdio-server", max_payload_size=100_000_000)

        @mcp.tool(name="extract.pdf", read_only=True, idempotent=True)
        async def extract_pdf(url: str, max_length: int = 15000) -> ToolResult:
            ...

        @mcp.tool(name="structured.data", structured_output=True)
        def get_data(id: str) -> Dict[str, Any]:  # Schema auto-generated
            return {"id": id, "value": 42}

        def lambda_handler(event, context):
            # Import transport adapter based on your deployment
            # from mcpbytes_lambda.apigw import ApiGatewayAdapter  # For API Gateway
            # from mcpbytes_lambda.stdio import StdioAdapter      # For stdio transport
            adapter = get_transport_adapter()  # Your adapter selection logic
            return mcp.handle(event, adapter, headers=event.get("headers"))
    """

    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        description: Optional[str] = None,
        log_level: str = "INFO",
        max_payload_size: int = 1_000_000,
    ):
        self.name = name
        self.version = version
        self.description = description or f"MCP Server: {name}"

        self._protocol = MCPProtocol(max_payload_size=max_payload_size)
        self._tools: Dict[str, ToolDefinition] = {}
        self._prompts: Dict[str, PromptDefinition] = {}

        # logging
        self._logger = logging.getLogger(f"mcpbytes_lambda.core.{name}")
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
        self._logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # -------------------------
    # Registration helpers
    # -------------------------

    def tool(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        title: Optional[str] = None,
        read_only: bool = False,
        destructive: bool = False,
        idempotent: bool = False,
        open_world: bool = True,
        structured_output: bool = False,  # MCP 2025-06-18: Structured output support
    ):
        """
        Decorator that applies the core @tool decorator and auto-registers the tool
        into this server's registry. MCP 2025-06-18 compliant.
        
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
        def _decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            decorated = tool_decorator(
                name=name,
                description=description,
                title=title,
                read_only=read_only,
                destructive=destructive,
                idempotent=idempotent,
                open_world=open_world,
                structured_output=structured_output,  # Pass through structured output flag
            )(func)

            tool_def: ToolDefinition = getattr(decorated, "_mcp_tool", None)
            if not tool_def:
                # Back-compat attribute name
                tool_def = getattr(decorated, "_mcp_tool_definition", None)
            if not tool_def:
                raise RuntimeError("Tool decorator did not attach _mcp_tool definition")

            self._tools[tool_def.name] = tool_def
            return decorated

        return _decorator

    def prompt(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        title: Optional[str] = None,
    ):
        """
        Decorator that applies the core @prompt decorator and auto-registers
        the prompt into this server's registry.
        """
        def _decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            decorated = prompt_decorator(
                name=name,
                description=description,
                title=title,
            )(func)

            prompt_def: PromptDefinition = getattr(decorated, "_mcp_prompt", None)
            if not prompt_def:
                # Back-compat attribute name
                prompt_def = getattr(decorated, "_mcp_prompt_definition", None)
            if not prompt_def:
                raise RuntimeError("Prompt decorator did not attach _mcp_prompt definition")

            self._prompts[prompt_def.name] = prompt_def
            return decorated

        return _decorator

    # -------------------------
    # Introspection
    # -------------------------

    def list_tools(self) -> Dict[str, ToolDefinition]:
        """Return copy of registered tools dictionary."""
        return dict(self._tools)

    def list_prompts(self) -> Dict[str, PromptDefinition]:
        """Return copy of registered prompts dictionary."""
        return dict(self._prompts)

    # -------------------------
    # Request handling
    # -------------------------

    def handle(
        self,
        event: Dict[str, Any],
        adapter: TransportAdapter,
        *,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Main entrypoint: convert a transport event into a JSON-RPC request,
        route it via MCPProtocol, and let the adapter convert the JSON-RPC
        response back to a transport response.

        MCP 2025-06-18 compliant with structured output support.

        Args:
            event: Raw event (e.g., API Gateway Lambda event)
            adapter: Provides to_core_request / from_core_response methods
            headers: Optional header dict for MCP version negotiation
                    (adapters may pass event.get("headers"))
                    
        Returns:
            Transport-specific response dict ready for Lambda return
        """
        # Convert transport event into a JSON-RPC payload (str|dict)
        try:
            payload = adapter.to_core_request(event)
        except TransportError as e:
            # Convert transport errors to JSON-RPC errors
            from .types import MCPErrorCodes
            rpc_error = self._protocol.build_error(
                request_id=None, code=e.error_code, message=e.message
            )
            return adapter.from_core_response(rpc_error)
        except Exception as e:  # noqa: BLE001
            from .types import MCPErrorCodes
            rpc_error = self._protocol.build_error(
                request_id=None, code=MCPErrorCodes.INTERNAL_ERROR, message="Internal server error"
            )
            return adapter.from_core_response(rpc_error)

        # Parse JSON-RPC request
        try:
            req = self._protocol.parse_payload(payload)
        except MCPProtocolError as e:
            rpc_error = self._protocol.build_error(
                request_id=None, code=e.code, message=e.message, data=e.data
            )
            return adapter.from_core_response(rpc_error)
        except Exception as e:  # noqa: BLE001
            from .types import MCPErrorCodes
            rpc_error = self._protocol.build_error(
                request_id=None, code=MCPErrorCodes.INTERNAL_ERROR, message=f"Internal error: {e}"
            )
            return adapter.from_core_response(rpc_error)

        # Route and execute with MCP 2025-06-18 support
        rpc_response = self._protocol.route(
            req,
            tools=self._tools,
            prompts=self._prompts,
            server_name=self.name,
            server_version=self.version,
            server_description=self.description,
            headers=headers,
        )

        # Convert back to transport response
        return adapter.from_core_response(rpc_response)
