from os.path import join
import os
import sys
import json
from ara_cli.error_handler import AraError
from ara_cli.error_handler import handle_errors, AraValidationError
from ara_cli.output_suppressor import suppress_stdout
from ara_cli.artefact_fuzzy_search import suggest_close_name_matches
from . import whitelisted_commands, error_handler


def check_validity(condition, error_message):
    if not condition:
        raise AraValidationError(error_message)


@handle_errors(context="create action", error_handler=error_handler)
def create_action(args):
    from ara_cli.artefact_creator import ArtefactCreator
    from ara_cli.classifier import Classifier
    from ara_cli.filename_validator import is_valid_filename
    from ara_cli.template_manager import SpecificationBreakdownAspects
    from ara_cli.artefact_reader import ArtefactReader
    from ara_cli.artefact_fuzzy_search import find_closest_rule

    check_validity(Classifier.is_valid_classifier(args.classifier), "Invalid classifier provided. Please provide a valid classifier.")
    check_validity(is_valid_filename(args.parameter), "Invalid filename provided. Please provide a valid filename.")

    def handle_parent_arguments(args):
        parent_classifier = args.parent_classifier if hasattr(args, "parent_classifier") else None
        parent_name = args.parent_name if hasattr(args, "parent_name") else None
        rule = args.rule if hasattr(args, 'rule') else None
        invalid_classifier_message = "Invalid parent classifier provided. Please provide a valid classifier"
        invalid_name_message = "Invalid filename provided for parent. Please provide a valid filename."
        if parent_classifier and parent_name and rule:
            check_validity(Classifier.is_valid_classifier(parent_classifier), invalid_classifier_message)
            check_validity(is_valid_filename(parent_name), invalid_name_message)
            parent_artefact = ArtefactReader.read_artefact(artefact_name=parent_name, classifier=parent_classifier)
            rule = find_closest_rule(parent_artefact, rule)
            return parent_classifier, parent_name, rule
        if parent_classifier and parent_name:
            check_validity(Classifier.is_valid_classifier(parent_classifier), invalid_classifier_message)
            check_validity(is_valid_filename(parent_name), invalid_name_message)
            return parent_classifier, parent_name, rule
        return None, None, None

    def handle_aspect_creation(args):
        aspect = args.aspect if hasattr(args, "aspect") else None
        if args.parameter and args.classifier and aspect:
            sba = SpecificationBreakdownAspects()
            try:
                sba.create(args.parameter, args.classifier, aspect)
                return True
            except ValueError as ve:
                print(f"Error: {ve}")
                sys.exit(1)
        return False

    parent_classifier, parent_name, rule = handle_parent_arguments(args)
    if handle_aspect_creation(args):
        return

    artefact_creator = ArtefactCreator()
    artefact_creator.run(args.parameter, args.classifier, parent_classifier, parent_name, rule)


@handle_errors(context="delete action", error_handler=error_handler)
def delete_action(args):
    from ara_cli.artefact_deleter import ArtefactDeleter

    artefact_deleter = ArtefactDeleter()
    artefact_deleter.delete(args.parameter, args.classifier, args.force)


@handle_errors(context="rename action", error_handler=error_handler)
def rename_action(args):
    from ara_cli.artefact_renamer import ArtefactRenamer
    from ara_cli.classifier import Classifier
    from ara_cli.filename_validator import is_valid_filename

    check_validity(is_valid_filename(args.parameter), "Invalid filename provided. Please provide a valid filename.")
    check_validity(Classifier.is_valid_classifier(args.classifier), "Invalid classifier provided. Please provide a valid classifier.")
    check_validity(is_valid_filename(args.aspect), "Invalid new filename provided. Please provide a valid filename.")

    artefact_renamer = ArtefactRenamer()
    artefact_renamer.rename(args.parameter, args.aspect, args.classifier)


