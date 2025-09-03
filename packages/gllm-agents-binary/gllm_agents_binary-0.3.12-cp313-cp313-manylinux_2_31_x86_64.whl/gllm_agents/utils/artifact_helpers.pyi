from gllm_agents.a2a.types import Artifact as Artifact, ArtifactType as ArtifactType, MimeType as MimeType, get_mime_type_from_filename as get_mime_type_from_filename
from langgraph.types import Command
from typing import Any

class ArtifactHandler:
    """Handler class for creating and managing artifacts in agent tools.

    This class provides a clean, object-oriented interface for artifact creation
    with built-in validation, deduplication, and standardized formatting.
    """
    def __init__(self) -> None:
        """Initialize the ArtifactHandler."""
    def create_file_artifact(self, result: str, artifact_data: bytes | str, artifact_name: str, artifact_description: str = '', mime_type: str | None = None, enable_deduplication: bool = True) -> dict[str, Any]:
        """Deprecated. Use create_artifact instead."""
    def create_text_artifact(self, result: str, artifact_text: str, artifact_name: str, artifact_description: str = '', mime_type: str | None = None, enable_deduplication: bool = True) -> dict[str, Any]:
        """Deprecated. Use create_artifact instead."""
    def create_artifact(self, result: str, data: bytes | str, artifact_name: str, artifact_description: str = '', mime_type: str | None = None, enable_deduplication: bool = True) -> dict[str, Any]:
        """Create an artifact with automatic text/binary handling.

        Args:
            result: The message/result to show to the agent.
            data: The data for the artifact. Bytes for binary; str for text or base64.
            artifact_name: The filename to present to users.
            artifact_description: Description of the artifact.
            mime_type: Optional MIME type. If None, inferred from filename.
            enable_deduplication: Whether to deduplicate by content hash.

        Returns:
            Dictionary with 'result' and 'artifact' keys.
        """
    def create_error_response(self, error_message: str) -> str:
        """Create a standardized error response for tools.

        Args:
            error_message: The error message to return.

        Returns:
            String with error information.
        """
    def clear_cache(self) -> None:
        """Clear the artifact cache."""
    def get_cache_size(self) -> int:
        """Get the number of cached artifacts.

        Returns:
            Number of artifacts in cache.
        """
    @staticmethod
    def generate_artifact_hash(artifact_data: str, name: str, mime_type: str) -> str:
        """Generate a hash for artifact deduplication.

        Args:
            artifact_data: Base64 encoded artifact data.
            name: Artifact name.
            mime_type: MIME type.

        Returns:
            Hash string for deduplication.
        """

def create_artifact_response(result: str, artifact_data: bytes | str, artifact_name: str, artifact_description: str = '', mime_type: str | None = None) -> dict[str, Any]:
    '''Create a standardized artifact response for tools.

    This function creates a response that separates the agent-facing result
    from the user-facing artifact, following the established pattern for
    artifact generation in the agent system.

    Args:
        result: The message/result to show to the agent (clean, no file data).
        artifact_data: The binary data or base64 string for the artifact.
        artifact_name: The name for the artifact file.
        artifact_description: Description of the artifact. Defaults to "".
        mime_type: MIME type of the artifact. If None, will be auto-detected from filename.

    Returns:
        Dictionary with \'result\' and \'artifacts\' keys (artifacts is always a list).

    Example:
        >>> import io
        >>> csv_data = "Name,Age\\\\nAlice,30\\\\nBob,25"
        >>> response = create_artifact_response(
        ...     result="Generated a 2-row CSV table",
        ...     artifact_data=csv_data.encode(\'utf-8\'),
        ...     artifact_name="data.csv",
        ...     artifact_description="Sample data table",
        ...     mime_type="text/csv"
        ... )
        >>> assert "result" in response
        >>> assert "artifacts" in response
        >>> assert isinstance(response["artifacts"], list)
    '''
def create_text_artifact_response(result: str, artifact_text: str, artifact_name: str, artifact_description: str = '', mime_type: str | None = None) -> dict[str, Any]:
    """Create a standardized artifact response for tools.

    Args:
        result: The message/result to show to the agent.
        artifact_text: The text content for the artifact.
        artifact_name: The name for the artifact file.
        artifact_description: Description of the artifact.
        mime_type: MIME type of the artifact. If None, will be auto-detected from filename.

    Returns:
        Dictionary with 'result' and 'artifacts' keys (artifacts is always a list).
    """
def create_multiple_artifacts_response(result: str, artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    """Create a standardized response for multiple artifacts.

    Args:
        result: The message/result to show to the agent.
        artifacts: List of artifact dictionaries.

    Returns:
        Dictionary with 'result' and 'artifacts' keys.
    """
def create_artifact_command(result: str, artifact_data: bytes | str, artifact_name: str, artifact_description: str = '', mime_type: str | None = None, metadata_update: dict[str, Any] | None = None) -> Command:
    """Create a Command that updates artifacts (and optional metadata).

    Args:
        result: Message/result to show to the agent (for ToolMessage content).
        artifact_data: The binary data or base64 string for the artifact.
        artifact_name: The name for the artifact file.
        artifact_description: Description of the artifact.
        mime_type: MIME type of the artifact. If None, auto-detected from filename.
        metadata_update: Optional metadata delta to merge into state metadata.

    Returns:
        Command: A LangGraph Command with update containing 'result', 'artifacts', and optional 'metadata'.
    """
def create_multiple_artifacts_command(result: str, artifacts: list[Artifact | dict[str, Any]] | None = None, metadata_update: dict[str, Any] | None = None) -> Command:
    """Create a Command that updates multiple artifacts (and optional metadata).

    The 'artifacts' list accepts mixed item types:
    - Artifact: a typed artifact model (preferred). Will be converted via model_dump().
    - dict: a prebuilt artifact dict ready for A2A.
    - DataSpec dict: raw spec to build an artifact with keys:
        {'data': bytes|str, 'artifact_name': str, 'artifact_description'?: str, 'mime_type'?: str}

    Args:
        result: Message/result to show to the agent.
        artifacts: List of items (Artifact | dict) to attach or build.
        metadata_update: Optional metadata delta to merge into state metadata.

    Returns:
        Command: A LangGraph Command with update containing 'result', 'artifacts', and optional 'metadata'.
    """
def create_error_response(error_message: str) -> str:
    """Create a standardized error response for tools.

    For error cases, we return a simple string that will be passed directly
    to the agent without any artifact processing.

    Args:
        error_message: The error message to return.

    Returns:
        String with error information.
    """
def extract_artifacts_from_agent_response(result: Any) -> tuple[str, list[dict[str, Any]]]:
    """Extract artifacts from agent response for delegation tools.

    Args:
        result: The result returned by the delegated agent.

    Returns:
        Tuple of (text_response, artifacts_list) where:
        - text_response: The text content for the agent
        - artifacts_list: List of artifacts to be passed through
    """
def create_delegation_response_with_artifacts(result: str, artifacts: list[dict[str, Any]], agent_name: str = '') -> Command:
    """Create a delegation response that includes artifacts only when needed.

    Args:
        result: The text result from the delegated agent.
        artifacts: List of artifacts from the delegated agent (always a list).
        agent_name: Name of the agent for prefixing the result.

    Returns:
        Command containing 'result' and optional 'artifacts'.
    """
