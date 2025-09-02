import re
import json
import os
import json_repair
from markdown_it import MarkdownIt
from ara_cli.prompt_handler import send_prompt, get_file_content
from ara_cli.classifier import Classifier
from ara_cli.directory_navigator import DirectoryNavigator
from ara_cli.artefact_models.artefact_mapping import title_prefix_to_artefact_class


def extract_code_blocks_md(markdown_text):
    md = MarkdownIt()
    tokens = md.parse(markdown_text)
    code_blocks = [token.content for token in tokens if token.type == 'fence']
    return code_blocks


def extract_responses(document_path, relative_to_ara_root=False, force=False, write=False):
    print(f"Starting extraction from '{document_path}'")
    block_extraction_counter = 0

    with open(document_path, 'r', encoding='utf-8', errors='replace') as file:
        content = file.read()

    cwd = os.getcwd()
    if relative_to_ara_root:
        navigator = DirectoryNavigator()
        navigator.navigate_to_target()
        os.chdir('..')

    code_blocks_found = extract_code_blocks_md(content)
    updated_content = content

    for block in code_blocks_found:
        block_lines = block.split('\n')

        if "# [x] extract" not in block_lines[0]:
            continue
        print("Block found and processed.")

        block_lines = block_lines[1:]

        file_path_search = re.search(r"# filename: (.+)", block_lines[0])

        if file_path_search:
            file_path = file_path_search.group(1).strip()
            print(f"Filename extracted: {file_path}")

            block_lines = block_lines[1:]  # Remove first line again after removing filename line
            block = '\n'.join(block_lines)

            handle_existing_file(file_path, block, force, write)
            block_extraction_counter += 1

            # Update the markdown content
            updated_content = update_markdown(content, block, file_path)
        else:
            # Extract artefact
            artefact_class = None
            for line in block_lines[:2]:
                words = line.strip().split(' ')
                if not words:
                    continue
                first_word = words[0]
                if first_word not in title_prefix_to_artefact_class:
                    continue
                artefact_class = title_prefix_to_artefact_class[first_word]
            if not artefact_class:
                print("No filename found, skipping this block.")
                continue
            artefact = artefact_class.deserialize('\n'.join(block_lines))
            serialized_artefact = artefact.serialize()

            original_directory = os.getcwd()
            directory_navigator = DirectoryNavigator()
            directory_navigator.navigate_to_target()

            artefact_path = artefact.file_path
            directory = os.path.dirname(artefact_path)
            os.makedirs(directory, exist_ok=True)
            handle_existing_file(artefact_path, serialized_artefact, force, write)

            os.chdir(original_directory)

            # TODO: make update_markdown work block by block instead of updating the whole document at once
            block_extraction_counter += 1
            updated_content = update_markdown(content, block, None)

    os.chdir(cwd)
    # Save the updated markdown content
    with open(document_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)

    print(f"End of extraction. Found {block_extraction_counter} blocks.")


def modify_and_save_file(response, file_path):
    print(f"Debug: Modifying and saving file {file_path}")
    try:
        response_data = json_repair.loads(response)
        filename_from_response = response_data['filename']
        print(f"""Found in JSON merge response {response[:200]} ...
        the file {filename_from_response}
        loaded as this content string: 
        {response_data['content'][:100]} ...
        """)

        if filename_from_response != file_path:
            user_decision = prompt_user_decision("Filename does not match, overwrite? (y/n): ")
            if user_decision.lower() not in ['y', 'yes']:
                print("Debug: User chose not to overwrite")
                print("Skipping block.")
                return

        with open(file_path, 'w', encoding='utf-8', errors='replace') as file:
            file.write(response_data['content'])
            print(f"File {file_path} updated successfully.")
    except json.JSONDecodeError as ex:
        print(f"ERROR: Failed to decode JSON response: {ex}")


def prompt_user_decision(prompt):
    return input(prompt)


def determine_should_create(skip_query=False):
    if skip_query:
        return True
    user_decision = prompt_user_decision("File does not exist. Create? (y/n): ")
    if user_decision.lower() in ['y', 'yes']:
        return True
    return False


def create_file_if_not_exist(filename, content, skip_query=False):
    try:
        if not os.path.exists(filename):
            if determine_should_create(skip_query):
                # Ensure the directory exists
                os.makedirs(os.path.dirname(filename), exist_ok=True)

                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(content)
                    print(f"File {filename} created successfully.")
            else:
                print("Automatic file creation skipped by user.")

    except OSError as e:
        print(f"Error: {e}")
        print(f"Failed to create file {filename} due to an OS error")


def create_prompt_for_file_modification(content_str, filename):
    if not os.path.exists(filename):
        print(f"WARNING: {filename} for merge prompt creation does not exist.")
        return

    content_of_existing_file = json.dumps(get_file_content(filename))
    content = json.dumps(content_str)

    prompt_text = f"""
    * given this new_content: 
    ```
    {content}
    ```
    * and given this existing file {filename}
    ```
    {content_of_existing_file}
    ```
    * Merge the new content into {filename}.
    * Include only the provided information; do not add any new details.
    * Use the following JSON format for the prompt response of the merged file:
    {{
        "filename": "path/filename.filextension",
        "content":  "full content of the modified file in valid json format"
    }}
    """

    # print(f"Debug: modification prompt created: {prompt_text}")

    return prompt_text


def handle_existing_file(filename, block_content, skip_query=False, write=False):
    if not os.path.isfile(filename):
        print(f"File {filename} does not exist, attempting to create")
        create_file_if_not_exist(filename, block_content, skip_query)
    elif write:
        print(f"File {filename} exists. Overwriting without LLM merge as requested.")
        try:
            directory = os.path.dirname(filename)
            if directory:
                os.makedirs(directory, exist_ok=True)
            with open(filename, 'w', encoding='utf-8', errors='replace') as file:
                file.write(block_content)
            print(f"File {filename} overwritten successfully.")
        except OSError as e:
            print(f"Error: {e}")
            print(f"Failed to overwrite file {filename} due to an OS error")
    else:
        print(f"File {filename} exists, creating modification prompt")
        prompt_text = create_prompt_for_file_modification(block_content, filename)
        if prompt_text is None:
            return

        messages = [{"role": "user", "content": prompt_text}]
        response = ""

        for chunk in send_prompt(messages, purpose='extraction'):
            content = chunk.choices[0].delta.content
            if content:
                response += content
        modify_and_save_file(response, filename)


def extract_and_save_prompt_results(classifier, param, write=False):
    sub_directory = Classifier.get_sub_directory(classifier)
    prompt_log_file = f"ara/{sub_directory}/{param}.data/{classifier}.prompt_log.md"
    print(f"Extract marked sections from: {prompt_log_file}")

    extract_responses(prompt_log_file, write=write)


def update_markdown(original_content, block_content, filename):
    """
    Update the markdown content by changing the extract block from "# [x] extract" to "# [v] extract"
    """
    updated_content = original_content.replace("# [x] extract", "# [v] extract")
    return updated_content
