import logging
from gllm_agents.tools.base import BaseTool as BaseTool
from gllm_agents.types import AgentProtocol as AgentProtocol
from gllm_core.event import EventEmitter as EventEmitter
from pydantic import BaseModel
from typing import Any

class NestedAgentTool(BaseTool):
    """Tool for wrapping an agent as a tool for use by another agent.

    This allows agents to delegate tasks to other specialized agents.
    The wrapped agent must conform to the AgentProtocol interface.

    Attributes:
        name: The name of the tool (derived from the agent's name).
        description: The description of the tool (derived from the agent's description).
        nested_agent: The agent to wrap as a tool.
        return_direct: Whether to return the result directly to the parent agent without
            additional processing. When True, the parent agent will receive the nested
            agent's response directly rather than incorporating it into its reasoning.
        logger: Logger for tracking tool execution.
    """
    name: str
    description: str
    nested_agent: AgentProtocol
    return_direct: bool
    logger: logging.Logger | None
    class ArgsSchema(BaseModel):
        """ArgsSchema is a Pydantic model that defines the schema for the arguments required by the nested agent.

        Attributes:
            query (str): User query to delegate to the nested agent. This field is required.
        """
        query: str
    args_schema: type[BaseModel]
    def __init__(self, nested_agent: AgentProtocol, **kwargs: Any) -> None:
        """Initialize the Tool class with an agent and additional data.

        Args:
            nested_agent (AgentProtocol): The agent instance to be wrapped.
            **kwargs (Any): Additional keyword arguments to pass to the parent constructor.

        Raises:
            ValueError: If the provided agent doesn't conform to AgentProtocol.
        """
