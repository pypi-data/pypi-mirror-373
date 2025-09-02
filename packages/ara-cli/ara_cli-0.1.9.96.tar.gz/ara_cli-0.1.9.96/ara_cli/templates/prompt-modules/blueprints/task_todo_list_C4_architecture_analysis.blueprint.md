### INTENTION and CONTEXT
My intention is to setup a todo list in my given task that helps me to implement a feature in a BDD way

Now do the following:
Search for a line starting with `Task: ` defined in the `### GIVENS` section. Just repeat the task_name you have found as confirmation
* Do not proceed if no task is defined. Return immediatly with the message: "No task defined as prompt control" 

* Focus on the description in the `Description` section of the defined task. Ignore all other sections.
* Analyze the content of the task description section and adapt your default recipe accordingly. You can add new "[@to-do]s ...", you can delete "[@to-do]s" that are not necessary anymore according to the existing task description content

* the format and formulation of your default recipe implementing a feature in BDD style is
```
[@to-do] my intention is to generate a very detailed "C4 System Context diagram" using the given code base of the application. In order to reach the intended level of detail you need to extract detailed information from each given source file. The path to the new diagram should be the ara/tasks/chainlit_C4_architecture_exploration.data/{diagram_name}+".md" filepath

[@to-do] my intention is to generate a very detailed "C4 Container diagram" using the given code base of the application. In order to reach the intended level of detail you need to extract detailed information from each given source file. The path to the new diagram should be the ara/tasks/chainlit_C4_architecture_exploration.data/{diagram_name}+".md" filepath

[@to-do] my intention is to generate a very detailed "C4 Component diagram" using the given code base of the application. For the component diagram now zoom in on the container '{container name}' described in the '{name of the container diagram}'. In order to reach the intended level of detail you need to extract detailed information from each given source file. The path to the new diagram should be the ara/tasks/chainlit_C4_architecture_exploration.data/{diagram_name}+".md" filepath

[@to-do] my intention is to generate a very detailed "C4 Code diagram" using the given code base of the application. For the code diagram now zoom in on the component '{component name}' described in the '{name of the component diagram}'. In order to reach the intended level of detail you need to extract detailed information from each given source file. The path to the new diagram should be the ara/tasks/chainlit_C4_architecture_exploration.data/{diagram_name}+".md" filepath
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
