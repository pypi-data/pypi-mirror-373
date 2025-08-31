import logging
from typing import Callable, Dict, List, Self, TypedDict

class ColorCodes(TypedDict):
    time: str
    name: str
    level: Dict[int, str]
    message: str
    reset: str

class LanoFormatter(logging.Formatter):
    """
    Custom logging formatter with colors for different log levels,
    a specific date format, and customized spacing.
    """

    COLOR_CODES: ColorCodes = {
        "time": "\033[37m",  # White for timestamp
        "name": "\033[94m",  # Blue for logger name
        "level": {
            logging.DEBUG: "\033[92m",  # Green for DEBUG level
            logging.INFO: "\033[96m",  # Cyan for INFO level
            logging.WARNING: "\033[93m",  # Yellow for WARNING level
            logging.ERROR: "\033[91m",  # Red for ERROR level
            logging.CRITICAL: "\033[95m",  # Magenta for CRITICAL level
        },
        "message": "\033[33m",  # Yellow for the message
        "reset": "\033[0m",  # Reset color
    }

    def __init__(self, log_format: str = "", date_format: str = ""):
        if not log_format:
            log_format = "[%(asctime)s]  - (%(name)-s) - [%(levelname)-s] - %(message)s"

        if not date_format:
            date_format = "%d/%m/%Y %H:%M:%S"

        super().__init__(fmt=log_format, datefmt=date_format)

    def format(self, record: logging.LogRecord) -> str:
        time_color = self.COLOR_CODES["name"]
        name_color = self.COLOR_CODES["name"]
        level_color = self.COLOR_CODES["level"].get(record.levelno, "")
        message_color = self.COLOR_CODES["message"]
        reset_color = self.COLOR_CODES["reset"]

        record.asctime = (
            f"{time_color}{self.formatTime(record, self.datefmt)}{reset_color}"
        )
        record.name = f"{name_color}{record.name}{reset_color}"
        record.levelname = f"{level_color}{record.levelname}{reset_color}"
        record.msg = f"{message_color}{record.msg}{reset_color}"
        return super().format(record)


class LoggerBuilder:
    """
    Builder class for constructing a custom logger with flexible configurations.
    """

    def __init__(self, name: str = "CustomLogger"):
        self._name = name
        self._level = logging.INFO
        self._formatter = LanoFormatter()
        self._handlers: List[logging.Handler] = []

    def set_level(self, level: int) -> Self:
        """
        Sets the logging level of the logger.

        Args:
            level (int): Logging level (e.g., logging.DEBUG, logging.INFO).

        Returns:
            LoggerBuilder: The builder instance for method chaining.
        """
        self._level = level
        return self

    def set_formatter(self, format_str: str) -> Self:
        """
        Sets a custom format for the log messages.

        Args:
            format_str (str): Format string for the logger.

        Returns:
            LoggerBuilder: The builder instance for method chaining.
        """
        self._formatter = LanoFormatter(format_str)
        return self

    def add_stream_handler(self) -> Self:
        """
        Adds a stream handler to output logs to the console.

        Returns:
            LoggerBuilder: The builder instance for method chaining.
        """
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(self._formatter)
        self._handlers.append(stream_handler)
        return self

    def add_file_handler(self, file_path: str, mode: str = "a") -> Self:
        """
        Adds a file handler to output logs to a specified file.

        Args:
            file_path (str): Path to the log file.
            mode (str): File mode (default is append mode 'a').

        Returns:
            LoggerBuilder: The builder instance for method chaining.
        """
        file_handler = logging.FileHandler(file_path, mode=mode)
        file_handler.setFormatter(self._formatter)
        self._handlers.append(file_handler)
        return self

    def build(self) -> logging.Logger:
        """
        Builds and returns the configured logger.

        Returns:
            logging.Logger: Configured logger instance.
        """
        logger = logging.getLogger(self._name)
        logger.setLevel(self._level)

        if not logger.handlers:
            for handler in self._handlers:
                logger.addHandler(handler)

        return logger

    def set_debug_mode(self, func: Callable):
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(self._name)

            if self._level == logging.DEBUG:
                logger.debug(
                    f"Function {func.__name__} called with args: {args}, kwargs: {kwargs}"
                )

            result = func(*args, **kwargs)

            if self._level == logging.DEBUG:
                logger.debug(f"Function {func.__name__} returned: {result}")

            return result

        return wrapper
