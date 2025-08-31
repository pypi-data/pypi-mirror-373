"""
Module for command line argument operations.
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import pkgutil
import types
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, ClassVar, get_type_hints

from lithi.logger import logger

from .args import Argument


@dataclass
class Command(ABC):
    """
    A base class for a cli command.
    """

    # Subclasses must override this
    name: ClassVar[str]

    args: list[Argument] | None = field(default=None)

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        if not cls.__doc__:
            raise TypeError(f"{cls.__name__} must define a docstring")

        # Collect all ClassVars defined in this base class
        base_hints = get_type_hints(Command, include_extras=True)
        classvars = [
            var
            for var, typ in base_hints.items()
            if getattr(typ, "__origin__", None) is ClassVar
        ]

        # Check that subclass actually overrides them
        missing = [var for var in classvars if var not in cls.__dict__]
        if missing:
            raise TypeError(
                f"{cls.__name__} "
                "must override class-level attribute(s): "
                "{', '.join(missing)}"
            )

    @abstractmethod
    def exec(self, args: argparse.Namespace) -> None:
        """
        Executes the command.
        """
        raise NotImplementedError


class Cli:
    """
    The command line argument manager.
    """

    def __init__(
        self,
        name: str = "app",
        description: str | None = None,
        on_init: Callable[[Cli, argparse.Namespace], None] | None = None,
        on_no_command: Callable[[Cli, argparse.Namespace], None] | None = None,
    ) -> None:
        self.on_init = on_init
        self.on_no_command = on_no_command
        self.commands: dict[str, Command] = {}

        self.parser = argparse.ArgumentParser(
            prog=name, description=description
        )

    def register_cmd(self, command: Command) -> None:
        """
        Registers a command.
        """
        logger.info("Registered %s", command.name)
        self.commands[command.name] = command

    def register_arg(
        self, parser: argparse.ArgumentParser, argument: Argument
    ) -> None:
        """
        Registers an argument.
        """
        logger.info("Registered %s", argument.name)
        argument.register(parser)

    def exec(self) -> None:
        """
        Executes the command line.
        """

        # Define optional arguments
        self.parser.add_argument(
            "--version", action="store_true", help="Get version."
        )
        self.parser.add_argument(
            "-v", "--verbose", action="store_true", help="Enable verbose mode."
        )

        if self.commands:
            subparsers = self.parser.add_subparsers(
                dest="command", required=False
            )

            for cmd in self.commands.values():
                doc_string = (cmd.__doc__ or "").strip()
                cmd_parser = subparsers.add_parser(cmd.name, help=doc_string)
                if cmd.args:
                    for arg in cmd.args:
                        self.register_arg(cmd_parser, arg)

        # Parse the command-line arguments
        args: argparse.Namespace = self.parser.parse_args()

        # Configure logger
        if self.on_init:
            self.on_init(self, args)

        # Execute subcommand
        if args.command is not None:
            cmd = self.commands[args.command]
            cmd.exec(args)
        else:
            if self.on_no_command:
                self.on_no_command(self, args)
            else:
                self.print_help()

    def print_help(self) -> None:
        """
        Prints the help message.
        """
        self.parser.print_help()


def load_commands(cli: Cli, package: types.ModuleType) -> None:
    """
    Load all Command subclasses from a package (folder) and register them.
    :param parser: Argparser instance
    :param package: Python package (module) to scan, e.g., commands
    """
    # Iterate all modules in the package
    for _, module_name, ispkg in pkgutil.iter_modules(package.__path__):
        if ispkg:
            continue
        full_module_name = f"{package.__name__}.{module_name}"
        module = importlib.import_module(full_module_name)

        # Scan for all subclasses of Command
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, Command) and cls is not Command:
                # Instantiate and register
                obj = cls()
                cli.register_cmd(obj)
