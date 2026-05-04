from dataclasses import dataclass
from typing import Literal, Sequence, TypedDict


ChatRole = Literal["system", "user", "assistant"]


class ChatMessageDict(TypedDict):
    role: ChatRole
    content: str


@dataclass(frozen=True)
class Message:
    role: ChatRole
    content: str

    @classmethod
    def system(cls, content: str) -> "Message":
        return cls(role="system", content=content)

    @classmethod
    def user(cls, content: str) -> "Message":
        return cls(role="user", content=content)

    @classmethod
    def assistant(cls, content: str) -> "Message":
        return cls(role="assistant", content=content)

    def to_dict(self) -> ChatMessageDict:
        return {"role": self.role, "content": self.content}


def to_message_dicts(messages: Sequence[Message]) -> list[ChatMessageDict]:
    return [message.to_dict() for message in messages]

