from _typeshed import Incomplete
from abc import ABC
from gllm_tools.mcp.client.config import MCPConfiguration as MCPConfiguration
from gllm_tools.mcp.client.resource import MCPResource as MCPResource, load_mcp_resources as load_mcp_resources
from gllm_tools.mcp.client.session import create_session as create_session
from gllm_tools.mcp.client.tool import MCPTool as MCPTool, load_mcp_tools as load_mcp_tools
from typing import Any

logger: Incomplete

class MCPClient(ABC):
    """The MCP (Model Context Protocol) Client handler.

    Responsible for creating MCP client sessions, managing its lifecycle, and
    connecting generating the tools, resources, and all server features MCP
    has to offer.

    Attributes:
        servers: A dictionary of MCP server configurations.
    """
    servers: dict[str, MCPConfiguration]
    def __init__(self, servers: dict[str, MCPConfiguration]) -> None:
        """Creates a new MCP client.

        Args:
            servers (dict[str, MCPConfiguration]): A dictionary of MCP server
                configurations.

        Example: how to get the tools from the MCP servers.

        ```python
        client = MCPClient(servers)
        tools = await client.get_tools()
        ```
        """
    def get_servers(self) -> list[str]:
        '''Returns a list of available MCP servers.

        This function retrieves the names of the available MCP servers from the
        MCP servers configuration dictionary.

        Returns:
            list[str]: A list of available MCP servers.

        Example: getting the available MCP servers:

        ```python
        servers = {
            "github": MCPConfiguration(...),
            "slack": MCPConfiguration(...),
        }
        client = MCPClient(servers)
        servers = await client.get_servers()
        print(servers)
        # Output: ["github", "slack"]
        ```
        '''
    async def get_tools(self, server: str | None = None) -> list[MCPTool | Any]:
        """Returns a list of available tools.

        This function retrieves the names of the available tools from the
        MCP servers configuration dictionary.

        NOTE: a new session is created for each tool call.

        Args:
            server (str | None): The name of the MCP server to connect to.

        Returns:
            list[MCPTool | Any]: A list of available tools. The tool can be adapted to a specific
                framework's tool using `tool_adapter`.
        """
    async def get_resources(self, server: str | None = None) -> list[MCPResource]:
        """Returns a list of available resources.

        This function retrieves the names of the available resources from the
        MCP servers configuration dictionary. Note that this function only
        returns the metadata of the resources, not the actual content. For the
        content, use the `get_resource` function.

        NOTE: a new session is created for each resource call.

        Args:
            server (str | None): The name of the MCP server to connect to.

        Returns:
            list[MCPResource]: A list of available resources. Only the metadata of the
                resources is returned.
        """
    async def get_resource(self, server: str, resource_uri: str) -> Any:
        """Returns a resource's entire content.

        This function retrieves the resource from the MCP servers configuration dictionary.
        Be careful with this function, as it will return the entire content of the resource,

        NOTE: a new session is created for each resource call.

        Args:
            server (str): The name of the MCP server to connect to.
            resource_uri (str): The URI of the resource to retrieve.

        Returns:
            Any: The resource's entire content. The resource can be adapted to a specific
                framework's resource using `resource_adapter`.
        """
