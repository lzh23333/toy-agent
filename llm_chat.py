from agent import ChatAgent
from llm import LLMClient, LLMError, format_config, load_config


def main() -> int:
    try:
        config = load_config()
        agent = ChatAgent(llm=LLMClient(config), memory=None)
    except (SystemExit, LLMError) as exc:
        print(f"LLM error: {exc}")
        return 1

    print(format_config(config))
    print("\nSmoke test prompt: 用一句话解释 ReAct agent")

    try:
        result = agent.run("用一句话解释 ReAct agent")
    except LLMError as exc:
        print(f"LLM error: {exc}")
        return 1

    print(f"\nAssistant > {result.answer}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

