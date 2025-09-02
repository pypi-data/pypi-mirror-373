import pytest
from unittest.mock import patch
from ara_cli.artefact_reader import ArtefactReader


@pytest.mark.parametrize("artefact_content, artefact_titles, expected_output", [
    ("Contributes to: parent_name Example", ["Example"], ("parent_name", "Example")),
    ("Contributes to parent_name Example", ["Example"], ("parent_name", "Example")),
    ("Contributes to : parent_name Feature", ["Example", "Feature"], ("parent_name", "Feature")),
    ("No contribution information here.", ["Example"], (None, None)),
    ("Contributes to : parent_name NotListedTitle", ["Example"], (None, None)),
])
def test_extract_parent_tree(artefact_content, artefact_titles, expected_output):
    with patch('ara_cli.classifier.Classifier.artefact_titles', return_value=artefact_titles):
        parent_name, parent_type = ArtefactReader.extract_parent_tree(artefact_content)
        assert (parent_name, parent_type) == expected_output