from _typeshed import Incomplete
from contextlib import asynccontextmanager
from gllm_tools.mcp.client.config import EncodingErrorHandler as EncodingErrorHandler, MCPConfiguration as MCPConfiguration, SSE_TRANSPORT as SSE_TRANSPORT, STDIO_TRANSPORT as STDIO_TRANSPORT, SseConfiguration as SseConfiguration, StdioConfiguration as StdioConfiguration, StreamConfiguration as StreamConfiguration
from mcp import ClientSession
from typing import AsyncIterator

logger: Incomplete
DEFAULT_ENCODING: str
DEFAULT_ENCODING_ERROR_HANDLER: EncodingErrorHandler
DEFAULT_HTTP_TIMEOUT: int
DEFAULT_SSE_READ_TIMEOUT: Incomplete
DEFAULT_STREAMABLE_HTTP_TIMEOUT: Incomplete
DEFAULT_STREAMABLE_HTTP_SSE_READ_TIMEOUT: Incomplete

@asynccontextmanager
async def create_session(config: MCPConfiguration) -> AsyncIterator[ClientSession]:
    """Create a new session to an MCP server.

    Args:
        config: MCP configuration
    """
