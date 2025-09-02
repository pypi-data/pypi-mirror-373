"""
mcpbytes-lambda • Stdio Transport Adapter

Production-ready STDIO transport adapter with full MCP protocol compliance.
Supports all MCP versions (2025-06-18, 2025-03-26, 2024-11-05)

ARCHITECTURAL DESIGN:
This adapter implements a clean separation of concerns between transport and protocol layers:

Transport Layer (this module):
- Handles STDIO-specific I/O operations (stdin/stdout)
- Validates transport requirements (line-delimited JSON, no embedded newlines)
- Manages stream encoding and buffering
- Provides graceful shutdown and signal handling

Protocol Layer (mcpbytes-lambda-core):
- Validates JSON-RPC structure (jsonrpc, method, id fields)
- Handles MCP protocol version negotiation
- Routes method calls to appropriate handlers
- Generates protocol-compliant error responses

This separation eliminates validation duplication and ensures each layer has
clear, focused responsibilities while maintaining full MCP protocol compliance.
"""

import json
import sys
import signal
import logging
from typing import Dict, Any, Optional

from mcpbytes_lambda.core.adapter import TransportAdapter
from mcpbytes_lambda.core.exceptions import (
    TransportError,
)
from mcpbytes_lambda.core.types import (
    MCPErrorCodes, 
    MCPProtocolVersions,
    JSONValue,
)
from mcpbytes_lambda.core.server import MCPServer


