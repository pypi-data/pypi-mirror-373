import pytest
from unittest.mock import patch, mock_open, MagicMock
from ara_cli.error_handler import AraError
from ara_cli.artefact_autofix import (
    read_report_file,
    parse_report,
    apply_autofix,
    read_artefact,
    determine_artefact_type_and_class,
    run_agent,
    write_corrected_artefact,
    construct_prompt,
    fix_title_mismatch,
    ask_for_correct_contribution,
    ask_for_contribution_choice,
    _has_valid_contribution,
    set_closest_contribution,
    fix_contribution,
    fix_rule,
    fix_scenario_placeholder_mismatch,
    _extract_scenario_block,
    _is_scenario_boundary,
    _process_scenario_block,
    _get_line_indentation,
    _extract_placeholders_from_scenario,
    _update_docstring_state,
    _convert_to_scenario_outline,
    _create_examples_table,
    populate_classified_artefact_info,
    should_skip_issue,
    determine_attempt_count,
    apply_deterministic_fix,
    apply_non_deterministic_fix,
    attempt_autofix_loop,
)
from ara_cli.artefact_models.artefact_model import Artefact, ArtefactType, Contribution


@pytest.fixture
def mock_artefact_type():
    """Provides a mock for the ArtefactType enum member."""
    mock_type = MagicMock()
    mock_type.value = "feature"
    return mock_type


@pytest.fixture
def mock_artefact_class():
    """Provides a mock for the Artefact class."""
    mock_class = MagicMock()
    mock_class._title_prefix.return_value = "Feature:"
    # Mock the serialize method for the agent tests
    mock_class.serialize.return_value = "llm corrected content"
    return mock_class


@pytest.fixture
def mock_classified_artefact_info():
    """Provides a mock for the classified artefact info dictionary."""
    return MagicMock()


@pytest.fixture
def mock_artefact_with_contribution():
    """Provides a mock Artefact with a mock Contribution."""
    mock_contribution = MagicMock(spec=Contribution)
    mock_contribution.artefact_name = "some_artefact"
    mock_contribution.classifier = "feature"
    mock_contribution.rule = "some rule"

    mock_artefact = MagicMock(spec=Artefact)
    mock_artefact.contribution = mock_contribution
    mock_artefact.title = "my_test_artefact"
    mock_artefact._artefact_type.return_value.value = "requirement"
    mock_artefact.serialize.return_value = "serialized artefact text"

    return mock_artefact


@pytest.fixture
def mock_contribution():
    m = MagicMock()
    m.artefact_name = "parent_name"
    m.classifier = "feature"
    m.rule = "my_rule"
    return m

@pytest.fixture
def mock_artefact(mock_contribution):
    m = MagicMock()
    m.contribution = mock_contribution
    m._artefact_type.return_value.value = "requirement"
    m.title = "my_title"
    m.serialize.return_value = "serialized-text"
    return m


def test_read_report_file_success():
    """Tests successful reading of the report file."""
    mock_content = "# Artefact Check Report\n- `file.feature`: reason"
    with patch("builtins.open", mock_open(read_data=mock_content)) as m:
        content = read_report_file()
        assert content == mock_content
        m.assert_called_once_with(
            "incompatible_artefacts_report.md", "r", encoding="utf-8"
        )


def test_read_report_file_not_found(capsys):
    with patch("builtins.open", side_effect=OSError("File not found")):
        content = read_report_file()
        assert content is None
        assert "Artefact scan results file not found" in capsys.readouterr().out


def test_parse_report_with_issues():
    content = (
        "# Artefact Check Report\n\n## feature\n- `path/to/file.feature`: A reason\n"
    )
    expected = {"feature": [("path/to/file.feature", "A reason")]}
    assert parse_report(content) == expected


def test_parse_report_no_issues():
    content = "# Artefact Check Report\n\nNo problems found.\n"
    assert parse_report(content) == {}


def test_parse_report_invalid_format():
    assert parse_report("This is not a valid report") == {}


def test_parse_report_invalid_line_format():
    content = "# Artefact Check Report\n\n## feature\n- an invalid line\n"
    assert parse_report(content) == {"feature": []}


def test_read_artefact_success():
    mock_content = "Feature: My Feature"
    with patch("builtins.open", mock_open(read_data=mock_content)) as m:
        content = read_artefact("file.feature")
        assert content == mock_content
        m.assert_called_once_with("file.feature", "r", encoding="utf-8")


def test_read_artefact_file_not_found(capsys):
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = read_artefact("nonexistent.feature")
        assert result is None
        assert "File not found: nonexistent.feature" in capsys.readouterr().out


