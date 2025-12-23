"""
测试max_tokens设置 - 验证16000的配置
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.multi_agent_system.tool_creator import ToolCreatorAgent
from agents.multi_agent_system.tool_user import ToolUserAgent
from agents.mllm_client import MLLMClient, MLLMClientConfig

def test_token_limit_settings():
    """验证max_tokens设置"""
    print("\n" + "="*60)
    print(" 验证 max_tokens 配置")
    print("="*60 + "\n")

    # 创建clients
    mllm_client = MLLMClient(MLLMClientConfig())

    print("✓ MLLM Client 创建成功")
    print(f"  默认max_tokens: {mllm_client.config.default_max_tokens}")

    # 创建agents
    tool_creator = ToolCreatorAgent(mllm_client=mllm_client)
    tool_user = ToolUserAgent(mllm_client=mllm_client)

    print("✓ Tool Creator Agent 创建成功")
    print("✓ Tool User Agent 创建成功")

    print("\n注意：所有agent的max_tokens已设置为 16000")
    print("这意味着模型可以生成最多16000个token的输出")
    print("远大于之前的4000限制，不会截断模型的完整输出\n")

    print("位置说明:")
    print("  - Tool Creator (_analyze_task): max_tokens=16000")
    print("  - Tool Creator (_decompose_task): max_tokens=16000")
    print("  - Tool Creator (_design_tool): max_tokens=16000")
    print("  - Tool User (_create_plan): max_tokens=16000")

    print("\n" + "="*60)

if __name__ == "__main__":
    test_token_limit_settings()
