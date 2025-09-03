from gllm_tools.mcp.client.client import MCPClient as MCPClient
from gllm_tools.mcp.client.config import MCPConfiguration as MCPConfiguration
from gllm_tools.mcp.client.resource import MCPResource as MCPResource
from gllm_tools.mcp.client.session import create_session as create_session
from gllm_tools.mcp.client.tool import MCPTool as MCPTool
from mcp.types import CallToolResult as CallToolResult, EmbeddedResource, ImageContent
from pydantic import AnyUrl as AnyUrl

NonTextContent = ImageContent | EmbeddedResource

class LangchainMCPClient(MCPClient):
    """Langchain MCP Client.

    This client is a wrapper around the MCPClient that converts MCP tools and resources
    into Langchain tools and resources. It is used to integrate MCP with Langchain.
    """
    RESOURCE_FETCH_TIMEOUT: int
