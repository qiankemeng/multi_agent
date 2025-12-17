"""
交互配置模块
定义多智能体系统中Agent之间、工具之间交互所需的所有变量和数据结构

这是整个系统的核心，定义了：
1. 消息传递格式
2. 工具调用请求/响应
3. 上下文管理
4. Agent状态
5. 交互协议
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from datetime import datetime
import uuid


# ==================== 枚举定义 ====================

class MessageType(Enum):
    """消息类型"""
    REQUEST = "request"              # 请求消息
    RESPONSE = "response"            # 响应消息
    NOTIFICATION = "notification"    # 通知消息
    COMMAND = "command"              # 命令消息
    EVENT = "event"                  # 事件消息
    ERROR = "error"                  # 错误消息


class AgentRole(Enum):
    """Agent角色"""
    TOOL_CREATOR = "tool_creator"    # 工具创建者
    TOOL_USER = "tool_user"          # 工具使用者
    COORDINATOR = "coordinator"      # 协调者
    MONITOR = "monitor"              # 监控者


class AgentStatus(Enum):
    """Agent状态"""
    IDLE = "idle"                    # 空闲
    BUSY = "busy"                    # 忙碌
    WAITING = "waiting"              # 等待
    ERROR = "error"                  # 错误状态
    OFFLINE = "offline"              # 离线


class ExecutionStatus(Enum):
    """执行状态"""
    PENDING = "pending"              # 待执行
    RUNNING = "running"              # 执行中
    SUCCESS = "success"              # 成功
    FAILED = "failed"                # 失败
    TIMEOUT = "timeout"              # 超时
    CANCELLED = "cancelled"          # 已取消


class Priority(Enum):
    """优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


# ==================== 核心数据结构 ====================

@dataclass
class Message:
    """
    消息：Agent之间通信的基本单位

    这是整个系统中最基础的交互单元，所有Agent间的通信都通过消息进行
    """
    # 基本信息
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType = MessageType.REQUEST
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # 路由信息
    sender_id: str = ""                      # 发送者ID
    sender_role: Optional[AgentRole] = None  # 发送者角色
    receiver_id: str = ""                    # 接收者ID
    receiver_role: Optional[AgentRole] = None # 接收者角色

    # 内容
    content: Any = None                      # 消息内容（可以是任意类型）
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据

    # 关联信息
    context_id: Optional[str] = None         # 关联的上下文ID
    session_id: Optional[str] = None         # 会话ID
    parent_message_id: Optional[str] = None  # 父消息ID（用于追踪对话链）

    # 控制信息
    priority: Priority = Priority.NORMAL     # 优先级
    requires_response: bool = True           # 是否需要响应
    timeout_seconds: Optional[int] = None    # 超时时间

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "timestamp": self.timestamp,
            "sender_id": self.sender_id,
            "sender_role": self.sender_role.value if self.sender_role else None,
            "receiver_id": self.receiver_id,
            "receiver_role": self.receiver_role.value if self.receiver_role else None,
            "content": self.content,
            "metadata": self.metadata,
            "context_id": self.context_id,
            "session_id": self.session_id,
            "priority": self.priority.value
        }


@dataclass
class ToolCallRequest:
    """
    工具调用请求：当Agent需要调用工具时发送

    这是工具使用Agent向工具创建Agent发送的请求
    """
    # 请求标识
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # 工具信息
    tool_name: str = ""                      # 要调用的工具名称
    tool_version: Optional[str] = None       # 工具版本（可选）

    # 调用参数
    parameters: Dict[str, Any] = field(default_factory=dict)  # 工具参数

    # 调用者信息
    caller_id: str = ""                      # 调用者Agent ID
    caller_role: AgentRole = AgentRole.TOOL_USER

    # 上下文
    context_id: str = ""                     # 上下文ID
    session_id: Optional[str] = None         # 会话ID

    # 执行控制
    priority: Priority = Priority.NORMAL     # 优先级
    timeout_seconds: int = 30                # 超时时间（秒）
    retry_on_failure: bool = True            # 失败时是否重试
    max_retries: int = 3                     # 最大重试次数

    # 额外配置
    execution_config: Dict[str, Any] = field(default_factory=dict)  # 执行配置
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "tool_name": self.tool_name,
            "tool_version": self.tool_version,
            "parameters": self.parameters,
            "caller_id": self.caller_id,
            "caller_role": self.caller_role.value,
            "context_id": self.context_id,
            "priority": self.priority.value,
            "timeout_seconds": self.timeout_seconds
        }


