"""Pack command implementation."""

from argparse import ArgumentParser, Namespace
from pathlib import Path

from .. import writer
from ..metadata import MetadataManager, find_meta_file
from .base import BaseCommand, CommandError


class PackCommand(BaseCommand):
    """Command to pack source files into MDX/MDD format."""

    @property
    def help_text(self) -> str:
        return "Pack source files into mdx/mdd format"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add pack command arguments."""
        parser.add_argument(
            "-a",
            "--add",
            dest="sources",
            metavar="RESOURCE",
            action="append",
            required=True,
            help="Add resource file (can be used multiple times)",
        )
        parser.add_argument(
            "output",
            nargs="?",  # 使参数变为可选
            help="Output MDX/MDD file (auto-generated from input name if not specified)",
        )
        parser.add_argument(
            "-m", "--meta", dest="meta_file", metavar="FILE", help="Metadata TOML file (auto-detect if not specified)"
        )
        parser.add_argument("--encoding", default="UTF-8", help="Text encoding (default: UTF-8)")
        parser.add_argument(
            "--key-size", type=int, default=32, metavar="SIZE", help="Key block size in KB (default: 32)"
        )
        parser.add_argument(
            "--record-size", type=int, default=64, metavar="SIZE", help="Record block size in KB (default: 64)"
        )
        parser.add_argument("--key-file", metavar="FILE", help="File containing specific keys to pack (one per line)")

    def _infer_output_filename(self, sources: list[str]) -> Path:
        """智能推断输出文件名"""
        first_source = Path(sources[0])

        # 检测是否为目录（通常是 MDD 内容）
        if first_source.is_dir():
            return Path(f"{first_source.name}.mdd")

        # 从文件名推断
        base_name = first_source.stem

        # 处理常见的命名模式
        if base_name.endswith(".mdx"):
            # wordfrequency.mdx.txt -> wordfrequency.mdx
            base_name = base_name[:-4]
            return Path(f"{base_name}.mdx")
        if base_name.endswith(".mdd"):
            # resources.mdd.txt -> resources.mdd
            base_name = base_name[:-4]
            return Path(f"{base_name}.mdd")
        # dict.txt -> dict.mdx (默认为词典)
        # 检查是否有多个源文件包含媒体内容
        has_media = any(
            Path(src).is_dir() or src.lower().endswith((".jpg", ".png", ".gif", ".mp3", ".wav")) for src in sources
        )

        if has_media:
            return Path(f"{base_name}.mdd")
        return Path(f"{base_name}.mdx")

    def execute(self, args: Namespace) -> None:
        """Execute the pack command."""
        # Validate inputs
        if not args.sources:
            raise CommandError("No source files specified. Use -a to add source files.")

        # 智能推断输出文件名
        if args.output:
            output_file = Path(args.output)
        else:
            output_file = self._infer_output_filename(args.sources)
            print(f"Auto-detected output file: {output_file}")

        if output_file.exists():
            response = input(f"Output file {output_file} already exists. Overwrite? [y/N]: ")
            if response.lower() != "y":
                raise CommandError("Operation cancelled")

        # Determine if this is MDD packing
        is_mdd = output_file.suffix.lower() == ".mdd"

        # Load metadata
        metadata_manager = MetadataManager()

        if args.meta_file:
            # Use specified metadata file
            meta_dict = metadata_manager.load_or_create(args.meta_file)
            print(f"Using metadata from: {args.meta_file}")
        else:
            # Try to auto-detect metadata file
            first_source = args.sources[0]
            meta_file_path = find_meta_file(first_source)

            if meta_file_path:
                meta_dict = metadata_manager.load_or_create(str(meta_file_path))
                print(f"Auto-detected metadata: {meta_file_path}")
            else:
                # Use default metadata
                meta_dict = metadata_manager.load_or_create()
                print("Using default metadata (no .meta.toml file found)")

        # Override metadata with command line arguments
        if args.encoding != "UTF-8":
            meta_dict.setdefault("advanced", {})["encoding"] = args.encoding
        if args.key_size != 32:
            meta_dict.setdefault("advanced", {})["key_size"] = args.key_size
        if args.record_size != 64:
            meta_dict.setdefault("advanced", {})["record_size"] = args.record_size

        # Load keys filter if specified
        keys = []
        if args.key_file:
            try:
                with open(args.key_file, encoding="utf-8") as f:
                    keys = [line.strip() for line in f if line.strip()]
                print(f"Loaded {len(keys)} keys from {args.key_file}")
            except Exception as e:
                raise CommandError(f"Failed to read key file {args.key_file}: {e}") from e

        # Prepare dictionary data
        print("Scanning source files...")
        dictionary = []
        total_entries = 0

        for source in args.sources:
            source_path = Path(source)
            if not source_path.exists():
                raise CommandError(f"Source file not found: {source}")

            print(f'Processing "{source}"...', end=" ", flush=True)

            try:
                if is_mdd:
                    # Handle MDD resources
                    if source_path.is_dir():
                        # Directory of files
                        entries = writer.pack_mdd_file(str(source_path))
                    elif source.endswith(".db"):
                        # Database source
                        entries = writer.pack_mdd_db(str(source_path))
                    else:
                        # Treat as file directory
                        entries = writer.pack_mdd_file(str(source_path))
                # Handle MDX text
                elif source.endswith(".db"):
                    # Database source
                    entries = writer.pack_mdx_db(str(source_path), encoding=args.encoding)
                else:
                    # Text file source
                    entries = writer.pack_mdx_txt(str(source_path), encoding=args.encoding, keys=keys or None)

                dictionary.extend(entries)
                entries_count = len(entries)
                total_entries += entries_count
                print(f"{entries_count} entries")

            except Exception as e:
                raise CommandError(f"Failed to process {source}: {e}") from e

        if not dictionary:
            raise CommandError("No dictionary entries found in source files")

        print(f"\nTotal entries: {total_entries}")

        # Convert metadata to writer parameters
        writer_params = metadata_manager.to_writer_params(meta_dict)

        # Pack the dictionary
        print(f'Packing to "{output_file}"...')

        try:
            writer.pack(
                str(output_file),
                dictionary,
                title=writer_params["title"],
                description=writer_params["description"],
                key_size=writer_params["key_size"],
                record_size=writer_params["record_size"],
                encoding=writer_params["encoding"],
                version=writer_params["version"],
                is_mdd=is_mdd,
            )

            file_size = output_file.stat().st_size
            print(f"✅ Successfully created {output_file} ({file_size:,} bytes)")

        except Exception as e:
            raise CommandError(f"Packing failed: {e}") from e
