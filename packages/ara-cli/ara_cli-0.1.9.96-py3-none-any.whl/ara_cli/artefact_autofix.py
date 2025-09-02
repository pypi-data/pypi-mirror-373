from ara_cli.error_handler import AraError
from ara_cli.artefact_scan import check_file
from ara_cli.artefact_fuzzy_search import (
    find_closest_name_matches,
    extract_artefact_names_of_classifier,
)
from ara_cli.file_classifier import FileClassifier
from ara_cli.artefact_reader import ArtefactReader
from ara_cli.artefact_models.artefact_load import artefact_from_content
from ara_cli.artefact_models.artefact_model import Artefact
from typing import Optional, Dict, List, Tuple
import difflib
import os
import re


def populate_classified_artefact_info(
    classified_artefact_info: Optional[dict], force: bool = False
):
    if not classified_artefact_info or force:
        file_classifier = FileClassifier(os)
        classified_artefact_info = file_classifier.classify_files()
    return classified_artefact_info


def read_report_file():
    file_path = "incompatible_artefacts_report.md"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        print(
            'Artefact scan results file not found. Did you run the "ara scan" command?'
        )
        return None
    return content


def parse_report(content: str) -> Dict[str, List[Tuple[str, str]]]:
    """
    Parses the incompatible artefacts report and returns structured data.
    Returns a dictionary where keys are artefact classifiers, and values are lists of (file_path, reason) tuples.
    """

    def is_valid_report(lines: List[str]) -> bool:
        return bool(lines) and lines[0] == "# Artefact Check Report"

    def has_no_problems(lines: List[str]) -> bool:
        return len(lines) >= 3 and lines[2] == "No problems found."

    def parse_classifier(line: str) -> Optional[str]:
        if line.startswith("## "):
            return line[3:].strip()
        return None

    def parse_issue(line: str) -> Optional[Tuple[str, str]]:
        if not line.startswith("- "):
            return None
        parts = line.split("`", 2)
        if len(parts) < 3:
            return None
        file_path = parts[1]
        reason = parts[2].split(":", 1)[1].strip() if ":" in parts[2] else ""
        return file_path, reason

    lines = content.splitlines()
    if not is_valid_report(lines) or has_no_problems(lines):
        return {}

    issues = {}
    current_classifier = None

    for line in map(str.strip, lines[1:]):
        if not line:
            continue
        classifier = parse_classifier(line)
        if classifier is not None:
            current_classifier = classifier
            issues[current_classifier] = []
            continue
        issue = parse_issue(line)
        if issue and current_classifier is not None:
            issues[current_classifier].append(issue)
    return issues


