import pytest
from unittest.mock import MagicMock, patch
from ara_cli.artefact_lister import ArtefactLister
from ara_cli.list_filter import ListFilter
from ara_cli.artefact_models.artefact_data_retrieval import (
    artefact_content_retrieval,
    artefact_path_retrieval,
    artefact_tags_retrieval,
)


@pytest.fixture
def artefact_lister():
    return ArtefactLister()


@pytest.mark.parametrize(
    "classified_files, list_filter, filter_result",
    [
        # Case 1: No filter applied
        (
            {"type1": [MagicMock(), MagicMock()]},
            None,
            {"type1": [MagicMock(), MagicMock()]},
        ),
        # Case 2: Filter with include tags
        (
            {"type1": [MagicMock(), MagicMock()]},
            ListFilter(include_tags=["tag1"]),
            {"type1": [MagicMock()]},
        ),
        # Case 3: Filter with exclude tags
        (
            {"type1": [MagicMock(), MagicMock()], "type2": [MagicMock()]},
            ListFilter(exclude_tags=["tag2"]),
            {"type1": [MagicMock()], "type2": []},
        ),
        # Case 4: Empty result after filtering
        (
            {"type1": [MagicMock(), MagicMock()]},
            ListFilter(include_tags=["nonexistent"]),
            {"type1": []},
        ),
        # Case 5: Multiple artefact types
        (
            {"type1": [MagicMock()], "type2": [MagicMock(), MagicMock()]},
            ListFilter(exclude_extension=[".txt"]),
            {"type1": [], "type2": [MagicMock()]},
        ),
    ],
)
def test_filter_artefacts(
    artefact_lister, classified_files, list_filter, filter_result
):
    # Mock the filter_list function
    with patch("ara_cli.artefact_lister.filter_list") as mock_filter_list:
        mock_filter_list.return_value = filter_result

        # Call the method under test
        result = artefact_lister.filter_artefacts(classified_files, list_filter)

        # Verify filter_list was called with correct parameters
        mock_filter_list.assert_called_once_with(
            list_to_filter=classified_files,
            list_filter=list_filter,
            content_retrieval_strategy=artefact_content_retrieval,
            file_path_retrieval=artefact_path_retrieval,
            tag_retrieval=artefact_tags_retrieval,
        )

        # Verify the structure matches (don't compare the actual MagicMock objects)
        assert set(result.keys()) == set(filter_result.keys())
        for key in filter_result:
            assert len(result[key]) == len(filter_result[key])


