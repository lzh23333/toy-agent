# Toy Agent

This repository is a teaching project for building a minimal ReAct-style file
agent from scratch.

The goal is to understand the core loop used by modern agents:

```text
observe -> reason -> act -> observe result -> repeat -> final answer
```

The first version will use OpenRouter through the OpenAI-compatible API and a
small set of safe local file tools.

## Current Status

The project is being built step by step. The design is documented in
`DESIGN.md`.

No agent runtime has been implemented yet.

## Planned Modules

- `tools.py`: safe file tools and tool registry.
- `agent.py`: ReAct loop, state, OpenRouter client, and CLI.
- `case_files/`: multi-step test fixture for observing the loop.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local config from the example:

```bash
cp config.example.json config.json
```

For this teaching project, local `config.json` may contain your OpenRouter API
key because it is ignored by Git:

```json
{
  "api_key": "sk-or-...",
  "model": "your/openrouter-model"
}
```

You can also set `OPENROUTER_API_KEY` in the environment. The environment
variable overrides `api_key` from `config.json`.

Then edit `config.json` and choose an OpenRouter model.

## Pure Chat Test

Before building the agent loop, run the plain chat test:

```bash
python3 llm_chat.py
```

This program sends the full message history on every request:

```text
system -> user -> assistant -> user -> assistant -> ...
```

Important LLM parameters in `config.json`:

- `model`: the OpenRouter model id.
- `temperature`: randomness. Lower values are more stable.
- `max_tokens`: maximum generated output tokens.
- `top_p`: nucleus sampling. Usually keep this at `1.0` while learning.
- `presence_penalty`: encourages the model to discuss new topics.
- `frequency_penalty`: discourages repeated wording.
- `max_steps`: reserved for the later ReAct loop, not used by `llm_chat.py`.

## Conversation Log

`cli.py` saves user and assistant messages to a per-session JSONL log:

```text
memory/sessions/<session-id>.jsonl
```

The `memory/` directory is ignored by Git because it may contain private
conversation data.

By default, each CLI run creates a new session. Saved messages are logged but
not loaded into unrelated sessions.

To continue a specific session, pass its session id. The full session history
is loaded:

```bash
python3 cli.py --session 20260504T102030Z
```

## Learning Approach

Implementation is intentionally incremental. Each module should be discussed
before it is written so the architecture stays visible.
