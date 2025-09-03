import logging
from _typeshed import Incomplete

BOSA_CORE_AVAILABLE: bool
DEFAULT_LOG_FORMAT: Incomplete
DEFAULT_DATE_FORMAT: str
LOG_COLORS: Incomplete
MAX_LOG_COLORS_LENGTH: Incomplete
TRUNCATED_MESSAGE: str
MAX_MESSAGE_LENGTH: Incomplete

class StandardizedFormatter(logging.Formatter):
    """Custom formatter that outputs logs in standardized JSON format with colors.

    Follows the standardized log format:
    - level: string (e.g., INFO, ERROR)
    - timestamp: ISO 8601 with timezone (e.g., 2025-07-23T00:29:05.091Z)
    - message: string (the content of the log) (max 500000 context length)
    - error: object (for error logs only)
        - message: string (the error message)
        - code: string (specific error code)
        - stacktrace: string (the stack trace for debugging)
    """
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record in standardized JSON format with colors.

        Args:
            record (logging.LogRecord): The log record to be formatted.

        Returns:
            str: The formatted log message in JSON format.
        """

class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors based on log level."""
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors based on log level.

        Args:
            record (logging.LogRecord): The log record to be formatted.

        Returns:
            str: The formatted log message with color codes.
        """

class LoggerManager:
    '''A singleton class to manage logging configuration.

    This class ensures that the root logger is initialized only once and is used across the application.
    Supports both traditional colored output and standardized format with colors.

    Example to get and use the logger:
    ```python
    manager = LoggerManager()

    logger = manager.get_logger()

    logger.info("This is an info message")
    ```

    Example to set logging configuration:
    ```python
    manager = LoggerManager()

    manager.set_level(logging.DEBUG)
    manager.set_output_format("traditional")  # or "standardized"
    ```

    Example to add a custom handler:
    ```python
    manager = LoggerManager()

    handler = logging.FileHandler("app.log")
    manager.add_handler(handler)
    ```

    Output format examples:

    Traditional format:
    ```python
    [16/04/2025 15:08:18.323 GDPLabsGenAILogger INFO] Loading prompt_builder catalog for chatbot `general-purpose`
    ```

    Standardized format:
    ```json
    {
        "level": "INFO",
        "timestamp": "2025-07-23T00:29:05.091Z",
        "message": "Loading prompt_builder catalog for chatbot `general-purpose`"
    }
    ```

    Error standardized format:
    ```json
    {
        "level": "ERROR",
        "timestamp": "2025-07-23T00:29:05.091Z",
        "message": "Failed to load configuration",
        "error": {
            "message": "Configuration file not found",
            "code": "CONFIG_NOT_FOUND",
            "stacktrace": "Traceback (most recent call last):..."
        }
    }
    ```
    '''
    def __new__(cls):
        """Initialize the singleton instance."""
    def get_logger(self, name: str | None = None) -> logging.Logger:
        """Get a logger instance.

        This method returns a logger instance that is a child of the root logger. If name is not provided,
        the root logger will be returned instead.

        Args:
            name (str | None, optional): The name of the child logger.
                If None, the root logger will be returned. Defaults to None.

        Returns:
            logging.Logger: Configured logger instance.
        """
    def set_level(self, level: int) -> None:
        """Set logging level for all loggers in the hierarchy.

        Args:
            level (int): The logging level to set (e.g., logging.INFO, logging.DEBUG).
        """
    def set_output_format(self, output_format: str) -> None:
        '''Set the output format for all loggers in the hierarchy.

        Args:
            output_format (str): The output format to set. Must be either "standardized" or "traditional".
        '''
    def set_log_format(self, log_format: str) -> None:
        """Set logging format for all loggers in the hierarchy (traditional mode only).

        Args:
            log_format (str): The log format to set.
        """
    def set_date_format(self, date_format: str) -> None:
        """Set date format for all loggers in the hierarchy (traditional mode only).

        Args:
            date_format (str): The date format to set.
        """
    def add_handler(self, handler: logging.Handler) -> None:
        """Add a custom handler to the root logger.

        Args:
            handler (logging.Handler): The handler to add to the root logger.
        """
