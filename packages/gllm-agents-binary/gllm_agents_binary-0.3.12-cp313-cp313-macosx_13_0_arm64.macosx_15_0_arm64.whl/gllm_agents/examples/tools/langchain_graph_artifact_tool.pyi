from gllm_agents.a2a.types import MimeType as MimeType
from gllm_agents.utils.artifact_helpers import create_artifact_command as create_artifact_command
from langchain_core.tools import BaseTool
from pydantic import BaseModel

class GraphCommandInput(BaseModel):
    """Input schema for a tiny bar/line chart artifact tool.

    Note: width/height are clamped to a small size to keep artifacts lightweight.
    """
    chart_type: str
    labels: list[str]
    values: list[float]
    title: str
    width: int
    height: int
    image_name: str

class GraphArtifactCommandTool(BaseTool):
    """Generate a very small PNG chart and return it as a Command artifact."""
    name: str
    description: str
    args_schema: type[BaseModel]
