"""LLM plugin for text file patching operations."""

import os
from pathlib import Path
import json

import llm
from pydantic import BaseModel, ValidationError

# Capture the initial working directory when the module is loaded
# This prevents CWD-change attacks from other tools during execution
_INITIAL_CWD = Path.cwd().resolve()


def _set_trusted_cwd_for_testing(new_cwd: Path) -> None:
    """Update the trusted CWD for testing purposes only.

    This should ONLY be used in test fixtures, not in production code.
    """
    global _INITIAL_CWD
    _INITIAL_CWD = new_cwd.resolve()


def _validate_path_security(file_path: str) -> tuple[Path, str]:
    """Validate and normalize a file path for security.

    Ensures the target path is within the initial working directory to prevent
    directory traversal attacks and unauthorized file access. Uses the working
    directory from when the module was loaded, not the current working directory,
    to prevent CWD-change attacks from other tools.

    Args:
        file_path: Path to validate (can be relative or absolute)

    Returns:
        tuple: (resolved_path, error_message_if_any)
               If error_message is not None, resolved_path will be None
    """
    try:
        # Use the initial CWD captured at module load time (security boundary)
        trusted_cwd = _INITIAL_CWD

        # Resolve the target path (handles .., ~, symlinks)
        target_path = Path(file_path).expanduser().resolve()

        # Check if target is within or equal to the trusted CWD
        try:
            target_path.relative_to(trusted_cwd)
        except ValueError:
            return (
                None,
                f"Error: Access denied - '{file_path}' is outside initial working directory",
            )

        return target_path, None

    except Exception as e:
        return None, f"Error: Invalid path '{file_path}': {str(e)}"


class EditOperation(BaseModel):
    """Represents a single edit operation."""

    old_string: str
    new_string: str
    replace_all: bool = False


def patch_read(file_path: str) -> str:
    """Read the complete contents of a text file.

    Args:
        file_path: Path to the file to read (can be relative or absolute)

    Returns:
        String containing the complete file contents, or error message
    """
    try:
        # Validate path security first
        path, error = _validate_path_security(file_path)
        if error:
            return error

        if not path.exists():
            return f"Error: File '{file_path}' does not exist"

        if not path.is_file():
            return f"Error: '{file_path}' is not a file"

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        return content

    except PermissionError:
        return f"Error: Permission denied reading '{file_path}'"
    except UnicodeDecodeError:
        return f"Error: Unable to decode '{file_path}' as text (binary file?)"
    except Exception as e:
        return f"Error reading '{file_path}': {str(e)}"


def patch_write(file_path: str, content: str) -> str:
    """Write content to a file, completely replacing any existing content.

    Args:
        file_path: Path to the file to write (can be relative or absolute)
        content: Content to write to the file

    Returns:
        Success message or error message
    """
    try:
        # Validate path security first
        path, error = _validate_path_security(file_path)
        if error:
            return error

        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Successfully wrote {len(content)} characters to '{file_path}'"

    except PermissionError:
        return f"Error: Permission denied writing to '{file_path}'"
    except Exception as e:
        return f"Error writing to '{file_path}': {str(e)}"


def patch_edit(
    file_path: str, old_string: str, new_string: str, replace_all: bool = False
) -> str:
    """Make a single string replacement in a file.

    Args:
        file_path: Path to the file to edit
        old_string: Text to find and replace
        new_string: Text to replace it with
        replace_all: If True, replace all occurrences; if False, replacement must be unique

    Returns:
        Success message or error message
    """
    try:
        # Validate path security first
        path, error = _validate_path_security(file_path)
        if error:
            return error

        if not path.exists():
            return f"Error: File '{file_path}' does not exist"

        if not path.is_file():
            return f"Error: '{file_path}' is not a file"

        # Read current content
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if old_string exists
        if old_string not in content:
            return f"Error: String not found in '{file_path}'"

        # Check uniqueness if not replace_all
        if not replace_all and content.count(old_string) > 1:
            return f"Error: String appears {content.count(old_string)} times in '{file_path}'. Use replace_all=True or provide more context to make it unique"

        # Perform replacement
        if replace_all:
            new_content = content.replace(old_string, new_string)
            replacements = content.count(old_string)
        else:
            new_content = content.replace(old_string, new_string, 1)
            replacements = 1

        # Write back
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return f"Successfully replaced {replacements} occurrence(s) in '{file_path}'"

    except PermissionError:
        return f"Error: Permission denied accessing '{file_path}'"
    except UnicodeDecodeError:
        return f"Error: Unable to decode '{file_path}' as text (binary file?)"
    except Exception as e:
        return f"Error editing '{file_path}': {str(e)}"


