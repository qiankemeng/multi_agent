"""
Multi-Agent System Core Data Structures
多Agent系统核心数据结构

功能说明:
---------
本模块定义了多Agent系统的所有核心数据结构，包括：
1. Tool - 工具定义（包含prompt模板、参数、原子操作）
2. AgentAction - Agent行动记录
3. AgentPlan - 执行计划（包含步骤和依赖关系）
4. MultiAgentSession - 完整会话记录

这些数据结构是整个系统的基础，确保了：
- Agent之间的数据传递标准化
- 完整的可追溯性（所有action都被记录）
- 成本和性能的精确统计

独立测试:
---------
直接运行本文件可以测试所有数据结构的创建和序列化：

    python agents/multi_agent_system/types.py

测试样例:
---------
# 创建一个工具定义
tool = Tool(
    tool_id="tool_001",
    tool_name="analyze_video",
    description="Analyze video content",
    purpose="Extract key information from video frames",
    prompt_template="Analyze the following frames: {frames}",
    system_prompt="You are a video analysis expert.",
    parameters={
        "frames": ToolParameter(
            name="frames",
            type="List[Frame]",
            description="Video frames to analyze"
        )
    },
    atomic_operations=["SAMPLE", "CALL_MODEL"]
)

# 创建执行计划
plan = AgentPlan(
    plan_id="plan_001",
    task_description="Analyze video and answer question",
    steps=[
        PlanStep(
            step_id="step_1",
            tool_name="analyze_video",
            tool_id="tool_001",
            inputs={"video_path": "test.mp4"},
            expected_output="Video analysis result"
        )
    ],
    reasoning="First analyze video, then answer question"
)

print(f"Tool: {tool.tool_name}")
print(f"Plan steps: {len(plan.steps)}")
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

# ==================== 独立测试代码 ====================

if __name__ == "__main__":
    print("=" * 70)
    print(" 测试 Multi-Agent System Data Structures ".center(70, "="))
    print("=" * 70)
    print()
    
    # Test 1: ToolParameter
    print("Test 1: Creating ToolParameter...")
    param = ToolParameter(
        name="video_path",
        type="str",
        description="Path to video file",
        required=True
    )
    print(f"  ✓ Parameter: {param.name} ({param.type})")
    print(f"  ✓ Required: {param.required}")
    print()
    
    # Test 2: Tool
    print("Test 2: Creating Tool...")
    tool = Tool(
        tool_id="tool_001",
        tool_name="analyze_video",
        description="Analyze video content and extract key information",
        purpose="Extract key information from video frames",
        prompt_template="Analyze the following video frames: {frames}\nQuestion: {question}",
        system_prompt="You are a video analysis expert.",
        parameters={
            "frames": ToolParameter(
                name="frames",
                type="List[Frame]",
                description="Video frames to analyze"
            ),
            "question": ToolParameter(
                name="question",
                type="str",
                description="Question to answer"
            )
        },
        atomic_operations=["SAMPLE", "CALL_MODEL"],
        created_by="tool_creator_001"
    )
    print(f"  ✓ Tool ID: {tool.tool_id}")
    print(f"  ✓ Tool Name: {tool.tool_name}")
    print(f"  ✓ Parameters: {len(tool.parameters)}")
    print(f"  ✓ Atomic Operations: {', '.join(tool.atomic_operations)}")
    print()
    
    # Test 3: PlanStep
    print("Test 3: Creating PlanStep...")
    step = PlanStep(
        step_id="step_1",
        tool_name="analyze_video",
        tool_id="tool_001",
        inputs={"video_path": "test.mp4", "question": "What happens in the video?"},
        expected_output="Video analysis describing main events",
        dependencies=[]
    )
    print(f"  ✓ Step ID: {step.step_id}")
    print(f"  ✓ Tool: {step.tool_name}")
    print(f"  ✓ Dependencies: {step.dependencies if step.dependencies else 'None'}")
    print()
    
    # Test 4: AgentPlan
    print("Test 4: Creating AgentPlan...")
    plan = AgentPlan(
        plan_id="plan_001",
        task_description="Analyze video and answer question about main events",
        steps=[step],
        available_tools=[tool],
        reasoning="First analyze the video frames, then answer the question based on the analysis"
    )
    print(f"  ✓ Plan ID: {plan.plan_id}")
    print(f"  ✓ Steps: {len(plan.steps)}")
    print(f"  ✓ Available Tools: {len(plan.available_tools)}")
    print(f"  ✓ Status: {plan.status.value}")
    print()
    
    # Test 5: AgentAction
    print("Test 5: Creating AgentAction...")
    action = AgentAction(
        action_id="action_001",
        agent_id="agent_001",
        agent_type=AgentType.TOOL_USER,
        action_type=ActionType.PLAN,
        tool=tool,
        inputs={"video_path": "test.mp4"},
        outputs={"analysis": "Video shows a person walking"},
        reasoning="User requested video analysis",
        tokens_used=1500,
        cost_usd=0.03
    )
    print(f"  ✓ Action ID: {action.action_id}")
    print(f"  ✓ Agent Type: {action.agent_type.value}")
    print(f"  ✓ Action Type: {action.action_type.value}")
    print(f"  ✓ Tokens Used: {action.tokens_used}")
    print(f"  ✓ Cost: ${action.cost_usd:.4f}")
    print()
    
    # Test 6: MultiAgentSession
    print("Test 6: Creating MultiAgentSession...")
    session = MultiAgentSession(
        session_id="session_001",
        task_description="Analyze video and answer questions",
        designed_tools=[tool],
        execution_plan=plan,
        tool_creator_actions=[action],
        tool_user_actions=[action],
        success=True
    )
    print(f"  ✓ Session ID: {session.session_id}")
    print(f"  ✓ Designed Tools: {len(session.designed_tools)}")
    print(f"  ✓ Tool Creator Actions: {len(session.tool_creator_actions)}")
    print(f"  ✓ Tool User Actions: {len(session.tool_user_actions)}")
    print(f"  ✓ Success: {session.success}")
    print()
    
    # Test 7: Serialization
    print("Test 7: Testing Serialization...")
    tool_dict = tool.to_dict()
    plan_dict = plan.to_dict()
    session_dict = session.to_dict()
    print(f"  ✓ Tool serialized: {len(tool_dict)} fields")
    print(f"  ✓ Plan serialized: {len(plan_dict)} fields")
    print(f"  ✓ Session serialized: {len(session_dict)} fields")
    print()
    
    print("=" * 70)
    print(" All Tests Passed! ".center(70, "="))
    print("=" * 70)