@dataclass
class ToolCallResponse:
    """
    工具调用响应：工具执行后返回的结果

    这是工具创建Agent执行工具后返回给工具使用Agent的响应
    """
    # 响应标识
    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = ""                     # 对应的请求ID
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # 执行状态
    status: ExecutionStatus = ExecutionStatus.SUCCESS

    # 返回结果
    result: Any = None                       # 执行结果
    error_message: Optional[str] = None      # 错误信息
    error_type: Optional[str] = None         # 错误类型
    error_traceback: Optional[str] = None    # 错误堆栈

    # 执行信息
    execution_time_ms: Optional[float] = None  # 执行时间（毫秒）
    start_time: Optional[str] = None         # 开始时间
    end_time: Optional[str] = None           # 结束时间

    # 资源使用
    resource_usage: Dict[str, Any] = field(default_factory=dict)  # 资源使用情况

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "response_id": self.response_id,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "status": self.status.value,
            "result": self.result,
            "error_message": self.error_message,
            "execution_time_ms": self.execution_time_ms
        }

    def is_success(self) -> bool:
        """判断是否执行成功"""
        return self.status == ExecutionStatus.SUCCESS


@dataclass
class Context:
    """
    上下文：贯穿整个交互过程的上下文信息

    上下文是多Agent交互的核心，维护了整个对话/任务的状态和历史
    """
    # 标识
    context_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # 历史记录
    message_history: List[Message] = field(default_factory=list)  # 消息历史
    tool_call_history: List[Dict[str, Any]] = field(default_factory=list)  # 工具调用历史

    # 共享状态
    shared_state: Dict[str, Any] = field(default_factory=dict)  # Agent之间共享的状态
    variables: Dict[str, Any] = field(default_factory=dict)     # 上下文变量

    # 参与者
    participants: List[str] = field(default_factory=list)  # 参与的Agent ID列表

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)  # 标签，便于分类和搜索

    # 配置
    max_history_length: int = 100            # 最大历史记录长度
    enable_compression: bool = True          # 是否启用历史压缩

    def add_message(self, message: Message) -> None:
        """添加消息到历史"""
        self.message_history.append(message)
        self.updated_at = datetime.now().isoformat()

        # 自动清理历史（如果超过最大长度）
        if len(self.message_history) > self.max_history_length:
            self.message_history = self.message_history[-self.max_history_length:]

    def add_tool_call(self, request: ToolCallRequest, response: ToolCallResponse) -> None:
        """添加工具调用记录"""
        self.tool_call_history.append({
            "request": request.to_dict(),
            "response": response.to_dict()
        })
        self.updated_at = datetime.now().isoformat()

    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """获取最近的N条消息"""
        return self.message_history[-count:]

    def update_state(self, key: str, value: Any) -> None:
        """更新共享状态"""
        self.shared_state[key] = value
        self.updated_at = datetime.now().isoformat()

    def get_state(self, key: str, default: Any = None) -> Any:
        """获取共享状态"""
        return self.shared_state.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "context_id": self.context_id,
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "message_count": len(self.message_history),
            "tool_call_count": len(self.tool_call_history),
            "participants": self.participants,
            "shared_state": self.shared_state,
            "variables": self.variables
        }


@dataclass
class AgentState:
    """
    Agent状态：描述Agent的当前状态

    用于追踪和管理每个Agent的运行状态
    """
    # 基本信息
    agent_id: str = ""
    agent_name: str = ""
    agent_role: AgentRole = AgentRole.TOOL_USER

    # 状态信息
    status: AgentStatus = AgentStatus.IDLE
    status_message: str = ""

    # 当前任务
    current_task_id: Optional[str] = None
    current_task_description: str = ""

    # 工作队列
    pending_tasks: List[Dict[str, Any]] = field(default_factory=list)

    # 时间信息
    last_active_time: str = field(default_factory=lambda: datetime.now().isoformat())
    uptime_seconds: float = 0.0

    # 性能指标
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    average_task_duration_ms: float = 0.0

    # 资源使用
    resource_usage: Dict[str, Any] = field(default_factory=dict)

    # 能力
    capabilities: List[str] = field(default_factory=list)  # Agent的能力列表
    available_tools: List[str] = field(default_factory=list)  # 可用的工具列表

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)

    def update_status(self, status: AgentStatus, message: str = "") -> None:
        """更新状态"""
        self.status = status
        self.status_message = message
        self.last_active_time = datetime.now().isoformat()

    def is_available(self) -> bool:
        """判断Agent是否可用"""
        return self.status in [AgentStatus.IDLE, AgentStatus.WAITING]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_role": self.agent_role.value,
            "status": self.status.value,
            "status_message": self.status_message,
            "current_task_id": self.current_task_id,
            "total_tasks_completed": self.total_tasks_completed,
            "capabilities": self.capabilities,
            "available_tools": self.available_tools
        }


