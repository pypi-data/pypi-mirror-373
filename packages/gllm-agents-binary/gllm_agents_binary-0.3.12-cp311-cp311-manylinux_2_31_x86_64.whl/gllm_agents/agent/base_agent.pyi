import abc
from _typeshed import Incomplete
from a2a.types import AgentCard
from gllm_agents.a2a.server.google_adk_executor import GoogleADKExecutor as GoogleADKExecutor
from gllm_agents.a2a.server.langgraph_executor import LangGraphA2AExecutor as LangGraphA2AExecutor
from gllm_agents.agent.interface import AgentInterface as AgentInterface
from gllm_agents.agent.types import A2AClientConfig as A2AClientConfig, AgentConfig as AgentConfig, BaseAgentConfig as BaseAgentConfig
from gllm_agents.credentials.manager import CredentialsManager as CredentialsManager
from gllm_agents.utils.a2a_connector import A2AConnector as A2AConnector
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from gllm_agents.utils.name_preprocessor.name_preprocessor import NamePreprocessor as NamePreprocessor
from starlette.applications import Starlette
from typing import Any, AsyncGenerator

logger: Incomplete
AGENT_EXECUTOR_MAPPING: Incomplete
DEFAULT_RETRY_CONFIG: Incomplete
LM_EXCLUDE_FIELDS: Incomplete
CUSTOM_PROVIDERS: Incomplete
OUTPUT_ANALYTICS_KEY: str