class StdioAdapter(TransportAdapter):
    """
    Example:
        adapter = StdioAdapter(log_to_stderr=True)
        mcp_server =  MCPServer(<args>)
        adapter.run(mcp_server)
    """

    def __init__(
        self,
        log_to_stderr: bool = True,
        max_line_length: int = 1_000_000,
        encoding: str = "utf-8",
        log_level: str = "INFO",
    ):
        """
        Initialize STDIO adapter with configuration options.
        
        Args:
            log_to_stderr: Enable MCP-compliant logging to stderr
            max_line_length: Maximum line length for memory protection
            encoding: Text encoding for stdin/stdout (default: utf-8)
            log_level: Logging level for stderr output
        """
        self.log_to_stderr = log_to_stderr
        self.max_line_length = max_line_length
        self.encoding = encoding
        self.log_level = log_level
        self._shutdown_requested = False
        
        # Setup stderr logging if enabled
        if self.log_to_stderr:
            self._setup_stderr_logging()

    def _setup_stderr_logging(self) -> None:
        """Setup MCP-compliant stderr logging."""
        self._logger = logging.getLogger("mcpbytes_lambda.stdio")
        if not self._logger.handlers:
            # Create stderr handler that doesn't interfere with stdout JSON-RPC
            handler = logging.StreamHandler(sys.stderr)
            formatter = logging.Formatter(
                "[%(asctime)s] %(levelname)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
        self._logger.setLevel(getattr(logging, self.log_level.upper(), logging.INFO))

    def _log(self, message: str, level: str = "INFO") -> None:
        """Log message to stderr if logging is enabled."""
        if self.log_to_stderr and hasattr(self, '_logger'):
            log_method = getattr(self._logger, level.lower(), self._logger.info)
            log_method(message)

    def to_core_request(self, line: str) -> Dict[str, Any]:
        """
        Convert stdin line to core request with transport-specific validation only.
        
        The core protocol layer handles all JSON-RPC validation (method field,
        jsonrpc version, request structure). This method only validates
        transport-specific concerns for STDIO.
        
        Args:
            line: Raw line from stdin (should be JSON-RPC)
            
        Returns:
            Parsed JSON dict for core protocol layer to validate
            
        Raises:
            TransportError: For transport-specific violations (empty lines, 
                          embedded newlines, oversized lines, invalid JSON)
        """
        # Strip whitespace but preserve the line for validation
        clean_line = line.strip()
        
        # STDIO transport-specific validation only
        if not clean_line:
            raise TransportError("Empty request line", MCPErrorCodes.INVALID_REQUEST)
        
        # Validate line length for memory protection
        if len(clean_line) > self.max_line_length:
            raise TransportError(
                f"Request line too long: {len(clean_line)} > {self.max_line_length}",
                MCPErrorCodes.INVALID_REQUEST
            )
        
        # MCP STDIO requirement: messages MUST NOT contain embedded newlines
        if '\n' in clean_line or '\r' in clean_line:
            raise TransportError(
                "JSON-RPC message contains embedded newlines (MCP STDIO violation)",
                MCPErrorCodes.INVALID_REQUEST
            )
        
        # Parse JSON - let core protocol layer handle all JSON-RPC validation
        try:
            request = json.loads(clean_line)
        except json.JSONDecodeError as e:
            raise TransportError(
                f"Invalid JSON: {e}",
                MCPErrorCodes.PARSE_ERROR
            )
        
        # Log the request method if available (for debugging)
        if isinstance(request, dict) and "method" in request:
            self._log(f"Received request: {request['method']}")
        
        return request

    def from_core_response(self, response: JSONValue) -> str:
        """
        Convert core response to stdout line with validation.
        
        Args:
            response: JSON-RPC response as JSONValue from core
            
        Returns:
            Line-delimited JSON for stdout (with newline)
            
        Raises:
            TransportError: For serialization errors
        """
        try:
            # Serialize to JSON
            json_str = json.dumps(response, ensure_ascii=False, separators=(',', ':'))
            
            # MCP STDIO requirement: validate no embedded newlines
            if '\n' in json_str or '\r' in json_str:
                # This should never happen with proper JSON serialization,
                # but we check to ensure MCP compliance
                raise TransportError(
                    "Response contains embedded newlines (MCP STDIO violation)",
                    MCPErrorCodes.INTERNAL_ERROR
                )
            
            # Add required newline delimiter
            result = json_str + '\n'
            
            # Accurate logging based on JSON-RPC response structure
            if isinstance(response, dict):
                response_id = response.get('id', 'unknown')
                response_type = 'error' if 'error' in response else 'success'
                self._log(f"Sending {response_type} response: {response_id}")
            else:
                self._log(f"Sending response: {response}")
            return result
            
        except (TypeError, ValueError) as e:
            raise TransportError(
                f"Failed to serialize response: {e}",
                MCPErrorCodes.INTERNAL_ERROR
            )

    def run(self, mcp_server: MCPServer) -> None:
        """
        Main STDIO server loop with comprehensive error handling.
        
        Reads JSON-RPC messages from stdin line-by-line, processes them
        through the MCP server, and writes responses to stdout.
        
        Features:
        - Graceful shutdown on SIGTERM/SIGINT
        - Comprehensive error handling and logging
        - Memory-efficient streaming processing
        - MCP protocol compliance validation
        - Proper EOF handling
        
        Args:
            mcp_server: Configured MCP server instance
        """
        self._log("Starting STDIO MCP server", "INFO")
        self._log(f"Server: {mcp_server.name} v{mcp_server.version}", "INFO")
        self._log(f"Supported MCP versions: {', '.join(MCPProtocolVersions.SUPPORTED)}", "INFO")
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
        try:
            # Main processing loop
            while not self._shutdown_requested:
                try:
                    # Read line from stdin with proper encoding
                    line = sys.stdin.readline()
                    
                    # Check for EOF (client closed stdin)
                    if not line:
                        self._log("Received EOF from stdin, shutting down", "INFO")
                        break
                    
                    # Process the request through the MCP server
                    # MCPServer.handle() catches TransportError from to_core_request() and 
                    # converts them to proper JSON-RPC errors using the protocol layer
                    response = mcp_server.handle(
                        event=line,
                        adapter=self,
                        headers=None  # STDIO doesn't use HTTP headers
                    )
                    
                    # Write response to stdout
                    if response:
                        output = self.from_core_response(response)
                        sys.stdout.write(output)
                        sys.stdout.flush()  # Ensure immediate delivery
                        
                except KeyboardInterrupt:
                    self._log("Received KeyboardInterrupt, shutting down", "INFO")
                    break
                    
                except EOFError:
                    self._log("Received EOFError, shutting down", "INFO")
                    break
                    
                except Exception as e:
                    self._log(f"Error in main loop: {e}", "ERROR")
                    # Continue processing unless it's a critical error
                    continue
                    
        except Exception as e:
            self._log(f"Critical error in STDIO server: {e}", "ERROR")
            sys.exit(1)
            
        finally:
            self._log("STDIO MCP server shutting down", "INFO")

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self._log(f"Received signal {signum}, initiating shutdown", "INFO")
            self._shutdown_requested = True
            
        # Handle SIGTERM and SIGINT for graceful shutdown
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