@handle_errors(context="rename action", error_handler=error_handler)
def list_action(args):
    from ara_cli.artefact_lister import ArtefactLister
    from ara_cli.list_filter import ListFilter

    branch_classifier, branch_artefact_name = args.branch_args
    children_classifier, children_artefact_name = args.children_args
    data_classifier, data_artefact_name = args.data_args

    artefact_lister = ArtefactLister()

    list_filter = ListFilter(
        include_content=args.include_content,
        exclude_content=args.exclude_content,
        include_extension=args.include_extension,
        exclude_extension=args.exclude_extension,
        include_tags=args.include_tags,
        exclude_tags=args.exclude_tags
    )

    if branch_classifier and branch_artefact_name:
        artefact_lister.list_branch(
            classifier=branch_classifier,
            artefact_name=branch_artefact_name,
            list_filter=list_filter
        )
        return

    if children_classifier and children_artefact_name:
        artefact_lister.list_children(
            classifier=children_classifier,
            artefact_name=children_artefact_name,
            list_filter=list_filter
        )
        return

    if data_classifier and data_artefact_name:
        artefact_lister.list_data(
            classifier=data_classifier,
            artefact_name=data_artefact_name,
            list_filter=list_filter
        )
        return

    if (args.tags):
        artefact_lister.list_files(tags=args.tags, list_filter=list_filter)
        return
    artefact_lister.list_files(list_filter=list_filter)


@handle_errors(context="list-tags action", error_handler=error_handler)
def list_tags_action(args):
    from ara_cli.tag_extractor import TagExtractor
    from ara_cli.list_filter import ListFilter

    list_filter = ListFilter(
        include_extension=args.include_classifier,
        exclude_extension=args.exclude_classifier,
    )

    tag_extractor = TagExtractor()
    tags = tag_extractor.extract_tags(
        filtered_extra_column=getattr(args, "filtered_extra_column", False),
        list_filter=list_filter
    )

    if args.json:
        output = json.dumps({"tags": tags})
        print(output)
        return

    output = "\n".join(f"- {tag}" for tag in tags)
    print(output)


@handle_errors(context="prompt action", error_handler=error_handler)
def prompt_action(args):
    from ara_cli.classifier import Classifier
    from ara_cli.filename_validator import is_valid_filename

    check_validity(Classifier.is_valid_classifier(args.classifier), "Invalid classifier provided. Please provide a valid classifier.")
    check_validity(is_valid_filename(args.parameter), "Invalid filename provided. Please provide a valid filename.")

    classifier = args.classifier
    param = args.parameter
    init = args.steps
    write = getattr(args, 'write', False)

    def handle_init():
        from ara_cli.prompt_handler import initialize_prompt_templates
        initialize_prompt_templates(classifier, param)

    def handle_init_rag():
        from ara_cli.prompt_handler import initialize_prompt_templates
        from ara_cli.prompt_rag import search_and_add_relevant_files_to_prompt_givens
        initialize_prompt_templates(classifier, param)
        search_and_add_relevant_files_to_prompt_givens(classifier, param)

    def handle_load():
        from ara_cli.prompt_handler import load_selected_prompt_templates
        load_selected_prompt_templates(classifier, param)

    def handle_send():
        from ara_cli.prompt_handler import create_and_send_custom_prompt
        create_and_send_custom_prompt(classifier, param)

    def handle_load_and_send():
        from ara_cli.prompt_handler import load_selected_prompt_templates, create_and_send_custom_prompt
        load_selected_prompt_templates(classifier, param)
        create_and_send_custom_prompt(classifier, param)

    def handle_extract():
        from ara_cli.prompt_extractor import extract_and_save_prompt_results
        from ara_cli.update_config_prompt import update_artefact_config_prompt_files
        extract_and_save_prompt_results(classifier, param, write=write)
        print(f"automatic update after extract")
        update_artefact_config_prompt_files(classifier, param, automatic_update=True)

    def handle_chat():
        from ara_cli.prompt_chat import initialize_prompt_chat_mode
        chat_name = args.chat_name
        reset = args.reset
        output_mode = args.output_mode
        append_strings = args.append
        restricted = args.restricted
        initialize_prompt_chat_mode(classifier, param, chat_name, reset=reset, output_mode=output_mode, append_strings=append_strings, restricted=restricted)

    def handle_update():
        from ara_cli.update_config_prompt import update_artefact_config_prompt_files
        update_artefact_config_prompt_files(classifier, param, automatic_update=True)

    command_dispatcher = {
        'init': handle_init,
        'init-rag': handle_init_rag,
        'load': handle_load,
        'send': handle_send,
        'load-and-send': handle_load_and_send,
        'extract': handle_extract,
        'chat': handle_chat,
        'update': handle_update,
    }

    if init in command_dispatcher:
        command_dispatcher[init]()
    else:
        raise ValueError(f"Unknown command '{init}' provided.")