@patch("ara_cli.artefact_models.artefact_mapping.artefact_type_mapping")
def test_determine_artefact_type_and_class_no_class_found(mock_mapping, capsys):
    mock_mapping.get.return_value = None
    with pytest.raises(AraError):
        artefact_type, artefact_class = determine_artefact_type_and_class("feature")


@patch("ara_cli.artefact_models.artefact_model.ArtefactType", side_effect=ValueError)
def test_determine_artefact_type_and_class_invalid(mock_artefact_type_enum, capsys):
    artefact_type, artefact_class = determine_artefact_type_and_class(
        "invalid_classifier"
    )
    assert artefact_type is None
    assert artefact_class is None
    assert "Invalid classifier: invalid_classifier" in capsys.readouterr().out


def test_write_corrected_artefact():
    with patch("builtins.open", mock_open()) as m:
        write_corrected_artefact("file.feature", "corrected content")
        m.assert_called_once_with("file.feature", "w", encoding="utf-8")
        m().write.assert_called_once_with("corrected content")


def test_construct_prompt_for_task():
    prompt = construct_prompt(ArtefactType.task, "some reason", "file.task", "text")
    assert (
        "For task artefacts, if the action items looks like template or empty"
        in prompt
    )


@patch("ara_cli.artefact_autofix.run_agent")
@patch(
    "ara_cli.artefact_autofix.determine_artefact_type_and_class",
    return_value=(None, None),
)
@patch("ara_cli.artefact_autofix.read_artefact")
def test_apply_autofix_exits_when_classifier_is_invalid(
    mock_read, mock_determine, mock_run_agent, mock_classified_artefact_info
):
    """Tests that apply_autofix exits early if the classifier is invalid."""
    result = apply_autofix(
        file_path="file.feature",
        classifier="invalid",
        reason="reason",
        deterministic=True,
        non_deterministic=True,
        classified_artefact_info=mock_classified_artefact_info,
    )
    assert result is False
    mock_determine.assert_called_once_with("invalid")
    mock_read.assert_not_called()
    mock_run_agent.assert_not_called()


@patch("ara_cli.artefact_autofix.FileClassifier")
@patch("ara_cli.artefact_autofix.check_file")
@patch("ara_cli.artefact_autofix.run_agent")
@patch("ara_cli.artefact_autofix.write_corrected_artefact")
@patch("ara_cli.artefact_autofix.fix_title_mismatch")
@patch("ara_cli.artefact_autofix.determine_artefact_type_and_class")
@patch("ara_cli.artefact_autofix.read_artefact", return_value="original text")
def test_apply_autofix_for_title_mismatch_with_deterministic_flag(
    mock_read,
    mock_determine,
    mock_fix_title,
    mock_write,
    mock_run_agent,
    mock_check_file,
    mock_file_classifier,
    mock_artefact_type,
    mock_artefact_class,
    mock_classified_artefact_info,
):
    """Tests that a deterministic fix is applied when the flag is True."""
    mock_determine.return_value = (mock_artefact_type, mock_artefact_class)
    mock_check_file.side_effect = [
        (False, "Filename-Title Mismatch: some details"),
        (True, ""),
    ]
    mock_fix_title.return_value = "fixed text"

    result = apply_autofix(
        file_path="file.feature",
        classifier="feature",
        reason="Filename-Title Mismatch: some details",
        deterministic=True,
        non_deterministic=False,
        classified_artefact_info=mock_classified_artefact_info,
    )

    assert result is True
    assert mock_check_file.call_count == 2
    mock_fix_title.assert_called_once_with(
        file_path="file.feature",
        artefact_text="original text",
        artefact_class=mock_artefact_class,
        classified_artefact_info=mock_classified_artefact_info,
    )
    mock_write.assert_called_once_with("file.feature", "fixed text")
    mock_run_agent.assert_not_called()
    mock_file_classifier.assert_called_once()


@patch("ara_cli.artefact_autofix.check_file")
@patch("ara_cli.artefact_autofix.run_agent")
@patch("ara_cli.artefact_autofix.write_corrected_artefact")
@patch("ara_cli.artefact_autofix.fix_title_mismatch")
@patch("ara_cli.artefact_autofix.determine_artefact_type_and_class")
@patch("ara_cli.artefact_autofix.read_artefact", return_value="original text")
def test_apply_autofix_skips_title_mismatch_without_deterministic_flag(
    mock_read,
    mock_determine,
    mock_fix_title,
    mock_write,
    mock_run_agent,
    mock_check_file,
    mock_artefact_type,
    mock_artefact_class,
    mock_classified_artefact_info,
):
    """Tests that a deterministic fix is skipped when the flag is False."""
    mock_determine.return_value = (mock_artefact_type, mock_artefact_class)
    mock_check_file.return_value = (False, "Filename-Title Mismatch: some details")

    result = apply_autofix(
        file_path="file.feature",
        classifier="feature",
        reason="Filename-Title Mismatch: some details",
        deterministic=False,
        non_deterministic=True,
        classified_artefact_info=mock_classified_artefact_info,
    )

    assert result is False
    mock_check_file.assert_called_once()
    mock_read.assert_called_once_with("file.feature")
    mock_fix_title.assert_not_called()
    mock_write.assert_not_called()
    mock_run_agent.assert_not_called()


