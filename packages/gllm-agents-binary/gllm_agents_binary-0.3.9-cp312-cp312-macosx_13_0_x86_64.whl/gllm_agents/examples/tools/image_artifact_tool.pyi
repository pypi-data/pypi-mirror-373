from gllm_agents.a2a.types import MimeType as MimeType
from gllm_agents.utils.artifact_helpers import create_artifact_response as create_artifact_response, create_error_response as create_error_response
from langchain_core.tools import BaseTool
from pydantic import BaseModel

class ImageArtifactInput(BaseModel):
    """Input schema for image artifact tool."""
    width: int
    height: int
    color: str
    text: str
    image_name: str

class ImageArtifactTool(BaseTool):
    """Tool that generates simple images with artifact support.

    This tool demonstrates the standardized artifact format for binary data by:
    1. Generating a simple image using PIL
    2. Providing a confirmation message for the agent
    3. Creating an image file artifact for the user
    """
    name: str
    description: str
    args_schema: type[BaseModel]
