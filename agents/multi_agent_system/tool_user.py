"""
Tool User Agent

负责使用Tool Creator设计的工具来完成任务。
核心能力：任务规划、工具选择、执行协调、结果整合。
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
    Tool, AgentAction, AgentPlan, PlanStep, PlanStatus,
    AgentType, ActionType
)
from experiments.video_variables import MLLMRequest, AnalysisTask
from agents.mllm_client import MLLMClient, MLLMClientConfig


class ToolUserAgent:
    """
    Tool User Agent - 工具使用专家

    核心职责：
    1. 接收任务和可用工具集
    2. 使用MLLM规划执行步骤（决定使用哪些工具，顺序如何）
    3. 执行计划，调用Tool Executor执行工具
    4. 整合结果，生成最终输出

    设计理念：
    - 智能规划：根据任务和工具动态规划执行步骤
    - 灵活执行：根据中间结果调整执行策略
    - 完整追踪：记录所有决策和执行过程
    """

    def __init__(self, agent_id: Optional[str] = None, mllm_client: Optional[MLLMClient] = None):
        """
        初始化Tool User Agent

        Args:
            agent_id: Agent唯一标识，如果不提供则自动生成
            mllm_client: MLLM客户端，如果不提供则使用默认配置创建
        """
        self.agent_id = agent_id or f"tool_user_{uuid.uuid4().hex[:8]}"

        # 初始化MLLM客户端
        if mllm_client:
            self.mllm = mllm_client
        else:
            config = MLLMClientConfig()
            self.mllm = MLLMClient(config)

        # 行动历史
        self.actions: List[AgentAction] = []

        # Tool Executor引用（稍后设置）
        self.tool_executor = None

    def set_tool_executor(self, executor):
        """设置Tool Executor"""
        self.tool_executor = executor

    def execute_task(
        self,
        task: str,
        tools: List[Tool],
        data: Dict[str, Any],
        atomic_ops: Any
    ) -> Dict[str, Any]:
        """
        执行任务 - 主入口

        完整流程：
        1. 创建执行计划（使用MLLM规划步骤）
        2. 执行计划中的每个步骤
        3. 整合结果

        Args:
            task: 任务描述
            tools: 可用工具列表
            data: 输入数据（如video_path, question等）
            atomic_ops: 原子操作实现

        Returns:
            任务执行结果
        """
        print(f"\n{'='*60}")
        print(f"Tool User Agent [{self.agent_id}] 开始执行任务")
        print(f"{'='*60}")
        print(f"\n任务: {task}")
        print(f"可用工具: {len(tools)} 个")

        # 确保tool_executor已设置
        if not self.tool_executor:
            from agents.multi_agent_system.tool_executor import ToolExecutor
            self.tool_executor = ToolExecutor(atomic_ops=atomic_ops)

        # Step 1: 创建执行计划
        print(f"\n[步骤1] 创建执行计划...")
        plan = self._create_plan(task, tools, data)
        print(f"  ✓ 计划创建完成，共 {len(plan.steps)} 个步骤")
        for i, step in enumerate(plan.steps, 1):
            print(f"    {i}. {step.tool_name}: {step.expected_output}")

        # Step 2: 执行计划
        print(f"\n[步骤2] 执行计划...")
        plan.status = PlanStatus.EXECUTING
        plan.started_at = datetime.now().isoformat()

        execution_results = {}

        for i, step in enumerate(plan.steps, 1):
            print(f"\n  [步骤 {i}/{len(plan.steps)}] 执行 {step.tool_name}...")

            try:
                # 准备输入
                step_inputs = self._prepare_inputs(step, execution_results, data)

                # 选择工具
                tool = self._select_tool(step.tool_name, tools)
                if not tool:
                    print(f"    ✗ 工具 {step.tool_name} 未找到")
                    step.status = "failed"
                    continue

                # 执行工具
                step.status = "running"
                result = self._execute_tool(tool, step_inputs, atomic_ops)

                # 记录结果
                execution_results[step.step_id] = result
                step.actual_output = result
                step.status = "completed"

                print(f"    ✓ 执行成功")
                if isinstance(result, dict) and "output" in result:
                    output_preview = str(result["output"])[:100]
                    print(f"      输出: {output_preview}...")

            except Exception as e:
                print(f"    ✗ 执行失败: {e}")
                step.status = "failed"
                execution_results[step.step_id] = {"error": str(e)}

        # Step 3: 整合结果
        print(f"\n[步骤3] 整合结果...")
        final_result = self._aggregate_results(execution_results, plan)

        plan.status = PlanStatus.COMPLETED
        plan.completed_at = datetime.now().isoformat()

        print(f"  ✓ 任务执行完成")
        print(f"\n{'='*60}")
        print(f"执行统计:")
        print(f"  - 总步骤: {len(plan.steps)}")
        print(f"  - 成功: {len([s for s in plan.steps if s.status == 'completed'])}")
        print(f"  - 失败: {len([s for s in plan.steps if s.status == 'failed'])}")
        print(f"  - Tokens: {plan.total_tokens}")
        print(f"  - 成本: ${plan.total_cost:.4f}")
        print(f"{'='*60}\n")

        return {
            "result": final_result,
            "plan": plan,
            "execution_results": execution_results
        }

    def _create_plan(self, task: str, tools: List[Tool], data: Dict[str, Any]) -> AgentPlan:
        """
        创建执行计划 - 使用MLLM规划执行步骤

        基于任务、可用工具和输入数据，规划执行步骤。

        Args:
            task: 任务描述
            tools: 可用工具列表
            data: 输入数据

        Returns:
            执行计划
        """
        start_time = time.time()

        # 格式化工具信息
        tools_info = []
        for tool in tools:
            tools_info.append({
                "tool_name": tool.tool_name,
                "description": tool.description,
                "purpose": tool.purpose,
                "inputs": list(tool.parameters.keys()),
                "atomic_operations": tool.atomic_operations
            })

        planning_prompt = f"""You are a task planning expert. Please create an execution plan for the following task.

