### COMMANDS FOR UPDATING THE FORMULATION OF FEATURE FILES
Your job is now:
* Examine the designated feature file, ensuring it aligns with the content and its relationships within the context files.
* If there is a discrepancy between the feature's specifications and the system behavior described in the context files, defer to the behavior outlined in the context files. This also applies to behaviors not yet described in the existing feature file.
* return a table of your five top rated proposed enhancements sorted by the "Formulation enhancement rating" and formatted in the following way (one example line is given as reference):
| Number | filename | Scenario name | Line of feature file (from - to) | Formulation enhancement rating (0 - 1) | explanation of enhancement | 
| 1      | file.feature  | some_scenario | 30-65                    | 0.9                             | {here comes an explanation and reasoning of the updated formulation and a reference to the context source} |

* Propose a revised formulation for the feature file based on the analysis.
* wrap and return the revised formulation in the following format 
```artefact
# [ ] extract 
# filename: {path/artefac_filename.feature} 
{formulation}
```
* the extract and filename statements are only allowed once per code block

* in case you think information is missing in order to generate a suffiently precise formulation, return a warning "WARNING: information is missing to update the formulation of the designated feature file" and then explain what kind of information you think is missing and how I could easily retrieve it  
