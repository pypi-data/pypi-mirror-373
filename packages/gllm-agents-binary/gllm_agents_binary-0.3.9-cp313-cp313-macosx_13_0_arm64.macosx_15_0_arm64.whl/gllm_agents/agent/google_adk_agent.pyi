from _typeshed import Incomplete
from a2a.types import AgentCard as AgentCard
from gllm_agents.agent.base_agent import BaseAgent as BaseAgent
from gllm_agents.mcp.client import GoogleADKMCPClient as GoogleADKMCPClient
from gllm_agents.utils.a2a_connector import A2AConnector as A2AConnector
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from google.adk.agents import LlmAgent
from google.adk.tools.langchain_tool import LangchainTool
from langchain.tools import BaseTool as LangchainBaseTool
from pydantic import BaseModel
from typing import Any, AsyncGenerator, AsyncIterator

logger: Incomplete
MODEL_TEMPERATURE: float
DEFAULT_AUTH_URL: str

class A2AToolInput(BaseModel):
    """Input for the A2ATool."""
    query: str

class A2ATool(LangchainBaseTool):
    """A tool that communicates with an A2A agent."""
    name: str
    description: str
    args_schema: type[BaseModel]
    agent_card: AgentCard

def create_a2a_tool(agent_card: AgentCard) -> LangchainTool:
    """Create a LangChain tool from an A2A agent card."""

class GoogleADKAgent(BaseAgent):
    """An agent that wraps a native Google ADK Agent.

    This class implements the AgentInterface and uses Google's LlmAgent
    to handle the core conversation and tool execution logic via ADK's
    async-first design.
    """
    adk_native_agent: LlmAgent
    model: Incomplete
    max_iterations: Incomplete
    tools: Incomplete
    agents: Incomplete
    session_service: Incomplete
    name: Incomplete
    def __init__(self, name: str, instruction: str, model: str, tools: list[Any] | None = None, description: str | None = None, max_iterations: int = 3, agents: list['GoogleADKAgent'] | None = None, **kwargs: Any) -> None:
        '''Initializes the GoogleADKAgent.

        Args:
            name: The name of this wrapper agent.
            instruction: The instruction for this wrapper agent.
            model: The name of the Google ADK model to use (e.g., "gemini-1.5-pro-latest").
            tools: An optional list of callable tools for the ADK agent.
            description: An optional human-readable description.
            max_iterations: Maximum number of iterations to run (default: 3).
            agents: Optional list of sub-agents that this agent can delegate to using ADK\'s
                   built-in multi-agent capabilities. These will be passed as sub_agents to the
                   underlying LlmAgent.
            **kwargs: Additional keyword arguments passed to the parent `__init__`.
        '''
    def run(self, query: str, **kwargs: Any) -> dict[str, Any]:
        '''Synchronously runs the Google ADK agent by wrapping the internal async run method.

        Args:
            query: The input query for the agent.
            **kwargs: Additional keyword arguments passed to the internal async run method.
                      Supports "session_id", "user_id", "app_name".

        Returns:
            A dictionary containing the agent\'s response.

        Raises:
            RuntimeError: If `asyncio.run()` is called from an already running event loop,
                          or for other unhandled errors during synchronous execution.
        '''
    async def arun(self, query: str, **kwargs: Any) -> dict[str, Any]:
        '''Asynchronously runs the agent with the given query and returns the response.

        Args:
            query: The user\'s query to process.
            **kwargs: Additional keyword arguments. Supports "session_id", "user_id", "app_name".

        Returns:
            A dictionary containing the output and other metadata.
        '''
    async def arun_stream(self, query: str, **kwargs: Any) -> AsyncIterator[str]:
        '''Runs the agent with the given query and streams the response parts.

        Args:
            query: The user\'s query to process.
            **kwargs: Additional keyword arguments. Supports "session_id", "user_id", "app_name".

        Yields:
            Text response chunks from the model. If an error occurs, the error message is yielded.
        '''
    def register_a2a_agents(self, agent_cards: list[AgentCard]) -> None:
        """Convert known A2A agents to LangChain tools.

        This method takes the agents from a2a_config.known_agents, creates A2AAgent
        instances for each one, and wraps them in LangChain tools.

        Returns:
            None: The tools are added to the existing tools list.
        """
    def add_mcp_server(self, mcp_config: dict[str, dict[str, Any]]) -> None:
        """Adds a new MCP server configuration.

        Args:
            mcp_config: Dictionary containing server name as key and its configuration as value.

        Raises:
            ValueError: If mcp_config is empty or None, or if any server configuration is invalid.
            KeyError: If any server name already exists in the configuration.
        """
    async def arun_a2a_stream(self, query: str, configurable: dict[str, Any] | None = None, **kwargs: Any) -> AsyncGenerator[dict[str, Any], None]:
        '''Asynchronously streams the agent\'s response in a format compatible with A2A.

        This method formats the ADK agent\'s streaming responses into a consistent format
        that the A2A executor can understand and process.

        Args:
            query: The input query for the agent.
            configurable: Optional dictionary for configuration, may include:
                - thread_id: The A2A task ID (used as session_id).
            **kwargs: Additional keyword arguments. Supports "user_id", "app_name".

        Yields:
            Dictionary with \'status\' and \'content\' fields that describe the agent\'s response state.
        '''
