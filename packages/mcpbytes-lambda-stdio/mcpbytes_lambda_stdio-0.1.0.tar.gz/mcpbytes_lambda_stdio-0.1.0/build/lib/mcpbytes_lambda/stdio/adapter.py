"""
mcpbytes-lambda • Stdio Transport Adapter
"""

import json
from typing import Dict, Any

from mcpbytes_lambda.core.adapter import TransportAdapter


class StdioAdapter(TransportAdapter):
    """
    Minimal stdio transport adapter for local MCP servers.
    """

    def to_core_request(self, line: str) -> str:
        """
        Convert stdin line to core request.
        
        Args:
            line: Raw line from stdin (already JSON-RPC)
            
        Returns:
            JSON-RPC string for core protocol handler
        """
        return line.strip()

    def from_core_response(self, response: Dict[str, Any]) -> str:
        """
        Convert core response to stdout line.
        
        Args:
            response: JSON-RPC response dict from core
            
        Returns:
            Line-delimited JSON for stdout
        """
        return json.dumps(response) + '\n'
