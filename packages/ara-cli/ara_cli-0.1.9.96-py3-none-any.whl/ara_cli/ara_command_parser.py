import argparse
import sys
from ara_cli.classifier import Classifier
from ara_cli.commandline_completer import (
    ArtefactCompleter,
    ParentNameCompleter,
    StatusCompleter,
)
from ara_cli.template_manager import SpecificationBreakdownAspects


classifiers = Classifier.ordered_classifiers()
aspects = SpecificationBreakdownAspects.VALID_ASPECTS


def create_parser(subparsers):
    create_parser = subparsers.add_parser(
        "create", help="Create a classified artefact with data directory"
    )
    create_parser.add_argument(
        "classifier",
        choices=classifiers,
        help="Classifier that also serves as file extension for the artefact file to be created. Valid Classifiers are: businessgoal, capability, keyfeature, feature, epic, userstory, example, task",
    )
    create_parser.add_argument(
        "parameter", help="Artefact name that serves as filename"
    ).completer = ArtefactCompleter()

    option_parser = create_parser.add_subparsers(dest="option")

    contribution_parser = option_parser.add_parser("contributes-to")
    contribution_parser.add_argument(
        "parent_classifier", choices=classifiers, help="Classifier of the parent"
    )
    contribution_parser.add_argument(
        "parent_name", help="Name of a parent artefact"
    ).completer = ParentNameCompleter()
    contribution_parser.add_argument("-r", "--rule", dest="rule", action="store")

    aspect_parser = option_parser.add_parser("aspect")
    aspect_parser.add_argument(
        "aspect",
        choices=aspects,
        help="Adds additional specification breakdown aspects in data directory.",
    )


def delete_parser(subparsers):
    delete_parser = subparsers.add_parser(
        "delete", help="Delete an artefact file including its data directory"
    )
    delete_parser.add_argument(
        "classifier",
        choices=classifiers,
        help="Classifier of the artefact to be deleted",
    )
    delete_parser.add_argument(
        "parameter", help="Filename of artefact"
    ).completer = ArtefactCompleter()
    delete_parser.add_argument(
        "-f",
        "--force",
        dest="force",
        action="store_true",
        help="ignore nonexistent files and arguments, never prompt",
    )


def rename_parser(subparsers):
    rename_parser = subparsers.add_parser(
        "rename", help="Rename a classified artefact and its data directory"
    )
    rename_parser.add_argument(
        "classifier", choices=classifiers, help="Classifier of the artefact"
    )
    rename_parser.add_argument(
        "parameter", help="Filename of artefact"
    ).completer = ArtefactCompleter()
    rename_parser.add_argument(
        "aspect", help="New artefact name and new data directory name"
    )


def add_filter_flags(parser):
    parser.add_argument(
        "-I",
        "--include-content",
        nargs="+",
        default=None,
        help="filter for files which include given content",
    )
    parser.add_argument(
        "-E",
        "--exclude-content",
        nargs="+",
        default=None,
        help="filter for files which do not include given content",
    )

    parser.add_argument(
        "--include-tags",
        nargs="+",
        default=None,
        help="filter for files which include given tags",
    )
    parser.add_argument(
        "--exclude-tags",
        nargs="+",
        default=None,
        help="filter for files which do not include given tags",
    )

    extension_group = parser.add_mutually_exclusive_group()
    extension_group.add_argument(
        "-i",
        "--include-extension",
        "--include-classifier",
        dest="include_extension",
        nargs="+",
        help="list of extensions to include in listing",
    )
    extension_group.add_argument(
        "-e",
        "--exclude-extension",
        "--exclude-classifier",
        dest="exclude_extension",
        nargs="+",
        help="list of extensions to exclude from listing",
    )


def list_parser(subparsers):
    list_parser = subparsers.add_parser("list", help="List files with optional tags")
    list_parser.add_argument("tags", nargs="*", help="Tags for listing files")

    add_filter_flags(list_parser)

    argument_group = list_parser.add_mutually_exclusive_group()
    argument_group.add_argument(
        "-b",
        "--branch",
        dest="branch_args",
        nargs=2,
        metavar=("classifier", "artefact_name"),
        help="List artefacts in the parent chain of the artefact with specified classifier and artefact_name",
    )
    argument_group.add_argument(
        "-c",
        "--children",
        dest="children_args",
        nargs=2,
        metavar=("classifier", "artefact_name"),
        help="List child artefacts of the artefact with specified classifier and artefact_name",
    )
    argument_group.add_argument(
        "-d",
        "--data",
        dest="data_args",
        nargs=2,
        metavar=("classifier", "artefact_name"),
        help="List file in the data directory of the artefact with specified classifier and artefact_name",
    )

    list_parser.set_defaults(
        branch_args=(None, None), children_args=(None, None), data_args=(None, None)
    )


