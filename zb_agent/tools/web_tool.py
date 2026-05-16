"""HTTP 网页抓取工具"""
from __future__ import annotations
import ipaddress
import re
from urllib.parse import urlparse

import httpx

from .base import BaseTool

_MAX_CONTENT_LENGTH = 5000

# 阻止访问的内部/元数据 IP 段（防止 SSRF 攻击）
_BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network(cidr)
    for cidr in (
        "127.0.0.0/8",       # loopback
        "10.0.0.0/8",        # RFC-1918 private
        "172.16.0.0/12",     # RFC-1918 private
        "192.168.0.0/16",    # RFC-1918 private
        "169.254.0.0/16",    # link-local / AWS metadata
        "::1/128",           # IPv6 loopback
        "fc00::/7",          # IPv6 unique-local
    )
]


def _validate_url(url: str) -> None:
    """验证 URL 合法性，阻止 SSRF 攻击（内网地址、元数据服务等）"""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"不支持的协议: {parsed.scheme}")
    hostname = parsed.hostname or ""
    # 阻止 localhost 及其变体
    if hostname in ("localhost", ""):
        raise PermissionError(f"禁止访问本地地址: {url}")
    # 解析并检查 IP 地址是否属于内部网段
    try:
        ip = ipaddress.ip_address(hostname)
        for network in _BLOCKED_IP_NETWORKS:
            if ip in network:
                raise PermissionError(f"禁止访问内部/元数据地址: {url}")
    except ValueError:
        pass  # hostname 不是 IP 地址，跳过 IP 检查


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
        """抓取 URL 内容，返回截断后的文本（含 SSRF 防护）"""
        _validate_url(url)
        async with httpx.AsyncClient(follow_redirects=False, timeout=15.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            text = resp.text[:_MAX_CONTENT_LENGTH]
            if len(resp.text) > _MAX_CONTENT_LENGTH:
                text += f"\n...[内容已截断，共 {len(resp.text)} 字符]"
            return text