@patch("ara_cli.artefact_autofix.FileClassifier")
@patch("ara_cli.artefact_autofix.check_file")
@patch("ara_cli.artefact_autofix.write_corrected_artefact")
@patch("ara_cli.artefact_autofix.run_agent")
@patch("ara_cli.artefact_autofix.determine_artefact_type_and_class")
@patch("ara_cli.artefact_autofix.read_artefact", return_value="original text")
def test_apply_autofix_for_llm_fix_with_non_deterministic_flag(
    mock_read,
    mock_determine,
    mock_run_agent,
    mock_write,
    mock_check_file,
    mock_file_classifier,
    mock_artefact_type,
    mock_artefact_class,
    mock_classified_artefact_info,
):
    """Tests that an LLM fix is applied when the non-deterministic flag is True."""
    mock_determine.return_value = (mock_artefact_type, mock_artefact_class)
    mock_check_file.side_effect = [(False, "Pydantic validation error"), (True, "")]
    mock_run_agent.return_value = mock_artefact_class

    result = apply_autofix(
        file_path="file.feature",
        classifier="feature",
        reason="Pydantic validation error",
        deterministic=False,
        non_deterministic=True,
        classified_artefact_info=mock_classified_artefact_info,
    )

    assert result is True
    assert mock_check_file.call_count == 2
    mock_read.assert_called_once_with("file.feature")
    mock_run_agent.assert_called_once()
    mock_write.assert_called_once_with("file.feature", "llm corrected content")
    mock_file_classifier.assert_called_once()


@patch("ara_cli.artefact_autofix.write_corrected_artefact")
@patch("ara_cli.artefact_autofix.run_agent")
@patch("ara_cli.artefact_autofix.determine_artefact_type_and_class")
@patch("ara_cli.artefact_autofix.read_artefact", return_value="original text")
def test_apply_autofix_skips_llm_fix_without_non_deterministic_flag(
    mock_read,
    mock_determine,
    mock_run_agent,
    mock_write,
    mock_artefact_type,
    mock_artefact_class,
    mock_classified_artefact_info,
):
    """Tests that an LLM fix is skipped when the non-deterministic flag is False."""
    mock_determine.return_value = (mock_artefact_type, mock_artefact_class)
    reason = "Pydantic validation error"

    result = apply_autofix(
        "file.feature",
        "feature",
        reason,
        deterministic=True,
        non_deterministic=False,
        classified_artefact_info=mock_classified_artefact_info,
    )

    assert result is False
    mock_run_agent.assert_not_called()
    mock_write.assert_not_called()


@patch("ara_cli.artefact_autofix.run_agent", side_effect=Exception("LLM failed"))
@patch("ara_cli.artefact_autofix.determine_artefact_type_and_class")
@patch("ara_cli.artefact_autofix.read_artefact", return_value="original text")
def test_apply_autofix_llm_exception(
    mock_read,
    mock_determine,
    mock_run_agent,
    capsys,
    mock_artefact_type,
    mock_artefact_class,
    mock_classified_artefact_info,
):
    """Tests that an exception during an LLM fix is handled gracefully."""
    mock_determine.return_value = (mock_artefact_type, mock_artefact_class)
    reason = "Pydantic validation error"

    result = apply_autofix(
        "file.feature",
        "feature",
        reason,
        deterministic=False,
        non_deterministic=True,
        classified_artefact_info=mock_classified_artefact_info,
    )

    assert result is False
    assert (
        "LLM agent failed to fix artefact at file.feature: LLM failed"
        in capsys.readouterr().out
    )


def test_fix_title_mismatch_success(mock_artefact_class):
    artefact_text = "Feature: wrong title\nSome other content"
    file_path = "path/to/correct_title.feature"

    expected_text = "Feature: correct title\nSome other content"

    result = fix_title_mismatch(file_path, artefact_text, mock_artefact_class)

    assert result == expected_text
    mock_artefact_class._title_prefix.assert_called_once()


def test_fix_title_mismatch_prefix_not_found(capsys, mock_artefact_class):
    artefact_text = "No title prefix here"
    file_path = "path/to/correct_title.feature"

    result = fix_title_mismatch(file_path, artefact_text, mock_artefact_class)

    assert result == artefact_text  # Should return original text
    assert "Warning: Title prefix 'Feature:' not found" in capsys.readouterr().out


