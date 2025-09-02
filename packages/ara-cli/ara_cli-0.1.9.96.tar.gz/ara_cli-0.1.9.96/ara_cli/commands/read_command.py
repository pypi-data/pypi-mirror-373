from ara_cli.commands.command import Command
from ara_cli.artefact_reader import ArtefactReader
from ara_cli.file_classifier import FileClassifier
from ara_cli.list_filter import ListFilter, filter_list
from ara_cli.artefact_models.artefact_data_retrieval import (
    artefact_content_retrieval, 
    artefact_path_retrieval, 
    artefact_tags_retrieval
)
from ara_cli.artefact_fuzzy_search import suggest_close_name_matches
import os


class ReadCommand(Command):
    def __init__(
        self,
        classifier: str,
        artefact_name: str,
        read_mode: str = "default",
        list_filter: ListFilter = None,
        output=None
    ):
        self.classifier = classifier
        self.artefact_name = artefact_name
        self.read_mode = read_mode
        self.list_filter = list_filter or ListFilter()
        self.output = output or print

    def execute(self) -> bool:
        """Execute the read command and return success status."""
        file_classifier = FileClassifier(os)
        classified_artefacts = ArtefactReader.read_artefacts()
        artefacts = classified_artefacts.get(self.classifier, [])
        all_artefact_names = [a.title for a in artefacts]

        if self.artefact_name not in all_artefact_names:
            suggest_close_name_matches(
                self.artefact_name,
                all_artefact_names
            )
            return False

        target_artefact = next(filter(
            lambda x: x.title == self.artefact_name, artefacts
        ))

        artefacts_by_classifier = {self.classifier: []}

        try:
            match self.read_mode:
                case "branch":
                    self._handle_branch_mode(
                        classified_artefacts, artefacts_by_classifier
                    )
                case "children":
                    artefacts_by_classifier = self._handle_children_mode(
                        classified_artefacts
                    )
                case _:
                    self._handle_default_mode(
                        target_artefact, artefacts_by_classifier
                    )

            # Apply filtering and print results
            filtered_artefacts = self._apply_filtering(artefacts_by_classifier)
            file_classifier.print_classified_files(
                filtered_artefacts, print_content=True
            )
            return True

        except Exception as e:
            self.output(f"Error reading artefact: {e}")
            return False

    def _handle_branch_mode(self, classified_artefacts, artefacts_by_classifier):
        """Handle branch read mode."""
        ArtefactReader.step_through_value_chain(
            artefact_name=self.artefact_name,
            classifier=self.classifier,
            artefacts_by_classifier=artefacts_by_classifier,
            classified_artefacts=classified_artefacts
        )

    def _handle_children_mode(self, classified_artefacts):
        """Handle children read mode."""
        return ArtefactReader.find_children(
            artefact_name=self.artefact_name,
            classifier=self.classifier,
            classified_artefacts=classified_artefacts
        )

    def _handle_default_mode(self, target_artefact, artefacts_by_classifier):
        """Handle default read mode."""
        artefacts_by_classifier[self.classifier].append(target_artefact)

    def _apply_filtering(self, artefacts_by_classifier):
        """Apply list filtering to artefacts."""
        return filter_list(
            list_to_filter=artefacts_by_classifier,
            list_filter=self.list_filter,
            content_retrieval_strategy=artefact_content_retrieval,
            file_path_retrieval=artefact_path_retrieval,
            tag_retrieval=artefact_tags_retrieval
        )