@pytest.mark.parametrize(
    "tags, navigate_to_target, list_filter, mock_artefacts, filtered_artefacts, expected_filtered",
    [
        # Test with no filter
        (
            None,
            False,
            None,
            {"type1": [MagicMock(), MagicMock()]},
            {"type1": [MagicMock(), MagicMock()]},
            {"type1": [MagicMock(), MagicMock()]},
        ),
        # Test with filter applied
        (
            ["tag1"],
            False,
            ListFilter(include_tags=["tag1"]),
            {"type1": [MagicMock(), MagicMock()]},
            {"type1": [MagicMock()]},
            {"type1": [MagicMock()]},
        ),
        # Test with None values in artefact list
        (
            None,
            False,
            None,
            {"type1": [MagicMock(), None, MagicMock()]},
            {"type1": [MagicMock(), None, MagicMock()]},
            {"type1": [MagicMock(), MagicMock()]},
        ),
        # Test with empty filtered results
        (
            ["tag1"],
            False,
            ListFilter(include_tags=["nonexistent"]),
            {"type1": [MagicMock(), MagicMock()]},
            {"type1": []},
            {"type1": []},
        ),
        # Test with multiple artefact types
        (
            None,
            True,
            ListFilter(exclude_extension=[".txt"]),
            {"type1": [MagicMock()], "type2": [MagicMock(), MagicMock()]},
            {"type1": [], "type2": [MagicMock()]},
            {"type1": [], "type2": [MagicMock()]},
        ),
    ],
)
def test_list_files(
    artefact_lister,
    tags,
    navigate_to_target,
    list_filter,
    mock_artefacts,
    filtered_artefacts,
    expected_filtered,
):
    # Mock ArtefactReader.read_artefacts
    with patch("ara_cli.artefact_lister.ArtefactReader") as mock_reader:
        mock_reader.read_artefacts.return_value = mock_artefacts

        # Mock filter_artefacts method
        artefact_lister.filter_artefacts = MagicMock(return_value=filtered_artefacts)

        # Mock FileClassifier
        with patch("ara_cli.artefact_lister.FileClassifier") as mock_file_classifier:
            mock_classifier_instance = MagicMock()
            mock_file_classifier.return_value = mock_classifier_instance

            # Call the method under test
            artefact_lister.list_files(
                tags=tags,
                navigate_to_target=navigate_to_target,
                list_filter=list_filter,
            )

            # Verify the correct calls were made
            mock_reader.read_artefacts.assert_called_once_with(tags=tags)
            artefact_lister.filter_artefacts.assert_called_once_with(
                mock_artefacts, list_filter
            )

            # Check that the correct filtered list is passed to print_classified_files
            # We need to check structure rather than exact equality because MagicMock instances are different
            call_arg = mock_classifier_instance.print_classified_files.call_args[0][0]

            # Verify structure matches expected filtered artefacts
            assert set(call_arg.keys()) == set(expected_filtered.keys())
            for key in expected_filtered:
                assert len(call_arg[key]) == len(expected_filtered[key])

            # Verify FileClassifier was initialized with the correct file system
            mock_file_classifier.assert_called_once_with(artefact_lister.file_system)


@pytest.mark.parametrize(
    "classifier, artefact_name, list_filter, classified_artefacts, artefact_info, matching_artefacts, child_artefacts, filtered_artefacts",
    [
        # Case 1: Artefact found, with children, no filter
        (
            "epic",
            "Epic1",
            None,
            {"epic": [{"title": "Epic1"}, {"title": "Epic2"}]},
            [{"title": "Epic1"}, {"title": "Epic2"}],
            [{"title": "Epic1"}],
            {"userstory": ["Story1", "Story2"]},
            {"userstory": ["Story1", "Story2"]},
        ),
        # Case 2: Artefact found, with children, with filter
        (
            "epic",
            "Epic1",
            ListFilter(include_tags=["tag1"]),
            {"epic": [{"title": "Epic1"}, {"title": "Epic2"}]},
            [{"title": "Epic1"}, {"title": "Epic2"}],
            [{"title": "Epic1"}],
            {"userstory": ["Story1", "Story2"]},
            {"userstory": ["Story1"]},  # Filtered result
        ),
        # Case 3: Artefact not found
        (
            "epic",
            "NonExistentEpic",
            None,
            {"epic": [{"title": "Epic1"}, {"title": "Epic2"}]},
            [{"title": "Epic1"}, {"title": "Epic2"}],
            [],
            {},
            {},
        ),
    ],
)
def test_list_children(
    artefact_lister,
    classifier,
    artefact_name,
    list_filter,
    classified_artefacts,
    artefact_info,
    matching_artefacts,
    child_artefacts,
    filtered_artefacts,
):
    # Setup mocks
    with patch("ara_cli.artefact_lister.FileClassifier") as mock_file_classifier, patch(
        "ara_cli.artefact_lister.suggest_close_name_matches"
    ) as mock_suggest, patch(
        "ara_cli.artefact_lister.ArtefactReader"
    ) as mock_artefact_reader:

        # Configure mock FileClassifier
        mock_classifier_instance = MagicMock()
        mock_file_classifier.return_value = mock_classifier_instance
        mock_classifier_instance.classify_files.return_value = classified_artefacts

        # Configure ArtefactReader mock
        mock_artefact_reader.find_children.return_value = child_artefacts

        # Mock filter_artefacts method
        artefact_lister.filter_artefacts = MagicMock(return_value=filtered_artefacts)

        # Call the method under test
        artefact_lister.list_children(classifier, artefact_name, list_filter)

        # Verify interactions
        mock_classifier_instance.classify_files.assert_called_once()

        # Check if suggestions were made for non-existent artefacts
        if not matching_artefacts:
            mock_suggest.assert_called_once_with(
                artefact_name, [info["title"] for info in artefact_info]
            )
        else:
            mock_suggest.assert_not_called()

        # Verify ArtefactReader.find_children was called
        mock_artefact_reader.find_children.assert_called_once_with(
            artefact_name=artefact_name, classifier=classifier
        )

        # Verify filter_artefacts was called with correct parameters
        artefact_lister.filter_artefacts.assert_called_once_with(
            child_artefacts, list_filter
        )

        # Verify print_classified_files was called with filtered results
        mock_classifier_instance.print_classified_files.assert_called_once_with(
            filtered_artefacts
        )