@patch("pydantic_ai.Agent")
def test_run_agent_exception_handling(mock_agent_class):
    mock_agent_instance = mock_agent_class.return_value
    mock_agent_instance.run_sync.side_effect = Exception("Agent error")
    with pytest.raises(Exception, match="Agent error"):
        run_agent("prompt", MagicMock())


@patch("builtins.input", side_effect=["1"])
def test_ask_for_contribution_choice_valid(mock_input):
    """Tests selecting a valid choice."""
    choices = ["choice1", "choice2"]
    # This simpler call now works without causing a TypeError
    result = ask_for_contribution_choice(choices)
    assert result == "choice1"

@patch("builtins.input", side_effect=["99"])
def test_ask_for_contribution_choice_out_of_range(mock_input, capsys):
    """Tests selecting a choice that is out of range."""
    choices = ["choice1", "choice2"]
    result = ask_for_contribution_choice(choices)
    assert result is None
    assert "Invalid choice" in capsys.readouterr().out


@patch("builtins.input", side_effect=["not a number"])
def test_ask_for_contribution_choice_invalid_input(mock_input, capsys):
    """Tests providing non-numeric input."""
    choices = ["choice1", "choice2"]
    result = ask_for_contribution_choice(choices)
    assert result is None
    assert "Invalid input" in capsys.readouterr().out


@patch("builtins.input", side_effect=["feature my_feature_name"])
def test_ask_for_correct_contribution_valid(mock_input):
    """Tests providing valid '<classifier> <name>' input."""
    name, classifier = ask_for_correct_contribution(("old_name", "feature"))
    assert name == "my_feature_name"
    assert classifier == "feature"


@patch("builtins.input", side_effect=[""])
def test_ask_for_correct_contribution_empty_input(mock_input):
    """Tests providing empty input."""
    name, classifier = ask_for_correct_contribution()
    assert name is None
    assert classifier is None


@patch("builtins.input", side_effect=["invalid-one-word-input"])
def test_ask_for_correct_contribution_invalid_format(mock_input, capsys):
    """Tests providing input with the wrong format."""
    # Fix: Use input that results in a single part after split()
    name, classifier = ask_for_correct_contribution()
    assert name is None
    assert classifier is None
    assert "Invalid input format" in capsys.readouterr().out


def test_has_valid_contribution_true(mock_artefact_with_contribution):
    """Tests with a valid contribution object."""
    # Fix: Check for truthiness, not strict boolean equality
    assert _has_valid_contribution(mock_artefact_with_contribution)


def test_has_valid_contribution_false_no_contribution():
    """Tests when the artefact's contribution is None."""
    mock_artefact = MagicMock(spec=Artefact)
    mock_artefact.contribution = None
    # Fix: Check for falsiness, not strict boolean equality
    assert not _has_valid_contribution(mock_artefact)


@patch("ara_cli.artefact_autofix.FileClassifier")
@patch("ara_cli.artefact_autofix.extract_artefact_names_of_classifier")
@patch("ara_cli.artefact_autofix.find_closest_name_matches")
def test_set_closest_contribution_no_change_needed(
    mock_find, mock_extract, mock_classifier, mock_artefact_with_contribution
):
    """Tests the case where the contribution name is already the best match."""
    mock_find.return_value = ["some_artefact"]  # Exact match is found
    artefact, changed = set_closest_contribution(mock_artefact_with_contribution)
    assert changed is False
    assert artefact == mock_artefact_with_contribution


@patch("ara_cli.artefact_autofix.FileClassifier")
@patch("ara_cli.artefact_autofix.extract_artefact_names_of_classifier")
@patch("ara_cli.artefact_autofix.find_closest_name_matches", return_value=[])
@patch(
    "ara_cli.artefact_autofix.ask_for_correct_contribution",
    return_value=("new_name", "new_classifier"),
)
def test_set_closest_contribution_no_matches_user_provides(
    mock_ask, mock_find, mock_extract, mock_classifier, mock_artefact_with_contribution
):
    """Tests when no matches are found and the user provides a new contribution."""
    artefact, changed = set_closest_contribution(mock_artefact_with_contribution)
    assert changed is True
    assert artefact.contribution.artefact_name == "new_name"
    assert artefact.contribution.classifier == "new_classifier"


@patch("ara_cli.artefact_autofix.set_closest_contribution")
@patch("ara_cli.artefact_autofix.FileClassifier")
def test_fix_contribution(
    mock_file_classifier, mock_set, mock_artefact_with_contribution
):
    """Tests the fix_contribution wrapper function."""
    # Arrange
    mock_artefact_class = MagicMock()
    mock_artefact_class.deserialize.return_value = mock_artefact_with_contribution
    mock_set.return_value = (mock_artefact_with_contribution, True)

    # Act
    result = fix_contribution(
        file_path="dummy.path",
        artefact_text="original text",
        artefact_class=mock_artefact_class,
        classified_artefact_info={},
    )

    # Assert
    assert result == "serialized artefact text"
    mock_artefact_class.deserialize.assert_called_once_with("original text")
    mock_set.assert_called_once_with(mock_artefact_with_contribution)


