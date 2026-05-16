"""数字员工 CLI 入口点"""
from __future__ import annotations
import asyncio
import os

import click
from rich.console import Console
from rich.table import Table

console = Console()


def _get_agent():
    """构建并返回代理实例"""
    from zb_agent.core.agent import AgentConfig, BaseAgent
    from zb_agent.llm.openai_provider import MockProvider, OpenAIProvider
    from zb_agent.memory.short_term import ShortTermMemory
    from zb_agent.tools.base import ToolRegistry
    from zb_agent.tools.file_tool import FileTool
    from zb_agent.tools.shell_tool import ShellTool
    from zb_agent.tools.web_tool import WebTool

    registry = ToolRegistry()
    registry.register(FileTool())
    registry.register(ShellTool())
    registry.register(WebTool())

    config = AgentConfig()
    memory = ShortTermMemory()

    if os.environ.get("OPENAI_API_KEY", "").strip():
        llm = OpenAIProvider(model=config.model)
    else:
        console.print("[yellow]⚠ 未检测到 OPENAI_API_KEY，使用 Mock Provider[/yellow]")
        llm = MockProvider()

    return BaseAgent(config=config, memory=memory, tools=registry, llm_provider=llm)


@click.group()
def main():
    """🤖 数字员工 AI Agent 系统"""


@main.command()
def chat():
    """与数字员工进行交互式对话"""
    agent = _get_agent()
    console.print("[bold green]数字员工已就绪，输入 'exit' 退出[/bold green]")
    while True:
        try:
            user_input = console.input("[bold blue]你[/bold blue]: ")
        except (EOFError, KeyboardInterrupt):
            break
        if user_input.strip().lower() in {"exit", "quit", "退出"}:
            console.print("[bold]再见！[/bold]")
            break
        result = asyncio.run(agent.run(user_input))
        console.print(f"[bold green]数字员工[/bold green]: {result}")


@main.command()
@click.argument("description")
def task(description: str):
    """提交一次性任务并执行"""
    agent = _get_agent()
    console.print(f"[bold]执行任务:[/bold] {description}")
    result = asyncio.run(agent.run(description))
    console.print(f"[bold green]结果:[/bold green] {result}")


@main.group()
def tasks():
    """任务管理命令"""


@tasks.command("list")
def tasks_list():
    """列出所有任务（示例）"""
    from zb_agent.tasks.scheduler import TaskScheduler
    from zb_agent.tasks.task import Priority, Task

    scheduler = TaskScheduler()
    scheduler.add_task(Task(title="示例任务", priority=Priority.HIGH))
    all_tasks = scheduler.list_tasks()

    table = Table(title="任务列表")
    table.add_column("ID", style="dim")
    table.add_column("标题")
    table.add_column("优先级")
    table.add_column("状态")
    for t in all_tasks:
        table.add_row(t.id[:8], t.title, t.priority.name, t.status.value)
    console.print(table)


@main.group()
def tools():
    """工具管理命令"""


@tools.command("list")
def tools_list():
    """列出所有可用工具"""
    from zb_agent.tools.base import ToolRegistry
    from zb_agent.tools.file_tool import FileTool
    from zb_agent.tools.shell_tool import ShellTool
    from zb_agent.tools.web_tool import WebTool

    registry = ToolRegistry()
    registry.register(FileTool())
    registry.register(ShellTool())
    registry.register(WebTool())

    table = Table(title="可用工具")
    table.add_column("名称", style="bold")
    table.add_column("描述")
    for t in registry.list_tools():
        table.add_row(t.name, t.description)
    console.print(table)


@main.command()
def memory():
    """显示当前记忆内容"""
    console.print("[yellow]记忆系统已就绪（当前会话记忆为空）[/yellow]")
