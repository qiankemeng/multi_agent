"""
工具使用Agent (Tool User Agent)

通过MLLM API使用工具处理视频数据
负责调用视觉模型分析视频帧，生成描述和理解结果
"""

import uuid
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

# 导入项目依赖
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    Message,
    MessageType,
    Context,
    AgentState,
    AgentStatus,
    AgentRole,
    Priority
)

from experiments import (
    MLLMRequest,
    MLLMResponse,
    AnalysisTask,
    Frame,
    Segment,
    FrameCaption,
    SegmentCaption,
    VideoMeta
)

from .mllm_client import MLLMClient, MLLMClientConfig


@dataclass
class VideoAnalysisRequest:
    """视频分析请求"""
    request_id: str
    task: AnalysisTask  # 分析任务类型

    # 输入数据（三选一）
    video_meta: Optional[VideoMeta] = None  # 整个视频
    segment: Optional[Segment] = None  # 视频片段
    frames: List[Frame] = field(default_factory=list)  # 视频帧列表

    # 分析参数
    prompt: str = ""  # 自定义提示（可选）
    context_info: str = ""  # 上下文信息（如前面片段的描述）
    max_frames: int = 10  # 最多分析多少帧

    # MLLM参数
    temperature: float = 0.7
    max_tokens: int = 1000


@dataclass
class VideoAnalysisResult:
    """视频分析结果"""
    success: bool
    request_id: str
    task: AnalysisTask

    # 结果数据
    frame_captions: List[FrameCaption] = field(default_factory=list)
    segment_caption: Optional[SegmentCaption] = None
    summary: str = ""

    # 元数据
    error_message: str = ""
    mllm_response: Optional[MLLMResponse] = None
    processing_time: float = 0.0