@patch("ara_cli.artefact_autofix.FileClassifier")
@patch("ara_cli.artefact_autofix.check_file")
@patch("ara_cli.artefact_autofix.write_corrected_artefact")
@patch("ara_cli.artefact_autofix.fix_contribution", return_value="fixed text")
@patch("ara_cli.artefact_autofix.determine_artefact_type_and_class")
@patch("ara_cli.artefact_autofix.read_artefact", return_value="original text")
def test_apply_autofix_for_contribution_mismatch(
    mock_read,
    mock_determine,
    mock_fix_contribution,
    mock_write,
    mock_check_file,
    mock_classifier,
    mock_artefact_type,
    mock_artefact_class,
    mock_classified_artefact_info,
):
    """Tests the deterministic fix for 'Invalid Contribution Reference'."""
    mock_determine.return_value = (mock_artefact_type, mock_artefact_class)
    mock_check_file.side_effect = [
        (False, "Invalid Contribution Reference"),
        (True, ""),
    ]

    result = apply_autofix(
        file_path="file.feature",
        classifier="feature",
        reason="Invalid Contribution Reference",
        classified_artefact_info=mock_classified_artefact_info,
    )

    assert result is True
    mock_fix_contribution.assert_called_once()
    mock_write.assert_called_once_with("file.feature", "fixed text")


@patch("ara_cli.artefact_autofix.check_file")
@patch("ara_cli.artefact_autofix.write_corrected_artefact")
@patch("ara_cli.artefact_autofix.fix_title_mismatch", return_value="original text")
@patch("ara_cli.artefact_autofix.determine_artefact_type_and_class")
@patch("ara_cli.artefact_autofix.read_artefact", return_value="original text")
def test_apply_autofix_stops_if_no_alteration(
    mock_read,
    mock_determine,
    mock_fix_title,
    mock_write,
    mock_check_file,
    capsys,
    mock_artefact_type,
    mock_artefact_class,
    mock_classified_artefact_info,
):
    """Tests that the loop stops if a fix attempt does not change the file content."""
    mock_determine.return_value = (mock_artefact_type, mock_artefact_class)
    mock_check_file.return_value = (False, "Filename-Title Mismatch")

    result = apply_autofix(
        file_path="file.feature",
        classifier="feature",
        reason="any",
        classified_artefact_info=mock_classified_artefact_info,
    )

    assert result is False
    mock_fix_title.assert_called_once()
    mock_write.assert_not_called()
    assert (
        "Fixing attempt did not alter the file. Stopping to prevent infinite loop."
        in capsys.readouterr().out
    )


@patch("ara_cli.artefact_autofix.check_file")
@patch("ara_cli.artefact_autofix.determine_artefact_type_and_class")
def test_apply_autofix_single_pass(
    mock_determine,
    mock_check_file,
    capsys,
    mock_artefact_type,
    mock_artefact_class,
    mock_classified_artefact_info,
):
    """Tests that single_pass=True runs the loop only once."""
    mock_determine.return_value = (mock_artefact_type, mock_artefact_class)
    # Simulate a failure that won't be fixed to ensure the loop doesn't repeat
    mock_check_file.return_value = (False, "Some unfixable error")

    apply_autofix(
        file_path="file.feature",
        classifier="feature",
        reason="any",
        single_pass=True,
        deterministic=False, # Disable fixes
        non_deterministic=False,
        classified_artefact_info=mock_classified_artefact_info,
    )

    output = capsys.readouterr().out
    assert "Single-pass mode enabled" in output
    assert "Attempt 1/1" in output
    assert "Attempt 2/1" not in output
    mock_check_file.assert_called_once()


@patch("ara_cli.artefact_autofix._update_rule")
@patch("ara_cli.artefact_autofix.populate_classified_artefact_info")
def test_fix_rule_with_rule(mock_populate, mock_update_rule, mock_artefact, mock_contribution, capsys):
    # Contribution has a rule
    artefact_class = MagicMock()
    artefact_class.deserialize.return_value = mock_artefact
    mock_populate.return_value = {"info": "dummy"}

    result = fix_rule(
        file_path="dummy.feature",
        artefact_text="text",
        artefact_class=artefact_class,
        classified_artefact_info={},
    )

    # deserialize called
    artefact_class.deserialize.assert_called_once_with("text")
    # _update_rule called with correct args
    mock_update_rule.assert_called_once_with(
        artefact=mock_artefact,
        name="parent_name",
        classifier="feature",
        classified_file_info={"info": "dummy"},
        delete_if_not_found=True,
    )
    # Feedback message contains rule
    assert "with rule" in capsys.readouterr().out
    # Result is the serialized text
    assert result == "serialized-text"

