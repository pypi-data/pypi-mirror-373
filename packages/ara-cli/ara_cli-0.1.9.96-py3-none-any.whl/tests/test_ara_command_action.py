import pytest
from unittest.mock import patch, MagicMock, call, mock_open
from ara_cli.error_handler import AraValidationError
from ara_cli.ara_command_action import (
    check_validity,
    create_action,
    delete_action,
    rename_action,
    list_action,
    read_status_action,
    read_user_action,
    set_status_action,
    set_user_action,
    classifier_directory_action,
    scan_action,
    autofix_action
)


@pytest.fixture
def mock_handle_errors():
    with patch("ara_cli.ara_command_action.handle_errors", lambda context: (lambda f: f)):
        yield


@pytest.fixture
def mock_dependencies():
    with patch(
        "ara_cli.artefact_creator.ArtefactCreator"
    ) as MockArtefactCreator, patch(
        "ara_cli.classifier.Classifier"
    ) as MockClassifier, patch(
        "ara_cli.filename_validator.is_valid_filename"
    ) as mock_is_valid_filename, patch(
        "ara_cli.template_manager.SpecificationBreakdownAspects"
    ) as MockSpecificationBreakdownAspects, patch(
        "ara_cli.artefact_fuzzy_search.find_closest_rule"
    ) as mock_find_closest_rule, patch(
        "ara_cli.artefact_reader.ArtefactReader"
    ) as MockArtefactReader:
        yield MockArtefactCreator, MockClassifier, mock_is_valid_filename, MockSpecificationBreakdownAspects, mock_find_closest_rule, MockArtefactReader


@pytest.fixture
def mock_classifier_get_sub_directory():
    with patch("ara_cli.classifier.Classifier.get_sub_directory") as mock_get_sub_directory:
        yield mock_get_sub_directory


@pytest.fixture
def mock_artefact_deleter():
    with patch("ara_cli.artefact_deleter.ArtefactDeleter") as MockArtefactDeleter:
        yield MockArtefactDeleter


@pytest.fixture
def mock_artefact_renamer():
    with patch(
        "ara_cli.artefact_renamer.ArtefactRenamer"
    ) as MockArtefactRenamer, patch(
        "ara_cli.classifier.Classifier"
    ) as MockClassifier, patch(
        "ara_cli.filename_validator.is_valid_filename"
    ) as mock_is_valid_filename:
        yield MockArtefactRenamer, MockClassifier, mock_is_valid_filename


@pytest.fixture
def mock_artefact_reader():
    with patch("ara_cli.artefact_reader.ArtefactReader") as MockArtefactReader:
        yield MockArtefactReader


@pytest.fixture
def mock_artefact_lister():
    with patch("ara_cli.artefact_lister.ArtefactLister") as MockArtefactLister:
        yield MockArtefactLister


@pytest.fixture
def mock_list_filter():
    with patch("ara_cli.list_filter.ListFilter") as MockListFilter:
        yield MockListFilter


@pytest.fixture
def mock_directory_navigator():
    with patch(
        "ara_cli.directory_navigator.DirectoryNavigator"
    ) as MockDirectoryNavigator:
        yield MockDirectoryNavigator


@pytest.fixture
def mock_artefact():
    with patch("ara_cli.artefact.Artefact") as MockArtefact:
        yield MockArtefact


@pytest.fixture
def mock_file_classifier():
    with patch("ara_cli.file_classifier.FileClassifier") as MockFileClassifier:
        yield MockFileClassifier


@pytest.fixture
def mock_suggest_close_name_matches():
    with patch(
        "ara_cli.ara_command_action.suggest_close_name_matches"
    ) as mock_suggest_close_name_matches:
        yield mock_suggest_close_name_matches


def test_check_validity_with_true_condition():
    """Test that check_validity does nothing when condition is True."""
    # This should not raise any exception
    check_validity(True, "This should not be printed")


def test_check_validity_with_false_condition():
    """Test that check_validity raises AraValidationError when condition is False."""
    error_message = "This is a test error message"

    with pytest.raises(AraValidationError, match=error_message):
        check_validity(False, error_message)


def test_check_validity_error_message_content():
    """Test that the raised exception contains the correct error message."""
    error_message = "Custom validation error"

    with pytest.raises(AraValidationError) as exc_info:
        check_validity(False, error_message)

    assert str(exc_info.value) == error_message


