"""OpenAI 兼容的 LLM Provider"""
from __future__ import annotations
import os
from typing import Optional

from .base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """调用 OpenAI API 的 LLM Provider"""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
    ) -> None:
        from openai import AsyncOpenAI  # 延迟导入，避免无 key 时崩溃

        self.model = model
        self.temperature = temperature
        self._client = AsyncOpenAI(
            api_key=api_key or os.environ.get("OPENAI_API_KEY", ""),
            base_url=base_url,
        )

    async def complete(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
    ) -> str:
        """调用 OpenAI Chat Completion API"""
        kwargs: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        if tools:
            kwargs["tools"] = tools

        response = await self._client.chat.completions.create(**kwargs)
        if not response.choices:
            return ""
        return response.choices[0].message.content or ""


class MockProvider(BaseLLMProvider):
    """用于测试的 Mock LLM Provider，返回预设脚本化回复"""

    def __init__(self, responses: list[str] | None = None) -> None:
        # 支持循环重复最后一条回复
        self._responses = responses or ['{"final_answer": "任务完成"}']
        self._index = 0

    async def complete(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
    ) -> str:
        """返回下一条预设回复"""
        resp = self._responses[min(self._index, len(self._responses) - 1)]
        self._index += 1
        return resp

    def reset(self) -> None:
        """重置回复序列"""
        self._index = 0
