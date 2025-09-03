import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from typing import Any

logger: Incomplete

class StorageError(Exception):
    """Base exception for storage operations."""

class BaseStorageProvider(ABC, metaclass=abc.ABCMeta):
    """Base interface for storage providers.

    This abstract class defines the contract that all storage providers
    must implement to store and retrieve tool outputs.
    """
    @abstractmethod
    def store(self, key: str, data: Any) -> None:
        """Store data with the given key.

        Args:
            key: Unique identifier for the data
            data: Data to store (must be serializable)

        Raises:
            StorageError: If storage operation fails
        """
    @abstractmethod
    def retrieve(self, key: str) -> Any:
        """Retrieve data by key.

        Args:
            key: Unique identifier for the data

        Returns:
            The stored data

        Raises:
            KeyError: If key not found
            StorageError: If retrieval operation fails
        """
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists.

        Args:
            key: Unique identifier to check

        Returns:
            True if key exists, False otherwise
        """
    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete data by key.

        Args:
            key: Unique identifier for the data

        Note:
            Should not raise error if key doesn't exist
        """
    @abstractmethod
    def list_keys(self, prefix: str = '') -> list[str]:
        """List all keys with optional prefix filter.

        Args:
            prefix: Optional prefix to filter keys

        Returns:
            List of matching keys
        """
    @abstractmethod
    def clear(self) -> None:
        """Clear all stored data.

        Warning:
            This operation is irreversible
        """
    def get_presigned_url(self, key: str, expires_hours: int = 24) -> str | None:
        """Generate presigned URL for direct access (optional).

        Args:
            key: Storage key
            expires_hours: URL expiration in hours

        Returns:
            Presigned URL if supported, None otherwise
        """
