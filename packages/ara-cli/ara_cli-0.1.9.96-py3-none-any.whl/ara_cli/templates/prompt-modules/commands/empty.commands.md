### COMMANDS FOR ...
Your job is now:
* remember you are strictly following your given RULES AS EXPERT <role defined in rules file> for code and architectural code quality
* ...
   
* return your results in the following format, ensuring your generated code blocks are not just code snippets but at complete method levels. Use for every single generated code block this format:
```python
# [ ] extract
# filename: {path/filename}.py
{python code}
```
* the extract and filename statements are only allowed once per code block

* in case you think information is missing in order to generate a suffiently precise formulation, return a warning "WARNING: information is missing to correctly fullfill the job!" and then explain what kind of information you think is missing and how I could easily retrieve it.  