"""Base command class for all subcommands."""

from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace


class BaseCommand(ABC):
    """Base class for all subcommands."""

    @abstractmethod
    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments to the parser."""
        pass

    @abstractmethod
    def execute(self, args: Namespace) -> None:
        """Execute the command with parsed arguments."""
        pass

    @property
    @abstractmethod
    def help_text(self) -> str:
        """Return help text for this command."""
        pass


class CommandError(Exception):
    """Exception raised by commands when they encounter an error."""

    pass