@patch("ara_cli.artefact_autofix._update_rule")
@patch("ara_cli.artefact_autofix.populate_classified_artefact_info")
def test_fix_rule_without_rule(mock_populate, mock_update_rule, mock_artefact, mock_contribution, capsys):
    # Contribution rule becomes None after update
    mock_contribution.rule = None
    artefact_class = MagicMock()
    artefact_class.deserialize.return_value = mock_artefact
    mock_populate.return_value = {"info": "dummy"}

    result = fix_rule(
        file_path="dummy.feature",
        artefact_text="text",
        artefact_class=artefact_class,
        classified_artefact_info={},
    )

    # Feedback message says "without a rule"
    assert "without a rule" in capsys.readouterr().out
    assert result == "serialized-text"

@patch("ara_cli.artefact_autofix.populate_classified_artefact_info")
def test_fix_rule_contribution_none_raises(mock_populate):
    # artefact.contribution is None: should assert
    artefact = MagicMock()
    artefact.contribution = None
    artefact_class = MagicMock()
    artefact_class.deserialize.return_value = artefact
    mock_populate.return_value = {}

    with pytest.raises(AssertionError):
        fix_rule(
            file_path="dummy.feature",
            artefact_text="stuff",
            artefact_class=artefact_class,
            classified_artefact_info={},
        )

def test_populate_classified_artefact_info_force_true():
    """Test populate_classified_artefact_info with force=True"""
    with patch('ara_cli.artefact_autofix.FileClassifier') as mock_classifier:
        mock_instance = mock_classifier.return_value
        mock_instance.classify_files.return_value = {"new": "data"}
        
        result = populate_classified_artefact_info({"old": "data"}, force=True)
        
        assert result == {"new": "data"}
        mock_classifier.assert_called_once()

def test_populate_classified_artefact_info_none_input():
    """Test populate_classified_artefact_info with None input"""
    with patch('ara_cli.artefact_autofix.FileClassifier') as mock_classifier:
        mock_instance = mock_classifier.return_value
        mock_instance.classify_files.return_value = {"classified": "data"}
        
        result = populate_classified_artefact_info(None)
        
        assert result == {"classified": "data"}
        mock_classifier.assert_called_once()

def test_parse_report_empty_content():
    """Test parse_report with empty content"""
    assert parse_report("") == {}

def test_parse_report_missing_reason():
    """Test parse_report with missing reason in issue line"""
    content = "# Artefact Check Report\n\n## feature\n- `file.feature`\n"
    expected = {"feature": [("file.feature", "")]}
    assert parse_report(content) == expected

def test_parse_report_multiple_classifiers():
    """Test parse_report with multiple classifiers"""
    content = (
        "# Artefact Check Report\n\n"
        "## feature\n- `file1.feature`: reason1\n\n"
        "## task\n- `file2.task`: reason2\n"
    )
    expected = {
        "feature": [("file1.feature", "reason1")],
        "task": [("file2.task", "reason2")]
    }
    assert parse_report(content) == expected

def test_construct_prompt_non_task_artefact():
    """Test construct_prompt for non-task artefact types"""
    prompt = construct_prompt(ArtefactType.feature, "some reason", "file.feature", "text")
    assert "For task artefacts" not in prompt
    assert "some reason" in prompt
    assert "file.feature" in prompt

@patch("pydantic_ai.Agent")
def test_run_agent_success(mock_agent_class):
    """Test successful run_agent execution"""
    mock_agent_instance = mock_agent_class.return_value
    mock_result = MagicMock()
    mock_result.output = "agent output"
    mock_agent_instance.run_sync.return_value = mock_result
    
    result = run_agent("test prompt", MagicMock())
    
    assert result == "agent output"
    mock_agent_class.assert_called_once()

def test_write_corrected_artefact_with_print(capsys):
    """Test write_corrected_artefact prints success message"""
    with patch("builtins.open", mock_open()) as m:
        write_corrected_artefact("file.feature", "corrected content")
        
        captured = capsys.readouterr()
        assert "Fixed artefact at file.feature" in captured.out

# Tests for the new scenario placeholder functions
def test_extract_scenario_block():
    """Test _extract_scenario_block function"""
    lines = [
        "Feature: Test",
        "Scenario: Test scenario",
        "  Given something",
        "  When something",
        "Scenario: Another scenario"
    ]
    
    scenario_lines, next_index = _extract_scenario_block(lines, 1)
    
    assert len(scenario_lines) == 3
    assert scenario_lines[0] == "Scenario: Test scenario"
    assert next_index == 4

