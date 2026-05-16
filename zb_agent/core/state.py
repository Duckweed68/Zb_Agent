"""代理状态机"""
from __future__ import annotations
from enum import Enum
from typing import Dict, Set


class AgentState(str, Enum):
    """代理生命周期状态"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    WAITING = "waiting"
    DONE = "done"
    ERROR = "error"


# 合法的状态转换表
_DEFAULT_TRANSITIONS: Dict[AgentState, Set[AgentState]] = {
    AgentState.IDLE:     {AgentState.THINKING, AgentState.ERROR},
    AgentState.THINKING: {AgentState.ACTING, AgentState.DONE, AgentState.ERROR, AgentState.WAITING},
    AgentState.ACTING:   {AgentState.THINKING, AgentState.DONE, AgentState.ERROR, AgentState.WAITING},
    AgentState.WAITING:  {AgentState.THINKING, AgentState.DONE, AgentState.ERROR},
    AgentState.DONE:     {AgentState.IDLE},
    AgentState.ERROR:    {AgentState.IDLE},
}


class StateMachine:
    """有限状态机，管理代理状态转换"""

    def __init__(
        self,
        initial: AgentState = AgentState.IDLE,
        transitions: Dict[AgentState, Set[AgentState]] | None = None,
    ) -> None:
        self.current_state: AgentState = initial
        self.transitions = transitions or _DEFAULT_TRANSITIONS

    def can_transition(self, new_state: AgentState) -> bool:
        """检查是否可以转换到目标状态"""
        allowed = self.transitions.get(self.current_state, set())
        return new_state in allowed

    def transition(self, new_state: AgentState) -> None:
        """执行状态转换，不合法时抛出 ValueError"""
        if not self.can_transition(new_state):
            raise ValueError(
                f"非法状态转换: {self.current_state} → {new_state}"
            )
        self.current_state = new_state
