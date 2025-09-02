### COMMANDS FOR EXPERT ARCHITECTURE CYCLOMATIC RADON SCORE compute
"""
Note: the metrics you are using are from the website: https://radon.readthedocs.io/en/latest/intro.html), the instruction list should reflect the command line call: radon hal <path/to_python_file.py>
"""

Your job is now:
* Remember you are strictly following your given RULES and SKILLS as ANALYST
* Now apply the following metric to every single python source file given in order to compute the 'Halstead Volume' on file level defined as follows
```
   ```latex
      \eta_1 = \text{the number of distinct operators used in given source file}
      \eta_2 = \text{the number of distinct operands used in given source file}
      N_1 = \text{the total number of operators used in given source file}
      N_2 = \text{the total number of operands used in given source file}
   ```
   to compute the Halstead Volume 'V' use:
   ```latex
      V = (N_1 + N_2) \log_2 (\eta_1 \eta_2)
   ```
```

* Finally, you must return a summary list which is the list of the previously computed 'Halstead Volumes' in the following format:
```text
# [ ] extract
# filename: {path_to_artefact}/Halstead_Volume_estimate.txt
{<filename1.py> - (<value of 'average Halstead Volume' of this file>) - '\eta_1' - '\eta_2' - 'N_1' - 'N_2'}
{<filename2.py> - (<value of 'average Halstead Volume' of this file>) - '\eta_1' - '\eta_2' - 'N_1' - 'N_2'}
{...}
```

* In case you think information is missing to generate a sufficiently precise estimate, return a warning "WARNING: information is missing to correctly fulfill the job!" and then explain what kind of information you think is missing and how it can be easily retrieved.