def list_tags_parser(subparsers):
    tags_parser = subparsers.add_parser("list-tags", help="Show tags")
    tags_parser.add_argument(
        "--json",
        "-j",
        help="Output tags as JSON",
        action=argparse.BooleanOptionalAction,
    )
    tags_parser.add_argument(
        "--include-classifier",
        choices=classifiers,
        help="Show tags for an artefact type",
    )
    tags_parser.add_argument(
        "--exclude_classifier",
        choices=classifiers,
        help="Show tags for an artefact type",
    )
    tags_parser.add_argument(
        "--filtered-extra-column",
        action="store_true",
        help="Filter tags for extra column",
    )


def add_chat_arguments(chat_parser):
    chat_parser.add_argument(
        "chat_name",
        help="Optional name for a specific chat. Pass the .md file to continue an existing chat",
        nargs="?",
        default=None,
    )

    chat_parser.add_argument(
        "-r",
        "--reset",
        dest="reset",
        action=argparse.BooleanOptionalAction,
        help="Reset the chat file if it exists",
    )
    chat_parser.set_defaults(reset=None)

    chat_parser.add_argument(
        "--out",
        dest="output_mode",
        action="store_true",
        help="Output the contents of the chat file instead of entering interactive chat mode",
    )

    chat_parser.add_argument(
        "--append", nargs="*", default=None, help="Append strings to the chat file"
    )

    chat_parser.add_argument(
        "--restricted",
        dest="restricted",
        action=argparse.BooleanOptionalAction,
        help="Start with a limited set of commands",
    )


def prompt_parser(subparsers):
    prompt_parser = subparsers.add_parser(
        "prompt", help="Base command for prompt interaction mode"
    )

    steps = [
        "init",
        "load",
        "send",
        "load-and-send",
        "extract",
        "update",
        "chat",
        "init-rag",
    ]
    steps_parser = prompt_parser.add_subparsers(dest="steps")
    for step in steps:
        step_parser = steps_parser.add_parser(step)
        step_parser.add_argument(
            "classifier", choices=classifiers, help="Classifier of the artefact"
        )
        step_parser.add_argument(
            "parameter",
            help="Name of artefact data directory for prompt creation and interaction",
        ).completer = ArtefactCompleter()
        if step == "chat":
            add_chat_arguments(step_parser)
        if step == "extract":
            step_parser.add_argument(
                "-w",
                "--write",
                action="store_true",
                help="Overwrite existing files without using LLM for merging."
            )


def chat_parser(subparsers):
    chat_parser = subparsers.add_parser(
        "chat", help="Command line chatbot. Chat control with SEND/s | RERUN/r | QUIT/q"
    )
    add_chat_arguments(chat_parser)


def template_parser(subparsers):
    template_parser = subparsers.add_parser(
        "template", help="Outputs a classified ara template in the terminal"
    )
    template_parser.add_argument(
        "classifier", choices=classifiers, help="Classifier of the artefact type"
    )


def fetch_templates_parser(subparsers):
    subparsers.add_parser(
        "fetch-templates", help="Fetches templates and stores them in .araconfig"
    )


def read_parser(subparsers):
    read_parser = subparsers.add_parser("read", help="Reads contents of artefacts")
    read_parser.add_argument(
        "classifier", choices=classifiers, help="Classifier of the artefact type"
    )
    read_parser.add_argument(
        "parameter", help="Filename of artefact"
    ).completer = ArtefactCompleter()

    add_filter_flags(read_parser)

    branch_group = read_parser.add_mutually_exclusive_group()
    branch_group.add_argument(
        "-b",
        "--branch",
        dest="read_mode",
        action="store_const",
        const="branch",
        help="Output the contents of artefacts in the parent chain",
    )
    branch_group.add_argument(
        "-c",
        "--children",
        dest="read_mode",
        action="store_const",
        const="children",
        help="Output the contents of child artefacts",
    )

    read_parser.set_defaults(read_mode=None)


def reconnect_parser(subparsers):
    reconnect_parser = subparsers.add_parser(
        "reconnect", help="Connect an artefact to a parent artefact"
    )
    reconnect_parser.add_argument(
        "classifier", choices=classifiers, help="Classifier of the artefact type"
    )
    reconnect_parser.add_argument(
        "parameter", help="Filename of artefact"
    ).completer = ArtefactCompleter()
    reconnect_parser.add_argument(
        "parent_classifier",
        choices=classifiers,
        help="Classifier of the parent artefact type",
    )
    reconnect_parser.add_argument(
        "parent_name", help="Filename of parent artefact"
    ).completer = ParentNameCompleter()
    reconnect_parser.add_argument("-r", "--rule", dest="rule", action="store")


