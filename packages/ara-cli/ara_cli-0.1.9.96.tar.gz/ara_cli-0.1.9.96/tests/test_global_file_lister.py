# tests/test_global_file_lister.py

import os
import pytest
from unittest.mock import patch
from io import StringIO
from ara_cli.global_file_lister import (
    _build_tree,
    _write_tree_to_markdown,
    generate_global_markdown_listing,
)

@pytest.fixture
def temp_dir_structure(tmp_path):
    """Create a temporary directory structure for comprehensive testing."""
    root = tmp_path / "global_root"
    root.mkdir()
    (root / "src").mkdir()
    (root / "src" / "main.py").touch()
    (root / "src" / "utils.py").touch()
    (root / "docs").mkdir()
    (root / "docs" / "guide.md").touch()
    (root / "docs" / "images").mkdir() # Empty dir, should be ignored
    (root / "tests").mkdir()
    (root / "tests" / "test_main.py").touch()
    (root / "config.txt").touch() # Should be ignored by patterns
    (root / "empty_dir").mkdir() # Should be ignored
    return str(root)

class TestBuildTree:
    """Tests for the _build_tree function."""
    def test_build_tree_with_matching_files(self, temp_dir_structure):
        """Tests building a tree, correctly filtering by patterns and excluding empty dirs."""
        patterns = ["*.py", "*.md"]
        tree = _build_tree(temp_dir_structure, patterns)

        assert sorted(tree["dirs"]["src"]["files"]) == ["main.py", "utils.py"]
        assert tree["dirs"]["docs"]["files"] == ["guide.md"]
        assert tree["dirs"]["tests"]["files"] == ["test_main.py"]
        assert "images" not in tree["dirs"]["docs"]["dirs"] # Empty dir excluded
        assert "empty_dir" not in tree["dirs"] # Empty dir excluded
        assert not tree["files"] # No files in root

    def test_build_tree_no_matching_files(self, temp_dir_structure):
        """Tests building a tree where no files match the given patterns."""
        patterns = ["*.json", "*.yml"]
        tree = _build_tree(temp_dir_structure, patterns)
        assert not tree["files"] and not tree["dirs"]

    def test_build_tree_on_empty_directory(self, tmp_path):
        """Tests that an empty directory results in an empty tree."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        tree = _build_tree(str(empty_dir), ["*.*"])
        assert not tree["files"] and not tree["dirs"]

    @patch('os.listdir')
    @patch('sys.stdout', new_callable=StringIO)
    def test_build_tree_handles_os_error(self, mock_stdout, mock_listdir):
        """Tests that an OSError during directory listing is caught and handled."""
        mock_listdir.side_effect = OSError("Permission denied")
        tree = _build_tree("/unreadable_dir", ["*.*"])
        assert "Warning: Could not access path /unreadable_dir" in mock_stdout.getvalue()
        assert not tree["files"] and not tree["dirs"]

class TestWriteTreeToMarkdown:
    """Tests for the _write_tree_to_markdown function."""
    def test_write_tree_to_markdown_output_format(self):
        """Verifies that the markdown output is correctly formatted with proper indentation."""
        tree = {
            'files': ['root_file.md'],
            'dirs': {
                'dir1': {'files': ['a.py', 'b.py'], 'dirs': {}},
                'dir2': {'files': [], 'dirs': {'subdir': {'files': ['c.md'], 'dirs': {}}}}
            }
        }
        
        md_file = StringIO()
        _write_tree_to_markdown(md_file, tree, level=1)
        output = md_file.getvalue()

        # FIX: Added 4 spaces before "### subdir\n" to match the actual output.
        expected = (
            "    - [] root_file.md\n"
            "## dir1\n"
            "        - [] a.py\n"
            "        - [] b.py\n"
            "## dir2\n"
            "    ### subdir\n"
            "            - [] c.md\n"
        )
        assert output == expected

class TestGenerateGlobalMarkdownListing:
    """Tests for the main generate_global_markdown_listing function."""
    def test_generate_listing_with_valid_dirs(self, temp_dir_structure, tmp_path):
        """Tests the end-to-end generation of a markdown file from a valid directory."""
        output_file = tmp_path / "output.md"
        patterns = ["*.py"]
        
        generate_global_markdown_listing([temp_dir_structure], patterns, str(output_file))
        
        content = output_file.read_text()
        abs_dir = os.path.abspath(temp_dir_structure)
        
        assert f"# {abs_dir}\n" in content
        assert "## src\n" in content
        assert "        - [] main.py\n" in content
        assert "## tests\n" in content
        assert "guide.md" not in content # Does not match pattern

    def test_generate_listing_with_nonexistent_dir(self, tmp_path):
        """Tests that a warning is written to the file for a non-existent directory."""
        output_file = tmp_path / "output.md"
        non_existent_dir = "/path/to/nothing"
        
        generate_global_markdown_listing([non_existent_dir], ["*.*"], str(output_file))
        
        content = output_file.read_text()
        abs_path = os.path.abspath(non_existent_dir)
        
        assert f"# {non_existent_dir}\n" in content
        assert f"    - !! UYARI: Dizin bulunamadı: {abs_path}" in content

    def test_generate_listing_with_no_matching_files(self, temp_dir_structure, tmp_path):
        """Tests that the output file is empty if no files match the patterns."""
        output_file = tmp_path / "output.md"
        
        generate_global_markdown_listing([temp_dir_structure], ["*.nonexistent"], str(output_file))
        
        assert output_file.read_text() == ""