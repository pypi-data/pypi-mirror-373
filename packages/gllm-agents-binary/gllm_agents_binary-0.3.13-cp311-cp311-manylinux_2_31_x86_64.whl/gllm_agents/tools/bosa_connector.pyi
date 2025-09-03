from _typeshed import Incomplete
from bosa_connectors.connector import BosaConnector
from typing import Any

MAX_ATTEMPTS: int
logger: Incomplete

class BOSAConnector:
    """Handler for fetching data using the BOSA Connector."""
    bosa: BosaConnector
    def __init__(self, api_base_url: str, api_key: str) -> None:
        """Initialize the BOSA connector.

        Args:
            api_base_url: Base URL for the BOSA API
            api_key: API key for authentication
        """
    def execute_endpoint(self, action: str, endpoint: str, input_: dict[str, Any], max_attempts: int = ..., forwards_cursor: bool = True) -> dict[str, Any]:
        """Execute a BOSA endpoint and fetch data.

        Args:
            action: The BOSA API action to call
            endpoint: The BOSA API endpoint to call
            input_: Parameters matching the API spec
            max_attempts: Max retry attempts
            forwards_cursor: Whether to use cursor-based pagination (True) or page-based pagination (False)

        Returns:
            dict containing response data with '0', 'data', and 'meta' fields
        """
