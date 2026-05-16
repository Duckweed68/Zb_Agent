"""短期记忆：基于 deque 的内存存储"""
from __future__ import annotations
from collections import deque
from typing import Any, Optional

from .base import BaseMemory


class ShortTermMemory(BaseMemory):
    """短期记忆，使用双端队列，超出容量时自动丢弃最旧条目"""

    def __init__(self, max_size: int = 100) -> None:
        self.max_size = max_size
        # 按插入顺序保留最新 max_size 条
        self._queue: deque[tuple[str, Any]] = deque(maxlen=max_size)
        # 最新值索引（同 key 覆盖）
        self._index: dict[str, Any] = {}

    def store(self, key: str, value: Any) -> None:
        """存储或覆盖一条记忆"""
        if key in self._index:
            # 移除旧条目
            self._queue = deque(
                ((k, v) for k, v in self._queue if k != key),
                maxlen=self.max_size,
            )
        self._queue.append((key, value))
        self._index[key] = value

    def retrieve(self, key: str) -> Optional[Any]:
        """检索最新值"""
        return self._index.get(key)

    def search(self, query: str) -> list[tuple[str, Any]]:
        """在键和值的字符串表示中搜索关键词"""
        q = query.lower()
        return [
            (k, v) for k, v in self._queue
            if q in k.lower() or q in str(v).lower()
        ]

    def clear(self) -> None:
        """清空短期记忆"""
        self._queue.clear()
        self._index.clear()

    def __len__(self) -> int:
        return len(self._queue)
