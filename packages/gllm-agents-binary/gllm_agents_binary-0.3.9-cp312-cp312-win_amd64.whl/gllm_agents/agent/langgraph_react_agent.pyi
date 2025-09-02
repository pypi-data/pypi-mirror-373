from _typeshed import Incomplete
from dataclasses import dataclass
from gllm_agents.agent.base_langgraph_agent import BaseLangGraphAgent as BaseLangGraphAgent
from gllm_agents.tools.tool_config_injector import TOOL_CONFIGS_KEY as TOOL_CONFIGS_KEY
from gllm_agents.utils import add_references_chunks as add_references_chunks
from gllm_agents.utils.langgraph import convert_langchain_messages_to_multimodal_prompt as convert_langchain_messages_to_multimodal_prompt, convert_lm_output_to_langchain_message as convert_lm_output_to_langchain_message
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from gllm_agents.utils.token_usage_helper import TOTAL_USAGE_KEY as TOTAL_USAGE_KEY, USAGE_METADATA_KEY as USAGE_METADATA_KEY, add_usage_metadata as add_usage_metadata, extract_and_update_token_usage_from_ai_message as extract_and_update_token_usage_from_ai_message, extract_token_usage_from_tool_output as extract_token_usage_from_tool_output
from gllm_core.event import EventEmitter as EventEmitter
from gllm_core.schema import Chunk
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage as BaseMessage, ToolMessage
from langchain_core.messages.ai import UsageMetadata as UsageMetadata
from langchain_core.tools import BaseTool as BaseTool
from langgraph.graph import StateGraph as StateGraph
from langgraph.graph.message import add_messages as add_messages
from langgraph.graph.state import CompiledStateGraph as CompiledStateGraph
from langgraph.managed import IsLastStep as IsLastStep, RemainingSteps as RemainingSteps
from typing import Any, Sequence
from typing_extensions import Annotated, TypedDict

logger: Incomplete
DEFAULT_INSTRUCTION: str
SAVE_OUTPUT_HISTORY: str
FORMAT_AGENT_REFERENCE: str

@dataclass
class ToolCallResult:
    """Container for the results of a single tool call execution.

    Holds all the data returned from a tool execution in a structured format.

    Attributes:
        messages: List of tool messages generated from the tool call.
        artifacts: List of artifacts produced by the tool call.
        metadata_delta: Dictionary of metadata updates from the tool call.
        references: List of reference chunks from the tool call.
        step_usage: Token usage metadata from the tool call.
    """
    messages: list[ToolMessage]
    artifacts: list[dict[str, Any]]
    metadata_delta: dict[str, Any]
    references: list[Chunk]
    step_usage: UsageMetadata | None

class ReactAgentState(TypedDict):
    """State schema for the ReAct agent.

    Includes messages, step tracking, optional event emission support, artifacts, references, and metadata.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    is_last_step: IsLastStep
    remaining_steps: RemainingSteps
    event_emitter: EventEmitter | None
    artifacts: list[dict[str, Any]] | None
    references: Annotated[list[Chunk], add_references_chunks]
    metadata: dict[str, Any] | None
    total_usage: Annotated[UsageMetadata | None, add_usage_metadata]

class LangGraphReactAgent(BaseLangGraphAgent):
    """A ReAct agent template built on LangGraph.

    This agent can use either:
    - An LMInvoker (if self.lm_invoker is set by BaseAgent)
    - A LangChain BaseChatModel (if self.model is set by BaseAgent)

    The graph structure follows the standard ReAct pattern:
    agent -> tools -> agent (loop) -> END
    """
    def __init__(self, name: str, instruction: str = ..., model: BaseChatModel | str | Any | None = None, tools: Sequence[BaseTool] | None = None, agents: Sequence[Any] | None = None, description: str | None = None, thread_id_key: str = 'thread_id', event_emitter: EventEmitter | None = None, **kwargs: Any) -> None:
        """Initialize the LangGraph ReAct Agent.

        Args:
            name: The name of the agent.
            instruction: The system instruction for the agent.
            model: The model to use (lm_invoker, LangChain model, string, etc.).
            tools: Sequence of LangChain tools available to the agent.
            agents: Optional sequence of sub-agents for delegation (coordinator mode).
            description: Human-readable description of the agent.
            thread_id_key: Key for thread ID in configuration.
            event_emitter: Optional event emitter for streaming updates.
            **kwargs: Additional keyword arguments passed to BaseLangGraphAgent.
        """
    def define_graph(self, graph_builder: StateGraph) -> CompiledStateGraph:
        """Define the ReAct agent graph structure.

        Args:
            graph_builder: The StateGraph builder to define the graph structure.

        Returns:
            Compiled LangGraph ready for execution.
        """

class LangGraphAgent(LangGraphReactAgent):
    """Alias for LangGraphReactAgent."""
class LangChainAgent(LangGraphReactAgent):
    """Alias for LangGraphReactAgent."""
