# artefact_link_updater.py
import os
import re
from ara_cli.classifier import Classifier
from functools import lru_cache


class ArtefactLinkUpdater:
    def __init__(self, file_system=None):
        self.file_system = file_system or os

    @lru_cache(maxsize=None)
    def compile_pattern(self, pattern):
        return re.compile(pattern, re.IGNORECASE | re.MULTILINE)

    def update_links_in_related_artefacts(self, old_name, new_name, dir_path='.'):
        new_name_formatted = new_name.replace('_', ' ')
        old_name_pattern = re.compile(f"\\b{old_name.replace(' ', '[ _]').replace('_', '[ _]')}\\b", re.IGNORECASE)

        patterns = {
            self.compile_pattern(f"^(\\s*)Contributes to[ ]+([A-Za-z ]+)?{old_name_pattern.pattern}"): r"\1Contributes to \2" + new_name_formatted,
            self.compile_pattern(f"^(\\s*)Illustrates[ ]+([A-Za-z ]+)?{old_name_pattern.pattern}"): r"\1Illustrates \2" + new_name_formatted
        }

        # Iterate over all items in the directory
        for item in self.file_system.listdir(dir_path):
            item_path = self.file_system.path.join(dir_path, item)
            extension = os.path.splitext(item)[-1][1:]

            # Check if it's a directory, then recurse
            if self.file_system.path.isdir(item_path):
                self.update_links_in_related_artefacts(old_name, new_name, item_path)

            # Check if it's a file and not a directory
            elif self.file_system.path.isfile(item_path) and Classifier.is_valid_classifier(extension):
                # Read the content of the file
                with open(item_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                # Replace all occurrences of the old name with the new name using regular expressions
                for pattern, replacement in patterns.items():
                    content = pattern.sub(replacement, content)

                # Write the updated content back to the file
                with open(item_path, 'w', encoding='utf-8') as file:
                    file.write(content)

    def remove_links_in_related_artefacts(self, artefact_name, dir_path="."):
        artefact_name_pattern = re.compile(rf"\b{re.escape(artefact_name)}\b", re.IGNORECASE)

        # Pattern for removing the artefact name from 'Contributes to' lines
        contribute_pattern = re.compile(rf"^(Contributes to).*{artefact_name_pattern.pattern}.*$", re.IGNORECASE | re.MULTILINE)

        # Pattern for removing the artefact name from 'Illustrates' lines (no colon)
        illustrates_pattern = re.compile(rf"^(Illustrates).*{artefact_name_pattern.pattern}.*$", re.IGNORECASE | re.MULTILINE)

        # Iterate over all items in the directory
        for item in self.file_system.listdir(dir_path):
            item_path = self.file_system.path.join(dir_path, item)
            extension = os.path.splitext(item)[-1][1:]

            # Check if it's a directory, then recurse
            if self.file_system.path.isdir(item_path):
                self.remove_links_in_related_artefacts(artefact_name, item_path)

            # Check if it's a file and not a directory, and if extension is a valid artefact classifier
            elif self.file_system.path.isfile(item_path) and Classifier.is_valid_classifier(extension):
                with open(item_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                # Remove the artefact name from 'Contributes to' and 'Illustrates' lines
                content = contribute_pattern.sub("Contributes to", content)
                content = illustrates_pattern.sub("Illustrates", content)

                with open(item_path, 'w', encoding='utf-8') as file:
                    file.write(content)
