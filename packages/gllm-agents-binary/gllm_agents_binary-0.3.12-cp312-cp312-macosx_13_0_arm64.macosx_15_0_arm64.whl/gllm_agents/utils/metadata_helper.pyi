from _typeshed import Incomplete
from enum import StrEnum
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from typing import Any

logger: Incomplete
METADATA_STATUS_KEY: str
TIME_KEY: str
FINAL_RESPONSE_MESSAGE: str

class Kind(StrEnum):
    """Constants for metadata kind values."""
    AGENT_STEP = 'agent_step'
    FINAL_RESPONSE = 'final_response'
    AGENT_DEFAULT = 'agent_default'

class Status(StrEnum):
    """Constants for metadata status values."""
    RUNNING = 'running'
    FINISHED = 'finished'
    STOPPED = 'stopped'

class MetadataTimeTracker:
    """Tracks cumulative execution time across agent steps for final response metadata.

    This class provides a clean way to accumulate execution times from individual
    agent steps and apply the total time to final response metadata.
    """
    def __init__(self) -> None:
        """Initialize the time tracker with zero accumulated time."""
    def update_response_metadata(self, response: dict[str, Any]) -> dict[str, Any]:
        """Update response metadata with accumulated time tracking.

        Args:
            response: Response dictionary containing metadata

        Returns:
            Response with updated metadata for final responses. If any error occurs,
            returns the original response unchanged.
        """

def detect_agent_step_content(content: str, default_kind: str, tool_calls: Any | None = None) -> str:
    """Detect if content corresponds to agent step patterns from LangGraph.

    Args:
        content: The content to detect.
        default_kind: The default kind to return if the content does not match any of the patterns.
        tool_calls: The tool calls to detect.

    Returns:
        The kind of the content.
    """
def create_metadata(content: str = '', kind: str = ..., status: str = ..., tool_calls: Any | None = None, is_final: bool = False, time: float | None = None, existing_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create metadata for A2A responses with content-based message.

    Args:
        content: The content to create metadata for.
        kind: The kind of the content.
        status: The status of the content.
        tool_calls: The tool calls to create metadata for.
        is_final: Whether the content is final.
        time: The time of the content.
        existing_metadata: Optional existing metadata to merge with. Existing metadata
            takes precedence over generated metadata for conflicting keys.

    Returns:
        The metadata for the content, merged with existing metadata if provided.
    """
