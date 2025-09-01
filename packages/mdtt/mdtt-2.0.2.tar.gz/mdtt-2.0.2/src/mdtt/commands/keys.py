"""Keys command implementation."""

from argparse import ArgumentParser, Namespace
from pathlib import Path

from .. import reader
from .base import BaseCommand, CommandError


class KeysCommand(BaseCommand):
    """Command to list dictionary keys."""

    @property
    def help_text(self) -> str:
        return "List all dictionary keys"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add keys command arguments."""
        parser.add_argument("file", help="Dictionary file (MDX/MDD/DB)")
        parser.add_argument(
            "-o", "--output", dest="output_file", metavar="FILE", help="Output to file instead of stdout"
        )
        parser.add_argument("--limit", type=int, metavar="N", help="Limit output to first N keys")
        parser.add_argument("--pattern", metavar="PATTERN", help="Filter keys by pattern (supports wildcards)")
        parser.add_argument("--substyle", action="store_true", help="Use substyle when reading")
        parser.add_argument("--passcode", metavar="CODE", help="Passcode for encrypted dictionaries")

    def execute(self, args: Namespace) -> None:
        """Execute the keys command."""
        dict_file = Path(args.file)
        if not dict_file.exists():
            raise CommandError(f"Dictionary file not found: {dict_file}")

        # Validate file type
        valid_extensions = [".mdx", ".mdd", ".db"]
        if dict_file.suffix.lower() not in valid_extensions:
            raise CommandError(f"Invalid file type: {dict_file.suffix}. Expected {', '.join(valid_extensions)}")

        try:
            # Get keys iterator
            keys_iter = reader.get_keys(str(dict_file), substyle=args.substyle, passcode=args.passcode)

            # Set up output
            output_file = None
            if args.output_file:
                output_file = open(args.output_file, "w", encoding="utf-8")
                print(f"Writing keys to {args.output_file}...")

            # Process keys
            try:
                count = 0
                pattern_matcher = None

                # Set up pattern matching if specified
                if args.pattern:
                    import fnmatch

                    pattern_matcher = lambda key: fnmatch.fnmatch(key, args.pattern)

                for key in keys_iter:
                    # Apply pattern filter
                    if pattern_matcher and not pattern_matcher(key):
                        continue

                    # Apply limit
                    if args.limit and count >= args.limit:
                        break

                    # Output key
                    if output_file:
                        output_file.write(key + "\n")
                    else:
                        print(key)

                    count += 1

                # Print summary
                if output_file:
                    print(f"✅ Wrote {count:,} keys to {args.output_file}")
                elif args.limit:
                    print(f"(Showing first {count:,} keys)")

            finally:
                if output_file:
                    output_file.close()

        except Exception as e:
            raise CommandError(f"Failed to list keys: {e}") from e
