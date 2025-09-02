import pytest
from unittest.mock import patch, call
from ara_cli.artefact_fuzzy_search import suggest_close_name_matches


@pytest.mark.parametrize("artefact_name, all_artefact_names, expected_output", [
    ("artefact1", ["artefact2", "artefact3"], ["No match found for artefact with name 'artefact1'"]),
    ("artefact1", ["artefact1", "artefact2"], [
        "No match found for artefact with name 'artefact1'",
        "Closest matches:",
        "  - artefact1",
        "  - artefact2"
    ]),
    ("artefact", ["artefac", "artefacto", "artifact"], [
        "No match found for artefact with name 'artefact'",
        "Closest matches:",
        "  - artefacto",
        "  - artefac",
        "  - artifact"
    ]),
    ("no_match", [], ["No match found for artefact with name 'no_match'"])
])
@patch('builtins.print')
def test_suggest_close_name_matches(mock_print, artefact_name, all_artefact_names, expected_output):
    # Call the method under test
    suggest_close_name_matches(artefact_name, all_artefact_names)

    # Prepare the expected calls
    expected_calls = [call(line) for line in expected_output]

    # Verify that print was called with the expected sequence of outputs
    mock_print.assert_has_calls(expected_calls, any_order=False)