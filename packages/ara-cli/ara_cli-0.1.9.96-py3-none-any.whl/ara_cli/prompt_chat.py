import os
from . import whitelisted_commands
from ara_cli.chat import Chat
from ara_cli.classifier import Classifier
from ara_cli.update_config_prompt import update_artefact_config_prompt_files
from ara_cli.output_suppressor import suppress_stdout


def initialize_prompt_chat_mode(classifier, param, chat_name, reset=None, output_mode=False, append_strings=[], restricted=False):
    sub_directory = Classifier.get_sub_directory(classifier)
    artefact_data_path = os.path.join("ara", sub_directory, f"{param}.data") # f"ara/{sub_directory}/{parameter}.data"

    if chat_name is None:
        chat_name = classifier

    with suppress_stdout(suppress=output_mode):
        update_artefact_config_prompt_files(classifier, param, automatic_update=True)

    classifier_chat_file = os.path.join(artefact_data_path, f"{chat_name}")
    start_chat_session(classifier_chat_file, reset, output_mode, append_strings, restricted)

def start_chat_session(chat_file, reset, output_mode, append_strings, restricted):
    with suppress_stdout(suppress=output_mode):
        chat = Chat(chat_file, reset=reset) if not restricted else Chat(chat_file, reset=reset, enable_commands=whitelisted_commands)
    if append_strings:
        chat.append_strings(append_strings)
    if output_mode:
        chat.start_non_interactive()
        return
    chat.start()
