from .base_name_preprocessor import BaseNamePreprocessor as BaseNamePreprocessor
from .google_name_preprocessor import GoogleNamePreprocessor as GoogleNamePreprocessor
from .openai_name_preprocessor import OpenAINamePreprocessor as OpenAINamePreprocessor
from _typeshed import Incomplete
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager

logger: Incomplete

class NamePreprocessor:
    """Name Preprocessor for Google ADK and OpenAI compatible models.

    Args:
        provider: The provider of the model.
    """
    PROVIDER_TO_NAME_PREPROCESSOR_MAP: Incomplete
    provider: Incomplete
    preprocessor: Incomplete
    def __init__(self, provider: str) -> None:
        """Initialize the name preprocessor.

        Args:
            provider: The provider of the model.
        """
    def sanitize_agent_name(self, name: str) -> str:
        """Preprocess an input name according to the rules of the name processor.

        Args:
            name: The input name to preprocess.

        Returns:
            A name that is valid for the name processor.
        """
    def sanitize_tool_name(self, name: str) -> str:
        """Preprocess an input name according to the rules of the name processor.

        Args:
            name: The input name to preprocess.

        Returns:
            A name that is valid for the name processor.
        """
