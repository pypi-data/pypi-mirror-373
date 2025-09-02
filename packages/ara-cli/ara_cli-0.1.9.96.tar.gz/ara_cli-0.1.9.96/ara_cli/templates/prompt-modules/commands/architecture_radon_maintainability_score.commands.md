### COMMANDS FOR EXPERT ARCHITECTURE MAINTAINABILITY RADON SCORE compute
"""
Note: the metrics you are using are from the website: https://radon.readthedocs.io/en/latest/intro.html), the instruction list should reflect the command line call: radon mi -s <path/to_python_file.py>
"""

Your job is now:
* Remember you are strictly following your given RULES and SKILLS as ANALYST
* Now apply the following metric to every single python source file given in order to compute the 'Halstead Volume' on file level defined as follows
```
   Halstead’s goal was to identify measurable properties of software, and the relations between them. These numbers are statically computed from the source code:

   ```latex
      \eta_1 = \text{the number of distinct operators}
      \eta_2 = \text{the number of distinct operands}
      N_1 = \text{the total number of operators}
      N_2 = \text{the total number of operands}
   ```
   to compute the Halstead Volume 'V' use:
   ```latex
      V = (N_1 + N_2) \log_2 (\eta_1 \eta_2)
   ```
```

* Now apply the following metric to every single python source file given in order to compute the 'Cyclomatic Complexity (G)' defined as follows:
```
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

* Now apply the following metric to every single python source file given in order to compute the 'Source Lines of Code (SLOC)' defined as follows
```
   SLOC: The number of source lines of code   
```

* Now apply the following metric to every single python source file given in order to compute the 'Percent of Comment Lines (C)' defined as follows
```
   C = Num_commented_Lines % SLOC: the ratio between number of comment lines and SLOC, expressed as a percentage
```

* By using the previously computed 'Halstead Volume', 'Cyclomatic Complexity', 'SLOC' and 'C' now compute the 'Maintainability Index' which is defined as follows:
```
   Maintainability Index is a software metric which measures how maintainable (easy to support and change) the source code is. The maintainability index is calculated as a factored formula consisting of SLOC (Source Lines Of Code), Cyclomatic Complexity and Halstead volume. It is used in several automated software metric tools, including the Microsoft Visual Studio 2010 development environment, which uses a shifted scale (0 to 100) derivative.

   Use this formula to calculate the radon 'Maintainability Index':
   ```latex
      MI = \max \left[ 0, 100\frac{171 - 5.2 \ln V - 0.23G - 16.2 \ln L + 50 \sin \left( 2.4 \sqrt{C} \right)}{171} \right]
   ```

   Where:

   V is the Halstead Volume (see below);
   G is the total Cyclomatic Complexity;
   L is the number of Source Lines of Code (SLOC);
   C is the percent of comment lines with respect to SLOC  (important: here converted to radians).
```

* Finally, you must return a summary list which lists the previously computed 'Maintainability indecies' in the following example format:
```text
# [ ] extract
# filename: {path_to_artefact}/maintainability_index_estimate.txt
{<filename1.py> - (<value of 'Maintainablilty Index of this file>) - Halstead: <V> - Cyclomatic Complexity <G> - SLOC <L> - Percent of comment lines in radians <C>}
{<filename2.py> - (<value of 'Maintainablilty Index of this file>) - Halstead: <V> - Cyclomatic Complexity <G> - SLOC <L> - Percent of comment lines in radians <C>}
{...}
```

* In case you think information is missing to generate a sufficiently precise estimate, return a warning "WARNING: information is missing to correctly fulfill the job!" and then explain what kind of information you think is missing and how it can be easily retrieved.

