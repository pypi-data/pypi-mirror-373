import os
import shutil
from functools import lru_cache
from ara_cli.template_manager import DirectoryNavigator
from ara_cli.classifier import Classifier
from ara_cli.artefact_link_updater import ArtefactLinkUpdater


class ArtefactDeleter:
    def __init__(self, file_system=None):
        self.file_system = file_system or os
        self.link_updater = ArtefactLinkUpdater()

    @lru_cache(maxsize=None)
    def navigate_to_target(self):
        navigator = DirectoryNavigator()
        navigator.navigate_to_target()

    def delete(self, filename, classifier, force=False):
        self.navigate_to_target()

        if not Classifier.is_valid_classifier(classifier):
            raise ValueError("Invalid classifier provided. Please provide a valid classifier.")

        sub_directory = Classifier.get_sub_directory(classifier)
        file_path = self.file_system.path.join(sub_directory, f"{filename}.{classifier}")
        dir_path = self.file_system.path.join(sub_directory, f"{filename}.data")

        if not self.file_system.path.exists(file_path):
            raise FileNotFoundError(f"Artefact {file_path} not found.")
        if not force:
            user_choice = input(f"Are you sure you want to delete the file {filename} and data directory if existing? (y/N): ")

        if not force and user_choice.lower() != "y":
            print("No changes were made.")
            return

        # Remove references to this artefact in other artefacts before deletion
        self.link_updater.remove_links_in_related_artefacts(filename)

        self.file_system.remove(file_path)
        print(f"Deleted file: {file_path}")

        if not self.file_system.path.exists(dir_path):
            print(f"Directory {dir_path} not found.")

        if self.file_system.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"Deleted directory: {dir_path}")