def setup_create_args_and_mocks(classifier_valid, filename_valid, mock_dependencies):
    (MockArtefactCreator, MockClassifier, mock_is_valid_filename, _, _, MockArtefactReader) = mock_dependencies
    MockClassifier.is_valid_classifier.return_value = classifier_valid
    mock_is_valid_filename.return_value = filename_valid
    MockArtefactReader.read_artefact.return_value = (None, None)

    args = MagicMock()
    args.classifier = "test_classifier"
    args.parameter = "test_parameter"
    return args

# Test for valid classifier and filename
def test_create_action_with_valid_params(mock_handle_errors, mock_dependencies):
    args = setup_create_args_and_mocks(True, True, mock_dependencies)
    with patch("ara_cli.ara_command_action.check_validity") as mock_check_validity:
        create_action(args)
        mock_check_validity.assert_any_call(True, "Invalid classifier provided. Please provide a valid classifier.")
        mock_check_validity.assert_any_call(True, "Invalid filename provided. Please provide a valid filename.")

# Test for invalid classifier
def test_create_action_with_invalid_classifier(mock_handle_errors, mock_dependencies):
    args = setup_create_args_and_mocks(False, True, mock_dependencies)
    with patch("ara_cli.ara_command_action.check_validity") as mock_check_validity:
        create_action(args)
        mock_check_validity.assert_any_call(False, "Invalid classifier provided. Please provide a valid classifier.")

# Test for invalid filename
def test_create_action_with_invalid_filename(mock_handle_errors, mock_dependencies):
    args = setup_create_args_and_mocks(True, False, mock_dependencies)
    with patch("ara_cli.ara_command_action.check_validity") as mock_check_validity:
        create_action(args)
        mock_check_validity.assert_any_call(False, "Invalid filename provided. Please provide a valid filename.")

# Test for both invalid classifier and filename
def test_create_action_with_invalid_classifier_and_filename(mock_handle_errors, mock_dependencies):
    args = setup_create_args_and_mocks(False, False, mock_dependencies)
    with patch("ara_cli.ara_command_action.check_validity") as mock_check_validity:
        create_action(args)
        mock_check_validity.assert_any_call(False, "Invalid classifier provided. Please provide a valid classifier.")
        mock_check_validity.assert_any_call(False, "Invalid filename provided. Please provide a valid filename.")


@pytest.mark.parametrize(
    "parameter, classifier, force",
    [
        ("valid_param", "valid_classifier", True),
        ("valid_param", "valid_classifier", False),
    ],
)
def test_delete_action(mock_artefact_deleter, parameter, classifier, force):
    MockArtefactDeleter = mock_artefact_deleter
    instance = MockArtefactDeleter.return_value

    args = MagicMock()
    args.parameter = parameter
    args.classifier = classifier
    args.force = force

    delete_action(args)

    instance.delete.assert_called_once_with(parameter, classifier, force)


@pytest.mark.parametrize(
    "parameter_valid, classifier_valid, aspect_valid",
    [
        (True, True, True),
        (False, True, True),
        (True, False, True),
        (True, True, False),
        (False, False, False),
    ],
)
def test_rename_action_validity_checks(
    mock_artefact_renamer, parameter_valid, classifier_valid, aspect_valid
):
    MockArtefactRenamer, MockClassifier, mock_is_valid_filename = mock_artefact_renamer
    MockClassifier.is_valid_classifier.return_value = classifier_valid
    mock_is_valid_filename.side_effect = [parameter_valid, aspect_valid]

    args = MagicMock()
    args.parameter = "test_parameter"
    args.classifier = "test_classifier"
    args.aspect = "test_aspect"

    with patch("ara_cli.ara_command_action.check_validity") as mock_check_validity:
        if parameter_valid and classifier_valid and aspect_valid:
            rename_action(args)
            mock_check_validity.assert_any_call(
                True, "Invalid filename provided. Please provide a valid filename."
            )
            mock_check_validity.assert_any_call(
                True, "Invalid classifier provided. Please provide a valid classifier."
            )
            mock_check_validity.assert_any_call(
                True, "Invalid new filename provided. Please provide a valid filename."
            )
        else:
            rename_action(args)
            if not parameter_valid:
                mock_check_validity.assert_any_call(
                    False, "Invalid filename provided. Please provide a valid filename."
                )
            if not classifier_valid:
                mock_check_validity.assert_any_call(
                    False,
                    "Invalid classifier provided. Please provide a valid classifier.",
                )
            if not aspect_valid:
                mock_check_validity.assert_any_call(
                    False,
                    "Invalid new filename provided. Please provide a valid filename.",
                )


