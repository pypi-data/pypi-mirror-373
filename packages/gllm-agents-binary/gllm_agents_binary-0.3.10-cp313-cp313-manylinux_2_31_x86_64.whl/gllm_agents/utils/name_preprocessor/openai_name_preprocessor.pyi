from _typeshed import Incomplete
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from gllm_agents.utils.name_preprocessor import BaseNamePreprocessor as BaseNamePreprocessor

logger: Incomplete

class OpenAINamePreprocessor(BaseNamePreprocessor):
    """Concrete implementation of NamePreprocessor according to OpenAI's name requirements."""
    CUT_OFF_INDEX: int
    def sanitize_agent_name(self, name: str) -> str:
        """Preprocess an input name according to OpenAI's name requirements for agents.

        As of now, OpenAI only has rule for tool name, and it is the same as Google's tool name rule,
        so just return the name as is.

        Args:
            name: The input name to preprocess.

        Returns:
            A name that is valid for OpenAI.
        """
    def sanitize_tool_name(self, name: str) -> str:
        """Preprocess an input name according to OpenAI's name requirements for tools.

        Args:
            name: The input name to preprocess.

        Returns:
            A name that is valid for OpenAI.

        Notes:
            Only contain letters (a-z, A-Z), digits (0-9), underscores (_), and dashes (-).
            It has a length limit of 64 characters.
        """