class ToolUserAgent:
    """
    工具使用Agent

    职责：
    1. 接收视频分析任务（帧描述、片段描述等）
    2. 构建带图像的prompt并调用MLLM API
    3. 解析返回结果生成结构化输出
    4. 管理多轮对话上下文
    """

    def __init__(
        self,
        agent_id: str,
        mllm_client: Optional[MLLMClient] = None,
        context: Optional[Context] = None
    ):
        """
        初始化工具使用Agent

        Args:
            agent_id: Agent唯一标识
            mllm_client: MLLM客户端，如果不提供则创建默认客户端（Vision模型）
            context: 上下文对象，用于消息历史和状态管理
        """
        self.agent_id = agent_id
        self.agent_name = "ToolUserAgent"

        # MLLM客户端 - 使用视觉模型
        if mllm_client is None:
            config = MLLMClientConfig(
                default_model="gpt-4-vision-preview",  # 视觉模型
                default_temperature=0.7,
                default_max_tokens=1000
            )
            self.mllm_client = MLLMClient(config)
        else:
            self.mllm_client = mllm_client

        # 上下文
        if context is None:
            self.context = Context(
                context_id=f"ctx_{agent_id}",
                message_history=[],
                tool_call_history=[],
                shared_state={},
                participants=[agent_id]
            )
        else:
            self.context = context

        # Agent状态
        self.state = AgentState(
            agent_id=agent_id,
            agent_name=self.agent_name,
            agent_role=AgentRole.TOOL_USER,
            status=AgentStatus.IDLE,
            status_message="",
            current_task_id=None,
            current_task_description=""
        )

        # 额外的能力和性能指标（不在AgentState中）
        self.capabilities = ["video_analysis", "frame_captioning", "segment_understanding"]
        self.performance_metrics = {
            "videos_analyzed": 0,
            "frames_processed": 0,
            "success_rate": 0.0,
            "avg_processing_time": 0.0
        }

        # 统计信息
        self.stats = {
            "total_requests": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "frames_processed": 0,
            "segments_processed": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }

    def analyze(self, request: VideoAnalysisRequest) -> VideoAnalysisResult:
        """
        执行视频分析

        Args:
            request: 视频分析请求

        Returns:
            VideoAnalysisResult: 分析结果
        """
        self.stats["total_requests"] += 1
        self.state.status = AgentStatus.PROCESSING
        self.state.current_task_description = f"Analyzing {request.task.value}"

        start_time = time.time()

        try:
            # 根据任务类型选择处理方法
            if request.task == AnalysisTask.CAPTION:
                if request.frames:
                    result = self._analyze_frames(request)
                elif request.segment:
                    result = self._analyze_segment(request)
                else:
                    result = VideoAnalysisResult(
                        success=False,
                        request_id=request.request_id,
                        task=request.task,
                        error_message="必须提供frames或segment"
                    )

            elif request.task == AnalysisTask.SUMMARY:
                result = self._generate_summary(request)

            elif request.task == AnalysisTask.QA:
                result = self._answer_question(request)

            else:
                result = VideoAnalysisResult(
                    success=False,
                    request_id=request.request_id,
                    task=request.task,
                    error_message=f"不支持的任务类型: {request.task}"
                )

            # 更新统计
            if result.success:
                self.stats["successful_analyses"] += 1
                if result.frame_captions:
                    self.stats["frames_processed"] += len(result.frame_captions)
                if result.segment_caption:
                    self.stats["segments_processed"] += 1
            else:
                self.stats["failed_analyses"] += 1

            if result.mllm_response:
                self.stats["total_tokens"] += result.mllm_response.total_tokens
                self.stats["total_cost"] += result.mllm_response.cost_usd

            result.processing_time = time.time() - start_time

            # 记录到上下文
            self._record_analysis(request, result)

            # 更新状态
            self.state.status = AgentStatus.IDLE
            self.state.current_task_description = ""
            self.state.last_active_time = datetime.now().isoformat()

            return result

        except Exception as e:
            self.stats["failed_analyses"] += 1
            self.state.status = AgentStatus.ERROR
            return VideoAnalysisResult(
                success=False,
                request_id=request.request_id,
                task=request.task,
                error_message=f"分析异常: {str(e)}",
                processing_time=time.time() - start_time
            )

    def _analyze_frames(self, request: VideoAnalysisRequest) -> VideoAnalysisResult:
        """
        分析视频帧

        Args:
            request: 分析请求

        Returns:
            分析结果
        """
        frame_captions = []

        # 限制帧数
        frames_to_analyze = request.frames[:request.max_frames]

        for frame in frames_to_analyze:
            # 构建prompt
            prompt = request.prompt if request.prompt else "请详细描述这一帧画面中的内容。"

            # 准备图像数据
            image_data = frame.image_base64 if frame.image_base64 else frame.image_path or ""

            if not image_data:
                continue

            # 调用MLLM
            mllm_request = MLLMRequest(
                request_id=f"mllm_{request.request_id}_{frame.frame_id}",
                model_name=self.mllm_client.config.default_model,
                api_endpoint=self.mllm_client.config.base_url,
                prompt=prompt,
                images=[image_data],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                task=request.task
            )

            mllm_response = self.mllm_client.call(mllm_request)

            if mllm_response.success:
                # 创建帧描述
                caption = FrameCaption(
                    caption_id=f"cap_{uuid.uuid4().hex[:8]}",
                    frame_id=frame.frame_id,
                    caption=mllm_response.text,
                    confidence=1.0,
                    model_name=mllm_response.model_name,
                    detected_objects=[],  # TODO: 可以从描述中提取
                    detected_actions=[],
                    scene_type=""
                )
                frame_captions.append(caption)

        if frame_captions:
            return VideoAnalysisResult(
                success=True,
                request_id=request.request_id,
                task=request.task,
                frame_captions=frame_captions,
                mllm_response=mllm_response if 'mllm_response' in locals() else None
            )
        else:
            return VideoAnalysisResult(
                success=False,
                request_id=request.request_id,
                task=request.task,
                error_message="没有可分析的帧"
            )

    def _analyze_segment(self, request: VideoAnalysisRequest) -> VideoAnalysisResult:
        """
        分析视频片段

        Args:
            request: 分析请求

        Returns:
            分析结果
        """
        if not request.segment or not request.frames:
            return VideoAnalysisResult(
                success=False,
                request_id=request.request_id,
                task=request.task,
                error_message="片段分析需要提供segment和frames"
            )

        # 准备图像数据（从frames提取）
        images = []
        for frame in request.frames[:request.max_frames]:
            image_data = frame.image_base64 if frame.image_base64 else frame.image_path or ""
            if image_data:
                images.append(image_data)

        if not images:
            return VideoAnalysisResult(
                success=False,
                request_id=request.request_id,
                task=request.task,
                error_message="没有可用的图像数据"
            )

        # 构建prompt
        base_prompt = f"""请分析这个视频片段（{request.segment.time_span.start_sec:.1f}秒 到 {request.segment.time_span.end_sec:.1f}秒）。

下面是从这个片段中采样的{len(images)}帧关键画面。

请提供：
1. 整体描述：这个片段发生了什么
2. 主要事件：按时间顺序列出主要事件
3. 关键对象：出现的重要人物、物体等
"""

        if request.context_info:
            base_prompt = f"前文背景：{request.context_info}\n\n" + base_prompt

        if request.prompt:
            base_prompt += f"\n\n特别关注：{request.prompt}"

        # 调用MLLM
        mllm_request = MLLMRequest(
            request_id=f"mllm_{request.request_id}",
            model_name=self.mllm_client.config.default_model,
            api_endpoint=self.mllm_client.config.base_url,
            prompt=base_prompt,
            images=images,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            task=request.task
        )

        mllm_response = self.mllm_client.call(mllm_request)

        if mllm_response.success:
            # 创建片段描述
            segment_caption = SegmentCaption(
                caption_id=f"seg_cap_{uuid.uuid4().hex[:8]}",
                segment_id=request.segment.segment_id,
                caption=mllm_response.text,
                summary=self._extract_summary(mllm_response.text),
                key_frames=[f.frame_id for f in request.frames[:5]],
                main_events=self._extract_events(mllm_response.text),
                key_objects=self._extract_objects(mllm_response.text),
                temporal_structure="",
                confidence=1.0,
                model_name=mllm_response.model_name
            )

            return VideoAnalysisResult(
                success=True,
                request_id=request.request_id,
                task=request.task,
                segment_caption=segment_caption,
                mllm_response=mllm_response
            )
        else:
            return VideoAnalysisResult(
                success=False,
                request_id=request.request_id,
                task=request.task,
                error_message=f"MLLM调用失败: {mllm_response.error_message}",
                mllm_response=mllm_response
            )

    def _generate_summary(self, request: VideoAnalysisRequest) -> VideoAnalysisResult:
        """
        生成摘要

        Args:
            request: 分析请求

        Returns:
            分析结果
        """
        # 基于上下文信息生成摘要
        prompt = f"""请根据以下视频分析信息，生成一个简洁的摘要：

{request.context_info}

要求：
1. 概括主要内容（2-3句话）
2. 突出重点事件
3. 保持客观描述
"""

        if request.prompt:
            prompt += f"\n\n特别关注：{request.prompt}"

        # 调用MLLM（文本任务，不需要图像）
        mllm_request = MLLMRequest(
            request_id=f"mllm_{request.request_id}",
            model_name=self.mllm_client.config.default_model,
            api_endpoint=self.mllm_client.config.base_url,
            prompt=prompt,
            temperature=request.temperature,
            max_tokens=min(request.max_tokens, 500),
            task=request.task
        )

        mllm_response = self.mllm_client.call(mllm_request)

        if mllm_response.success:
            return VideoAnalysisResult(
                success=True,
                request_id=request.request_id,
                task=request.task,
                summary=mllm_response.text,
                mllm_response=mllm_response
            )
        else:
            return VideoAnalysisResult(
                success=False,
                request_id=request.request_id,
                task=request.task,
                error_message=f"生成摘要失败: {mllm_response.error_message}",
                mllm_response=mllm_response
            )

    def _answer_question(self, request: VideoAnalysisRequest) -> VideoAnalysisResult:
        """
        回答问题

        Args:
            request: 分析请求

        Returns:
            分析结果
        """
        if not request.prompt:
            return VideoAnalysisResult(
                success=False,
                request_id=request.request_id,
                task=request.task,
                error_message="QA任务需要提供问题（prompt）"
            )

        # 准备图像（如果有）
        images = []
        if request.frames:
            for frame in request.frames[:request.max_frames]:
                image_data = frame.image_base64 if frame.image_base64 else frame.image_path or ""
                if image_data:
                    images.append(image_data)

        # 构建prompt
        prompt = f"""根据视频内容回答以下问题：

问题：{request.prompt}
"""

        if request.context_info:
            prompt = f"视频内容：\n{request.context_info}\n\n" + prompt

        # 调用MLLM
        mllm_request = MLLMRequest(
            request_id=f"mllm_{request.request_id}",
            model_name=self.mllm_client.config.default_model,
            api_endpoint=self.mllm_client.config.base_url,
            prompt=prompt,
            images=images,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            task=request.task
        )

        mllm_response = self.mllm_client.call(mllm_request)

        if mllm_response.success:
            return VideoAnalysisResult(
                success=True,
                request_id=request.request_id,
                task=request.task,
                summary=mllm_response.text,
                mllm_response=mllm_response
            )
        else:
            return VideoAnalysisResult(
                success=False,
                request_id=request.request_id,
                task=request.task,
                error_message=f"回答问题失败: {mllm_response.error_message}",
                mllm_response=mllm_response
            )

    def _extract_summary(self, text: str) -> str:
        """从文本中提取摘要"""
        # 简单实现：取前200个字符
        return text[:200] + "..." if len(text) > 200 else text

    def _extract_events(self, text: str) -> List[str]:
        """从文本中提取事件列表"""
        # 简单实现：查找数字开头的行
        import re
        pattern = r'\d+[\.、]\s*(.+)'
        events = re.findall(pattern, text)
        return events[:5] if events else []

    def _extract_objects(self, text: str) -> List[str]:
        """从文本中提取对象列表"""
        # 简单实现：查找常见名词
        # TODO: 可以使用NER或者更智能的提取
        common_keywords = ['人', '车', '建筑', '动物', '植物', '天空', '道路']
        objects = [kw for kw in common_keywords if kw in text]
        return objects

    def _record_analysis(
        self,
        request: VideoAnalysisRequest,
        result: VideoAnalysisResult
    ):
        """
        记录分析到上下文

        Args:
            request: 分析请求
            result: 分析结果
        """
        # 创建消息记录
        message = Message(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            message_type=MessageType.TASK_RESULT,
            sender_id=self.agent_id,
            receiver_id="system",
            content={
                "task": "video_analysis",
                "request": {
                    "task_type": request.task.value,
                    "num_frames": len(request.frames),
                    "has_segment": request.segment is not None
                },
                "result": {
                    "success": result.success,
                    "num_frame_captions": len(result.frame_captions),
                    "has_segment_caption": result.segment_caption is not None,
                    "error": result.error_message if not result.success else None
                },
                "metrics": {
                    "processing_time": result.processing_time,
                    "tokens": result.mllm_response.total_tokens if result.mllm_response else 0,
                    "cost_usd": result.mllm_response.cost_usd if result.mllm_response else 0
                }
            },
            context_id=self.context.context_id,
            priority=Priority.NORMAL,
            timestamp=time.time()
        )

        self.context.message_history.append(message)
        self.context.updated_at = time.time()

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "stats": self.stats.copy(),
            "state": {
                "status": self.state.status.value,
                "current_task": self.state.current_task_description
            }
        }

    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            "total_requests": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "frames_processed": 0,
            "segments_processed": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }
