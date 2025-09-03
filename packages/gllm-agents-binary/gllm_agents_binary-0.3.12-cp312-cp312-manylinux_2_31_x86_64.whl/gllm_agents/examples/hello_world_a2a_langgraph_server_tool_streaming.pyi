from _typeshed import Incomplete
from gllm_agents.agent import LangChainAgent as LangChainAgent
from gllm_agents.examples.tools.langgraph_streaming_tool import LangGraphStreamingTool as LangGraphStreamingTool
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager

logger: Incomplete
SERVER_AGENT_NAME: str

def main(host: str, port: int):
    """Runs the LangGraph Agent Wrapper A2A server."""
