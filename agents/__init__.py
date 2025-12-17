"""
Agents模块

提供多Agent系统的核心组件：
- MLLMClient: MLLM API调用封装
- ToolCreatorAgent: 工具创建Agent（通过MLLM生成工具代码）
- ToolUserAgent: 工具使用Agent（通过MLLM分析视频内容）
"""

from .mllm_client import (
    MLLMClient,
    MLLMClientConfig,
    create_client
)

from .tool_creator_agent import (
    ToolCreatorAgent,
    ToolCreationRequest,
    ToolCreationResult
)

from .tool_user_agent import (
    ToolUserAgent,
    VideoAnalysisRequest,
    VideoAnalysisResult
)

__all__ = [
    # MLLM Client
    'MLLMClient',
    'MLLMClientConfig',
    'create_client',

    # Tool Creator Agent
    'ToolCreatorAgent',
    'ToolCreationRequest',
    'ToolCreationResult',

    # Tool User Agent
    'ToolUserAgent',
    'VideoAnalysisRequest',
    'VideoAnalysisResult',
]
