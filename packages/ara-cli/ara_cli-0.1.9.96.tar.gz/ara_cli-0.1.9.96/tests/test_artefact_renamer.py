from unittest.mock import call, mock_open, patch, Mock
from ara_cli.artefact_renamer import ArtefactRenamer
from ara_cli.classifier import Classifier
import pytest
import os
import shutil


@pytest.fixture(autouse=True)
def cleanup():
    """
    A fixture to clean up the 'new_name.data' directory after each test case.
    """
    yield  # This is where the test runs
    new_data_dir = "ara/userstories/new_name.data"
    if os.path.exists(new_data_dir):
        shutil.rmtree(new_data_dir)


def test_rename_checks_classifier_valid():
    ar = ArtefactRenamer(os)
    with pytest.raises(ValueError):
        ar.rename("existing_file", "new_file", "invalid_classifier")


def test_rename_checks_new_name_provided():
    ar = ArtefactRenamer(os)
    with pytest.raises(ValueError):
        ar.rename("existing_file", None, None)


@pytest.mark.parametrize("classifier,artefact_name,read_data_prefix,old_title,new_title", [
    ("vision", "Vision", "Vision: ", "Old Title", "New title"),
    ("businessgoal", "Businessgoal", "Businessgoal: ", "Old Title", "New title"),
    ("capability", "Capability", "Capability: ", "Old Title", "New title"),
    ("keyfeature", "Keyfeature", "Keyfeature: ", "Old Title", "New title"),
    ("feature", "Feature", "Feature: ", "Old Title", "New title"),
    ("epic", "Epic", "Epic: ", "Old Title", "New title"),
    ("userstory", "Userstory", "Userstory: ", "Old Title", "New title"),
    ("task", "Task", "Task: ", "Old Title", "New title"),
    ("task", "Task list", "Task list: ", "Old Title", "New title"),
    ("example", "Example", "Example: ", "Old Title", "New title"),
])
@patch("builtins.open", new_callable=mock_open)
def test_update_title_in_artefact(mock_file, classifier, artefact_name, read_data_prefix, old_title, new_title):
    ar = ArtefactRenamer(os)
    read_data = f"{read_data_prefix}{old_title}\nOther content that remains unchanged."
    mock_file.return_value.read = Mock(return_value=read_data)
    artefact_path = f"path/to/{classifier}.artefact"

    # Ensure that the mock for get_artefact_title returns the prefix without an extra colon and space
    with patch.object(Classifier, 'get_artefact_title', return_value=artefact_name):
        ar._update_title_in_artefact(artefact_path, new_title, classifier)

    # Check that the file was opened for reading
    mock_file.assert_any_call(artefact_path, 'r', encoding='utf-8')
    # Check that the file was opened for writing
    mock_file.assert_any_call(artefact_path, 'w', encoding='utf-8')
    # Check that the file write was called with the correct new content
    expected_content = read_data.replace(f"{read_data_prefix}{old_title}", f"{read_data_prefix}{new_title}")
    mock_file().write.assert_called_with(expected_content)


@patch("builtins.open", new_callable=mock_open)
def test_update_title_invalid_classifier(mocker):
    ar = ArtefactRenamer()
    with pytest.raises(ValueError):
        ar._update_title_in_artefact("path", "title", "invalid_classifier")


@patch("builtins.open", new_callable=mock_open)
@patch("ara_cli.artefact_renamer.Classifier.get_artefact_title", return_value="Vision")
def test_update_title_no_title_line(mock_get_artefact_title, mock_file):
    ar = ArtefactRenamer()

    read_data = "content that remains unchanged."
    mock_file.return_value.read = Mock(return_value=read_data)
    artefact_path = "path/to/artefact.vision"

    with pytest.raises(ValueError):
        ar._update_title_in_artefact(artefact_path, "title", "vision")
