# llm-tools-patch

[![PyPI](https://img.shields.io/pypi/v/llm-tools-patch.svg)](https://pypi.org/project/llm-tools-patch/)
[![Changelog](https://img.shields.io/github/v/release/dannyob/llm-tools-patch?include_prereleases&label=changelog)](https://github.com/dannyob/llm-tools-patch/releases)
[![Tests](https://github.com/dannyob/llm-tools-patch/actions/workflows/test.yml/badge.svg)](https://github.com/dannyob/llm-tools-patch/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/dannyob/llm-tools-patch/blob/main/LICENSE)

LLM plugin for Simon Willison's `llm` providing text file manipulation, including reading, writing, and edits.

## Installation

Install this plugin in the same environment as [LLM](https://llm.datasette.io/). You'll need at least LLM [0.26a1](https://llm.datasette.io/en/latest/changelog.html#a1-2025-05-25) or later.

### From PyPI (recommended)

```bash
llm install llm-tools-patch
```

### From source

```bash
git clone https://github.com/dannyob/llm-tools-patch
cd llm-tools-patch
llm install .
```

## ⚠️ Security Warning

**This plugin provides AI agents with direct file system access.** The tools can read, write, and modify files within your current working directory. Before enabling this plugin:

- File access is restricted to the working directory where you run the `llm` command
- Only use with trusted AI models and prompts
- Use `--ta` (tool approval) mode - review all file operations carefully
- Consider the potential impact if an AI agent modifies important files

## Usage

The plugin provides a single `Patch` toolbox with five core operations:

### Available Tools

- `read` - Read complete contents of a text file
- `write` - Write new content to a file (overwrites existing)
- `edit` - Make a single string replacement
- `multi_edit` - Apply multiple string replacements in sequence  
- `info` - Get file metadata and information

### Basic Usage

```bash
# Make a single edit
llm prompt -m gpt-4o-mini "Change port 8080 to 3000 in config.txt" --tool Patch --ta
```

```bash
# Make multiple edits
llm prompt -m gpt-4o-mini "Add a smiley face to the first heading in README.md, then a thank you emoji to the last heading" --tool Patch --ta --chain-limit 0
```

### Recommended Options

For interactive use, combine these flags:
- `--ta` - Requires user confirmation before executing functions (safety)
- `--chain-limit 0` - Allows unlimited tool calls in one session (default is 5)

## Development

### Setup Development Environment

```bash
# Clone and set up development environment
git clone https://github.com/dannyob/llm-tools-patch
cd llm-tools-patch
make dev-setup
source .venv/bin/activate
```

### Testing

```bash
make test           # Run all tests
make test-coverage  # Run tests with coverage report
make quick-test     # Fast test run (exits on first failure)
```

### Plugin Testing

After installation, verify the plugin is working:

```bash
llm tools  # Should list Patch tools
llm prompt "Read this README.md file" --tool Patch
```

## Credits and Thanks

Inspired by Claude Code's Read, Edit and MultiEdit tools.

Coded with Claude.
