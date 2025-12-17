"""
配置模块
提供项目所有配置的统一入口
"""

# 全局配置
from .settings import (
    Settings,
    settings,
    get_settings,
    reload_settings,
    OpenAIConfig,
    ClaudeConfig,
    GeminiConfig,
    MLLMConfig,
    CostConfig,
    AgentConfig,
    VideoConfig,
    PathConfig,
    LogConfig,
    ExperimentConfig,
    PerformanceConfig,
    DevConfig,
    PROJECT_ROOT
)

# 工具配置
from .tool_config import (
    ToolConfig,
    ToolParameter,
    ToolCategory,
    ParameterType,
    ToolStatus,
    ToolExecutionConfig,
    TOOL_REGISTRY,
    register_tool,
    get_tool_config,
    list_all_tools,
    ToolDefaults
)

# 交互配置
from .interaction_config import (
    # 枚举
    MessageType,
    AgentRole,
    AgentStatus,
    ExecutionStatus,
    Priority,

    # 核心数据结构
    Message,
    ToolCallRequest,
    ToolCallResponse,
    Context,
    AgentState,
    InteractionConfig,

    # 协议常量
    InteractionProtocol,
    DEFAULT_INTERACTION_CONFIG
)

__all__ = [
    # 全局配置
    'Settings',
    'settings',
    'get_settings',
    'reload_settings',
    'OpenAIConfig',
    'ClaudeConfig',
    'GeminiConfig',
    'MLLMConfig',
    'CostConfig',
    'AgentConfig',
    'VideoConfig',
    'PathConfig',
    'LogConfig',
    'ExperimentConfig',
    'PerformanceConfig',
    'DevConfig',
    'PROJECT_ROOT',

    # 工具配置
    'ToolConfig',
    'ToolParameter',
    'ToolCategory',
    'ParameterType',
    'ToolStatus',
    'ToolExecutionConfig',
    'TOOL_REGISTRY',
    'register_tool',
    'get_tool_config',
    'list_all_tools',
    'ToolDefaults',

    # 交互配置 - 枚举
    'MessageType',
    'AgentRole',
    'AgentStatus',
    'ExecutionStatus',
    'Priority',

    # 交互配置 - 核心数据结构
    'Message',
    'ToolCallRequest',
    'ToolCallResponse',
    'Context',
    'AgentState',
    'InteractionConfig',

    # 交互配置 - 协议
    'InteractionProtocol',
    'DEFAULT_INTERACTION_CONFIG'
]
