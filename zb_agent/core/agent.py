"""数字员工核心代理类
负责协调工具、记忆、任务和LLM的统一代理框架
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from .message import Conversation, Message, MessageRole
from .state import AgentState, StateMachine

if TYPE_CHECKING:
    from zb_agent.llm.base import BaseLLMProvider
    from zb_agent.memory.base import BaseMemory
    from zb_agent.tools.base import ToolRegistry


@dataclass
class AgentConfig:
    """代理配置"""
    name: str = "数字员工"
    role: str = "通用数字员工助手"
    model: str = "gpt-4o-mini"
    max_iterations: int = 10
    temperature: float = 0.7


@dataclass
class AgentAction:
    """代理单步动作"""
    thought: str = ""
    tool_name: Optional[str] = None
    tool_args: dict = field(default_factory=dict)
    final_answer: Optional[str] = None


class BaseAgent:
    """数字员工基础代理

    协调 LLM、工具、记忆系统，完成用户交代的任务。
    """

    def __init__(
        self,
        config: AgentConfig,
        memory: "BaseMemory",
        tools: "ToolRegistry",
        llm_provider: "BaseLLMProvider",
    ) -> None:
        self.config = config
        self.memory = memory
        self.tools = tools
        self.llm = llm_provider
        self.state_machine = StateMachine()
        self.conversation = Conversation()

    def _build_system_prompt(self) -> str:
        """构建系统提示词，包含角色定义和可用工具说明"""
        tool_list = "\n".join(
            f"- {t.name}: {t.description}"
            for t in self.tools.list_tools()
        )
        return (
            f"你是「{self.config.name}」，{self.config.role}。\n"
            "你能够使用工具完成各种任务，并保持上下文记忆。\n\n"
            f"可用工具:\n{tool_list}\n\n"
            "当需要调用工具时，以 JSON 格式回复:\n"
            '{"tool_call": {"name": "<工具名>", "args": {<参数>}}}\n\n'
            "当任务完成时，以 JSON 格式回复:\n"
            '{"final_answer": "<你的最终回答>"}\n\n'
            "否则直接以纯文本回复即可。"
        )

    async def step(self, messages: list[dict]) -> AgentAction:
        """单步 LLM 推理，解析动作"""
        raw = await self.llm.complete(messages)

        # 尝试解析 JSON 动作
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                if "tool_call" in data:
                    tc = data["tool_call"]
                    return AgentAction(
                        thought=raw,
                        tool_name=tc.get("name"),
                        tool_args=tc.get("args", {}),
                    )
                if "final_answer" in data:
                    return AgentAction(
                        thought=raw,
                        final_answer=data["final_answer"],
                    )
            except (json.JSONDecodeError, KeyError):
                pass

        # 纯文本回复视为最终答案
        return AgentAction(thought=raw, final_answer=raw)

    async def run(self, task: str) -> str:
        """主运行循环: 规划 → 调用工具 → 综合结果"""
        self.state_machine.transition(AgentState.THINKING)

        # 初始化会话
        self.conversation.clear()
        self.conversation.add(Message(
            role=MessageRole.SYSTEM,
            content=self._build_system_prompt(),
        ))
        self.conversation.add(Message(
            role=MessageRole.USER,
            content=task,
        ))

        # 将任务存入记忆
        self.memory.store("last_task", task)

        result = "任务执行完毕，但未生成最终回答。"

        for iteration in range(self.config.max_iterations):
            try:
                action = await self.step(self.conversation.to_openai_format())
            except Exception as exc:  # noqa: BLE001
                self.state_machine.transition(AgentState.ERROR)
                self.state_machine.transition(AgentState.IDLE)
                return f"[错误] LLM 调用失败: {exc}"

            # 添加助手消息
            self.conversation.add(Message(
                role=MessageRole.ASSISTANT,
                content=action.thought,
            ))

            if action.final_answer is not None:
                result = action.final_answer
                break

            if action.tool_name:
                self.state_machine.transition(AgentState.ACTING)
                tool_result = await self._call_tool(action.tool_name, action.tool_args)
                self.conversation.add(Message(
                    role=MessageRole.TOOL,
                    content=tool_result,
                    tool_name=action.tool_name,
                    tool_result=tool_result,
                ))
                self.state_machine.transition(AgentState.THINKING)
            else:
                # 没有工具调用也没有最终答案，退出循环
                result = action.thought
                break

        # 存储结果
        self.memory.store("last_result", result)
        self.state_machine.transition(AgentState.DONE)
        self.state_machine.transition(AgentState.IDLE)
        return result

    async def _call_tool(self, tool_name: str, args: dict) -> str:
        """安全调用工具，失败时返回错误信息"""
        tool = self.tools.get_tool(tool_name)
        if tool is None:
            return f"[工具错误] 未找到工具: {tool_name}"
        try:
            return await tool.execute(**args)
        except Exception as exc:  # noqa: BLE001
            return f"[工具错误] {tool_name} 执行失败: {exc}"
