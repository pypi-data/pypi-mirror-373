from _typeshed import Incomplete
from fastapi import FastAPI
from gllm_agents.examples.hello_world_langgraph import langgraph_example as langgraph_example
from gllm_agents.sentry import setup_telemetry as setup_telemetry
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager

logger: Incomplete
BASE_URL: str
SENTRY_ENVIRONMENT: Incomplete
USE_OPENTELEMETRY: Incomplete

def fetch_endpoints() -> None:
    """Fetch all endpoints from the server."""
def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: The configured FastAPI application.
    """
def run_server() -> None:
    """Run the FastAPI server."""
