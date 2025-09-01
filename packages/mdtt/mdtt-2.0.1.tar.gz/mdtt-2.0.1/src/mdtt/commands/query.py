"""Query command implementation."""

from argparse import ArgumentParser, Namespace

from .. import reader
from .base import BaseCommand, CommandError


class QueryCommand(BaseCommand):
    """Command to query words from dictionary."""

    @property
    def help_text(self) -> str:
        return "Query word from dictionary"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add query command arguments."""
        parser.add_argument("word", help="Word or phrase to query")
        parser.add_argument("file", help="Dictionary file (MDX/DB)")
        parser.add_argument("-o", "--output", dest="output_file", help="Output file for query result (default: <word>.html)")
        parser.add_argument("--substyle", action="store_true", help="Use substyle when reading")
        parser.add_argument("--passcode", metavar="CODE", help="Passcode for encrypted dictionaries")

    def execute(self, args: Namespace) -> None:
        """Execute the query command."""
        import re
        from pathlib import Path

        dict_file = Path(args.file)
        if not dict_file.exists():
            raise CommandError(f"Dictionary file not found: {dict_file}")

        # Validate file type
        valid_extensions = [".mdx", ".db"]
        if dict_file.suffix.lower() not in valid_extensions:
            raise CommandError(f"Invalid file type: {dict_file.suffix}. Expected {', '.join(valid_extensions)}")

        try:
            # Query the word
            result = reader.query(str(dict_file), args.word, substyle=args.substyle, passcode=args.passcode)

            if result:
                # Determine output file
                if args.output_file:
                    output_file = Path(args.output_file)
                else:
                    # Generate safe filename from the word
                    safe_word = re.sub(r'[<>:"/\\|?*]', '_', args.word)
                    safe_word = safe_word.strip()[:50]  # Limit length to avoid filesystem issues
                    output_file = Path(f"{safe_word}.html")

                # Write result to file
                output_file.write_text(result, encoding='utf-8')
                print(f'✅ Query result for "{args.word}" saved to {output_file}')
                
                # Also display result to console
                print(result)
            else:
                print(f'No result found for "{args.word}"')
                return

        except Exception as e:
            raise CommandError(f"Query failed: {e}") from e
