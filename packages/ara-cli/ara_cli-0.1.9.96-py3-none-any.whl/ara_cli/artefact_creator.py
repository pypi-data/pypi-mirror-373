import os
from functools import lru_cache
from ara_cli.classifier import Classifier
from ara_cli.template_manager import DirectoryNavigator
from ara_cli.artefact_reader import ArtefactReader
from ara_cli.artefact_models.artefact_model import Artefact
from ara_cli.artefact_models.artefact_templates import template_artefact_of_type
from ara_cli.artefact_fuzzy_search import suggest_close_name_matches
from pathlib import Path
from shutil import copyfile, rmtree


class ArtefactCreator:
    def __init__(self, file_system=None):
        self.file_system = file_system or os

    @lru_cache(maxsize=None)
    def read_template_content(self, template_file_path):
        with open(template_file_path, "r", encoding="utf-8") as template_file:
            return template_file.read()

    def create_artefact_prompt_files(self, dir_path, template_path, classifier):
        if not template_path:
            raise ValueError("template_path must not be None or empty!")

        if not classifier:
            raise ValueError("classifier must not be None or empty!")

        # Standard prompt log artefact
        self._copy_template_file(dir_path, template_path, f"template.{classifier}.prompt_log.md", f"{classifier}.prompt_log.md")

        # Additional prompt log artefact for 'feature' classifier
        if classifier == 'feature':
            self._copy_template_file(dir_path, template_path, "template.steps.prompt_log.md", "steps.prompt_log.md")

    def _copy_template_file(self, dir_path, template_path, source_name, dest_name):
        source = Path(template_path) / source_name
        destination = Path(dir_path) / dest_name

        if not source.exists():
            raise FileNotFoundError(f"Source file {source} not found!")

        if not destination.parent.exists():
            raise NotADirectoryError(f"Destination directory {destination.parent} does not exist!")

        copyfile(source, destination)

    def template_exists(self, template_path, template_name):
        if not template_path:
            return False

        full_path = self.file_system.path.join(template_path, template_name)

        if not self.file_system.path.isfile(full_path):
            print(f"Template file '{template_name}' not found at: {full_path}")
            return False

        return True

    def handle_existing_files(self, file_exists):
        if file_exists:
            user_choice = input("File already exists. Do you want to overwrite the existing file and directory? (y/N): ")
            if user_choice.lower() != "y":
                print("No changes were made to the existing file and directory.")
                return False
        return True

    def validate_template(self, template_path, classifier):
        template_name = f"template.{classifier}"
        if not self.template_exists(template_path, template_name):
            raise FileNotFoundError(f"Template file '{template_name}' not found in the specified template path.")

    def set_artefact_parent(self, artefact, parent_classifier, parent_file_name) -> Artefact:
        classified_artefacts = ArtefactReader.read_artefacts()
        if parent_classifier not in classified_artefacts:
            return artefact
        artefact_list = classified_artefacts[parent_classifier]
        matching_artefacts = list(filter(lambda a: a.file_name == parent_file_name, artefact_list))
        if not matching_artefacts:
            artefact_names_list = [a.file_name for a in artefact_list]
            suggest_close_name_matches(parent_file_name, artefact_names_list)
            return artefact
        artefact._parent = matching_artefacts[0]
        return artefact

    def run(self, filename, classifier, parent_classifier=None, parent_name=None, rule=None):
        # make sure this function is always called from the ara top level directory
        original_directory = os.getcwd()
        navigator = DirectoryNavigator()
        navigator.navigate_to_target()

        if not Classifier.is_valid_classifier(classifier):
            raise ValueError("Invalid classifier provided. Please provide a valid classifier.")

        sub_directory = Classifier.get_sub_directory(classifier)
        file_path = self.file_system.path.join(sub_directory, f"{filename}.{classifier}")
        dir_path = self.file_system.path.join(sub_directory, f"{filename}.data")

        file_exists = self.file_system.path.exists(file_path)

        if not self.handle_existing_files(file_exists):
            return

        artefact = template_artefact_of_type(classifier, filename, True)

        if parent_classifier and parent_name:
            artefact.set_contribution(
                artefact_name=parent_name,
                classifier=parent_classifier,
                rule=rule
            )
        else:
            artefact.set_contribution(None, None, None)

        artefact_content = artefact.serialize()
        rmtree(dir_path, ignore_errors=True)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as artefact_file:
            artefact_file.write(artefact_content)

        relative_file_path = os.path.relpath(file_path, original_directory)
        relative_dir_path = os.path.relpath(dir_path, original_directory)

        os.chdir(original_directory)

        print(f"Created file: {relative_file_path}")
        print(f"Created directory: {relative_dir_path}")

    def get_title(self, file_path, classifier):
        """
        Extract the title from the file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Parent file {file_path} not found!")

        title = Classifier.get_artefact_title(classifier)

        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                if line.strip().startswith(title):
                    return line.split(':')[1].strip()

        raise ValueError(f"Title not found in the parent file {file_path}")
