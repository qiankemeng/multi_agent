"""
MLLM API调用封装模块

提供统一的接口调用OpenAI等MLLM API服务
支持文本和图像输入，返回标准化响应
"""

import os
import time
import base64
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import json

try:
    import openai
    from openai import OpenAI
except ImportError:
    print("Warning: openai package not installed. Please install it with: pip install openai")
    OpenAI = None

# 导入项目定义的数据结构
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments import (
    MLLMRequest,
    MLLMResponse,
    AnalysisTask
)

# 导入全局配置
from config import settings


@dataclass
class MLLMClientConfig:
    """MLLM客户端配置"""
    api_key: Optional[str] = None  # API密钥，如果不提供则从配置读取
    base_url: Optional[str] = None  # API基础URL，如果不提供则从配置读取
    default_model: Optional[str] = None  # 默认模型，如果不提供则从配置读取
    default_temperature: Optional[float] = None  # 默认温度，如果不提供则从配置读取
    default_max_tokens: Optional[int] = None  # 默认最大token数，如果不提供则从配置读取
    timeout: Optional[int] = None  # 超时时间（秒），如果不提供则从配置读取
    max_retries: Optional[int] = None  # 最大重试次数，如果不提供则从配置读取
    retry_delay: Optional[float] = None  # 重试延迟（秒），如果不提供则从配置读取

    # Token价格（美元/1K tokens），如果不提供则从配置读取
    price_per_1k_prompt_tokens: Optional[float] = None
    price_per_1k_completion_tokens: Optional[float] = None

    def __post_init__(self):
        """初始化后处理 - 从全局配置加载默认值"""
        # API配置
        if self.api_key is None:
            self.api_key = settings.openai.api_key
            if not self.api_key and not settings.dev.mock_mode:
                print("Warning: OPENAI_API_KEY not set in configuration")

        if self.base_url is None:
            self.base_url = settings.openai.base_url

        if self.default_model is None:
            self.default_model = settings.openai.default_model

        # MLLM参数
        if self.default_temperature is None:
            self.default_temperature = settings.mllm.default_temperature

        if self.default_max_tokens is None:
            self.default_max_tokens = settings.mllm.default_max_tokens

        if self.timeout is None:
            self.timeout = settings.mllm.request_timeout

        if self.max_retries is None:
            self.max_retries = settings.mllm.max_retries

        if self.retry_delay is None:
            self.retry_delay = settings.mllm.retry_delay

        # 价格配置
        if self.price_per_1k_prompt_tokens is None:
            self.price_per_1k_prompt_tokens = settings.openai.price_prompt_1k

        if self.price_per_1k_completion_tokens is None:
            self.price_per_1k_completion_tokens = settings.openai.price_completion_1k


