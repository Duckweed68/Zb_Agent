"""Shell 命令执行工具（沙箱化）"""
from __future__ import annotations
import asyncio
import re

from .base import BaseTool

# 危险命令黑名单正则
_DANGEROUS_PATTERNS = re.compile(
    r"\b(rm\s+-rf|mkfs|dd\s+if|chmod\s+777|curl\s+.*\|.*sh|wget\s+.*\|.*sh|:(){ :|:& };:)\b",
    re.IGNORECASE,
)


class ShellTool(BaseTool):
    """沙箱化 Shell 命令执行工具"""

    name = "shell_tool"
    description = "在受限环境中执行 Shell 命令"
    parameters_schema = {
        "type": "object",
        "properties": {
            "cmd": {"type": "string", "description": "要执行的命令"},
            "timeout": {"type": "integer", "description": "超时秒数，默认 10", "default": 10},
        },
        "required": ["cmd"],
    }

    async def execute(self, cmd: str, timeout: int = 10) -> str:
        """执行 Shell 命令，返回输出"""
        if _DANGEROUS_PATTERNS.search(cmd):
            raise PermissionError(f"检测到危险命令，已拒绝执行: {cmd}")

        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError as exc:
            proc.kill()
            raise TimeoutError(f"命令超时 ({timeout}s): {cmd}") from exc

        out = stdout.decode("utf-8", errors="replace").strip()
        err = stderr.decode("utf-8", errors="replace").strip()
        if err:
            return f"{out}\n[stderr]: {err}".strip()
        return out