@handle_errors(context="chat action", error_handler=error_handler)
def chat_action(args):
    from ara_cli.chat import Chat

    reset = args.reset
    output_mode = args.output_mode
    append_strings = args.append
    restricted = args.restricted

    chat_name = "chat"
    if args.chat_name:
        chat_name = args.chat_name
    cwd = os.getcwd()
    chat_file_path = join(cwd, chat_name)

    with suppress_stdout(output_mode):
        chat = Chat(chat_file_path, reset=reset) if not restricted else Chat(chat_file_path, reset=reset, enable_commands=whitelisted_commands)

    if append_strings:
        chat.append_strings(append_strings)

    if output_mode:
        chat.start_non_interactive()
        return
    chat.start()


@handle_errors(context="template action", error_handler=error_handler)
def template_action(args):
    from ara_cli.classifier import Classifier
    from ara_cli.template_manager import TemplatePathManager

    check_validity(Classifier.is_valid_classifier(args.classifier), "Invalid classifier provided. Please provide a valid classifier.")

    template_manager = TemplatePathManager()
    content = template_manager.get_template_content(args.classifier)

    print(content)


@handle_errors(context="fetch-templates action", error_handler=error_handler)
def fetch_templates_action(args):
    import shutil
    from ara_cli.ara_config import ConfigManager
    from ara_cli.template_manager import TemplatePathManager

    config = ConfigManager().get_config()
    prompt_templates_dir = config.local_prompt_templates_dir
    template_base_path = TemplatePathManager.get_template_base_path()
    global_prompt_templates_path = join(template_base_path, "prompt-modules")

    subdirs = ["commands", "rules", "intentions", "blueprints"]

    os.makedirs(join(prompt_templates_dir, "global-prompt-modules"), exist_ok=True)
    for subdir in subdirs:
        target_dir = join(prompt_templates_dir, "global-prompt-modules", subdir)
        source_dir = join(global_prompt_templates_path, subdir)
        os.makedirs(target_dir, exist_ok=True)
        for item in os.listdir(source_dir):
            source = join(source_dir, item)
            target = join(target_dir, item)
            shutil.copy2(source, target)

    custom_prompt_templates_subdir = config.custom_prompt_templates_subdir
    local_prompt_modules_dir = join(prompt_templates_dir, custom_prompt_templates_subdir)
    os.makedirs(local_prompt_modules_dir, exist_ok=True)
    for subdir in subdirs:
        os.makedirs(join(local_prompt_modules_dir, subdir), exist_ok=True)


@handle_errors(context="read action", error_handler=error_handler)
def read_action(args):
    from ara_cli.commands.read_command import ReadCommand
    from ara_cli.list_filter import ListFilter

    classifier = args.classifier
    artefact_name = args.parameter
    read_mode = args.read_mode

    list_filter = ListFilter(
        include_content=args.include_content,
        exclude_content=args.exclude_content,
        include_extension=args.include_extension,
        exclude_extension=args.exclude_extension,
        include_tags=args.include_tags,
        exclude_tags=args.exclude_tags
    )

    command = ReadCommand(
        classifier=classifier,
        artefact_name=artefact_name,
        read_mode=read_mode,
        list_filter=list_filter
    )

    command.execute()


