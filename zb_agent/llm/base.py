"""LLM Provider 抽象接口"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional


class BaseLLMProvider(ABC):
    """LLM 服务提供者抽象基类"""

    @abstractmethod
    async def complete(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
    ) -> str:
        """发送消息列表，返回模型回复文本"""