@pytest.mark.parametrize(
    "classifier, artefact_name, list_filter, classified_artefacts, artefact_info, matching_artefacts, value_chain_artefacts, filtered_artefacts",
    [
        # Case 1: Artefact found, with value chain, no filter
        (
            "epic",
            "Epic1",
            None,
            {"epic": [{"title": "Epic1"}, {"title": "Epic2"}]},
            [{"title": "Epic1"}, {"title": "Epic2"}],
            [{"title": "Epic1"}],
            {"epic": ["Epic1"], "userstory": ["Story1", "Story2"]},
            {"epic": ["Epic1"], "userstory": ["Story1", "Story2"]},
        ),
        # Case 2: Artefact found, with value chain, with filter
        (
            "epic",
            "Epic1",
            ListFilter(include_tags=["tag1"]),
            {"epic": [{"title": "Epic1"}, {"title": "Epic2"}]},
            [{"title": "Epic1"}, {"title": "Epic2"}],
            [{"title": "Epic1"}],
            {"epic": ["Epic1"], "userstory": ["Story1", "Story2"]},
            {"epic": ["Epic1"], "userstory": ["Story1"]},  # Filtered result
        ),
        # Case 3: Artefact not found
        (
            "epic",
            "NonExistentEpic",
            None,
            {"epic": [{"title": "Epic1"}, {"title": "Epic2"}]},
            [{"title": "Epic1"}, {"title": "Epic2"}],
            [],
            {"epic": []},
            {"epic": []},
        ),
        # Case 4: Empty artefact list
        (
            "epic",
            "Epic1",
            None,
            {"epic": []},
            [],
            [],
            {"epic": []},
            {"epic": []},
        ),
    ],
)
def test_list_branch(
    artefact_lister,
    classifier,
    artefact_name,
    list_filter,
    classified_artefacts,
    artefact_info,
    matching_artefacts,
    value_chain_artefacts,
    filtered_artefacts,
):
    # Setup mocks
    with patch("ara_cli.artefact_lister.FileClassifier") as mock_file_classifier, patch(
        "ara_cli.artefact_lister.suggest_close_name_matches"
    ) as mock_suggest, patch(
        "ara_cli.artefact_lister.ArtefactReader"
    ) as mock_artefact_reader, patch(
        "ara_cli.artefact_lister.os"
    ) as mock_os:

        # Configure mock FileClassifier
        mock_classifier_instance = MagicMock()
        mock_file_classifier.return_value = mock_classifier_instance
        mock_classifier_instance.classify_files.return_value = classified_artefacts

        # Mock step_through_value_chain to modify the provided dictionary
        def mock_step_through(artefact_name, classifier, artefacts_by_classifier):
            # Replace the artefacts_by_classifier with our test data
            for k, v in value_chain_artefacts.items():
                artefacts_by_classifier[k] = v

        mock_artefact_reader.step_through_value_chain.side_effect = mock_step_through

        # Mock filter_artefacts method
        artefact_lister.filter_artefacts = MagicMock(return_value=filtered_artefacts)

        # Call the method under test
        artefact_lister.list_branch(classifier, artefact_name, list_filter)

        # Verify interactions
        mock_file_classifier.assert_called_once_with(mock_os)
        mock_classifier_instance.classify_files.assert_called_once()

        # Check if suggestions were made for non-existent artefacts
        if not matching_artefacts:
            mock_suggest.assert_called_once_with(
                artefact_name, [info["title"] for info in artefact_info]
            )
        else:
            mock_suggest.assert_not_called()

        # Verify ArtefactReader.step_through_value_chain was called with correct parameters
        mock_artefact_reader.step_through_value_chain.assert_called_once()
        call_args = mock_artefact_reader.step_through_value_chain.call_args[1]
        assert call_args["artefact_name"] == artefact_name
        assert call_args["classifier"] == classifier
        assert classifier in call_args["artefacts_by_classifier"]

        # Verify filter_artefacts was called with correct parameters
        # The exact contents will have been modified by the mock_step_through function
        artefact_lister.filter_artefacts.assert_called_once()
        filter_args = artefact_lister.filter_artefacts.call_args[0]
        assert filter_args[1] == list_filter

        # Verify print_classified_files was called with filtered results
        mock_classifier_instance.print_classified_files.assert_called_once_with(
            filtered_artefacts
        )


