from langchain_core.tools import BaseTool
from pydantic import BaseModel

FORMAT_STRING: str

class TimeToolInput(BaseModel):
    """Input schema for the TimeTool."""
    datetime_format: str

class TimeTool(BaseTool):
    """Tool to get the current time."""
    name: str
    description: str
    save_output_history: bool
    args_schema: type[BaseModel]
