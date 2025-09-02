from functools import lru_cache


class Classifier:
    valid_classifiers = {
        "vision": "vision",
        "businessgoal": "businessgoals",
        "capability": "capabilities",
        "keyfeature": "keyfeatures",
        "feature": "features",
        "epic": "epics",
        "userstory": "userstories",
        "task": "tasks",
        "example": "examples",
        "issue": "issues",
    }

    classifier_order = [
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

    artefact_title = {
        "vision": "Vision",
        "businessgoal": "Businessgoal",
        "capability": "Capability",
        "keyfeature": "Keyfeature",
        "epic": "Epic",
        "userstory": "Userstory",
        "example": "Example",
        "feature": "Feature",
        "task": "Task",
        "issue": "Issue"
    }

    artefact_reverse_title = dict((v, k) for k, v in artefact_title.items())

    @staticmethod
    @lru_cache(maxsize=None)
    def get_sub_directory(classifier):
        return Classifier.valid_classifiers.get(classifier)

    @staticmethod
    @lru_cache(maxsize=None)
    def is_valid_classifier(classifier):
        return classifier in Classifier.valid_classifiers

    @staticmethod
    @lru_cache(maxsize=None)
    def ordered_classifiers():
        return Classifier.classifier_order

    @staticmethod
    @lru_cache(maxsize=None)
    def get_artefact_title(classifier):
        return Classifier.artefact_title.get(classifier)

    @staticmethod
    @lru_cache(maxsize=None)
    def get_artefact_classifier(title):
        return Classifier.artefact_reverse_title.get(title)

    @staticmethod
    @lru_cache(maxsize=None)
    def artefact_titles():
        return Classifier.artefact_title.values()
