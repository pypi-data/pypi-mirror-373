from _typeshed import Incomplete
from a2a.types import AgentCard as AgentCard
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from gllm_agents.utils.metadata_helper import Kind as Kind, MetadataTimeTracker as MetadataTimeTracker, Status as Status, create_metadata as create_metadata
from pydantic import BaseModel
from typing import Any, AsyncGenerator

logger: Incomplete

class ArtifactInfo(BaseModel):
    """Structured artifact information for A2A communication.

    This Pydantic model provides type safety and validation for artifact data
    exchanged between agents through the A2A protocol.
    """
    artifact_id: str | None
    name: str | None
    content_type: str | None
    mime_type: str | None
    file_name: str | None
    has_file_data: bool
    has_file_uri: bool
    file_data: str | None
    file_uri: str | None
    description: str | None
    parts: int | None

class A2AConnector:
    """Handles A2A protocol communication between agents.

    This class provides methods for sending messages to other agents using the A2A protocol,
    supporting both synchronous and asynchronous communication patterns, as well as streaming
    responses with immediate artifact event handling.
    """
    @staticmethod
    def send_to_agent(agent_card: AgentCard, message: str | dict[str, Any], **kwargs: Any) -> dict[str, Any]:
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
            RuntimeError: If asend_to_agent encounters an unhandled exception.
        """
    @staticmethod
    async def asend_to_agent(agent_card: AgentCard, message: str | dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        '''Asynchronously sends a message to another agent using the A2A protocol.

        This method uses the streaming approach internally but only returns the final response,
        avoiding direct httpx usage that can cause issues with Nuitka compilation.

        Args:
            agent_card: The AgentCard instance containing the target agent\'s details including
                URL, authentication requirements, and capabilities.
            message: The message to send to the agent. Can be either a string for simple text
                messages or a dictionary for structured data.
            **kwargs: Additional keyword arguments.

        Returns:
            A dictionary containing the final response with the simplified structure:
                - status (str): "success" or "error"
                - task_state (str): Final A2A TaskState value
                - content (str): Final text content from the agent
                - task_id (str): ID of the associated task
                - context_id (str): Context ID of the task
                - final (bool): Always True for final responses
                - artifacts (list): List of all artifacts created during execution

        Raises:
            Exception: If there\'s an error during message sending or processing.
        '''
    @staticmethod
    async def astream_to_agent(agent_card: AgentCard, message: str | dict[str, Any], **kwargs: Any) -> AsyncGenerator[dict[str, Any], None]:
        '''Asynchronously sends a streaming message to another agent using the A2A protocol.

        This method supports streaming responses from the target agent, yielding chunks of
        the response as they become available. It handles the official A2A streaming event
        types as defined in the specification.

        Args:
            agent_card: The AgentCard instance containing the target agent\'s details including
                URL, authentication requirements, and capabilities.
            message: The message to send to the agent. Can be either a string for simple text
                messages or a dictionary for structured data.
            **kwargs: Additional keyword arguments.

        Yields:
            Dictionaries containing streaming response chunks with a simplified structure:

            For successful responses:
                - status (str): "success" or "error"
                - task_state (str): A2A TaskState value
                - content (str): Text content from the agent
                - task_id (str): ID of the associated task
                - context_id (str): Context ID of the task
                - final (bool): Whether this is the final update
                - artifacts (list, optional): List of artifacts created in this step

            Each artifact in the artifacts list contains:
                - artifact_id (str): ID of the artifact
                - name (str): Name of the artifact
                - content_type (str): "text" or "file"
                - mime_type (str): MIME type of the artifact
                - file_name (str, optional): Name of the file for file artifacts
                - has_file_data (bool): Whether file data is included
                - has_file_uri (bool): Whether file URI is included
                - file_data (str, optional): Base64 encoded file content
                - file_uri (str, optional): URI reference to the file

            For errors:
                - status (str): "error"
                - error_type (str): Type of error encountered
                - message (str): Error description

        Raises:
            httpx.HTTPError: If there\'s an HTTP-related error during the streaming request.
            Exception: For any other unexpected errors during message streaming or processing.
        '''