@pytest.mark.parametrize(
    "parameter, aspect, classifier",
    [
        ("valid_param", "new_valid_aspect", "valid_classifier"),
    ],
)
def test_rename_action_renamer_call(
    mock_artefact_renamer, parameter, aspect, classifier
):
    MockArtefactRenamer, MockClassifier, mock_is_valid_filename = mock_artefact_renamer
    MockClassifier.is_valid_classifier.return_value = True
    mock_is_valid_filename.return_value = True

    args = MagicMock()
    args.parameter = parameter
    args.classifier = classifier
    args.aspect = aspect

    rename_action(args)
    MockArtefactRenamer.return_value.rename.assert_called_once_with(
        parameter, aspect, classifier
    )


@pytest.mark.parametrize(
    "branch_args, children_args, data_args, expected_call",
    [
        (
            ("branch_classifier", "branch_name"),
            (None, None),
            (None, None),
            "list_branch",
        ),
        (
            (None, None),
            ("children_classifier", "children_name"),
            (None, None),
            "list_children",
        ),
        ((None, None), (None, None), ("data_classifier", "data_name"), "list_data"),
    ],
)
def test_list_action_calls_correct_method(
    mock_artefact_lister,
    mock_list_filter,
    branch_args,
    children_args,
    data_args,
    expected_call,
):
    MockArtefactLister = mock_artefact_lister
    list_filter_instance = mock_list_filter.return_value

    args = MagicMock()
    args.branch_args = branch_args
    args.children_args = children_args
    args.data_args = data_args
    args.include_content = None
    args.exclude_content = None
    args.include_extension = None
    args.exclude_extension = None

    list_action(args)
    instance = MockArtefactLister.return_value
    getattr(instance, expected_call).assert_called_once_with(
        classifier=branch_args[0] or children_args[0] or data_args[0],
        artefact_name=branch_args[1] or children_args[1] or data_args[1],
        list_filter=list_filter_instance,
    )


@pytest.mark.parametrize(
    "include_content, exclude_content, include_extension, exclude_extension, include_tags, exclude_tags",
    [
        ("text", None, ".txt", None, None, None),
        (None, "text", None, ".txt", None, None),
        ("text", "text", ".txt", ".md", None, None),
        ("text", None, ".txt", None, "a_tag", None),
        (None, "text", None, ".txt", None, "taggo"),
    ],
)
def test_list_action_creates_list_filter(
    mock_artefact_lister,
    mock_list_filter,
    include_content,
    exclude_content,
    include_extension,
    exclude_extension,
    include_tags,
    exclude_tags,
):
    mock_list_filter.return_value = MagicMock()

    args = MagicMock()
    args.branch_args = (None, None)
    args.children_args = (None, None)
    args.data_args = (None, None)
    args.include_content = include_content
    args.exclude_content = exclude_content
    args.include_extension = include_extension
    args.exclude_extension = exclude_extension
    args.include_tags = include_tags
    args.exclude_tags = exclude_tags

    list_action(args)
    mock_list_filter.assert_called_once_with(
        include_content=include_content,
        exclude_content=exclude_content,
        include_extension=include_extension,
        exclude_extension=exclude_extension,
        include_tags=include_tags,
        exclude_tags=exclude_tags,
    )


@pytest.mark.parametrize(
    "classifier, artefact_name, artefact_exists, status, expected_output",
    [
        # Case when artefact_name is not found in artefact_names
        ("test_classifier", "non_existent_artefact", False, None, None),
        
        # Case when artefact_name is found but no status is available
        ("test_classifier", "artefact1", True, None, "No status found"),
        
        # Case when artefact_name is found and status is available
        ("test_classifier", "artefact2", True, "Active", "Active"),
    ]
)
def test_read_status_action(classifier, artefact_name, artefact_exists, status, expected_output):
    args = MagicMock()
    args.classifier = classifier
    args.parameter = artefact_name

    mock_artefact = MagicMock()
    mock_artefact.status = status

    # Create mock artefact info
    artefact_info_dicts = []
    if artefact_exists:
        artefact_info_dicts.append({
            "title": artefact_name,
            "file_path": f"/path/to/{artefact_name}.md"
        })
    
    all_artefact_names = [info["title"] for info in artefact_info_dicts]

    with patch('ara_cli.file_classifier.FileClassifier') as MockFileClassifier, \
         patch('ara_cli.artefact_models.artefact_load.artefact_from_content') as mock_artefact_from_content, \
         patch('ara_cli.ara_command_action.suggest_close_name_matches') as mock_suggest_close_name_matches, \
         patch('builtins.open', new_callable=MagicMock()) as mock_open, \
         patch('builtins.print') as mock_print:

        # Configure file classifier mock
        mock_classifier_instance = MockFileClassifier.return_value
        mock_classifier_instance.classify_files.return_value = {classifier: artefact_info_dicts}
        
        # Configure file open mock
        mock_file_handle = MagicMock()
        mock_file_handle.__enter__.return_value.read.return_value = "mock file content"
        mock_open.return_value = mock_file_handle
        
        # Configure artefact mock
        mock_artefact_from_content.return_value = mock_artefact

        # Call the function
        read_status_action(args)

        # Verify behavior
        if not artefact_exists:
            # Should suggest close matches when artefact not found
            mock_suggest_close_name_matches.assert_called_once_with(artefact_name, all_artefact_names, report_as_error=True)
            mock_open.assert_not_called()
        else:
            # Should open the file and read content
            mock_open.assert_called_once()
            mock_artefact_from_content.assert_called_once_with("mock file content")
            
            if status:
                mock_print.assert_called_once_with(status)
            else:
                mock_print.assert_called_once_with("No status found")


def read_user_action(args):
    from ara_cli.artefact_models.artefact_load import artefact_from_content
    from ara_cli.file_classifier import FileClassifier

    classifier = args.classifier
    artefact_name = args.parameter

    file_classifier = FileClassifier(os)
    artefact_info = file_classifier.classify_files()
    artefact_info_dicts = artefact_info.get(classifier, [])

    all_artefact_names = [artefact_info["title"] for artefact_info in artefact_info_dicts]
    if artefact_name not in all_artefact_names:
        suggest_close_name_matches(artefact_name, all_artefact_names)
        return

    artefact_info = next(filter(
        lambda x: x["title"] == artefact_name, artefact_info_dicts
    ))

    with open(artefact_info["file_path"], 'r', encoding='utf-8') as file:
        content = file.read()
    artefact = artefact_from_content(content)

    user_tags = artefact.users

    if not user_tags:
        print("No user found")
        return
    for tag in user_tags:
        print(f" - {tag}")


