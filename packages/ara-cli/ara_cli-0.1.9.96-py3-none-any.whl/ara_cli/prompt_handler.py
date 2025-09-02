import base64
import litellm
from ara_cli.classifier import Classifier
from ara_cli.artefact_creator import ArtefactCreator
from ara_cli.template_manager import TemplatePathManager
from ara_cli.ara_config import ConfigManager, LLMConfigItem
from ara_cli.file_lister import generate_markdown_listing
from os.path import exists, join
import os
from os import makedirs
from re import findall
import re
import shutil
import glob
import logging


class LLMSingleton:
    _instance = None
    _default_model = None
    _extraction_model = None

    def __init__(self, default_model_id, extraction_model_id):
        config = ConfigManager().get_config()
        default_config_data = config.llm_config.get(str(default_model_id))

        if not default_config_data:
            raise ValueError(f"No configuration found for the default model: {default_model_id}")
        self.default_config_params = default_config_data.model_dump(exclude_none=True)

        extraction_config_data = config.llm_config.get(str(extraction_model_id))
        if not extraction_config_data:
            raise ValueError(f"No configuration found for the extraction model: {extraction_model_id}")
        self.extraction_config_params = extraction_config_data.model_dump(exclude_none=True)

        LLMSingleton._default_model = default_model_id
        LLMSingleton._extraction_model = extraction_model_id
        LLMSingleton._instance = self

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            config = ConfigManager().get_config()
            default_model = config.default_llm
            if not default_model:
                if not config.llm_config:
                    raise ValueError("No LLM configurations are defined in the configuration file.")
                default_model = next(iter(config.llm_config))

            extraction_model = getattr(config, 'extraction_llm', default_model)
            if not extraction_model:
                extraction_model = default_model

            cls(default_model, extraction_model)
        return cls._instance

    @classmethod
    def get_config_by_purpose(cls, purpose='default'):
        """
        purpose= 'default' or 'extraction'
        """
        instance = cls.get_instance()
        if purpose == 'extraction':
            return instance.extraction_config_params.copy()
        return instance.default_config_params.copy()

    @classmethod
    def set_default_model(cls, model_name):
        """Sets the default language model for the current session."""
        cls.get_instance()
        if model_name == cls._default_model:
            return cls._instance
        cls(model_name, cls._extraction_model)
        return cls._instance

    @classmethod
    def set_extraction_model(cls, model_name):
        """Sets the extraction language model for the current session."""
        cls.get_instance()
        if model_name == cls._extraction_model:
            return cls._instance
        cls(cls._default_model, model_name)
        return cls._instance

    @classmethod
    def get_default_model(cls):
        """Gets the default model name stored in the singleton instance."""
        if cls._instance is None:
            cls.get_instance()
        return cls._default_model

    @classmethod
    def get_extraction_model(cls):
        """Gets the extraction model name stored in the singleton instance."""
        if cls._instance is None:
            cls.get_instance()
        return cls._extraction_model


def write_string_to_file(filename, string, mode):
    with open(filename, mode, encoding='utf-8') as file:
        file.write(f"\n{string}\n")
    return file


def read_string_from_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text


def _is_valid_message(message: dict) -> bool:
    """
    Checks if a message in a prompt is valid (i.e., not empty).
    It handles both string content and list content (for multimodal inputs).
    """
    content = message.get('content')

    if isinstance(content, str):
        return content.strip() != ''
    
    if isinstance(content, list):
        # For multimodal content, check if there's at least one non-empty text part.
        return any(
            item.get('type') == 'text' and item.get('text', '').strip() != ''
            for item in content
        )
        
    return False


def send_prompt(prompt, purpose='default'):
    """Prepares and sends a prompt to the LLM, streaming the response."""
    chat_instance = LLMSingleton.get_instance()
    config_parameters = chat_instance.get_config_by_purpose(purpose)

    config_parameters.pop("provider", None)

    filtered_prompt = [msg for msg in prompt if _is_valid_message(msg)]

    completion = litellm.completion(
        **config_parameters,
        messages=filtered_prompt,
        stream=True
    )
    for chunk in completion:
        yield chunk


