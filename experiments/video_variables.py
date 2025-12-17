"""
长视频理解MVP实验变量定义
定义长视频理解任务所需的所有数据变量

实验目标：验证多Agent系统在长视频理解任务中的可行性

实验场景：长视频理解流程
- 工具使用Agent请求创建视频处理工具
- 工具创建Agent动态生成视频分析工具
- 工具使用Agent使用工具处理视频数据
- Agent通过MLLM API理解视频内容
- 验证完整的理解流程

设计原则：
1. 变量定义贴近视频处理领域
2. 支持MLLM API调用
3. 易于修改和扩展
4. 完整的追溯能力
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import uuid


# ==================== 枚举定义 ====================

class VideoFormat(Enum):
    """视频格式"""
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"


class SegmentationStrategy(Enum):
    """分段策略"""
    FIXED_DURATION = "fixed_duration"      # 固定时长分段
    SCENE_CHANGE = "scene_change"          # 场景变化分段
    SHOT_BOUNDARY = "shot_boundary"        # 镜头边界分段
    CUSTOM = "custom"                      # 自定义分段


class FrameSamplingMethod(Enum):
    """帧采样方法"""
    UNIFORM = "uniform"                    # 均匀采样
    KEY_FRAME = "key_frame"                # 关键帧采样
    ADAPTIVE = "adaptive"                  # 自适应采样


class AnalysisTask(Enum):
    """分析任务类型"""
    CAPTION = "caption"                    # 生成描述
    QA = "question_answering"              # 问答
    OBJECT_DETECTION = "object_detection"  # 目标检测
    ACTION_RECOGNITION = "action_recognition"  # 动作识别
    SCENE_UNDERSTANDING = "scene_understanding"  # 场景理解


class ProcessingStatus(Enum):
    """处理状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


# ==================== 基础视频变量 ====================

@dataclass
class VideoMeta:
    """
    视频元数据
    描述视频的基本信息
    """
    video_id: str                          # 视频唯一标识
    file_path: str                         # 视频文件路径

    # 视频基本属性
    duration_sec: float                    # 视频时长（秒）
    fps: float                             # 帧率
    num_frames: int                        # 总帧数
    width: int                             # 视频宽度
    height: int                            # 视频高度
    format: VideoFormat = VideoFormat.MP4  # 视频格式

    # 音频信息（可选）
    has_audio: bool = True                 # 是否包含音频
    audio_channels: Optional[int] = None   # 音频声道数
    audio_sample_rate: Optional[int] = None  # 音频采样率

    # 元数据
    file_size_mb: Optional[float] = None   # 文件大小（MB）
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    source: str = ""                       # 视频来源
    description: str = ""                  # 视频描述
    tags: List[str] = field(default_factory=list)  # 标签

    def to_dict(self) -> Dict[str, Any]:
        return {
            "video_id": self.video_id,
            "file_path": self.file_path,
            "duration_sec": self.duration_sec,
            "fps": self.fps,
            "num_frames": self.num_frames,
            "width": self.width,
            "height": self.height,
            "format": self.format.value,
            "has_audio": self.has_audio
        }


@dataclass
class TimeSpan:
    """
    时间跨度
    描述视频中的一个时间段
    """
    start_sec: float                       # 开始时间（秒）
    end_sec: float                         # 结束时间（秒）

    @property
    def duration(self) -> float:
        """返回时间跨度长度"""
        return self.end_sec - self.start_sec

    def to_dict(self) -> Dict[str, float]:
        return {
            "start_sec": self.start_sec,
            "end_sec": self.end_sec,
            "duration": self.duration
        }


@dataclass
class Segment:
    """
    视频分段
    将长视频切分为多个片段便于处理
    """
    segment_id: str                        # 分段唯一标识
    video_id: str                          # 所属视频ID
    time_span: TimeSpan                    # 时间跨度

    # 分段信息
    segment_index: int                     # 分段索引（从0开始）
    total_segments: int                    # 总分段数

    # 帧信息
    start_frame: int                       # 起始帧号
    end_frame: int                         # 结束帧号
    num_frames: int                        # 该段帧数

    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    strategy: SegmentationStrategy = SegmentationStrategy.FIXED_DURATION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "video_id": self.video_id,
            "time_span": self.time_span.to_dict(),
            "segment_index": self.segment_index,
            "total_segments": self.total_segments,
            "start_frame": self.start_frame,
            "end_frame": self.end_frame,
            "num_frames": self.num_frames
        }


@dataclass
class Frame:
    """
    视频帧
    单个视频帧的信息
    """
    frame_id: str                          # 帧唯一标识
    video_id: str                          # 所属视频ID
    segment_id: Optional[str] = None       # 所属分段ID（如果有）

    # 帧信息
    frame_index: int = 0                   # 帧索引
    timestamp_sec: float = 0.0             # 时间戳（秒）

    # 帧数据（可选，避免存储大量图像数据）
    image_path: Optional[str] = None       # 帧图像文件路径
    image_base64: Optional[str] = None     # 帧图像base64编码（用于API）

    # 元数据
    width: int = 0
    height: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_id": self.frame_id,
            "video_id": self.video_id,
            "segment_id": self.segment_id,
            "frame_index": self.frame_index,
            "timestamp_sec": self.timestamp_sec,
            "has_image": self.image_path is not None or self.image_base64 is not None
        }


