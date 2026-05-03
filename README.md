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

Set your OpenRouter API key:

```bash
export OPENROUTER_API_KEY="..."
```

Then edit `config.json` and choose a model that supports tool calling.

## Learning Approach

Implementation is intentionally incremental. Each module should be discussed
before it is written so the architecture stays visible.

