"""
Agents模块

提供多Agent系统的核心组件：
- MLLMClient: MLLM API调用封装
- Multi-Agent System: 完整的多代理系统实现
  - ToolCreatorAgent: 动态工具创建Agent
  - ToolUserAgent: 工具使用和执行规划Agent
  - ToolExecutor: 工具执行引擎
  - MultiAgentCoordinator: 多代理协调器
"""

from .mllm_client import (
    MLLMClient,
    MLLMClientConfig,
    create_client
)

# Import multi-agent system components
from .multi_agent_system.tool_creator import ToolCreatorAgent
from .multi_agent_system.tool_user import ToolUserAgent
from .multi_agent_system.tool_executor import ToolExecutor
from .multi_agent_system.coordinator import MultiAgentCoordinator
from .multi_agent_system.types import (
    Tool,
    ToolParameter,
    AgentPlan,
    PlanStep
)

__all__ = [
    # MLLM Client
    'MLLMClient',
    'MLLMClientConfig',
    'create_client',

    # Multi-Agent System
    'ToolCreatorAgent',
    'ToolUserAgent',
    'ToolExecutor',
    'MultiAgentCoordinator',

    # Types
    'Tool',
    'ToolParameter',
    'AgentPlan',
    'PlanStep',
]
