import logging
from _typeshed import Incomplete
from gllm_core.constants import LogFormat as LogFormat
from pythonjsonlogger.core import LogRecord
from pythonjsonlogger.json import JsonFormatter

TEXT_LOG_FORMAT: Incomplete
JSON_LOG_FORMAT: str
DEFAULT_DATE_FORMAT: str
LOG_COLORS: Incomplete
DEPRECATION_MESSAGE: str

class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors based on log level."""
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors based on log level.

        Args:
            record (logging.LogRecord): The log record to be formatted.

        Returns:
            str: The formatted log message with color codes.
        """

class AppJsonFormatter(JsonFormatter):
    """Json formatter that groups error-related fields under an 'error' key.

    This formatter renames the following fields when present:
    1. exc_info -> error.message
    2. stack_info -> error.stacktrace
    3. error_code -> error.code
    """
    def process_log_record(self, log_record: LogRecord) -> LogRecord:
        """Process log record to group and rename error-related fields.

        Args:
            log_record (LogRecord): The original log record.

        Returns:
            LogRecord: The processed log record.
        """

class LoggerManager:
    '''A singleton class to manage logging configuration.

    This class ensures that the root logger is initialized only once and is used across the application.

    There are two logging modes:
    1. TEXT (Default): Uses the ColoredFormatter to add colors based on log level.
    2. JSON: Uses the JsonFormatter to format the log record as a JSON object.

    Switch between the two by setting the environment variable `LOG_FORMAT` to `json` or `text`.

    Get and use the logger:
    ```python
    manager = LoggerManager()

    logger = manager.get_logger()

    logger.info("This is an info message")
    ```

    Set logging configuration:
    ```python
    manager = LoggerManager()

    manager.set_level(logging.DEBUG)
    manager.set_log_format(custom_log_format)
    manager.set_date_format(custom_date_format)
    ```

    Add a custom handler:
    ```python
    manager = LoggerManager()

    handler = logging.FileHandler("app.log")
    manager.add_handler(handler)
    ```

    Log stack traces and exceptions:
    ```python
    try:
        1 / 0
    except Exception as e:
        logger.error("Exception occurred", exc_info=True)
    ```

    During errors, pass the error code using the `extra` parameter:
    ```python
    logger.error("I am dead!", extra={"error_code": "ERR_CONN_REFUSED"})
    ```

    Output format in text mode:
    ```
    [16/04/2025 15:08:18.323 Test INFO] Message
    ```

    Output format in JSON mode:
    ```json
    {"timestamp": "2025-08-11T19:40:30+07:00", "name": "Test", "level": "INFO", "message": "Message"}
    ```
    '''
    def __new__(cls) -> LoggerManager:
        """Initialize the singleton instance.

        Returns:
            LoggerManager: The singleton instance.
        """
    def get_logger(self, name: str | None = None) -> logging.Logger:
        """Get a logger instance.

        This method returns a logger instance that is a child of the root logger. If name is not provided,
        the root logger will be returned instead.

        Args:
            name (str | None, optional): The name of the child logger. If None, the root logger will be returned.
                Defaults to None.

        Returns:
            logging.Logger: Configured logger instance.
        """
    def set_level(self, level: int) -> None:
        """Set logging level for all loggers in the hierarchy.

        Args:
            level (int): The logging level to set (e.g., logging.INFO, logging.DEBUG).
        """
    def set_log_format(self, log_format: str) -> None:
        """Set logging format for all loggers in the hierarchy.

        Args:
            log_format (str): The log format to set.
        """
    def set_date_format(self, date_format: str) -> None:
        """Set date format for all loggers in the hierarchy.

        Args:
            date_format (str): The date format to set.
        """
    def add_handler(self, handler: logging.Handler) -> None:
        """Add a custom handler to the root logger.

        Args:
            handler (logging.Handler): The handler to add to the root logger.
        """
