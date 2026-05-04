import argparse
import sys

from agent import ChatAgent
from llm import LLMClient, LLMError, format_config, load_config
from memory import ConversationStore


class Console:
    def info(self, message: str) -> None:
        print(message)

    def error(self, message: str) -> None:
        print(f"Error: {message}", file=sys.stderr)

    def assistant(self, message: str) -> None:
        print(f"\nAssistant > {message}")

    def thinking(self) -> None:
        print("\nThinking...", flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the toy agent CLI.")
    parser.add_argument("--config", default="config.json", help="path to config JSON")
    parser.add_argument(
        "--memory-dir",
        default="memory/sessions",
        help="directory for JSONL conversation sessions",
    )
    parser.add_argument(
        "--session",
        default=None,
        help="session id to resume fully; omit to create a new session",
    )
    parser.add_argument(
        "--no-memory",
        action="store_true",
        help="do not save or load conversation memory",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    console = Console()

    try:
        config = load_config(args.config)
        llm = LLMClient(config)
    except (SystemExit, LLMError) as exc:
        console.error(str(exc))
        return 1

    session_id = None
    memory = None
    if not args.no_memory:
        try:
            store = ConversationStore(args.memory_dir)
            session_id, memory = store.open(args.session)
        except ValueError as exc:
            console.error(str(exc))
            return 1

    agent = ChatAgent(llm=llm, memory=memory)

    console.info(format_config(config))
    if args.no_memory:
        console.info("Memory: disabled")
    else:
        console.info(f"Session: {session_id}")
        console.info(f"Memory: logging to {memory.path}")
        if args.session:
            resumed = memory.load_all()
            agent.resume(resumed)
            console.info(f"Resumed {len(resumed)} messages.")

    console.info("\nType your message. Use Ctrl-D or an empty line to exit.")

    while True:
        try:
            user_input = input("\nUser > ").strip()
        except EOFError:
            print()
            return 0

        if not user_input:
            return 0

        console.thinking()
        try:
            result = agent.run(user_input)
        except LLMError as exc:
            console.error(str(exc))
            return 1

        console.assistant(result.answer)


if __name__ == "__main__":
    raise SystemExit(main())
