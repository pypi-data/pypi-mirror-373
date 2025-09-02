from unittest.mock import patch, mock_open
from ara_cli.artefact_link_updater import ArtefactLinkUpdater
import os


@patch("ara_cli.artefact_link_updater.os.listdir")
@patch("ara_cli.artefact_link_updater.os.path.isfile")
def test_update_links_in_related_artefacts(mock_isfile, mock_listdir):
    # Setup
    old_name = "Old_name"
    new_name = "New name"
    dir_path = "path/to/artefacts"
    file_contents = {
        "contributing_artefact.userstory": "Contributes to Old_name\nSome other content",
        "illustrating.example": "Illustrates Old_name\nSome other content"
    }

    # Mock the listdir to return a list of files
    mock_listdir.return_value = list(file_contents.keys())

    # Mock the isfile to return True, assuming all listdir entries are files
    mock_isfile.return_value = True

    # Mock the open function using mock_open
    mock_file_handles = {filename: mock_open(read_data=content).return_value
                         for filename, content in file_contents.items()}
    mock_open_function = mock_open()
    mock_open_function.side_effect = lambda file_path, mode='r', encoding='utf-8': mock_file_handles[os.path.basename(file_path)]

    with patch("builtins.open", mock_open_function):
        # Instantiate the ArtefactLinkUpdater with the mocked file system
        link_updater = ArtefactLinkUpdater(file_system=os)

        # Execute the method under test
        link_updater.update_links_in_related_artefacts(old_name, new_name, dir_path)

        # Assertions
        # Verify that the open function was called correctly for each file
        for filename in file_contents.keys():
            expected_file_path = os.path.join(dir_path, filename)
            mock_open_function.assert_any_call(expected_file_path, 'r', encoding='utf-8')
            mock_open_function.assert_any_call(expected_file_path, 'w', encoding='utf-8')

        # Verify the content of the files was updated correctly
        for filename, content in file_contents.items():
            expected_new_content = content.replace(old_name, new_name)
            file_object = mock_file_handles[filename]
            file_object.write.assert_called_with(expected_new_content)
