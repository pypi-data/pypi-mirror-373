### COMMANDS FOR EXPERT ARCHITECTURE CYCLOMATIC RADON SCORE ESTIMATE
"""
Note: the metrics you are using are from the website: https://radon.readthedocs.io/en/latest/intro.html), the instruction list should reflect the command line call: radon cc -s --total-average <path/to_python_file.py>
"""

Your job is now:
* Remember you are strictly following your given RULES and SKILLS as ANALYST
* Now apply the following metric to every single python source file given in order to compute the 'Cyclomatic Complexity (G)' defined as follows:
```
Cyclomatic Complexity corresponds to the number of decisions a block of code contains plus 1. This number (also called McCabe number) is equal to the number of linearly independent paths through the code. This number can be used as a guide when testing conditional logic in blocks. Analyze the AST tree of a Python program to compute Cyclomatic Complexity. Statements in the following table have the following effects on Cyclomatic Complexity
   | Construct          |	Effect on CC | Reasoning
   | if	               |  +1       	 | An if statement is a single decision.
   | elif	            |  +1	          | The elif statement adds another decision.
   | else	            |  +0           | The else statement does not cause a new decision. The decision is at the if.
   | for	               |  +1           |	There is a decision at the start of the loop.
   | while	            |  +1           |	There is a decision at the while statement.
   | except	            |  +1           |	Each except branch adds a new conditional path of execution.
   | finally	         |  +0           | The finally block is unconditionally executed.
   | with               |  +1           |	The with statement roughly corresponds to a try/except block (see PEP 343 for details).
   | assert	            |  +1           |	The assert statement internally roughly equals a conditional statement.
   | Comprehension      |	+1           |	A list/set/dict comprehension of generator expression is equivalent to a for loop.
   | Boolean Operator   |	+1	          | Every boolean operator (and, or) adds a decision point.

   Return the 'average Cyclomatic Complexity' (CC) of `<filename>.py` as: `sum of all CCs`/`number of methods`. Do only include methods with CC>0 in when adding up the 'number of methods'.
```

* Finally, you must return a summary list which lists the previously computed 'cyclomatic complexity score's in the following format:
```text
# [ ] extract
# filename: {path_to_artefact}/CC_index_estimate.txt
{<filename1.py> - (<value of 'average Cyclomatic Complexity' of this file>) - number of methods with CC > 0 - sum of all CCs}
{<filename2.py> - (<value of 'average Cyclomatic Complexity' of this file>) - number of methods with CC > 0 - sum of all CCs}
{...}
```

* In case you think information is missing to generate a sufficiently precise estimate, return a warning "WARNING: information is missing to correctly fulfill the job!" and then explain what kind of information you think is missing and how it can be easily retrieved.

