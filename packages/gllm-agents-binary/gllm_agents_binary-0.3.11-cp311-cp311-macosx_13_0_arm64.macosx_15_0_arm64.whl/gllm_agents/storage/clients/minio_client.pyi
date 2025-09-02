from _typeshed import Incomplete
from dataclasses import dataclass
from gllm_agents.storage.base import BaseObjectStorageClient as BaseObjectStorageClient
from typing import BinaryIO

S3_ERR_NO_SUCH_KEY: str
S3_ERR_NO_SUCH_BUCKET: str
S3_ERR_ACCESS_DENIED: str

@dataclass
class MinioConfig:
    """Configuration for MinIO object storage client.

    Attributes:
        endpoint: MinIO server endpoint URL
        access_key: Access key for authentication
        secret_key: Secret key for authentication
        bucket: Bucket name to use for storage
        secure: Whether to use HTTPS (defaults to True)
    """
    endpoint: str
    access_key: str
    secret_key: str
    bucket: str
    secure: bool = ...
    @classmethod
    def from_env(cls) -> MinioConfig:
        """Create MinioConfig from environment variables.

        Expected environment variables:
        - OBJECT_STORAGE_URL
        - OBJECT_STORAGE_USER
        - OBJECT_STORAGE_PASSWORD
        - OBJECT_STORAGE_BUCKET
        - OBJECT_STORAGE_SECURE (optional, defaults to True)

        Returns:
            MinioConfig instance

        Raises:
            ValueError: If required environment variables are not set
        """

class MinioObjectStorage(BaseObjectStorageClient):
    """Implementation of ObjectStorageInterface using Minio."""
    config: Incomplete
    client: Incomplete
    bucket: Incomplete
    def __init__(self, config: MinioConfig | None = None, ensure_bucket: bool = True) -> None:
        """Initialize MinioObjectStorage with configuration.

        Args:
            config: MinioConfig instance. If None, will attempt to load from environment variables.
            ensure_bucket: Whether to ensure bucket exists during initialization (optional). Defaults to True.

        Raises:
            ValueError: If configuration is invalid or incomplete
        """
    def upload(self, object_key: str, file_stream: bytes | BinaryIO, filename: str | None = None, content_type: str | None = None, metadata: dict[str, str] | None = None) -> str:
        """Upload data to Minio object storage.

        Args:
            object_key: The key to store the object under
            file_stream: The data to upload (bytes or file-like object)
            filename: The filename of the data (optional)
            content_type: The content type of the data (optional)
            metadata: Additional metadata to store with the object (optional)

        Returns:
            The object key of the uploaded data

        Raises:
            ValueError: If the file stream is empty or invalid
            ConnectionError: If there's an issue connecting to Minio
            Exception: For other unexpected errors during upload
        """
    def get(self, object_key: str) -> bytes:
        """Get data from Minio object storage.

        Args:
            object_key: The key of the object to retrieve

        Returns:
            The object data as bytes

        Raises:
            KeyError: If the object is not found
            ConnectionError: If there's a network or connection issue
        """
    def delete(self, object_key: str) -> None:
        """Delete data from Minio object storage.

        Args:
            object_key: The key of the object to delete

        Raises:
            ConnectionError: If there's a network or connection issue
        """
    def object_exists(self, object_key: str) -> bool:
        """Check if an object exists in the MinIO bucket.

        Args:
            object_key: The key of the object to check.

        Returns:
            True if the object exists, False otherwise.

        Raises:
            ConnectionError: If there's a network or connection issue (excluding not found errors)
        """
    def list_objects(self, prefix: str = '') -> list[str]:
        """List objects in the bucket with optional prefix filter.

        Args:
            prefix: Optional prefix to filter objects

        Returns:
            List of object keys

        Raises:
            ConnectionError: If there's an issue listing objects
        """
    def generate_presigned_url(self, object_key: str, expires: int = 24, response_headers: dict[str, str] | None = None) -> str:
        """Generate a presigned URL for accessing the object.

        Args:
            object_key: The key of the object
            expires: Expiration time in hours (defaults to 24)
            response_headers: Additional response headers (optional)

        Returns:
            A presigned URL

        Raises:
            ValueError: If expiration time is not positive
            ConnectionError: If there's an issue generating the URL
        """