def patch_multi_edit(file_path: str, edits_json: str) -> str:
    """Make multiple string replacements in a file in sequence.

    Each edit is applied to the result of the previous edit, so the order matters.
    All edits must succeed or none will be applied.

    Args:
        file_path: Path to the file to edit
        edits_json: JSON string containing array of edit objects

    Example:
        [{"old_string": "foo", "new_string": "bar"},
         {"old_string": "baz", "new_string": "qux", "replace_all": true}]

    Returns:
        Success message or error message
    """
    try:
        # Validate path security first
        path, error = _validate_path_security(file_path)
        if error:
            return error

        if not path.exists():
            return f"Error: File '{file_path}' does not exist"

        if not path.is_file():
            return f"Error: '{file_path}' is not a file"

        # Parse edits JSON
        try:
            edits_data = json.loads(edits_json)
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON format - {str(e)}"

        if not isinstance(edits_data, list):
            return "Error: edits_json must be a JSON array of edit objects"

        if not edits_data:
            return "Error: No edits provided"

        # Validate edit operations
        edits = []
        for i, edit_data in enumerate(edits_data):
            try:
                edit = EditOperation(**edit_data)
                edits.append(edit)
            except ValidationError as e:
                return f"Error in edit {i + 1}: {str(e)}"

        # Read current content
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Apply edits sequentially
        for i, edit in enumerate(edits):
            if edit.old_string not in content:
                return f"Error in edit {i + 1}: String not found after previous edits"

            if not edit.replace_all and content.count(edit.old_string) > 1:
                return f"Error in edit {i + 1}: String appears {content.count(edit.old_string)} times. Use replace_all=true or provide more context"

            if edit.old_string == edit.new_string:
                return f"Error in edit {i + 1}: old_string and new_string are identical"

            # Apply the edit
            if edit.replace_all:
                content = content.replace(edit.old_string, edit.new_string)
            else:
                content = content.replace(edit.old_string, edit.new_string, 1)

        # Write back the final result
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        total_edits = len(edits)
        return f"Successfully applied {total_edits} edit(s) to '{file_path}'"

    except PermissionError:
        return f"Error: Permission denied accessing '{file_path}'"
    except UnicodeDecodeError:
        return f"Error: Unable to decode '{file_path}' as text (binary file?)"
    except Exception as e:
        return f"Error editing '{file_path}': {str(e)}"


def patch_info(file_path: str) -> str:
    """Get information about a file including size, permissions, and modification time.

    Args:
        file_path: Path to the file to examine

    Returns:
        Formatted string with file information or error message
    """
    try:
        # Validate path security first
        path, error = _validate_path_security(file_path)
        if error:
            return error

        if not path.exists():
            return f"Error: Path '{file_path}' does not exist"

        stat = path.stat()

        info = f"File: {path}\n"
        info += f"Size: {stat.st_size} bytes\n"
        info += f"Type: {'File' if path.is_file() else 'Directory' if path.is_dir() else 'Other'}\n"
        info += f"Readable: {os.access(path, os.R_OK)}\n"
        info += f"Writable: {os.access(path, os.W_OK)}\n"
        info += f"Modified: {stat.st_mtime}\n"

        if path.is_file():
            # Try to determine if it's a text file
            try:
                with open(path, "r", encoding="utf-8") as f:
                    f.read(100)  # Try to read first 100 chars
                info += "Encoding: Text (UTF-8 compatible)\n"
            except UnicodeDecodeError:
                info += "Encoding: Binary or non-UTF-8\n"

        return info

    except Exception as e:
        return f"Error getting info for '{file_path}': {str(e)}"


