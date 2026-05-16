"""工具系统基础接口和注册中心"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional


class BaseTool(ABC):
    """工具抽象基类"""

    name: str
    description: str
    parameters_schema: dict

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """执行工具，返回字符串结果"""


class ToolRegistry:
    """工具注册中心，管理所有可用工具"""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """注册工具"""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """按名称获取工具"""
        return self._tools.get(name)

    def list_tools(self) -> list[BaseTool]:
        """列出所有已注册工具"""
        return list(self._tools.values())

    def to_openai_functions_format(self) -> list[dict]:
        """转换为 OpenAI function calling 格式"""
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters_schema,
                },
            }
            for t in self._tools.values()
        ]
