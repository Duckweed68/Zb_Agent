"""任务管理测试"""
import pytest
from zb_agent.tasks.task import Priority, Task, TaskStatus
from zb_agent.tasks.scheduler import TaskScheduler


# ── Task ─────────────────────────────────────────────────────
def test_task_defaults():
    t = Task(title="测试任务")
    assert t.status == TaskStatus.PENDING
    assert t.priority == Priority.MEDIUM
    assert t.id  # 有 UUID
    assert t.result is None
    assert t.error is None


def test_task_custom_priority():
    t = Task(title="紧急任务", priority=Priority.CRITICAL)
    assert t.priority == Priority.CRITICAL


def test_task_comparison():
    high = Task(title="高优先级", priority=Priority.HIGH)
    low = Task(title="低优先级", priority=Priority.LOW)
    # 高优先级 < 低优先级 (因为 __lt__ 按优先级降序排列，高优先级先被弹出)
    assert high < low


# ── TaskScheduler ────────────────────────────────────────────
def test_scheduler_add_and_get():
    sched = TaskScheduler()
    t = Task(title="任务A", priority=Priority.HIGH)
    task_id = sched.add_task(t)
    assert task_id == t.id
    next_task = sched.get_next_task()
    assert next_task is not None
    assert next_task.title == "任务A"
    assert next_task.status == TaskStatus.RUNNING


def test_scheduler_priority_ordering():
    sched = TaskScheduler()
    low = Task(title="低优先级", priority=Priority.LOW)
    critical = Task(title="最高优先级", priority=Priority.CRITICAL)
    medium = Task(title="中优先级", priority=Priority.MEDIUM)

    sched.add_task(low)
    sched.add_task(medium)
    sched.add_task(critical)

    first = sched.get_next_task()
    assert first.title == "最高优先级"

    second = sched.get_next_task()
    assert second.title == "中优先级"


def test_scheduler_update_status():
    sched = TaskScheduler()
    t = Task(title="状态测试")
    sched.add_task(t)
    sched.update_status(t.id, TaskStatus.COMPLETED, result="成功")
    assert sched._tasks[t.id].status == TaskStatus.COMPLETED
    assert sched._tasks[t.id].result == "成功"


def test_scheduler_update_status_with_error():
    sched = TaskScheduler()
    t = Task(title="失败任务")
    sched.add_task(t)
    sched.update_status(t.id, TaskStatus.FAILED, error="超时")
    assert sched._tasks[t.id].error == "超时"


def test_scheduler_list_tasks():
    sched = TaskScheduler()
    for i in range(3):
        sched.add_task(Task(title=f"任务{i}"))
    assert len(sched.list_tasks()) == 3


def test_scheduler_list_tasks_by_status():
    sched = TaskScheduler()
    t1 = Task(title="任务1")
    t2 = Task(title="任务2")
    sched.add_task(t1)
    sched.add_task(t2)
    sched.get_next_task()  # t1 变为 RUNNING

    pending = sched.list_tasks(status=TaskStatus.PENDING)
    assert all(t.status == TaskStatus.PENDING for t in pending)


def test_scheduler_empty_queue():
    sched = TaskScheduler()
    assert sched.get_next_task() is None


def test_scheduler_update_nonexistent():
    sched = TaskScheduler()
    with pytest.raises(KeyError):
        sched.update_status("nonexistent-id", TaskStatus.COMPLETED)