@pytest.mark.parametrize(
    "classifier, artefact_name, artefact_names, new_status, status_tags, content, expected_output, should_suggest",
    [
        # Case when artefact_name is not found in artefact_names
        ("test_classifier", "non_existent_artefact", ["artefact1", "artefact2"], "to-do", ["to-do", "review", "done"], None, None, True),

        # Case when new_status is invalid
        ("test_classifier", "artefact1", ["artefact1", "artefact2"], "invalid_status", ["to-do", "review", "done"], "some_content", None, False),

        # Case when artefact_name is found and status is successfully changed
        ("test_classifier", "artefact1", ["artefact1", "artefact2"], "review", ["to-do", "review", "done"], "some_content", 
         "Status of task 'artefact1' has been updated to 'review'.", False),
        
        # Case when new_status has a leading '@'
        ("test_classifier", "artefact1", ["artefact1", "artefact2"], "@done", ["to-do", "review", "done"], "some_content", 
         "Status of task 'artefact1' has been updated to 'done'.", False),
    ]
)
def test_set_status_action(classifier, artefact_name, artefact_names, new_status, status_tags, content, expected_output, should_suggest):
    args = MagicMock()
    args.classifier = classifier
    args.parameter = artefact_name
    args.new_status = new_status

    # Create artefact info dictionaries for each artefact name
    artefact_info_dicts = [
        {"title": name, "file_path": f"/path/to/{name}.md"} 
        for name in artefact_names
    ]

    mock_artefact = MagicMock()
    mock_artefact.serialize.return_value = "serialized_content"

    with patch('ara_cli.artefact_models.artefact_model.ALLOWED_STATUS_VALUES', status_tags), \
         patch('ara_cli.file_classifier.FileClassifier') as MockFileClassifier, \
         patch('ara_cli.artefact_models.artefact_load.artefact_from_content') as mock_artefact_from_content, \
         patch('ara_cli.ara_command_action.suggest_close_name_matches') as mock_suggest_close_name_matches, \
         patch('builtins.open', new_callable=MagicMock) as mock_open, \
         patch('ara_cli.ara_command_action.check_validity') as mock_check_validity:

        # Configure mock file classifier
        mock_classifier_instance = MockFileClassifier.return_value
        mock_classifier_instance.classify_files.return_value = {classifier: artefact_info_dicts}
        
        # Configure mock file handling
        mock_file_handle = MagicMock()
        mock_file_handle.__enter__.return_value.read.return_value = content
        mock_open.return_value = mock_file_handle
        
        # Configure artefact loading
        mock_artefact_from_content.return_value = mock_artefact

        # Run the function under test
        if expected_output:
            with patch('builtins.print') as mock_print:
                set_status_action(args)
                
                # Verify the status was set on the artefact
                assert mock_artefact.status == new_status.lstrip('@') if new_status.startswith('@') else new_status
                
                # Verify the file was opened for reading and writing
                expected_file_path = next(info["file_path"] for info in artefact_info_dicts if info["title"] == artefact_name)
                mock_open.assert_any_call(expected_file_path, 'r', encoding='utf-8')
                mock_open.assert_any_call(expected_file_path, 'w', encoding='utf-8')
                
                # Verify the serialized content was written
                mock_file_handle.__enter__.return_value.write.assert_called_once_with("serialized_content")
                
                # Verify the success message was printed
                mock_print.assert_called_once_with(expected_output)
        else:
            set_status_action(args)
            if should_suggest:
                # Should suggest close matches when artefact not found
                mock_suggest_close_name_matches.assert_called_once_with(artefact_name, artefact_names)
                mock_artefact_from_content.assert_not_called()
            else:
                # Should validate the status
                mock_check_validity.assert_called_once_with(
                    new_status.lstrip('@') if new_status.startswith('@') else new_status in status_tags, 
                    "Invalid status provided. Please provide a valid status."
                )


@pytest.mark.parametrize(
    "classifier, artefact_name, artefact_names, new_user, expected_output",
    [
        # Normal case
        ("test_classifier", "valid_artefact", ["valid_artefact"], "john_doe", "User of task 'valid_artefact' has been updated to 'john_doe'."),
        # Case with @ prefix in user name
        ("test_classifier", "valid_artefact", ["valid_artefact"], "@john_doe", "User of task 'valid_artefact' has been updated to 'john_doe'."),
        # Case where artefact is not found
        ("test_classifier", "invalid_artefact", ["valid_artefact"], "john_doe", None),
    ],
)
def test_set_user_action(
    classifier, artefact_name, artefact_names, new_user, expected_output
):
    args = MagicMock()
    args.classifier = classifier
    args.parameter = artefact_name
    args.new_user = new_user

    # Create artefact info dictionaries for each artefact name
    artefact_info_dicts = [
        {"title": name, "file_path": f"/path/to/{name}.md"} 
        for name in artefact_names
    ]
    
    mock_artefact = MagicMock()
    mock_artefact.serialize.return_value = "serialized_content"
    
    mock_file_content = "mock file content"

    with patch('ara_cli.file_classifier.FileClassifier') as MockFileClassifier, \
         patch('ara_cli.artefact_models.artefact_load.artefact_from_content') as mock_artefact_from_content, \
         patch('ara_cli.ara_command_action.suggest_close_name_matches') as mock_suggest_close_name_matches, \
         patch('builtins.open', new_callable=MagicMock()) as mock_open, \
         patch('builtins.print') as mock_print:
        
        # Configure mocks
        mock_file_classifier_instance = MockFileClassifier.return_value
        mock_file_classifier_instance.classify_files.return_value = {classifier: artefact_info_dicts}
        
        mock_file_handle = MagicMock()
        mock_file_handle.__enter__.return_value.read.return_value = mock_file_content
        mock_open.return_value = mock_file_handle
        
        mock_artefact_from_content.return_value = mock_artefact

        # Call the function
        set_user_action(args)

        # Verify behavior
        if artefact_name not in artefact_names:
            # Should suggest close matches when artefact not found
            mock_suggest_close_name_matches.assert_called_once_with(artefact_name, artefact_names)
            mock_artefact_from_content.assert_not_called()
        else:
            # Should open the file and read content
            expected_file_path = next(info["file_path"] for info in artefact_info_dicts if info["title"] == artefact_name)
            mock_open.assert_any_call(expected_file_path, 'r', encoding='utf-8')
            mock_artefact_from_content.assert_called_once_with(mock_file_content)
            
            # Should set the users attribute on the artefact
            assert mock_artefact.users == [new_user.lstrip('@') if new_user.startswith('@') else new_user]
            
            # Should write the serialized content back to the file
            mock_open.assert_any_call(expected_file_path, 'w', encoding='utf-8')
            mock_file_handle.__enter__.return_value.write.assert_called_once_with("serialized_content")
            
            # Should print a success message
            mock_print.assert_called_once_with(expected_output)