class Patch(llm.Toolbox):
    """Toolbox containing all text file manipulation tools.

    This toolbox provides safe, controlled access to file operations commonly needed
    when working with configuration files, source code, documentation, and other text files.

    ## Available Operations

    - **patch_read**: Read complete contents of a text file
    - **patch_write**: Write new content to a file (overwrites existing content)
    - **patch_edit**: Make a single string replacement in a file
    - **patch_multi_edit**: Make multiple string replacements in sequence
    - **patch_info**: Get file metadata and information

    ## Safety Features

    - Automatic encoding detection and UTF-8 handling
    - Parent directory creation when writing files
    - Comprehensive error handling and validation
    - Protection against binary file corruption
    - Atomic multi-edit operations (all succeed or all fail)

    ## Best Practices

    1. Always read a file before editing to understand its structure
    2. Use patch_info to verify file accessibility before operations
    3. For multiple changes, prefer patch_multi_edit over multiple patch_edit calls
    4. Be precise with string matching - include enough context to ensure uniqueness
    5. Use replace_all=True only when you're certain you want to replace all occurrences

    This toolbox is designed to be LLM-friendly with clear error messages and
    straightforward operations that map well to common file manipulation tasks.
    """

    def patch_read(self, file_path: str) -> str:
        """Read the complete contents of a text file.

        Perfect for examining configuration files, source code, or any text file
        before making changes. Handles various text encodings automatically.

        Args:
            file_path: Path to file (relative or absolute, ~ expansion supported)

        Returns:
            Complete file contents as string, or error message if unable to read
        """
        return patch_read(file_path)

    def patch_write(self, file_path: str, content: str) -> str:
        """Write content to a file, replacing any existing content completely.

        Use this when you need to create a new file or completely rewrite an existing one.
        Creates parent directories automatically if they don't exist.

        Args:
            file_path: Path to file to write
            content: Complete content to write to the file

        Returns:
            Success message with character count, or error message
        """
        return patch_write(file_path, content)

    def patch_edit(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False,
    ) -> str:
        """Make a single string replacement in a file.

        Finds exact string matches and replaces them. By default requires the match
        to be unique unless replace_all=True. Perfect for targeted changes like
        updating configuration values or fixing specific code sections.

        Args:
            file_path: Path to file to edit
            old_string: Exact string to find and replace
            new_string: String to replace it with
            replace_all: If True, replace all occurrences; if False, must be unique

        Returns:
            Success message with replacement count, or error message
        """
        return patch_edit(file_path, old_string, new_string, replace_all)

    def patch_multi_edit(self, file_path: str, edits_json: str) -> str:
        """Make multiple string replacements in a file in sequence.

        Applies edits one after another to the same file. Each edit operates on the
        result of the previous edit, so order matters. All edits must succeed or
        none will be applied. Perfect for complex refactoring or multi-step updates.

        Args:
            file_path: Path to file to edit
            edits_json: JSON array of edit objects with old_string, new_string, and optional replace_all

        Example JSON:
            [{"old_string": "port = 8080", "new_string": "port = 3000"},
             {"old_string": "debug = false", "new_string": "debug = true"}]

        Returns:
            Success message with total edit count, or error message
        """
        return patch_multi_edit(file_path, edits_json)

    def patch_info(self, file_path: str) -> str:
        """Get detailed information about a file including size, permissions, and type.

        Useful for understanding file characteristics before performing operations.
        Helps identify binary files, permission issues, and file accessibility.

        Args:
            file_path: Path to file or directory to examine

        Returns:
            Formatted information string including size, permissions, type, and encoding
        """
        return patch_info(file_path)


@llm.hookimpl
def register_tools(register):
    """Register patch toolbox with LLM."""
    register(Patch)
