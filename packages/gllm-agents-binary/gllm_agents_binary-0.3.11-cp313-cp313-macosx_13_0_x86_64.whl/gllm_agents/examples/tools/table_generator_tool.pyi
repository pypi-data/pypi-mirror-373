from gllm_agents.a2a.types import MimeType as MimeType
from gllm_agents.utils.artifact_helpers import create_artifact_response as create_artifact_response
from langchain_core.tools import BaseTool
from pydantic import BaseModel

class TableGeneratorInput(BaseModel):
    """Input schema for table generator tool."""
    rows: int
    columns: list[str]
    table_name: str

class TableGeneratorTool(BaseTool):
    """Tool that generates sample data tables with artifact support.

    This tool demonstrates the standardized artifact format by:
    1. Generating sample data
    2. Creating a markdown table for the agent's context
    3. Creating a CSV file artifact for the user
    """
    name: str
    description: str
    args_schema: type[BaseModel]
