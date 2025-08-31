# mcpbytes_lambda/core/adapter.py
# Clean, minimal interface that enables pluggability
from typing import Protocol, Dict, Any

class TransportAdapter(Protocol):
    def to_core_request(self, event: Dict[str, Any]) -> Dict[str, Any]: ...
    def from_core_response(self, rpc_response: Dict[str, Any]) -> Dict[str, Any]: ...
