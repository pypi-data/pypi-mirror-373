### INTENTION and CONTEXT
Search for a line starting with `Task: ` defined in the `### GIVENS` section. Just repeat the task name you have found as confirmation
* Do not proceed if no task is defined. Return immediatly with the message: "No task defined as prompt control" 
* Focus on the description in the `Description` section of the defined task. Ignore all other sections. 
* Search in the task description section for a line starting with `[@in-progress]`. Do not proceed if no '[@in-progress]' step is defined. Return immediatly with the message: "No task todo defined as [@in-progress] as prompt intention."
* Otherwise confirm the '[@in-progress]' step you have found. Then focus on the intention of this step only. Ignore all other steps.  