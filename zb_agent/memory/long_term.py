"""长期记忆：基于 SQLite 的持久化存储"""
from __future__ import annotations
import sqlite3
import threading
import time
from typing import Any, Optional

from .base import BaseMemory


class LongTermMemory(BaseMemory):
    """长期记忆，使用 SQLite 持久化，支持标签和全文搜索

    线程安全：通过 threading.Lock 保护所有数据库操作。
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        # check_same_thread=False 允许跨线程使用同一连接，
        # 由 _lock 保证线程安全（同一时刻只有一个线程持有连接）
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._lock = threading.Lock()
        self._create_tables()

    def _create_tables(self) -> None:
        """初始化数据库表结构"""
        with self._lock:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    tags TEXT DEFAULT '',
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            self._conn.commit()

    def store(self, key: str, value: Any, tags: str = "") -> None:
        """存储或更新一条长期记忆"""
        now = time.time()
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO memories (key, value, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    tags = excluded.tags,
                    updated_at = excluded.updated_at
                """,
                (key, str(value), tags, now, now),
            )
            self._conn.commit()

    def retrieve(self, key: str) -> Optional[str]:
        """检索指定键的值"""
        with self._lock:
            row = self._conn.execute(
                "SELECT value FROM memories WHERE key = ?", (key,)
            ).fetchone()
        return row[0] if row else None

    def search(self, query: str) -> list[tuple[str, Any]]:
        """全文搜索键、值和标签"""
        like = f"%{query}%"
        with self._lock:
            rows = self._conn.execute(
                "SELECT key, value FROM memories WHERE key LIKE ? OR value LIKE ? OR tags LIKE ?",
                (like, like, like),
            ).fetchall()
        return [(r[0], r[1]) for r in rows]

    def clear(self) -> None:
        """清空所有记忆"""
        with self._lock:
            self._conn.execute("DELETE FROM memories")
            self._conn.commit()

    def close(self) -> None:
        """关闭数据库连接"""
        with self._lock:
            self._conn.close()
