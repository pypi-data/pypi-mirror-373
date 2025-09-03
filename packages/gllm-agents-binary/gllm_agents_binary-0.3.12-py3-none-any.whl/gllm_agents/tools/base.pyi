from langchain_core.tools import BaseTool as LangchainBaseTool
from typing import Any

class BaseTool(LangchainBaseTool):
    """Base class for tools inheriting from Langchain's BaseTool.

    Tools should inherit from this class and implement the _run and optionally
    _arun methods.

    Attributes:
        name (str): The name of the tool.
        description (str): A description of what the tool does.
        args_schema (Optional[Type[Any]]): The schema for the tool's arguments.
        return_direct (bool): Whether to return the tool's output directly.
    """
    name: str
    description: str
    args_schema: type[Any] | None
    return_direct: bool
    def run(self, tool_input: Any, **_kwargs: Any) -> Any:
        """Run the tool synchronously. (Not Implemented)

        This method is intentionally not implemented to encourage asynchronous
        operations via the `arun` method.

        Args:
            tool_input: The input for the tool.
            **_kwargs: Unused. Additional keyword arguments.

        Raises:
            NotImplementedError: Always raised.
        """
    async def arun(self, tool_input: Any, **_kwargs: Any) -> Any:
        """Run the tool asynchronously.

        Args:
            tool_input: The input for the tool.
            **_kwargs: Unused. Additional keyword arguments.

        Returns:
            The output of the tool.
        """
    async def __call__(self, tool_input: Any) -> Any:
        """Allows the tool instance to be called asynchronously."""
