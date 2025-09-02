# Usage: 
# necessary input and adaption: 
# replace text snippets in <> with specific context
# ...
# expected output: 
# ...
Do not use usage information as prompt instructions


Given source code
```python
<source code for context, skip irrelevant for current task>
```

Given existing unit tests
```python
<existing unit tests>
```

Given pytest is available

Modify and/or create unit tests so this is fully covered:
```python
<snippet you want to cover in the next step>
```

Give me only what is relevant to testing this snippet. Use parametrization where applicable. Split into multiple tests instead of using if-else blocks. Mock all dependencies of tested code.
