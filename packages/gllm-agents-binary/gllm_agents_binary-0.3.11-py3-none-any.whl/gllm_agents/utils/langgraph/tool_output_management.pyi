from _typeshed import Incomplete
from dataclasses import dataclass
from datetime import datetime, timedelta
from gllm_agents.storage.providers.base import BaseStorageProvider as BaseStorageProvider, StorageError as StorageError
from gllm_agents.storage.providers.memory import InMemoryStorageProvider as InMemoryStorageProvider
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from typing import Any

logger: Incomplete
STRING_TRUNCATION_LENGTH: int
MAX_TOOL_ARGS_DISPLAY: int
DATA_PREVIEW_TRUNCATION_LENGTH: int
TOOL_OUTPUT_REFERENCE_PREFIX: str

class ToolReferenceError(Exception):
    """Specialized exception for tool output reference resolution errors.

    This exception is raised when there are issues with resolving tool output references,
    such as invalid reference syntax, missing outputs, or security violations.

    Attributes:
        reference: The original reference string that caused the error.
        call_id: The call ID that was attempted to be resolved, if applicable.
        details: Additional error details for debugging.
    """
    reference: Incomplete
    call_id: Incomplete
    details: Incomplete
    def __init__(self, message: str, reference: str | None = None, call_id: str | None = None, details: dict[str, Any] | None = None) -> None:
        """Initialize a ToolReferenceError.

        Args:
            message: Human-readable error message describing what went wrong.
            reference: The original reference string that caused the error, if applicable.
            call_id: The call ID that was attempted to be resolved, if applicable.
            details: Additional error details for debugging, if applicable.
        """

@dataclass
class ToolOutputConfig:
    """Configuration for tool output management system.

    This class defines the operational parameters for the tool output management
    system, including storage limits, cleanup intervals, and lifecycle policies.

    Attributes:
        max_stored_outputs: Maximum number of tool outputs to store simultaneously.
            When this limit is reached, oldest outputs are evicted. Defaults to 100.
        max_age_minutes: Maximum age in minutes for stored outputs before they
            become eligible for cleanup. Defaults to 60 minutes.
        cleanup_interval: Number of tool calls between automatic cleanup operations.
            Set to 0 to disable automatic cleanup. Defaults to 20.
        storage_provider: Optional storage provider for persistent storage.
            If None, uses in-memory storage (backward compatible). Defaults to None.
    """
    max_stored_outputs: int = ...
    max_age_minutes: int = ...
    cleanup_interval: int = ...
    storage_provider: BaseStorageProvider | None = ...

@dataclass
class ToolOutput:
    """Container for tool outputs with optional data payload.

    This class represents tool output metadata and optionally the actual data.
    When used as metadata only, the data field is None and must be retrieved
    from storage. When loaded with data, it contains the complete output.

    Attributes:
        call_id: Unique identifier for this tool call, used for reference resolution.
        tool_name: Name of the tool that produced this output.
        timestamp: When this output was created and stored.
        size_bytes: Approximate size of the stored data in bytes for memory management.
        tool_args: Input arguments that were passed to the tool for this call.
        data: Optional actual output data. None when used as metadata only.
        data_description: Optional human-readable description of the data content,
            typically provided by the tool itself.
        tags: Optional list of tags for categorization and filtering.
        agent_name: Name of the agent that created this output, for multi-agent context.
    """
    call_id: str
    tool_name: str
    timestamp: datetime
    size_bytes: int
    tool_args: dict[str, Any]
    data: Any | None = ...
    data_description: str | None = ...
    tags: list[str] | None = ...
    agent_name: str | None = ...
    @property
    def is_metadata_only(self) -> bool:
        """Check if this instance contains only metadata without data."""
    def is_expired(self, max_age: timedelta) -> bool:
        """Check if this output has expired based on the given maximum age."""
    def get_data_preview(self, max_length: int = 200, storage_provider: BaseStorageProvider | None = None, thread_id: str | None = None) -> str | None:
        """Get a truncated string representation of the stored data.

        Args:
            max_length: Maximum length of the preview string.
            storage_provider: Required only if data is not loaded.
            thread_id: Thread ID required for proper storage key generation.

        Returns:
            A string representation of the data, truncated if necessary. None if data is not found.
        """
    def with_data(self, data: Any) -> ToolOutput:
        """Create a new instance with data populated.

        Returns a new ToolOutput instance with the same metadata but with
        data field populated. Useful for converting metadata-only instances
        to complete instances.
        """

@dataclass
class StoreOutputParams:
    """Parameters for storing tool outputs.

    Reduces the number of arguments passed to store_output method.

    Attributes:
        call_id: Unique identifier for this tool call.
        tool_name: Name of the tool that produced the output.
        data: The actual output data to store.
        tool_args: Input arguments used for the tool call.
        thread_id: Thread/conversation ID to organize outputs by conversation.
        description: Optional human-readable description of the output.
        tags: Optional list of tags for categorization.
        agent_name: Name of the agent that created this output.
    """
    call_id: str
    tool_name: str
    data: Any
    tool_args: dict[str, Any]
    thread_id: str
    description: str | None = ...
    tags: list[str] | None = ...
    agent_name: str | None = ...