@handle_errors(context="reconnect action", error_handler=error_handler)
def reconnect_action(args):
    from ara_cli.artefact_models.artefact_load import artefact_from_content
    from ara_cli.artefact_models.artefact_model import Contribution
    from ara_cli.artefact_reader import ArtefactReader
    from ara_cli.file_classifier import FileClassifier
    from ara_cli.artefact_fuzzy_search import find_closest_rule

    classifier = args.classifier
    artefact_name = args.parameter
    parent_classifier = args.parent_classifier
    parent_name = args.parent_name
    rule = args.rule if hasattr(args, 'rule') else None

    read_error_message = f"Could not connect {classifier} '{artefact_name}' to {parent_classifier} '{parent_name}'"

    feedback_message = f"Updated contribution of {classifier} '{artefact_name}' to {parent_classifier} '{parent_name}'"

    file_classifier = FileClassifier(os)
    classified_file_info = file_classifier.classify_files()

    artefact = ArtefactReader.read_artefact(
        artefact_name=artefact_name,
        classifier=classifier,
        classified_file_info=classified_file_info
    )

    if not artefact:
        raise AraError(read_error_message)

    parent = ArtefactReader.read_artefact(
        artefact_name=parent_name,
        classifier=parent_classifier,
        classified_file_info=classified_file_info
    )

    if not parent:
        raise AraError(read_error_message)

    contribution = Contribution(
        artefact_name=parent.title,
        classifier=parent.artefact_type
    )

    if rule:
        closest_rule = find_closest_rule(parent, rule)
        contribution.rule = closest_rule
        feedback_message += f" using rule '{closest_rule}'"

    artefact.contribution = contribution
    with open(artefact.file_path, 'w', encoding='utf-8') as file:
        artefact_content = artefact.serialize()
        file.write(artefact_content)

    print(feedback_message + ".")


@handle_errors(context="read-status action", error_handler=error_handler)
def read_status_action(args):
    from ara_cli.file_classifier import FileClassifier
    from ara_cli.artefact_models.artefact_load import artefact_from_content

    classifier = args.classifier
    artefact_name = args.parameter

    file_classifier = FileClassifier(os)
    artefact_info = file_classifier.classify_files()
    artefact_info_dicts = artefact_info.get(classifier, [])

    all_artefact_names = [artefact_info["title"] for artefact_info in artefact_info_dicts]
    if artefact_name not in all_artefact_names:
        suggest_close_name_matches(artefact_name, all_artefact_names, report_as_error=True)
        return

    artefact_info = next(filter(
        lambda x: x["title"] == artefact_name, artefact_info_dicts
    ))

    with open(artefact_info["file_path"], 'r', encoding='utf-8') as file:
        content = file.read()
    artefact = artefact_from_content(content)

    status = artefact.status

    if not status:
        print("No status found")
        return
    print(status)


@handle_errors(context="read-user action", error_handler=error_handler)
def read_user_action(args):
    from ara_cli.artefact_models.artefact_load import artefact_from_content
    from ara_cli.file_classifier import FileClassifier

    classifier = args.classifier
    artefact_name = args.parameter

    file_classifier = FileClassifier(os)
    artefact_info = file_classifier.classify_files()
    artefact_info_dicts = artefact_info.get(classifier, [])

    all_artefact_names = [artefact_info["title"] for artefact_info in artefact_info_dicts]
    if artefact_name not in all_artefact_names:
        suggest_close_name_matches(artefact_name, all_artefact_names, report_as_error=True)
        return

    artefact_info = next(filter(
        lambda x: x["title"] == artefact_name, artefact_info_dicts
    ))

    with open(artefact_info["file_path"], 'r', encoding='utf-8') as file:
        content = file.read()
    artefact = artefact_from_content(content)

    user_tags = artefact.users

    if not user_tags:
        print("No user found")
        return
    for tag in user_tags:
        print(f" - {tag}")


@handle_errors(context="set-status action", error_handler=error_handler)
def set_status_action(args):
    from ara_cli.artefact_models.artefact_model import ALLOWED_STATUS_VALUES
    from ara_cli.artefact_models.artefact_load import artefact_from_content
    from ara_cli.file_classifier import FileClassifier

    status_tags = ALLOWED_STATUS_VALUES

    classifier = args.classifier
    artefact_name = args.parameter
    new_status = args.new_status

    if new_status.startswith('@'):
        new_status = new_status.lstrip('@')

    check_validity(new_status in status_tags, "Invalid status provided. Please provide a valid status.")

    file_classifier = FileClassifier(os)
    classified_artefacts_info = file_classifier.classify_files()
    classified_artefact_dict = classified_artefacts_info.get(classifier, [])
    all_artefact_names = [artefact_info["title"] for artefact_info in classified_artefact_dict]

    if artefact_name not in all_artefact_names:
        suggest_close_name_matches(artefact_name, all_artefact_names)
        return

    artefact_info = next(filter(
        lambda x: x["title"] == artefact_name, classified_artefact_dict
    ))

    with open(artefact_info["file_path"], 'r', encoding='utf-8') as file:
        content = file.read()
    artefact = artefact_from_content(content)

    artefact.status = new_status

    serialized_content = artefact.serialize()
    with open(f"{artefact_info['file_path']}", 'w', encoding='utf-8') as file:
        file.write(serialized_content)

    print(f"Status of task '{artefact_name}' has been updated to '{new_status}'.")


