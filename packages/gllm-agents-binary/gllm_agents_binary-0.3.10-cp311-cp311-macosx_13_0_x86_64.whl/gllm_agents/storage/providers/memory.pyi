from gllm_agents.storage.providers.base import BaseStorageProvider as BaseStorageProvider, StorageError as StorageError
from typing import Any

class InMemoryStorageProvider(BaseStorageProvider):
    """In-memory storage provider for fast access to small data.

    This provider stores all data in memory, providing the fastest
    access times but limited by available RAM.

    Best for:
    - Small to medium datasets
    - Temporary storage
    - Development and testing
    - High-frequency access patterns
    """
    def __init__(self) -> None:
        """Initialize in-memory storage."""
    def store(self, key: str, data: Any) -> None:
        """Store data in memory.

        Args:
            key: Unique identifier for the data
            data: Data to store

        Raises:
            StorageError: If storage operation fails
        """
    def retrieve(self, key: str) -> Any:
        """Retrieve data from memory.

        Args:
            key: Unique identifier for the data

        Returns:
            The stored data

        Raises:
            KeyError: If key not found
        """
    def exists(self, key: str) -> bool:
        """Check if key exists in memory.

        Args:
            key: Unique identifier to check

        Returns:
            True if key exists, False otherwise
        """
    def delete(self, key: str) -> None:
        """Delete data from memory.

        Args:
            key: Unique identifier for the data
        """
    def list_keys(self, prefix: str = '') -> list[str]:
        """List all keys with optional prefix.

        Args:
            prefix: Optional prefix to filter keys

        Returns:
            List of matching keys
        """
    def clear(self) -> None:
        """Clear all data from memory."""
    @property
    def size_bytes(self) -> int:
        """Get approximate memory usage in bytes.

        Returns:
            Approximate memory usage in bytes
        """
    @property
    def count(self) -> int:
        """Get number of stored items.

        Returns:
            Number of items in storage
        """
