from _typeshed import Incomplete
from langchain_core.tools import BaseTool
from pydantic import BaseModel

logger: Incomplete

class GoogleSerperInput(BaseModel):
    """Input schema for the GoogleSerperTool."""
    query: str

class MockGoogleSerperTool(BaseTool):
    """Mock Tool to simulate Google Serper API results for testing."""
    name: str
    description: str
    save_output_history: bool
    args_schema: type[BaseModel]
