from . import error_handler
from ara_cli.classifier import Classifier
from ara_cli.file_classifier import FileClassifier
from ara_cli.artefact_models.artefact_model import Artefact
from ara_cli.artefact_models.artefact_load import artefact_from_content
from ara_cli.artefact_fuzzy_search import suggest_close_name_matches_for_parent, suggest_close_name_matches
from typing import Dict, List
import os
import re


class ArtefactReader:
    @staticmethod
    def read_artefact_data(artefact_name, classifier, classified_file_info = None) -> tuple[str, dict[str, str]]:
        if not Classifier.is_valid_classifier(classifier):
            raise ValueError("Invalid classifier provided. Please provide a valid classifier.")

        if not classified_file_info:
            file_classifier = FileClassifier(os)
            classified_file_info = file_classifier.classify_files()
        artefact_info_of_classifier = classified_file_info.get(classifier, [])

        for artefact_info in artefact_info_of_classifier:
            file_path = artefact_info["file_path"]
            artefact_title = artefact_info["title"]
            if artefact_title == artefact_name:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                return content, artefact_info

        all_artefact_names = [info["title"] for info in artefact_info_of_classifier]
        suggest_close_name_matches(
            artefact_name,
            all_artefact_names
        )

        return None, None

    @staticmethod
    def read_artefact(artefact_name, classifier, classified_file_info=None) -> Artefact:
        content, artefact_info = ArtefactReader.read_artefact_data(artefact_name, classifier, classified_file_info)
        if not content or not artefact_info:
            return None
        file_path = artefact_info["file_path"]
        artefact = artefact_from_content(content)
        artefact._file_path = file_path
        return artefact

    @staticmethod
    def extract_parent_tree(artefact_content):
        artefact_titles = Classifier.artefact_titles()
        title_segment = '|'.join(artefact_titles)

        regex_pattern = rf'(?:Contributes to|Illustrates)\s*:*\s*(.*)\s+({title_segment}).*'
        regex = re.compile(regex_pattern)
        match = re.search(regex, artefact_content)
        if not match:
            return None, None

        parent_name = match.group(1).strip()
        parent_type = match.group(2).strip()

        return parent_name, parent_type

    @staticmethod
    def merge_dicts(dict1, dict2):
        from collections import defaultdict

        merged = defaultdict(list)
        for d in [dict1, dict2]:
            for key, artefacts in d.items():
                merged[key].extend(artefacts)
        return dict(merged)

    @staticmethod
    def read_artefacts(classified_artefacts=None, file_system=os, tags=None) -> Dict[str, List[Artefact]]:

        if classified_artefacts is None:
            file_classifier = FileClassifier(file_system)
            classified_artefacts = file_classifier.classify_files()

        artefacts = {artefact_type: []
                     for artefact_type in classified_artefacts.keys()}
        for artefact_type, artefact_info_dicts in classified_artefacts.items():
            for artefact_info in artefact_info_dicts:
                title = artefact_info["title"]
                try:
                    artefact = ArtefactReader.read_artefact(title, artefact_type, classified_artefacts)
                    artefacts[artefact_type].append(artefact)
                except Exception as e:
                    error_handler.report_error(e, f"reading {artefact_type} '{title}'")
                    continue
        return artefacts

    @staticmethod
    def find_children(artefact_name, classifier, artefacts_by_classifier=None, classified_artefacts=None):
        artefacts_by_classifier = artefacts_by_classifier or {}
        filtered_artefacts = {k: [] for k in artefacts_by_classifier.keys()}

        if classified_artefacts is None:
            classified_artefacts = ArtefactReader.read_artefacts()

        for artefact_classifier, artefacts in classified_artefacts.items():
            for artefact in artefacts:
                ArtefactReader._process_artefact(
                    artefact, artefact_name, classifier, filtered_artefacts
                )

        return ArtefactReader.merge_dicts(artefacts_by_classifier, filtered_artefacts)

    @staticmethod
    def _process_artefact(artefact, artefact_name, classifier, filtered_artefacts):
        if not isinstance(artefact, Artefact):
            return
        contribution = getattr(artefact, 'contribution', None)
        if not contribution:
            return
        if getattr(contribution, 'artefact_name', None) != artefact_name:
            return
        if getattr(contribution, 'classifier', None) != classifier:
            return

        file_classifier = getattr(artefact, '_file_path', '').split('.')[-1]
        if file_classifier not in filtered_artefacts:
            filtered_artefacts[file_classifier] = []
        filtered_artefacts[file_classifier].append(artefact)

    @staticmethod
    def step_through_value_chain(
            artefact_name,
            classifier,
            artefacts_by_classifier=None,
            classified_artefacts: dict[str, list['Artefact']] | None = None
    ):
        from ara_cli.artefact_models.artefact_load import artefact_from_content

        artefacts_by_classifier = artefacts_by_classifier or {}

        if classified_artefacts is None:
            classified_artefacts = ArtefactReader.read_artefacts()

        ArtefactReader._ensure_classifier_key(classifier, artefacts_by_classifier)

        artefact = ArtefactReader._find_artefact_by_name(
            artefact_name,
            classified_artefacts.get(classifier, [])
        )

        if not artefact or artefact in artefacts_by_classifier[classifier]:
            return

        artefacts_by_classifier[classifier].append(artefact)

        parent = getattr(artefact, 'contribution', None)
        if not ArtefactReader._has_valid_parent(parent):
            return

        parent_name = parent.artefact_name
        parent_classifier = parent.classifier

        parent_classifier_artefacts = classified_artefacts.get(parent_classifier, [])
        all_artefact_names = [x.title for x in parent_classifier_artefacts]

        if parent_name not in all_artefact_names:
            ArtefactReader._suggest_parent_name_match(
                artefact_name, all_artefact_names, parent_name
            )
            print()
            return

        ArtefactReader.step_through_value_chain(
            artefact_name=parent_name,
            classifier=parent_classifier,
            artefacts_by_classifier=artefacts_by_classifier,
            classified_artefacts=classified_artefacts
        )

    @staticmethod
    def _ensure_classifier_key(classifier, artefacts_by_classifier):
        if classifier not in artefacts_by_classifier:
            artefacts_by_classifier[classifier] = []

    @staticmethod
    def _find_artefact_by_name(artefact_name, artefacts):
        return next((x for x in artefacts if x.title == artefact_name), None)

    @staticmethod
    def _has_valid_parent(parent):
        return parent and getattr(parent, 'artefact_name', None) and getattr(parent, 'classifier', None)

    @staticmethod
    def _suggest_parent_name_match(artefact_name, all_artefact_names, parent_name):
        if parent_name is not None:
            suggest_close_name_matches_for_parent(
                artefact_name,
                all_artefact_names,
                parent_name
            )
