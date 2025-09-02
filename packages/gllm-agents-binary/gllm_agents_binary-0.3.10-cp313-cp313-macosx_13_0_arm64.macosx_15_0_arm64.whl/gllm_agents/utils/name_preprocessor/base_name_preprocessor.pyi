import abc
from abc import ABC, abstractmethod

class BaseNamePreprocessor(ABC, metaclass=abc.ABCMeta):
    """Base class for name preprocessing.

    It contains the common methods for name preprocessing.
    """
    def regex_substitute(self, name: str, regex: str, replacement: str) -> str:
        """Substitute a regex pattern in a name.

        Args:
            name: The input name to preprocess.
            regex: The regex pattern to substitute.
            replacement: The replacement string.

        Returns:
            A name that is valid for the name processor.
        """
    def clean_up_name(self, name: str) -> str:
        """Process a processed name.

        Step:
            1. collapse multiple underscores to single underscore
            2. remove trailing underscores
            3. if name is empty after clean up, add a single underscore

        Args:
            name: The input name to preprocess.

        Returns:
            A name that starts with a letter or an underscore.
        """
    @abstractmethod
    def sanitize_agent_name(self, name: str) -> str:
        """Process a name according to the rules of the name processor.

        Args:
            name: The input name to preprocess.

        Returns:
            A name that is valid for the name processor.
        """
    @abstractmethod
    def sanitize_tool_name(self, name: str) -> str:
        """Process a name according to the rules of the name processor.

        Args:
            name: The input name to preprocess.

        Returns:
            A name that is valid for the name processor.
        """
