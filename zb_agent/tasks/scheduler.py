"""任务调度器，基于优先级队列"""
from __future__ import annotations
import heapq
from typing import Optional

from .task import Priority, Task, TaskStatus


class TaskScheduler:
    """优先级任务调度器"""

    def __init__(self) -> None:
        self._heap: list[Task] = []
        self._tasks: dict[str, Task] = {}

    def add_task(self, task: Task) -> str:
        """添加任务，返回任务 ID"""
        heapq.heappush(self._heap, task)
        self._tasks[task.id] = task
        return task.id

    def get_next_task(self) -> Optional[Task]:
        """弹出优先级最高的待执行任务"""
        while self._heap:
            task = heapq.heappop(self._heap)
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.RUNNING
                return task
        return None

    def update_status(
        self,
        task_id: str,
        status: TaskStatus,
        result: str | None = None,
        error: str | None = None,
    ) -> None:
        """更新任务状态"""
        task = self._tasks.get(task_id)
        if task is None:
            raise KeyError(f"任务不存在: {task_id}")
        task.status = status
        if result is not None:
            task.result = result
        if error is not None:
            task.error = error

    def list_tasks(self, status: TaskStatus | None = None) -> list[Task]:
        """列出任务，可按状态过滤"""
        tasks = list(self._tasks.values())
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, reverse=True)
