import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from messages import ChatRole, Message


@dataclass(frozen=True)
class MemoryRecord:
    timestamp: str
    role: ChatRole
    content: str

    @classmethod
    def from_message(cls, message: Message) -> "MemoryRecord":
        return cls(
            timestamp=datetime.now(timezone.utc).isoformat(),
            role=message.role,
            content=message.content,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryRecord":
        return cls(
            timestamp=str(data["timestamp"]),
            role=data["role"],
            content=str(data["content"]),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "timestamp": self.timestamp,
            "role": self.role,
            "content": self.content,
        }

    def to_message(self) -> Message:
        return Message(role=self.role, content=self.content)


class ConversationMemory:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(self, message: Message) -> None:
        record = MemoryRecord.from_message(message)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")

    def load_all(self) -> list[Message]:
        if not self.path.exists():
            return []

        records: list[MemoryRecord] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                records.append(MemoryRecord.from_dict(json.loads(line)))
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                continue

        return [record.to_message() for record in records]


def new_session_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


class ConversationStore:
    def __init__(self, root: str = "memory/sessions") -> None:
        self.root = Path(root)

    def session_path(self, session_id: str) -> Path:
        if not session_id:
            raise ValueError("session_id must not be empty")
        if "/" in session_id or "\\" in session_id or session_id in {".", ".."}:
            raise ValueError("session_id must be a simple file name")
        return self.root / f"{session_id}.jsonl"

    def open(self, session_id: str | None = None) -> tuple[str, ConversationMemory]:
        resolved_session_id = session_id or new_session_id()
        return resolved_session_id, ConversationMemory(
            self.session_path(resolved_session_id)
        )