def describe_image(image_path: str) -> str:
    """
    Send an image to the LLM and get a text description.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Text description of the image
    """
    import base64
    
    # Read and encode the image
    with open(image_path, 'rb') as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Determine image type
    image_extension = os.path.splitext(image_path)[1].lower()
    mime_type = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp'
    }.get(image_extension, 'image/png')
    
    # Create message with image
    message = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Please describe this image in detail. If it contains text, transcribe it exactly. If it's a diagram or chart, explain its structure and content. If it's a photo or illustration, describe what you see."
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{base64_image}"
                }
            }
        ]
    }
    
    # Get response from LLM using the extraction model purpose
    response_text = ""
    for chunk in send_prompt([message], purpose='extraction'):
        chunk_content = chunk.choices[0].delta.content
        if chunk_content:
            response_text += chunk_content
    
    return response_text.strip()


def append_headings(classifier, param, heading_name):
    sub_directory = Classifier.get_sub_directory(classifier)

    artefact_data_path = f"ara/{sub_directory}/{param}.data/{classifier}.prompt_log.md"

    # Check if the file exists, and if not, create an empty file
    if not os.path.exists(artefact_data_path):
        with open(artefact_data_path, 'w', encoding='utf-8') as file:
            file.write("")

    content = read_string_from_file(artefact_data_path)
    pattern = r'## {}_(\d+)'.format(heading_name)
    matches = findall(pattern, content)

    max_number = 1
    if matches:
        max_number = max(map(int, matches)) + 1
    heading = f"## {heading_name}_{max_number}"

    write_string_to_file(artefact_data_path, heading, 'a')


def write_prompt_result(classifier, param, text):
    sub_directory = Classifier.get_sub_directory(classifier)

    # TODO change absolute path to relative path with directory navigator
    artefact_data_path = f"ara/{sub_directory}/{param}.data/{classifier}.prompt_log.md"
    write_string_to_file(artefact_data_path, text, 'a')


def prompt_data_directory_creation(classifier, parameter):
    sub_directory = Classifier.get_sub_directory(classifier)
    prompt_data_path = f"ara/{sub_directory}/{parameter}.data/prompt.data"
    if not exists(prompt_data_path):
        makedirs(prompt_data_path)
    return prompt_data_path


def get_file_content(path):
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()


def initialize_prompt_templates(classifier, parameter):
    prompt_data_path = prompt_data_directory_creation(classifier, parameter)
    prompt_log_path = os.path.dirname(prompt_data_path)

    template_path = os.path.join(os.path.dirname(__file__), 'templates')
    artefact_creator = ArtefactCreator()
    artefact_creator.create_artefact_prompt_files(prompt_log_path, template_path, classifier)

    generate_config_prompt_template_file(prompt_data_path, "config.prompt_templates.md")

    # Mark the relevant artefact in the givens list
    generate_config_prompt_givens_file(prompt_data_path, "config.prompt_givens.md", artefact_to_mark=f"{parameter}.{classifier}")

    generate_config_prompt_global_givens_file(prompt_data_path, "config.prompt_global_givens.md")


def write_template_files_to_config(template_type, config_file, base_template_path):
    template_path = os.path.join(base_template_path, template_type)
    for root, _, files in os.walk(template_path):
        for file in sorted(files):
            config_file.write(f"  - [] {template_type}/{file}\n")


def load_selected_prompt_templates(classifier, parameter):
    sub_directory = Classifier.get_sub_directory(classifier)
    prompt_data_path = f"ara/{sub_directory}/{parameter}.data/prompt.data"
    config_file_path = os.path.join(prompt_data_path, "config.prompt_templates.md")

    if not os.path.exists(config_file_path):
        print("WARNING: config.prompt_templates.md does not exist.")
        return

    with open(config_file_path, 'r', encoding='utf-8') as config_file:
        content = config_file.read()

    global_base_template_path = TemplatePathManager.get_template_base_path()
    local_base_template_path = ConfigManager.get_config().local_prompt_templates_dir

    markdown_items = extract_and_load_markdown_files(config_file_path)

    # Ensure the prompt archive directory exists
    prompt_archive_path = os.path.join(prompt_data_path, "prompt.archive")
    if not os.path.exists(prompt_archive_path):
        os.makedirs(prompt_archive_path)
        print(f"Created archive directory: {prompt_archive_path}")

    for item in markdown_items:
        if item.startswith("custom-prompt-modules"):
            source_path = os.path.join(local_base_template_path, item)
            target_path = os.path.join(prompt_data_path, os.path.basename(item))
        elif item.startswith("prompt-modules"):
            source_path = os.path.join(global_base_template_path, item)
            target_path = os.path.join(prompt_data_path, os.path.basename(item))
        else:
            print(f"WARNING: Unrecognized template type for item {item}.")
            continue

        move_and_copy_files(source_path, prompt_data_path, prompt_archive_path)


def find_files_with_endings(directory, endings):
    """
    this function finds only files in the given directory it does not iterate recursively over sub directories
    """

    # Create an empty dictionary to store files according to their endings
    files_by_ending = {ending: [] for ending in endings}

    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    # Walk through the files list
    for file in files:
        # Check each file to see if it ends with one of the specified endings
        for ending in endings:
            if file.endswith(ending):
                # If it does, append the file to the corresponding list
                files_by_ending[ending].append(file)
                break  # Move to the next file after finding a matching ending

    # Collect and sort files by the order of their endings, flatten the dictionary values into a list
    sorted_files = []
    for ending in endings:
        sorted_files.extend(files_by_ending[ending])

    return sorted_files


def move_and_copy_files(source_path, prompt_data_path, prompt_archive_path):
    """
    method detects existing prompt templates in the prompt.data directory and move them to the prompt.archive directory before new prompt templates are loaded in the prompt.data directory. So it is guaranteed, that only one .rules.md, .commands.md and .intention.md exists in the prompt.data directory
    """
    if os.path.exists(source_path):
        file_name = os.path.basename(source_path)

        # Check the name ending and extension of source path
        endings = [".blueprint.md", ".commands.md", ".rules.md", ".intention.md"]
        if any(file_name.endswith(ext) for ext in endings):
            for ext in endings:
                if file_name.endswith(ext):
                    # Define glob pattern to match all files with the same ending in the prompt_data_path
                    glob_pattern = os.path.join(prompt_data_path, f"*{ext}")

                    # Move all existing files with the same ending to the prompt_archive_path
                    for existing_file in glob.glob(glob_pattern):
                        archived_file_path = os.path.join(prompt_archive_path, os.path.basename(existing_file))
                        shutil.move(existing_file, archived_file_path)
                        print(f"Moved existing prompt-module: {os.path.basename(existing_file)} to prompt.archive")
                    
                    # Copy the source_path file to the prompt_data_path directory
                    target_path = os.path.join(prompt_data_path, file_name)
                    shutil.copy(source_path, target_path)
                    print(f"Loaded new prompt-module: {os.path.basename(target_path)}")

        else:
            print(f"File name {file_name} does not end with one of the specified patterns, skipping move and copy.")
    else:
        print(f"WARNING: template {source_path} does not exist.")


