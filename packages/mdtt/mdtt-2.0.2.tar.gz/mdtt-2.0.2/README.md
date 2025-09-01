# MDTT - MDx Dict Trans ToolKit

A modern Python 3.13+ tool for packing and unpacking MDict dictionary files (.mdx/.mdd) with advanced features and intuitive CLI interface.

English | [中文](https://github.com/libukai/mdtt/blob/master/README-zh.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> **Version 2.0 - Complete Rewrite:**
> - 🆕 **Modern Subcommand Architecture** - Clean CLI interface similar to `git` and `docker`
> - 🆕 **TOML Metadata Management** - User-friendly `.meta.toml` configuration files with auto-detection
> - 🆕 **Rich Information Display** - Beautiful formatted output with JSON/TOML export options
> - 🆕 **Comprehensive Testing** - Full test suite including unit, integration, and real-file testing
> - 🆕 **Enhanced Query System** - Smart output file naming and custom file specification
> - 🆕 **Format Conversion Tools** - Built-in converters between text, database, and MDict formats

## Key Features

- ✅ **Full MDict Support**: Read/Write MDict 2.0, Read MDict 3.0, supports encrypted dictionaries
- ✅ **Multiple Output Formats**: MDX/MDD files, SQLite databases, plain text, split files
- ✅ **Intelligent CLI**: Context-aware commands with comprehensive help and error handling
- ✅ **Metadata System**: Automatic `.meta.toml` file detection and generation
- ✅ **Advanced Extraction**: Split by alphabet, custom chunk sizes, metadata export
- ✅ **Developer Friendly**: Modern Python 3.13+, uv package manager, comprehensive type hints

## Installation

### From PyPI (Recommended)
```bash
pip install mdtt
```

### Development Setup
```bash
git clone https://github.com/likai/mdtt.git
cd mdtt
uv sync  # Install dependencies with uv (recommended)
# or: pip install -e ".[dev]"  # Alternative with pip
```

### Requirements
- Python 3.13+ (required for modern typing features)
- Optional: `uv` package manager for faster dependency resolution

## Quick Start

### View Available Commands
```bash
mdtt --help
```

### Extract a Dictionary
```bash
# Basic extraction (outputs to current directory with .txt and .meta.toml)
mdtt extract my_dict.mdx

# Extract to specific directory
mdtt extract my_dict.mdx -o ./output

# Extract as database
mdtt extract my_dict.mdx --db

# Extract without metadata file
mdtt extract my_dict.mdx --no-meta
```

### Create a Dictionary

1. **Create your content file** (`my_dict.txt`):
```
apple
A round fruit that grows on trees.
</>
banana
A long curved yellow fruit.
</>
```

2. **Create metadata file** (`my_dict.meta.toml`):
```toml
[dictionary]
title = "My Custom Dictionary"
description = "A simple English dictionary"
```

3. **Pack the dictionary**:
```bash
# Auto-detect output filename
mdtt pack -a my_dict.txt

# Or specify explicit output name  
mdtt pack -a my_dict.txt my_dict.mdx
```

### Query and Information

```bash
# Query a word (displays result and saves to apple.html)
mdtt query apple my_dict.mdx

# Query with custom output filename
mdtt query apple my_dict.mdx -o definitions/apple_def.html

# Query phrases (automatically creates safe filenames)
mdtt query "can't believe" my_dict.mdx  # Creates can_t_believe.html

# Show dictionary information (rich formatted output)
mdtt info my_dict.mdx

# Export information as JSON or TOML
mdtt info my_dict.mdx --format json
mdtt info my_dict.mdx --format toml

# List dictionary keys with filtering
mdtt keys my_dict.mdx --limit 100
mdtt keys my_dict.mdx --pattern "apple*"
```

## Advanced Usage

### Working with TOML Metadata

Create `.meta.toml` files for automatic metadata detection:

```toml
[dictionary]
title = "Oxford Advanced Dictionary"
description = """
Comprehensive English dictionary with detailed definitions.
Perfect for students and professionals.
"""

# 其他属性（encoding, version 等）使用系统默认值
# 如需自定义，可添加 [advanced] 部分
```

### Multiple Input Sources

```bash
# Pack multiple files (auto-detect output name)
mdtt pack -a part1.txt -a part2.txt

# Pack with explicit output name
mdtt pack -a part1.txt -a part2.txt combined.mdx

# Use custom metadata
mdtt pack -a source.txt -m custom.meta.toml

# Pack media resources (auto-detects .mdd extension)
mdtt pack -a images_folder/
```

### Format Conversion & Import Tools

```bash
# Convert between text and database formats
mdtt convert txt-to-db dict.txt dict.db
mdtt convert db-to-txt dict.db dict.txt

# TBX (Translation Memory) to MDict conversion
# Convert TBX/TMX translation memory files to MDict format
python tests/script_convert_tbx_to_mdict.py input.tbx output.mdx
# Features:
# - Automatic metadata generation from TBX header
# - CSS styling for professional appearance  
# - Support for multiple languages and terminology
```

### Advanced Query Options

```bash
# Query with automatic HTML output (creates word.html)
mdtt query "hello world" my_dict.mdx

# Query with custom output file
mdtt query apple my_dict.mdx -o definitions/apple.html

# Query encrypted dictionaries
mdtt query word encrypted.mdx --passcode mypassword

# Special characters in queries are handled automatically
# e.g., "can't" becomes "can_t.html"
mdtt query "can't" my_dict.mdx
```

### Advanced Extraction Options

```bash
# Split by alphabet (with metadata)
mdtt extract large_dict.mdx --split-az

# Split into N files
mdtt extract large_dict.mdx --split-n 5

# Handle encrypted dictionaries
mdtt extract encrypted.mdx --passcode mypassword

# Extract to specific directory without metadata
mdtt extract dict.mdx -o ./output --no-meta
```

## Command Reference

| Command | Purpose | Key Features | Options |
|---------|---------|-------------|---------|
| `extract` | Extract MDX/MDD files with metadata export | Auto-metadata export, split options, database output | `-o` (output dir), `--db`, `--no-meta`, `--split-az`, `--split-n` |
| `pack` | Create MDX/MDD from sources (smart output naming) | Auto-detects output filename, metadata file discovery | `-a` (add source), `-m` (metadata file), multiple sources |
| `query` | Search words with smart HTML file output | Safe filename generation, custom output paths | `-o` (output file), `--passcode`, auto HTML creation |
| `info` | Display rich dictionary information | Beautiful formatting, multiple export formats | `--format` (text/json/toml), comprehensive metadata |
| `keys` | List and filter dictionary keys | Pattern matching, pagination, sampling | `--limit`, `--pattern`, memory-efficient streaming |
| `convert` | Convert between formats | Text ↔ Database conversion, preservation of structure | `txt-to-db`, `db-to-txt`, maintains indexes |

### Special Tools
- **TBX Converter**: `tests/script_convert_tbx_to_mdict.py` - Convert TBX/TMX translation memories to MDict format

## Testing

The project includes comprehensive testing:

```bash
# Run all tests
tests/run_tests.sh all

# Run specific test types
tests/run_tests.sh unit          # Fast unit tests
tests/run_tests.sh integration   # Tests with real files
tests/run_tests.sh -c            # With coverage report

# Shell integration test
tests/test_integration.sh
```

## MDX File Format

An `.mdx` file consists of:

1. **Header**: Dictionary metadata (Title, Description, Version, etc.) in UTF-16LE XML
2. **Keyword Section**: Compressed blocks of keywords with index for quick lookup
3. **Record Section**: Compressed blocks of dictionary entries (HTML content)

This structure allows efficient random access even in large dictionaries with millions of entries.

## Development

### Project Architecture

The project follows a modern, modular architecture:

```
src/mdict_utils/
├── __main__.py          # CLI entry point with subcommand routing
├── commands/            # Individual command implementations
│   ├── extract.py       # Dictionary extraction with metadata
│   ├── pack.py          # Dictionary packing with auto-detection
│   ├── query.py         # Word lookup with smart file output
│   ├── info.py          # Rich information display
│   ├── keys.py          # Key listing and filtering
│   └── convert.py       # Format conversion utilities
├── base/                # Low-level MDict format implementation
├── metadata.py          # TOML metadata management system
├── reader.py           # High-level reading interface
└── writer.py           # High-level writing interface
```

**Core Statistics:**
- ~4,700 lines of Python code
- 6 main commands with consistent interface
- Comprehensive test suite (38+ tests)
- Full type hints and documentation

### Development Setup

```bash
git clone https://github.com/likai/mdtt.git
cd mdtt
uv sync  # Install dependencies and create virtual environment
```

### Code Quality & Testing

```bash
# Code quality checks
uv run ruff check         # Linting (pycodestyle, pyflakes, security, etc.)
uv run ruff format        # Code formatting
uv run pyright          # Static type checking

# Testing options
tests/run_tests.sh all           # Complete test suite
tests/run_tests.sh unit          # Fast unit tests only  
tests/run_tests.sh integration   # Integration tests with real files
tests/run_tests.sh -c            # Run with coverage report
tests/test_integration.sh        # Shell-based integration testing

# Direct pytest usage
uv run pytest                   # Run all tests
uv run pytest -m "not slow"     # Skip performance tests
```

### Current Status

- ✅ **Core Functionality**: All major features implemented and tested
- ✅ **Modern CLI**: Complete subcommand architecture with rich help
- ✅ **TOML Metadata**: Full implementation with auto-detection
- ✅ **Test Coverage**: Comprehensive testing including real dictionary files
- ⚠️ **Code Quality**: Minor linting issues in legacy base modules (308 warnings)
- 🔄 **Active Development**: Recent commits include TBX converter and enhanced query system


## Acknowledgments

This project is built upon and significantly evolved from the original [mdict-utils](https://github.com/liuyug/mdict-utils) by Yugang LIU. While MDTT has been extensively rewritten with modern architecture, new features, and enhanced functionality, we acknowledge the foundational work that made this project possible.

Key differences in MDTT:
- Complete rewrite with modern Python 3.13+ and subcommand architecture
- TOML-based metadata management system  
- Enhanced CLI interface with comprehensive help
- Extensive test suite with real dictionary file testing
- New features: TBX conversion, smart query system, format conversion tools

### Migration from mdict-utils v1.x

If you're upgrading from the original mdict-utils v1.x:

1. **Update command syntax** to use subcommands
2. **Replace** `-t`/`-d` flags with `.meta.toml` files
3. **Use** `mdtt info` instead of `mdtt -m`
4. **Benefit** from improved help, error messages, and output formatting

## Reference

- [MDict Format Analysis](https://bitbucket.org/xwang/mdict-analysis)
- [Write MDict](https://github.com/zhansliu/writemdict)

## License

MIT License - see LICENSE file for details.
