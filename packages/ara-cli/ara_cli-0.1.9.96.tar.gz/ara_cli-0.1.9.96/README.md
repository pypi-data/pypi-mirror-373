# ara-cli

**ara-cli** is a powerful, open source command-line tool for managing, structuring and automating software development artifacts in line with Behavior-Driven Development (BDD) and AI-assisted processes. With an intuitive interface and platform-independent implementation in Python, ara-cli enables teams to structure business goals, capabilities, features, user stories, and tasks, and to leverage integrated AI/chat capabilities for requirements engineering, documentation, and process automation.

---

## Features

- **Comprehensive Artefact Management:**  
  Create, edit, rename, delete, and list all core artefacts of the software development lifecycle: businessgoals, vision, capabilities, keyfeatures, features, epics, userstories, examples, and tasks.

- **Structured Traceability:**  
  Organize and link artefacts for full traceability from business goals to implementation tasks. Effortlessly navigate artefact hierarchies and dependencies.

- **Integrated AI and Chat:**  
  Interact with AI language models directly from your terminal. Use chat and prompt commands to assist with documentation, requirements refinement, and artefact management.

- **Prompt Templates:**  
  Fetch, use, and manage reusable prompt templates for consistent and efficient requirements and documentation workflows.

- **Artefact Status and User Management:**  
  Assign and query status and responsible users for artefacts to support project coordination and tracking.

- **Automated Quality Assurance:**  
  Scan artefact trees for inconsistencies and automatically correct issues using integrated LLM-powered autofix functionality.

- **Powerful Listing and Search:**  
  List artefacts and filter by type, tags, content, contributor relationships, file extensions, and more.

- **Open Source & Platform Independent:**  
  Implemented in Python and available on PyPI for easy installation and integration into any workflow.

---

## Use Cases

- **Requirements Engineering:**  
  Capture and structure business requirements and user stories with clear traceability.

- **Agile Development:**  
  Manage and automate backlog refinement, sprint planning, and task tracking.

- **AI-Enhanced Productivity:**  
  Use chat and prompt features to accelerate documentation, code review, and knowledge management.

- **Quality Management:**  
  Ensure artefact consistency and high documentation quality via automated scans and fixes.

---

## Quick Start

Install from PyPI:
```bash
pip install ara-cli
````

Create your first feature artefact:

```bash
ara create feature login
```

List all features:

```bash
ara list --include-extension .feature
```

Chat with the integrated AI:

```bash
ara chat
```

Scan and autofix artefacts:

```bash
ara scan
ara autofix
```

---

## Command Overview

| Action                  | Description                                                             |
| ----------------------- | ----------------------------------------------------------------------- |
| create                  | Create a classified artefact with data directory                        |
| delete                  | Delete an artefact and its data directory                               |
| rename                  | Rename an artefact and its data directory                               |
| list, list-tags         | List artefacts, show tags, filter by content, extension, hierarchy etc. |
| prompt, chat            | Use AI-powered chat and prompt templates for artefact management        |
| template                | Print artefact templates in the terminal                                |
| fetch-templates         | Download and manage reusable prompt templates                           |
| read                    | Output artefact contents and their full contribution chain              |
| reconnect               | Connect artefacts to parent artefacts                                   |
| read-status, set-status | Query and assign status to artefacts                                    |
| read-user, set-user     | Query and assign responsible users                                      |
| classifier-directory    | Show directory of artefact classifiers                                  |
| scan                    | Scan the ARA tree for incompatible or inconsistent artefacts            |
| autofix                 | Automatically correct artefact issues with LLM assistance               |

See `ara -h` for the complete list of commands and usage examples.

---

## Artefact Structure

ara-cli organizes your project artefacts in a clear directory structure:

```
./ara/
   ├── businessgoals/
   ├── vision/
   ├── capabilities/
   ├── keyfeatures/
   ├── features/
   ├── epics/
   ├── userstories/
   ├── examples/
   ├── tasks/
```

---

## Example Workflows

- **Create a new feature and link it to a user story:**

```bash
ara create feature payment contributes-to userstory checkout
```

- **Read an artefact's content and its full parent chain:**

```bash
ara read task implement_api --branch
```

- **List tasks containing specific content:**

```bash
ara list --include-extension .task --include-content "API integration"
```

- **Automate prompt-based LLM interaction for a task:**

```bash
ara prompt send task implement_api
ara prompt extract task implement_api
```

---

## Requirements

- Python 3.8+
- Platform-independent; tested on Linux, macOS, and Windows

---

## License

This project is open source and freely available under the [MIT License](vector://vector/webapp/LICENSE).

---

## Links

- **PyPI:** https://pypi.org/project/ara-cli/
- **Source code:** \[GitHub link or repository URL\]
- **Documentation:** \[Link if available\]

---

## Contributing

Contributions, issues, and feature requests are welcome! Please open an issue or submit a pull request via GitHub.

---

**ara-cli — Structure your development. Automate with AI. Build better software.**

