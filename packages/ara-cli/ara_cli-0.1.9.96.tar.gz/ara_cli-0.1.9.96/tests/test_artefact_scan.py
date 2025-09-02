import pytest
from unittest.mock import patch, MagicMock, mock_open, call
from ara_cli.artefact_scan import (
    check_file,
    find_invalid_files,
    show_results,
    is_contribution_valid,
    is_rule_valid,
    check_contribution,
)


@pytest.mark.parametrize("contribution", [None, False, 0, "", []])
def test_check_contribution_none_contribution(contribution):
    # Should return (True, None) if contribution is falsey
    result = check_contribution(
        contribution, classified_artefact_info={}, file_path="irrelevant"
    )
    assert result == (True, None)


def test_check_contribution_invalid_contribution(monkeypatch):
    # If is_contribution_valid returns False, should return (False, custom_reason)
    contribution = MagicMock()
    contribution.classifier = "some_cls"
    contribution.artefact_name = "some_art"
    with patch(
        "ara_cli.artefact_scan.is_contribution_valid", return_value=False
    ) as mock_is_contrib, patch("ara_cli.artefact_scan.is_rule_valid") as mock_is_rule:
        result = check_contribution(
            contribution, classified_artefact_info={}, file_path="f"
        )
        assert result == (
            False,
            "Invalid Contribution Reference: The contribution references "
            "'some_cls' artefact 'some_art' which does not exist.",
        )
        mock_is_contrib.assert_called_once_with(contribution, {})
        mock_is_rule.assert_not_called()


def test_check_contribution_invalid_rule(monkeypatch):
    # is_contribution_valid returns True, is_rule_valid returns False
    contribution = MagicMock()
    contribution.classifier = "c"
    contribution.artefact_name = "a"
    contribution.rule = "r"
    with patch(
        "ara_cli.artefact_scan.is_contribution_valid", return_value=True
    ) as mock_is_contrib, patch(
        "ara_cli.artefact_scan.is_rule_valid", return_value=False
    ) as mock_is_rule:
        result = check_contribution(
            contribution, classified_artefact_info={"x": 1}, file_path="myfile"
        )
        assert result == (
            False,
            "Rule Mismatch: The contribution references rule 'r' which the parent c 'a' does not have.",
        )
        mock_is_contrib.assert_called_once_with(contribution, {"x": 1})
        mock_is_rule.assert_called_once_with(contribution, {"x": 1})


def test_check_contribution_all_valid(monkeypatch):
    # Both is_contribution_valid and is_rule_valid return True
    contribution = MagicMock()
    contribution.classifier = "c"
    contribution.artefact_name = "a"
    contribution.rule = "r"
    with patch(
        "ara_cli.artefact_scan.is_contribution_valid", return_value=True
    ) as mock_is_contrib, patch(
        "ara_cli.artefact_scan.is_rule_valid", return_value=True
    ) as mock_is_rule:
        result = check_contribution(
            contribution, classified_artefact_info={1: 2}, file_path="p"
        )
        assert result == (True, None)
        mock_is_contrib.assert_called_once_with(contribution, {1: 2})
        mock_is_rule.assert_called_once_with(contribution, {1: 2})


@pytest.mark.parametrize(
    "contribution_attrs,expected",
    [
        (None, True),  # contribution is None
        ({"artefact_name": None, "classifier": "foo"}, True),  # artefact_name is None
        (
            {"artefact_name": "", "classifier": "foo"},
            True,
        ),  # artefact_name is empty string
        ({"artefact_name": "bar", "classifier": None}, True),  # classifier is None
        (
            {"artefact_name": "bar", "classifier": ""},
            True,
        ),  # classifier is empty string
    ],
)
def test_is_rule_valid_short_circuits(contribution_attrs, expected):
    if contribution_attrs is None:
        contribution = None
    else:
        contribution = MagicMock()
        for k, v in contribution_attrs.items():
            setattr(contribution, k, v)
    with patch("ara_cli.artefact_reader.ArtefactReader.read_artefact") as mock_read:
        result = is_rule_valid(contribution, classified_artefact_info={})
        assert result is expected
        mock_read.assert_not_called()