def read_status_parser(subparsers):
    read_status_parser = subparsers.add_parser(
        "read-status", help="Read status of an artefact by checking its tags"
    )
    read_status_parser.add_argument(
        "classifier", choices=classifiers, help="Classifier of the artefact type"
    )
    read_status_parser.add_argument(
        "parameter", help="Filename of artefact"
    ).completer = ArtefactCompleter()


def read_user_parser(subparsers):
    read_user_parser = subparsers.add_parser(
        "read-user", help="Read user of an artefact by checking its tags"
    )
    read_user_parser.add_argument(
        "classifier", choices=classifiers, help="Classifier of the artefact type"
    )
    read_user_parser.add_argument(
        "parameter", help="Filename of artefact"
    ).completer = ArtefactCompleter()


def set_status_parser(subparsers):
    set_status_parser = subparsers.add_parser(
        "set-status", help="Set the status of a task"
    )
    set_status_parser.add_argument(
        "classifier",
        choices=classifiers,
        help="Classifier of the artefact type, typically 'task'",
    )
    set_status_parser.add_argument(
        "parameter", help="Name of the task artefact"
    ).completer = ArtefactCompleter()
    set_status_parser.add_argument(
        "new_status", help="New status to set for the task"
    ).completer = StatusCompleter()


def set_user_parser(subparsers):
    set_user_parser = subparsers.add_parser("set-user", help="Set the user of a task")
    set_user_parser.add_argument(
        "classifier",
        choices=classifiers,
        help="Classifier of the artefact type, typically 'task'",
    )
    set_user_parser.add_argument(
        "parameter", help="Name of the task artefact"
    ).completer = ArtefactCompleter()
    set_user_parser.add_argument("new_user", help="New user to assign to the task")


def classifier_directory_parser(subparsers):
    classifier_directory_parser = subparsers.add_parser(
        "classifier-directory",
        help="Print the ara subdirectory for an artefact classifier",
    )
    classifier_directory_parser.add_argument(
        "classifier", choices=classifiers, help="Classifier of the artefact type"
    )


def scan_parser(subparsers):
    subparsers.add_parser("scan", help="Scan ARA tree for incompatible artefacts.")


def autofix_parser(subparsers):
    autofix_parser = subparsers.add_parser(
        "autofix",
        help="Fix ARA tree with llm models for scanned artefacts with ara scan command. By default three attemps for every file.",
    )
    autofix_parser.add_argument(
        "--single-pass",
        action="store_true",
        help="Run the autofix once for every scaned file.",
    )
    determinism_group = autofix_parser.add_mutually_exclusive_group()
    determinism_group.add_argument(
        "--deterministic",
        "-d",
        action="store_true",
        help="Run only deterministic fixes e.g Title-FileName Mismatch fix",
    )
    determinism_group.add_argument(
        "--non-deterministic",
        "-nd",
        action="store_true",
        help="Run only non-deterministic fixes",
    )


def extract_parser(subparsers):
    extract_parser = subparsers.add_parser("extract", help="Extract blocks of marked content from a given file.")
    extract_parser.add_argument(
        "filename",
        help="Input file to extract from."
    )
    extract_parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Answer queries with yes when extracting."
    )
    extract_parser.add_argument(
        "-w",
        "--write",
        action="store_true",
        help="Overwrite existing files without using LLM for merging."
    )


