import abc
from _typeshed import Incomplete
from a2a.server.agent_execution import AgentExecutor as A2ASDKExecutor, RequestContext as RequestContext
from a2a.server.events.event_queue import EventQueue as EventQueue
from abc import ABC, abstractmethod
from enum import StrEnum
from gllm_agents.types import A2AEvent as A2AEvent, A2AStreamEventType as A2AStreamEventType
from gllm_agents.utils import serialize_references_for_metadata as serialize_references_for_metadata
from gllm_agents.utils.artifact_helpers import ArtifactHandler as ArtifactHandler
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from gllm_agents.utils.token_usage_helper import STEP_USAGE_KEY as STEP_USAGE_KEY, TOTAL_USAGE_KEY as TOTAL_USAGE_KEY

logger: Incomplete

class MetadataFieldKeys(StrEnum):
    """Enumeration of standard metadata field keys used in A2A events."""
    TOOL_INFO = 'tool_info'
    REFERENCES = 'references'
    THINKING_AND_ACTIVITY_INFO = 'thinking_and_activity_info'
    STEP_USAGE = STEP_USAGE_KEY
    TOTAL_USAGE = TOTAL_USAGE_KEY

class BaseA2AExecutor(A2ASDKExecutor, ABC, metaclass=abc.ABCMeta):
    """Abstract base class for GLLM Agent framework's A2A server-side executors.

    This class extends the A2A SDK's `AgentExecutor`. It serves as a common
    foundation for specific executors tailored to different agent types within the
    `gllm-agents` framework, such as `LangGraphA2AExecutor` or
    `GoogleADKA2AExecutor`.

    Subclasses are required to implement the `execute` method to handle A2A
    requests. The `cancel` method has a common implementation.

    Attributes:
        _active_tasks (dict[str, asyncio.Task]): A dictionary mapping task IDs to
            their corresponding asyncio.Task instances for active agent executions.
    """
    def __init__(self) -> None:
        """Initializes the BaseA2AExecutor."""
    @abstractmethod
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Processes an incoming agent request and manages its execution.

        Implementations should interact with the underlying agent (e.g., a LangGraph
        or Google ADK agent) based on the provided `context`. All communications
        regarding task status, artifacts, and completion must be sent through
        the `event_queue`.

        This method typically involves:
        1. Calling `_handle_initial_execute_checks` for validation and setup.
        2. Defining an agent-specific coroutine for processing (e.g., `_process_stream`).
        3. Calling `_execute_agent_processing` to manage the lifecycle of this coroutine.

        Args:
            context (RequestContext): The request context containing information about the incoming
                     message, task, and other relevant data.
            event_queue (EventQueue): The queue used to send events (e.g., task status updates,
                         artifacts) back to the A2A server infrastructure.
        """
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Handles a request to cancel an ongoing agent task.

        This method attempts to cancel an active asyncio.Task associated with the
        given `context.task_id`. It waits for a short period for the task to handle
        the cancellation gracefully. The `event_queue` is used to report the
        outcome of the cancellation attempt (e.g., success, error during cleanup).

        Args:
            context (RequestContext): The request context for the task to be cancelled,
                primarily used to get the `task_id` and `context_id`.
            event_queue (EventQueue): The queue for sending cancellation status events.
        """
