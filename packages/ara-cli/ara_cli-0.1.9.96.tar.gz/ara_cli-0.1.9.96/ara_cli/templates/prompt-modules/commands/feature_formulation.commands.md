### COMMANDS FOR FORMULATING AGILE REQUIREMENTS ARTIFACTS
Your job is now:
* remember your RULES
* analyze the given files with respect to content and relationship
* analyze the new artefact with respect to content and the relationship to the given files
* generate a formulation proposal for the specified documents

* Use this example of a simple feature file, the corresponding step definitions and the production code as best practice to get your job done
    """
    Feature file:
    **features/arithmetic.feature**
    ```gherkin
    Feature: Arithmetic Operations

    Contributes to: <Any artefact name to which this feature contributes value> <Classifier of this artefact>

      Scenario: Addition of two numbers
        Given the CLI is initialized
        When the user runs the addition command with "2" and "3"
        Then the result should be "5"

      Scenario Outline: Subtraction of two numbers
        Given the CLI is initialized
        When the user runs the subtraction command with "<num1>" and "<num2>"
        Then the result should be "<result>"

        Examples:
          | num1 | num2 | result |
          | 5    | 3    | 2      |
          | 10   | 4    | 6      |
          | 0    | 0    | 0      |
    ```

* wrap and return the formulated feature in the following format 
```artefact
# [ ] extract 
# filename: {path/filename.filextension} 
{formulation}
```
* the extract and filename statements are only allowed once per code block

* in case you think information is missing in order to generate a suffiently precise formulation, return a warning "WARNING: information is missing to formulate the new artefacts" and then explain what kind of information you think is missing and how I could easily retrieve it  

