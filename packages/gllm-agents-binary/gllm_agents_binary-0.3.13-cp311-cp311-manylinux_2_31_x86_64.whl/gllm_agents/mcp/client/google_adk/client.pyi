from gllm_tools.mcp.client.client import MCPClient
from gllm_tools.mcp.client.config import MCPConfiguration as MCPConfiguration
from gllm_tools.mcp.client.resource import MCPResource as MCPResource
from gllm_tools.mcp.client.tool import MCPTool as MCPTool
from mcp.types import CallToolResult as CallToolResult, EmbeddedResource, ImageContent

NonTextContent = ImageContent | EmbeddedResource

class GoogleADKMCPClient(MCPClient):
    '''Google ADK MCP Client.

    This client is a wrapper around the MCPClient that converts MCP tools and resources
    into Google ADK-compatible FunctionTool instances and resources. It enables seamless
    integration between MCP servers and ADK agents.

    The client handles:
    - Converting MCP tools to ADK FunctionTool instances
    - Managing MCP server sessions and connections
    - Converting MCP resources to ADK-compatible formats
    - Handling tool execution and response formatting

    Example:
        ```python
        from gllm_tools.mcp.client.google_adk import GoogleADKMCPClient
        from gllm_tools.mcp.client.config import MCPConfiguration

        servers = {
            "filesystem": MCPConfiguration(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/folder"]
            )
        }

        client = GoogleADKMCPClient(servers)
        tools = await client.get_tools()  # Returns list of ADK FunctionTool instances
        ```
    '''
    RESOURCE_FETCH_TIMEOUT: int
