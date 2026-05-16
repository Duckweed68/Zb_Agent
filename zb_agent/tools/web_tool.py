"""HTTP 网页抓取工具"""
from __future__ import annotations
import httpx

from .base import BaseTool

_MAX_CONTENT_LENGTH = 5000


class WebTool(BaseTool):
    """HTTP GET 网页内容抓取工具"""

    name = "web_tool"
    description = "通过 HTTP GET 请求获取网页文本内容"
    parameters_schema = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "目标 URL"},
        },
        "required": ["url"],
    }

    async def execute(self, url: str) -> str:
        """抓取 URL 内容，返回截断后的文本"""
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            text = resp.text[:_MAX_CONTENT_LENGTH]
            if len(resp.text) > _MAX_CONTENT_LENGTH:
                text += f"\n...[内容已截断，共 {len(resp.text)} 字符]"
            return text
