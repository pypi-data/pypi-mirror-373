### INTENTION and CONTEXT
My intention is to setup a todo list in my given task that helps me to implement a feature in a BDD way

Now do the following:
Search for a line starting with `Task: ` defined in the `### GIVENS` section. Just repeat the task_name you have found as confirmation
* Do not proceed if no task is defined. Return immediatly with the message: "No task defined as prompt control" 

* Focus on the description in the `Description` section of the defined task. Ignore all other sections.
* Analyze the content of the task description section and adapt your default recipe accordingly. You can add new "[@to-do]s ...", you can delete "[@to-do]s" that are not necessary anymore according to the existing task description content

* the format and formulation of your default recipe implementing a feature in BDD style is
```
[@to-do] analyze and understand the given `user story`
[@to-do] generate an example contributing to the rule `rule of userstory to implement` which should be turned into a scenario or feature description
[@to-do] use the example and aditional relevant context `{context list}` to formulate the feature file
[@to-do] use the formulated feature file, relevant existing step implementations and relevant existing production code to implement the new step implementations that will fail
[@to-do] use the created step definitions, the relevant existing production code to modify existing code and to create new code implementing the requested behavior so that the step implementations will pass 
```

* append your recipe at the end of task
* return the extended task in the following format 
```artefact
# [ ] extract 
# filename: ara/tasks/{task_name}.task 
{initial task content}
{recipe}
```
* the extract and filename statements are only allowed once per code block

* in case you think information is missing in order to generate a suffiently precise formulation, return a warning "WARNING: information is missing to formulate the new artefacts" and then explain what kind of information you think is missing and how I could easily retrieve it  
