from gllm_agents.agent import LangGraphAgent as LangGraphAgent
from gllm_agents.agent.types import A2AClientConfig as A2AClientConfig

A2A_SERVER_PORT: int
A2A_AGENT_NAME: str
MCP_SERVER_PORT: int
MCP_AGENT_NAME: str
MODEL_NAME: str

async def create_agent() -> tuple[LangGraphAgent, dict[str, bool]]:
    """Create and configure the LangGraphAgent with MCP and A2A connections.

    Returns:
        tuple: (agent, connected_servers) where connected_servers is a dict
        showing which servers were successfully connected.
    """
async def connect_to_mcp_server(agent: LangGraphAgent) -> bool:
    """Connect to the MCP server and register tools.

    Args:
        agent: The LangGraphAgent instance to configure.

    Returns:
        bool: True if connection was successful, False otherwise.
    """
async def connect_to_a2a_server(agent: LangGraphAgent) -> bool:
    """Connect to the A2A server and register agents.

    Args:
        agent: The LangGraphAgent instance to configure.

    Returns:
        bool: True if connection was successful, False otherwise.
    """
async def test_mcp_weather_tool(agent: LangGraphAgent) -> None:
    """Test the MCP weather tool if available.

    Args:
        agent: The configured LangGraphAgent instance.
    """
async def test_stock_agent(agent: LangGraphAgent) -> None:
    """Test the A2A Stock Agent if available.

    Args:
        agent: The configured LangGraphAgent instance.
    """
async def main() -> None:
    """Main function to run the A2A and MCP integration example."""