class CustomHelpFormatter(argparse.HelpFormatter):
    def __init__(self, *args, **kwargs):
        self.add_examples = kwargs.pop("add_examples", False)
        super().__init__(*args, **kwargs)

    def format_help(self):
        help_message = super().format_help()
        if self.add_examples:
            examples = (
                "\nValid classified artefacts are: businessgoal, vision, capability, keyfeature, feature, epic, userstory, example, feature, task.\n"
                "The default ara directory structure of classified artefact of the ara cli tool is:\n"
                ".\n"
                "└── ara\n"
                "   ├── businessgoals\n"
                "   ├── capabilities\n"
                "   ├── epics\n"
                "   ├── examples\n"
                "   ├── features\n"
                "   ├── keyfeatures\n"
                "   ├── tasks\n"
                "   ├── userstories\n"
                "   └── vision\n"
                "\n"
                "\nara artefact handling examples:\n"
                "  > create a new artefact for e.g. a feature:                                        ara create feature {feature_name}\n"
                "  > create a new artefact for e.g. a feature that contributes to an userstory:       ara create feature {feature_name} contributes-to userstory {story_name}\n"
                "  > read an artefact and return the content as terminal output, for eg. of a task:   ara read task {task_name}\n"
                "  > read an artefact and its full chain of contributions to its parents and return\n"
                "    the content as terminal output, for eg. of a task:                               ara read task {task_name} --branch\n"
                "  > delete an artefact for e.g. feature:                                             ara delete feature {feature_name}\n"
                "  > rename artefact and artefact data directory for e.g. a feature:                  ara rename feature {initial_feature_name} {new_feature_name}\n"
                "  > create additional templates for a specific aspect (valid aspects are: customer,\n"
                "    persona, concept, technology) related to an existing artefact like a feature:    ara create feature {feature_name} aspect {aspect_name}\n"
                "  > list artefact data with .md file extension                                       ara list --data {classifier} {artefact_name} --include-extension .md\n"
                "  > list artefact data with .md and .json file extensions                            ara list --data {classifier} {artefact_name} --include-extension .md .json\n"
                "  > list everything but userstories                                                  ara list --exclude-extension .userstory\n"
                "  > list all existing features:                                                      ara list --include-extension .feature\n"
                '  > list all child artefacts contributing value to a parent artefact:                ara list --include-content "Contributes to {name_of_parent_artefact} {ara classifier_of_parent_artefact}"\n'
                "  > list tasks which contain 'example content'                                       ara list --include-extension .task --include-content \"example content\"\n"
                "  > list children artefacts of a userstory                                           ara list --children userstory {name_of_userstory}\n"
                "  > list parent artefacts of a userstory                                             ara list --branch userstory {name_of_userstory}\n"
                "  > list parent businessgoal artefact of a userstory                                 ara list --branch userstory {name_of_userstory} --include-extension .businessgoal\n"
                "  > print any artefact template for e.g. a feature file template in the terminal:    ara template feature\n"
                "\n"
                " \nara prompt templates examples:\n"
                " > get and copy all prompt templates (blueprints, rules, intentions, commands\n"
                "   in the ara/.araconfig/global-prompt-modules directory:                            ara fetch-templates\n"
                "\n"
                " \nara chat examples:\n"
                "  > chat with ara and save the default chat.md file in the working directory:        ara chat\n"
                "  > chat with ara and save the default task_chat.md file in the task.data directory: ara prompt chat task {task_name}\n"
                "\n"
                "  > initialize a macro prompt for a task:                                            ara prompt init task {task_name}\n"
                "  > load selected templates in config_prompt_templates.md for the task {task_name}:  ara prompt load task {task_name}\n"
                "  > create and send configured prompt of the task {task_name} to the configured LLM: ara prompt send task {task_name}\n"
                "  > extract the selected LLM response in task.exploration.md and save to disk:       ara prompt extract task {task_name}\n"
            )
            return help_message + examples
        return help_message


class CustomArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        self.add_examples = False
        kwargs["formatter_class"] = CustomHelpFormatter
        super().__init__(*args, **kwargs)

    def _get_formatter(self):
        # Pass add_examples flag to formatter
        return self.formatter_class(prog=self.prog, add_examples=self.add_examples)

    def print_help(self, file=None):
        # Use the formatter with the current add_examples
        if file is None:
            file = sys.stdout
        file.write(self.format_help())
        file.write("\n")

    def error(self, message):
        self.add_examples = True
        sys.stderr.write(f"error: {message}\n")
        self.print_help(sys.stderr)
        sys.exit(2)


def action_parser():
    # Use the CustomArgumentParser instead of argparse.ArgumentParser
    parser = CustomArgumentParser(
        description="The ara cli terminal tool is a management tool for classified ara artefacts."
    )

    subparsers = parser.add_subparsers(dest="action", help="Action to perform")
    create_parser(subparsers)
    delete_parser(subparsers)
    rename_parser(subparsers)
    list_parser(subparsers)
    list_tags_parser(subparsers)
    prompt_parser(subparsers)
    chat_parser(subparsers)
    template_parser(subparsers)
    fetch_templates_parser(subparsers)
    read_parser(subparsers)
    reconnect_parser(subparsers)
    read_status_parser(subparsers)
    read_user_parser(subparsers)
    set_status_parser(subparsers)
    set_user_parser(subparsers)
    classifier_directory_parser(subparsers)
    scan_parser(subparsers)
    autofix_parser(subparsers)
    extract_parser(subparsers)

    return parser