Task:
{task}

Available Tools:
{json.dumps(tools_info, ensure_ascii=False, indent=2)}

Input Data:
{json.dumps({k: str(v)[:100] for k, v in data.items()}, ensure_ascii=False, indent=2)}

Please create an execution plan in JSON format:

{{
    "reasoning": "Why adopt this execution plan? What factors were considered?",
    "steps": [
        {{
            "step_id": "step_1",
            "tool_name": "Tool name to use (must be one of the available tools)",
            "inputs": {{
                "param1": "value1 or {{from_step_X}} (if from previous step output)",
                "param2": "value2"
            }},
            "expected_output": "Expected output of this step",
            "dependencies": ["step_X"]  // Prerequisite steps
        }},
        ...
    ]
}}

Important Tips:
1. Steps should be arranged in execution order
2. If a step needs output from previous steps, use {{from_step_X}} in inputs
3. Ensure all tool names are in the available tools list
4. Consider the logical flow of the task

**IMPORTANT**: Output ONLY pure JSON. Do not add any explanatory text. Do not use Markdown code blocks.
Ensure the first character is {{ and the last character is }}."""

        system_prompt = "You are a professional task planning expert, skilled at analyzing task requirements and planning efficient execution steps."

        try:
            # 创建MLLMRequest对象
            request = MLLMRequest(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                model_name=self.mllm.config.default_model,
                api_endpoint=self.mllm.config.base_url or "",
                prompt=planning_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=16000,  # 不限制输出，让模型充分表达
                task=AnalysisTask.CAPTION
            )

            response = self.mllm.call(request)

            # 解析JSON响应
            response_text = response.text.strip()

            # 调试：打印实际响应（前500字符）
            print(f"      [调试] Planning API响应（前500字符）: {response_text[:500]}...")

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

            plan_data = json.loads(response_text)

            # 构建PlanStep对象
            steps = []
            for step_data in plan_data.get("steps", []):
                step = PlanStep(
                    step_id=step_data.get("step_id", f"step_{len(steps)+1}"),
                    tool_name=step_data.get("tool_name", ""),
                    tool_id="",  # 稍后填充
                    inputs=step_data.get("inputs", {}),
                    expected_output=step_data.get("expected_output", ""),
                    dependencies=step_data.get("dependencies", [])
                )
                steps.append(step)

            # 创建AgentPlan
            plan = AgentPlan(
                plan_id=f"plan_{uuid.uuid4().hex[:8]}",
                task_description=task,
                steps=steps,
                available_tools=tools,
                reasoning=plan_data.get("reasoning", ""),
                status=PlanStatus.PLANNING
            )

            # 记录行动
            action = AgentAction(
                action_id=f"action_{uuid.uuid4().hex[:8]}",
                agent_id=self.agent_id,
                agent_type=AgentType.TOOL_USER,
                action_type=ActionType.PLAN,
                inputs={"task": task, "num_tools": len(tools)},
                outputs={"plan": plan.to_dict()},
                reasoning="创建任务执行计划",
                tokens_used=response.total_tokens,
                cost_usd=response.cost_usd,
                duration_ms=(time.time() - start_time) * 1000,
                status="completed"
            )
            self.actions.append(action)

            # 更新计划统计
            plan.total_tokens += response.total_tokens
            plan.total_cost += response.cost_usd

            return plan

        except Exception as e:
            print(f"    ⚠️ 计划创建失败: {e}")
            # 返回默认计划（使用所有工具按顺序执行）
            steps = []
            for i, tool in enumerate(tools, 1):
                step = PlanStep(
                    step_id=f"step_{i}",
                    tool_name=tool.tool_name,
                    tool_id=tool.tool_id,
                    expected_output=f"Output from {tool.tool_name}",
                    dependencies=[f"step_{i-1}"] if i > 1 else []
                )
                steps.append(step)

            return AgentPlan(
                plan_id=f"plan_{uuid.uuid4().hex[:8]}",
                task_description=task,
                steps=steps,
                available_tools=tools,
                reasoning="默认计划：按顺序使用所有工具",
                status=PlanStatus.PLANNING
            )

    def _select_tool(self, tool_name: str, tools: List[Tool]) -> Optional[Tool]:
        """
        选择工具 - 根据工具名称选择工具

        Args:
            tool_name: 工具名称
            tools: 可用工具列表

        Returns:
            选中的工具，如果未找到则返回None
        """
        for tool in tools:
            if tool.tool_name == tool_name:
                return tool
        return None

    def _prepare_inputs(
        self,
        step: PlanStep,
        execution_results: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        准备工具输入 - 从数据和前置步骤结果中准备输入

        处理两种输入来源：
        1. 直接从data中获取（如video_path, question）
        2. 从前置步骤的输出中获取（标记为{from_step_X}）

        Args:
            step: 当前步骤
            execution_results: 已执行步骤的结果
            data: 原始输入数据

        Returns:
            准备好的输入参数
        """
        inputs = {}

        for key, value in step.inputs.items():
            # 检查是否引用了前置步骤的输出
            if isinstance(value, str) and value.startswith("{from_step_"):
                # 提取步骤ID
                step_id = value.strip("{}")
                if step_id in execution_results:
                    # 获取前置步骤的输出
                    prev_result = execution_results[step_id]
                    if isinstance(prev_result, dict) and "output" in prev_result:
                        inputs[key] = prev_result["output"]
                    else:
                        inputs[key] = prev_result
                else:
                    print(f"      ⚠️ 前置步骤 {step_id} 的结果不可用")
                    inputs[key] = None
            elif value in data:
                # 从原始数据中获取
                inputs[key] = data[value]
            else:
                # 直接使用值
                inputs[key] = value

        return inputs

    def _execute_tool(self, tool: Tool, inputs: Dict[str, Any], atomic_ops: Any) -> Any:
        """
        执行工具 - 调用Tool Executor执行工具

        Args:
            tool: 要执行的工具
            inputs: 输入参数
            atomic_ops: 原子操作实现

        Returns:
            执行结果
        """
        start_time = time.time()

        try:
            # 调用Tool Executor执行工具
            result = self.tool_executor.execute(tool, inputs, atomic_ops)

            # 记录行动
            action = AgentAction(
                action_id=f"action_{uuid.uuid4().hex[:8]}",
                agent_id=self.agent_id,
                agent_type=AgentType.TOOL_USER,
                action_type=ActionType.USE_TOOL,
                tool=tool,
                inputs=inputs,
                outputs=result,
                reasoning=f"使用工具 {tool.tool_name} 执行任务",
                tokens_used=result.get("tokens_used", 0) if isinstance(result, dict) else 0,
                cost_usd=result.get("cost_usd", 0.0) if isinstance(result, dict) else 0.0,
                duration_ms=(time.time() - start_time) * 1000,
                status="completed"
            )
            self.actions.append(action)

            return result

        except Exception as e:
            # 记录失败的行动
            action = AgentAction(
                action_id=f"action_{uuid.uuid4().hex[:8]}",
                agent_id=self.agent_id,
                agent_type=AgentType.TOOL_USER,
                action_type=ActionType.USE_TOOL,
                tool=tool,
                inputs=inputs,
                outputs={},
                reasoning=f"尝试使用工具 {tool.tool_name}，但失败了",
                duration_ms=(time.time() - start_time) * 1000,
                status="failed",
                error_message=str(e)
            )
            self.actions.append(action)

            raise

    def _aggregate_results(self, execution_results: Dict[str, Any], plan: AgentPlan) -> Any:
        """
        整合结果 - 整合所有步骤的结果

        从最后一个成功步骤获取结果作为最终输出。

        Args:
            execution_results: 所有步骤的执行结果
            plan: 执行计划

        Returns:
            最终结果
        """
        # 找到最后一个成功的步骤
        for step in reversed(plan.steps):
            if step.status == "completed" and step.step_id in execution_results:
                result = execution_results[step.step_id]
                if isinstance(result, dict) and "output" in result:
                    return result["output"]
                return result

        # 如果没有成功的步骤，返回错误信息
        return {"error": "No successful execution steps"}

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
