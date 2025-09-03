import abc
from _typeshed import Incomplete
from a2a.types import AgentCard as AgentCard
from abc import abstractmethod
from gllm_agents.agent.base_agent import BaseAgent as BaseAgent
from gllm_agents.agent.types import StreamMode as StreamMode
from gllm_agents.mcp.client.langchain import LangchainMCPClient as LangchainMCPClient
from gllm_agents.tools.tool_config_injector import CONFIG_SCHEMA_ATTR as CONFIG_SCHEMA_ATTR, TOOL_CONFIG_SCHEMA_ATTR as TOOL_CONFIG_SCHEMA_ATTR, inject_config_methods_into_tool as inject_config_methods_into_tool
from gllm_agents.types import A2AEvent as A2AEvent, A2AStreamEventType as A2AStreamEventType
from gllm_agents.utils import validate_references as validate_references
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from gllm_agents.utils.metadata_helper import Status as Status
from gllm_agents.utils.token_usage_helper import STEP_USAGE_KEY as STEP_USAGE_KEY, TOTAL_USAGE_KEY as TOTAL_USAGE_KEY, USAGE_METADATA_KEY as USAGE_METADATA_KEY
from gllm_core.event import EventEmitter
from langchain_core.messages import BaseMessage as BaseMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages as add_messages
from langgraph.graph.state import CompiledStateGraph as CompiledStateGraph
from langgraph.types import Checkpointer as Checkpointer, StreamWriter as StreamWriter
from typing import Any, AsyncGenerator, Sequence

logger: Incomplete

class BaseLangGraphAgent(BaseAgent, metaclass=abc.ABCMeta):
    """Base class for LangGraph-based agents with unified tool approach.

    Provides core LangGraph functionality including:
    - Graph compilation and execution
    - State schema management
    - I/O mapping between user inputs and graph states
    - Event emission support
    - Tool resolution and handling
    - A2A communication capabilities via tools
    - Agent delegation capabilities via tools
    - MCP server integration via tools
    - Enhanced output extraction from various state formats

    Tool Management:
    - regular_tools: Standard LangChain tools provided during initialization
    - mcp_tools: Tools retrieved from MCP servers
    - resolved_tools: Combined collection of all tools for graph execution

    Subclasses must implement:
    - define_graph(): Define the specific graph structure
    - _prepare_graph_input(): Convert user input to graph state
    - _format_graph_output(): Convert final graph state to user output
    """
    state_schema: Incomplete
    thread_id_key: Incomplete
    event_emitter: Incomplete
    checkpointer: Incomplete
    a2a_tool_manager: Incomplete
    delegation_tool_manager: Incomplete
    regular_tools: list[BaseTool]
    mcp_tools: list[BaseTool]
    resolved_tools: list[BaseTool]
    def __init__(self, name: str, instruction: str, description: str | None = None, model: Any | None = None, tools: Sequence[BaseTool] | None = None, state_schema: type | None = None, thread_id_key: str = 'thread_id', event_emitter: EventEmitter | None = None, checkpointer: Checkpointer | None = None, **kwargs: Any) -> None:
        """Initialize the BaseLangGraphAgent.

        Args:
            name: The name of the agent.
            instruction: The system instruction for the agent.
            description: Human-readable description of the agent.
            model: The model to use (lm_invoker, LangChain model, string, etc.).
            tools: Sequence of regular LangChain tools (not A2A or delegation tools).
            state_schema: The state schema for the LangGraph. Defaults to basic message state.
            thread_id_key: Key for thread ID in configuration.
            event_emitter: Optional event emitter for streaming updates.
            checkpointer: Optional checkpointer for conversation persistence.
            **kwargs: Additional keyword arguments passed to BaseAgent (including tool_configs).
        """
    @abstractmethod
    def define_graph(self, graph_builder: StateGraph) -> CompiledStateGraph:
        """Define the specific graph structure for this agent type.

        Subclasses must implement this method to:
        1. Add nodes to the graph_builder
        2. Add edges and conditional edges
        3. Set entry points
        4. Return the compiled graph

        Args:
            graph_builder: The StateGraph builder to define nodes and edges on.

        Returns:
            The compiled graph ready for execution.
        """
    def register_a2a_agents(self, agent_cards: list[AgentCard]) -> None:
        """Register A2A communication capabilities using the A2A tool manager.

        Args:
            agent_cards (list[AgentCard]): List of AgentCard instances for external communication.
        """
    def register_delegation_agents(self, agents: list[BaseAgent]) -> None:
        """Register internal agent delegation capabilities using the delegation tool manager.

        Args:
            agents: List of BaseAgent instances for internal task delegation.
        """
    tools: Incomplete
    def update_regular_tools(self, new_tools: list[BaseTool], rebuild_graph: bool | None = None) -> None:
        """Update regular tools (not capabilities).

        Args:
            new_tools: New list of regular tools to use.
            rebuild_graph: Whether to rebuild graph. If None, uses auto_rebuild_graph setting.
        """
    def run(self, query: str, **kwargs: Any) -> dict[str, Any]:
        """Synchronously run the LangGraph agent.

        Args:
            query: The input query for the agent.
            **kwargs: Additional keyword arguments.

        Returns:
            Dictionary containing the agent's response.
        """
    async def arun(self, query: str, **kwargs: Any) -> dict[str, Any]:
        """Asynchronously run the LangGraph agent.

        If MCP configuration exists, connects to the MCP server and registers tools before running.

        Args:
            query: The input query for the agent.
            **kwargs: Additional keyword arguments including configurable for LangGraph.

        Returns:
            Dictionary containing the agent's response and full final state.
        """
    async def arun_stream(self, query: str, **kwargs: Any) -> AsyncGenerator[str | dict[str, Any], None]:
        """Asynchronously stream the LangGraph agent's response.

        If MCP configuration exists, connects to the MCP server and registers tools before streaming.
        This method properly handles both LM Invoker and LangChain model streaming:
        - For LM Invoker: Uses StreamEventHandler to capture streaming events
        - For LangChain models: Uses LangGraph's native streaming implementation

        Args:
            query: The input query for the agent.
            **kwargs: Additional keyword arguments.

        Yields:
            Chunks of output (strings or dicts) from the streaming response.
        """
    def add_mcp_server(self, mcp_config: dict[str, dict[str, Any]]) -> None:
        """Add MCP server configuration.

        Args:
            mcp_config (dict[str, dict[str, Any]]): Dictionary containing MCP server configurations.
        """
    async def arun_a2a_stream(self, query: str, **kwargs: Any) -> AsyncGenerator[dict[str, Any], None]:
        '''Asynchronously streams the agent\'s response in a generic format for A2A.

        If MCP configuration exists, connects to the MCP server and registers tools before streaming.

        Args:
            query: The input query for the agent.
            **kwargs: Additional keyword arguments.

        Yields:
            Dictionaries with "status" and "content" keys.
            Possible statuses: "working", "completed", "failed", "canceled".
        '''
