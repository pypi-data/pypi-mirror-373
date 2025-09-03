from _typeshed import Incomplete
from a2a.server.agent_execution import RequestContext as RequestContext
from a2a.server.events.event_queue import EventQueue as EventQueue
from a2a.server.tasks import TaskUpdater as TaskUpdater
from gllm_agents.a2a.server.base_executor import BaseA2AExecutor as BaseA2AExecutor
from gllm_agents.agent.google_adk_agent import GoogleADKAgent as GoogleADKAgent
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager

logger: Incomplete

class GoogleADKExecutor(BaseA2AExecutor):
    '''A2A Executor for serving a `GoogleADKAgent`.

    This executor bridges the A2A server protocol with a `gllm_agents.agent.GoogleADKAgent`.
    It handles incoming requests by invoking the agent\'s `arun_a2a_stream` method,
    which is specifically designed to yield ADK events in an A2A-compatible dictionary
    format. This executor\'s `_process_stream` method is tailored to handle this stream,
    including ADK-specific statuses like "auth_required", before delegating common
    status handling to `BaseA2AExecutor._handle_stream_event`.

    It leverages common functionality from `BaseA2AExecutor` for task management,
    initial request checks, and cancellation.

    Attributes:
        agent (GoogleADKAgent): The instance of `GoogleADKAgent` to be executed.
    '''
    agent: GoogleADKAgent
    def __init__(self, agent: GoogleADKAgent) -> None:
        """Initializes the GoogleADKExecutor.

        Args:
            agent (GoogleADKAgent): A fully initialized instance of `GoogleADKAgent`.

        Raises:
            TypeError: If `agent` is not an instance of `GoogleADKAgent`.
        """
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Processes an incoming agent request using the `GoogleADKAgent`.

        This method first performs initial checks using `_handle_initial_execute_checks`
        from the base class. If successful, it prepares the `_process_stream` coroutine
        and passes it to `_execute_agent_processing` (also from the base class) to
        manage its execution lifecycle. The `_process_stream` method is responsible for
        calling the agent's `arun_a2a_stream` and handling its ADK-specific output.

        Args:
            context (RequestContext): The A2A request context containing message details,
                task ID, and context ID.
            event_queue (EventQueue): The queue for sending A2A events (task status,
                artifacts) back to the server.
        """