# ==================== 视频理解结果变量 ====================

@dataclass
class FrameCaption:
    """
    帧描述
    单个帧的文本描述
    """
    caption_id: str                        # 描述唯一标识
    frame_id: str                          # 关联的帧ID

    # 描述内容
    caption: str                           # 描述文本
    confidence: float = 1.0                # 置信度 0-1

    # 生成信息
    model_name: str = ""                   # 使用的模型名称
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    generation_time_ms: Optional[float] = None  # 生成耗时

    # 额外信息
    detected_objects: List[str] = field(default_factory=list)  # 检测到的对象
    detected_actions: List[str] = field(default_factory=list)  # 检测到的动作
    scene_type: str = ""                   # 场景类型

    def to_dict(self) -> Dict[str, Any]:
        return {
            "caption_id": self.caption_id,
            "frame_id": self.frame_id,
            "caption": self.caption,
            "confidence": self.confidence,
            "model_name": self.model_name
        }


@dataclass
class SegmentCaption:
    """
    分段描述
    视频片段的文本描述
    """
    caption_id: str                        # 描述唯一标识
    segment_id: str                        # 关联的分段ID

    # 描述内容
    caption: str                           # 分段描述文本
    summary: str = ""                      # 摘要

    # 详细信息
    key_frames: List[str] = field(default_factory=list)  # 关键帧ID列表
    frame_captions: List[str] = field(default_factory=list)  # 帧描述ID列表

    # 分析结果
    main_events: List[str] = field(default_factory=list)  # 主要事件
    key_objects: List[str] = field(default_factory=list)  # 关键对象
    key_actions: List[str] = field(default_factory=list)  # 关键动作

    # 生成信息
    model_name: str = ""                   # 使用的模型名称
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    confidence: float = 1.0                # 置信度

    def to_dict(self) -> Dict[str, Any]:
        return {
            "caption_id": self.caption_id,
            "segment_id": self.segment_id,
            "caption": self.caption,
            "summary": self.summary,
            "main_events": self.main_events,
            "key_objects": self.key_objects,
            "key_actions": self.key_actions
        }


@dataclass
class VideoUnderstanding:
    """
    完整视频理解
    整合所有片段的理解结果
    """
    understanding_id: str                  # 理解结果唯一标识
    video_id: str                          # 关联的视频ID

    # 整体描述
    overall_caption: str                   # 整体描述
    summary: str                           # 视频摘要
    title: str = ""                        # 视频标题（如果生成）

    # 结构化信息
    segment_captions: List[str] = field(default_factory=list)  # 分段描述ID列表
    timeline_events: List[Dict[str, Any]] = field(default_factory=list)  # 时间线事件

    # 分析结果
    main_topics: List[str] = field(default_factory=list)  # 主要话题
    key_entities: List[str] = field(default_factory=list)  # 关键实体
    narrative_structure: str = ""          # 叙事结构分析

    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    model_name: str = ""                   # 使用的模型
    processing_time_ms: Optional[float] = None  # 处理总耗时

    def to_dict(self) -> Dict[str, Any]:
        return {
            "understanding_id": self.understanding_id,
            "video_id": self.video_id,
            "overall_caption": self.overall_caption,
            "summary": self.summary,
            "title": self.title,
            "main_topics": self.main_topics,
            "key_entities": self.key_entities
        }


# ==================== MLLM API交互变量 ====================

@dataclass
class MLLMRequest:
    """
    MLLM API请求
    封装对多模态大语言模型的API调用
    """
    request_id: str                        # 请求唯一标识

    # 模型配置
    model_name: str                        # 模型名称 (e.g., "gpt-4-vision", "claude-3")
    api_endpoint: str                      # API端点

    # 输入内容（必需字段）
    prompt: str                            # 文本提示

    # 可选字段（有默认值）
    api_key: str = ""                      # API密钥（实际使用时从环境变量读取）
    images: List[str] = field(default_factory=list)  # 图像列表（base64或URL）
    video_frames: List[str] = field(default_factory=list)  # 视频帧列表
    system_prompt: str = ""                # 系统提示（可选）

    # 请求参数
    temperature: float = 0.7               # 温度参数
    max_tokens: int = 1000                 # 最大token数
    top_p: float = 1.0                     # top_p采样

    # 任务类型
    task: AnalysisTask = AnalysisTask.CAPTION

    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    timeout_seconds: int = 60              # 超时时间
    retry_count: int = 0                   # 重试次数

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "model_name": self.model_name,
            "prompt": self.prompt,
            "num_images": len(self.images),
            "num_frames": len(self.video_frames),
            "task": self.task.value,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }


