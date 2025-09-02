from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from ara_cli.artefact_creator import ArtefactCreator
import pytest


def test_template_exists_with_valid_path():
    mock_fs = Mock()
    mock_fs.path.join.return_value = "full_path"
    mock_fs.path.isfile.return_value = True

    fc = ArtefactCreator(mock_fs)
    result = fc.template_exists("template_path", "template_name")

    assert result


def test_run_with_invalid_classifier_raises_error(capfd):
    fc = ArtefactCreator()
    with pytest.raises(ValueError):
        fc.run("filename", "invalid_classifier")


@patch("ara_cli.artefact_creator.input", return_value="n")
@patch("ara_cli.artefact_creator.os.path.exists", return_value=True)
@patch("ara_cli.artefact_creator.os.listdir", return_value=["data_folder_content"])
def test_run_with_existing_file_does_not_overwrite(mock_input, mock_exists, mock_list, capfd):
    fc = ArtefactCreator()
    fc.run("filename", "vision")

    captured = capfd.readouterr()
    assert "No changes were made to the existing file and directory." in captured.out


def test_create_artefact_exploration_success():
    creator = ArtefactCreator()

    # Mock the Path's exists method to always return True
    with patch.object(Path, "exists", return_value=True):
        with patch("builtins.open", mock_open()), patch("shutil.copyfile"):
            creator.create_artefact_prompt_files("./dest", "./source", "sample")



def test_create_artefact_exploration_source_not_found():
    creator = ArtefactCreator()

    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            creator.create_artefact_prompt_files("./dest", "./source", "sample")


def test_create_artefact_exploration_dest_not_found():
    creator = ArtefactCreator()

    with patch.object(Path, "exists", lambda self: "source" in str(self)):
        with pytest.raises(NotADirectoryError):
            creator.create_artefact_prompt_files("./dest", "./source", "sample")
