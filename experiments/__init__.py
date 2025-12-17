"""
MVP实验模块
提供最小可行实验所需的所有变量定义
"""

from .mvp_variables import (
    # 枚举
    ToolType,
    TaskStatus,
    ExperimentPhase,

    # 数据类
    ToolCreationRequest,
    CreatedTool,
    TaskData,
    TaskExecution,
    ExperimentRun,
    ValidationResult,

    # 配置
    ExperimentConfig,
    MVPScenarios
)

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
