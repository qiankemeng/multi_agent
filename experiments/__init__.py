"""
实验模块
提供长视频理解实验所需的所有变量定义
"""

from .video_variables import (
    # 枚举
    VideoFormat,
    SegmentationStrategy,
    FrameSamplingMethod,
    AnalysisTask,
    ProcessingStatus,

    # 基础视频变量
    VideoMeta,
    TimeSpan,
    Segment,
    Frame,

    # 视频理解结果
    FrameCaption,
    SegmentCaption,
    VideoUnderstanding,

    # MLLM API交互
    MLLMRequest,
    MLLMResponse,

    # 原子操作
    AtomicOperation,
    AtomicOperations,

    # 实验运行
    VideoExperimentRun
)

__all__ = [
    # 枚举
    'VideoFormat',
    'SegmentationStrategy',
    'FrameSamplingMethod',
    'AnalysisTask',
    'ProcessingStatus',

    # 基础视频变量
    'VideoMeta',
    'TimeSpan',
    'Segment',
    'Frame',

    # 视频理解结果
    'FrameCaption',
    'SegmentCaption',
    'VideoUnderstanding',

    # MLLM API交互
    'MLLMRequest',
    'MLLMResponse',

    # 原子操作
    'AtomicOperation',
    'AtomicOperations',

    # 实验运行
    'VideoExperimentRun'
]