@dataclass
class InteractionConfig:
    """
    交互配置：定义Agent之间交互的规则和参数

    这是系统级别的配置，控制整个多Agent系统的交互行为
    """
    # 消息配置
    message_queue_size: int = 1000           # 消息队列大小
    message_timeout_seconds: int = 60        # 消息默认超时时间
    enable_message_persistence: bool = True  # 是否持久化消息

    # 重试配置
    default_max_retries: int = 3             # 默认最大重试次数
    retry_delay_seconds: float = 1.0         # 重试延迟
    exponential_backoff: bool = True         # 是否使用指数退避

    # 超时配置
    tool_call_timeout_seconds: int = 30      # 工具调用默认超时
    agent_response_timeout_seconds: int = 60 # Agent响应超时
    context_idle_timeout_seconds: int = 3600 # 上下文空闲超时（1小时）

    # 上下文管理
    max_context_history: int = 100           # 最大上下文历史长度
    context_compression_threshold: int = 80  # 上下文压缩阈值
    enable_context_cleanup: bool = True      # 是否自动清理过期上下文

    # 并发控制
    max_concurrent_tool_calls: int = 10      # 最大并发工具调用数
    max_concurrent_agents: int = 5           # 最大并发Agent数

    # 路由配置
    enable_load_balancing: bool = True       # 是否启用负载均衡
    routing_strategy: str = "round_robin"    # 路由策略

    # 监控和日志
    enable_detailed_logging: bool = True     # 是否启用详细日志
    log_message_content: bool = False        # 是否记录消息内容（可能包含敏感信息）
    enable_performance_monitoring: bool = True  # 是否启用性能监控

    # 安全配置
    enable_message_validation: bool = True   # 是否启用消息验证
    enable_authentication: bool = False      # 是否启用认证
    enable_encryption: bool = False          # 是否启用加密

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "message_queue_size": self.message_queue_size,
            "message_timeout_seconds": self.message_timeout_seconds,
            "default_max_retries": self.default_max_retries,
            "tool_call_timeout_seconds": self.tool_call_timeout_seconds,
            "max_context_history": self.max_context_history,
            "max_concurrent_tool_calls": self.max_concurrent_tool_calls,
            "routing_strategy": self.routing_strategy
        }


# ==================== 交互协议常量 ====================

class InteractionProtocol:
    """交互协议常量定义"""

    # 消息头标准字段
    HEADER_MESSAGE_ID = "message_id"
    HEADER_SENDER_ID = "sender_id"
    HEADER_RECEIVER_ID = "receiver_id"
    HEADER_TIMESTAMP = "timestamp"
    HEADER_CONTEXT_ID = "context_id"

    # 工具调用协议
    TOOL_CALL_REQUEST_TYPE = "tool_call_request"
    TOOL_CALL_RESPONSE_TYPE = "tool_call_response"
    TOOL_CREATE_REQUEST_TYPE = "tool_create_request"
    TOOL_CREATE_RESPONSE_TYPE = "tool_create_response"

    # 控制命令
    CMD_START = "start"
    CMD_STOP = "stop"
    CMD_PAUSE = "pause"
    CMD_RESUME = "resume"
    CMD_RESET = "reset"

    # 事件类型
    EVENT_AGENT_READY = "agent_ready"
    EVENT_AGENT_BUSY = "agent_busy"
    EVENT_AGENT_ERROR = "agent_error"
    EVENT_TOOL_CREATED = "tool_created"
    EVENT_TOOL_EXECUTED = "tool_executed"

    # 错误代码
    ERROR_INVALID_REQUEST = "INVALID_REQUEST"
    ERROR_TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    ERROR_TIMEOUT = "TIMEOUT"
    ERROR_EXECUTION_FAILED = "EXECUTION_FAILED"
    ERROR_INVALID_PARAMETERS = "INVALID_PARAMETERS"


# ==================== 全局默认配置 ====================

DEFAULT_INTERACTION_CONFIG = InteractionConfig()


# ==================== 导出 ====================

__all__ = [
    # 枚举
    'MessageType',
    'AgentRole',
    'AgentStatus',
    'ExecutionStatus',
    'Priority',

    # 核心数据结构
    'Message',
    'ToolCallRequest',
    'ToolCallResponse',
    'Context',
    'AgentState',
    'InteractionConfig',

    # 协议常量
    'InteractionProtocol',
    'DEFAULT_INTERACTION_CONFIG'
]
