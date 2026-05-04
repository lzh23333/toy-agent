import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    OpenAIError,
    RateLimitError,
)

from memory import ConversationMemory
from messages import Message, to_message_dicts


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class LLMError(Exception):
    pass


def normalize_proxy_environment() -> None:
    for name in ("ALL_PROXY", "all_proxy"):
        value = os.environ.get(name)
        if value and value.startswith("socks://"):
            os.environ[name] = "socks5://" + value[len("socks://") :]


@dataclass(frozen=True)
class LLMConfig:
    api_key: str | None
    model: str
    temperature: float = 0.2
    max_tokens: int | None = None
    top_p: float | None = None
    presence_penalty: float | None = None
    frequency_penalty: float | None = None


def load_config(path: str = "config.json") -> LLMConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise SystemExit(
            "Missing config.json. Copy config.example.json to config.json "
            "and set the model."
        )

    data = json.loads(config_path.read_text(encoding="utf-8"))
    model = data.get("model")
    if not model or model == "your/openrouter-model":
        raise SystemExit("config.json must set a real OpenRouter model name.")

    return LLMConfig(
        api_key=data.get("api_key"),
        model=model,
        temperature=float(data.get("temperature", 0.2)),
        max_tokens=data.get("max_tokens"),
        top_p=data.get("top_p"),
        presence_penalty=data.get("presence_penalty"),
        frequency_penalty=data.get("frequency_penalty"),
    )


class LLMClient:
    def __init__(self, config: LLMConfig) -> None:
        api_key = os.environ.get("OPENROUTER_API_KEY") or config.api_key
        if not api_key or api_key == "sk-or-your-api-key":
            raise SystemExit(
                "Missing OpenRouter API key. Set api_key in config.json or "
                "OPENROUTER_API_KEY in the environment."
            )

        self.config = config
        normalize_proxy_environment()
        try:
            self.client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)
        except ValueError as exc:
            raise LLMError(
                "Failed to create the LLM client. If this mentions a proxy URL "
                "with 'socks://', install socks support or use an http/https proxy."
            ) from exc
        except OpenAIError as exc:
            raise LLMError(f"Failed to create the LLM client: {exc}") from exc

    def chat(self, messages: list[Message]) -> str:
        params: dict[str, Any] = {
            "model": self.config.model,
            "messages": to_message_dicts(messages),
            "temperature": self.config.temperature,
        }

        optional_params = {
            "max_tokens": self.config.max_tokens,
            "top_p": self.config.top_p,
            "presence_penalty": self.config.presence_penalty,
            "frequency_penalty": self.config.frequency_penalty,
        }
        params.update(
            {name: value for name, value in optional_params.items() if value is not None}
        )

        try:
            response = self.client.chat.completions.create(**params)
        except AuthenticationError as exc:
            raise LLMError(
                "Authentication failed. Check your OpenRouter API key."
            ) from exc
        except RateLimitError as exc:
            raise LLMError(
                "The LLM provider rate-limited this request or your quota is exhausted."
            ) from exc
        except APITimeoutError as exc:
            raise LLMError("The LLM request timed out. Try again later.") from exc
        except APIConnectionError as exc:
            raise LLMError(
                f"Could not connect to the LLM provider. Check your network. {exc}"
            ) from exc
        except APIStatusError as exc:
            raise LLMError(
                f"LLM provider returned HTTP {exc.status_code}: {exc.message}"
            ) from exc
        except OpenAIError as exc:
            raise LLMError(f"OpenAI-compatible client error: {exc}") from exc

        content = response.choices[0].message.content
        if content is None:
            return ""
        return content


def print_config(config: LLMConfig) -> None:
    print("LLM parameters:")
    print(f"- model: {config.model}")
    print(f"- temperature: {config.temperature}")
    print(f"- max_tokens: {config.max_tokens}")
    print(f"- top_p: {config.top_p}")
    print(f"- presence_penalty: {config.presence_penalty}")
    print(f"- frequency_penalty: {config.frequency_penalty}")
    print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a pure chat LLM test.")
    parser.add_argument(
        "--resume",
        type=int,
        default=0,
        metavar="N",
        help="load the most recent N saved user/assistant messages",
    )
    parser.add_argument(
        "--memory-path",
        default="memory/chat.jsonl",
        help="path to the JSONL conversation log",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()
    try:
        client = LLMClient(config)
    except LLMError as exc:
        print(f"LLM error: {exc}")
        return

    memory = ConversationMemory(args.memory_path)
    messages = [
        Message.system(
            "You are a concise assistant. Answer in Chinese unless asked otherwise."
        )
    ]
    resumed_messages = memory.load_recent(args.resume)
    messages.extend(resumed_messages)

    print_config(config)
    if resumed_messages:
        print(f"Resumed {len(resumed_messages)} messages from {args.memory_path}.")
    print("Type your message. Use Ctrl-D or an empty line to exit.")

    while True:
        try:
            user_input = input("\nUser > ").strip()
        except EOFError:
            print()
            break

        if not user_input:
            break

        user_message = Message.user(user_input)
        messages.append(user_message)
        memory.append(user_message)

        try:
            assistant_reply = client.chat(messages)
        except LLMError as exc:
            print(f"\nLLM error: {exc}")
            break

        assistant_message = Message.assistant(assistant_reply)
        messages.append(assistant_message)
        memory.append(assistant_message)
        print(f"\nAssistant > {assistant_reply}")


if __name__ == "__main__":
    main()
