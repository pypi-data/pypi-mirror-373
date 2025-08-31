"""
The main application.
"""

import argparse
import logging
import sys

from . import __version__, commands
from .core.cli import Cli, load_commands
from .logger import logger


def on_cli_init(_: Cli, args: argparse.Namespace) -> None:
    """
    Performs custom initialisation for the command line init.
    """
    if args.verbose:
        logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.ERROR)


def on_cli_no_command(cli: Cli, args: argparse.Namespace) -> None:
    """
    Default action if no command is selected by the user.
    """
    if args.version:
        print(__version__)
        sys.exit(0)
    else:
        cli.print_help()


def app() -> None:
    """
    Main application logic.
    """
    try:
        logger.setLevel(logging.WARNING)
        cli = Cli(
            name="mnimi",
            description="ELF parser and memory live inspector",
            on_init=on_cli_init,
            on_no_command=on_cli_no_command,
        )

        load_commands(cli, commands)
        cli.exec()

    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
        sys.exit(1)


if __name__ == "__main__":
    app()
