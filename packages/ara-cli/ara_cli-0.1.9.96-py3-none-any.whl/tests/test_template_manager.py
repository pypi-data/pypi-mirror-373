from unittest.mock import patch, MagicMock
from ara_cli.template_manager import SpecificationBreakdownAspects, ArtefactFileManager
from ara_cli.directory_navigator import DirectoryNavigator

import pytest
import os



@pytest.fixture(autouse=True)
def navigate_to_ara_directory():
    with patch('builtins.input', return_value='y'):
        navigator = DirectoryNavigator("ara")
        original_directory = navigator.navigate_to_target()
        yield
        os.chdir(original_directory)


@pytest.mark.parametrize(
    "file_exists, dir_exists, expected_mkdir_calls, expected_chdir_calls",
    [
        (True, True, 0, 1),
        (True, False, 1, 1),
        (False, False, 0, 0)
    ]
)
def test_create_directory(file_exists, dir_exists, expected_mkdir_calls, expected_chdir_calls):
    artefact_file = 'test_artefact'
    data_dir = 'test_artefact.data'
    sba = ArtefactFileManager()

    with patch('os.path.isfile', return_value=file_exists), \
         patch('os.path.exists', return_value=dir_exists), \
         patch('os.mkdir') as mock_mkdir, \
         patch('os.chdir') as mock_chdir:

        if not file_exists:
            with pytest.raises(ValueError, match=f"File {artefact_file} does not exist. Please create it first."):
                sba.create_directory(artefact_file, data_dir)
        else:
            sba.create_directory(artefact_file, data_dir)

        assert mock_mkdir.call_count == expected_mkdir_calls
        assert mock_chdir.call_count == expected_chdir_calls


@pytest.mark.parametrize(
    "aspect, expect_exception, match_str",
    [
        ("technology", False, None),
        ("", True, f"Template file .* does not exist."),
        ("invalid", True, f"Template file .* does not exist.")
    ]
)
def test_copy_templates_to_directory(aspect, expect_exception, match_str):
    sba = ArtefactFileManager()

    if expect_exception:
        with pytest.raises(FileNotFoundError, match=match_str):
            sba.copy_aspect_templates_to_directory(aspect)
    else:
        with patch("ara_cli.template_manager.copy") as mock_copy:
            with patch('builtins.print') as mock_print:
                sba.copy_aspect_templates_to_directory(aspect)
                mock_copy.assert_called()
                mock_print.assert_called()

@pytest.fixture
def mock_file_manager():
    with patch("ara_cli.template_manager.ArtefactFileManager") as MockFileManager:
        yield MockFileManager.return_value

@pytest.fixture
def mock_navigator():
    with patch("ara_cli.template_manager.DirectoryNavigator") as MockNavigator:
        mock_nav_instance = MockNavigator.return_value
        yield mock_nav_instance

@pytest.fixture
def mock_classifier():
    with patch("ara_cli.template_manager.Classifier") as MockClassifier:
        MockClassifier.valid_classifiers = ['valid_classifier']
        MockClassifier.is_valid_classifier.return_value = True
        yield MockClassifier


def test_create_valid_step_aspect(mock_file_manager, mock_navigator, mock_classifier):
    sba = SpecificationBreakdownAspects()

    # Mock values returned by file_manager methods
    mock_file_manager.get_artefact_file_path.return_value = "/tmp/path/file"
    mock_file_manager.get_data_directory_path.return_value = "/tmp/path/data"
    mock_file_manager.generate_behave_steps.return_value = ["step 1", "step 2"]

    # Run the function
    sba.create(artefact_name="my_artefact", classifier="valid_classifier", aspect="step")

    # Assert navigator was used
    mock_navigator.navigate_to_target.assert_called_once()

    # Assert file_manager method calls
    mock_file_manager.get_artefact_file_path.assert_called_once_with("my_artefact", "valid_classifier")
    mock_file_manager.get_data_directory_path.assert_called_once_with("my_artefact", "valid_classifier")
    mock_file_manager.create_directory.assert_called_once_with("/tmp/path/file", "/tmp/path/data")
    mock_file_manager.copy_aspect_templates_to_directory.assert_called_once()
    mock_file_manager.generate_behave_steps.assert_called_once_with("my_artefact")
    mock_file_manager.save_behave_steps_to_file.assert_called_once_with("my_artefact", ["step 1", "step 2"])
