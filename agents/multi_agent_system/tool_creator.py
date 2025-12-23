"""
Tool Creator Agent

负责根据任务需求动态设计工具，核心能力是设计高质量的prompt。
"""

import os
import json
import time
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

# 导入项目数据结构
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.multi_agent_system.types import (
    Tool, ToolParameter, AgentAction, AgentType, ActionType
)
from experiments.video_variables import AtomicOperations, MLLMRequest, AnalysisTask
from agents.mllm_client import MLLMClient, MLLMClientConfig


class ToolCreatorAgent:
    """
    Tool Creator Agent - 工具设计专家

    核心职责：
    1. 分析任务需求，理解用户意图
    2. 将任务分解为可执行的子任务
    3. 为每个子任务设计专门的工具（核心：prompt设计）
    4. 优化工具集，确保工具之间协同工作

    设计理念：
    - 动态Prompt：根据任务特点设计定制化prompt，而非硬编码
    - 原子操作组合：工具通过组合原子操作实现功能
    - 可追踪决策：记录所有设计决策和推理过程
    """

    def __init__(self, agent_id: Optional[str] = None, mllm_client: Optional[MLLMClient] = None):
        """
        初始化Tool Creator Agent

        Args:
            agent_id: Agent唯一标识，如果不提供则自动生成
            mllm_client: MLLM客户端，如果不提供则使用默认配置创建
        """
        self.agent_id = agent_id or f"tool_creator_{uuid.uuid4().hex[:8]}"

        # 初始化MLLM客户端
        if mllm_client:
            self.mllm = mllm_client
        else:
            config = MLLMClientConfig()
            self.mllm = MLLMClient(config)

        # 可用的原子操作
        self.atomic_operations = AtomicOperations.get_all_operations()

        # 行动历史
        self.actions: List[AgentAction] = []

    def design_tools(self, task_description: str, constraints: Optional[Dict[str, Any]] = None) -> List[Tool]:
        """
        设计工具集 - 主入口

        完整流程：
        1. 分析任务（理解需求和目标）
        2. 分解任务（识别子任务）
        3. 设计工具（为每个子任务设计专门工具）
        4. 优化工具集（合并、精简、优化）

        Args:
            task_description: 任务描述
            constraints: 约束条件（可选），如最大成本、时间限制等

        Returns:
            设计好的工具列表
        """
        print(f"\n{'='*60}")
        print(f"Tool Creator Agent [{self.agent_id}] Starting Tool Design")
        print(f"{'='*60}")
        print(f"\nTask: {task_description}")

        constraints = constraints or {}

        # Step 1: Analyze task
        print(f"\n[Step 1] Analyzing task...")
        task_analysis = self._analyze_task(task_description)
        print(f"  ✓ Task type: {task_analysis.get('task_type', 'unknown')}")
        print(f"  ✓ Key elements: {', '.join(task_analysis.get('key_elements', []))}")

        # Step 2: Decompose task
        print(f"\n[Step 2] Decomposing task...")
        subtasks = self._decompose_task(task_analysis, task_description)
        print(f"  ✓ Identified {len(subtasks)} subtasks:")
        for i, subtask in enumerate(subtasks, 1):
            print(f"    {i}. {subtask.get('name', 'unnamed')}: {subtask.get('description', '')[:60]}...")

        # Step 3: Design tools for each subtask
        print(f"\n[Step 3] Designing tools...")
        tools = []
        for i, subtask in enumerate(subtasks, 1):
            print(f"  [Tool {i}/{len(subtasks)}] Designing...")
            tool = self._design_tool(subtask, task_analysis, constraints)
            if tool:
                tools.append(tool)
                print(f"    ✓ {tool.tool_name}")
                print(f"      Purpose: {tool.purpose[:80]}...")
                print(f"      Atomic ops: {', '.join(tool.atomic_operations)}")

        # Step 4: Optimize toolset
        print(f"\n[Step 4] Optimizing toolset...")
        optimized_tools = self._optimize_toolset(tools, task_analysis)
        print(f"  ✓ Optimization complete: {len(tools)} → {len(optimized_tools)} tools")

        print(f"\n{'='*60}")
        print(f"Tool Design Complete! Designed {len(optimized_tools)} tools")
        print(f"{'='*60}\n")

        return optimized_tools

    def _analyze_task(self, task_description: str) -> Dict[str, Any]:
        """
        分析任务 - 理解任务需求和目标

        使用MLLM分析任务，提取关键信息：
        - 任务类型（视频问答、摘要、分析等）
        - 输入数据（视频路径、问题等）
        - 预期输出（答案、摘要、时间线等）
        - 关键要素（需要关注的内容）

        Args:
            task_description: 任务描述

        Returns:
            任务分析结果
        """
        start_time = time.time()

        analysis_prompt = f"""You are a video understanding task analysis expert. Please analyze the following task:

Task Description:
{task_description}

Provide a detailed task analysis in JSON format:

{{
    "task_type": "Task type (video_qa, video_summary, scene_analysis, event_detection, etc.)",
    "key_elements": ["key element 1", "key element 2", "..."],
    "input_data": {{
        "video": "Whether video input is needed",
        "question": "Whether question input is needed",
        "other": "Other input requirements"
    }},
    "expected_output": "Expected output format and content",
    "complexity": "Task complexity (simple, medium, complex)",
    "requires_temporal_understanding": "Whether temporal understanding is needed (true/false)",
    "requires_detail_analysis": "Whether detailed analysis is needed (true/false)",
    "recommended_approach": "Recommended processing approach"
}}

**IMPORTANT**: Output ONLY pure JSON. Do not add any explanatory text. Do not use Markdown code blocks.
Ensure the first character is {{ and the last character is }}."""

        system_prompt = "You are a professional task analysis expert, skilled at understanding video understanding task requirements and objectives."

        try:
            # 创建MLLMRequest对象
            request = MLLMRequest(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                model_name=self.mllm.config.default_model,
                api_endpoint=self.mllm.config.base_url or "",
                prompt=analysis_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=16000,  # 不限制输出，让模型充分表达
                task=AnalysisTask.CAPTION
            )

            response = self.mllm.call(request)

            # 解析JSON响应
            response_text = response.text.strip()

            # 尝试提取JSON（如果被代码块包裹）
            if "```json" in response_text:
                # 提取```json```代码块中的内容
                import re
                json_match = re.search(r'```json\s*\n(.*?)\n```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1).strip()
            elif "```" in response_text:
                # 提取普通代码块
                import re
                json_match = re.search(r'```\s*\n(.*?)\n```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1).strip()

            analysis = json.loads(response_text)

            # 记录行动
            action = AgentAction(
                action_id=f"action_{uuid.uuid4().hex[:8]}",
                agent_id=self.agent_id,
                agent_type=AgentType.TOOL_CREATOR,
                action_type=ActionType.REASON,
                inputs={"task_description": task_description},
                outputs={"analysis": analysis},
                reasoning="分析任务以理解需求和目标",
                tokens_used=response.total_tokens,
                cost_usd=response.cost_usd,
                duration_ms=(time.time() - start_time) * 1000,
                status="completed"
            )
            self.actions.append(action)

            return analysis

        except Exception as e:
            print(f"    ⚠️ Task analysis failed: {e}")
            # 返回默认分析
            return {
                "task_type": "video_qa",
                "key_elements": ["video", "question"],
                "complexity": "medium",
                "requires_temporal_understanding": True,
                "requires_detail_analysis": True
            }

    def _decompose_task(self, task_analysis: Dict[str, Any], task_description: str) -> List[Dict[str, Any]]:
        """
        分解任务 - 将任务分解为可执行的子任务

        基于任务分析结果，使用MLLM将任务分解为子任务。
        每个子任务都有明确的输入、输出和目标。

        Args:
            task_analysis: 任务分析结果
            task_description: 原始任务描述

        Returns:
            子任务列表
        """
        start_time = time.time()

        decompose_prompt = f"""You are a task decomposition expert. Based on the following task analysis, decompose the task into executable subtasks.

Original Task:
{task_description}

Task Analysis:
{json.dumps(task_analysis, ensure_ascii=False, indent=2)}

Available Atomic Operations:
- SAMPLE: Extract frames from video/segment
- SEGMENT: Split video into segments
- CALL_MODEL: Call MLLM for understanding
- BBOX: Draw annotations on frames

Please decompose the task into 3-5 subtasks in JSON format:

{{
    "subtasks": [
        {{
            "name": "Subtask name",
            "description": "Detailed description of what this subtask does",
            "purpose": "Why this subtask is needed",
            "inputs": ["input1", "input2"],
            "outputs": ["output1", "output2"],
            "atomic_operations": ["required atomic operations"],
            "priority": 1
        }},
        ...
    ]
}}

Notes:
1. Subtasks should be arranged in execution order
2. Each subtask should have a clear objective
3. Subtasks should have logical connections
4. Prioritize CALL_MODEL for understanding and analysis

**IMPORTANT**: Output ONLY pure JSON. Do not add any explanatory text. Do not use Markdown code blocks.
Ensure the first character is {{ and the last character is }}."""

        system_prompt = "You are a professional task decomposition expert, skilled at breaking down complex tasks into executable subtasks."

        try:
            # 创建MLLMRequest对象
            request = MLLMRequest(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                model_name=self.mllm.config.default_model,
                api_endpoint=self.mllm.config.base_url or "",
                prompt=decompose_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=16000,  # 不限制输出，让模型充分表达
                task=AnalysisTask.CAPTION
            )

            response = self.mllm.call(request)

            # 解析JSON响应
            response_text = response.text.strip()

            # 尝试提取JSON（如果被代码块包裹）
            if "```json" in response_text:
                import re
                json_match = re.search(r'```json\s*\n(.*?)\n```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1).strip()
            elif "```" in response_text:
                import re
                json_match = re.search(r'```\s*\n(.*?)\n```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1).strip()

            result = json.loads(response_text)
            subtasks = result.get("subtasks", [])

            # 记录行动
            action = AgentAction(
                action_id=f"action_{uuid.uuid4().hex[:8]}",
                agent_id=self.agent_id,
                agent_type=AgentType.TOOL_CREATOR,
                action_type=ActionType.REASON,
                inputs={"task_analysis": task_analysis},
                outputs={"subtasks": subtasks},
                reasoning="将任务分解为可执行的子任务",
                tokens_used=response.total_tokens,
                cost_usd=response.cost_usd,
                duration_ms=(time.time() - start_time) * 1000,
                status="completed"
            )
            self.actions.append(action)

            return subtasks

        except Exception as e:
            print(f"    ⚠️ Task decomposition failed: {e}")
            # 返回默认子任务（标准视频问答流程）
            return [
                {
                    "name": "video_segmentation",
                    "description": "将视频分割成多个片段以便分析",
                    "purpose": "处理长视频，提高分析效率",
                    "inputs": ["video"],
                    "outputs": ["segments"],
                    "atomic_operations": ["SEGMENT"],
                    "priority": 1
                },
                {
                    "name": "segment_analysis",
                    "description": "分析每个视频片段的内容",
                    "purpose": "理解视频各部分的内容",
                    "inputs": ["segment"],
                    "outputs": ["segment_caption"],
                    "atomic_operations": ["SAMPLE", "CALL_MODEL"],
                    "priority": 2
                },
                {
                    "name": "question_answering",
                    "description": "基于视频分析回答问题",
                    "purpose": "提供最终答案",
                    "inputs": ["question", "segment_captions"],
                    "outputs": ["answer"],
                    "atomic_operations": ["CALL_MODEL"],
                    "priority": 3
                }
            ]

    def _design_tool(
        self,
        subtask: Dict[str, Any],
        task_analysis: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> Optional[Tool]:
        """
        设计工具 - 为子任务设计专门的工具

        这是Tool Creator Agent最核心的方法！
        使用MLLM设计：
        1. 高质量的Prompt模板（使用{var}占位符）
        2. System Prompt
        3. 参数定义
        4. 输出格式

        Args:
            subtask: 子任务信息
            task_analysis: 任务分析结果
            constraints: 约束条件

        Returns:
            设计好的工具
        """
        start_time = time.time()

        # 构建工具设计prompt
        design_prompt = f"""You are an AI tool design expert, skilled at designing high-quality prompts.

Subtask to Design Tool For:
Name: {subtask.get('name', 'unnamed')}
Description: {subtask.get('description', '')}
Purpose: {subtask.get('purpose', '')}
Inputs: {', '.join(subtask.get('inputs', []))}
Outputs: {', '.join(subtask.get('outputs', []))}
Atomic Operations to Use: {', '.join(subtask.get('atomic_operations', []))}

Task Context:
Task Type: {task_analysis.get('task_type', 'unknown')}
Requires Temporal Understanding: {task_analysis.get('requires_temporal_understanding', False)}
Requires Detail Analysis: {task_analysis.get('requires_detail_analysis', False)}

Please design a tool to accomplish this subtask. Design content includes:

1. **Prompt Template**: Design a clear and effective prompt, use {{variable}} as placeholders
   - Clearly instruct what the model should do
   - Specify expected output format
   - Include necessary context

2. **System Prompt**: Define the model's role and expertise

3. **Parameter Definitions**: List all required input parameters

4. **Output Format**: Clearly define the output structure

Output the tool definition in JSON format:

{{
    "tool_name": "Tool name (snake_case)",
    "description": "Brief description of the tool",
    "purpose": "Purpose and use of the tool",
    "prompt_template": "Detailed prompt template, use {{var}} as placeholders, include clear instructions and output format requirements",
    "system_prompt": "System prompt defining the model's role",
    "parameters": [
        {{
            "name": "parameter name",
            "type": "parameter type (str, int, Segment, Frame, etc.)",
            "description": "parameter description",
            "required": true/false,
            "default": null
        }},
        ...
    ],
    "output_schema": {{
        "type": "object/string/list",
        "description": "output format description",
        "example": "output example"
    }},
    "atomic_operations": ["required atomic operations"],
    "usage_example": "usage example",
    "best_practices": ["best practice 1", "best practice 2"]
}}

Important Tips:
- Prompt should be specific and clear, avoid vague expressions
- Clearly specify output format for easy downstream processing
- System prompt should highlight model's professional capabilities
- If video analysis is involved, consider temporal relationships and context

**IMPORTANT**: Output ONLY pure JSON. Do not add any explanatory text. Do not use Markdown code blocks.
Ensure the first character is {{ and the last character is }}."""

        system_prompt = "You are a professional AI tool design expert, skilled at designing high-quality prompts and tool definitions."

        try:
            # 创建MLLMRequest对象
            request = MLLMRequest(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                model_name=self.mllm.config.default_model,
                api_endpoint=self.mllm.config.base_url or "",
                prompt=design_prompt,
                system_prompt=system_prompt,
                temperature=0.4,
                max_tokens=16000,  # 不限制输出，让模型充分表达
                task=AnalysisTask.CAPTION
            )

            response = self.mllm.call(request)

            # 解析JSON响应
            response_text = response.text.strip()

            # 调试：打印实际响应（前500字符）
            print(f"      [Debug] API response (first 500 chars): {response_text[:500]}...")

            # 尝试提取JSON（如果被代码块包裹）
            if "```json" in response_text:
                import re
                json_match = re.search(r'```json\s*\n(.*?)\n```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1).strip()
            elif "```" in response_text:
                import re
                json_match = re.search(r'```\s*\n(.*?)\n```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1).strip()

            tool_def = json.loads(response_text)

            # 构建Tool对象
            tool = Tool(
                tool_id=f"tool_{uuid.uuid4().hex[:8]}",
                tool_name=tool_def.get("tool_name", subtask.get("name", "unnamed_tool")),
                description=tool_def.get("description", ""),
                purpose=tool_def.get("purpose", ""),
                prompt_template=tool_def.get("prompt_template", ""),
                system_prompt=tool_def.get("system_prompt", "You are a helpful AI assistant."),
                parameters={
                    param["name"]: ToolParameter(
                        name=param["name"],
                        type=param["type"],
                        description=param.get("description", ""),
                        required=param.get("required", True),
                        default=param.get("default")
                    )
                    for param in tool_def.get("parameters", [])
                },
                output_schema=tool_def.get("output_schema", {}),
                atomic_operations=tool_def.get("atomic_operations", []),
                usage_example=tool_def.get("usage_example", ""),
                best_practices=tool_def.get("best_practices", []),
                created_by=self.agent_id
            )

            # 记录行动
            action = AgentAction(
                action_id=f"action_{uuid.uuid4().hex[:8]}",
                agent_id=self.agent_id,
                agent_type=AgentType.TOOL_CREATOR,
                action_type=ActionType.DESIGN_TOOL,
                tool=tool,
                inputs={"subtask": subtask},
                outputs={"tool": tool.to_dict()},
                reasoning=f"为子任务'{subtask.get('name', 'unnamed')}'设计专门的工具，包含定制化prompt",
                tokens_used=response.total_tokens,
                cost_usd=response.cost_usd,
                duration_ms=(time.time() - start_time) * 1000,
                status="completed"
            )
            self.actions.append(action)

            return tool

        except Exception as e:
            print(f"    ⚠️ Tool design failed: {e}")
            return None

    def _optimize_toolset(self, tools: List[Tool], task_analysis: Dict[str, Any]) -> List[Tool]:
        """
        优化工具集 - 合并、精简、优化工具

        检查工具集，进行优化：
        1. 合并功能相似的工具
        2. 移除冗余工具
        3. 优化工具顺序
        4. 确保工具之间协同良好

        Args:
            tools: 初始工具列表
            task_analysis: 任务分析结果

        Returns:
            优化后的工具列表
        """
        # 当前版本：简单返回原工具列表
        # 未来可以添加更复杂的优化逻辑

        # 基本验证：确保每个工具都有必要的信息
        valid_tools = []
        for tool in tools:
            if tool.tool_name and tool.prompt_template and tool.atomic_operations:
                valid_tools.append(tool)
            else:
                print(f"    ⚠️ Tool {tool.tool_name} has incomplete information, removed")

        return valid_tools

    def get_actions(self) -> List[AgentAction]:
        """获取所有行动记录"""
        return self.actions

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_tokens = sum(action.tokens_used for action in self.actions)
        total_cost = sum(action.cost_usd for action in self.actions)
        total_duration = sum(action.duration_ms for action in self.actions)

        return {
            "agent_id": self.agent_id,
            "total_actions": len(self.actions),
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost,
            "total_duration_ms": total_duration,
            "actions_by_type": {
                action_type.value: len([a for a in self.actions if a.action_type == action_type])
                for action_type in ActionType
            }
        }
