"""
Multi-Agent Core Data Structures

定义Tool、AgentAction、AgentPlan等核心数据结构
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class AgentType(Enum):
    """Agent类型"""
    TOOL_CREATOR = "tool_creator"
    TOOL_USER = "tool_user"


class ActionType(Enum):
    """行动类型"""
    DESIGN_TOOL = "design_tool"
    USE_TOOL = "use_tool"
    PLAN = "plan"
    REASON = "reason"
    EXECUTE = "execute"


class PlanStatus(Enum):
    """计划状态"""
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


# ==================== Tool Definition ====================

@dataclass
class ToolParameter:
    """工具参数定义"""
    name: str
    type: str  # "str", "int", "float", "Segment", "Frame", etc.
    description: str = ""
    required: bool = True
    default: Any = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "required": self.required,
            "default": self.default
        }


@dataclass
class Tool:
    """
    工具定义 - 由Tool Creator Agent设计

    工具封装了一组原子操作，并包含专门设计的prompt
    """
    tool_id: str
    tool_name: str
    description: str

    # 核心：Prompt设计
    purpose: str                             # 工具目的
    prompt_template: str                     # Prompt模板（包含占位符{var}）
    system_prompt: str = "You are a helpful AI assistant."

    # 参数定义
    parameters: Dict[str, ToolParameter] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)

    # 使用的原子操作
    atomic_operations: List[str] = field(default_factory=list)

    # 使用指南
    usage_example: str = ""
    best_practices: List[str] = field(default_factory=list)

    # 元数据
    created_by: str = ""  # agent_id
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "tool_name": self.tool_name,
            "description": self.description,
            "purpose": self.purpose,
            "prompt_template": self.prompt_template,
            "system_prompt": self.system_prompt,
            "parameters": {k: v.to_dict() for k, v in self.parameters.items()},
            "output_schema": self.output_schema,
            "atomic_operations": self.atomic_operations,
            "usage_example": self.usage_example,
            "best_practices": self.best_practices,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "version": self.version
        }


# ==================== Agent Action ====================

@dataclass
class AgentAction:
    """
    Agent的单次行动记录

    记录Agent的决策、推理和执行过程
    """
    action_id: str
    agent_id: str
    agent_type: AgentType
    action_type: ActionType

    # 行动内容
    tool: Optional[Tool] = None
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)

    # 推理过程
    reasoning: str = ""
    confidence: float = 1.0

    # 统计
    tokens_used: int = 0
    cost_usd: float = 0.0
    duration_ms: float = 0.0

    # 元数据
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "pending"  # pending, running, completed, failed
    error_message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "action_type": self.action_type.value,
            "tool": self.tool.to_dict() if self.tool else None,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
            "status": self.status,
            "error_message": self.error_message
        }


# ==================== Agent Plan ====================

@dataclass
class PlanStep:
    """执行计划中的单个步骤"""
    step_id: str
    tool_name: str
    tool_id: str

    # 输入输出
    inputs: Dict[str, Any] = field(default_factory=dict)
    expected_output: str = ""
    actual_output: Any = None

    # 依赖关系
    dependencies: List[str] = field(default_factory=list)  # 依赖哪些step_id

    # 执行状态
    status: str = "pending"  # pending, running, completed, failed, skipped
    execution_result: Optional[AgentAction] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "tool_name": self.tool_name,
            "tool_id": self.tool_id,
            "inputs": self.inputs,
            "expected_output": self.expected_output,
            "actual_output": self.actual_output,
            "dependencies": self.dependencies,
            "status": self.status,
            "execution_result": self.execution_result.to_dict() if self.execution_result else None
        }


@dataclass
class AgentPlan:
    """
    Tool User Agent的执行计划

    包含完整的执行步骤和依赖关系
    """
    plan_id: str
    task_description: str

    # 计划步骤
    steps: List[PlanStep] = field(default_factory=list)

    # 可用资源
    available_tools: List[Tool] = field(default_factory=list)

    # 执行状态
    current_step: int = 0
    status: PlanStatus = PlanStatus.PLANNING

    # 推理
    reasoning: str = ""  # 为什么这样规划

    # 统计
    total_tokens: int = 0
    total_cost: float = 0.0
    total_duration_ms: float = 0.0

    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "task_description": self.task_description,
            "steps": [step.to_dict() for step in self.steps],
            "available_tools": [tool.to_dict() for tool in self.available_tools],
            "current_step": self.current_step,
            "status": self.status.value,
            "reasoning": self.reasoning,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "total_duration_ms": self.total_duration_ms,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }


# ==================== Multi-Agent Session ====================

@dataclass
class MultiAgentSession:
    """
    Multi-Agent会话记录

    记录整个任务从Tool Creation到Tool Usage的完整过程
    """
    session_id: str
    task_description: str

    # Agent记录
    tool_creator_actions: List[AgentAction] = field(default_factory=list)
    tool_user_actions: List[AgentAction] = field(default_factory=list)

    # 工具和计划
    designed_tools: List[Tool] = field(default_factory=list)
    execution_plan: Optional[AgentPlan] = None

    # 最终结果
    final_result: Any = None
    success: bool = False

    # 统计
    total_tokens: int = 0
    total_cost: float = 0.0
    total_duration_ms: float = 0.0

    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "task_description": self.task_description,
            "tool_creator_actions": [a.to_dict() for a in self.tool_creator_actions],
            "tool_user_actions": [a.to_dict() for a in self.tool_user_actions],
            "designed_tools": [t.to_dict() for t in self.designed_tools],
            "execution_plan": self.execution_plan.to_dict() if self.execution_plan else None,
            "final_result": self.final_result,
            "success": self.success,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "total_duration_ms": self.total_duration_ms,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }
