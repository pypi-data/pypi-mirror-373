from _typeshed import Incomplete
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from gllm_agents.utils.name_preprocessor import BaseNamePreprocessor as BaseNamePreprocessor

logger: Incomplete

class GoogleNamePreprocessor(BaseNamePreprocessor):
    """Concrete implementation of NamePreprocessor according to Google's name requirements."""
    NAME_SETTINGS: Incomplete
    CUT_OFF_INDEX: int
    def sanitize_agent_name(self, name: str) -> str:
        """Preprocess an input name according to Google's name requirements for agents.

        Args:
            name: The input name to preprocess.

        Returns:
            A name that is valid for Google.

        Notes:
            Name should start with a letter (a-z, A-Z) or an underscore (_),
            and can only contain letters, digits (0-9), and underscores.
            It has no length limit. ( based on experiment )
        """
    def sanitize_tool_name(self, name: str) -> str:
        """Preprocess an input name according to Google's name requirements for tools.

        Args:
            name: The input name to preprocess.

        Returns:
            A name that is valid for Google.

        Notes:
            Name should start with a letter (a-z, A-Z) or an underscore (_),
            and can only contain letters, digits (0-9), underscores, and dashes.
            It has a length limit of 64 characters, but google throws error if the length is exactly 64, so cut to 63.
        """