def read_artefact(file_path):
    """Reads the artefact text from the given file path."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None


def determine_artefact_type_and_class(classifier):
    from ara_cli.artefact_models.artefact_mapping import artefact_type_mapping
    from ara_cli.artefact_models.artefact_model import ArtefactType

    try:
        artefact_type = ArtefactType(classifier)
    except ValueError:
        print(f"Invalid classifier: {classifier}")
        return None, None

    artefact_class = artefact_type_mapping.get(artefact_type)
    if not artefact_class:
        raise AraError(f"No artefact class found for {artefact_type}")
        # print(f"No artefact class found for {artefact_type}")
        # return None, None

    return artefact_type, artefact_class


def construct_prompt(artefact_type, reason, file_path, artefact_text):
    from ara_cli.artefact_models.artefact_model import ArtefactType

    prompt = (
        f"Correct the following {artefact_type.value} artefact to fix the issue: {reason}. "
        "Provide the corrected artefact. Do not reformulate the artefact, "
        "just fix the pydantic model errors, use correct grammar. "
        "You should follow the name of the file "
        f"from its path {file_path} for naming the artefact's title. "
        "You are not allowed to use file extention in the artefact title. "
        "You are not allowed to modify, delete or add tags. "
        "User tag should be '@user_<username>'. The pydantic model already provides the '@user_' prefix. "
        "So you should be careful to not make it @user_user_<username>. "
    )

    if artefact_type == ArtefactType.task:
        prompt += (
            "For task artefacts, if the action items looks like template or empty "
            "then just delete those action items."
        )

    prompt += "\nThe current artefact is:\n" "```\n" f"{artefact_text}\n" "```"

    return prompt


def run_agent(prompt, artefact_class):
    from pydantic_ai import Agent

    # gpt-4o
    # anthropic:claude-3-7-sonnet-20250219
    # anthropic:claude-4-sonnet-20250514
    agent = Agent(
        model="anthropic:claude-4-sonnet-20250514",
        output_type=artefact_class,
        instrument=True,
    )
    result = agent.run_sync(prompt)
    return result.output


def write_corrected_artefact(file_path, corrected_text):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(corrected_text)
    print(f"Fixed artefact at {file_path}")


def ask_for_correct_contribution(
    artefact_info: Optional[tuple[str, str]] = None
) -> tuple[str, str]:
    """
    Ask the user to provide a valid contribution when no match can be found.

    Args:
        artefact_info: Optional tuple containing (artefact_name, artefact_classifier)

    Returns:
        A tuple of (name, classifier) for the contribution
    """

    artefact_name, artefact_classifier = (
        artefact_info if artefact_info else (None, None)
    )
    contribution_message = (
        f"of {artefact_classifier} artefact '{artefact_name}'" if artefact_name else ""
    )

    print(
        f"Can not determine a match for contribution {contribution_message}. "
        f"Please provide a valid contribution or contribution will be empty ([classifier] [file_name])."
    )

    user_input = input().strip()

    if not user_input:
        return None, None

    parts = user_input.split(maxsplit=1)
    if len(parts) != 2:
        print("Invalid input format. Expected: <classifier> <file_name>")
        return None, None

    classifier, name = parts
    return name, classifier


def ask_for_contribution_choice(choices: List[str], artefact_info: Optional[tuple[str, str]] = None) -> Optional[str]:
    artefact_name, artefact_classifier = artefact_info if artefact_info else (None, None)
    message = "Found multiple close matches for the contribution"
    if artefact_name and artefact_classifier:
        message += f" of the {artefact_classifier} '{artefact_name}'"
    message += "."
    return get_user_choice(choices, message)


def _has_valid_contribution(artefact: Artefact) -> bool:
    contribution = artefact.contribution
    return contribution and contribution.artefact_name and contribution.classifier


def get_user_choice(choices: List[str], message: str) -> Optional[str]:
    """
    Generic function to present user with a list of choices and return their selection.

    Args:
        choices: A list of strings representing the choices to display.
        message: A message to display before listing the choices.

    Returns:
        The chosen item from the list or None if the input was invalid.
    """
    print(message)
    for i, choice in enumerate(choices):
        print(f"{i + 1}: {choice}")

    choice_number = input("Please enter your choice (number): ")

    try:
        choice_index = int(choice_number) - 1
        if choice_index < 0 or choice_index >= len(choices):
            print("Invalid choice. Aborting operation.")
            return None
        return choices[choice_index]
    except ValueError:
        print("Invalid input. Aborting operation.")
        return None


def ask_for_rule_choice(matches: List[str]) -> Optional[str]:
    """Asks the user for a choice between multiple rule matches"""
    message = "Multiple rule matches found:"
    return get_user_choice(matches, message)


def _update_rule(
    artefact: Artefact, name: str, classifier: str, classified_file_info: dict, delete_if_not_found: bool = False
) -> None:
    """Updates the rule in the contribution if a close match is found."""
    rule = artefact.contribution.rule

    content, artefact_data = ArtefactReader.read_artefact_data(
        artefact_name=name,
        classifier=classifier,
        classified_file_info=classified_file_info,
    )

    parent = artefact_from_content(content=content)
    rules = parent.rules

    closest_rule_match = difflib.get_close_matches(rule, rules, cutoff=0.5)
    if not closest_rule_match and delete_if_not_found:
        artefact.contribution.rule = None
        return
    if not closest_rule_match:
        return
    if len(closest_rule_match) > 1:
        artefact.contribution.rule = ask_for_rule_choice(closest_rule_match)
        return
    artefact.contribution.rule = closest_rule_match[0]


def _set_contribution_multiple_matches(
    artefact: Artefact,
    closest_matches: list,
    artefact_tuple: tuple,
    classified_file_info: dict,
) -> tuple[Artefact, bool]:
    contribution = artefact.contribution
    classifier = contribution.classifier
    original_name = contribution.artefact_name

    closest_match = closest_matches[0]
    if len(closest_matches) > 1:
        closest_match = ask_for_contribution_choice(closest_matches, artefact_tuple)

    if not closest_match:
        print(
            f"Contribution of {artefact_tuple[1]} '{artefact_tuple[0]}' will be empty."
        )
        artefact.contribution = None
        return artefact, True

    print(
        f"Updating contribution of {artefact_tuple[1]} '{artefact_tuple[0]}' to {classifier} '{closest_match}'"
    )
    contribution.artefact_name = closest_match
    artefact.contribution = contribution

    if contribution.rule:
        _update_rule(artefact, original_name, classifier, classified_file_info)

    return artefact, True


def set_closest_contribution(
    artefact: Artefact, classified_file_info=None
) -> tuple[Artefact, bool]:
    if not _has_valid_contribution(artefact):
        return artefact, False
    contribution = artefact.contribution
    name = contribution.artefact_name
    classifier = contribution.classifier
    rule = contribution.rule

    classified_file_info = populate_classified_artefact_info(classified_artefact_info=classified_file_info)

    all_artefact_names = extract_artefact_names_of_classifier(
        classified_files=classified_file_info, classifier=classifier
    )
    closest_matches = find_closest_name_matches(
        artefact_name=name, all_artefact_names=all_artefact_names
    )

    artefact_tuple = (artefact.title, artefact._artefact_type().value)

    if not closest_matches:
        name, classifier = ask_for_correct_contribution(artefact_tuple)
        if not name or not classifier:
            artefact.contribution = None
            return artefact, True
        print(
            f"Updating contribution of {artefact._artefact_type().value} '{artefact.title}' to {classifier} '{name}'"
        )
        contribution.artefact_name = name
        contribution.classifier = classifier
        artefact.contribution = contribution
        return artefact, True

    if closest_matches[0] == name:
        return artefact, False

    return _set_contribution_multiple_matches(
        artefact=artefact,
        closest_matches=closest_matches,
        artefact_tuple=artefact_tuple,
        classified_file_info=classified_file_info,
    )

    print(
        f"Updating contribution of {artefact._artefact_type().value} '{artefact.title}' to {classifier} '{closest_match}'"
    )
    contribution.artefact_name = closest_match
    artefact.contribution = contribution

    if not rule:
        return artefact, True

    content, artefact = ArtefactReader.read_artefact_data(
        artefact_name=name,
        classifier=classifier,
        classified_file_info=classified_file_info,
    )
    parent = artefact_from_content(content=content)
    rules = parent.rules

    closest_rule_match = difflib.get_close_matches(rule, rules, cutoff=0.5)
    if closest_rule_match:
        contribution.rule = closest_rule_match
        artefact.contribution = contribution
    return artefact, True


def fix_scenario_placeholder_mismatch(
    file_path: str, artefact_text: str, artefact_class, **kwargs
) -> str:
    """
    Converts a regular Scenario with placeholders to a Scenario Outline.
    This is a deterministic fix that detects placeholders and converts the format.
    """
    lines = artefact_text.splitlines()
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped_line = line.strip()
        
        if stripped_line.startswith('Scenario:'):
            scenario_lines, next_index = _extract_scenario_block(lines, i)
            processed_lines = _process_scenario_block(scenario_lines)
            new_lines.extend(processed_lines)
            i = next_index
        else:
            new_lines.append(line)
            i += 1
    
    return "\n".join(new_lines)


def _extract_scenario_block(lines: list, start_index: int) -> tuple[list, int]:
    """Extract all lines belonging to a scenario block."""
    scenario_lines = [lines[start_index]]
    j = start_index + 1
    
    while j < len(lines):
        next_line = lines[j].strip()
        if _is_scenario_boundary(next_line):
            break
        scenario_lines.append(lines[j])
        j += 1
    
    return scenario_lines, j


def _is_scenario_boundary(line: str) -> bool:
    """Check if a line marks the boundary of a scenario block."""
    boundaries = ['Scenario:', 'Scenario Outline:', 'Background:', 'Feature:']
    return any(line.startswith(boundary) for boundary in boundaries)


def _process_scenario_block(scenario_lines: list) -> list:
    """Process a scenario block and convert to outline if placeholders are found."""
    if not scenario_lines:
        return scenario_lines
    
    first_line = scenario_lines[0]
    indentation = _get_line_indentation(first_line)
    placeholders = _extract_placeholders_from_scenario(scenario_lines[1:])
    
    if not placeholders:
        return scenario_lines
    
    return _convert_to_scenario_outline(scenario_lines, placeholders, indentation)


def _get_line_indentation(line: str) -> str:
    """Get the indentation of a line."""
    return line[:len(line) - len(line.lstrip())]


def _extract_placeholders_from_scenario(step_lines: list) -> set:
    """Extract placeholders from scenario step lines, ignoring docstrings."""
    placeholders = set()
    in_docstring = False
    
    for line in step_lines:
        step_line = line.strip()
        if not step_line:
            continue
            
        in_docstring = _update_docstring_state(step_line, in_docstring)
        
        if not in_docstring and '"""' not in step_line:
            found = re.findall(r'<([^>]+)>', step_line)
            placeholders.update(found)
    
    return placeholders


