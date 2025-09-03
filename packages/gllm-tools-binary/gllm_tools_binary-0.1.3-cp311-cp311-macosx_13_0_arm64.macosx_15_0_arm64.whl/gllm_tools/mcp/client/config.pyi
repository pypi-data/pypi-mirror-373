from _typeshed import Incomplete
from typing import Any, Literal, TypedDict

STDIO_TRANSPORT: str
SSE_TRANSPORT: str
STREAMABLE_HTTP_TRANSPORT: str
EncodingErrorHandler: Incomplete

class MCPConfiguration(TypedDict):
    """Base MCP Configuration class. Not intended to be used directly."""
    transport: Literal['stdio', 'sse', 'streamable_http']
    session_kwargs: dict[str, Any] | None

class StdioConfiguration(MCPConfiguration):
    """Configuration for STDIO-based MCP.

    STDIO-based MCP uses the `subprocess` module to execute commands.
    More information can be found here:
    https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#stdio
    """
    transport: Literal['stdio']
    command: str
    args: list[str]
    env: dict[str, str]
    cwd: str
    encoding: str
    encoding_error_handler: EncodingErrorHandler

class SseConfiguration(MCPConfiguration):
    """Configuration for SSE-based MCP.

    The SSE MCP Transport is a deprecated transport that uses Server-Sent
    Events to send messages to the client. More information can be found
    here:
    https://modelcontextprotocol.io/specification/2024-11-05/basic/transports#http-with-sse
    """
    transport: Literal['sse']
    url: str
    headers: dict[str, str]
    timeout: float | None
    sse_read_timeout: float | None

class StreamConfiguration(MCPConfiguration):
    """The configuration for connecting to a Streamable HTTP server.

    The Streamable HTTP server is a HTTP Protocol that replaces the
    Server-Sent Events transport. More information can be found here:
    https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http
    """
    transport: Literal['streamable_http']
    url: str
    headers: dict[str, str]
    timeout: float | None
    sse_read_timeout: float | None
