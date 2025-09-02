from gllm_agents.a2a.types import MimeType as MimeType
from gllm_agents.utils.artifact_helpers import create_artifact_command as create_artifact_command
from langchain_core.tools import BaseTool
from pydantic import BaseModel
from typing import Any

class ChartInput(BaseModel):
    """Input schema for chart generation."""
    data_source: Any
    chart_type: str
    title: str

class DataVisualizerTool(BaseTool):
    """Tool that creates visualizations with automatic output storage."""
    name: str
    description: str
    args_schema: type[BaseModel]