def _update_docstring_state(line: str, current_state: bool) -> bool:
    """Update the docstring state based on the current line."""
    if '"""' in line:
        return not current_state
    return current_state


def _convert_to_scenario_outline(scenario_lines: list, placeholders: set, indentation: str) -> list:
    """Convert scenario lines to scenario outline format with examples table."""
    first_line = scenario_lines[0]
    title = first_line.strip()[len('Scenario:'):].strip()
    
    new_lines = [f"{indentation}Scenario Outline: {title}"]
    new_lines.extend(scenario_lines[1:])
    new_lines.append("")
    
    examples_lines = _create_examples_table(placeholders, indentation)
    new_lines.extend(examples_lines)
    
    return new_lines


def _create_examples_table(placeholders: set, base_indentation: str) -> list:
    """Create the Examples table for the scenario outline."""
    examples_indentation = base_indentation + "    "
    table_indentation = examples_indentation + "  "
    
    sorted_placeholders = sorted(placeholders)
    header = "| " + " | ".join(sorted_placeholders) + " |"
    sample_row = "| " + " | ".join(f"<{p}_value>" for p in sorted_placeholders) + " |"
    
    return [
        f"{examples_indentation}Examples:",
        f"{table_indentation}{header}",
        f"{table_indentation}{sample_row}"
    ]


