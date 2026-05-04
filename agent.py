from dataclasses import dataclass, field

from llm import LLMClient
from memory import ConversationMemory
from messages import Message


DEFAULT_SYSTEM_PROMPT = (
    "You are a concise assistant. Answer in Chinese unless asked otherwise."
)


@dataclass
class AgentState:
    messages: list[Message]
    turns: int = 0
    final_answer: str | None = None


@dataclass(frozen=True)
class AgentResult:
    answer: str
    state: AgentState


@dataclass
class ChatAgent:
    llm: LLMClient
    memory: ConversationMemory | None = None
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    state: AgentState = field(init=False)

    def __post_init__(self) -> None:
        self.state = AgentState(messages=[Message.system(self.system_prompt)])

    def resume(self, messages: list[Message]) -> None:
        self.state.messages.extend(messages)

    def run(self, user_input: str) -> AgentResult:
        user_message = Message.user(user_input)
        self.state.messages.append(user_message)
        if self.memory is not None:
            self.memory.append(user_message)

        answer = self.llm.chat(self.state.messages)
        assistant_message = Message.assistant(answer)
        self.state.messages.append(assistant_message)
        if self.memory is not None:
            self.memory.append(assistant_message)

        self.state.turns += 1
        self.state.final_answer = answer
        return AgentResult(answer=answer, state=self.state)