def test_is_scenario_boundary():
    """Test _is_scenario_boundary function"""
    assert _is_scenario_boundary("Scenario: test")
    assert _is_scenario_boundary("Scenario Outline: test")
    assert _is_scenario_boundary("Background:")
    assert _is_scenario_boundary("Feature: test")
    assert not _is_scenario_boundary("Given something")

def test_process_scenario_block_no_placeholders():
    """Test _process_scenario_block with no placeholders"""
    scenario_lines = [
        "  Scenario: Test",
        "    Given something",
        "    When something"
    ]
    
    result = _process_scenario_block(scenario_lines)
    
    assert result == scenario_lines

def test_process_scenario_block_with_placeholders():
    """Test _process_scenario_block with placeholders"""
    scenario_lines = [
        "  Scenario: Test",
        "    Given something with <placeholder>",
        "    When something with <another>"
    ]
    
    result = _process_scenario_block(scenario_lines)
    
    assert "Scenario Outline:" in result[0]
    assert "Examples:" in result[-3]

def test_get_line_indentation():
    """Test _get_line_indentation function"""
    assert _get_line_indentation("    indented line") == "    "
    assert _get_line_indentation("no indent") == ""
    assert _get_line_indentation("  two spaces") == "  "

def test_extract_placeholders_from_scenario():
    """Test _extract_placeholders_from_scenario function"""
    step_lines = [
        "  Given something with <placeholder1>",
        "  When something with <placeholder2>",
        "  Then something normal"
    ]
    
    placeholders = _extract_placeholders_from_scenario(step_lines)
    
    assert placeholders == {"placeholder1", "placeholder2"}

def test_extract_placeholders_with_docstring():
    """Test _extract_placeholders_from_scenario ignoring docstrings"""
    step_lines = [
        "  Given something with <placeholder1>",
        '  """',
        "  Some docstring with <not_a_placeholder>",
        '  """',
        "  When something with <placeholder2>"
    ]
    
    placeholders = _extract_placeholders_from_scenario(step_lines)
    
    assert placeholders == {"placeholder1", "placeholder2"}

def test_update_docstring_state():
    """Test _update_docstring_state function"""
    assert _update_docstring_state('"""', False) == True
    assert _update_docstring_state('"""', True) == False
    assert _update_docstring_state('normal line', False) == False
    assert _update_docstring_state('normal line', True) == True

def test_convert_to_scenario_outline():
    """Test _convert_to_scenario_outline function"""
    scenario_lines = [
        "  Scenario: Test scenario",
        "    Given something",
        "    When something"
    ]
    placeholders = {"placeholder1", "placeholder2"}
    
    result = _convert_to_scenario_outline(scenario_lines, placeholders, "  ")
    
    assert "Scenario Outline: Test scenario" in result[0]
    assert "Examples:" in result[-3]

def test_create_examples_table():
    """Test _create_examples_table function"""
    placeholders = {"param1", "param2"}
    
    result = _create_examples_table(placeholders, "  ")
    
    assert len(result) == 3
    assert "Examples:" in result[0]
    assert "| param1 | param2 |" in result[1]
    assert "<param1_value>" in result[2]

def test_fix_scenario_placeholder_mismatch_no_scenarios():
    """Test fix_scenario_placeholder_mismatch with no scenarios"""
    artefact_text = "Feature: Test\nBackground:\n  Given something"
    
    result = fix_scenario_placeholder_mismatch("file.feature", artefact_text, MagicMock())
    
    assert result == artefact_text

def test_fix_scenario_placeholder_mismatch_with_placeholders():
    """Test fix_scenario_placeholder_mismatch converting to outline"""
    artefact_text = """Feature: Test
Scenario: Test scenario
  Given something with <placeholder>
  When something happens"""
    
    result = fix_scenario_placeholder_mismatch("file.feature", artefact_text, MagicMock())
    
    assert "Scenario Outline:" in result
    assert "Examples:" in result
    assert "<placeholder>" in result

def test_should_skip_issue_non_deterministic_false():
    """Test should_skip_issue when non_deterministic is False"""
    result = should_skip_issue(None, True, False, "file.txt")
    assert result == True

def test_should_skip_issue_deterministic_false():
    """Test should_skip_issue when deterministic is False"""
    result = should_skip_issue("some_issue", False, True, "file.txt")
    assert result == True

def test_should_skip_issue_no_skip():
    """Test should_skip_issue when no skip is needed"""
    result = should_skip_issue("some_issue", True, True, "file.txt")
    assert result == False

def test_determine_attempt_count_single_pass():
    """Test determine_attempt_count with single_pass=True"""
    result = determine_attempt_count(True, "file.txt")
    assert result == 1