def test_list_data_artefact_found_data_exists(artefact_lister):
    classifier = "epic"
    artefact_name = "Epic1"
    list_filter = None
    classified_artefacts = {
        "epic": [
            {"title": "Epic1", "file_path": "path/to/Epic1.epic"},
            {"title": "Epic2", "file_path": "path/to/Epic2.epic"},
        ]
    }

    with patch("ara_cli.artefact_lister.FileClassifier") as mock_file_classifier, patch(
        "ara_cli.artefact_lister.suggest_close_name_matches"
    ) as mock_suggest, patch("ara_cli.artefact_lister.os") as mock_os, patch(
        "ara_cli.artefact_lister.list_files_in_directory"
    ) as mock_list_files:

        # Configure mocks
        mock_classifier_instance = MagicMock()
        mock_file_classifier.return_value = mock_classifier_instance
        mock_classifier_instance.classify_files.return_value = classified_artefacts

        mock_os.path.splitext.return_value = ("path/to/Epic1", ".epic")
        mock_os.path.exists.return_value = True

        # Call the method under test
        artefact_lister.list_data(classifier, artefact_name, list_filter)

        # Verify interactions
        mock_suggest.assert_not_called()
        mock_os.path.splitext.assert_called_with("path/to/Epic1.epic")
        mock_os.path.exists.assert_called_with("path/to/Epic1.data")
        mock_list_files.assert_called_once_with("path/to/Epic1.data", list_filter)


def test_list_data_artefact_found_data_not_exists(artefact_lister):
    classifier = "epic"
    artefact_name = "Epic1"
    list_filter = None
    classified_artefacts = {
        "epic": [
            {"title": "Epic1", "file_path": "path/to/Epic1.epic"},
            {"title": "Epic2", "file_path": "path/to/Epic2.epic"},
        ]
    }

    with patch("ara_cli.artefact_lister.FileClassifier") as mock_file_classifier, patch(
        "ara_cli.artefact_lister.suggest_close_name_matches"
    ) as mock_suggest, patch("ara_cli.artefact_lister.os") as mock_os, patch(
        "ara_cli.artefact_lister.list_files_in_directory"
    ) as mock_list_files:

        # Configure mocks
        mock_classifier_instance = MagicMock()
        mock_file_classifier.return_value = mock_classifier_instance
        mock_classifier_instance.classify_files.return_value = classified_artefacts

        mock_os.path.splitext.return_value = ("path/to/Epic1", ".epic")
        mock_os.path.exists.return_value = False

        # Call the method under test
        artefact_lister.list_data(classifier, artefact_name, list_filter)

        # Verify interactions
        mock_suggest.assert_not_called()
        mock_os.path.splitext.assert_called_with("path/to/Epic1.epic")
        mock_os.path.exists.assert_called_with("path/to/Epic1.data")
        mock_list_files.assert_not_called()


