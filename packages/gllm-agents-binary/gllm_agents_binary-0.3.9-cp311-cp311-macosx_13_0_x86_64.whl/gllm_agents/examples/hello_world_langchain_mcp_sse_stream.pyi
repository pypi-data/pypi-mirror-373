from gllm_agents.agent import LangChainAgent as LangChainAgent
from gllm_agents.examples.mcp_configs.configs import mcp_config_sse as mcp_config_sse

async def main() -> None:
    """Demonstrates the LangChainAgent with MCP tools via SSE transport and streaming capabilities."""
