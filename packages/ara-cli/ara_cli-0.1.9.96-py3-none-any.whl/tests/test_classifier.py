from ara_cli.classifier import Classifier
import pytest


@pytest.mark.parametrize("classifier, expected", [
    ("vision", "vision"),
    ("businessgoal", "businessgoals"),
    ("capability", "capabilities"),
    ("keyfeature", "keyfeatures"),
    ("epic", "epics"),
    ("userstory", "userstories"),
    ("task", "tasks"),
    ("example", "examples"),
    ("issue", "issues"),
    ("feature", "features"),
    ("nonexistent", None),  # Test for a non-existent classifier
])
def test_get_sub_directory(classifier, expected):
    assert Classifier.get_sub_directory(classifier) == expected


@pytest.mark.parametrize("classifier, expected", [
    ("vision", True),
    ("businessgoal", True),
    ("capability", True),
    ("keyfeature", True),
    ("epic", True),
    ("userstory", True),
    ("task", True),
    ("example", True),
    ("issue", True),
    ("feature", True),
    ("nonexistent", False),  # Test for a non-existent classifier
])
def test_is_valid_classifier(classifier, expected):
    assert Classifier.is_valid_classifier(classifier) == expected


def test_ordered_classifiers():
    expected_classifiers = [
        "vision",
        "businessgoal",
        "capability",
        "keyfeature",
        "epic",
        "userstory",
        "example",
        "feature",
        "task",
        "issue",
    ]
    assert Classifier.ordered_classifiers() == expected_classifiers


@pytest.mark.parametrize("classifier, expected", [
    ("vision", "Vision"),
    ("businessgoal", "Businessgoal"),
    ("capability", "Capability"),
    ("keyfeature", "Keyfeature"),
    ("epic", "Epic"),
    ("userstory", "Userstory"),
    ("task", "Task"),
    ("example", "Example"),
    ("issue", "Issue"),
    ("feature", "Feature"),
    ("nonexistent", None),  # Test for a non-existent classifier
])
def test_get_artefact_title(classifier, expected):
    assert Classifier.get_artefact_title(classifier) == expected