def test_is_rule_valid_rule_is_none():
    """Should return True if contribution.rule is None or falsey."""
    contribution = MagicMock()
    contribution.artefact_name = "foo"
    contribution.classifier = "bar"
    contribution.rule = None
    with patch("ara_cli.artefact_reader.ArtefactReader.read_artefact") as mock_read:
        result = is_rule_valid(contribution, classified_artefact_info={})
        assert result is True
        mock_read.assert_not_called()

    # Also test rule as empty string
    contribution.rule = ""
    with patch("ara_cli.artefact_reader.ArtefactReader.read_artefact") as mock_read:
        result = is_rule_valid(contribution, classified_artefact_info={})
        assert result is True
        mock_read.assert_not_called()


@pytest.mark.parametrize(
    "parent,expected",
    [
        (None, True),  # parent is None
        (MagicMock(rules=None), True),  # parent.rules is None
    ],
)
def test_is_rule_valid_parent_or_rules_none(parent, expected):
    contribution = MagicMock()
    contribution.artefact_name = "foo"
    contribution.classifier = "bar"
    contribution.rule = "r1"
    with patch(
        "ara_cli.artefact_reader.ArtefactReader.read_artefact", return_value=parent
    ) as mock_read:
        result = is_rule_valid(contribution, classified_artefact_info={})
        assert result is expected
        mock_read.assert_called_once_with("foo", "bar")


def test_is_rule_valid_rule_not_in_parent_rules():
    """Should return False if rule is not in parent.rules."""
    contribution = MagicMock()
    contribution.artefact_name = "foo"
    contribution.classifier = "bar"
    contribution.rule = "missing_rule"
    parent = MagicMock()
    parent.rules = ["rule1", "rule2"]
    with patch(
        "ara_cli.artefact_reader.ArtefactReader.read_artefact", return_value=parent
    ) as mock_read:
        result = is_rule_valid(contribution, classified_artefact_info={})
        assert result is False
        mock_read.assert_called_once_with("foo", "bar")


def test_is_rule_valid_rule_in_parent_rules():
    """Should return True if rule is in parent.rules."""
    contribution = MagicMock()
    contribution.artefact_name = "foo"
    contribution.classifier = "bar"
    contribution.rule = "my_rule"
    parent = MagicMock()
    parent.rules = ["my_rule", "other_rule"]
    with patch(
        "ara_cli.artefact_reader.ArtefactReader.read_artefact", return_value=parent
    ) as mock_read:
        result = is_rule_valid(contribution, classified_artefact_info={})
        assert result is True
        mock_read.assert_called_once_with("foo", "bar")


@pytest.mark.parametrize(
    "contribution_attrs,expected",
    [
        # contribution is None
        (None, True),
        # artefact_name missing/None/empty
        ({"artefact_name": None, "classifier": "foo"}, True),
        ({"artefact_name": "", "classifier": "foo"}, True),
        # classifier missing/None/empty
        ({"artefact_name": "bar", "classifier": None}, True),
        ({"artefact_name": "bar", "classifier": ""}, True),
    ],
)
def test_is_contribution_valid_short_circuits(contribution_attrs, expected):
    classified_artefact_info = {"dummy": []}
    if contribution_attrs is None:
        contribution = None
    else:
        contribution = MagicMock()
        for k, v in contribution_attrs.items():
            setattr(contribution, k, v)
    with patch(
        "ara_cli.artefact_fuzzy_search.extract_artefact_names_of_classifier"
    ) as mock_extract:
        result = is_contribution_valid(contribution, classified_artefact_info)
        assert result is expected
        # The extract function should NOT be called in these cases
        mock_extract.assert_not_called()


