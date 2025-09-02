import difflib
from textwrap import indent
from typing import Optional
from . import error_handler
from ara_cli.error_handler import AraError


def suggest_close_names(artefact_name: str, all_artefact_names: list[str], message: str, cutoff=0.5, report_as_error: bool = False):
    closest_matches = difflib.get_close_matches(artefact_name, all_artefact_names, cutoff=cutoff)
    if report_as_error:
        error_handler.report_error(AraError(message))
    else:
        print(message)
    if not closest_matches:
        return
    print("Closest matches:")
    for match in closest_matches:
        print(f"  - {match}")


def suggest_close_name_matches(artefact_name: str, all_artefact_names: list[str], report_as_error: bool = False):
    message = f"No match found for artefact with name '{artefact_name}'"

    suggest_close_names(
        artefact_name=artefact_name,
        all_artefact_names=all_artefact_names,
        message=message,
        report_as_error=report_as_error
    )


def suggest_close_name_matches_for_parent(artefact_name: str, all_artefact_names: list[str], parent_name: str, report_as_error: bool = False):
    message = f"No match found for parent of '{artefact_name}' with name '{parent_name}'"

    suggest_close_names(
        artefact_name=parent_name,
        all_artefact_names=all_artefact_names,
        message=message,
        report_as_error=report_as_error
    )


def find_closest_name_matches(artefact_name: str, all_artefact_names: list[str]) -> Optional[str]:
    closest_matches = difflib.get_close_matches(artefact_name, all_artefact_names, cutoff=0.5)
    if not closest_matches:
        return None
    return closest_matches


def extract_artefact_names_of_classifier(classified_files: dict[str, list[dict]], classifier: str):
    artefact_info_of_classifier = classified_files.get(classifier, [])
    titles = list(map(lambda artefact: artefact['title'], artefact_info_of_classifier))
    return titles


def find_closest_rule(parent_artefact: 'Artefact', rule: str):
    parent_classifier = parent_artefact.artefact_type.value
    parent_title = parent_artefact.title
    if not hasattr(parent_artefact, 'rules'):
        raise TypeError(f"{parent_classifier.capitalize()} artefact '{parent_title}' can not possess rules. Only userstories and epics have rules.")
    rules = parent_artefact.rules
    if rule in rules:
        return rule
    print(f"Rule '{rule}' does not match existing rules in {parent_classifier} artefact '{parent_title}'. Attempting to find closest match among existing rules.")
    closest_matches = difflib.get_close_matches(rule, rules, cutoff=0.5)
    rules_list_string = indent('\n'.join(rules), prefix='\t- ')
    if not closest_matches:
        raise ValueError(f"Can not determine a match for rule '{rule}' in {parent_classifier} artefact '{parent_title}'. Found rules:\n{rules_list_string}")
    closest_match = closest_matches[0]
    print(f"Found closest matching rule of '{closest_match}'")
    return closest_match
