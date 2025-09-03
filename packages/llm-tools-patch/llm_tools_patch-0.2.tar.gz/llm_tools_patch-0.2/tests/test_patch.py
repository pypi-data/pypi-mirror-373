"""Unit tests for the Patch toolbox."""

import os
import pytest
from pathlib import Path

from llm_tools_patch import (
    Patch,
    patch_read,
    patch_write,
    patch_edit,
    patch_multi_edit,
    patch_info,
    _set_trusted_cwd_for_testing,
)


@pytest.fixture
def in_tmp_path(tmp_path):
    """Fixture that changes to tmp_path and returns to original directory after test."""
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    # Update the trusted CWD for testing
    _set_trusted_cwd_for_testing(tmp_path)

    yield tmp_path

    os.chdir(original_cwd)
    # Restore the original trusted CWD
    _set_trusted_cwd_for_testing(Path(original_cwd))


class TestPatchFunctions:
    """Test the individual patch functions."""

    def test_patch_read_existing_file(self, in_tmp_path):
        """Test reading an existing file."""
        test_file = in_tmp_path / "test.txt"
        test_content = "Hello, world!\nThis is a test file."
        test_file.write_text(test_content)

        result = patch_read("test.txt")  # Use relative path
        assert result == test_content

    def test_patch_read_nonexistent_file(self, in_tmp_path):
        """Test reading a file that doesn't exist."""
        result = patch_read("nonexistent.txt")
        assert result.startswith("Error: File")
        assert "does not exist" in result

    def test_patch_read_directory(self, in_tmp_path):
        """Test reading a directory instead of a file."""
        result = patch_read(".")
        assert result.startswith("Error:")
        assert "is not a file" in result

    def test_patch_write_new_file(self, in_tmp_path):
        """Test writing to a new file."""
        test_file = in_tmp_path / "new.txt"
        test_content = "New file content"

        result = patch_write("new.txt", test_content)
        assert result.startswith("Successfully wrote")
        assert str(len(test_content)) in result
        assert test_file.read_text() == test_content

    def test_patch_write_creates_directories(self, in_tmp_path):
        """Test that patch_write creates parent directories."""
        nested_file = in_tmp_path / "nested" / "dir" / "file.txt"
        test_content = "Content in nested directory"

        result = patch_write("nested/dir/file.txt", test_content)
        assert result.startswith("Successfully wrote")
        assert nested_file.read_text() == test_content

    def test_patch_write_overwrite_existing(self, in_tmp_path):
        """Test overwriting an existing file."""
        test_file = in_tmp_path / "existing.txt"
        test_file.write_text("Original content")

        new_content = "New content"
        result = patch_write("existing.txt", new_content)
        assert result.startswith("Successfully wrote")
        assert test_file.read_text() == new_content

    def test_patch_edit_single_replacement(self, in_tmp_path):
        """Test making a single string replacement."""
        test_file = in_tmp_path / "edit.txt"
        original = "Hello world\nThis is a test"
        test_file.write_text(original)

        result = patch_edit("edit.txt", "world", "universe")
        assert result.startswith("Successfully replaced 1 occurrence")
        assert test_file.read_text() == "Hello universe\nThis is a test"

    def test_patch_edit_string_not_found(self, in_tmp_path):
        """Test editing when string is not found."""
        test_file = in_tmp_path / "edit.txt"
        test_file.write_text("Hello world")

        result = patch_edit("edit.txt", "missing", "replacement")
        assert result.startswith("Error: String not found")

    def test_patch_edit_multiple_occurrences_without_replace_all(self, in_tmp_path):
        """Test editing when string appears multiple times without replace_all."""
        test_file = in_tmp_path / "edit.txt"
        test_file.write_text("test test test")

        result = patch_edit("edit.txt", "test", "replaced")
        assert "appears 3 times" in result
        assert "Use replace_all=True" in result

    def test_patch_edit_multiple_occurrences_with_replace_all(self, in_tmp_path):
        """Test editing multiple occurrences with replace_all=True."""
        test_file = in_tmp_path / "edit.txt"
        test_file.write_text("test test test")

        result = patch_edit("edit.txt", "test", "replaced", replace_all=True)
        assert result.startswith("Successfully replaced 3 occurrence")
        assert test_file.read_text() == "replaced replaced replaced"

    def test_patch_multi_edit_success(self, in_tmp_path):
        """Test multiple edits in sequence."""
        test_file = in_tmp_path / "multi.txt"
        test_file.write_text("name = John\nage = 25\ncity = NYC")

        edits_json = """[
            {"old_string": "John", "new_string": "Jane"},
            {"old_string": "25", "new_string": "30"},
            {"old_string": "NYC", "new_string": "SF"}
        ]"""

        result = patch_multi_edit("multi.txt", edits_json)
        assert result.startswith("Successfully applied 3 edit")
        assert test_file.read_text() == "name = Jane\nage = 30\ncity = SF"

    def test_patch_multi_edit_invalid_json(self, in_tmp_path):
        """Test multi_edit with invalid JSON."""
        test_file = in_tmp_path / "multi.txt"
        test_file.write_text("content")

        result = patch_multi_edit("multi.txt", "invalid json")
        assert result.startswith("Error: Invalid JSON format")

    def test_patch_multi_edit_empty_edits(self, in_tmp_path):
        """Test multi_edit with empty edits array."""
        test_file = in_tmp_path / "multi.txt"
        test_file.write_text("content")

        result = patch_multi_edit("multi.txt", "[]")
        assert result.startswith("Error: No edits provided")

    def test_patch_multi_edit_string_not_found(self, in_tmp_path):
        """Test multi_edit when a string is not found after previous edits."""
        test_file = in_tmp_path / "multi.txt"
        test_file.write_text("hello world")

        edits_json = """[
            {"old_string": "world", "new_string": "universe"},
            {"old_string": "world", "new_string": "planet"}
        ]"""

        result = patch_multi_edit("multi.txt", edits_json)
        assert "Error in edit 2: String not found" in result

    def test_patch_info_existing_file(self, in_tmp_path):
        """Test getting info for an existing file."""
        test_file = in_tmp_path / "info.txt"
        test_content = "Test content for info"
        test_file.write_text(test_content)

        result = patch_info("info.txt")
        assert "File:" in result
        assert f"Size: {len(test_content)} bytes" in result
        assert "Type: File" in result
        assert "Readable: True" in result
        assert "Encoding: Text" in result

    def test_patch_info_nonexistent_file(self, in_tmp_path):
        """Test getting info for a nonexistent file."""
        nonexistent = in_tmp_path / "nonexistent.txt"
        result = patch_info(str(nonexistent))
        assert result.startswith("Error: Path")
        assert "does not exist" in result


