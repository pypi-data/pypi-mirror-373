from langchain_core.tools import BaseTool
from pydantic import BaseModel
from typing import Literal

class DataInput(BaseModel):
    """Input schema for data generation."""
    data_type: Literal['sales', 'scores', 'growth']
    size: int

class DataGeneratorTool(BaseTool):
    """Tool that generates sample datasets with automatic output storage."""
    name: str
    description: str
    args_schema: type[BaseModel]
    store_final_output: bool