@dataclass
class MLLMResponse:
    """
    MLLM API响应
    模型返回的结果
    """
    response_id: str                       # 响应唯一标识
    request_id: str                        # 对应的请求ID

    # 响应内容
    text: str                              # 文本响应
    confidence: float = 1.0                # 置信度

    # 响应状态
    success: bool = True                   # 是否成功
    error_message: str = ""                # 错误信息

    # 使用情况
    prompt_tokens: int = 0                 # 提示token数
    completion_tokens: int = 0             # 完成token数
    total_tokens: int = 0                  # 总token数
    cost_usd: float = 0.0                  # API调用成本（美元）

    # 时间信息
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    response_time_ms: Optional[float] = None  # 响应时间
    timestamp: float = 0.0                 # Unix时间戳

    # 元数据
    model_name: str = ""                   # 实际使用的模型
    finish_reason: str = ""                # 完成原因 (e.g., "stop", "length")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "response_id": self.response_id,
            "request_id": self.request_id,
            "text": self.text[:100] + "..." if len(self.text) > 100 else self.text,
            "success": self.success,
            "total_tokens": self.total_tokens,
            "cost_usd": self.cost_usd,
            "response_time_ms": self.response_time_ms
        }


# ==================== 原子操作定义 ====================

@dataclass
class AtomicOperation:
    """
    原子操作
    定义视频处理的基本操作单元
    """
    operation_id: str                      # 操作唯一标识
    operation_name: str                    # 操作名称
    operation_type: str                    # 操作类型

    # 输入输出
    input_spec: Dict[str, str]             # 输入规格
    output_spec: Dict[str, str]            # 输出规格

    # 操作参数
    parameters: Dict[str, Any] = field(default_factory=dict)

    # 执行状态
    status: ProcessingStatus = ProcessingStatus.PENDING
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_ms: Optional[float] = None

    # 执行结果
    result: Optional[Any] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation_id": self.operation_id,
            "operation_name": self.operation_name,
            "operation_type": self.operation_type,
            "status": self.status.value,
            "duration_ms": self.duration_ms
        }


# ==================== 预定义原子操作类型 ====================

class AtomicOperations:
    """预定义的原子操作类型"""

    # 视频预处理操作
    EXTRACT_METADATA = "extract_metadata"        # 提取视频元数据
    SEGMENT_VIDEO = "segment_video"              # 视频分段
    EXTRACT_FRAMES = "extract_frames"            # 提取帧
    SAMPLE_FRAMES = "sample_frames"              # 帧采样

    # 视频分析操作
    ANALYZE_FRAME = "analyze_frame"              # 分析单帧
    ANALYZE_SEGMENT = "analyze_segment"          # 分析片段
    DETECT_OBJECTS = "detect_objects"            # 目标检测
    RECOGNIZE_ACTIONS = "recognize_actions"      # 动作识别
    DETECT_SCENES = "detect_scenes"              # 场景检测

    # 描述生成操作
    GENERATE_FRAME_CAPTION = "generate_frame_caption"      # 生成帧描述
    GENERATE_SEGMENT_CAPTION = "generate_segment_caption"  # 生成片段描述
    MERGE_CAPTIONS = "merge_captions"                      # 合并描述
    GENERATE_SUMMARY = "generate_summary"                  # 生成摘要

    # MLLM交互操作
    CALL_MLLM_API = "call_mllm_api"              # 调用MLLM API
    PARSE_MLLM_RESPONSE = "parse_mllm_response"  # 解析MLLM响应
    BUILD_PROMPT = "build_prompt"                # 构建提示词


# ==================== 实验运行记录 ====================

@dataclass
class VideoExperimentRun:
    """
    视频理解实验运行记录
    记录一次完整的长视频理解实验
    """
    run_id: str                            # 运行唯一标识
    experiment_name: str                   # 实验名称

    # 视频信息
    video_meta: Optional[VideoMeta] = None

    # 处理过程
    segments: List[str] = field(default_factory=list)  # 分段ID列表
    frames: List[str] = field(default_factory=list)    # 提取的帧ID列表
    operations: List[str] = field(default_factory=list)  # 执行的操作ID列表

    # MLLM调用记录
    mllm_requests: List[str] = field(default_factory=list)  # 请求ID列表
    mllm_responses: List[str] = field(default_factory=list)  # 响应ID列表

    # 理解结果
    frame_captions: List[str] = field(default_factory=list)  # 帧描述ID列表
    segment_captions: List[str] = field(default_factory=list)  # 分段描述ID列表
    video_understanding: Optional[str] = None  # 最终理解结果ID

    # 实验状态
    status: ProcessingStatus = ProcessingStatus.PENDING
    current_stage: str = "initialization"

    # 时间信息
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None
    total_duration_ms: Optional[float] = None

    # 统计信息
    total_api_calls: int = 0               # API调用总次数
    total_tokens_used: int = 0             # 使用token总数
    total_cost_usd: float = 0.0            # 总成本（美元）

    # 元数据
    description: str = ""
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "experiment_name": self.experiment_name,
            "video_id": self.video_meta.video_id if self.video_meta else None,
            "status": self.status.value,
            "current_stage": self.current_stage,
            "total_segments": len(self.segments),
            "total_frames": len(self.frames),
            "total_api_calls": self.total_api_calls,
            "total_tokens_used": self.total_tokens_used,
            "total_cost_usd": self.total_cost_usd
        }


# ==================== 导出 ====================

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