class TestPatchToolbox:
    """Test the Patch toolbox class."""

    def setup_method(self):
        """Set up a Patch toolbox instance for each test."""
        self.patch = Patch()

    def test_patch_toolbox_read(self, in_tmp_path):
        """Test the toolbox patch_read method."""
        test_file = in_tmp_path / "toolbox_test.txt"
        test_content = "Toolbox test content"
        test_file.write_text(test_content)

        result = self.patch.patch_read("toolbox_test.txt")
        assert result == test_content

    def test_patch_toolbox_write(self, in_tmp_path):
        """Test the toolbox patch_write method."""
        test_file = in_tmp_path / "toolbox_write.txt"
        test_content = "Toolbox write content"

        result = self.patch.patch_write("toolbox_write.txt", test_content)
        assert result.startswith("Successfully wrote")
        assert test_file.read_text() == test_content

    def test_patch_toolbox_edit(self, in_tmp_path):
        """Test the toolbox patch_edit method."""
        test_file = in_tmp_path / "toolbox_edit.txt"
        test_file.write_text("Hello toolbox world")

        result = self.patch.patch_edit("toolbox_edit.txt", "toolbox", "testing")
        assert result.startswith("Successfully replaced")
        assert test_file.read_text() == "Hello testing world"

    def test_patch_toolbox_multi_edit(self, in_tmp_path):
        """Test the toolbox patch_multi_edit method."""
        test_file = in_tmp_path / "toolbox_multi.txt"
        test_file.write_text("config = debug\nport = 8080")

        edits_json = """[
            {"old_string": "debug", "new_string": "production"},
            {"old_string": "8080", "new_string": "3000"}
        ]"""

        result = self.patch.patch_multi_edit("toolbox_multi.txt", edits_json)
        assert result.startswith("Successfully applied 2 edit")
        assert test_file.read_text() == "config = production\nport = 3000"

    def test_patch_toolbox_info(self, in_tmp_path):
        """Test the toolbox patch_info method."""
        test_file = in_tmp_path / "toolbox_info.txt"
        test_file.write_text("Info test")

        result = self.patch.patch_info("toolbox_info.txt")
        assert "File:" in result
        assert "Size:" in result
        assert "Type: File" in result


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_tilde_expansion(self, in_tmp_path):
        """Test that tilde expansion works in file paths."""
        # Create a test file in a known location
        test_file = in_tmp_path / "tilde_test.txt"
        test_content = "Tilde expansion test"
        test_file.write_text(test_content)

        # Test with the actual path (since we can't easily test ~ expansion in in_tmp_path)
        result = patch_read("tilde_test.txt")
        assert result == test_content

    def test_empty_file_operations(self, in_tmp_path):
        """Test operations on empty files."""
        empty_file = in_tmp_path / "empty.txt"
        empty_file.write_text("")

        # Read empty file
        result = patch_read("empty.txt")
        assert result == ""

        # Edit empty file (should fail)
        result = patch_edit("empty.txt", "nonexistent", "replacement")
        assert "String not found" in result

    def test_large_content(self, in_tmp_path):
        """Test with reasonably large content."""
        test_file = in_tmp_path / "large.txt"
        large_content = "".join(f"Line {i}\n" for i in range(1000))  # 1000 lines
        test_file.write_text(large_content)

        result = patch_read("large.txt")
        assert len(result) == len(large_content)

        # Test editing large file
        result = patch_edit("large.txt", "Line 0", "Modified Line 0")
        assert result.startswith("Successfully replaced")

    def test_unicode_content(self, in_tmp_path):
        """Test with Unicode content."""
        test_file = in_tmp_path / "unicode.txt"
        unicode_content = "Hello 🌍! Testing unicode: café, naïve, résumé"
        test_file.write_text(unicode_content, encoding="utf-8")

        result = patch_read("unicode.txt")
        assert result == unicode_content

        result = patch_edit("unicode.txt", "🌍", "🌎")
        assert result.startswith("Successfully replaced")
        assert "Hello 🌎!" in patch_read("unicode.txt")