def test_is_contribution_valid_references_existing_artefact():
    """
    contribution with valid artefact_name and classifier,
    artefact_name IS in list returned by extract_artefact_names_of_classifier.
    """
    contribution = MagicMock()
    contribution.artefact_name = "valid_art"
    contribution.classifier = "valid_clf"
    classified_artefact_info = {"valid_clf": [{"name": "valid_art"}]}
    with patch(
        "ara_cli.artefact_fuzzy_search.extract_artefact_names_of_classifier",
        return_value=["valid_art"],
    ) as mock_extract:
        result = is_contribution_valid(contribution, classified_artefact_info)
        assert result is True
        mock_extract.assert_called_once_with(
            classified_files=classified_artefact_info, classifier="valid_clf"
        )


def test_is_contribution_valid_references_missing_artefact():
    """
    contribution with valid artefact_name and classifier,
    artefact_name is NOT in list returned by extract_artefact_names_of_classifier.
    """
    contribution = MagicMock()
    contribution.artefact_name = "missing_art"
    contribution.classifier = "some_clf"
    classified_artefact_info = {"some_clf": [{"name": "another"}]}
    with patch(
        "ara_cli.artefact_fuzzy_search.extract_artefact_names_of_classifier",
        return_value=["another", "something_else"],
    ) as mock_extract:
        result = is_contribution_valid(contribution, classified_artefact_info)
        assert result is False
        mock_extract.assert_called_once_with(
            classified_files=classified_artefact_info, classifier="some_clf"
        )


def test_check_file_valid():
    """Tests the happy path where the file is valid and the title matches."""
    mock_artefact_instance = MagicMock()
    mock_artefact_instance.title = "dummy_path"
    # Mock contribution to be None to avoid contribution reference check
    mock_artefact_instance.contribution = None

    mock_artefact_class = MagicMock()
    mock_artefact_class.deserialize.return_value = mock_artefact_instance

    with patch("builtins.open", mock_open(read_data="valid content")):
        is_valid, reason = check_file("dummy_path.feature", mock_artefact_class)

    assert (
        reason is None
    ), f"Reason for invalid found, expected none to be found. The reason found: {reason}"
    assert is_valid is True, "File detected as invalid, expected to be valid"


def test_check_file_title_mismatch():
    """Tests the case where the filename and artefact title do not match."""
    mock_artefact_instance = MagicMock()
    mock_artefact_instance.title = "wrong_title"

    mock_artefact_class = MagicMock()
    mock_artefact_class.deserialize.return_value = mock_artefact_instance

    with patch("builtins.open", mock_open(read_data="content")):
        is_valid, reason = check_file("correct_path.feature", mock_artefact_class)

    assert is_valid is False
    assert "Filename-Title Mismatch" in reason

    assert "'correct_path'" in reason
    assert "'wrong_title'" in reason


def test_check_file_value_error():
    mock_artefact_class = MagicMock()
    mock_artefact_class.deserialize.side_effect = ValueError("Value error")

    with patch("builtins.open", mock_open(read_data="invalid content")):
        is_valid, reason = check_file("dummy_path", mock_artefact_class)
        assert is_valid is False
        assert "Value error" in reason


def test_check_file_assertion_error():
    mock_artefact_class = MagicMock()
    mock_artefact_class.deserialize.side_effect = AssertionError("Assertion error")

    with patch("builtins.open", mock_open(read_data="invalid content")):
        is_valid, reason = check_file("dummy_path", mock_artefact_class)
        assert is_valid is False
        assert "Assertion error" in reason


def test_check_file_os_error():
    mock_artefact_class = MagicMock()

    with patch("builtins.open", side_effect=OSError("File not found")):
        is_valid, reason = check_file("dummy_path", mock_artefact_class)
        assert is_valid is False
        assert "File error: File not found" in reason


def test_check_file_unexpected_error():
    mock_artefact_class = MagicMock()
    mock_artefact_class.deserialize.side_effect = Exception("Unexpected error")

    with patch("builtins.open", mock_open(read_data="content")):
        is_valid, reason = check_file("dummy_path", mock_artefact_class)
        assert is_valid is False
        assert "Unexpected error: Exception('Unexpected error')" in reason


# Tests for find_invalid_files


