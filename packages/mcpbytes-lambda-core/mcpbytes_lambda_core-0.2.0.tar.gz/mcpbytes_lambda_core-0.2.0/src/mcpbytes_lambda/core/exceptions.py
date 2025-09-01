"""Transport layer exceptions for MCP Lambda adapters."""

from typing import Optional
from .types import MCPErrorCodes


class TransportError(Exception):
    """Base exception for transport layer errors."""
    
    def __init__(self, message: str, error_code: int = MCPErrorCodes.INTERNAL_ERROR):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class InvalidRequestError(TransportError):
    """Request format is invalid for this transport."""
    
    def __init__(self, message: str = "Invalid request format"):
        super().__init__(message, MCPErrorCodes.INVALID_REQUEST)


class UnsupportedMediaTypeError(TransportError):
    """Content-Type not supported by this transport."""
    
    def __init__(self, content_type: Optional[str] = None):
        message = f"Unsupported Content-Type: {content_type}" if content_type else "Unsupported Content-Type"
        super().__init__(message, MCPErrorCodes.PARSE_ERROR)


class NotAcceptableError(TransportError):
    """Accept header requirements cannot be satisfied."""
    
    def __init__(self, accept_header: Optional[str] = None):
        message = f"Cannot satisfy Accept header: {accept_header}" if accept_header else "Cannot satisfy Accept header requirements"
        super().__init__(message, MCPErrorCodes.INVALID_PARAMS)


class AuthenticationError(TransportError):
    """Authentication failed."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, MCPErrorCodes.INVALID_PARAMS)
