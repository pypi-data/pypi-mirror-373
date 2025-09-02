import os
import subprocess
from pathlib import Path
from shutil import copy
from ara_cli.classifier import Classifier
from ara_cli.directory_navigator import DirectoryNavigator
from ara_cli.artefact_models.artefact_templates import template_artefact_of_type


class TemplatePathManager:
    @staticmethod
    def get_template_base_path():
        """Returns the absolute path to the prompt creation templates directory."""
        current_file_path = Path(__file__).absolute()
        base_dir = current_file_path.parent
        return base_dir / "templates"

    @staticmethod
    def get_template_base_path_aspects():
        """Returns the absolute path to the templates directory."""
        current_file_path = Path(__file__).absolute()  # Get current absolute path
        base_dir = current_file_path.parent  # Get directory of current file
        return base_dir / "templates" / "specification_breakdown_files"

    def get_aspect_template_path(self, aspect):
        """Returns the path to the template for the given aspect."""
        base_path = self.get_template_base_path_aspects()
        return [
            (base_path / f"template.{aspect}.md", f"{aspect}.md"),
            (base_path / f"template.{aspect}.exploration.md", f"{aspect}.exploration.md")
        ]

    def get_template_content(self, classifier):
        artefact = template_artefact_of_type(classifier)
        return artefact.serialize()


class ArtefactFileManager:
    def __init__(self):
        self.template_manager = TemplatePathManager()
        self.navigator = DirectoryNavigator()

    def get_artefact_file_path(self, artefact_name, classifier, sub_directory=None):
        if not sub_directory:
            sub_directory = Classifier.get_sub_directory(classifier)
        return os.path.join(sub_directory, f"{artefact_name}.{classifier}")

    def get_data_directory_path(self, artefact_name, classifier, sub_directory=None):
        if not sub_directory:
            sub_directory = Classifier.get_sub_directory(classifier)
        return os.path.join(sub_directory, f"{artefact_name}.data")

    def get_data_directory(self, artefact_name):
        return f"{artefact_name}.data"

    def create_directory(self, artefact_file_path, data_dir):
        # make sure this function is called from the ara top level directory
        self.navigator.navigate_to_target()

        """Creates the data directory if needed and navigates into it."""
        if os.path.isfile(artefact_file_path):
            if not os.path.exists(data_dir):
                os.mkdir(data_dir)
            os.chdir(data_dir)
        else:
            raise ValueError(f"File {artefact_file_path} does not exist. Please create it first.")

    def copy_aspect_templates_to_directory(self, aspect, print_relative_to=""):
        """Copies the templates for the given aspect to the current directory."""
        templates = self.template_manager.get_aspect_template_path(aspect)
        for src, dest in templates:
            if not src.exists():
                raise FileNotFoundError(f"Template file {src} does not exist.")
            copy(src, dest)
            if print_relative_to:
                relative_file_path = os.path.relpath(dest, print_relative_to)
                print(f"Created file: {relative_file_path}")
                continue
            print(f"Created file: {dest}")

    def generate_behave_steps(self, artefact_name):
        self.navigator.navigate_to_target()
        # Clear steps file before executing behave command
        steps_file_path = f"features/steps/{artefact_name}_steps.py"

        behave_command = f"behave features/{artefact_name}.feature"
        result = subprocess.run(behave_command, shell=True, capture_output=True, text=True)

        # Stderr command output needs to be reduced to only given-when-then statements
        if len(result.stderr) == 0:
            return ""
        formatted_result = self.format_behave_command_output(result.stderr)
        return formatted_result

    def format_behave_command_output(self, raw_result):
        # Split the input string by lines
        lines = raw_result.split('\n')

        # Find the first given/when/then and last raise NotImplementedError line
        keywords = ["@given", "@when", "@then"]
        start_index = next(i for i, line in enumerate(lines) if any(keyword in line for keyword in keywords))
        end_index = next(i for i, line in reversed(list(enumerate(lines))) if "raise NotImplementedError" in line)

        # Extract the relevant given-when-then portion
        formatted_code = '\n'.join(lines[start_index:end_index + 1])
        return formatted_code

    def save_behave_steps_to_file(self, artefact_name, behave_steps):
        self.navigator.navigate_to_target()
        file_path = f"features/steps/{artefact_name}_steps.py"
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(behave_steps)


class SpecificationBreakdownAspects:
    VALID_ASPECTS = ['technology', 'concept', 'persona', 'customer', 'step']

    def __init__(self):
        self.file_manager = ArtefactFileManager()

    def validate_input(self, artefact_name, classifier, aspect):
        """Validates the inputs to ensure they're appropriate."""
        if artefact_name in Classifier.valid_classifiers:
            raise ValueError(f"{artefact_name} is not a valid artefact name")

        if not Classifier.is_valid_classifier(classifier) or classifier in self.VALID_ASPECTS:
            raise ValueError(f"{classifier} is not a valid classifier.")

        if aspect not in self.VALID_ASPECTS:
            raise ValueError(f"{aspect} does not exist. Please choose one of the {self.VALID_ASPECTS} list.")


    def create(self, artefact_name='artefact_name', classifier='classifier', aspect='specification_breakdown_aspect'):
        original_directory = os.getcwd()
        navigator = DirectoryNavigator()
        navigator.navigate_to_target()

        self.validate_input(artefact_name, classifier, aspect)
        artefact_file_path = self.file_manager.get_artefact_file_path(artefact_name, classifier)
        data_dir = self.file_manager.get_data_directory_path(artefact_name, classifier)
        self.file_manager.create_directory(artefact_file_path, data_dir)
        self.file_manager.copy_aspect_templates_to_directory(aspect, print_relative_to=original_directory)
        
        if (aspect == "step"):
            # Instead of generating from behave command, read from the template file
            template_file_path = f"{aspect}.md"
            try:
                with open(template_file_path, 'r', encoding='utf-8') as file:
                    steps_content = file.read()
                self.file_manager.save_behave_steps_to_file(artefact_name, steps_content)
            except FileNotFoundError:
                # Fallback to the original behavior if template doesn't exist
                steps = self.file_manager.generate_behave_steps(artefact_name)
                self.file_manager.save_behave_steps_to_file(artefact_name, steps)

        os.chdir(original_directory)