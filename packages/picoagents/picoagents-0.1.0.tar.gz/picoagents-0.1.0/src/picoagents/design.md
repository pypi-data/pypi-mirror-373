## Model Client Clas

base llm/AI model class ...
should have mthodss for

- get_response [sequence [system message, user message, multimodal etc]]
- close

## Agent Class

- Run
  - construct model call
    - take instruction + task + tools (convert tools to right format)
  - make model client call
  - check if tool exists
  - make tool calls in parrallel or in sequence
  - return result of everything
-