@handle_errors(context="set-user action", error_handler=error_handler)
def set_user_action(args):
    from ara_cli.file_classifier import FileClassifier
    from ara_cli.artefact_models.artefact_load import artefact_from_content

    classifier = args.classifier
    artefact_name = args.parameter
    new_user = args.new_user

    if new_user.startswith('@'):
        new_user = new_user.lstrip('@')

    file_classifier = FileClassifier(os)
    classified_artefacts_info = file_classifier.classify_files()
    classified_artefact_dict = classified_artefacts_info.get(classifier, [])
    all_artefact_names = [artefact_info["title"] for artefact_info in classified_artefact_dict]

    if artefact_name not in all_artefact_names:
        suggest_close_name_matches(artefact_name, all_artefact_names)
        return

    artefact_info = next(filter(
        lambda x: x["title"] == artefact_name, classified_artefact_dict
    ))

    with open(artefact_info["file_path"], 'r', encoding='utf-8') as file:
        content = file.read()
    artefact = artefact_from_content(content)

    artefact.users = [new_user]

    serialized_content = artefact.serialize()

    with open(artefact_info["file_path"], 'w', encoding='utf-8') as file:
        file.write(serialized_content)

    print(f"User of task '{artefact_name}' has been updated to '{new_user}'.")


@handle_errors(context="classifier-directory action", error_handler=error_handler)
def classifier_directory_action(args):
    from ara_cli.classifier import Classifier

    classifier = args.classifier
    subdirectory = Classifier.get_sub_directory(classifier)
    print(subdirectory)


@handle_errors(context="scan action", error_handler=error_handler)
def scan_action(args):
    from ara_cli.file_classifier import FileClassifier
    from ara_cli.artefact_scan import find_invalid_files, show_results
    import os

    classified_artefact_info = FileClassifier(os).classify_files()
    invalid_artefacts = {}
    for classifier in classified_artefact_info:
        invalid = find_invalid_files(classified_artefact_info, classifier)
        if invalid:
            invalid_artefacts[classifier] = invalid
    show_results(invalid_artefacts)


@handle_errors(context="autofix_action", error_handler=error_handler)
def autofix_action(args):
    from ara_cli.artefact_autofix import parse_report, apply_autofix, read_report_file
    from ara_cli.file_classifier import FileClassifier

    # If the user passes --non-deterministic, only_deterministic_fix becomes False.
    # If the user passes --deterministic, only_non_deterministic_fix becomes False.
    # If no flags are passed, both are True, and all fixes are attempted.
    run_deterministic = not args.non_deterministic
    run_non_deterministic = not args.deterministic

    content = read_report_file()
    if not content:
        return False

    issues = parse_report(content)
    if not issues:
        print("No issues found in the report. Nothing to fix.")
        return

    file_classifier = FileClassifier(os)
    classified_artefact_info = file_classifier.classify_files()

    # print("\nStarting autofix process...")
    for classifier, files in issues.items():
        print(f"\nClassifier: {classifier}")
        for file_path, reason in files:
            apply_autofix(
                file_path,
                classifier,
                reason,
                single_pass=args.single_pass,
                deterministic=run_deterministic,
                non_deterministic=run_non_deterministic,
                classified_artefact_info=classified_artefact_info
            )

    print("\nAutofix process completed. Please review the changes.")


@handle_errors(context="extract action", error_handler=error_handler)
def extract_action(args):
    from ara_cli.commands.extract_command import ExtractCommand

    filename = args.filename
    force = args.force
    write = getattr(args, 'write', False)
    command = ExtractCommand(
        file_name=filename,
        force=force,
        write=write,
        output=lambda msg: print(msg, file=sys.stdout)
    )
    command.execute()
