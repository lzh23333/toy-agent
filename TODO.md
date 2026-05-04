# Development TODO

This project should be implemented one module at a time. Each module should be
discussed before coding so the agent architecture stays clear.

## Workflow

For every module:

1. Discuss the concept and boundary.
2. Agree on the minimal interface.
3. Implement only that module.
4. Run a small manual check.
5. Commit the focused change.

## Module 1: Safe Path Handling

Goal:

- Make sure every file tool stays inside the project directory.

Why it matters:

- LLM tool arguments are untrusted input.
- A file agent must not read or edit arbitrary system files.

Expected output:

- A `ToolError` exception.
- A helper that resolves project-relative paths safely.

Acceptance checks:

- Allows paths like `README.md` and `case_files/report.md`.
- Rejects absolute paths like `/etc/passwd`.
- Rejects traversal paths like `../secret.txt`.

## Module 2: Basic File Tools

Goal:

- Implement local Python tools before connecting them to the LLM.

Tools:

- `list_files(path: str)`
- `read_file(path: str)`
- `edit_file(path: str, old_text: str, new_text: str)`

Why it matters:

- Tools are the agent's controlled actions.
- The ReAct loop is only useful if actions are safe and predictable.

Acceptance checks:

- Can list files under a project-relative directory.
- Can read a project-relative text file.
- Can edit a file only when `old_text` appears exactly once.
- Tool failures return clear error messages.

## Module 3: Tool Registry and Schemas

Goal:

- Expose Python tools in a format the LLM can understand.

Expected output:

- A `ToolRegistry` class.
- OpenAI-compatible tool schemas.
- A `dispatch` method that executes requested tool calls.

Why it matters:

- Tool schemas are the model's tool manual.
- Dispatch is the bridge from model intent to Python execution.

Acceptance checks:

- `schemas()` returns all tool definitions.
- Known tool calls execute the correct Python function.
- Unknown tools and invalid arguments return tool error observations.

## Module 4: Case Files Fixture

Goal:

- Create a small multi-file task that forces the agent to loop.

Expected output:

- A `case_files/` directory with several evidence files.
- A `report.md` containing an intentionally wrong conclusion.

Why it matters:

- A good fixture tests exploration, reading, reasoning, editing, and
  verification.

Acceptance checks:

- The task cannot be completed by reading only one file.
- The final report can be fixed with `edit_file`.
- The expected reasoning chain is understandable to a beginner.

## Module 5: Config Loading

Goal:

- Load runtime settings from `config.json`.

Expected settings:

- `model`
- `temperature`
- `max_steps`

Why it matters:

- The agent should not hard-code model names.
- The loop limit should be configurable.

Acceptance checks:

- Missing `config.json` gives a clear error.
- Missing `model` gives a clear error.
- `max_steps` defaults or validates cleanly.

## Module 6: OpenRouter Client

Goal:

- Connect to OpenRouter through the OpenAI-compatible SDK.

Expected output:

- A small client setup using `OPENROUTER_API_KEY`.
- `base_url` set to `https://openrouter.ai/api/v1`.

Why it matters:

- The LLM is the decision maker in the loop.
- OpenRouter is only the transport; the architecture should stay provider-light.

Acceptance checks:

- Missing API key gives a clear error.
- A simple non-tool chat request works.

## Module 7: Agent State

Goal:

- Represent one running task.

Expected output:

- An `AgentState` dataclass.

State fields:

- `task`
- `messages`
- `steps`
- `final_answer`
- `step_count`
- `max_steps`
- `done`

Why it matters:

- Short-term memory is the current task state.
- The loop needs explicit state to be observable and debuggable.

Acceptance checks:

- A new task initializes with system and user messages.
- Step records can be appended.

## Module 8: One-Step LLM Decision

Goal:

- Run exactly one ReAct decision step.

Expected behavior:

- Send current messages and tool schemas to the model.
- Receive either a final answer or tool calls.
- Do not loop yet.

Why it matters:

- One step is the smallest useful unit of agent behavior.
- It lets us inspect model decisions before adding automation.

Acceptance checks:

- A normal question can produce a final answer.
- A file task can produce a tool call.

## Module 9: Full ReAct Loop

Goal:

- Turn one-step decisions into an autonomous loop.

Expected behavior:

- Continue until final answer or `max_steps`.
- Execute tool calls.
- Append tool observations to messages.
- Record structured steps.

Why it matters:

- The loop is what makes the system an agent rather than a one-shot tool caller.

Acceptance checks:

- Multi-step fixture task triggers several tool calls.
- Tool observations influence later model decisions.
- The agent stops cleanly at `max_steps`.

## Module 10: CLI Trace Output

Goal:

- Make the loop visible during learning.

Expected output:

- Print each step number.
- Print tool name and arguments.
- Print a short observation summary.
- Print the final answer.

Why it matters:

- Agent development requires observability.
- The trace is how we debug reasoning and tool behavior.

Acceptance checks:

- Running the agent shows a readable sequence of actions.
- Long observations are shortened in the console.

## Module 11: End-to-End Fixture Run

Goal:

- Run the case-files task from the CLI.

Expected behavior:

- The agent lists files.
- The agent reads multiple evidence files.
- The agent edits `report.md`.
- The agent reads `report.md` again to verify.
- The agent explains the final reasoning.

Why it matters:

- This proves that the core ReAct architecture works.

Acceptance checks:

- The final report is corrected.
- The trace shows multiple loop iterations.
- The working tree diff matches the expected report edit.