@pytest.mark.parametrize(
    "classifier, expected_subdirectory",
    [
        ("test_classifier", "test_subdirectory"),
        ("another_classifier", "another_subdirectory"),
    ],
)
def test_classifier_directory_action(mock_classifier_get_sub_directory, classifier, expected_subdirectory):
    mock_classifier_get_sub_directory.return_value = expected_subdirectory

    args = MagicMock()
    args.classifier = classifier

    with patch("builtins.print") as mock_print:
        classifier_directory_action(args)
        mock_classifier_get_sub_directory.assert_called_once_with(classifier)
        mock_print.assert_called_once_with(expected_subdirectory)


def test_scan_action_with_issues(capsys):
    args = MagicMock()
    with patch("ara_cli.file_classifier.FileClassifier") as MockFileClassifier, \
            patch("ara_cli.artefact_scan.find_invalid_files") as mock_find_invalid_files, \
            patch("builtins.open", mock_open()) as m:

        mock_classifier = MockFileClassifier.return_value
        mock_classifier.classify_files.return_value = {
            "classifier1": ["file1.txt"],
            "classifier2": ["file2.txt"]
        }

        def find_invalid_side_effect(artefact_files, classifier):
            if classifier == "classifier1":
                return [("file1.txt", "reason1")]
            elif classifier == "classifier2":
                return []

        mock_find_invalid_files.side_effect = find_invalid_side_effect

        scan_action(args)

        captured = capsys.readouterr()
        expected_output = (
            "\nIncompatible classifier1 Files:\n"
            "\t- file1.txt\n"
            "\t\treason1\n"
        )
        assert captured.out == expected_output
        m.assert_called_once_with("incompatible_artefacts_report.md", "w", encoding="utf-8")
        handle = m()
        expected_writes = [
            call("# Artefact Check Report\n\n"),
            call("## classifier1\n"),
            call("- `file1.txt`: reason1\n"),
            call("\n")
        ]
        handle.write.assert_has_calls(expected_writes, any_order=False)


def test_scan_action_all_good(capsys):
    args = MagicMock()
    with patch("ara_cli.file_classifier.FileClassifier") as MockFileClassifier, \
         patch("ara_cli.artefact_scan.find_invalid_files") as mock_find_invalid_files, \
         patch("builtins.open", mock_open()) as m:

        mock_classifier = MockFileClassifier.return_value
        mock_classifier.classify_files.return_value = {
            "classifier1": ["file1.txt"],
            "classifier2": ["file2.txt"]
        }

        mock_find_invalid_files.return_value = []

        scan_action(args)

        captured = capsys.readouterr()
        assert captured.out == "All files are good!\n"
        m.assert_called_once_with("incompatible_artefacts_report.md", "w", encoding="utf-8")
        handle = m()
        handle.write.assert_has_calls([
            call("# Artefact Check Report\n\n"),
            call("No problems found.\n")
        ], any_order=False)
