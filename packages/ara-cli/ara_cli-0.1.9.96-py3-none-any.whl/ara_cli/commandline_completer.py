from ara_cli.classifier import Classifier
from ara_cli.directory_navigator import DirectoryNavigator
import os


def find_classified_artefacts(prefix, classifier):
    navigator = DirectoryNavigator()
    navigator.navigate_to_target()
    subdirectory = Classifier.get_sub_directory(classifier)

    classifier_length = len(classifier)

    if os.path.isdir(subdirectory):
        files = os.listdir(subdirectory)
        return [file[:-classifier_length-1] for file in files if file.startswith(prefix) and file.endswith(f".{classifier}")]
    return []


class ArtefactCompleter:
    def __call__(self, prefix, parsed_args, **kwargs):
        classifier = parsed_args.classifier

        return find_classified_artefacts(prefix, classifier)


class ParentNameCompleter:
    def __call__(self, prefix, parsed_args, **kwargs):
        classifier = parsed_args.parent_classifier

        return find_classified_artefacts(prefix, classifier)


class StatusCompleter:
    def __call__(self, prefix, parsed_args, **kwargs):
        status_tags = [
            "to-do",
            "in-progress",
            "review",
            "done",
            "closed"
        ]
        return status_tags
