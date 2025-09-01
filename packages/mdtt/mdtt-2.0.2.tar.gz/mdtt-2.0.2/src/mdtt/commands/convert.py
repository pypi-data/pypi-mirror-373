"""Convert command implementation."""

from argparse import ArgumentParser, Namespace
from pathlib import Path

from .. import writer
from .base import BaseCommand, CommandError


class ConvertCommand(BaseCommand):
    """Command to convert between different formats."""

    @property
    def help_text(self) -> str:
        return "Convert between different formats"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add convert command arguments."""
        subparsers = parser.add_subparsers(dest="convert_type", help="Conversion type")

        # txt-to-db subcommand
        txt_to_db = subparsers.add_parser("txt-to-db", help="Convert text format to SQLite database")
        txt_to_db.add_argument("input", help="Input TXT file")
        txt_to_db.add_argument("output", help="Output DB file")
        txt_to_db.add_argument("--encoding", default="UTF-8", help="Text encoding (default: UTF-8)")

        # db-to-txt subcommand
        db_to_txt = subparsers.add_parser("db-to-txt", help="Convert SQLite database to text format")
        db_to_txt.add_argument("input", help="Input DB file")
        db_to_txt.add_argument("output", help="Output TXT file")
        db_to_txt.add_argument("--encoding", default="UTF-8", help="Text encoding (default: UTF-8)")

    def execute(self, args: Namespace) -> None:
        """Execute the convert command."""
        if not hasattr(args, "convert_type") or not args.convert_type:
            raise CommandError("No conversion type specified. Use 'txt-to-db' or 'db-to-txt'")

        input_file = Path(args.input)
        output_file = Path(args.output)

        # Validate input file
        if not input_file.exists():
            raise CommandError(f"Input file not found: {input_file}")

        # Check if output file exists
        if output_file.exists():
            response = input(f"Output file {output_file} already exists. Overwrite? [y/N]: ")
            if response.lower() != "y":
                raise CommandError("Operation cancelled")

        try:
            if args.convert_type == "txt-to-db":
                self._convert_txt_to_db(input_file, output_file, args.encoding)
            elif args.convert_type == "db-to-txt":
                self._convert_db_to_txt(input_file, output_file, args.encoding)
            else:
                raise CommandError(f"Unknown conversion type: {args.convert_type}")

        except Exception as e:
            raise CommandError(f"Conversion failed: {e}") from e

    def _convert_txt_to_db(self, input_file: Path, output_file: Path, encoding: str) -> None:
        """Convert TXT file to database."""
        print(f'Converting "{input_file}" to database "{output_file}"...')

        # Create progress callback
        def progress_callback(count):
            if count % 1000 == 0:
                print(f"Processed {count:,} entries...", end="\r")

        try:
            writer.txt2db(str(input_file), callback=progress_callback)

            # txt2db creates file as source + ".db"
            expected_output = Path(str(input_file) + ".db")
            if expected_output.exists():
                if expected_output != output_file:
                    # Move to desired output location
                    expected_output.rename(output_file)
                
                file_size = output_file.stat().st_size
                print(f"\n✅ Successfully converted to {output_file} ({file_size:,} bytes)")
            else:
                raise CommandError(f"Conversion failed: Expected output file {expected_output} was not created")

        except Exception as e:
            raise CommandError(f"TXT to DB conversion failed: {e}") from e

    def _convert_db_to_txt(self, input_file: Path, output_file: Path, encoding: str) -> None:
        """Convert database to TXT file."""
        print(f'Converting "{input_file}" to text "{output_file}"...')

        # Create progress callback
        def progress_callback(count):
            if count % 1000 == 0:
                print(f"Processed {count:,} entries...", end="\r")

        try:
            writer.db2txt(str(input_file), encoding=encoding, callback=progress_callback)

            # db2txt creates file as source + ".txt"
            expected_output = Path(str(input_file) + ".txt")
            if expected_output.exists():
                if expected_output != output_file:
                    # Move to desired output location
                    expected_output.rename(output_file)
                
                file_size = output_file.stat().st_size
                print(f"\n✅ Successfully converted to {output_file} ({file_size:,} bytes)")
            else:
                raise CommandError(f"Conversion failed: Expected output file {expected_output} was not created")

        except Exception as e:
            raise CommandError(f"DB to TXT conversion failed: {e}") from e
