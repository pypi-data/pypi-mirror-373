### COMMANDS FOR REVERSE ENGINEER PROGRAM FLOW FROM EXISTING CODE
Your job is now:
* remember you are strictly following your given RULES AS CODE ANAYLST
* Silently analyze the intended behavior of the given code
* create as result of your silent analysis this analysis table
  | filename       | method                                   | short description of logical contribution to the logical program flow      |
  | {filename}.py  | {method name, descriptive name of code block}  | {detailed explanation of the value to the program flow}      |

* then generate based on your analysis and by using your generated analysis table the pseudo code that summarizes the logical flow for the whole process to generate the listing from start to end. Here is an example how the pseude code could look like:
  ```pseudo code
Initialize the system to prepare for use
Verify if the user is authenticated
IF the user is authenticated:
    Retrieve and process user information
ELSE:
    Display an error message if authentication fails
  ```

* in case you think information is missing in order to generate a suffiently precise formulation, return a warning "WARNING: information is missing to correctly fullfill the job!" and then explain what kind of information you think is missing and how I could easily retrieve it.  