from dataclasses import dataclass
from enum import StrEnum
from gllm_agents.storage.base import BaseObjectStorageClient as BaseObjectStorageClient
from gllm_agents.storage.clients.minio_client import MinioConfig as MinioConfig, MinioObjectStorage as MinioObjectStorage
from gllm_agents.storage.providers.base import BaseStorageProvider as BaseStorageProvider
from gllm_agents.storage.providers.memory import InMemoryStorageProvider as InMemoryStorageProvider
from gllm_agents.storage.providers.object_storage import ObjectStorageProvider as ObjectStorageProvider

OBJECT_STORAGE_PREFIX: str

class StorageType(StrEnum):
    """Supported storage types."""
    MEMORY = 'memory'
    OBJECT_STORAGE = 'object_storage'

@dataclass
class StorageConfig:
    """Configuration for storage providers.

    Attributes:
        storage_type: Type of storage to use
        object_prefix: Prefix for object storage keys (like a directory path)
        object_use_json: Use JSON serialization instead of pickle for object storage
    """
    storage_type: StorageType = ...
    object_prefix: str = ...
    object_use_json: bool = ...
    @classmethod
    def from_env(cls) -> StorageConfig:
        '''Create StorageConfig from environment variables.

        Environment variables:
        - TOOL_OUTPUT_STORAGE_TYPE: "memory" or "object_storage"
        - TOOL_OUTPUT_OBJECT_PREFIX: Prefix for object storage keys
        - TOOL_OUTPUT_USE_JSON: "true" to use JSON serialization

        Returns:
            StorageConfig instance
        '''

class StorageProviderFactory:
    """Factory for creating storage providers based on configuration."""
    @staticmethod
    def create(config: StorageConfig, object_storage_client: BaseObjectStorageClient | None = None) -> BaseStorageProvider:
        """Create storage provider based on configuration.

        Args:
            config: Storage configuration
            object_storage_client: Object storage client (required for object storage)

        Returns:
            Configured storage provider

        Raises:
            ValueError: If configuration is invalid
        """
    @staticmethod
    def create_from_env(object_storage_client: BaseObjectStorageClient | None = None) -> BaseStorageProvider:
        """Create storage provider from environment variables.

        Args:
            object_storage_client: Optional object storage client

        Returns:
            Configured storage provider
        """
