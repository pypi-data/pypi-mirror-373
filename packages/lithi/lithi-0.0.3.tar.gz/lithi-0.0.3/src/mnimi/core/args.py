"""
Module for providing types for command line arguments.
"""

import argparse
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Argument(ABC):
    """
    A base class for a cli command argument.
    """

    name: str
    flag: str | None = None
    description: str | None = None

    @abstractmethod
    def register(self, parser: argparse.ArgumentParser) -> None:
        """
        Registers the argument.
        """
        raise NotImplementedError


@dataclass(frozen=True)
class ArgumentBoolean(Argument):
    """
    A boolean cli command argument.
    """

    default: bool = True

    def register(self, parser: argparse.ArgumentParser) -> None:
        """
        Registers the argument.
        """
        name = self.name.replace("-", "_")
        action = "store_true" if not self.default else "store_false"
        description = f"{self.description} (default={self.default})"
        if self.flag:
            parser.add_argument(
                f"-{self.flag}",
                f"--{self.name}",
                dest=name,
                action=action,
                default=self.default,
                help=description,
            )
        else:
            parser.add_argument(
                f"--{self.name}",
                dest=name,
                action=action,
                default=self.default,
                help=description,
            )


@dataclass(frozen=True)
class ArgumentInt(Argument):
    """
    An integer command argument.
    """

    default: int | None = None

    def register(self, parser: argparse.ArgumentParser) -> None:
        """
        Registers the argument.
        """
        name = self.name.replace("-", "_")
        description = f"{self.description} (default={self.default})"
        if self.flag:
            parser.add_argument(
                f"-{self.flag}",
                f"--{self.name}",
                dest=name,
                type=int,
                default=self.default,
                help=description,
            )
        else:
            parser.add_argument(
                f"--{self.name}",
                dest=name,
                type=int,
                default=self.default,
                help=description,
            )


@dataclass(frozen=True)
class ArgumentString(Argument):
    """
    A string cli command argument.
    """

    default: str | None = None

    def register(self, parser: argparse.ArgumentParser) -> None:
        """
        Registers the argument.
        """
        name = self.name.replace("-", "_")
        description = f"{self.description} (default={self.default})"
        if self.flag:
            parser.add_argument(
                f"-{self.flag}",
                f"--{self.name}",
                dest=name,
                type=str,
                default=self.default,
                help=description,
            )
        else:
            parser.add_argument(
                f"--{self.name}",
                dest=name,
                type=str,
                default=self.default,
                help=description,
            )
