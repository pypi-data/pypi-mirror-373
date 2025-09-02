from . import error_handler
from ara_cli.classifier import Classifier
from ara_cli.artefact_models.artefact_model import Artefact
from ara_cli.artefact_fuzzy_search import find_closest_name_matches
from functools import lru_cache
from typing import Optional
import textwrap
import os


class FileClassifier:
    def __init__(self, file_system):
        self.file_system = file_system

    def find_closest_artefact_name_match(self, name, classifier) -> Optional[str]:
        classified_artefacts = self.classify_files()
        all_artefact_names = [
            info["title"] for info in classified_artefacts.get(classifier, [])]
        if name in all_artefact_names:
            return name
        return find_closest_name_matches(name, all_artefact_names)

    @lru_cache(maxsize=None)
    def read_file_content(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def is_binary_file(self, file_path):
        # Heuristic check to determine if a file is binary.
        # This is not foolproof but can help in most cases.
        try:
            with open(file_path, 'rb') as f:
                for byte in f.read(1024):
                    if byte > 127:
                        return True
        except Exception as e:
            error_handler.report_error(e, "checking if file is binary")
            # print(f"Error while checking if file is binary: {e}")
        return False

    def read_file_with_fallback(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                # Try reading with a different encoding if utf-8 fails
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except UnicodeDecodeError:
                # Skip the file if it still fails
                return None

    def file_contains_tags(self, file_path, tags):
        content = self.read_file_with_fallback(file_path)
        if content is None:
            return False
        return all(tag in content for tag in tags)

    def classify_file(self, file_path, tags):
        if tags and (self.is_binary_file(file_path) or not self.file_contains_tags(file_path, tags)):
            return None
        for classifier in Classifier.ordered_classifiers():
            if file_path.endswith(f".{classifier}"):
                return classifier
        return None

    def classify_files(self, tags=None) -> dict[str, list[dict]]:
        files_by_classifier = {classifier: [] for classifier in Classifier.ordered_classifiers()}

        for root, _, files in self.file_system.walk("."):
            if root.endswith(".data") or root.endswith("templates"):
                continue
            for file in files:
                file_path = self.file_system.path.join(root, file)
                classifier = self.classify_file(file_path, tags)
                if not classifier:
                    # no return
                    continue

                file_info = {"file_path": file_path, "title": '.'.join(file.split('.')[:-1])}

                files_by_classifier[classifier].append(file_info)
                continue

        return files_by_classifier

    def print_artefact_list(self, artefacts: list[Artefact], print_content=False):
        for artefact in artefacts:
            print(f"  - ./{os.path.relpath(artefact.file_path, os.getcwd())}")
            if print_content:
                indented_content = textwrap.indent(artefact.serialize(), prefix="      ")
                print(f"    Content:\n{indented_content}")

    def print_classified_files(self, files_by_classifier, print_content=False):
        for classifier, files in files_by_classifier.items():
            if not files:
                continue
            print(f"{Classifier.get_artefact_title(classifier)} files:")
            self.print_artefact_list(files, print_content)
            print()