class ToolOutputManager:
    """Production-ready tool output manager with comprehensive lifecycle management.

    This class provides centralized management of tool outputs including storage,
    retrieval, lifecycle management, and LLM-friendly summarization. It handles
    memory management through configurable cleanup policies and provides secure
    access to stored outputs.

    Key Features:
    - Automatic and manual storage of tool outputs with metadata
    - Configurable lifecycle management with age and size-based eviction
    - LLM-friendly summary generation with data previews and context
    - Memory management with size tracking and cleanup
    - Thread-safe operations with proper error handling and locking
    - Concurrent access support for multi-agent and parallel processing scenarios

    Attributes:
        config: Configuration object defining operational parameters.
    """
    config: Incomplete
    def __init__(self, config: ToolOutputConfig) -> None:
        """Initialize the ToolOutputManager with the given configuration.

        Args:
            config: Configuration object defining storage limits and cleanup policies.
        """
    def store_output(self, params: StoreOutputParams) -> None:
        """Store a tool output with automatic cleanup and size management.

        This method stores a tool output along with its metadata, automatically
        handling size limits, cleanup, and memory management. If the same call_id
        is used multiple times within the same thread, the previous output will be overwritten.

        Thread-safe: This method uses internal locking to ensure safe concurrent access.

        Args:
            params: StoreOutputParams containing all necessary parameters including thread_id.

        Raises:
            Exception: If storage operation fails for any reason.
        """
    def get_output(self, call_id: str, thread_id: str) -> ToolOutput | None:
        """Retrieve a stored tool output by its call ID and thread ID.

        Thread-safe: This method uses internal locking to ensure safe concurrent access.

        Args:
            call_id: The unique identifier for the tool call.
            thread_id: The thread/conversation ID to search in.

        Returns:
            The ToolOutput object with data if found, None otherwise.
        """
    def has_outputs(self, thread_id: str | None = None) -> bool:
        """Check if any outputs are currently stored.

        Thread-safe: This method uses internal locking to ensure safe concurrent access.

        Args:
            thread_id: Optional thread ID to check for outputs in a specific thread.
                If None, checks across all threads.

        Returns:
            True if there are stored outputs, False otherwise.
        """
    def generate_summary(self, thread_id: str, max_entries: int = 10) -> str:
        """Generate an LLM-friendly structured summary as JSON.

        This method creates a comprehensive, structured summary of stored outputs that
        can be easily parsed by LLMs and other systems. The JSON format provides rich
        metadata and context about each tool output.

        Thread-safe: This method uses internal locking to ensure safe concurrent access.

        Args:
            thread_id: Thread ID to generate summary for.
            max_entries: Maximum number of entries to include in the summary.
                Defaults to 10.

        Returns:
            A JSON string containing structured data about tool outputs. Always returns
            valid JSON, even when no outputs are stored (empty entries list).
        """
    def get_stats(self) -> dict[str, Any]:
        """Get thread-safe statistics about the current state of the manager.

        Args:
            thread_id: Thread ID to generate summary for.
            max_entries: Maximum number of entries to include in the summary.
            Defaults to 10.

        Returns:
            Dictionary containing current statistics including output count,
            total size, call count, and thread information.
        """
    def clear_all_outputs(self) -> int:
        """Clear all stored outputs and reset counters.

        Thread-safe: This method uses internal locking to ensure safe concurrent access.

        Returns:
            Number of outputs that were cleared.
        """
    def clear_thread_outputs(self, thread_id: str) -> int:
        """Clear all stored outputs for a specific thread.

        Thread-safe: This method uses internal locking to ensure safe concurrent access.

        Args:
            thread_id: The thread ID to clear outputs for.

        Returns:
            Number of outputs that were cleared for the thread.
        """
    def clear_all(self) -> None:
        """Clear all stored outputs from both metadata and storage.

        Warning:
            This operation is irreversible and will remove all stored tool outputs.
        """
    def get_storage_stats(self) -> dict[str, Any]:
        """Get storage statistics for monitoring and debugging.

        Returns:
            Dictionary containing storage statistics.
        """

class ToolReferenceResolver:
    """Secure and efficient tool output reference resolution system.

    This class handles the resolution of tool output references in a secure manner,
    preventing injection attacks while providing simple and reliable access to
    stored tool outputs. It uses a whitelist approach with regex validation to
    ensure only safe references are processed.

    Security Features:
    - Strict regex pattern matching for reference syntax
    - Whitelist-based validation to prevent injection attacks
    - Fail-fast error handling with detailed error messages
    - Input sanitization and validation at multiple levels

    Supported Reference Syntax:
    - $tool_output.<call_id> - Direct reference to a tool output by call ID

    Attributes:
        config: Configuration object for operational parameters.
    """
    config: Incomplete
    def __init__(self, config: ToolOutputConfig) -> None:
        """Initialize the ToolReferenceResolver with security configuration.

        Args:
            config: Configuration object defining operational parameters.
        """
    def resolve_references(self, args: dict[str, Any], manager: ToolOutputManager, thread_id: str | None = None) -> dict[str, Any]:
        """Resolve all tool output references in the given arguments dictionary.

        This method recursively processes a dictionary of tool arguments, finding
        and resolving any tool output references. It supports nested dictionaries
        and lists, providing comprehensive reference resolution.

        Args:
            args: Dictionary of tool arguments that may contain references.
            manager: ToolOutputManager instance to resolve references against.
            thread_id: Optional thread ID for context-aware resolution.

        Returns:
            New dictionary with all references resolved to their actual values.

        Raises:
            ToolReferenceError: If any reference is invalid or cannot be resolved.
        """
