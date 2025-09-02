from textwrap import indent
import os


def is_contribution_valid(contribution, classified_artefact_info) -> bool:
    from ara_cli.artefact_fuzzy_search import extract_artefact_names_of_classifier
    if not contribution or not contribution.artefact_name or not contribution.classifier:
        return True

    all_artefact_names = extract_artefact_names_of_classifier(
        classified_files=classified_artefact_info,
        classifier=contribution.classifier
    )
    if contribution.artefact_name not in all_artefact_names:
        return False
    return True


def is_rule_valid(contribution, classified_artefact_info) -> bool:
    from ara_cli.artefact_reader import ArtefactReader

    if not contribution or not contribution.artefact_name or not contribution.classifier:
        return True
    rule = contribution.rule
    if not rule:
        return True
    parent = ArtefactReader.read_artefact(contribution.artefact_name, contribution.classifier)
    if not parent or not parent.rules:
        return True
    rules = parent.rules
    if rule not in rules:
        return False
    return True


def check_contribution(contribution, classified_artefact_info, file_path) -> tuple[bool, str]:
    if not contribution:
        return True, None

    if not is_contribution_valid(contribution, classified_artefact_info):
        reason = (f"Invalid Contribution Reference: The contribution references "
                  f"'{contribution.classifier}' artefact '{contribution.artefact_name}' "
                  f"which does not exist.")
        return False, reason

    if not is_rule_valid(contribution, classified_artefact_info):
        reason = (f"Rule Mismatch: The contribution references "
                  f"rule '{contribution.rule}' which the parent "
                  f"{contribution.classifier} '{contribution.artefact_name}' does not have.")
        return False, reason
    return True, None


def check_file(file_path, artefact_class, classified_artefact_info=None):
    from pydantic import ValidationError
    from ara_cli.file_classifier import FileClassifier

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        return False, f"File error: {e}"

    if not classified_artefact_info:
        file_classifier = FileClassifier(os)
        classified_artefact_info = file_classifier.classify_files()

    try:
        artefact_instance = artefact_class.deserialize(content)

        base_name = os.path.basename(file_path)
        file_name_without_ext, _ = os.path.splitext(base_name)

        # Check title and file name matching
        if artefact_instance.title != file_name_without_ext:
            reason = (f"Filename-Title Mismatch: The file name '{file_name_without_ext}' "
                      f"does not match the artefact title '{artefact_instance.title}'.")
            return False, reason

        contribution = artefact_instance.contribution

        contribution_valid, reason = check_contribution(contribution, classified_artefact_info, file_path)
        if not contribution_valid:
            return False, reason

        return True, None
    except (ValidationError, ValueError, AssertionError) as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {e!r}"


def find_invalid_files(classified_artefact_info, classifier):
    from ara_cli.artefact_models.artefact_mapping import artefact_type_mapping

    artefact_class = artefact_type_mapping[classifier]
    invalid_files = []
    for artefact_info in classified_artefact_info[classifier]:
        if "templates/" in artefact_info["file_path"]:
            continue
        if ".data" in artefact_info["file_path"]:
            continue
        is_valid, reason = check_file(artefact_info["file_path"], artefact_class, classified_artefact_info)
        if not is_valid:
            invalid_files.append((artefact_info["file_path"], reason))
    return invalid_files


def show_results(invalid_artefacts):
    has_issues = False
    with open("incompatible_artefacts_report.md", "w", encoding="utf-8") as report:
        report.write("# Artefact Check Report\n\n")
        for classifier, files in invalid_artefacts.items():
            if files:
                has_issues = True
                print(f"\nIncompatible {classifier} Files:")
                report.write(f"## {classifier}\n")
                for file, reason in files:
                    indented_reason = indent(reason, prefix="\t\t")
                    print(f"\t- {file}\n{indented_reason}")
                    report.write(f"- `{file}`: {reason}\n")
                report.write("\n")
        if not has_issues:
            print("All files are good!")
            report.write("No problems found.\n")