def test_determine_attempt_count_multiple_pass():
    """Test determine_attempt_count with single_pass=False"""
    result = determine_attempt_count(False, "file.txt")
    assert result == 3

def test_apply_deterministic_fix_with_issue():
    """Test apply_deterministic_fix when deterministic issue exists"""
    mock_fix_function = MagicMock(return_value="fixed_text")
    deterministic_markers = {"test_issue": mock_fix_function}
    
    result = apply_deterministic_fix(
        True, "test_issue", "file.txt", "original", MagicMock(), 
        {}, deterministic_markers, "corrected"
    )
    
    assert result == "fixed_text"
    mock_fix_function.assert_called_once()

def test_apply_deterministic_fix_no_issue():
    """Test apply_deterministic_fix when no deterministic issue"""
    result = apply_deterministic_fix(
        True, None, "file.txt", "original", MagicMock(), 
        {}, {}, "corrected"
    )
    
    assert result == "corrected"

@patch('ara_cli.artefact_autofix.construct_prompt')
@patch('ara_cli.artefact_autofix.run_agent')
def test_apply_non_deterministic_fix_success(mock_run_agent, mock_construct_prompt):
    """Test apply_non_deterministic_fix successful execution"""
    mock_construct_prompt.return_value = "test prompt"
    mock_artefact = MagicMock()
    mock_artefact.serialize.return_value = "fixed_text"
    mock_run_agent.return_value = mock_artefact
    
    result = apply_non_deterministic_fix(
        True, None, "corrected", MagicMock(), "reason", 
        "file.txt", "original", MagicMock()
    )
    
    assert result == "fixed_text"

def test_apply_non_deterministic_fix_with_deterministic_issue():
    """Test apply_non_deterministic_fix when deterministic issue exists"""
    result = apply_non_deterministic_fix(
        True, "some_issue", "corrected", MagicMock(), "reason", 
        "file.txt", "original", MagicMock()
    )
    
    assert result == "corrected"

@patch('ara_cli.artefact_autofix.construct_prompt')
@patch('ara_cli.artefact_autofix.run_agent', side_effect=Exception("LLM Error"))
def test_apply_non_deterministic_fix_exception(mock_run_agent, mock_construct_prompt, capsys):
    """Test apply_non_deterministic_fix with exception"""
    mock_construct_prompt.return_value = "test prompt"
    
    result = apply_non_deterministic_fix(
        True, None, "corrected", MagicMock(), "reason", 
        "file.txt", "original", MagicMock()
    )
    
    assert result is None
    assert "LLM agent failed" in capsys.readouterr().out

@patch('ara_cli.artefact_autofix.check_file')
@patch('ara_cli.artefact_autofix.read_artefact')
@patch('ara_cli.artefact_autofix.write_corrected_artefact')
@patch('ara_cli.artefact_autofix.populate_classified_artefact_info')
@patch('ara_cli.artefact_autofix.should_skip_issue', return_value=False)
@patch('ara_cli.artefact_autofix.apply_deterministic_fix')
@patch('ara_cli.artefact_autofix.apply_non_deterministic_fix')
def test_attempt_autofix_loop_max_attempts_reached(
    mock_apply_non_det, mock_apply_det, mock_should_skip, mock_populate, 
    mock_write, mock_read, mock_check_file, capsys
):
    """Test attempt_autofix_loop when max attempts are reached"""
    mock_check_file.return_value = (False, "persistent error")
    mock_read.return_value = "original text"
    mock_apply_det.return_value = "modified text"  # Ensure text is modified
    mock_apply_non_det.return_value = "modified text"  # Ensure text is modified
    
    result = attempt_autofix_loop(
        "file.txt", MagicMock(), MagicMock(), {}, 2, True, True, {}
    )
    
    assert result == False
    assert "Failed to fix file.txt after 2 attempts" in capsys.readouterr().out

@patch('ara_cli.artefact_autofix.check_file')
def test_attempt_autofix_loop_already_valid(mock_check_file, capsys):
    """Test attempt_autofix_loop when file is already valid"""
    mock_check_file.return_value = (True, "")
    
    result = attempt_autofix_loop(
        "file.txt", MagicMock(), MagicMock(), {}, 3, True, True, {}
    )
    
    assert result == True
    assert "is now valid" in capsys.readouterr().out

@patch('ara_cli.artefact_autofix.check_file')
@patch('ara_cli.artefact_autofix.read_artefact', return_value=None)
def test_attempt_autofix_loop_read_fails(mock_read, mock_check_file):
    """Test attempt_autofix_loop when reading artefact fails"""
    mock_check_file.return_value = (False, "some error")
    
    result = attempt_autofix_loop(
        "file.txt", MagicMock(), MagicMock(), {}, 3, True, True, {}
    )
    
    assert result == False