class MLLMClient:
    """
    MLLM API客户端

    封装OpenAI API调用，支持文本和图像输入
    提供统一的请求/响应接口
    """

    def __init__(self, config: Optional[MLLMClientConfig] = None):
        """
        初始化MLLM客户端

        Args:
            config: 客户端配置，如果不提供则使用默认配置
        """
        self.config = config or MLLMClientConfig()

        # 初始化OpenAI客户端
        if OpenAI is None:
            raise ImportError("openai package is required. Install it with: pip install openai")

        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout
        )

        # 统计信息
        self.total_requests = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0

    def call(self, request: MLLMRequest) -> MLLMResponse:
        """
        调用MLLM API

        Args:
            request: MLLM请求对象

        Returns:
            MLLMResponse: MLLM响应对象
        """
        # 构建消息
        messages = self._build_messages(request)

        # 准备API调用参数
        api_params = {
            "model": request.model_name or self.config.default_model,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        # 重试逻辑
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                # 调用API
                response = self.client.chat.completions.create(**api_params)

                # 解析响应
                mllm_response = self._parse_response(request, response)

                # 更新统计
                self._update_stats(mllm_response)

                return mllm_response

            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
                    continue
                else:
                    # 最后一次重试失败，返回错误响应
                    return self._create_error_response(request, str(e))

        # 理论上不会到这里，但为了安全
        return self._create_error_response(request, str(last_error))

    def _build_messages(self, request: MLLMRequest) -> List[Dict[str, Any]]:
        """
        构建OpenAI API消息格式

        Args:
            request: MLLM请求对象

        Returns:
            消息列表
        """
        messages = []

        # 系统消息（如果有）
        if hasattr(request, 'system_prompt') and request.system_prompt:
            messages.append({
                "role": "system",
                "content": request.system_prompt
            })

        # 用户消息内容
        content = []

        # 添加文本
        if request.prompt:
            content.append({
                "type": "text",
                "text": request.prompt
            })

        # 添加图像
        for image_data in request.images:
            image_content = self._format_image(image_data)
            if image_content:
                content.append(image_content)

        # 添加视频帧（作为图像序列）
        for frame_data in request.video_frames:
            frame_content = self._format_image(frame_data)
            if frame_content:
                content.append(frame_content)

        messages.append({
            "role": "user",
            "content": content
        })

        return messages

    def _format_image(self, image_data: str) -> Optional[Dict[str, Any]]:
        """
        格式化图像数据为OpenAI API格式

        Args:
            image_data: 图像数据（URL或base64编码）

        Returns:
            图像内容字典，如果格式错误则返回None
        """
        if not image_data:
            return None

        # 判断是URL还是base64
        if image_data.startswith(('http://', 'https://')):
            # URL格式
            return {
                "type": "image_url",
                "image_url": {
                    "url": image_data
                }
            }
        elif image_data.startswith('data:image'):
            # data URL格式 (data:image/jpeg;base64,...)
            return {
                "type": "image_url",
                "image_url": {
                    "url": image_data
                }
            }
        else:
            # 假设是base64编码，添加data URL前缀
            return {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_data}"
                }
            }

    def _parse_response(self, request: MLLMRequest, api_response) -> MLLMResponse:
        """
        解析API响应为MLLMResponse对象

        Args:
            request: 原始请求
            api_response: OpenAI API响应

        Returns:
            MLLMResponse对象
        """
        # 提取响应文本
        text = api_response.choices[0].message.content

        # 提取token统计
        usage = api_response.usage
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens

        # 计算成本
        cost = self._calculate_cost(prompt_tokens, completion_tokens)

        # 创建响应对象
        response = MLLMResponse(
            response_id=f"resp_{int(time.time() * 1000)}",
            request_id=request.request_id,
            text=text,
            success=True,
            error_message=None,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            model_name=request.model_name or self.config.default_model,
            timestamp=time.time()
        )

        return response

    def _create_error_response(self, request: MLLMRequest, error_message: str) -> MLLMResponse:
        """
        创建错误响应

        Args:
            request: 原始请求
            error_message: 错误消息

        Returns:
            MLLMResponse对象
        """
        return MLLMResponse(
            response_id=f"resp_{int(time.time() * 1000)}",
            request_id=request.request_id,
            text="",
            success=False,
            error_message=error_message,
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            cost_usd=0.0,
            model_name=request.model_name or self.config.default_model,
            timestamp=time.time()
        )

    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        计算API调用成本

        Args:
            prompt_tokens: 提示token数
            completion_tokens: 完成token数

        Returns:
            成本（美元）
        """
        prompt_cost = (prompt_tokens / 1000) * self.config.price_per_1k_prompt_tokens
        completion_cost = (completion_tokens / 1000) * self.config.price_per_1k_completion_tokens
        return prompt_cost + completion_cost

    def _update_stats(self, response: MLLMResponse):
        """
        更新统计信息

        Args:
            response: MLLM响应
        """
        if response.success:
            self.total_requests += 1
            self.total_prompt_tokens += response.prompt_tokens
            self.total_completion_tokens += response.completion_tokens
            self.total_cost += response.cost_usd

    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        return {
            "total_requests": self.total_requests,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "total_cost_usd": self.total_cost,
            "avg_tokens_per_request": (
                (self.total_prompt_tokens + self.total_completion_tokens) / self.total_requests
                if self.total_requests > 0 else 0
            ),
            "avg_cost_per_request": (
                self.total_cost / self.total_requests
                if self.total_requests > 0 else 0
            )
        }

    def reset_stats(self):
        """重置统计信息"""
        self.total_requests = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0


# 便捷函数
def create_client(
    api_key: Optional[str] = None,
    model: str = "gpt-4-vision-preview",
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> MLLMClient:
    """
    创建MLLM客户端的便捷函数

    Args:
        api_key: OpenAI API密钥
        model: 默认模型
        temperature: 默认温度
        max_tokens: 默认最大token数

    Returns:
        MLLMClient实例
    """
    config = MLLMClientConfig(
        api_key=api_key,
        default_model=model,
        default_temperature=temperature,
        default_max_tokens=max_tokens
    )
    return MLLMClient(config)