def fix_title_mismatch(
    file_path: str, artefact_text: str, artefact_class, **kwargs
) -> str:
    """
    Deterministically fixes the title in the artefact text to match the filename.
    """
    base_name = os.path.basename(file_path)
    correct_title_underscores, _ = os.path.splitext(base_name)
    correct_title_spaces = correct_title_underscores.replace("_", " ")

    title_prefix = artefact_class._title_prefix()

    lines = artefact_text.splitlines()
    new_lines = []
    title_found_and_replaced = False

    for line in lines:
        if not title_found_and_replaced and line.strip().startswith(title_prefix):
            new_lines.append(f"{title_prefix} {correct_title_spaces}")
            title_found_and_replaced = True
        else:
            new_lines.append(line)

    if not title_found_and_replaced:
        print(
            f"Warning: Title prefix '{title_prefix}' not found in {file_path}. Title could not be fixed."
        )
        return artefact_text

    return "\n".join(new_lines)


def fix_contribution(
    file_path: str,
    artefact_text: str,
    artefact_class: str,
    classified_artefact_info: dict,
    **kwargs,
):
    classified_artefact_info = populate_classified_artefact_info(classified_artefact_info=classified_artefact_info)
    artefact = artefact_class.deserialize(artefact_text)
    artefact, _ = set_closest_contribution(artefact)
    artefact_text = artefact.serialize()
    return artefact_text


def fix_rule(
    file_path: str,
    artefact_text: str,
    artefact_class: str,
    classified_artefact_info: dict,
    **kwargs,
):
    classified_artefact_info = populate_classified_artefact_info(classified_artefact_info=classified_artefact_info)
    artefact = artefact_class.deserialize(artefact_text)
    contribution = artefact.contribution
    assert contribution is not None
    _update_rule(
        artefact=artefact,
        name=contribution.artefact_name,
        classifier=contribution.classifier,
        classified_file_info=classified_artefact_info,
        delete_if_not_found=True
    )
    feedback_message = (f"Updating contribution of {artefact._artefact_type().value} "
                        f"'{artefact.title}' to {contribution.classifier} "
                        f"'{contribution.artefact_name}' ")
    rule = contribution.rule
    if rule:
        feedback_message += f"with rule '{rule}'"
    else:
        feedback_message += "without a rule"
    print(feedback_message)
    return artefact.serialize()


def should_skip_issue(deterministic_issue, deterministic, non_deterministic, file_path) -> bool:
    if not non_deterministic and not deterministic_issue:
        print(f"Skipping non-deterministic fix for {file_path} as per request.")
        return True
    if not deterministic and deterministic_issue:
        print(f"Skipping fix for {file_path} as per request flags.")
        return True
    return False

def determine_attempt_count(single_pass, file_path) -> int:
    if single_pass:
        print(f"Single-pass mode enabled for {file_path}. Running for 1 attempt.")
        return 1
    return 3

