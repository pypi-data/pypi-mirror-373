"""
mcpbytes-lambda • Stdio Transport Adapter

Ultra-minimal stdio transport for MCP servers. Handles line-delimited JSON-RPC
over stdin/stdout for local MCP server deployment.
"""

from .adapter import StdioAdapter

__all__ = ["StdioAdapter"]
