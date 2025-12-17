"""
工具创建Agent (Tool Creator Agent)

通过MLLM API动态创建视频处理工具
根据用户需求描述，生成工具的定义、参数和实现代码
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
    ToolCallRequest,
    ToolCallResponse,
    Priority
)

from experiments import (
    MLLMRequest,
    MLLMResponse,
    AnalysisTask
)

from .mllm_client import MLLMClient, MLLMClientConfig

# 导入全局配置
from config import settings


@dataclass
class ToolCreationRequest:
    """工具创建请求"""
    request_id: str
    tool_name: str  # 工具名称
    tool_description: str  # 工具描述
    input_requirements: str  # 输入要求
    output_requirements: str  # 输出要求
    example_usage: str = ""  # 使用示例（可选）
    constraints: str = ""  # 约束条件（可选）


@dataclass
class ToolCreationResult:
    """工具创建结果"""
    success: bool
    tool_name: str
    tool_code: str = ""  # 生成的工具代码
    tool_description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    usage_example: str = ""
    error_message: str = ""
    mllm_response: Optional[MLLMResponse] = None


class ToolCreatorAgent:
    """
    工具创建Agent

    职责：
    1. 接收工具创建需求
    2. 构建prompt并调用MLLM API
    3. 解析MLLM返回的工具代码
    4. 返回工具定义和实现
    """

    def __init__(
        self,
        agent_id: str,
        mllm_client: Optional[MLLMClient] = None,
        context: Optional[Context] = None
    ):
        """
        初始化工具创建Agent

        Args:
            agent_id: Agent唯一标识
            mllm_client: MLLM客户端，如果不提供则创建默认客户端
            context: 上下文对象，用于消息历史和状态管理
        """
        self.agent_id = agent_id
        self.agent_name = "ToolCreatorAgent"

        # MLLM客户端
        if mllm_client is None:
            # 使用配置中的Tool Creator Agent设置
            config = MLLMClientConfig(
                default_model=settings.agent.tool_creator_model,
                default_temperature=settings.agent.tool_creator_temperature,
                default_max_tokens=settings.agent.tool_creator_max_tokens
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
            agent_role=AgentRole.TOOL_CREATOR,
            status=AgentStatus.IDLE,
            status_message="",
            current_task_id=None,
            current_task_description=""
        )

        # 额外的能力和性能指标（不在AgentState中）
        self.capabilities = ["tool_creation", "code_generation"]
        self.performance_metrics = {
            "tools_created": 0,
            "success_rate": 0.0,
            "avg_creation_time": 0.0
        }

        # 统计信息
        self.stats = {
            "total_requests": 0,
            "successful_creations": 0,
            "failed_creations": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }

    def create_tool(self, request: ToolCreationRequest) -> ToolCreationResult:
        """
        创建工具

        Args:
            request: 工具创建请求

        Returns:
            ToolCreationResult: 工具创建结果
        """
        self.stats["total_requests"] += 1
        self.state.status = AgentStatus.PROCESSING
        self.state.current_task_description = f"Creating tool: {request.tool_name}"

        start_time = time.time()

        try:
            # 1. 构建prompt
            prompt = self._build_tool_creation_prompt(request)

            # 2. 调用MLLM API
            mllm_request = MLLMRequest(
                request_id=f"mllm_{request.request_id}",
                model_name=self.mllm_client.config.default_model,
                api_endpoint=self.mllm_client.config.base_url,
                prompt=prompt,
                system_prompt=self._get_system_prompt(),
                temperature=self.mllm_client.config.default_temperature,
                max_tokens=self.mllm_client.config.default_max_tokens,
                task=AnalysisTask.OTHER
            )

            mllm_response = self.mllm_client.call(mllm_request)

            # 3. 解析响应
            if mllm_response.success:
                result = self._parse_tool_code(request, mllm_response)
                if result.success:
                    self.stats["successful_creations"] += 1
                else:
                    self.stats["failed_creations"] += 1
            else:
                result = ToolCreationResult(
                    success=False,
                    tool_name=request.tool_name,
                    error_message=f"MLLM API调用失败: {mllm_response.error_message}",
                    mllm_response=mllm_response
                )
                self.stats["failed_creations"] += 1

            # 4. 更新统计
            self.stats["total_tokens"] += mllm_response.total_tokens
            self.stats["total_cost"] += mllm_response.cost_usd

            # 5. 记录到上下文
            self._record_creation(request, result, time.time() - start_time)

            # 6. 更新状态
            self.state.status = AgentStatus.IDLE
            self.state.current_task_description = ""
            self.state.last_active_time = datetime.now().isoformat()

            return result

        except Exception as e:
            self.stats["failed_creations"] += 1
            self.state.status = AgentStatus.ERROR
            return ToolCreationResult(
                success=False,
                tool_name=request.tool_name,
                error_message=f"工具创建异常: {str(e)}"
            )

    def _get_system_prompt(self) -> str:
        """获取系统提示"""
        return """你是一个专业的Python工具开发专家，专门为视频理解任务创建工具。