def extract_and_load_markdown_files(md_prompt_file_path):
    """
    Extracts markdown files paths based on checked items and constructs proper paths respecting markdown header hierarchy.
    """
    header_stack = []
    path_accumulator = []
    with open(md_prompt_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip().startswith('#'):
                level = line.count('#')
                header = line.strip().strip('#').strip()
                # Adjust the stack based on the current header level
                current_depth = len(header_stack)
                if level <= current_depth:
                    header_stack = header_stack[:level-1]
                header_stack.append(header)
            elif '[x]' in line:
                relative_path = line.split(']')[-1].strip()
                full_path = os.path.join('/'.join(header_stack), relative_path)
                path_accumulator.append(full_path)
    return path_accumulator


def load_givens(file_path):
    content = ""
    image_data_list = []
    markdown_items = extract_and_load_markdown_files(file_path)

    # Only proceed and add the header if there are marked items to load.
    if not markdown_items:
        return "", []

    content = "### GIVENS\n\n"

    for item in markdown_items:
        if item.lower().endswith(('.png', '.jpeg', '.jpg')):
            with open(item, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")
            image_data_list.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}})
            content += item + "\n"
            content += f'![{item}](data:image/png;base64,{base64_image})' + "\n"
        else:
            # Check if the item specifies line ranges
            # TODO item has currently no trailing [] see extraction and handover method in extract and load 
            # item = f"[10:29] {item}"
            # print(f"found {item}, check for subsection")
            # TODO re.match can not split the item with [] correctly and extract the line numbers
            # TODO logic of subsections is not supported by the update algorithm of the config prompt givens updater
            # TODO extract in lines of *.md files potential images and add them to the image list

            match = re.match(r".*?\[(\d+:\d+(?:,\s*\d+:\d+)*)\]\s+(.+)", item)
            if match:
                line_ranges, file_name = match.groups()
                content += file_name + "\n" + "```\n"
                content += get_partial_file_content(file_name, line_ranges) + "\n"
                content += "```\n\n"
            else:
                content += item + "\n" + "```\n"
                content += get_file_content(item) + "\n"
                content += "```\n\n"
    return content, image_data_list


def get_partial_file_content(file_name, line_ranges):
    """
    Reads specific lines from a file based on the line ranges provided.

    Args:
    file_name (str): The path to the file.
    line_ranges (str): A string representing the line ranges to read, e.g., '10:20,25:30'.

    Returns:
    str: The content of the specified lines.
    """
    line_ranges = line_ranges.strip('[]').split(',')
    lines_to_read = []
    for line_range in line_ranges:
        start, end = map(int, line_range.split(':'))
        lines_to_read.extend(range(start, end + 1))

    partial_content = []
    with open(file_name, 'r', encoding='utf-8') as file:
        for i, line in enumerate(file, 1):
            if i in lines_to_read:
                partial_content.append(line)

    return ''.join(partial_content)


def collect_file_content_by_extension(prompt_data_path, extensions):
    combined_content = ""
    image_data_list = []
    for ext in extensions:
        files = find_files_with_endings(prompt_data_path, [ext])
        for file_name in files:
            file_path = join(prompt_data_path, file_name)
            if ext in [".prompt_givens.md", ".prompt_global_givens.md"]:
                givens, image_data = load_givens(file_path)
                combined_content += givens
                image_data_list.extend(image_data)
            else:
                combined_content += get_file_content(file_path) + "\n\n"
    return combined_content, image_data_list


def prepend_system_prompt(message_list):
    system_prompt = {
        "role": "system",
        "content": "You are a helpful assistant that can process both text and images."
    }
    message_list.insert(0, system_prompt)
    return message_list


def append_images_to_message(message, image_data_list):
    logger = logging.getLogger(__name__)

    logger.debug(f"append_images_to_message called with image_data_list length: {len(image_data_list) if image_data_list else 0}")

    if not image_data_list:
        logger.debug("No images to append, returning original message")
        return message

    message_content = message["content"]
    logger.debug(f"Original message content: {message_content}")

    if isinstance(message_content, str):
        message["content"] = [{"type": "text", "text": message_content}]
    
    message["content"].extend(image_data_list)

    logger.debug(f"Updated message content with {len(image_data_list)} images")

    return message


