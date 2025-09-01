"""Extract command implementation."""

from argparse import ArgumentParser, Namespace
from pathlib import Path

from .. import reader
from ..metadata import MetadataManager
from .base import BaseCommand, CommandError


class ExtractCommand(BaseCommand):
    """Command to extract MDX/MDD files."""

    @property
    def help_text(self) -> str:
        return "Extract mdx/mdd dictionary files"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add extract command arguments."""
        parser.add_argument("file", help="MDX/MDD file to extract")
        parser.add_argument(
            "-o", "--output", dest="output_dir", help="Output directory (default: current working directory)"
        )
        parser.add_argument(
            "--no-meta", action="store_true", help="Skip metadata export (default: export simplified .meta.toml)"
        )
        parser.add_argument(
            "--full-meta", action="store_true", help="Export all metadata fields (including technical details)"
        )
        parser.add_argument("--split-az", action="store_true", help="Split output by alphabet (a-z)")
        parser.add_argument("--split-n", type=int, metavar="N", help="Split output into N files")
        parser.add_argument("--db", action="store_true", help="Extract to SQLite database format")
        parser.add_argument("--db-zip", action="store_true", help="Extract to compressed SQLite database")
        parser.add_argument("--convert-chtml", action="store_true", help="Convert compact HTML format")
        parser.add_argument("--substyle", action="store_true", help="Use substyle when reading (advanced)")
        parser.add_argument("--passcode", metavar="CODE", help="Passcode for encrypted dictionaries")

    def execute(self, args: Namespace) -> None:
        """Execute the extract command."""
        input_file = Path(args.file)

        # Validate input file
        if not input_file.exists():
            raise CommandError(f"Input file not found: {input_file}")

        if input_file.suffix.lower() not in [".mdx", ".mdd"]:
            raise CommandError(f"Invalid file type: {input_file.suffix}. Expected .mdx or .mdd")

        # Determine output directory
        if args.output_dir:
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = Path.cwd()  # 默认使用当前工作目录

        print(f'Extracting "{input_file}" to "{output_dir}"...')

        try:
            # Extract based on format choice
            if args.db or args.db_zip:
                # Extract to database
                reader.unpack_to_db(str(output_dir), str(input_file), zip=args.db_zip)
                print(f"✅ Extracted to database in {output_dir}")
            else:
                # Extract to text files
                split = None
                if args.split_az:
                    split = "az"
                elif args.split_n:
                    split = str(args.split_n)

                reader.unpack(
                    str(output_dir),
                    str(input_file),
                    split=split,
                    convert_chtml=args.convert_chtml,
                    export_legacy_meta=False,  # 不自动输出HTML元数据文件
                )
                print(f"✅ Extracted to text files in {output_dir}")

            # Export metadata by default (unless --no-meta is specified)
            if not args.no_meta:
                self._export_metadata(input_file, output_dir, args.full_meta)

        except Exception as e:
            raise CommandError(f"Extraction failed: {e}") from e

    def _export_metadata(self, input_file: Path, output_dir: Path, full_meta: bool = False) -> None:
        """Export metadata to TOML file."""
        try:
            # Read metadata from MDX file
            meta_dict = reader.meta(str(input_file))

            # Determine what metadata to export
            # Extract title and description with fallback defaults
            title = meta_dict.get("title", "").strip()
            if not title:
                title = f"Dictionary from {input_file.stem}"
            
            description = meta_dict.get("description", "").strip()
            if not description:
                description = f"Extracted from {input_file.name}"
            
            if full_meta:
                # Export all metadata fields for advanced users
                toml_data = {
                    "dictionary": {
                        "title": title,
                        "description": description,
                        "version": str(meta_dict.get("version", "2.0")),
                    },
                    "advanced": {
                        "encoding": meta_dict.get("encoding", "UTF-8"),
                        "engine_version": meta_dict.get("generatedbyengineversion", ""),
                        "required_version": meta_dict.get("requiredengineversion", ""),
                        "creation_date": meta_dict.get("creationdate", ""),
                        "format": meta_dict.get("format", "Html"),
                        "keycasesensitive": meta_dict.get("keycasesensitive", "No"),
                        "stripkey": meta_dict.get("stripkey", "Yes"),
                        "encrypted": meta_dict.get("encrypted", "0"),
                    },
                }
            else:
                # Export only essential fields for normal users
                toml_data = {
                    "dictionary": {
                        "title": title,
                        "description": description,
                        # version 等技术属性省略，使用默认值
                    }
                }

            # Clean up description formatting
            if toml_data["dictionary"]["description"]:
                toml_data["dictionary"]["description"] = (
                    toml_data["dictionary"]["description"].replace("\r\n", "\n").strip()
                )

            # Add extraction info (create advanced section if it doesn't exist)
            from datetime import datetime

            if "advanced" not in toml_data:
                toml_data["advanced"] = {}
            toml_data["advanced"]["extracted_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            toml_data["advanced"]["extracted_from"] = str(input_file)

            # Save TOML file
            meta_file = output_dir / f"{input_file.name}.meta.toml"
            manager = MetadataManager()
            manager.save(toml_data, meta_file)

            print(f"✅ Metadata exported to {meta_file}")

        except Exception as e:
            print(f"⚠️  Failed to export metadata: {e}")
            # Don't fail the entire extraction for metadata export issues
