"""
standalone script to run the file_lister to list all files of a directory tree in this way:
```tree
ara
├── agile_artefact_deletion.data
│   ├── feature.exploration.md
│   └── steps.exploration.md
├── agile_artefact_deletion.feature
├── agile_artefact_prompt_creation.data
│   ├── feature.exploration.md
│   ├── feature_exploration.docx
│   ├── prompt.data
│   │   ├── feature.prompt
│   │   └── rules.md
│   ├── prompt_order.exploration.md
│   └── steps.exploration.md
```

formated in the resultsfile "config.prompt_givens.md" like this:
```markdown
# ara
    - [] agile_artefact_deletion.feature
## agile_artefact_deletion.data
    - [] feature.exploration.md
    - [] steps.exploration.md
## agile_artefact_prompt_creation.data
    - [] feature.exploration.md
    - [] feature_exploration.docx
    - [] prompt_order.exploration.md
    - [] steps.exploration.md
### prompt.data
    - [] feature.prompt
    - [] rules.md
```
Usage:
python run_file_lister.py ara,src,test *.py,*.md,*.task"

Warning: this test script has a little bug and always needs at least 2 file types listed, the generate list function itself works correctly
"""
from file_lister import generate_markdown_listing
import sys

def parse_input(input_str):
    """Helper function to parse the command line input."""
    return input_str.split(',') if input_str else []

if __name__ == "__main__":
    if len(sys.argv) == 3:
        directories = parse_input(sys.argv[1])
        file_types_to_be_listed = parse_input(sys.argv[2])
    elif len(sys.argv) == 2:
        directories = parse_input(sys.argv[1])
        file_types_to_be_listed = []  # Assume no specific file types if only one argument is given
    else:
        print("Usage: python run_file_lister.py [directories] [file_types]")
        print("Example: python run_file_lister.py ara,src,test *.py,*.md,*.task")
        sys.exit(1)

    print(f"Directories to be listed: {directories}")
    print(f"File types to be listed:  {file_types_to_be_listed}")

    if not directories:
        print("Error: No directories provided.")
        sys.exit(1)

    if not file_types_to_be_listed:
        print("Warning: No file types specified, all files will be listed.")

    generate_markdown_listing(directories, file_types_to_be_listed)
