from llama_index.core import (
    SimpleDirectoryReader,
)

from ara_cli.prompt_handler import read_string_from_file
from ara_cli.ara_config import ConfigManager
from ara_cli.classifier import Classifier

import os

def find_files_in_prompt_config_givens(search_file, prompt_givens_file_path):
    """
    Extracts markdown files paths based on checked items and constructs proper paths respecting markdown header hierarchy.
    """
    file_found = False
    header_stack = []
    modified_lines = []  # To store the modified file content

    with open(prompt_givens_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip().startswith('#'):
                level = line.count('#')
                header = line.strip().strip('#').strip()
                # Adjust the stack based on the current header level
                current_depth = len(header_stack)
                if level <= current_depth:
                    header_stack = header_stack[:level-1]
                header_stack.append(header)
            elif os.path.basename(search_file) in line:
                relative_path = line.split(']')[-1].strip()
                full_path = os.path.join('/'.join(header_stack), relative_path)
                if full_path == search_file:
                    line = line.replace('[]', '[x]')  # Replace "[]" with "[x]"
                    file_found = True
                    print(f"found {search_file} and checked [x] selection box")
            modified_lines.append(line)  # Append potentially modified line to list

    if file_found:
        # Rewrite the file with the modified content if any line was changed
        with open(prompt_givens_file_path, 'w', encoding='utf-8') as file:
            file.writelines(modified_lines)

    return file_found


def print_and_select_retrieved_nodes(classifier, param, nodes):
    if not nodes:
        print("No nodes found.")
        return

    print("found-nodes-list")

    sub_directory = Classifier.get_sub_directory(classifier)
    prompt_givens_file_path = f"ara/{sub_directory}/{param}.data/prompt.data/config.prompt_givens.md"

    for index, source_node in enumerate(nodes, start=1):
        # only propose retrieved nodes with a score greater than 0.6 (usually lower is not interesting at all)
        if source_node.score > 0.4:
            print(f"{index}:\n")
            print(f"filename: {source_node.node.metadata['filepath']}")
            print(f"Score: {source_node.score:.2f}") 
            print(f"node: {source_node.text[:200]}")

            user_input = input("Select this node? [Y/n]: ").strip().lower()

            # Default to 'yes' if the user presses RETURN without input
            if user_input in ['', 'y', 'yes']:
                file_path_proposed_file = source_node.node.metadata['filepath'].replace(os.getcwd(), '').strip('/')
                file_found = find_files_in_prompt_config_givens(file_path_proposed_file, prompt_givens_file_path)

                if not file_found:
                    print(f"File not found: {file_path_proposed_file}. Continue? [Y/n]")

                    continue_input = input().strip().lower()
                    if continue_input not in ['', 'y', 'yes']:
                        break
            elif user_input in ['n', 'no']:
                continue
            else:
                print("Invalid input. Please enter 'Y' or 'n'.")
                continue


def is_directory_not_empty(directory_path, required_exts=None):
    """
    Checks if the specified directory is not empty and optionally if it contains files with specific extensions.

    :param directory_path: Path to the directory to check.
    :param required_exts: List of required file extensions to check for (e.g., [".py", ".md"]). If None, just checks if directory is not empty.

    :return: True if the directory is not empty (and contains files with required extensions if specified), False otherwise.
    """
    try:
        # Attempt to list the contents of the directory
        files_in_directory = os.listdir(directory_path)

        if not files_in_directory:
            # Directory is empty
            print(f"Directory {directory_path} is empty.")
            return False

        if required_exts is None:
            # No specific extensions required, just check if directory is not empty
            return True

        # Check if any files match the required extensions
        for file_name in files_in_directory:
            if any(file_name.endswith(ext) for ext in required_exts):
                return True

        # No files with the required extensions found
        # print(f"Directory {directory_path} does not contain any files with the required extensions: {required_exts}")
        return False

    except FileNotFoundError:
        # Directory does not exist
        print(f"Directory {directory_path} does not exist.")
        return False

    except PermissionError:
        # Not enough permissions to access the directory
        print(f"Directory {directory_path} permission denied.")
        return False


def extract_in_progress_text(input_string):
    """
    Extracts the text starting with '[in-progress]' until the end of the file or until the next '[]'.

    Parameters:
    input_string (str): The input string from which to extract the text.

    Returns:
    str: The extracted text or an empty string if '[in-progress]' is not found.
    """
    import re

    pattern = r'\[@in-progress\](.*?)(\[\@.*?\]|\[\]|$)'
    match = re.search(pattern, input_string, re.DOTALL)

    if match:
        extracted_text = match.group(1).strip()
        return extracted_text
    else:
        return ""


def search_and_add_relevant_files_to_prompt_givens(classifier, param):
    from ara_cli.codefusionretriever import CodeFusionRetriever
    from ara_cli.codehierachieretriever import CodeHierarchyRetriever

    config = ConfigManager.get_config()
    dir_list = ["ara"] + [item for ext in config.ext_code_dirs for key, item in ext.items()] + [config.doc_dir] + [config.glossary_dir]
    documents = []
    exts = [".py", ".ipynb"] # python and jupyter Notebooks

    for directory in dir_list:
        for root, dirs, files in os.walk(directory):
            if is_directory_not_empty(root, required_exts=exts):
                print(f"Loading {root} to RAG documents")
                documents += SimpleDirectoryReader(
                    input_dir=root,
                    required_exts=exts,
                    file_metadata=lambda x: {"filepath": x},
                    recursive=False).load_data()

    sub_directory = Classifier.get_sub_directory(classifier)
    prompt_path = f"ara/{sub_directory}/{param}.{classifier}"
    context = read_string_from_file(prompt_path)

    # extract an @in-progress task to-do description as query string if possible.
    query_string = extract_in_progress_text(context)

    # in case an artefact without [@in-progress] block is used, use as default fall back the whole context of the used artefact
    if query_string == "":
        query_string = f"{context}"

    print(f"Query string for retrieval: {query_string}")

    codefusionretriever = CodeFusionRetriever(documents)
    nodes = codefusionretriever.retrieve(query_string)

    print_and_select_retrieved_nodes(classifier, param, nodes)

    print(f"Hierarchy Retriever")
    codehierarchyretriever = CodeHierarchyRetriever(documents)
    codehierarchyretriever.retrieve(query_string)