def test_list_data_artefact_not_found(artefact_lister):
    classifier = "epic"
    artefact_name = "NonExistentEpic"
    list_filter = None
    classified_artefacts = {
        "epic": [
            {"title": "Epic1", "file_path": "path/to/Epic1.epic"},
            {"title": "Epic2", "file_path": "path/to/Epic2.epic"},
        ]
    }

    with patch("ara_cli.artefact_lister.FileClassifier") as mock_file_classifier, patch(
        "ara_cli.artefact_lister.suggest_close_name_matches"
    ) as mock_suggest, patch("ara_cli.artefact_lister.os") as mock_os, patch(
        "ara_cli.artefact_lister.list_files_in_directory"
    ) as mock_list_files:

        # Configure mocks
        mock_classifier_instance = MagicMock()
        mock_file_classifier.return_value = mock_classifier_instance
        mock_classifier_instance.classify_files.return_value = classified_artefacts

        # Call the method under test
        artefact_lister.list_data(classifier, artefact_name, list_filter)

        # Verify interactions
        mock_suggest.assert_called_once_with(artefact_name, ["Epic1", "Epic2"])
        mock_os.path.splitext.assert_not_called()
        mock_os.path.exists.assert_not_called()
        mock_list_files.assert_not_called()


def test_list_data_with_filter(artefact_lister):
    classifier = "userstory"
    artefact_name = "Story1"
    list_filter = ListFilter(include_tags=["tag1"])
    classified_artefacts = {
        "userstory": [
            {"title": "Story1", "file_path": "path/to/Story1.userstory"},
            {"title": "Story2", "file_path": "path/to/Story2.userstory"},
        ]
    }

    with patch("ara_cli.artefact_lister.FileClassifier") as mock_file_classifier, patch(
        "ara_cli.artefact_lister.suggest_close_name_matches"
    ) as mock_suggest, patch("ara_cli.artefact_lister.os") as mock_os, patch(
        "ara_cli.artefact_lister.list_files_in_directory"
    ) as mock_list_files:

        # Configure mocks
        mock_classifier_instance = MagicMock()
        mock_file_classifier.return_value = mock_classifier_instance
        mock_classifier_instance.classify_files.return_value = classified_artefacts

        mock_os.path.splitext.return_value = ("path/to/Story1", ".userstory")
        mock_os.path.exists.return_value = True

        # Call the method under test
        artefact_lister.list_data(classifier, artefact_name, list_filter)

        # Verify interactions
        mock_suggest.assert_not_called()
        mock_os.path.splitext.assert_called_with("path/to/Story1.userstory")
        mock_os.path.exists.assert_called_with("path/to/Story1.data")
        mock_list_files.assert_called_once_with("path/to/Story1.data", list_filter)


def test_list_data_empty_artefact_list(artefact_lister):
    classifier = "epic"
    artefact_name = "Epic1"
    list_filter = None
    classified_artefacts = {"epic": []}

    with patch("ara_cli.artefact_lister.FileClassifier") as mock_file_classifier, patch(
        "ara_cli.artefact_lister.suggest_close_name_matches"
    ) as mock_suggest, patch("ara_cli.artefact_lister.os") as mock_os, patch(
        "ara_cli.artefact_lister.list_files_in_directory"
    ) as mock_list_files:

        # Configure mocks
        mock_classifier_instance = MagicMock()
        mock_file_classifier.return_value = mock_classifier_instance
        mock_classifier_instance.classify_files.return_value = classified_artefacts

        # Call the method under test
        artefact_lister.list_data(classifier, artefact_name, list_filter)

        # Verify interactions
        mock_suggest.assert_called_once_with(artefact_name, [])
        mock_os.path.splitext.assert_not_called()
        mock_os.path.exists.assert_not_called()
        mock_list_files.assert_not_called()
