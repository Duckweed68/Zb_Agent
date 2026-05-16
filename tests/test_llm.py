"""LLM 集成层测试"""
import pytest
from zb_agent.llm.openai_provider import MockProvider
from zb_agent.llm.prompt import PromptTemplate, SYSTEM_PROMPT_ZH


# ── MockProvider ─────────────────────────────────────────────
@pytest.mark.asyncio
async def test_mock_provider_returns_response():
    provider = MockProvider(responses=["你好，我是数字员工"])
    result = await provider.complete([{"role": "user", "content": "hello"}])
    assert result == "你好，我是数字员工"


@pytest.mark.asyncio
async def test_mock_provider_multiple_responses():
    provider = MockProvider(responses=["第一条", "第二条", "第三条"])
    r1 = await provider.complete([])
    r2 = await provider.complete([])
    r3 = await provider.complete([])
    assert r1 == "第一条"
    assert r2 == "第二条"
    assert r3 == "第三条"


@pytest.mark.asyncio
async def test_mock_provider_repeats_last():
    """超出预设回复数量时，重复最后一条回复"""
    provider = MockProvider(responses=["唯一回复"])
    for _ in range(5):
        result = await provider.complete([])
        assert result == "唯一回复"


@pytest.mark.asyncio
async def test_mock_provider_reset():
    provider = MockProvider(responses=["A", "B"])
    await provider.complete([])
    provider.reset()
    result = await provider.complete([])
    assert result == "A"


# ── PromptTemplate ───────────────────────────────────────────
def test_prompt_template_format():
    tmpl = PromptTemplate("你好，${name}！你的角色是 ${role}。")
    result = tmpl.format(name="小智", role="数据分析师")
    assert result == "你好，小智！你的角色是 数据分析师。"


def test_prompt_template_partial_format():
    """safe_substitute 不报错，未替换变量保持原样"""
    tmpl = PromptTemplate("你好，${name}！${未知变量}")
    result = tmpl.format(name="小智")
    assert "小智" in result
    assert "${未知变量}" in result


def test_prompt_template_repr():
    tmpl = PromptTemplate("短模板")
    assert "PromptTemplate" in repr(tmpl)


# ── SYSTEM_PROMPT_ZH ─────────────────────────────────────────
def test_system_prompt_zh_not_empty():
    assert len(SYSTEM_PROMPT_ZH) > 100


def test_system_prompt_zh_contains_keywords():
    assert "数字员工" in SYSTEM_PROMPT_ZH
    assert "工具" in SYSTEM_PROMPT_ZH


# ── OpenAIProvider 配置测试（不调用实际 API）────────────────
def test_openai_provider_init_with_fake_key():
    """验证 OpenAIProvider 可以用 fake key 实例化，不报错"""
    from zb_agent.llm.openai_provider import OpenAIProvider
    provider = OpenAIProvider(model="gpt-4o-mini", api_key="sk-fake-key-for-testing")
    assert provider.model == "gpt-4o-mini"
    assert provider.temperature == 0.7


def test_openai_provider_raises_without_key(monkeypatch):
    """验证未提供 API key 时抛出 ValueError"""
    import os
    from zb_agent.llm.openai_provider import OpenAIProvider
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        OpenAIProvider(model="gpt-4o-mini")
