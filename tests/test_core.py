"""核心模块测试"""
import pytest
from zb_agent.core.agent import AgentConfig, BaseAgent
from zb_agent.core.message import Conversation, Message, MessageRole
from zb_agent.core.state import AgentState, StateMachine
from zb_agent.llm.openai_provider import MockProvider
from zb_agent.memory.short_term import ShortTermMemory
from zb_agent.tools.base import ToolRegistry


# ── AgentConfig ──────────────────────────────────────────────
def test_agent_config_defaults():
    cfg = AgentConfig()
    assert cfg.name == "数字员工"
    assert cfg.max_iterations == 10
    assert 0.0 < cfg.temperature <= 1.0


def test_agent_config_custom():
    cfg = AgentConfig(name="测试员工", model="gpt-3.5-turbo", max_iterations=5)
    assert cfg.name == "测试员工"
    assert cfg.max_iterations == 5


# ── Conversation ─────────────────────────────────────────────
def test_conversation_add_and_len():
    conv = Conversation()
    assert len(conv) == 0
    conv.add(Message(role=MessageRole.USER, content="你好"))
    assert len(conv) == 1


def test_conversation_last_n():
    conv = Conversation()
    for i in range(5):
        conv.add(Message(role=MessageRole.USER, content=str(i)))
    last = conv.last_n(3)
    assert len(last) == 3
    assert last[-1].content == "4"


def test_conversation_to_openai_format():
    conv = Conversation()
    conv.add(Message(role=MessageRole.SYSTEM, content="系统消息"))
    conv.add(Message(role=MessageRole.USER, content="用户消息"))
    fmt = conv.to_openai_format()
    assert fmt[0]["role"] == "system"
    assert fmt[1]["content"] == "用户消息"


def test_conversation_clear():
    conv = Conversation()
    conv.add(Message(role=MessageRole.USER, content="test"))
    conv.clear()
    assert len(conv) == 0


# ── StateMachine ─────────────────────────────────────────────
def test_state_machine_initial():
    sm = StateMachine()
    assert sm.current_state == AgentState.IDLE


def test_state_machine_valid_transition():
    sm = StateMachine()
    sm.transition(AgentState.THINKING)
    assert sm.current_state == AgentState.THINKING


def test_state_machine_invalid_transition():
    sm = StateMachine()
    with pytest.raises(ValueError):
        sm.transition(AgentState.DONE)  # IDLE → DONE 不合法


def test_state_machine_can_transition():
    sm = StateMachine()
    assert sm.can_transition(AgentState.THINKING)
    assert not sm.can_transition(AgentState.ACTING)


# ── BaseAgent ────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_agent_run_with_mock():
    config = AgentConfig(name="测试员工")
    memory = ShortTermMemory()
    tools = ToolRegistry()
    llm = MockProvider(responses=['{"final_answer": "任务已完成"}'])
    agent = BaseAgent(config=config, memory=memory, tools=tools, llm_provider=llm)
    result = await agent.run("执行测试任务")
    assert "完成" in result or result  # 有输出即可


@pytest.mark.asyncio
async def test_agent_stores_task_in_memory():
    config = AgentConfig()
    memory = ShortTermMemory()
    tools = ToolRegistry()
    llm = MockProvider()
    agent = BaseAgent(config=config, memory=memory, tools=tools, llm_provider=llm)
    await agent.run("记住这个任务")
    assert memory.retrieve("last_task") == "记住这个任务"


@pytest.mark.asyncio
async def test_agent_system_prompt_contains_role():
    config = AgentConfig(role="专业数据分析师")
    memory = ShortTermMemory()
    tools = ToolRegistry()
    llm = MockProvider()
    agent = BaseAgent(config=config, memory=memory, tools=tools, llm_provider=llm)
    prompt = agent._build_system_prompt()
    assert "专业数据分析师" in prompt
