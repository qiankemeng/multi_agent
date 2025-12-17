"""
MVP实验变量定义
定义最小可行实验所需的所有数据变量

实验目标：验证多Agent系统（工具创建Agent + 工具使用Agent）的可行性

实验场景：文本处理任务
- 工具使用Agent请求创建文本处理工具
- 工具创建Agent动态生成工具
- 工具使用Agent使用工具处理数据
- 验证完整的交互流程

设计原则：
1. 变量定义简单清晰
2. 易于修改和扩展
3. 所有实验数据都在此定义
4. 修改只需更新此文件或对应的MD文档
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


# ==================== 枚举定义 ====================

class ToolType(Enum):
    """工具类型"""
    STRING_TRANSFORM = "string_transform"    # 字符串转换
    TEXT_ANALYSIS = "text_analysis"          # 文本分析
    DATA_VALIDATION = "data_validation"      # 数据验证
    CUSTOM = "custom"                        # 自定义


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"        # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"          # 失败


class ExperimentPhase(Enum):
    """实验阶段"""
    INITIALIZATION = "initialization"      # 初始化
    TOOL_REQUEST = "tool_request"         # 工具请求
    TOOL_CREATION = "tool_creation"       # 工具创建
    TOOL_EXECUTION = "tool_execution"     # 工具执行
    RESULT_VALIDATION = "result_validation"  # 结果验证
    COMPLETED = "completed"                # 完成


# ==================== 实验数据变量 ====================

@dataclass
class ToolCreationRequest:
    """
    工具创建请求
    工具使用Agent发送给工具创建Agent的请求
    """
    request_id: str                        # 请求唯一标识
    tool_type: ToolType                    # 要创建的工具类型
    tool_name: str                         # 工具名称
    description: str                       # 工具描述

    # 工具需求规格
    requirements: Dict[str, Any]           # 功能需求
    input_spec: Dict[str, str]             # 输入参数规格
    output_spec: Dict[str, str]            # 输出规格

    # 元数据
    requester_id: str = ""                 # 请求者Agent ID
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    priority: int = 2                      # 优先级 1-5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "tool_type": self.tool_type.value,
            "tool_name": self.tool_name,
            "description": self.description,
            "requirements": self.requirements,
            "input_spec": self.input_spec,
            "output_spec": self.output_spec,
            "requester_id": self.requester_id
        }


@dataclass
class CreatedTool:
    """
    创建的工具
    工具创建Agent创建的工具实例
    """
    tool_id: str                           # 工具唯一标识
    request_id: str                        # 对应的请求ID
    tool_name: str                         # 工具名称
    tool_type: ToolType                    # 工具类型

    # 工具实现
    implementation_code: str               # 实现代码（字符串形式）

    # 工具规格
    input_parameters: Dict[str, str]       # 输入参数定义
    output_format: Dict[str, str]          # 输出格式定义

    # 以下字段有默认值
    implementation_function: Optional[Any] = None  # 实现函数（可调用对象）

    # 元数据
    creator_id: str = ""                   # 创建者Agent ID
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0.0"                 # 版本号
    test_cases: List[Dict[str, Any]] = field(default_factory=list)  # 测试用例

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "request_id": self.request_id,
            "tool_name": self.tool_name,
            "tool_type": self.tool_type.value,
            "input_parameters": self.input_parameters,
            "output_format": self.output_format,
            "creator_id": self.creator_id,
            "created_at": self.created_at,
            "version": self.version
        }


@dataclass
class TaskData:
    """
    任务数据
    需要使用工具处理的输入数据
    """
    task_id: str                           # 任务唯一标识
    data_type: str                         # 数据类型（text, number, json等）
    input_data: Any                        # 输入数据

    # 任务配置
    tool_name: str = ""                    # 要使用的工具名称
    parameters: Dict[str, Any] = field(default_factory=dict)  # 额外参数

    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    source: str = ""                       # 数据来源
    description: str = ""                  # 任务描述
    expected_output: Optional[Any] = None  # 期望输出（用于验证）

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "data_type": self.data_type,
            "input_data": self.input_data,
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "description": self.description
        }


@dataclass
class TaskExecution:
    """
    任务执行记录
    记录工具执行任务的过程和结果
    """
    execution_id: str                      # 执行唯一标识
    task_id: str                           # 关联的任务ID
    tool_id: str                           # 使用的工具ID
    tool_name: str                         # 工具名称

    # 执行状态
    status: TaskStatus                     # 执行状态
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None         # 结束时间
    duration_ms: Optional[float] = None    # 执行时长（毫秒）

    # 执行结果
    output_data: Optional[Any] = None      # 输出数据
    error_message: Optional[str] = None    # 错误信息

    # 执行元数据
    executor_id: str = ""                  # 执行者Agent ID
    retry_count: int = 0                   # 重试次数

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "task_id": self.task_id,
            "tool_id": self.tool_id,
            "tool_name": self.tool_name,
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "output_data": self.output_data,
            "error_message": self.error_message
        }


@dataclass
class ExperimentRun:
    """
    实验运行记录
    记录一次完整的MVP实验运行
    """
    run_id: str                            # 运行唯一标识
    experiment_name: str                   # 实验名称

    # 时间信息
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None         # 结束时间
    total_duration_ms: Optional[float] = None  # 总时长

    # 实验阶段
    current_phase: ExperimentPhase = ExperimentPhase.INITIALIZATION
    phases_completed: List[str] = field(default_factory=list)  # 已完成的阶段

    # 参与者
    agents: Dict[str, str] = field(default_factory=dict)  # agent_id -> agent_name

    # 实验数据
    tool_requests: List[str] = field(default_factory=list)      # 请求ID列表
    created_tools: List[str] = field(default_factory=list)      # 创建的工具ID列表
    tasks: List[str] = field(default_factory=list)              # 任务ID列表
    executions: List[str] = field(default_factory=list)         # 执行ID列表

    # 实验结果
    success: bool = False                  # 实验是否成功
    total_tasks: int = 0                   # 总任务数
    successful_tasks: int = 0              # 成功任务数
    failed_tasks: int = 0                  # 失败任务数

    # 性能指标
    metrics: Dict[str, Any] = field(default_factory=dict)  # 性能指标

    # 元数据
    description: str = ""                  # 实验描述
    notes: List[str] = field(default_factory=list)  # 备注

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "experiment_name": self.experiment_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "current_phase": self.current_phase.value,
            "phases_completed": self.phases_completed,
            "agents": self.agents,
            "success": self.success,
            "total_tasks": self.total_tasks,
            "successful_tasks": self.successful_tasks,
            "failed_tasks": self.failed_tasks,
            "metrics": self.metrics
        }


@dataclass
class ValidationResult:
    """
    验证结果
    验证实验结果是否符合预期
    """
    validation_id: str                     # 验证唯一标识
    execution_id: str                      # 关联的执行ID

    # 验证状态
    passed: bool                           # 是否通过验证

    # 验证详情
    expected_output: Any                   # 期望输出
    actual_output: Any                     # 实际输出
    match_score: float = 0.0               # 匹配分数 0.0-1.0

    # 差异信息
    differences: List[str] = field(default_factory=list)  # 差异列表

    # 元数据
    validated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    validator_id: str = ""                 # 验证者ID

    def to_dict(self) -> Dict[str, Any]:
        return {
            "validation_id": self.validation_id,
            "execution_id": self.execution_id,
            "passed": self.passed,
            "match_score": self.match_score,
            "differences": self.differences,
            "validated_at": self.validated_at
        }


# ==================== 实验配置常量 ====================

class ExperimentConfig:
    """实验配置常量"""

    # 默认实验参数
    DEFAULT_TIMEOUT_SECONDS = 30
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_BATCH_SIZE = 10

    # 工具创建参数
    TOOL_CREATION_TIMEOUT = 10
    MAX_TOOL_COMPLEXITY = 5  # 1-5，工具复杂度限制

    # 任务执行参数
    TASK_EXECUTION_TIMEOUT = 5
    MAX_CONCURRENT_TASKS = 5

    # 验证参数
    VALIDATION_THRESHOLD = 0.95  # 验证通过阈值

    # 日志配置
    ENABLE_DETAILED_LOGGING = True
    LOG_LEVEL = "INFO"


# ==================== 预定义实验场景 ====================

class MVPScenarios:
    """MVP实验场景定义"""

    @staticmethod
    def get_string_reverser_scenario() -> Dict[str, Any]:
        """场景1: 字符串反转工具"""
        return {
            "name": "string_reverser",
            "description": "创建并使用字符串反转工具",
            "tool_request": {
                "tool_type": ToolType.STRING_TRANSFORM,
                "tool_name": "string_reverser",
                "description": "反转输入的字符串",
                "requirements": {
                    "function": "reverse_string",
                    "complexity": "simple"
                },
                "input_spec": {
                    "text": "string"
                },
                "output_spec": {
                    "reversed_text": "string"
                }
            },
            "test_data": [
                {"input": "Hello", "expected": "olleH"},
                {"input": "World", "expected": "dlroW"},
                {"input": "12345", "expected": "54321"}
            ]
        }

    @staticmethod
    def get_uppercase_converter_scenario() -> Dict[str, Any]:
        """场景2: 大写转换工具"""
        return {
            "name": "uppercase_converter",
            "description": "创建并使用大写转换工具",
            "tool_request": {
                "tool_type": ToolType.STRING_TRANSFORM,
                "tool_name": "uppercase_converter",
                "description": "将输入字符串转换为大写",
                "requirements": {
                    "function": "to_uppercase",
                    "complexity": "simple"
                },
                "input_spec": {
                    "text": "string"
                },
                "output_spec": {
                    "uppercase_text": "string"
                }
            },
            "test_data": [
                {"input": "hello", "expected": "HELLO"},
                {"input": "world", "expected": "WORLD"},
                {"input": "Test123", "expected": "TEST123"}
            ]
        }

    @staticmethod
    def get_word_counter_scenario() -> Dict[str, Any]:
        """场景3: 单词计数工具"""
        return {
            "name": "word_counter",
            "description": "创建并使用单词计数工具",
            "tool_request": {
                "tool_type": ToolType.TEXT_ANALYSIS,
                "tool_name": "word_counter",
                "description": "统计输入文本的单词数量",
                "requirements": {
                    "function": "count_words",
                    "complexity": "medium"
                },
                "input_spec": {
                    "text": "string"
                },
                "output_spec": {
                    "word_count": "integer"
                }
            },
            "test_data": [
                {"input": "Hello World", "expected": 2},
                {"input": "This is a test", "expected": 4},
                {"input": "One", "expected": 1}
            ]
        }


# ==================== 导出 ====================

__all__ = [
    # 枚举
    'ToolType',
    'TaskStatus',
    'ExperimentPhase',

    # 数据类
    'ToolCreationRequest',
    'CreatedTool',
    'TaskData',
    'TaskExecution',
    'ExperimentRun',
    'ValidationResult',

    # 配置
    'ExperimentConfig',
    'MVPScenarios'
]
