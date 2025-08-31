"""
Logging functionality
"""

import logging
import os
import time

from mnimi.config import get_cache_dirpath, get_config_name

_t0 = time.monotonic()  # reference start time


class ColoredFormatter(logging.Formatter):
    """
    A custom formatter for adding colors to log messages.
    """

    COLORS: dict[str, str] = {
        "RESET": "\033[0m",
        "DEBUG": "\033[0;36m",  # Cyan
        "INFO": "\033[0;32m",  # Green
        "WARNING": "\033[0;33m",  # Yellow
        "ERROR": "\033[0;31m",  # Red
        "CRITICAL": "\033[1;31m",  # Bold Red
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Overrides the format method to add color codes to the log messages.
        """
        log_level: str = record.levelname
        relative_time_sec = time.monotonic() - _t0
        # Total width 10 including 's', left-aligned
        record.rel_secs = f"{relative_time_sec:.4f}s".rjust(10)
        record.color = self.COLORS.get(log_level, "")
        record.reset = self.COLORS["RESET"]
        return super().format(record)


class Logger(logging.Logger):
    """
    Custom logger class.
    """

    def __init__(
        self, name: str = "default", level: int = logging.NOTSET
    ) -> None:
        """
        Initializes the Logger class with console and file handlers.
        """
        super().__init__(name, level)

        log_filepath = os.path.join(
            get_cache_dirpath(), f"{get_config_name()}.log"
        )

        # Ensure the directory exists
        os.makedirs(os.path.dirname(log_filepath), exist_ok=True)

        if not self.handlers:
            # Create handlers
            self.c_handler = logging.StreamHandler()
            self.f_handler = logging.FileHandler(log_filepath)

            self.c_handler.setLevel(level)
            self.f_handler.setLevel(logging.WARNING)

            # Create formatters and add them to handlers
            c_format = ColoredFormatter(
                "[%(color)s%(levelname)-8s%(reset)s]: %(rel_secs)s "
                "%(filename)20s:%(lineno)d - "
                "%(message)s"
            )
            f_format = logging.Formatter(
                "[%(levelname)-8s]: %(asctime)s "
                "%(filename)20s:%(lineno)d"
                "%(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            self.c_handler.setFormatter(c_format)
            self.f_handler.setFormatter(f_format)

            # Add handlers to the logger
            self.addHandler(self.c_handler)
            self.addHandler(self.f_handler)

    def setLevel(self, level: int | str) -> None:
        """
        Override setLevel to also update the console handler level.
        """
        super().setLevel(level)
        if hasattr(self, "c_handler"):
            self.c_handler.setLevel(level)


logger = Logger(__name__)