def apply_deterministic_fix(
    deterministic, deterministic_issue, file_path, artefact_text, artefact_class, classified_artefact_info,
    deterministic_markers_to_functions, corrected_text
) -> str:
    if deterministic and deterministic_issue:
        print(f"Applying deterministic fix for '{deterministic_issue}'...")
        fix_function = deterministic_markers_to_functions[deterministic_issue]
        return fix_function(
            file_path=file_path,
            artefact_text=artefact_text,
            artefact_class=artefact_class,
            classified_artefact_info=classified_artefact_info,
        )
    return corrected_text

def apply_non_deterministic_fix(
    non_deterministic, deterministic_issue, corrected_text,
    artefact_type, current_reason, file_path, artefact_text, artefact_class
) -> Optional[str]:
    """
    Applies LLM fix. Return None in case of an exception
    """
    if non_deterministic and not deterministic_issue:
        print("Applying non-deterministic (LLM) fix...")
        prompt = construct_prompt(
            artefact_type, current_reason, file_path, artefact_text
        )
        try:
            corrected_artefact = run_agent(prompt, artefact_class)
            corrected_text = corrected_artefact.serialize()
        except Exception as e:
            print(f"   ❌ LLM agent failed to fix artefact at {file_path}: {e}")
            return None
    return corrected_text

def attempt_autofix_loop(
    file_path: str,
    artefact_type,
    artefact_class,
    deterministic_markers_to_functions,
    max_attempts,
    deterministic: bool,
    non_deterministic: bool,
    classified_artefact_info: Optional[Dict[str, List[Dict[str, str]]]],
) -> bool:
    """
    Attempts to fix the artefact in a loop, up to max_attempts.
    """
    for attempt in range(max_attempts):
        is_valid, current_reason = check_file(
            file_path, artefact_class, classified_artefact_info
        )

        if is_valid:
            print(f"✅ Artefact at {file_path} is now valid.")
            return True

        print(
            f"Attempting to fix {file_path} (Attempt {attempt + 1}/{max_attempts})..."
        )
        print(f"   Reason: {current_reason}")

        artefact_text = read_artefact(file_path)
        if artefact_text is None:
            return False

        deterministic_issue = next(
            (
                marker
                for marker in deterministic_markers_to_functions
                if marker in current_reason
            ),
            None,
        )

        if should_skip_issue(deterministic_issue, deterministic, non_deterministic, file_path):
            return False

        corrected_text = None

        corrected_text = apply_deterministic_fix(
            deterministic, deterministic_issue, file_path, artefact_text,
            artefact_class, classified_artefact_info,
            deterministic_markers_to_functions, corrected_text
        )
        corrected_text = apply_non_deterministic_fix(
            non_deterministic, deterministic_issue, corrected_text,
            artefact_type, current_reason, file_path, artefact_text, artefact_class
        )

        if corrected_text is None or corrected_text.strip() == artefact_text.strip():
            print(
                "   Fixing attempt did not alter the file. Stopping to prevent infinite loop."
            )
            return False

        write_corrected_artefact(file_path, corrected_text)

        print("   File modified. Re-classifying artefact information for next check...")
        classified_artefact_info = populate_classified_artefact_info(classified_artefact_info, force=True)

    print(f"❌ Failed to fix {file_path} after {max_attempts} attempts.")
    return False

def apply_autofix(
    file_path: str,
    classifier: str,
    reason: str,
    single_pass: bool = False,
    deterministic: bool = True,
    non_deterministic: bool = True,
    classified_artefact_info: Optional[Dict[str, List[Dict[str, str]]]] = None,
) -> bool:
    """
    Applies fixes to a single artefact file iteratively until it is valid
    or a fix cannot be applied. If single_pass is True, it runs for only one attempt.
    """
    deterministic_markers_to_functions = {
        "Filename-Title Mismatch": fix_title_mismatch,
        "Invalid Contribution Reference": fix_contribution,
        "Rule Mismatch": fix_rule,
        "Scenario Contains Placeholders": fix_scenario_placeholder_mismatch,
    }

    artefact_type, artefact_class = determine_artefact_type_and_class(classifier)
    if artefact_type is None or artefact_class is None:
        return False

    classified_artefact_info = populate_classified_artefact_info(classified_artefact_info)
    max_attempts = determine_attempt_count(single_pass, file_path)

    return attempt_autofix_loop(
        file_path=file_path,
        artefact_type=artefact_type,
        artefact_class=artefact_class,
        deterministic_markers_to_functions=deterministic_markers_to_functions,
        max_attempts=max_attempts,
        deterministic=deterministic,
        non_deterministic=non_deterministic,
        classified_artefact_info=classified_artefact_info,
    )
