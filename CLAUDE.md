# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A hands-on learning project for understanding how LLM-based agents work under the hood. The goal is to build a minimal ReAct agent from scratch — no frameworks, no abstractions — so each concept (message format, tool calls, the observe-reason-act loop) is visible and inspectable.

The project is built incrementally. At each stage only the modules needed for that lesson exist. Currently at: **basic chat agent** (OpenRouter client, session memory, CLI). Next: tools + ReAct loop.

## Commands

```bash
pip install -r requirements.txt   # Install dependencies (openai, httpx[socks])
python3 cli.py                    # Run the interactive CLI
python3 cli.py --session <id>     # Resume a specific session
python3 cli.py --no-memory        # Disable conversation persistence
python3 llm_chat.py               # Smoke test (single chat request)
```

## Architecture (Current)

Each module is a single file with a clear responsibility. They form a dependency chain:

```
messages.py  →  llm.py  →  agent.py  →  cli.py
                 ↓
            memory.py (independent, used by cli.py)
```

- **`messages.py`** — Foundation layer. `Message` dataclass with `role`/`content`, `ChatRole` type, `ChatMessageDict` TypedDict. No imports from other modules in the project. Every other module depends on this.

- **`llm.py`** — LLM transport layer. `LLMClient` wraps the OpenAI SDK pointed at OpenRouter, `LLMConfig` holds model params, `load_config()` reads them from `config.json`. API errors are translated to `LLMError`. SOCKS proxy env vars are normalized automatically.

- **`memory.py`** — Conversation persistence. `ConversationMemory` appends/loads per-session JSONL files under `memory/sessions/`. `MemoryRecord` adds a UTC timestamp to each message. `ConversationStore` validates session IDs to prevent path traversal.

- **`agent.py`** — The agent itself. `ChatAgent` holds state (`AgentState`: messages, turn count, final answer) and runs one LLM call per `run()`. Currently a straightforward chat loop — the ReAct loop will replace this later.

- **`cli.py`** — Interactive REPL. `argparse` entry point, session management via `ConversationStore`, `Console` helper for formatted output.

- **`llm_chat.py`** — Standalone smoke test. Useful for validating API connectivity and config before building agent features.

## Learning Path

The implementation follows the sequence in `DESIGN.md`. Each module is meant to be discussed before coding:

1. Safe path handling → 2. File tools → 3. ToolRegistry + schemas → 4. Case files fixture → 5. Config loading → 6. OpenRouter client → 7. AgentState → 8. One-step LLM decision → 9. Full ReAct loop → 10. CLI trace → 11. End-to-end run

The current code covers steps 5–6 (config + OpenRouter client), step 7 partially (AgentState), and step 10 partially (CLI).

## Guidelines

- Follow `DESIGN.md`'s module order — one concept at a time, discuss before coding.
- Tool errors become observations, not exceptions — the LLM decides how to handle them.
- File tools must stay inside the project directory (safe path resolution comes first).
- v1 scope: no bash execution, no long-term memory, no streaming, no plugins.
- API keys come from `OPENROUTER_API_KEY` env var or `config.json`. `config.json` is gitignored.
- Keep the ReAct loop explicit — no hiding it behind abstractions.
- Small, readable files over abstractions.
- Do not replace discussion with a full implementation dump.

## Git Commits

- Keep commits focused on the discussed module or setup step.
- `Co-authored-by: Codex <codex@openai.com>` when Codex contributes changes.