def test_find_invalid_files():
    """Tests finding invalid files with proper mocking of check_file."""
    mock_artefact_class = MagicMock()
    classified_info = {
        "test_classifier": [
            {"file_path": "file1.txt"},  # Should be checked
            {"file_path": "file2.txt"},  # Should be checked
            {"file_path": "templates/file3.txt"},  # Should be skipped
            {"file_path": "some/path/file.data"},  # Should be skipped
        ]
    }

    with patch(
        "ara_cli.artefact_models.artefact_mapping.artefact_type_mapping",
        {"test_classifier": mock_artefact_class},
    ):
        with patch("ara_cli.artefact_scan.check_file") as mock_check_file:
            mock_check_file.side_effect = [
                (True, None),  # for file1.txt
                (False, "Invalid content"),  # for file2.txt
            ]

            invalid_files = find_invalid_files(classified_info, "test_classifier")

            assert len(invalid_files) == 1
            assert invalid_files[0] == ("file2.txt", "Invalid content")
            assert mock_check_file.call_count == 2

            # Check that check_file was called with the correct parameters
            mock_check_file.assert_has_calls(
                [
                    call("file1.txt", mock_artefact_class, classified_info),
                    call("file2.txt", mock_artefact_class, classified_info),
                ],
                any_order=False,
            )


def test_show_results_no_issues(capsys):
    invalid_artefacts = {}
    with patch("builtins.open", mock_open()) as m:
        show_results(invalid_artefacts)
        captured = capsys.readouterr()
        assert captured.out == "All files are good!\n"
        m.assert_called_once_with(
            "incompatible_artefacts_report.md", "w", encoding="utf-8"
        )
        handle = m()
        handle.write.assert_has_calls(
            [call("# Artefact Check Report\n\n"), call("No problems found.\n")],
            any_order=False,
        )


def test_show_results_with_issues(capsys):
    invalid_artefacts = {
        "classifier1": [("file1.txt", "reason1"), ("file2.txt", "reason2")],
        "classifier2": [("file3.txt", "reason3")],
    }
    with patch("builtins.open", mock_open()) as m:
        show_results(invalid_artefacts)
        captured = capsys.readouterr()
        expected_output = (
            "\nIncompatible classifier1 Files:\n"
            "\t- file1.txt\n"
            "\t\treason1\n"
            "\t- file2.txt\n"
            "\t\treason2\n"
            "\nIncompatible classifier2 Files:\n"
            "\t- file3.txt\n"
            "\t\treason3\n"
        )
        assert captured.out == expected_output
        m.assert_called_once_with(
            "incompatible_artefacts_report.md", "w", encoding="utf-8"
        )
        handle = m()
        expected_writes = [
            call("# Artefact Check Report\n\n"),
            call("## classifier1\n"),
            call("- `file1.txt`: reason1\n"),
            call("- `file2.txt`: reason2\n"),
            call("\n"),
            call("## classifier2\n"),
            call("- `file3.txt`: reason3\n"),
            call("\n"),
        ]
        handle.write.assert_has_calls(expected_writes, any_order=False)


def test_check_file_with_invalid_contribution():
    """Tests file with invalid contribution reference."""
    mock_artefact_instance = MagicMock()
    mock_artefact_instance.title = "dummy_path"

    # Set up invalid contribution
    mock_contribution = MagicMock()
    mock_contribution.classifier = "test_classifier"
    mock_contribution.artefact_name = "non_existing_artefact"
    mock_artefact_instance.contribution = mock_contribution

    mock_artefact_class = MagicMock()
    mock_artefact_class.deserialize.return_value = mock_artefact_instance

    # Mock classified_artefact_info
    classified_info = {"test_classifier": [{"name": "existing_artefact"}]}

    # Mock extract_artefact_names_of_classifier to return a list without the referenced artefact
    with patch("builtins.open", mock_open(read_data="valid content")):
        with patch(
            "ara_cli.artefact_fuzzy_search.extract_artefact_names_of_classifier",
            return_value=["existing_artefact"],
        ):
            is_valid, reason = check_file(
                "dummy_path.feature", mock_artefact_class, classified_info
            )

    assert is_valid is False
    assert "Invalid Contribution Reference" in reason
