"""文件读写工具，含安全路径检查"""
from __future__ import annotations
import os
from pathlib import Path

from .base import BaseTool

# 禁止访问的危险目录前缀（系统目录和敏感凭证目录）
_BLOCKED_PREFIXES = ("/etc", "/sys", "/proc", "/dev", "/boot", "/root")

# 禁止访问的用户敏感目录（相对 home 目录）
_BLOCKED_HOME_SUBDIRS = (".ssh", ".aws", ".gnupg", ".config/gcloud", ".kube")


def _check_safe_path(path: str) -> None:
    """检查路径安全性，阻止访问系统敏感目录和用户凭证目录"""
    resolved = str(Path(path).resolve())
    for prefix in _BLOCKED_PREFIXES:
        if resolved.startswith(prefix):
            raise PermissionError(f"禁止访问受保护目录: {path}")
    # 阻止访问用户 home 目录下的敏感凭证目录
    home = os.path.expanduser("~")
    for subdir in _BLOCKED_HOME_SUBDIRS:
        blocked_home = str(Path(home) / subdir)
        if resolved.startswith(blocked_home):
            raise PermissionError(f"禁止访问用户凭证目录: {path}")


class FileTool(BaseTool):
    """文件系统操作工具"""

    name = "file_tool"
    description = "读取、写入文件或列出目录内容"
    parameters_schema = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["read_file", "write_file", "list_dir"],
                "description": "操作类型",
            },
            "path": {"type": "string", "description": "文件或目录路径"},
            "content": {"type": "string", "description": "写入内容（write_file 时必填）"},
        },
        "required": ["action", "path"],
    }

    async def execute(self, action: str, path: str, content: str = "") -> str:
        """执行文件操作"""
        _check_safe_path(path)
        if action == "read_file":
            return self._read_file(path)
        if action == "write_file":
            return self._write_file(path, content)
        if action == "list_dir":
            return self._list_dir(path)
        raise ValueError(f"未知操作: {action}")

    def _read_file(self, path: str) -> str:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        return p.read_text(encoding="utf-8")

    def _write_file(self, path: str, content: str) -> str:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"已写入文件: {path} ({len(content)} 字节)"

    def _list_dir(self, path: str) -> str:
        p = Path(path)
        if not p.is_dir():
            raise NotADirectoryError(f"不是目录: {path}")
        entries = sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name))
        lines = [
            f"{'[D]' if e.is_dir() else '[F]'} {e.name}"
            for e in entries
        ]
        return "\n".join(lines) if lines else "(空目录)"
