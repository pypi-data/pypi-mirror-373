"""
Development command
"""

import argparse
from dataclasses import dataclass
from typing import ClassVar

from mnimi.core.cli import Command
from mnimi.logger import logger


@dataclass
class Development(Command):
    """
    Development testing
    """

    name: ClassVar[str] = "dev"

    def exec(self, _: argparse.Namespace) -> None:
        """
        Executes the command.
        """
        logger.debug("This is a debug log")
        logger.info("This is an info log")
        logger.warning("This is a warning log")
        logger.error("This is an error log")
        logger.critical("This is a critial log")
