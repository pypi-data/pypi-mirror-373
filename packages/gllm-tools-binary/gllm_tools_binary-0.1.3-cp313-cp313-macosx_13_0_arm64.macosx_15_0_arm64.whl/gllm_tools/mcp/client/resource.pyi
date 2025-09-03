from _typeshed import Incomplete
from gllm_tools.mcp.client.config import MCPConfiguration as MCPConfiguration
from gllm_tools.mcp.client.session import create_session as create_session
from mcp.types import Annotations as Annotations
from pydantic import AnyUrl as AnyUrl, UrlConstraints as UrlConstraints
from typing import Annotated

logger: Incomplete

class MCPResource:
    """The MCP (Model Context Protocol) Resource."""
    uri: Annotated[AnyUrl, None]
    name: str
    description: str | None
    mime_type: str | None
    size: int | None
    annotations: Annotations | None
    def __init__(self, name: str, description: str | None = None, uri: AnyUrl | None = None, mime_type: str | None = None, size: int | None = None, annotations: Annotations | None = None) -> None:
        """Constructs a new MCP resource.

        Args:
            name (str): The name of the resource.
            description (str | None): The description of the resource.
            uri (AnyUrl | None): The URI of the resource.
            mime_type (str | None): The MIME type of the resource.
            size (int | None): The size of the resource in bytes.
            annotations (Annotations | None): The annotations of the resource.
        """

async def load_mcp_resources(*, config: MCPConfiguration) -> list[MCPResource]:
    """Load all available MCP resources and convert them to resource objects.

    This function only returns the metadata of the resources, not the actual
    content.

    Args:
        config (MCPConfiguration): The MCP server configuration.

    Returns:
        list[MCPResource]: A list of MCP resources.
    """
