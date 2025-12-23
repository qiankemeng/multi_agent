"""
Tool Executor

工具执行引擎，负责解释Tool定义并调用原子操作。
"""

import time
from typing import Dict, Any, List, Optional

# 导入项目数据结构
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.multi_agent_system.types import Tool
from experiments.video_variables import AtomicOperations


class ToolExecutor:
    """
    Tool Executor - 工具执行引擎

    核心职责：
    1. 解释Tool定义
    2. 根据tool的atomic_operations调用相应的原子操作
    3. 使用tool的prompt_template格式化输入
    4. 返回标准化的执行结果

    设计理念：
    - 桥接工具定义和原子操作实现
    - 处理prompt模板填充
    - 统一执行接口
    """

    def __init__(self, atomic_ops: Any = None):
        """
        初始化Tool Executor

        Args:
            atomic_ops: 原子操作实现（AtomicOperationsImplementation实例）
        """
        self.atomic_ops = atomic_ops

    def execute(self, tool: Tool, inputs: Dict[str, Any], atomic_ops: Any) -> Dict[str, Any]:
        """
        执行工具

        根据工具定义，调用相应的原子操作并返回结果。

        执行流程：
        1. 验证输入参数
        2. 根据atomic_operations确定执行流程
        3. 调用原子操作
        4. 格式化输出

        Args:
            tool: 要执行的工具
            inputs: 输入参数
            atomic_ops: 原子操作实现

        Returns:
            执行结果，包含：
            - output: 主要输出
            - tokens_used: 使用的tokens（如果有MLLM调用）
            - cost_usd: 成本（如果有MLLM调用）
            - intermediate_results: 中间结果
        """
        print(f"    [Executor] 执行工具: {tool.tool_name}")

        start_time = time.time()
        result = {
            "output": None,
            "tokens_used": 0,
            "cost_usd": 0.0,
            "intermediate_results": {},
            "duration_ms": 0.0
        }

        try:
            # 1. 验证输入参数
            self._validate_inputs(tool, inputs)

            # 2. 根据atomic_operations执行
            operations = tool.atomic_operations

            # SEGMENT操作
            if AtomicOperations.SEGMENT in operations:
                print(f"      → 执行SEGMENT操作")
                result["intermediate_results"]["segments"] = self._execute_segment(
                    tool, inputs, atomic_ops
                )

            # SAMPLE操作
            if AtomicOperations.SAMPLE in operations:
                print(f"      → 执行SAMPLE操作")
                result["intermediate_results"]["frames"] = self._execute_sample(
                    tool, inputs, atomic_ops
                )

            # BBOX操作
            if AtomicOperations.BBOX in operations:
                print(f"      → 执行BBOX操作")
                result["intermediate_results"]["annotated_frames"] = self._execute_bbox(
                    tool, inputs, atomic_ops
                )

            # CALL_MODEL操作（通常是最后一步）
            if AtomicOperations.CALL_MODEL in operations:
                print(f"      → 执行CALL_MODEL操作")
                model_result = self._execute_call_model(
                    tool, inputs, result["intermediate_results"], atomic_ops
                )
                result["output"] = model_result["output"]
                result["tokens_used"] = model_result.get("tokens_used", 0)
                result["cost_usd"] = model_result.get("cost_usd", 0.0)
            else:
                # 如果没有CALL_MODEL，使用最后一个中间结果作为输出
                if result["intermediate_results"]:
                    last_key = list(result["intermediate_results"].keys())[-1]
                    result["output"] = result["intermediate_results"][last_key]

            result["duration_ms"] = (time.time() - start_time) * 1000
            print(f"      ✓ 执行完成 ({result['duration_ms']:.0f}ms)")

            return result

        except Exception as e:
            print(f"      ✗ 执行失败: {e}")
            result["error"] = str(e)
            result["duration_ms"] = (time.time() - start_time) * 1000
            raise

    def _validate_inputs(self, tool: Tool, inputs: Dict[str, Any]):
        """
        验证输入参数

        检查必需参数是否都提供了。

        Args:
            tool: 工具定义
            inputs: 输入参数

        Raises:
            ValueError: 如果缺少必需参数
        """
        for param_name, param in tool.parameters.items():
            if param.required and param_name not in inputs:
                raise ValueError(f"缺少必需参数: {param_name}")

    def _execute_segment(self, tool: Tool, inputs: Dict[str, Any], atomic_ops: Any) -> List[Any]:
        """
        执行SEGMENT操作

        将视频分段。

        Args:
            tool: 工具定义
            inputs: 输入参数
            atomic_ops: 原子操作实现

        Returns:
            分段列表
        """
        # 从inputs中获取video_meta
        video_meta = inputs.get("video_meta")
        if not video_meta:
            raise ValueError("SEGMENT操作需要video_meta参数")

        # 获取分段参数（如果tool的parameters中定义了）
        strategy = inputs.get("strategy", "fixed_duration")
        params = inputs.get("params", {"duration_sec": 60.0})

        # 调用原子操作
        segments = atomic_ops.segment(
            video_meta=video_meta,
            strategy=strategy,
            params=params
        )

        return segments

    def _execute_sample(self, tool: Tool, inputs: Dict[str, Any], atomic_ops: Any) -> List[Any]:
        """
        执行SAMPLE操作

        从视频或片段中采样帧。

        Args:
            tool: 工具定义
            inputs: 输入参数
            atomic_ops: 原子操作实现

        Returns:
            帧列表
        """
        # 确定source（可能是video_meta或segment）
        source = inputs.get("segment") or inputs.get("video_meta")
        if not source:
            raise ValueError("SAMPLE操作需要segment或video_meta参数")

        # 获取采样参数
        method = inputs.get("method", "uniform")
        params = inputs.get("params", {"num_frames": 5})

        # 调用原子操作
        frames = atomic_ops.sample(
            source=source,
            method=method,
            params=params
        )

        return frames

    def _execute_bbox(self, tool: Tool, inputs: Dict[str, Any], atomic_ops: Any) -> List[Any]:
        """
        执行BBOX操作

        在帧上绘制边界框。

        Args:
            tool: 工具定义
            inputs: 输入参数
            atomic_ops: 原子操作实现

        Returns:
            标注后的帧列表
        """
        frames = inputs.get("frames", [])
        boxes = inputs.get("boxes", [])

        if not frames:
            raise ValueError("BBOX操作需要frames参数")

        annotated_frames = []
        for frame in frames:
            annotated = atomic_ops.bbox(
                frame=frame,
                boxes=boxes
            )
            annotated_frames.append(annotated)

        return annotated_frames

    def _execute_call_model(
        self,
        tool: Tool,
        inputs: Dict[str, Any],
        intermediate_results: Dict[str, Any],
        atomic_ops: Any
    ) -> Dict[str, Any]:
        """
        执行CALL_MODEL操作

        这是最核心的操作：使用tool设计的prompt调用MLLM。

        流程：
        1. 准备prompt（使用tool.prompt_template填充参数）
        2. 准备图像（如果有）
        3. 调用MLLM
        4. 返回结果

        Args:
            tool: 工具定义
            inputs: 输入参数
            intermediate_results: 中间结果（可能包含frames等）
            atomic_ops: 原子操作实现

        Returns:
            模型输出结果
        """
        # 1. 准备prompt填充参数
        prompt_params = {}

        # 从inputs中获取参数
        for param_name in tool.parameters.keys():
            if param_name in inputs:
                value = inputs[param_name]
                # 如果是对象，转换为字符串表示
                if hasattr(value, '__dict__'):
                    prompt_params[param_name] = str(value)
                else:
                    prompt_params[param_name] = value

        # 从intermediate_results中获取参数
        for key, value in intermediate_results.items():
            if key == "frames":
                # 帧数量
                prompt_params["num_frames"] = len(value)
            elif key == "segments":
                # 片段数量
                prompt_params["num_segments"] = len(value)

        # 2. 填充prompt模板
        try:
            prompt = tool.prompt_template.format(**prompt_params)
        except KeyError as e:
            print(f"      ⚠️ Prompt模板参数缺失: {e}")
            # 尝试部分填充
            prompt = tool.prompt_template
            for key, value in prompt_params.items():
                placeholder = "{" + key + "}"
                if placeholder in prompt:
                    prompt = prompt.replace(placeholder, str(value))

        # 3. 准备图像（如果有frames）
        images = []
        if "frames" in intermediate_results:
            frames = intermediate_results["frames"]
            for frame in frames:
                if hasattr(frame, 'image_path') and frame.image_path:
                    images.append(frame.image_path)

        # 4. 获取其他MLLM参数
        temperature = inputs.get("temperature", 0.7)
        max_tokens = inputs.get("max_tokens", 4000)

        # 5. 调用MLLM
        response = atomic_ops.call_model(
            model_type="mllm",
            model_name=inputs.get("model_name", "default"),
            inputs={
                "prompt": prompt,
                "system_prompt": tool.system_prompt,
                "images": images
            },
            params={
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        )

        # 6. 返回结果
        return {
            "output": response.output if hasattr(response, 'output') else response.text,
            "tokens_used": response.total_tokens if hasattr(response, 'total_tokens') else 0,
            "cost_usd": response.cost_usd if hasattr(response, 'cost_usd') else 0.0,
            "response": response
        }
