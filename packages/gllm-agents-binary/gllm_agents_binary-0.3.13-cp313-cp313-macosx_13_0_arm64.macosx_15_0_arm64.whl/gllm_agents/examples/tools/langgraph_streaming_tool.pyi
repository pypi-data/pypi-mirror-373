from gllm_agents.agent.langgraph_react_agent import LangGraphReactAgent as LangGraphReactAgent
from gllm_agents.examples.tools.langchain_weather_tool import weather_tool as weather_tool
from gllm_agents.examples.tools.time_tool import TimeTool as TimeTool
from langchain_core.runnables import RunnableConfig as RunnableConfig
from langchain_core.tools import BaseTool
from pydantic import BaseModel
from typing import Any

class StreamingToolConfig(BaseModel):
    """Tool configuration schema for the LangGraph streaming tool."""
    time_format: str

class LangGraphStreamingToolInput(BaseModel):
    """Input schema for the LangGraphStreamingTool."""
    query: str

class LangGraphStreamingTool(BaseTool):
    """Tool that wraps a LangGraph agent with time and weather forecast capabilities."""
    name: str
    description: str
    args_schema: type[BaseModel]
    tool_config_schema: type[BaseModel]
    def __init__(self, model: Any = None, **kwargs) -> None:
        """Initialize the LangGraphStreamingTool.

        Args:
            model: The model to use for the agent.
            **kwargs: Additional keyword arguments.
        """
    @property
    def agent(self):
        """Access the internal agent."""
    async def arun_streaming(self, query: str = None, config: RunnableConfig = None, **kwargs):
        """Execute the LangGraph agent asynchronously with A2A streaming output.

        Args:
            query: The query to execute.
            config: Tool configuration containing user context and preferences.
            **kwargs: Additional keyword arguments.

        Returns:
            An async generator that yields streaming events.
        """
