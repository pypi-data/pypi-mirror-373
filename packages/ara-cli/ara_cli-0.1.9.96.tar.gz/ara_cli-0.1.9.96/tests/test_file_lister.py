import os
import tempfile
import shutil
import pytest
from unittest.mock import MagicMock, patch
from ara_cli.file_lister import generate_markdown_listing, list_files_in_directory, get_files_in_directory, list_files
from ara_cli.list_filter import ListFilter


@pytest.fixture
def setup_test_environment():
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Create nested directories and files
    os.makedirs(os.path.join(temp_dir, 'dir1'))
    os.makedirs(os.path.join(temp_dir, 'dir2', 'subdir1'))

    # Create files
    open(os.path.join(temp_dir, 'file1.py'), 'a').close()
    open(os.path.join(temp_dir, 'file2.txt'), 'a').close()
    open(os.path.join(temp_dir, 'dir1', 'file3.py'), 'a').close()
    open(os.path.join(temp_dir, 'dir2', 'file4.py'), 'a').close()
    open(os.path.join(temp_dir, 'dir2', 'subdir1', 'file5.py'), 'a').close()

    yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir)


def test_generate_markdown_listing_multiple_directories(setup_test_environment):
    temp_dir = setup_test_environment
    another_temp_dir = tempfile.mkdtemp()

    try:
        os.makedirs(os.path.join(another_temp_dir, 'dir3'))
        open(os.path.join(another_temp_dir, 'file6.py'), 'a').close()

        output_file_path = os.path.join(temp_dir, "output_multiple_dirs.md")

        expected_content = [
            f"# {os.path.basename(temp_dir)}",
            " - [] file1.py",
            "## dir1",
            "     - [] file3.py",
            "## dir2",
            "     - [] file4.py",
            "### subdir1",
            "         - [] file5.py",
            f"# {os.path.basename(another_temp_dir)}",
            " - [] file6.py",
            "## dir3"
        ]

        generate_markdown_listing([temp_dir, another_temp_dir], ['*.py'], output_file_path)

        with open(output_file_path, 'r', encoding='utf-8') as f:
            output_content = f.read().splitlines()

        assert output_content == expected_content

    finally:
        shutil.rmtree(another_temp_dir)


def test_get_files_in_directory():
    with patch('os.scandir') as mock_scandir:
        mock_entry = MagicMock()
        mock_entry.is_file.return_value = True
        mock_entry.name = 'file1.py'
        mock_scandir.return_value.__enter__.return_value = [mock_entry]

        result = get_files_in_directory('some_directory')

        assert result == ['some_directory/file1.py']


@pytest.mark.parametrize("files, expected_output", [
    ([], ""),
    (["file1.py"], "- file1.py"),
    (["file1.py", "file2.txt"], "- file1.py\n- file2.txt")
])
def test_list_files(capfd, files, expected_output):
    list_files(files)
    captured = capfd.readouterr()
    assert captured.out.strip() == expected_output


@patch('ara_cli.file_lister.get_files_in_directory')
@patch('ara_cli.file_lister.filter_list')
@patch('ara_cli.file_lister.list_files')
def test_list_files_in_directory(mock_list_files, mock_filter_list, mock_get_files_in_directory):
    mock_get_files_in_directory.return_value = ['some_directory/file1.py']
    mock_filter_list.return_value = ['some_directory/file1.py']

    list_files_in_directory('some_directory', list_filter=None)

    mock_get_files_in_directory.assert_called_once_with('some_directory')
    mock_filter_list.assert_called_once_with(['some_directory/file1.py'], None)
    mock_list_files.assert_called_once_with(['some_directory/file1.py'])


@patch('ara_cli.file_lister.get_files_in_directory')
@patch('ara_cli.file_lister.filter_list')
@patch('ara_cli.file_lister.list_files')
def test_list_files_in_directory_with_filter(mock_list_files, mock_filter_list, mock_get_files_in_directory):
    mock_get_files_in_directory.return_value = ['some_directory/file1.py', 'some_directory/file2.txt']
    mock_filter_list.return_value = ['some_directory/file1.py']

    list_filter = ListFilter(
        include_extension=['.py'],
        exclude_extension=None,
        include_content=None,
        exclude_content=None
    )

    list_files_in_directory('some_directory', list_filter=list_filter)

    mock_get_files_in_directory.assert_called_once_with('some_directory')
    mock_filter_list.assert_called_once_with(['some_directory/file1.py', 'some_directory/file2.txt'], list_filter)
    mock_list_files.assert_called_once_with(['some_directory/file1.py'])
