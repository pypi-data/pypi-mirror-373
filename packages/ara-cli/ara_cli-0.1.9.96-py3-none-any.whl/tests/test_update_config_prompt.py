from ara_cli.classifier import Classifier
from unittest.mock import patch, mock_open, MagicMock
import pytest
import os

from ara_cli.update_config_prompt import (
    read_file, write_file, find_checked_items, update_items_in_file,
    update_config_prompt_files, update_artefact_config_prompt_files,
    ensure_directory_exists, handle_existing_file
)

# Mock content for testing
mock_content = """
# Section 1
[x] Item 1
[] Item 2
## Section 1.1
[x] Item 1.1
# Section 2
[] Item 3
"""

mock_content_updated = """
# Section 1
[x] Item 1
[x] Item 2
## Section 1.1
[x] Item 1.1
# Section 2
[] Item 3
"""


def test_read_file():
    with patch('builtins.open', mock_open(read_data="data")) as mocked_file:
        result = read_file('dummy_path')
        mocked_file.assert_called_once_with('dummy_path', 'r', encoding='utf-8')
        assert result == "data"

def test_write_file():
    with patch('builtins.open', mock_open()) as mocked_file:
        write_file('dummy_path', 'data')
        mocked_file.assert_called_once_with('dummy_path', 'w', encoding='utf-8')
        mocked_file().write.assert_called_once_with('data')

def test_find_checked_items():
    checked_items = find_checked_items(mock_content)
    assert checked_items == [
        "# Section 1[x] Item 1",
        "# Section 1## Section 1.1[x] Item 1.1"
    ]

def test_update_items_in_file():
    checked_items = ["# Section 1[x] Item 2", "# Section 1## Section 1.1[x] Item 1.1"]
    updated_content = update_items_in_file(mock_content, checked_items)
    assert updated_content == mock_content_updated


@patch('ara_cli.update_config_prompt.read_file')
@patch('ara_cli.update_config_prompt.write_file')
@patch('ara_cli.update_config_prompt.update_items_in_file')
@patch('os.replace')
def test_update_config_prompt_files(mock_replace, mock_update_items_in_file, mock_write_file, mock_read_file):
    mock_read_file.side_effect = [mock_content, mock_content]
    mock_update_items_in_file.return_value = mock_content_updated

    update_config_prompt_files('input1', 'input2')

    mock_read_file.assert_any_call('input1')
    mock_read_file.assert_any_call('input2')
    mock_write_file.assert_called_once_with('input2', mock_content_updated)
    mock_replace.assert_called_once_with('input2', 'input1')


@pytest.mark.parametrize("path, exists", [
    ("/path/that/exists", True),
    ("/path/that/does/not/exist", False),
])
@patch("os.makedirs")
@patch("os.path.exists")
def test_ensure_directory_exists(mock_exists, mock_makedirs, path, exists):
    mock_exists.return_value = exists

    ensure_directory_exists(path)

    mock_exists.assert_called_once_with(path)
    if not exists:
        mock_makedirs.assert_called_once_with(path)
    else:
        mock_makedirs.assert_not_called()


@pytest.mark.parametrize("file_exists, automatic_update, user_input, expected_generate_calls, expected_update_calls", [
    (False, False, None, 1, 0),  # File doesn't exist
    (True, True, None, 1, 1),    # File exists, automatic update
    (True, False, 'o', 1, 0),    # File exists, user chooses to overwrite
    (True, False, 'u', 1, 1),    # File exists, user chooses to update
])
@patch('ara_cli.update_config_prompt.generate_config_prompt_template_file')
@patch('ara_cli.update_config_prompt.generate_config_prompt_givens_file')
@patch('ara_cli.update_config_prompt.update_config_prompt_files')
@patch('builtins.input', create=True)
@patch('os.path.exists')
def test_handle_existing_file(mock_exists, mock_input, mock_update_files, mock_generate_template, mock_generate_givens, 
                              file_exists, automatic_update, user_input, expected_generate_calls, expected_update_calls):
    file_path = "test_file_path"
    tmp_file_path = "test_tmp_file_path"

    # Configure the mock objects
    mock_exists.return_value = file_exists
    mock_input.return_value = user_input

    def generate_file_func(dir_path, file_name):
        pass

    generate_func_mock = MagicMock(side_effect=generate_file_func)

    handle_existing_file(file_path, tmp_file_path, generate_func_mock, automatic_update)

    assert generate_func_mock.call_count == expected_generate_calls
    assert mock_update_files.call_count == expected_update_calls

    if not file_exists:
        generate_func_mock.assert_called_with(os.path.dirname(file_path), os.path.basename(file_path))
    elif automatic_update:
        generate_func_mock.assert_called_with(os.path.dirname(file_path), os.path.basename(tmp_file_path))
        mock_update_files.assert_called_with(file_path, tmp_file_path)
    elif user_input == 'o':
        generate_func_mock.assert_called_with(os.path.dirname(file_path), os.path.basename(file_path))
    elif user_input == 'u':
        generate_func_mock.assert_called_with(os.path.dirname(file_path), os.path.basename(tmp_file_path))
        mock_update_files.assert_called_with(file_path, tmp_file_path)


@pytest.mark.parametrize("automatic_update", [True, False])
@patch("ara_cli.update_config_prompt.Classifier.get_sub_directory", return_value="sub_dir")
@patch("ara_cli.update_config_prompt.os.path.join", side_effect=lambda *args: "/".join(args))
@patch("ara_cli.update_config_prompt.ensure_directory_exists")
@patch("ara_cli.update_config_prompt.handle_existing_file")
@patch('ara_cli.update_config_prompt.generate_config_prompt_givens_file')
@patch('ara_cli.update_config_prompt.generate_config_prompt_template_file')
def test_update_artefact_config_prompt_files(mock_generate_template, mock_generate_givens, mock_handle_existing_file, mock_ensure_directory_exists, mock_os_path_join, mock_get_sub_directory, automatic_update):
    prompt_config_givens = "ara/sub_dir/test_param.data/prompt.data/config.prompt_givens.md"
    prompt_config_givens_tmp = "ara/sub_dir/test_param.data/prompt.data/config.prompt_givens_tmp.md"
    prompt_config_templates = "ara/sub_dir/test_param.data/prompt.data/config.prompt_templates.md"
    prompt_config_templates_tmp = "ara/sub_dir/test_param.data/prompt.data/config.prompt_templates_tmp.md"

    # Call the function
    update_artefact_config_prompt_files("test_classifier", "test_param", automatic_update)

    # Assert calls
    mock_get_sub_directory.assert_called_once_with("test_classifier")
    mock_os_path_join.assert_any_call("ara", "sub_dir", f"test_param.data")
    mock_os_path_join.assert_any_call("ara/sub_dir/test_param.data", "prompt.data")

    mock_ensure_directory_exists.assert_called_once_with("ara/sub_dir/test_param.data/prompt.data")

    mock_handle_existing_file.assert_any_call(prompt_config_givens, prompt_config_givens_tmp, mock_generate_givens, automatic_update)
    mock_handle_existing_file.assert_any_call(prompt_config_templates, prompt_config_templates_tmp, mock_generate_template, automatic_update)
