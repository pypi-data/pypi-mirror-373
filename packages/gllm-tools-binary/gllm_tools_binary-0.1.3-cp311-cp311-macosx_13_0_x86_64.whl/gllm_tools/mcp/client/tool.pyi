from _typeshed import Incomplete
from gllm_tools.mcp.client.config import MCPConfiguration as MCPConfiguration
from gllm_tools.mcp.client.session import create_session as create_session
from mcp.types import ToolAnnotations as ToolAnnotations
from typing import Any, Callable

logger: Incomplete

class MCPTool:
    """Represents an MCP tool.

    The MCP tool is an agnostic representation of a tool created by an MCP
    server. It is not intended to be used directly, but rather to be used as
    a base class for other tools.
    """
    name: str
    description: str | None
    parameters: dict[str, Any]
    annotations: ToolAnnotations | None
    model_config: Incomplete
    def __init__(self, *, name: str, parameters: dict[str, Any], description: str | None = None, annotations: ToolAnnotations | None = None) -> None:
        """Constructs a new MCP tool.

        Args:
            name (str): The name of the tool.
            parameters (dict[str, Any]): The parameters of the tool.
            description (str | None): The description of the tool.
            annotations (ToolAnnotations | None): The annotations of the tool.
        """

async def load_mcp_tools(*, config: MCPConfiguration, tool_adapter: Callable[[MCPTool, MCPConfiguration], Any] | None = None) -> list[Any]:
    """Load all available MCP tools and convert them to tool objects.

    Args:
        config (MCPConfiguration): The MCP server configuration.
        tool_adapter (Callable[[MCPTool, MCPConfiguration], Any] | None): The adapter to use to
            convert the MCP tools to a specific framework's tool. If not provided, the
            MCP tools are returned as is.

    Returns:
        list[Any]: A list of MCP tools. The tool can be adapted to a specific
        tool using `tool_adapter`.
    """