def create_and_send_custom_prompt(classifier, parameter):
    sub_directory = Classifier.get_sub_directory(classifier)
    prompt_data_path = f"ara/{sub_directory}/{parameter}.data/prompt.data"
    prompt_file_path_markdown = join(prompt_data_path, f"{classifier}.prompt.md")

    extensions = [".blueprint.md", ".rules.md", ".prompt_givens.md", ".prompt_global_givens.md", ".intention.md", ".commands.md"]
    combined_content_markdown, image_data_list = collect_file_content_by_extension(prompt_data_path, extensions)

    with open(prompt_file_path_markdown, 'w', encoding='utf-8') as file:
        file.write(combined_content_markdown)

    prompt = read_string_from_file(prompt_file_path_markdown)
    append_headings(classifier, parameter, "prompt")
    write_prompt_result(classifier, parameter, prompt)

    message = {
        "role": "user",
        "content": combined_content_markdown
    }

    message_list = [message]

    message_list = append_images_to_message(message_list, image_data_list)
    append_headings(classifier, parameter, "result")

    artefact_data_path = f"ara/{sub_directory}/{parameter}.data/{classifier}.prompt_log.md"
    with open(artefact_data_path, 'a', encoding='utf-8') as file:
        for chunk in send_prompt(message_list):
            chunk_content = chunk.choices[0].delta.content
            if not chunk_content:
                continue
            file.write(chunk_content)
            file.flush()
    # write_prompt_result(classifier, parameter, response)


def generate_config_prompt_template_file(prompt_data_path, config_prompt_templates_name):
    config_prompt_templates_path = os.path.join(prompt_data_path, config_prompt_templates_name)
    config = ConfigManager.get_config()
    global_prompt_template_path = TemplatePathManager.get_template_base_path()
    dir_list = ["ara/.araconfig/custom-prompt-modules"] + [f"{os.path.join(global_prompt_template_path,'prompt-modules')}"]
    file_list = ['*.blueprint.md','*.rules.md','*.intention.md', '*.commands.md']

    print(f"used {dir_list} for prompt templates file listing")
    generate_markdown_listing(dir_list, file_list, config_prompt_templates_path)


def generate_config_prompt_givens_file(prompt_data_path, config_prompt_givens_name, artefact_to_mark=None):
    config_prompt_givens_path = os.path.join(prompt_data_path, config_prompt_givens_name)
    config = ConfigManager.get_config()
    dir_list = ["ara"] + [path for d in config.ext_code_dirs for path in d.values()] + [config.doc_dir] + [config.glossary_dir]

    print(f"used {dir_list} for prompt givens file listing")
    generate_markdown_listing(dir_list, config.ara_prompt_given_list_includes, config_prompt_givens_path)

    # If an artefact is specified, mark it with [x]
    if artefact_to_mark:
        print(f"artefact {artefact_to_mark} marked in related config.prompt_givens.md per default")

        # Read the generated file content
        with open(config_prompt_givens_path, 'r', encoding='utf-8') as file:
            markdown_listing = file.readlines()

        updated_listing = []
        for line in markdown_listing:
            # Use a regular expression to match the exact string
            if re.search(r'\b' + re.escape(artefact_to_mark) + r'\b', line):
                line = line.replace("[]", "[x]")
            updated_listing.append(line)

        # Write the updated listing back to the file
        with open(config_prompt_givens_path, 'w', encoding='utf-8') as file:
            file.write("".join(updated_listing))

def generate_config_prompt_global_givens_file(prompt_data_path, config_prompt_givens_name, artefact_to_mark=None):
    from ara_cli.global_file_lister import generate_global_markdown_listing
    config_prompt_givens_path = os.path.join(prompt_data_path, config_prompt_givens_name)
    config = ConfigManager.get_config()

    if not hasattr(config, 'global_dirs') or not config.global_dirs:
        return

    dir_list = [path for d in config.global_dirs for path in d.values()]
    print(f"used {dir_list} for global prompt givens file listing with absolute paths")
    generate_global_markdown_listing(dir_list, config.ara_prompt_given_list_includes, config_prompt_givens_path)