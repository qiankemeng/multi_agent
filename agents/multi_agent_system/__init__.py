"""
Multi-Agent System

新的multi-agent架构：
- Tool Creator Agent: 设计工具和prompt
- Tool User Agent: 规划和执行工具
- Tool Executor: 执行引擎
- Coordinator: 协调器
"""

from .types import (
    # 核心数据结构
    Tool, ToolParameter,
    AgentAction, AgentPlan, PlanStep,
    MultiAgentSession,

    # 枚举类型
    AgentType, ActionType, PlanStatus
)

from .tool_creator import ToolCreatorAgent
from .tool_user import ToolUserAgent
from .tool_executor import ToolExecutor
from .coordinator import MultiAgentCoordinator


__all__ = [
    # Types
    'Tool', 'ToolParameter',
    'AgentAction', 'AgentPlan', 'PlanStep',
    'MultiAgentSession',
    'AgentType', 'ActionType', 'PlanStatus',

    # Agents
    'ToolCreatorAgent',
    'ToolUserAgent',
    'ToolExecutor',
    'MultiAgentCoordinator'
]
