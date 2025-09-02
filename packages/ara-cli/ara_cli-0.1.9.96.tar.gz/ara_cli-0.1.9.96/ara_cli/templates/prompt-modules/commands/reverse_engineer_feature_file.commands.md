### COMMANDS FOR REVERSE ENGINEER A FEATURE FILE FROM EXISTING CODE
Your job is now:
* remember you are strictly following your given RULES AS GHERKIN EXPERT
* Silently analyze the intended behavior of the given code and if given any other description of the program flow like pseudo code
* do not add any additional behavior in the feature file, describe strictly the behavior that is defined by code or pseudo code
* if any existing feature files are provided maximize reusage of formulated steps so that later step implementation effort can be reduces

* return your results in the following format 
```gherkin
# [ ] extract
# filename: {path/filename}.feature
{feature file}
```

* in case you think information is missing in order to generate a suffiently precise formulation, return a warning "WARNING: information is missing to correctly fullfill the job!" and then explain what kind of information you think is missing and how I could easily retrieve it.  