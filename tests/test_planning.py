"""
测试Tool User的Planning功能
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.multi_agent_system.tool_user import ToolUserAgent
from agents.multi_agent_system.types import Tool, ToolParameter
from agents.mllm_client import MLLMClient, MLLMClientConfig

def test_planning():
    """测试执行计划创建"""
    print("\n=== 测试Tool User Planning ===\n")

    # 创建agent
    mllm_client = MLLMClient(MLLMClientConfig())
    agent = ToolUserAgent(mllm_client=mllm_client)

    # 创建简单的工具列表
    tools = [
        Tool(
            tool_id="tool_1",
            tool_name="analyze_video",
            description="Analyze video content",
            purpose="Extract information from video",
            prompt_template="Analyze this video: {video_path}",
            system_prompt="You are a video analyst",
            parameters={
                "video_path": ToolParameter("video_path", "str", "Path to video", True)
            },
            atomic_operations=["SAMPLE", "CALL_MODEL"]
        ),
        Tool(
            tool_id="tool_2",
            tool_name="answer_question",
            description="Answer questions about video",
            purpose="Provide answers based on analysis",
            prompt_template="Answer this question: {question} based on: {analysis}",
            system_prompt="You are a QA assistant",
            parameters={
                "question": ToolParameter("question", "str", "Question to answer", True),
                "analysis": ToolParameter("analysis", "str", "Video analysis", True)
            },
            atomic_operations=["CALL_MODEL"]
        )
    ]

    # 简单任务
    task = "Analyze the video and answer the question: What happens in the video?"
    data = {
        "video_path": "test.mp4",
        "question": "What happens in the video?"
    }

    print(f"任务: {task}")
    print(f"可用工具: {len(tools)}")
    print(f"数据: {data}\n")

    # 创建计划
    print("创建执行计划...\n")
    plan = agent._create_plan(task, tools, data)

    print(f"\n计划创建完成!")
    print(f"推理: {plan.reasoning}")
    print(f"步骤数: {len(plan.steps)}\n")

    for i, step in enumerate(plan.steps, 1):
        print(f"步骤 {i}: {step.tool_name}")
        print(f"  输入: {step.inputs}")
        print(f"  预期输出: {step.expected_output}")
        print(f"  依赖: {step.dependencies}\n")

if __name__ == "__main__":
    test_planning()
