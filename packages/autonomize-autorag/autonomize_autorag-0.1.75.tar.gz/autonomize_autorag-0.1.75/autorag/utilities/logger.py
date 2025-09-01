"""Logging setup and configuration module"""

# pylint: disable=line-too-long

import logging
from typing import Optional

# To disable HTTP request logs.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("anthropic").setLevel(logging.WARNING)


def setup_logger(
    log_level: int = logging.DEBUG, log_format: Optional[str] = None
) -> None:
    """
    Set up the logger configuration. This function initializes the logging system
    with a default log level and format. By default, logs will be printed to the console.

    Args:
        log_level (int): The logging level (e.g., logging.DEBUG, logging.INFO). Default is logging.DEBUG.
        log_format (Optional[str]): The log format string. If not provided, a default format will be used.

    """

    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(level=log_level, format=log_format, datefmt="%Y-%m-%d %H:%M:%S")


# Call setup_logger when the logger module is imported
setup_logger()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Retrieve a logger for the specified module or component. The logger
    will inherit the base configuration.

    Args:
        name (Optional[str]): The name of the logger, typically `__name__` is used. If not provided, root is used.

    Returns:
        logging.Logger: A logger instance with the specified name.
    """

    return logging.getLogger(name)
