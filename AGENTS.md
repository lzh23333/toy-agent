# Project Agent Guidelines

This repository is a teaching project. Do not implement large chunks without
first discussing the module boundary and intended behavior.

## Development Style

- Prefer small, readable Python modules.
- Keep the ReAct loop explicit rather than hiding it behind abstractions.
- Add only the dependencies needed for the current lesson.
- Keep file tools restricted to this project directory.
- Treat tool errors as observations when possible.

## Implementation Order

Follow the sequence in `DESIGN.md`:

1. Safe path handling and file tools.
2. Tool schemas and `ToolRegistry`.
3. Case-file fixture.
4. Config loading and OpenRouter client setup.
5. `AgentState`.
6. One-step LLM decision.
7. Full ReAct loop.
8. CLI trace printing.

## Constraints

- Do not add bash execution in version 1.
- Do not add long-term memory in version 1.
- Do not store API keys in tracked files.
- Do not replace discussion with a full implementation dump.

## Git Commits

- Keep commits focused on the discussed module or setup step.
- Include the correct co-author trailer when Codex contributes changes:
  `Co-authored-by: Codex <codex@openai.com>`.
- Use the exact trailer spelling `Co-authored-by:` so Git hosting tools can
  recognize it.
