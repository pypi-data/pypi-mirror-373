import os
from ara_cli.classifier import Classifier
from ara_cli.prompt_handler import generate_config_prompt_template_file, generate_config_prompt_givens_file


def read_file(filepath):
    """Read and return the content of a file."""
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()


def write_file(filepath, content):
    """Write content to a file."""
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)


def find_checked_items(content):
    """
    Find all checked items ([x]) in the content and return a list of their sections and items.
    """
    sections = []
    checked_items = []
    lines = content.split('\n')

    for line in lines:
        if line.startswith('#'):
            header_level = line.count('#')
            sections = sections[:header_level-1]  # Trim sections to the current header level
            sections.append(line)
        if '[x]' in line:
            item = ''.join(sections) + line.strip()
            checked_items.append(item)

    return checked_items


def update_items_in_file(content, checked_items):
    """
    Update items in the content based on the checked items found.
    """
    sections = []
    updated_lines = []
    lines = content.split('\n')

    for line in lines:
        if line.startswith('#'):
            header_level = line.count('#')
            sections = sections[:header_level-1]  # Trim sections to the current header level
            sections.append(line)
        section_path = ''.join(sections)
        if '[]' in line:
            for item in checked_items:
                if section_path in item and line.strip() in item.replace('[x]', '[]'):
                    line = line.replace('[]', '[x]')
                    #print(f"Debug Updated: {item}")
                    break
        updated_lines.append(line)

    return '\n'.join(updated_lines)


def update_config_prompt_files(input1, input2):
    """
    Update the prompt config files with the new chat.
    """
    content1 = read_file(input1)
    content2 = read_file(input2)

    checked_items = find_checked_items(content1)

    updated_content2 = update_items_in_file(content2, checked_items)

    write_file(input2, updated_content2)

    # Overwrite input1 with input2 and delete input2
    os.replace(input2, input1)

    print("Update process completed.")


def ensure_directory_exists(path):
    """Ensure that the directory exists."""
    if not os.path.exists(path):
        os.makedirs(path)


def handle_existing_file(file_path, tmp_file_path, generate_file_func, automatic_update):
    """Handle the existing file based on user input or automatic update."""
    if not os.path.exists(file_path):
        generate_file_func(os.path.dirname(file_path), os.path.basename(file_path))
    else:
        if automatic_update:
            generate_file_func(os.path.dirname(file_path), os.path.basename(tmp_file_path))
            update_config_prompt_files(file_path, tmp_file_path)
        else:
            action = input(f"{file_path} already exists. Do you want to overwrite (o) or update (u)? ")
            if action.lower() == 'o':
                generate_file_func(os.path.dirname(file_path), os.path.basename(file_path))
            elif action.lower() == 'u':
                generate_file_func(os.path.dirname(file_path), os.path.basename(tmp_file_path))
                update_config_prompt_files(file_path, tmp_file_path)


def update_artefact_config_prompt_files(classifier, param, automatic_update=False):
    from ara_cli.prompt_handler import generate_config_prompt_global_givens_file
    sub_directory = Classifier.get_sub_directory(classifier)
    artefact_data_path = os.path.join("ara", sub_directory, f"{param}.data")
    prompt_data_path = os.path.join(artefact_data_path, "prompt.data")

    ensure_directory_exists(prompt_data_path)

    givens_file_name = "config.prompt_givens.md"
    givens_tmp_file_name = "config.prompt_givens_tmp.md"
    global_givens_file_name = "config.prompt_global_givens.md"
    global_givens_tmp_file_name = "config.prompt_global_givens_tmp.md"
    template_file_name = "config.prompt_templates.md"
    template_tmp_file_name = "config.prompt_templates_tmp.md"

    prompt_config_givens = os.path.join(prompt_data_path, givens_file_name)
    prompt_config_givens_tmp = os.path.join(prompt_data_path, givens_tmp_file_name)
    prompt_config_global_givens = os.path.join(prompt_data_path, global_givens_file_name)
    prompt_config_global_givens_tmp = os.path.join(prompt_data_path, global_givens_tmp_file_name)
    prompt_config_templates = os.path.join(prompt_data_path, template_file_name)
    prompt_config_templates_tmp = os.path.join(prompt_data_path, template_tmp_file_name)

    handle_existing_file(prompt_config_givens, prompt_config_givens_tmp, generate_config_prompt_givens_file, automatic_update)
    handle_existing_file(prompt_config_global_givens, prompt_config_global_givens_tmp, generate_config_prompt_global_givens_file, automatic_update)
    handle_existing_file(prompt_config_templates, prompt_config_templates_tmp, generate_config_prompt_template_file, automatic_update)