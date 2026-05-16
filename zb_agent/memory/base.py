"""记忆系统基础接口"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseMemory(ABC):
    """记忆系统抽象基类"""

    @abstractmethod
    def store(self, key: str, value: Any) -> None:
        """存储键值对"""

    @abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        """检索指定键的值"""

    @abstractmethod
    def search(self, query: str) -> list[tuple[str, Any]]:
        """全文搜索，返回匹配的 (key, value) 列表"""

    @abstractmethod
    def clear(self) -> None:
        """清空记忆"""
