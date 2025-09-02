### COMMANDS FOR ERROR FIXING
Your job is now to fix the error:
* Silently analyze the described error and draft a potential solution to the fix the error
* Silently review the provided source files to understand both the current faulty implementation and the intended changes to fix the error.
* Develop implementation strategies that minimize code changes, prefer reusing existing methods over new implementations.
* Output a "change table" listing all necessary changes. Include an example line for reference:
  | filename       | method                                   | short description of intended changes      |
  | {filename}.py  | {method name of existing or new method}  | {detailed explanation of the changes serving as code generation prompt}      |

* Implement the changes as specified in the change table, ensuring your generated code blocks are not just code snippets but at complete method levels. Use for every single generated code block this format:
```python
# [ ] extract
# filename: {path/filename}.py
{python code}
```
* the extract and filename statements are only allowed once per code block

* Adhere strictly to established rules for high-quality Python code and architecture.

* If essential information is missing for code generation, issue a warning: "WARNING: Information is missing to do a correct implementation." Specify what information is lacking and suggest how it might be retrieved.