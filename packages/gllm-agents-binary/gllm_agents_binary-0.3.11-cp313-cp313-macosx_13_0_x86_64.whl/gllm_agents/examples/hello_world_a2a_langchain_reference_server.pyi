from _typeshed import Incomplete
from gllm_agents.agent import LangChainAgent as LangChainAgent
from gllm_agents.examples.tools import google_serper_tool as google_serper_tool, time_tool as time_tool
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager

logger: Incomplete
SERVER_AGENT_NAME: str

def main(host: str, port: int):
    """Runs the LangChain Weather A2A server."""
