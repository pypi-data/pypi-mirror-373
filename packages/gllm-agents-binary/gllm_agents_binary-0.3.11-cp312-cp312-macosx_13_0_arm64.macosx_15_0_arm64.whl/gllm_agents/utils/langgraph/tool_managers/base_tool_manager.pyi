import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from langchain_core.tools import BaseTool as BaseTool
from typing import Any

logger: Incomplete

class BaseLangGraphToolManager(ABC, metaclass=abc.ABCMeta):
    """Base class for managing specialized tools in LangGraph agents.

    This abstract base class provides a common interface for tool managers
    that convert different types of capabilities into LangChain tools for
    use in LangGraph agents.

    The design follows a simple pattern:
    1. Register resources (agents, cards, etc.)
    2. Convert resources to LangChain tools
    3. Provide access to created tools
    """
    created_tools: list[BaseTool]
    def __init__(self) -> None:
        """Initialize the tool manager."""
    @abstractmethod
    def register_resources(self, resources: list[Any]) -> list[BaseTool]:
        """Register resources and convert them to LangChain tools.

        Args:
            resources: List of resources to convert to tools.

        Returns:
            List of created tools.
        """
    def get_tools(self) -> list[BaseTool]:
        """Get all created tools.

        Returns:
            Copy of created tools list.
        """
    def clear_tools(self) -> None:
        """Clear all created tools."""
    @abstractmethod
    def get_resource_names(self) -> list[str]:
        """Get names of all registered resources.

        Returns:
            List of resource names.
        """
