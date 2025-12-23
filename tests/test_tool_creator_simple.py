"""
简化测试 - 只测试Tool Creator的工具设计功能
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.multi_agent_system.tool_creator import ToolCreatorAgent
from agents.mllm_client import MLLMClient, MLLMClientConfig

def test_tool_design():
    """测试工具设计功能"""
    print("\n=== 测试Tool Creator工具设计 ===\n")

    # 创建agent
    mllm_client = MLLMClient(MLLMClientConfig())
    agent = ToolCreatorAgent(mllm_client=mllm_client)

    # 简单的任务
    task = """
任务类型: 视频问答

视频: test.mp4
问题: 视频中发生了什么？

要求: 分析视频并回答问题。
"""

    # 设计工具
    print(f"任务描述: {task}\n")
    tools = agent.design_tools(task)

    print(f"\n设计完成！共{len(tools)}个工具\n")

    for i, tool in enumerate(tools, 1):
        print(f"\n工具{i}: {tool.tool_name}")
        print(f"目的: {tool.purpose}")
        print(f"Prompt: {tool.prompt_template[:150]}...")
        print(f"原子操作: {tool.atomic_operations}")

if __name__ == "__main__":
    test_tool_design()
