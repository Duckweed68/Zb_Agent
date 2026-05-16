"""消息类型和会话管理"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class MessageRole(str, Enum):
    """消息角色枚举"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """单条消息"""
    role: MessageRole
    content: str
    tool_name: Optional[str] = None
    tool_result: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def to_openai_dict(self) -> dict:
        """转换为 OpenAI API 格式"""
        d: dict = {"role": self.role.value, "content": self.content}
        if self.tool_name:
            d["name"] = self.tool_name
        return d


class Conversation:
    """会话记录，管理消息列表"""

    def __init__(self) -> None:
        self._messages: list[Message] = []

    def add(self, message: Message) -> None:
        """添加消息"""
        self._messages.append(message)

    def to_openai_format(self) -> list[dict]:
        """转换为 OpenAI API 格式的消息列表"""
        return [m.to_openai_dict() for m in self._messages]

    def last_n(self, n: int) -> list[Message]:
        """获取最近 n 条消息"""
        return self._messages[-n:] if n > 0 else []

    def clear(self) -> None:
        """清空会话"""
        self._messages.clear()

    def __len__(self) -> int:
        return len(self._messages)
