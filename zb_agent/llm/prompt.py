"""提示词模板系统"""
from __future__ import annotations
from string import Template


# 数字员工系统提示词（中文）
SYSTEM_PROMPT_ZH = """\
你是一名专业的数字员工，由智博科技开发。你具备以下核心能力：

1. **任务执行**：理解并分解复杂任务，制定执行计划
2. **工具使用**：灵活调用文件、网络、命令行等工具
3. **记忆管理**：维护短期和长期记忆，保持上下文连贯性
4. **智能问答**：基于知识库和实时信息提供准确回答
5. **中英双语**：支持中英文交流，默认使用中文

你的工作原则：
- 诚实可靠，遇到不确定的信息会明确说明
- 高效执行，尽量用最少的步骤完成任务
- 安全优先，不执行可能造成损害的操作
- 持续学习，将重要信息存入长期记忆

请始终以专业、友好的态度为用户提供帮助。
"""


class PromptTemplate:
    """提示词模板，支持 ${变量名} 占位符替换"""

    def __init__(self, template: str) -> None:
        self._template = Template(template)
        self.raw = template

    def format(self, **kwargs: str) -> str:
        """渲染模板，替换变量"""
        return self._template.safe_substitute(**kwargs)

    def __repr__(self) -> str:
        return f"PromptTemplate({self.raw[:50]!r}...)"