class BaseAgent(AgentInterface, metaclass=abc.ABCMeta):
    """Base class for agents, providing common A2A client method implementations.

    Concrete agent implementations (e.g., LangGraphAgent, GoogleADKAgent)
    should inherit from this class if they need to utilize the shared A2A
    client functionalities.

    This class now supports flexible model handling:
    - model: Optional[Any] - can be an lm_invoker, string/ModelId, LangChain BaseChatModel, or other types
    - Automatically sets self.lm_invoker if an lm_invoker is provided or can be built
    - Stores the original model in self.model for subclass use
    """
    model: Incomplete
    tools: Incomplete
    mcp_config: Incomplete
    tool_configs: Incomplete
    name_preprocessor: Incomplete
    def __init__(self, name: str, instruction: str, description: str | None = None, model: Any | None = None, tools: list[Any] | None = None, config: BaseAgentConfig | dict[str, Any] | None = None, tool_configs: dict[str, Any] | None = None, **kwargs: Any) -> None:
        """Initializes the BaseAgent.

        Args:
            name: The name of the agent.
            instruction: The core directive or system prompt for the agent.
            description: Human-readable description. Defaults to instruction if not provided.
            model: The model to use. Can be:
                - BaseLMInvoker instance (will be set as self.lm_invoker)
                - String or ModelId (will build an lm_invoker)
                - LangChain BaseChatModel (will be stored in self.model)
                - Any other type (will be stored in self.model)
            tools: List of tools available to the agent.
            config: Additional configuration for the agent. Can be a BaseAgentConfig instance or dict.
            tool_configs: Default tool configurations applied to all tool calls from this agent.
            **kwargs: Additional keyword arguments for AgentInterface.
        """
    def get_name_preprocessor(self) -> NamePreprocessor:
        """Get the name preprocessor based on the provider.

        This will be used to correct the agent name and tool name. (mostly tool name)

        Returns:
            NamePreprocessor: The name preprocessor for the model.
        """
    @property
    def model_provider(self) -> str:
        """Get the provider of the model with simplified logic.

        Returns:
            str: The provider of the model.
        """
    def to_a2a(self, agent_card: AgentCard, **kwargs: Any) -> Starlette:
        """Converts the agent to an A2A-compatible ASGI application.

        This implementation provides a base setup for A2A server components.
        Subclasses can override this method if they need custom executor
        or task store implementations.

        Args:
            agent_card: The agent card to use for the A2A application.
            **kwargs: Additional keyword arguments for ASGI application configuration.

        Returns:
            A Starlette ASGI application that can be used with any ASGI server.
        """
    @classmethod
    def discover_agents(cls, a2a_config: A2AClientConfig, **kwargs: Any) -> list[AgentCard]:
        """Discover agents from the URLs specified in a2a_config.discovery_urls.

        This concrete implementation fetches and parses .well-known/agent.json
        from each discovery URL to build a list of available agents.

        Args:
            a2a_config: Configuration containing discovery URLs and other A2A settings.
            **kwargs: Additional keyword arguments (unused in this implementation).

        Returns:
            A list of AgentCard objects representing discovered agents.
        """
    def send_to_agent(self, agent_card: AgentCard, message: str | dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """Synchronously sends a message to another agent using the A2A protocol.

        This method is a synchronous wrapper around asend_to_agent. It handles the creation
        of an event loop if one doesn't exist, and manages the asynchronous call internally.

        Args:
            agent_card: The AgentCard instance containing the target agent's details including
                URL, authentication requirements, and capabilities.
            message: The message to send to the agent. Can be either a string for simple text
                messages or a dictionary for structured data.
            **kwargs: Additional keyword arguments passed to asend_to_agent.

        Returns:
            A dictionary containing the response details:
                - status (str): 'success' or 'error'
                - content (str): Extracted text content from the response
                - task_id (str, optional): ID of the created/updated task
                - task_state (str, optional): Current state of the task
                - raw_response (str): Complete JSON response from the A2A client
                - error_type (str, optional): Type of error if status is 'error'
                - message (str, optional): Error message if status is 'error'

        Raises:
            RuntimeError: If called from within an existing event loop or if asend_to_agent
                encounters an unhandled exception.
        """
    async def asend_to_agent(self, agent_card: AgentCard, message: str | dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """Asynchronously sends a message to another agent using the A2A protocol.

        This method handles the core A2A communication logic, creating and sending properly
        formatted A2A messages and processing the responses.

        Args:
            agent_card: The AgentCard instance containing the target agent's details including
                URL, authentication requirements, and capabilities.
            message: The message to send to the agent. Can be either a string for simple text
                messages or a dictionary for structured data.
            **kwargs: Additional keyword arguments.

        Returns:
            A dictionary containing the response details:
                - status (str): 'success' or 'error'
                - content (str): Extracted text content from the response
                - task_id (str, optional): ID of the created/updated task
                - task_state (str, optional): Current state of the task
                - raw_response (str): Complete JSON response from the A2A client
                - error_type (str, optional): Type of error if status is 'error'
                - message (str, optional): Error message if status is 'error'

        Raises:
            httpx.HTTPError: If there's an HTTP-related error during the request.
            Exception: For any other unexpected errors during message sending or processing.
        """
    async def astream_to_agent(self, agent_card: AgentCard, message: str | dict[str, Any], **kwargs: Any) -> AsyncGenerator[dict[str, Any], None]:
        """Asynchronously sends a streaming message to another agent using the A2A protocol.

        This method supports streaming responses from the target agent, yielding chunks of
        the response as they become available. It handles various types of streaming events
        including task status updates, artifact updates, and message parts.

        Args:
            agent_card: The AgentCard instance containing the target agent's details including
                URL, authentication requirements, and capabilities.
            message: The message to send to the agent. Can be either a string for simple text
                messages or a dictionary for structured data.
            **kwargs: Additional keyword arguments.

        Yields:
            Dictionaries containing streaming response chunks:
                For successful chunks:
                    - status (str): 'success'
                    - content (str): Extracted text content from the chunk
                    - task_id (str): ID of the associated task
                    - task_state (str): Current state of the task
                    - final (bool): Whether this is the final chunk
                    - artifact_name (str, optional): Name of the artifact if chunk is an artifact update
                For error chunks:
                    - status (str): 'error'
                    - error_type (str): Type of error encountered
                    - message (str): Error description

        Raises:
            httpx.HTTPError: If there's an HTTP-related error during the streaming request.
            Exception: For any other unexpected errors during message streaming or processing.
        """
    @staticmethod
    def format_agent_description(agent_card: AgentCard) -> str:
        """Format the description of an agent card including skills information.

        Args:
            agent_card (AgentCard): The agent card to format.

        Returns:
            str: The formatted description including skills.
        """
    def add_mcp_server(self, mcp_config: dict[str, dict[str, Any]]) -> None:
        """Adds MCP servers to the agent.

        Args:
            mcp_config: A dictionary containing MCP server configurations.

        Raises:
            ValueError: If the MCP configuration is empty or None.
            KeyError: If a server with the same name already exists in the MCP configuration.
        """
