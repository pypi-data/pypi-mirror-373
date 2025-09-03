from _typeshed import Incomplete
from gllm_agents.tools.base_bosa_tools import BaseBosaTool as BaseBosaTool
from gllm_agents.tools.constants import Action as Action, ActionEndpointMap as ActionEndpointMap
from langchain_core.tools import BaseTool as LangchainBaseTool
from pydantic import BaseModel

logger: Incomplete

class GitHubPRDetailsSchema(BaseModel):
    """Schema for retrieving details of specific GitHub Pull Requests."""
    repository: str
    pr_numbers: list[int]

class GitHubPRDetailsTool(BaseBosaTool, LangchainBaseTool):
    """Tool for retrieving details of specific pull requests."""
    name: str
    description: str
    args_schema: type[BaseModel]
    def __init__(self, **kwargs) -> None:
        """Initialize the GitHubPRDetailsTool.

        Calls both LangchainBaseTool and BaseBosaTool __init__ methods.

        Args:
            **kwargs: Additional keyword arguments for initialization.
        """
