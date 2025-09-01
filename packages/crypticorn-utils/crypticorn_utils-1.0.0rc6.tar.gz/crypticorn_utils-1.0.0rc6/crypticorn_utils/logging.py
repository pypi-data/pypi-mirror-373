from __future__ import annotations

import logging
import os
import sys
from datetime import datetime
from enum import StrEnum
from logging.handlers import RotatingFileHandler
from typing import Optional

from crypticorn_utils.ansi_colors import AnsiColors as C


class _LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    @classmethod
    def get_color(cls, level: str) -> str:
        """Get the ansi color based on the log level."""
        if level == cls.DEBUG:
            return C.GREEN_BRIGHT
        elif level == cls.INFO:
            return C.BLUE_BRIGHT
        elif level == cls.WARNING:
            return C.YELLOW_BRIGHT
        elif level == cls.ERROR:
            return C.RED_BRIGHT
        elif level == cls.CRITICAL:
            return C.RED_BOLD
        else:
            return C.RESET


_LOGFORMAT = (
    f"{C.CYAN_BOLD}%(asctime)s{C.RESET} - "
    f"{C.GREEN_BOLD}%(name)s{C.RESET} - "
    f"%(levelcolor)s%(levelname)s{C.RESET} - "
    f"%(message)s"
)
_DATEFMT = "%Y-%m-%d %H:%M:%S.%f:"


class _CustomFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record):
        color = _LogLevel.get_color(record.levelname)
        record.levelcolor = color
        return super().format(record)

    def formatTime(self, record, datefmt=_DATEFMT):
        dt = datetime.fromtimestamp(record.created)
        s = dt.strftime(datefmt)
        return s[:-3]  # Trim last 3 digits to get milliseconds


def configure_logging(
    name: Optional[str] = None,
    fmt: str = _LOGFORMAT,
    datefmt: str = _DATEFMT,
    stdout_level: int = logging.INFO,
    file_level: int = logging.INFO,
    log_file: Optional[str] = None,
    filters: list[logging.Filter] = [],
) -> None:
    """Configures the logging for the application.
    Run this function as early as possible in the application (for example using the `lifespan` parameter in FastAPI).
    Then use can use the default `logging.getLogger(__name__)` method to get the logger (or <name> if you set the name parameter).
    :param name: The name of the logger. If not provided, the root logger will be used. Use a name if you use multiple loggers in the same application.
    :param fmt: The format of the log message.
    :param datefmt: The date format of the log message.
    :param stdout_level: The level of the log message to be printed to the console.
    :param file_level: The level of the log message to be written to the file. Only used if `log_file` is provided.
    :param log_file: The file to write the log messages to.
    :param filters: A list of filters to apply to the log handlers.
    """
    logger = logging.getLogger(name) if name else logging.getLogger()

    if logger.hasHandlers():  # clear existing handlers to avoid duplicates
        logger.handlers.clear()

    logger.setLevel(min(stdout_level, file_level))  # set to most verbose level

    # Configure stdout handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(stdout_level)
    stdout_handler.setFormatter(_CustomFormatter(fmt=fmt, datefmt=datefmt))
    for filter in filters:
        stdout_handler.addFilter(filter)
    logger.addHandler(stdout_handler)

    # Configure file handler
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        file_handler.setLevel(file_level)
        file_handler.setFormatter(_CustomFormatter(fmt=fmt, datefmt=datefmt))
        for filter in filters:
            file_handler.addFilter(filter)
        logger.addHandler(file_handler)

    if name:
        logger.propagate = False


def disable_logging():
    """Disable logging for the crypticorn logger."""
    logger = logging.getLogger("crypticorn")
    logger.disabled = True
