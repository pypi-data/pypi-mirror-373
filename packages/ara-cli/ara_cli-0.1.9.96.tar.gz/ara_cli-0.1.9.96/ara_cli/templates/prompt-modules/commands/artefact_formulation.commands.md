### COMMANDS FOR FORMULATING AGILE REQUIREMENTS ARTIFACTS
Your job is now:
* analyze the given files with respect to content and relationship
* analyze the new artefact with respect to content and the relationship to the given files
* generate a formulation proposal for the specified documents
* wrap and return the formulated  in the following format 
```artefact
# [ ] extract 
# filename: {path/filename.filextension} 
{formulation}
```
* the extract and filename statements are only allowed once per code block

* in case you think information is missing in order to generate a suffiently precise formulation, return a warning "WARNING: information is missing to formulate the new artefacts" and then explain what kind of information you think is missing and how I could easily retrieve it  
