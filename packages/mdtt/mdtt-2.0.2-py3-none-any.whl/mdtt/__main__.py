"""Main entry point for MDTT (MDx Dict Trans ToolKit) with subcommand architecture."""

import argparse
import sys
from typing import NoReturn

from . import about
from .commands import (
    ConvertCommand,
    ExtractCommand,
    InfoCommand,
    KeysCommand,
    PackCommand,
    QueryCommand,
)
from .commands.base import CommandError


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="mdtt",
        description="MDTT (MDx Dict Trans ToolKit) - A modern Python tool for packing and unpacking MDict dictionary files (.mdx/.mdd).",
        usage="mdtt [OPTIONS] <COMMAND>",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Use 'mdtt <command> --help' for more information on a specific command.",
        add_help=False,  # We'll add custom help
    )

    # Add custom help option
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    parser.add_argument(
        "-V", "--version", action="version", version=f"mdtt {about.version}", help="Display the mdtt version"
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Use quiet output")
    parser.add_argument("-v", "--verbose", action="store_true", help="Use verbose output")

    # Commands section
    subparsers = parser.add_subparsers(dest="command", title="Commands", metavar="<COMMAND>")

    # Register commands with clean descriptions like uv
    commands = {
        "extract": (ExtractCommand(), "Extract mdx/mdd dictionary files with metadata"),
        "pack": (PackCommand(), "Pack source files into mdx/mdd format (auto-detects output name)"),
        "query": (QueryCommand(), "Query word from dictionary"),
        "info": (InfoCommand(), "Display dictionary information and metadata"),
        "keys": (KeysCommand(), "List all dictionary keys"),
        "convert": (ConvertCommand(), "Convert between different formats"),
    }

    for name, (command, detailed_help) in commands.items():
        subparser = subparsers.add_parser(name, help=detailed_help, description=detailed_help)
        command.add_arguments(subparser)
        # Store command instance for later execution
        subparser.set_defaults(command_instance=command)

    return parser


def handle_error(error: Exception, verbose: bool = False) -> NoReturn:
    """Handle command execution errors."""
    if isinstance(error, CommandError):
        # User-facing error
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    elif verbose:
        # Developer error with traceback
        import traceback

        print(f"Internal error: {error}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(2)
    else:
        # Developer error without traceback
        print(f"Internal error: {error}", file=sys.stderr)
        print("Use --verbose for detailed error information", file=sys.stderr)
        sys.exit(2)


def run() -> None:
    """Main entry point for the application."""
    parser = create_parser()

    # Handle case with no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    # Parse arguments
    args = parser.parse_args()

    # Check if a command was specified
    if not hasattr(args, "command") or args.command is None:
        parser.print_help()
        sys.exit(1)

    # Set up global options (for future use)
    if args.quiet:
        # Could implement quiet logging here
        pass

    if args.verbose:
        # Could implement verbose logging here
        pass

    # Execute the command
    try:
        command_instance = args.command_instance
        command_instance.execute(args)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)  # Standard exit code for Ctrl+C

    except Exception as e:
        handle_error(e, verbose=args.verbose)


if __name__ == "__main__":
    run()
