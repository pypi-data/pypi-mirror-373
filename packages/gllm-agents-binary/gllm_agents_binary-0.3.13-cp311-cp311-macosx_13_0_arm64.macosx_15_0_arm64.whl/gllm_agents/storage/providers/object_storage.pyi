from _typeshed import Incomplete
from gllm_agents.storage.base import BaseObjectStorageClient as BaseObjectStorageClient
from gllm_agents.storage.providers.base import BaseStorageProvider as BaseStorageProvider, StorageError as StorageError
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from typing import Any

logger: Incomplete

class ObjectStorageProvider(BaseStorageProvider):
    """Object storage provider for S3-compatible storage.

    Works with any S3-compatible storage including AWS S3, MinIO,
    Google Cloud Storage (with S3 compatibility), etc.

    Best for:
    - Very large datasets
    - Distributed systems
    - Cloud deployments
    - Long-term storage
    - Multi-region access
    """
    client: Incomplete
    prefix: Incomplete
    use_json: Incomplete
    def __init__(self, client: BaseObjectStorageClient, prefix: str = '', use_json: bool = False) -> None:
        """Initialize object storage provider.

        Args:
            client: Object storage client instance
            prefix: Prefix for all keys (like a directory)
            use_json: Use JSON format (True) or pickle (False)
        """
    def store(self, key: str, data: Any) -> None:
        """Store data in object storage.

        Args:
            key: Unique identifier for the data
            data: Data to store

        Raises:
            StorageError: If storage operation fails
        """
    def retrieve(self, key: str) -> Any:
        """Retrieve data from object storage.

        Args:
            key: Unique identifier for the data

        Returns:
            The stored data

        Raises:
            KeyError: If key not found
            StorageError: If retrieval operation fails
        """
    def exists(self, key: str) -> bool:
        """Check if object exists.

        Args:
            key: Unique identifier to check

        Returns:
            True if key exists, False otherwise
        """
    def delete(self, key: str) -> None:
        """Delete object.

        Args:
            key: Unique identifier for the data
        """
    def list_keys(self, prefix: str = '') -> list[str]:
        """List all keys with optional prefix.

        Args:
            prefix: Optional prefix to filter keys

        Raises:
            NotImplementedError: list_keys is not implemented
        """
    def clear(self) -> None:
        """Clear all objects with the configured prefix.

        Warning:
            This is a dangerous operation!
        """
    def get_presigned_url(self, key: str, expires_hours: int = 24) -> str | None:
        """Generate presigned URL for direct access.

        Args:
            key: Storage key
            expires_hours: URL expiration in hours

        Returns:
            Presigned URL for direct access

        Raises:
            StorageError: If URL generation fails
        """
