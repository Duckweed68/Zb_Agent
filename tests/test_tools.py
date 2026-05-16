"""工具系统测试"""
import os
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from zb_agent.tools.base import BaseTool, ToolRegistry
from zb_agent.tools.file_tool import FileTool
from zb_agent.tools.shell_tool import ShellTool
from zb_agent.tools.web_tool import WebTool


# ── ToolRegistry ─────────────────────────────────────────────
def test_registry_register_and_list():
    registry = ToolRegistry()
    registry.register(FileTool())
    tools = registry.list_tools()
    assert any(t.name == "file_tool" for t in tools)


def test_registry_get_tool():
    registry = ToolRegistry()
    ft = FileTool()
    registry.register(ft)
    assert registry.get_tool("file_tool") is ft


def test_registry_get_missing():
    registry = ToolRegistry()
    assert registry.get_tool("nonexistent") is None


def test_registry_to_openai_format():
    registry = ToolRegistry()
    registry.register(FileTool())
    fmt = registry.to_openai_functions_format()
    assert len(fmt) == 1
    assert fmt[0]["type"] == "function"
    assert "name" in fmt[0]["function"]


# ── FileTool ─────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_file_tool_write_and_read(tmp_path):
    ft = FileTool()
    test_file = str(tmp_path / "test.txt")
    result = await ft.execute(action="write_file", path=test_file, content="你好世界")
    assert "已写入" in result

    content = await ft.execute(action="read_file", path=test_file)
    assert content == "你好世界"


@pytest.mark.asyncio
async def test_file_tool_list_dir(tmp_path):
    (tmp_path / "dir_a").mkdir()
    (tmp_path / "file_b.txt").write_text("hello")
    ft = FileTool()
    result = await ft.execute(action="list_dir", path=str(tmp_path))
    assert "dir_a" in result
    assert "file_b.txt" in result


@pytest.mark.asyncio
async def test_file_tool_blocked_path():
    ft = FileTool()
    with pytest.raises(PermissionError):
        await ft.execute(action="read_file", path="/etc/passwd")


@pytest.mark.asyncio
async def test_file_tool_missing_file(tmp_path):
    ft = FileTool()
    with pytest.raises(FileNotFoundError):
        await ft.execute(action="read_file", path=str(tmp_path / "missing.txt"))


# ── ShellTool ─────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_shell_tool_echo():
    st = ShellTool()
    result = await st.execute(cmd="echo 你好")
    assert "你好" in result


@pytest.mark.asyncio
async def test_shell_tool_dangerous_command():
    st = ShellTool()
    with pytest.raises(PermissionError):
        await st.execute(cmd="rm -rf /tmp/test")


@pytest.mark.asyncio
async def test_shell_tool_chmod_777_blocked():
    """测试 chmod 777 和八进制变体被阻止"""
    st = ShellTool()
    with pytest.raises(PermissionError):
        await st.execute(cmd="chmod 777 /tmp/test")
    with pytest.raises(PermissionError):
        await st.execute(cmd="chmod 0777 /tmp/test")


@pytest.mark.asyncio
async def test_shell_tool_pwd():
    st = ShellTool()
    result = await st.execute(cmd="pwd")
    assert "/" in result


# ── WebTool ───────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_web_tool_fetch():
    """测试 WebTool，mock httpx 请求"""
    import httpx
    from unittest.mock import patch, AsyncMock

    wt = WebTool()

    mock_response = MagicMock()
    mock_response.text = "<html>测试内容</html>"
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await wt.execute(url="https://example.com")
    assert "测试内容" in result


@pytest.mark.asyncio
async def test_web_tool_truncation():
    """测试内容截断"""
    from unittest.mock import patch, AsyncMock, MagicMock

    wt = WebTool()
    long_content = "A" * 10000

    mock_response = MagicMock()
    mock_response.text = long_content
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await wt.execute(url="https://example.com")
    assert "截断" in result
    assert len(result) < len(long_content)


@pytest.mark.asyncio
async def test_web_tool_ssrf_localhost_blocked():
    """测试 SSRF 防护：localhost 被阻止"""
    wt = WebTool()
    with pytest.raises(PermissionError):
        await wt.execute(url="http://localhost:8080/secret")


@pytest.mark.asyncio
async def test_web_tool_ssrf_metadata_blocked():
    """测试 SSRF 防护：AWS 元数据服务 169.254.169.254 被阻止"""
    wt = WebTool()
    with pytest.raises(PermissionError):
        await wt.execute(url="http://169.254.169.254/latest/meta-data/")


@pytest.mark.asyncio
async def test_web_tool_invalid_scheme_blocked():
    """测试非 HTTP/HTTPS 协议被阻止"""
    wt = WebTool()
    with pytest.raises(ValueError):
        await wt.execute(url="ftp://example.com/file")