你的任务是根据用户需求，生成完整的、可执行的Python工具代码。

要求：
1. 代码必须是完整的、可执行的Python函数
2. 包含详细的docstring说明
3. 包含参数类型提示
4. 包含输入验证
5. 包含错误处理
6. 代码风格清晰、易读
7. 专注于视频处理相关功能

输出格式：
```python
# 工具代码
def tool_name(param1: Type1, param2: Type2) -> ReturnType:
    \"\"\"
    工具描述

    Args:
        param1: 参数1说明
        param2: 参数2说明

    Returns:
        返回值说明
    \"\"\"
    # 实现代码
    pass
```

然后简要说明：
- 工具功能
- 参数说明
- 使用示例"""

    def _build_tool_creation_prompt(self, request: ToolCreationRequest) -> str:
        """
        构建工具创建的prompt

        Args:
            request: 工具创建请求

        Returns:
            完整的prompt字符串
        """
        prompt = f"""请创建一个名为 `{request.tool_name}` 的Python工具。

**工具描述：**
{request.tool_description}

**输入要求：**
{request.input_requirements}

**输出要求：**
{request.output_requirements}
"""

        if request.example_usage:
            prompt += f"""
**使用示例：**
{request.example_usage}
"""

        if request.constraints:
            prompt += f"""
**约束条件：**
{request.constraints}
"""

        prompt += """

请生成完整的、可执行的Python代码，并提供使用说明。"""

        return prompt

    def _parse_tool_code(
        self,
        request: ToolCreationRequest,
        mllm_response: MLLMResponse
    ) -> ToolCreationResult:
        """
        解析MLLM返回的工具代码

        Args:
            request: 原始请求
            mllm_response: MLLM响应

        Returns:
            工具创建结果
        """
        try:
            response_text = mllm_response.text

            # 提取代码块
            tool_code = self._extract_code_block(response_text)

            if not tool_code:
                return ToolCreationResult(
                    success=False,
                    tool_name=request.tool_name,
                    error_message="无法从响应中提取代码块",
                    mllm_response=mllm_response
                )

            # 提取描述和使用示例
            description = request.tool_description
            usage_example = self._extract_usage_example(response_text)

            return ToolCreationResult(
                success=True,
                tool_name=request.tool_name,
                tool_code=tool_code,
                tool_description=description,
                usage_example=usage_example,
                mllm_response=mllm_response
            )

        except Exception as e:
            return ToolCreationResult(
                success=False,
                tool_name=request.tool_name,
                error_message=f"解析工具代码失败: {str(e)}",
                mllm_response=mllm_response
            )

    def _extract_code_block(self, text: str) -> str:
        """
        从响应文本中提取代码块

        Args:
            text: 响应文本

        Returns:
            代码块内容
        """
        # 查找 ```python ... ``` 代码块
        import re
        pattern = r"```python\s*(.*?)\s*```"
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            return matches[0].strip()

        # 如果没有找到python代码块，尝试查找普通代码块
        pattern = r"```\s*(.*?)\s*```"
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            return matches[0].strip()

        return ""

    def _extract_usage_example(self, text: str) -> str:
        """
        从响应文本中提取使用示例

        Args:
            text: 响应文本

        Returns:
            使用示例
        """
        # 简单提取：查找"使用"、"example"等关键词后的内容
        lines = text.split('\n')
        example_started = False
        example_lines = []

        for line in lines:
            if any(keyword in line.lower() for keyword in ['使用示例', '示例', 'example', 'usage']):
                example_started = True
                continue

            if example_started:
                if line.strip().startswith('```'):
                    continue
                if line.strip() and not line.strip().startswith('#'):
                    example_lines.append(line)
                if len(example_lines) > 10:  # 限制长度
                    break

        return '\n'.join(example_lines) if example_lines else ""

    def _record_creation(
        self,
        request: ToolCreationRequest,
        result: ToolCreationResult,
        duration: float
    ):
        """
        记录工具创建到上下文

        Args:
            request: 工具创建请求
            result: 工具创建结果
            duration: 创建耗时
        """
        # 创建消息记录
        message = Message(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            message_type=MessageType.TASK_RESULT,
            sender_id=self.agent_id,
            receiver_id="system",
            content={
                "task": "tool_creation",
                "request": {
                    "tool_name": request.tool_name,
                    "description": request.tool_description
                },
                "result": {
                    "success": result.success,
                    "tool_name": result.tool_name,
                    "error": result.error_message if not result.success else None
                },
                "metrics": {
                    "duration_sec": duration,
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
            "successful_creations": 0,
            "failed_creations": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }
