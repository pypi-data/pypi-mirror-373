"""TOML metadata handling for MDict dictionaries."""

import tomllib
from pathlib import Path
from typing import Any


def load_meta(path: Path) -> dict[str, Any]:
    """Load metadata from TOML file."""
    if not path.exists():
        raise FileNotFoundError(f"Metadata file not found: {path}")

    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"Invalid TOML format in {path}: {e}") from e


def save_meta(meta: dict[str, Any], path: Path) -> None:
    """Save metadata to TOML file."""
    import tomli_w  # For writing TOML files

    try:
        with open(path, "wb") as f:
            tomli_w.dump(meta, f)
    except Exception as e:
        raise ValueError(f"Failed to save metadata to {path}: {e}") from e


def find_meta_file(base_path: str) -> Path | None:
    """
    Automatically find metadata file based on source file path.

    Examples:
        source.txt -> source.meta.toml
        mydict -> mydict.meta.toml
        /path/to/dict.txt -> /path/to/dict.meta.toml
    """
    base = Path(base_path)

    # Remove .txt extension if present
    if base.suffix == ".txt":
        name_without_ext = base.stem
    else:
        name_without_ext = base.name

    # Look for .meta.toml file in the same directory
    meta_file = base.parent / f"{name_without_ext}.meta.toml"

    return meta_file if meta_file.exists() else None


def merge_with_defaults(meta: dict[str, Any]) -> dict[str, Any]:
    """Merge user metadata with default values."""
    defaults = {
        "dictionary": {
            "version": "2.0",
            "author": "",
            "email": "",
            "website": "",
            "copyright": "",
        },
        "advanced": {
            "encoding": "UTF-8",
            "key_size": 32,  # KB
            "record_size": 64,  # KB
        },
    }

    # Deep merge function
    def deep_merge(base: dict, override: dict) -> dict:
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    return deep_merge(defaults, meta)


def toml_to_writer_params(meta: dict[str, Any]) -> dict[str, Any]:
    """Convert TOML metadata to parameters for writer functions with comprehensive defaults."""
    dict_meta = meta.get("dictionary", {})
    advanced = meta.get("advanced", {})

    # 为所有参数提供合理的默认值
    return {
        "title": dict_meta.get("title", "Untitled Dictionary"),
        "description": dict_meta.get("description", "A dictionary created with MDTT"),
        "encoding": advanced.get("encoding", "UTF-8"),
        "version": str(dict_meta.get("version", "2.0")),  # MDX 格式版本
        "key_size": advanced.get("key_size", 32) * 1024,  # 32KB 默认键块大小
        "record_size": advanced.get("record_size", 64) * 1024,  # 64KB 默认记录块大小
    }


def header_to_toml(mdx_header: dict[bytes, bytes], version: str = "2.0") -> dict[str, Any]:
    """Convert MDX header information to TOML format."""

    # Decode binary header data
    def decode_header_value(value: bytes) -> str:
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
            # Fallback for non-UTF-8 data
            return value.decode("utf-8", errors="replace")

    toml_data = {"dictionary": {}, "advanced": {}}

    # Map common header fields
    field_mapping = {
        b"Title": ("dictionary", "title"),
        b"Description": ("dictionary", "description"),
        b"Encoding": ("advanced", "encoding"),
        b"GeneratedByEngineVersion": ("advanced", "engine_version"),
        b"RequiredEngineVersion": ("advanced", "required_version"),
        b"CreationDate": ("advanced", "creation_date"),
    }

    for header_key, value in mdx_header.items():
        if header_key in field_mapping:
            section, key = field_mapping[header_key]
            decoded_value = decode_header_value(value)

            # Clean up description formatting
            if key == "description":
                decoded_value = decoded_value.replace("\r\n", "\n").strip()

            toml_data[section][key] = decoded_value

    # Set version from parameter or try to detect from headers
    if version:
        toml_data["dictionary"]["version"] = version
    elif b"GeneratedByEngineVersion" in mdx_header:
        toml_data["dictionary"]["version"] = decode_header_value(mdx_header[b"GeneratedByEngineVersion"])
    else:
        toml_data["dictionary"]["version"] = "2.0"  # Default

    # Add metadata that's commonly needed
    toml_data["advanced"]["extracted_date"] = ""  # Will be filled by caller

    return toml_data


def validate_metadata(meta: dict[str, Any]) -> list[str]:
    """Validate metadata structure and return list of issues."""
    issues = []

    if "dictionary" not in meta:
        issues.append("Missing 'dictionary' section")
        return issues

    dict_meta = meta["dictionary"]

    # Check required fields
    if not dict_meta.get("title", "").strip():
        issues.append("Dictionary title is required")

    # Check version only if present (allow missing version)
    version = dict_meta.get("version")
    if version is not None and str(version) not in ["1.2", "2.0", "3.0"]:
        issues.append(f"Invalid version '{version}', must be 1.2, 2.0, or 3.0")

    # Check advanced settings if present
    if "advanced" in meta:
        advanced = meta["advanced"]

        # Check key/record sizes
        for size_field in ["key_size", "record_size"]:
            if size_field in advanced:
                size = advanced[size_field]
                if not isinstance(size, int) or size <= 0:
                    issues.append(f"Invalid {size_field}: must be positive integer")

        # Check encoding
        encoding = advanced.get("encoding", "UTF-8")
        if not isinstance(encoding, str):
            issues.append("Encoding must be a string")

    return issues


def create_default_metadata(title: str = "", description: str = "") -> dict[str, Any]:
    """Create a simplified metadata structure with only essential fields."""
    return {
        "dictionary": {
            "title": title or "Untitled Dictionary",
            "description": description or "A dictionary created with MDTT",
            # 其他属性（version, author 等）在转换为 writer 参数时提供默认值
        }
        # advanced 部分也在转换时提供默认值，保持 TOML 文件简洁
    }


class MetadataManager:
    """Helper class for managing metadata operations."""

    def __init__(self, base_path: str | None = None):
        self.base_path = Path(base_path) if base_path else None
        self._cached_meta: dict[str, Any] | None = None

    def load_or_create(self, meta_path: str | None = None) -> dict[str, Any]:
        """Load metadata from file or create default if not found."""
        if meta_path:
            meta_file = Path(meta_path)
        elif self.base_path:
            meta_file = find_meta_file(str(self.base_path))
        else:
            meta_file = None

        if meta_file and meta_file.exists():
            self._cached_meta = load_meta(meta_file)
        else:
            self._cached_meta = create_default_metadata()

        return merge_with_defaults(self._cached_meta)

    def save(self, meta: dict[str, Any], path: Path) -> None:
        """Save metadata with validation."""
        issues = validate_metadata(meta)
        if issues:
            raise ValueError("Metadata validation failed:\n" + "\n".join(f"- {issue}" for issue in issues))

        save_meta(meta, path)
        self._cached_meta = meta

    def to_writer_params(self, meta: dict[str, Any] | None = None) -> dict[str, Any]:
        """Convert to writer parameters."""
        if meta is None:
            meta = self._cached_meta or {}
        return toml_to_writer_params(meta)
