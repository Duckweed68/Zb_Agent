"""任务数据模型"""
from __future__ import annotations
import uuid
import time
from dataclasses import dataclass, field
from enum import IntEnum, Enum
from typing import Optional


class Priority(IntEnum):
    """任务优先级"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """任务数据类"""
    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = field(default=TaskStatus.PENDING)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    result: Optional[str] = None
    error: Optional[str] = None

    def __lt__(self, other: "Task") -> bool:
        """优先级队列比较：优先级高的排前面（取反），同优先级按时间升序"""
        if self.priority != other.priority:
            return self.priority > other.priority
        return self.created_at < other.created_at
