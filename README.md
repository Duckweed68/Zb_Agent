# Zb_Agent — 数字员工 AI Agent 系统

> **Digital Employee AI Agent System** — A comprehensive Python framework for building intelligent digital employees powered by LLMs.

## Features

- 🤖 **Core Agent** — ReAct-style planning loop with tool use, configurable roles, and iterative reasoning
- 🧠 **Memory System** — Short-term (in-memory deque) and long-term (SQLite) memory with full-text search
- 🔧 **Tool System** — File I/O, sandboxed shell execution, and HTTP web fetching with safety guards
- 📋 **Task Scheduler** — Priority-based task queue with status lifecycle management
- 🔌 **LLM Integration** — OpenAI-compatible provider + mock provider for testing
- 💬 **Prompt Templates** — `${variable}` substitution with Chinese system prompts built-in
- 🖥️ **CLI** — Rich terminal interface (`zb-agent chat`, `zb-agent task`, etc.)

## Project Structure

```
Zb_Agent/
├── pyproject.toml
├── zb_agent/
│   ├── core/          # Agent, Message, StateMachine
│   ├── memory/        # ShortTermMemory, LongTermMemory
│   ├── tools/         # FileTool, ShellTool, WebTool
│   ├── tasks/         # Task, TaskScheduler
│   ├── llm/           # BaseLLMProvider, OpenAIProvider, MockProvider, PromptTemplate
│   └── cli.py         # Click CLI entry point
└── tests/             # 60 unit tests across all modules
```

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

```bash
# Interactive chat
zb-agent chat

# One-shot task
zb-agent task "查找当前目录下所有 Python 文件"

# List tools
zb-agent tools list

# List tasks
zb-agent tasks list
```

### Programmatic API

```python
import asyncio
from zb_agent.core.agent import AgentConfig, BaseAgent
from zb_agent.llm.openai_provider import OpenAIProvider
from zb_agent.memory.short_term import ShortTermMemory
from zb_agent.tools.base import ToolRegistry
from zb_agent.tools.file_tool import FileTool

registry = ToolRegistry()
registry.register(FileTool())

agent = BaseAgent(
    config=AgentConfig(name="小智", role="文件管理专家"),
    memory=ShortTermMemory(),
    tools=registry,
    llm_provider=OpenAIProvider(api_key="sk-..."),
)

result = asyncio.run(agent.run("列出当前目录下的所有文件"))
print(result)
```

## Environment Variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key (falls back to MockProvider if unset) |

## Running Tests

```bash
python -m pytest tests/ -v
```

All 60 tests pass.
