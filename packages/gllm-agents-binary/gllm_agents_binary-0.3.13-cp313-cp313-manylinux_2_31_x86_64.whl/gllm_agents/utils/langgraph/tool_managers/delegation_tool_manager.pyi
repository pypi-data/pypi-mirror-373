from _typeshed import Incomplete
from gllm_agents.agent.base_agent import BaseAgent as BaseAgent
from gllm_agents.types.a2a_events import A2AEvent as A2AEvent, A2AStreamEventType as A2AStreamEventType
from gllm_agents.utils.artifact_helpers import extract_artifacts_from_agent_response as extract_artifacts_from_agent_response
from gllm_agents.utils.langgraph.tool_managers.base_tool_manager import BaseLangGraphToolManager as BaseLangGraphToolManager
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from gllm_agents.utils.reference_helper import extract_references_from_agent_response as extract_references_from_agent_response
from gllm_agents.utils.token_usage_helper import TOTAL_USAGE_KEY as TOTAL_USAGE_KEY, USAGE_METADATA_KEY as USAGE_METADATA_KEY, extract_token_usage_from_agent_response as extract_token_usage_from_agent_response
from langchain_core.runnables import RunnableConfig as RunnableConfig
from langchain_core.tools import BaseTool as BaseTool
from langgraph.types import StreamWriter as StreamWriter

RESULT_KEY: str
ARTIFACTS_KEY: str
METADATA_KEY: str
REFERENCES_KEY: str
OUTPUT_KEY: str
logger: Incomplete
METADATA_INTERNAL_PREFIXES: Incomplete
METADATA_INTERNAL_KEYS: Incomplete
AGENT_RUN_A2A_STREAMING_METHOD: str

class DelegationToolManager(BaseLangGraphToolManager):
    """Manages internal agent delegation tools for LangGraph agents.

    This tool manager converts internal agent instances into LangChain tools
    that can be used for task delegation within a unified ToolNode. Each
    delegated agent becomes a tool that the coordinator can call.

    Simplified version following legacy BaseLangChainAgent patterns.
    """
    registered_agents: list[BaseAgent]
    def __init__(self) -> None:
        """Initialize the delegation tool manager."""
    created_tools: Incomplete
    def register_resources(self, agents: list[BaseAgent]) -> list[BaseTool]:
        """Register internal agents for delegation and convert them to tools.

        Args:
            agents: List of BaseAgent instances for internal task delegation.

        Returns:
            List of created delegation tools.
        """
    def get_resource_names(self) -> list[str]:
        """Get names of all registered delegation agents.

        Returns:
            list[str]: A list of names of all registered delegation agents.
        """
