import os
import argparse
import cmd2
from . import error_handler
from ara_cli.prompt_handler import send_prompt

from ara_cli.file_loaders.document_file_loader import DocumentFileLoader
from ara_cli.file_loaders.binary_file_loader import BinaryFileLoader
from ara_cli.file_loaders.text_file_loader import TextFileLoader


extract_parser = argparse.ArgumentParser()
extract_parser.add_argument('-f', '--force', action='store_true', help='Force extraction')
extract_parser.add_argument('-w','--write', action='store_true', help='Overwrite existing files without using LLM for merging.')

load_parser = argparse.ArgumentParser()
load_parser.add_argument('file_name', nargs='?', default='', help='File to load')
load_parser.add_argument('--load-images', action='store_true', help='Extract and describe images from documents')

extract_parser = argparse.ArgumentParser()
extract_parser.add_argument('-f', '--force', action='store_true', help='Force extraction')
extract_parser.add_argument('-w','--write', action='store_true', help='Overwrite existing files without using LLM for merging.')

load_parser = argparse.ArgumentParser()
load_parser.add_argument('file_name', nargs='?', default='', help='File to load')
load_parser.add_argument('--load-images', action='store_true', help='Extract and describe images from documents')


class Chat(cmd2.Cmd):
    CATEGORY_CHAT_CONTROL = "Chat control commands"
    CATEGORY_LLM_CONTROL = "Language model controls"

    INTRO = """/***************************************/
                 araarar
               aa       ara
             aa    aa   aara
             a        araarar
             a        ar  ar
           aa          ara
          a               a
          a               aa
           a              a
   ar      aa           aa
    (c) ara chat by talsen team
              aa      aa
               aa    a
                a aa
                 aa
/***************************************/
Start chatting (type 'HELP'/'h' for available commands, 'QUIT'/'q' to exit chat mode):"""

    ROLE_PROMPT = "ara prompt"
    ROLE_RESPONSE = "ara response"

    BINARY_TYPE_MAPPING = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
        }

    DOCUMENT_TYPE_EXTENSIONS = [".docx", ".doc", ".odt", ".pdf"]

    def __init__(
        self,
        chat_name: str,
        reset: bool | None = None,
        enable_commands: list[str] | None = None
    ):
        shortcuts = dict(cmd2.DEFAULT_SHORTCUTS)
        if enable_commands:
            enable_commands.append("quit")  # always allow quitting
            enable_commands.append("eof")  # always allow quitting with ctrl-D
            enable_commands.append("help")  # always allow help

            shortcuts = {key: value for key, value in shortcuts.items() if value in enable_commands}

        super().__init__(
            allow_cli_args=False,
            shortcuts=shortcuts
        )
        self.create_default_aliases()

        if enable_commands:
            all_commands = self.get_all_commands()
            commands_to_disable = [command for command in all_commands if command not in enable_commands]
            self.disable_commands(commands_to_disable)

        self.prompt = "ara> "
        self.intro = Chat.INTRO

        self.default_chat_content = f"# {Chat.ROLE_PROMPT}:\n"
        self.chat_name = self.setup_chat(chat_name, reset)
        self.chat_name = os.path.abspath(self.chat_name)
        self.chat_history = []
        self.message_buffer = []
        self.config = self._retrieve_ara_config()

    def disable_commands(self, commands: list[str]):
        for command in commands:
            setattr(self, f'do_{command}', self.default)
            self.hidden_commands.append(command)
        aliases_to_remove = [alias for alias, cmd in self.aliases.items() if cmd in commands]
        for alias in aliases_to_remove:
            del self.aliases[alias]

    def create_default_aliases(self):
        self.aliases["QUIT"] = "quit"
        self.aliases["q"] = "quit"
        self.aliases["r"] = "RERUN"
        self.aliases["s"] = "SEND"
        self.aliases["c"] = "CLEAR"
        self.aliases["HELP"] = "help"
        self.aliases["h"] = "help"
        self.aliases["n"] = "NEW"
        self.aliases["e"] = "EXTRACT"
        self.aliases["l"] = "LOAD"
        self.aliases["lr"] = "LOAD_RULES"
        self.aliases["li"] = "LOAD_INTENTION"
        self.aliases["lc"] = "LOAD_COMMANDS"
        self.aliases["lg"] = "LOAD_GIVENS"
        self.aliases["lb"] = "LOAD_BLUEPRINT"
        self.aliases["lt"] = "LOAD_TEMPLATE"

    def setup_chat(self, chat_name, reset: bool = None):
        if os.path.exists(chat_name):
            return self.handle_existing_chat(chat_name, reset=reset)
        if os.path.exists(f"{chat_name}.md"):
            return self.handle_existing_chat(f"{chat_name}.md", reset=reset)
        if os.path.exists(f"{chat_name}_chat.md"):
            return self.handle_existing_chat(f"{chat_name}_chat.md", reset=reset)
        return self.initialize_new_chat(chat_name)

    def handle_existing_chat(self, chat_file: str, reset: bool = None):
        chat_file_short = os.path.split(chat_file)[-1]

        if reset is None:
            user_input = input(f"{chat_file_short} already exists. Do you want to reset the chat? (y/N): ")
            if user_input.lower() == 'y':
                self.create_empty_chat_file(chat_file)
        if reset:
            self.create_empty_chat_file(chat_file)
        self.chat_history = self.load_chat_history(chat_file)
        print(f"Reloaded {chat_file_short} content")
        return chat_file

    def initialize_new_chat(self, chat_name: str):
        if chat_name.endswith(".md"):
            chat_name_md = chat_name
        else:
            if not chat_name.endswith("chat"):
                chat_name = f"{chat_name}_chat"
            chat_name_md = f"{chat_name}.md"
        self.create_empty_chat_file(chat_name_md)
        chat_name_md_short = os.path.split(chat_name_md)[-1]
        print(f"Created new chat file {chat_name_md_short}")
        return chat_name_md

    def file_exists_check(method):
        def wrapper(self, file_name, *args, **kwargs):
            file_path = self.determine_file_path(file_name)
            if not file_path:
                print(f"File {file_name} not found.")
                return False
            return method(self, file_path, *args, **kwargs)
        return wrapper

    @staticmethod
    def get_last_role_marker(lines):
        if not lines:
            return
        role_markers = [
            f"# {Chat.ROLE_PROMPT}:",
            f"# {Chat.ROLE_RESPONSE}"
        ]
        for line in reversed(lines):
            stripped_line = line.strip()
            if stripped_line.startswith(tuple(role_markers)):
                return stripped_line
        return None

    def start_non_interactive(self):
        with open(self.chat_name, 'r', encoding='utf-8') as file:
            content = file.read()
        print(content)

    def start(self):
        chat_name = self.chat_name
        directory = os.path.dirname(chat_name)
        os.chdir(directory)
        self.cmdloop()

    def get_last_non_empty_line(self, file) -> str:
        stripped_line = ""
        file.seek(0)
        lines = file.read().splitlines()
        if lines:
            for line in reversed(lines):
                stripped_line = line.strip()
                if stripped_line:
                    break
        return stripped_line

    def get_last_line(self, file):
        file.seek(0)
        lines = file.read().splitlines()
        if lines:
            return lines[-1].strip()
        return ""

    def assemble_message(self, message, role):
        import re
        from ara_cli.prompt_handler import append_images_to_message

        text_content = []
        image_data_list = []

        image_pattern = re.compile(r'\((data:image/[^;]+;base64,.*?)\)')

        for line in message.splitlines():
            match = image_pattern.search(line)
            if match:
                image_data = {"type": "image_url", "image_url": {"url": match.group(1)}}
                image_data_list.append(image_data)
            else:
                text_content.append(line)

        message_content = {
            "type": "text",
            "text": '\n'.join(text_content)}
        message = {
            "role": role,
            "content": [message_content]
        }
        message = append_images_to_message(message, image_data_list)
        return message

    def assemble_prompt(self):
        import re
        from ara_cli.prompt_handler import prepend_system_prompt

        prompt_marker = f"# {self.ROLE_PROMPT}:"
        response_marker = f"# {self.ROLE_RESPONSE}:"

        split_pattern = re.compile(f"({prompt_marker}|{response_marker})")

        parts = re.split(split_pattern, '\n'.join(self.chat_history))

        all_prompts_and_responses = []
        current = ""
        for part in parts:
            if part.startswith(prompt_marker) or part.startswith(response_marker):
                if current:
                    all_prompts_and_responses.append(current.strip())
                current = part
            else:
                current += part
        if current:
            all_prompts_and_responses.append(current)

        message_list = []
        for segment in all_prompts_and_responses:
            role = "user"
            if segment.startswith(prompt_marker):
                segment = segment.removeprefix(response_marker)
            if segment.startswith(response_marker):
                segment = segment.removeprefix(response_marker)
                role = "assistant"
            message = self.assemble_message(segment, role)
            message_list.append(message)

        message_list = prepend_system_prompt(message_list=message_list)

        return message_list

    def send_message(self):
        self.chat_history = self.load_chat_history(self.chat_name)
        prompt_to_send = self.assemble_prompt()
        role_marker = f"# {Chat.ROLE_RESPONSE}:"

        with open(self.chat_name, 'a+', encoding='utf-8') as file:
            last_line = self.get_last_line(file)

            print(role_marker)

            if not last_line.startswith(role_marker):
                if last_line:
                    file.write("\n")
                file.write(role_marker + "\n")

            for chunk in send_prompt(prompt_to_send):
                chunk_content = chunk.choices[0].delta.content
                if not chunk_content:
                    continue
                print(chunk_content, end="", flush=True)
                file.write(chunk_content)
                file.flush()
            print()

        self.message_buffer.clear()

    def save_message(self, role: str, message: str):
        role_marker = f"# {role}:"
        with open(self.chat_name, 'r', encoding='utf-8') as file:
            stripped_line = self.get_last_non_empty_line(file)
        line_to_write = f"{message}\n\n"
        if stripped_line != role_marker:
            line_to_write = f"\n{role_marker}\n{message}\n"

        with open(self.chat_name, 'a', encoding='utf-8') as file:
            file.write(line_to_write)
        self.chat_history.append(line_to_write)

    def resend_message(self):
        with open(self.chat_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        if not lines:
            return
        index_to_remove = self.find_last_reply_index(lines)
        if index_to_remove is not None:
            with open(self.chat_name, 'w', encoding='utf-8') as file:
                file.writelines(lines[:index_to_remove])
        self.send_message()

    def find_last_reply_index(self, lines: list[str]):
        index_to_remove = None
        for i, line in enumerate(reversed(lines)):
            if line.strip().startswith(f"# {Chat.ROLE_PROMPT}"):
                break
            if line.strip().startswith(f"# {Chat.ROLE_RESPONSE}"):
                index_to_remove = len(lines) - i - 1
                break
        return index_to_remove

    def append_strings(self, strings: list[str]):
        output = '\n'.join(strings)
        with open(self.chat_name, 'a') as file:
            file.write(output + '\n')

    def load_chat_history(self, chat_file: str):
        chat_history = []
        if os.path.exists(chat_file):
            with open(chat_file, 'r', encoding='utf-8') as file:
                chat_history = file.readlines()
        return chat_history

    def create_empty_chat_file(self, chat_file: str):
        with open(chat_file, 'w', encoding='utf-8') as file:
            file.write(self.default_chat_content)
        self.chat_history = []

    def add_prompt_tag_if_needed(self, chat_file: str):
        with open(chat_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        prompt_tag = f"# {Chat.ROLE_PROMPT}:"
        if Chat.get_last_role_marker(lines) == prompt_tag:
            return
        append = prompt_tag
        last_line = lines[-1].strip()
        if last_line != "" and last_line != '\n':
            append = f"\n{append}"
        with open(chat_file, 'a', encoding='utf-8') as file:
            file.write(append)

    def determine_file_path(self, file_name: str):
        current_directory = os.path.dirname(self.chat_name)
        file_path = os.path.join(current_directory, file_name)
        if not os.path.exists(file_path):
            file_path = file_name
        if not os.path.exists(file_path):
            print(f"File {file_name} not found")
            return None
        return file_path

    # @file_exists_check
    def load_text_file(
        self,
        file_path,
        prefix: str = "",
        suffix: str = "",
        block_delimiter: str = "",
        extract_images: bool = False
    ):
        loader = TextFileLoader(self)
        return loader.load(
            file_path,
            prefix=prefix,
            suffix=suffix,
            block_delimiter=block_delimiter,
            extract_images=extract_images
        )

    # @file_exists_check
    def load_binary_file(self, file_path, mime_type: str, prefix: str = "", suffix: str = ""):
        loader = BinaryFileLoader(self)
        return loader.load(
            file_path,
            mime_type=mime_type,
            prefix=prefix,
            suffix=suffix
        )

    def read_markdown(self, file_path: str, extract_images: bool = False) -> str:
        """Read markdown file and optionally extract/describe images"""
        from ara_cli.file_loaders.text_file_loader import MarkdownReader

        reader = MarkdownReader(file_path)
        return reader.read(extract_images=extract_images)

    # @file_exists_check
    def load_document_file(
        self,
        file_path: str,
        prefix: str = "",
        suffix: str = "",
        block_delimiter: str = "```",
        extract_images: bool = False
    ):
        loader = DocumentFileLoader(self)
        return loader.load(
            file_path,
            prefix=prefix,
            suffix=suffix,
            block_delimiter=block_delimiter,
            extract_images=extract_images
        )

    def load_file(
        self,
        file_name: str,
        prefix: str = "",
        suffix: str = "",
        block_delimiter: str = "",
        extract_images: bool = False
    ):
        binary_type_mapping = Chat.BINARY_TYPE_MAPPING
        document_type_extensions = Chat.DOCUMENT_TYPE_EXTENSIONS

        file_type = None
        file_name_lower = file_name.lower()
        for extension, mime_type in binary_type_mapping.items():
            if file_name_lower.endswith(extension):
                file_type = mime_type
                break

        is_file_document = any(file_name_lower.endswith(ext)
                                for ext in document_type_extensions)

        if is_file_document:
            return self.load_document_file(
                file_path=file_name,
                prefix=prefix,
                suffix=suffix,
                block_delimiter=block_delimiter,
                extract_images=extract_images
            )
        elif file_type:
            return self.load_binary_file(
                file_path=file_name,
                mime_type=file_type,
                prefix=prefix,
                suffix=suffix
            )
        else:
            return self.load_text_file(
                file_path=file_name,
                prefix=prefix,
                suffix=suffix,
                block_delimiter=block_delimiter,
                extract_images=extract_images
            )

    def choose_file_to_load(self, files: list[str], pattern: str):
        if len(files) > 1 or pattern in ["*", "global/*"]:
            files.sort()
            for i, file in enumerate(files):
                print(f"{i + 1}: {os.path.basename(file)}")
            choice = input("Please choose a file to load (enter number): ")
            try:
                choice_index = int(choice) - 1
                if choice_index < 0 or choice_index >= len(files):
                    print("Invalid choice. Aborting load.")
                    return None
                file_path = files[choice_index]
            except ValueError:
                print("Invalid input. Aborting load.")
                return None
        else:
            file_path = files[0]
        return file_path

    def _help_menu(self, verbose: bool = False):
        super()._help_menu(verbose)
        if self.aliases:
            aliases = [f"{alias} -> {command}" for alias, command in self.aliases.items()]
            self._print_topics("Aliases", aliases, verbose)

    def do_quit(self, _):
        """Exit ara-cli"""
        print("Chat ended")
        self.last_result = True
        return True

    def onecmd(self, *args, **kwargs):
        try:
            return super().onecmd(*args, **kwargs)
        except Exception as e:
            error_handler.report_error(e)
        return False

    def onecmd_plus_hooks(self, line, orig_rl_history_length):
        # store the full line for use with default()
        self.full_input = line
        return super().onecmd_plus_hooks(line, orig_rl_history_length=orig_rl_history_length)

    def default(self, line):
        self.message_buffer.append(self.full_input)

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    @cmd2.with_argparser(load_parser)
    def do_LOAD(self, args):
        """Load a file and append its contents to chat file. Can be given the file name in-line. Will attempt to find the file relative to chat file first, then treat the given path as absolute. Use --load-images flag to extract and describe images from documents."""
        from ara_cli.commands.load_command import LoadCommand

        file_name = args.file_name
        load_images = args.load_images
        
        matching_files = self.find_matching_files_to_load(file_name)
        if not matching_files:
            return

        for file_path in matching_files:
            block_delimiter = "```"
            prefix = f"\nFile: {file_path}\n"
            self.add_prompt_tag_if_needed(self.chat_name)
            
            if not os.path.isdir(file_path):
                command = LoadCommand(
                    chat_instance=self,
                    file_path=file_path,
                    prefix=prefix,
                    block_delimiter=block_delimiter,
                    extract_images=load_images,
                    output=self.poutput
                )
                command.execute()

    def complete_LOAD(self, text, line, begidx, endidx):
        import glob
        return [x for x in glob.glob(text + '*')]

    def _retrieve_ara_config(self):
        from ara_cli.prompt_handler import ConfigManager
        return ConfigManager().get_config()

    def _retrieve_llm_config(self):
        config = self.config
        llm_config = config.llm_config
        return llm_config

    def find_matching_files_to_load(self, file_name):
        import glob

        if file_name == "":
            file_name = input("What file do you want to load? ")
        file_pattern = os.path.join(os.path.dirname(self.chat_name), file_name)
        matching_files = glob.glob(file_pattern)
        if not matching_files:
            print(f"No files matching pattern {file_name} found.")
            return
        return matching_files

    def load_image(self, file_name: str, prefix: str = "", suffix: str = ""):
        binary_type_mapping = Chat.BINARY_TYPE_MAPPING

        file_type = None
        file_name_lower = file_name.lower()
        for extension, mime_type in binary_type_mapping.items():
            if file_name_lower.endswith(extension):
                file_type = mime_type
                break

        if file_type:
            return self.load_binary_file(
                file_path=file_name,
                mime_type=file_type,
                prefix=prefix,
                suffix=suffix
            )
        print(f"File {file_name} not recognized as image, could not load")

    def _verify_llm_choice(self, model_name):
        llm_config = self._retrieve_llm_config()
        models = [name for name in llm_config.keys()]
        if model_name not in models:
            print(f"Model {model_name} unavailable. Retrieve the list of available models using the LIST_MODELS command.")
            return False
        return True


    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_LOAD_IMAGE(self, file_name):
        """Load an image file and append it to chat file. Can be given the file name in-line. Will attempt to find the file relative to chat file first, then treat the given path as absolute"""
        from ara_cli.commands.load_image_command import LoadImageCommand
        
        matching_files = self.find_matching_files_to_load(file_name)
        if not matching_files:
            return

        for file_path in matching_files:
            prefix = f"\nFile: {file_path}\n"
            self.add_prompt_tag_if_needed(self.chat_name)
            
            if not os.path.isdir(file_path):
                # Determine mime type
                file_type = None
                file_path_lower = file_path.lower()
                for extension, mime_type in Chat.BINARY_TYPE_MAPPING.items():
                    if file_path_lower.endswith(extension):
                        file_type = mime_type
                        break
                
                if file_type:
                    command = LoadImageCommand(
                        chat_instance=self,
                        file_path=file_path,
                        mime_type=file_type,
                        prefix=prefix,
                        output=self.poutput
                    )
                    command.execute()
                else:
                    self.perror(f"File {file_path} not recognized as image, could not load")

    @cmd2.with_category(CATEGORY_LLM_CONTROL)
    def do_LIST_MODELS(self, _):
        llm_config = self._retrieve_llm_config()
        models = [name for name in llm_config.keys()]
        print("Available models:")
        for model in models:
            print(f"  - {model}")

    @cmd2.with_category(CATEGORY_LLM_CONTROL)
    def do_CHOOSE_MODEL(self, model_name):
        from ara_cli.prompt_handler import LLMSingleton
        from ara_cli.ara_config import DEFAULT_CONFIG_LOCATION, save_data
        from ara_cli.directory_navigator import DirectoryNavigator

        original_dir = os.getcwd()
        navigator = DirectoryNavigator()
        navigator.navigate_to_target()
        os.chdir('..')

        if not self._verify_llm_choice(model_name):
            return

        self.config.default_llm = model_name
        save_data(filepath=DEFAULT_CONFIG_LOCATION, config=self.config)

        LLMSingleton.set_default_model(model_name)
        print(f"Language model switched to '{model_name}'")

        os.chdir(original_dir)

    @cmd2.with_category(CATEGORY_LLM_CONTROL)
    def do_CHOOSE_EXTRACTION_MODEL(self, model_name):
        from ara_cli.prompt_handler import LLMSingleton
        from ara_cli.ara_config import DEFAULT_CONFIG_LOCATION, save_data
        from ara_cli.directory_navigator import DirectoryNavigator

        original_dir = os.getcwd()
        navigator = DirectoryNavigator()
        navigator.navigate_to_target()
        os.chdir('..')

        if not self._verify_llm_choice(model_name):
            return

        self.config.extraction_llm = model_name
        save_data(filepath=DEFAULT_CONFIG_LOCATION, config=self.config)
        
        LLMSingleton.set_extraction_model(model_name)
        print(f"Extraction model switched to '{model_name}'")

        os.chdir(original_dir)

    @cmd2.with_category(CATEGORY_LLM_CONTROL)
    def do_CURRENT_MODEL(self, _):
        from ara_cli.prompt_handler import LLMSingleton

        print(LLMSingleton.get_default_model())

    @cmd2.with_category(CATEGORY_LLM_CONTROL)
    def do_CURRENT_EXTRACTION_MODEL(self, _):
        """Displays the current extraction language model."""
        from ara_cli.prompt_handler import LLMSingleton
        
        print(LLMSingleton.get_extraction_model())

    def _complete_llms(self, text, line, begidx, endidx):
        llm_config = self._retrieve_llm_config()
        models = [name for name in llm_config.keys()]

        if not text:
            completions = models
        else:
            completions = [model for model in models if model.startswith(text)]

        return completions

    def complete_CHOOSE_MODEL(self, text, line, begidx, endidx):
        return self._complete_llms(text, line, begidx, endidx)

    def complete_CHOOSE_EXTRACTION_MODEL(self, text, line, begidx, endidx):
        return self._complete_llms(text, line, begidx, endidx)

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_NEW(self, chat_name):
        """Create a new chat. Optionally provide a chat name in-line: NEW new_chat"""
        if chat_name == "":
            chat_name = input("What should be the new chat name? ")
        current_directory = os.path.dirname(self.chat_name)
        chat_file_path = os.path.join(current_directory, chat_name)
        self.__init__(chat_file_path)

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_RERUN(self, _):
        """Rerun the last prompt in the chat file"""
        self.resend_message()

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_CLEAR(self, _):
        """Clear the chat and the file containing it"""
        user_input = input("Are you sure you want to clear the chat? (y/N): ")
        if user_input.lower() != 'y':
            return
        self.create_empty_chat_file(self.chat_name)
        self.chat_history = self.load_chat_history(self.chat_name)
        print(f"Cleared content of {self.chat_name}")

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_LOAD_RULES(self, rules_name):
        """Load rules from ./prompt.data/*.rules.md or from a specified template directory if an argument is given. Specify global/<rules_template> to access globally defined rules templates"""
        self._load_template_helper(rules_name, "rules", "*.rules.md")

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_LOAD_INTENTION(self, intention_name):
        """Load intention from ./prompt.data/*.intention.md or from a specified template directory if an argument is given. Specify global/<intention_template> to access globally defined intention templates"""
        self._load_template_helper(intention_name, "intention", "*.intention.md")

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_LOAD_COMMANDS(self, commands_name):
        """Load commands from ./prompt.data/*.commands.md or from a specified template directory if an argument is given. Specify global/<commands_template> to access globally defined commands templates"""
        self._load_template_helper(commands_name, "commands", "*.commands.md")

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_LOAD_BLUEPRINT(self, blueprint_name):
        """Load specified blueprint. Specify global/<blueprint_name> to access globally defined blueprints"""
        self._load_template_from_global_or_local(blueprint_name, "blueprint")

    def _load_helper(self, directory: str, pattern: str, file_type: str, exclude_pattern: str | None = None):
        import glob

        directory_path = os.path.join(os.path.dirname(self.chat_name), directory)
        file_pattern = os.path.join(directory_path, pattern)

        exclude_files = []
        matching_files = glob.glob(file_pattern)
        if exclude_pattern:
            exclude_files = glob.glob(exclude_pattern)
            matching_files = list(set(matching_files) - set(exclude_files))

        if not matching_files:
            print(f"No {file_type} file found.")
            return

        file_path = self.choose_file_to_load(matching_files, pattern)

        if file_path is None:
            return

        self.add_prompt_tag_if_needed(self.chat_name)
        if self.load_file(file_path):
            print(f"Loaded {file_type} from {os.path.basename(file_path)}")

    def _load_template_from_global_or_local(self, template_name, template_type):
        from ara_cli.template_manager import TemplatePathManager
        from ara_cli.ara_config import ConfigManager
        from ara_cli.directory_navigator import DirectoryNavigator

        plurals = {
            "commands": "commands",
            "rules": "rules"
        }

        plural = f"{template_type}s"
        if template_type in plurals:
            plural = plurals[template_type]

        if template_name.startswith("global/"):
            directory = f"{TemplatePathManager.get_template_base_path()}/prompt-modules/{plural}/"
            self._load_helper(directory, template_name.removeprefix("global/"), template_type)
            return

        ara_config = ConfigManager.get_config()
        navigator = DirectoryNavigator()

        original_directory = os.getcwd()
        navigator.navigate_to_target()
        local_templates_path = ara_config.local_prompt_templates_dir
        os.chdir("..")
        local_templates_path = os.path.join(os.getcwd(), local_templates_path)
        os.chdir(original_directory)

        custom_prompt_templates_subdir = self.config.custom_prompt_templates_subdir
        template_directory = f"{local_templates_path}/{custom_prompt_templates_subdir}/{plural}"
        self._load_helper(template_directory, template_name, template_type)

    def _load_template_helper(self, template_name, template_type, default_pattern):
        if not template_name:
            self._load_helper("prompt.data", default_pattern, template_type)
            return

        self._load_template_from_global_or_local(template_name=template_name, template_type=template_type)

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    @cmd2.with_argparser(extract_parser)
    def do_EXTRACT(self, args):
        """Search for markdown code blocks containing "# [x] extract" as first line and "# filename: <path/filename>" as second line and copy the content of the code block to the specified file. The extracted code block is then marked with "# [v] extract"."""
        from ara_cli.commands.extract_command import ExtractCommand

        command = ExtractCommand(
            file_name=self.chat_name,
            force=args.force,
            write=args.write,
            output=self.poutput
        )
        command.execute()

    def _find_givens_files(self, file_name: str) -> list[str]:
        """
        Finds the givens files to be processed.
        - If file_name is provided, it resolves that path.
        - Otherwise, it looks for default givens files.
        - If no defaults are found, it prompts the user.
        Returns a list of absolute file paths or an empty list if none are found.
        """
        base_directory = os.path.dirname(self.chat_name)

        def resolve_path(name):
            """Inner helper to resolve a path relative to chat, then absolute."""
            relative_path = os.path.join(base_directory, name)
            if os.path.exists(relative_path):
                return relative_path
            if os.path.exists(name):
                return name
            return None

        if file_name:
            path = resolve_path(file_name)
            if path:
                return [path]
            relative_path_for_error = os.path.join(base_directory, file_name)
            self.perror(f"No givens file found at {relative_path_for_error} or {file_name}")
            return []

        # If no file_name, check for defaults
        default_files_to_check = [
            os.path.join(base_directory, "prompt.data", "config.prompt_givens.md"),
            os.path.join(base_directory, "prompt.data", "config.prompt_global_givens.md")
        ]
        existing_defaults = [f for f in default_files_to_check if os.path.exists(f)]
        if existing_defaults:
            return existing_defaults

        # No defaults found, prompt user
        user_input = input("Please specify a givens file: ")
        if not user_input:
            self.poutput("Aborting.")
            return []
        
        path = resolve_path(user_input)
        if path:
            return [path]
        self.perror(f"No givens file found at {user_input}. Aborting.")
        return []

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_LOAD_GIVENS(self, file_name):
        """Load all files listed in a ./prompt.data/config.prompt_givens.md and ./prompt.data/config.prompt_global_givens.md"""
        from ara_cli.prompt_handler import load_givens

        givens_files_to_process = self._find_givens_files(file_name)
        if not givens_files_to_process:
            self.poutput("No givens files to load.")
            return

        for givens_path in givens_files_to_process:
            # The givens_path is absolute, and load_givens reconstructs absolute paths
            # from the markdown file. No directory change is needed.
            content, _ = load_givens(givens_path)

            with open(self.chat_name, 'a', encoding='utf-8') as chat_file:
                chat_file.write(content)

            self.poutput(f"Loaded files listed and marked in {givens_path}")

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_SEND(self, _):
        """Send prompt to the LLM"""
        message = "\n".join(self.message_buffer)
        self.save_message(Chat.ROLE_PROMPT, message)
        self.send_message()

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_LOAD_TEMPLATE(self, template_name):
        """Load artefact template"""
        from ara_cli.artefact_models.artefact_templates import template_artefact_of_type

        artefact = template_artefact_of_type(''.join(template_name))
        if not artefact:
            raise ValueError(f"No template for '{template_name}' found.")
        write_content = artefact.serialize()
        self.add_prompt_tag_if_needed(self.chat_name)
        with open(self.chat_name, 'a', encoding='utf-8') as chat_file:
            chat_file.write(write_content)
        print(f"Loaded {template_name} artefact template")

    def complete_LOAD_TEMPLATE(self, text, line, begidx, endidx):
        return self._complete_classifiers(text, line, begidx, endidx)

    def _complete_classifiers(self, text, line, begidx, endidx):
        from ara_cli.classifier import Classifier

        classifiers = Classifier.ordered_classifiers()
        if not text:
            completions = classifiers
        else:
            completions = [classifier for classifier in classifiers if classifier.startswith(text)]

        return completions


    def _get_plural_template_type(self, template_type: str) -> str:
        """Determines the plural form of a template type."""
        plurals = {"commands": "commands", "rules": "rules"}
        return plurals.get(template_type, f"{template_type}s")

    def _find_project_root(self) -> str | None:
        """
        Finds the project root by searching for an 'ara' directory,
        starting from the chat file's directory and moving upwards.
        """
        current_dir = os.path.dirname(self.chat_name)
        while True:
            if os.path.isdir(os.path.join(current_dir, 'ara')):
                return current_dir
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:  # Reached the filesystem root
                return None
            current_dir = parent_dir

    def _gather_templates_from_path(self, search_path: str, templates_set: set, prefix: str = ""):
        """
        Scans a given path for items and adds them to the provided set,
        optionally prepending a prefix.
        """
        import glob
        if not os.path.isdir(search_path):
            return
        for path in glob.glob(os.path.join(search_path, '*')):
            templates_set.add(f"{prefix}{os.path.basename(path)}")

    def _get_available_templates(self, template_type: str) -> list[str]:
        """
        Scans for available global and project-local custom templates.
        This method safely searches for template files without changing the
        current directory, making it safe for use in autocompleters.

        Args:
            template_type: The type of template to search for (e.g., 'rules').

        Returns:
            A sorted list of unique template names. Global templates are
            prefixed with 'global/'.
        """
        from ara_cli.template_manager import TemplatePathManager

        plural_type = self._get_plural_template_type(template_type)
        templates = set()

        # 1. Find Global Templates
        try:
            global_base_path = TemplatePathManager.get_template_base_path()
            global_template_dir = os.path.join(global_base_path, "prompt-modules", plural_type)
            self._gather_templates_from_path(global_template_dir, templates, prefix="global/")
        except Exception:
            pass  # Silently ignore if global templates are not found

        # 2. Find Local Custom Templates
        try:
            project_root = self._find_project_root()
            if project_root:
                local_templates_base = os.path.join(project_root, self.config.local_prompt_templates_dir)
                custom_dir = os.path.join(local_templates_base, self.config.custom_prompt_templates_subdir, plural_type)
                self._gather_templates_from_path(custom_dir, templates)
        except Exception:
            pass  # Silently ignore if local templates cannot be resolved

        return sorted(list(templates))

    def _template_completer(self, text: str, template_type: str) -> list[str]:
        """Generic completer for different template types."""
        available_templates = self._get_available_templates(template_type)
        if not text:
            return available_templates
        return [t for t in available_templates if t.startswith(text)]

    def complete_LOAD_RULES(self, text, line, begidx, endidx):
        """Completer for the LOAD_RULES command."""
        return self._template_completer(text, "rules")

    def complete_LOAD_INTENTION(self, text, line, begidx, endidx):
        """Completer for the LOAD_INTENTION command."""
        return self._template_completer(text, "intention")

    def complete_LOAD_COMMANDS(self, text, line, begidx, endidx):
        """Completer for the LOAD_COMMANDS command."""
        return self._template_completer(text, "commands")

    def complete_LOAD_BLUEPRINT(self, text, line, begidx, endidx):
        """Completer for the LOAD_BLUEPRINT command."""
        return self._template_completer(text, "blueprint")
