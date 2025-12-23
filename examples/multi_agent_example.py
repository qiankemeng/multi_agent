"""
Multi-Agent System 测试示例

演示完整的multi-agent工作流程：
1. Tool Creator Agent 设计工具
2. Tool User Agent 使用工具完成任务
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.multi_agent_system import MultiAgentCoordinator
from processors.atomic_operations_impl import AtomicOperationsImplementation
from agents.mllm_client import MLLMClient, MLLMClientConfig


def test_multi_agent_videoqa():
    """
    测试multi-agent系统的视频问答功能
    """
    print("\n" + "="*70)
    print(" Multi-Agent System 测试 - 视频问答 ".center(70, "="))
    print("="*70 + "\n")

    # 视频和问题
    video_path = "data/videos/source.mp4"
    question = "视频中发生了什么？请详细描述主要内容和事件。"

    # 检查视频文件是否存在
    if not os.path.exists(video_path):
        print(f"⚠️ 视频文件不存在: {video_path}")
        print("请确保视频文件存在后再运行测试")
        return

    try:
        # 1. 初始化MLLM客户端
        print("📋 初始化系统...")
        mllm_config = MLLMClientConfig()
        mllm_client = MLLMClient(mllm_config)

        # 2. 初始化原子操作
        atomic_ops = AtomicOperationsImplementation(mllm_client=mllm_client)

        # 3. 创建Multi-Agent协调器
        coordinator = MultiAgentCoordinator(mllm_client=mllm_client)

        # 4. 执行任务
        print("✓ 系统初始化完成")
        print(f"\n视频: {video_path}")
        print(f"问题: {question}\n")

        session = coordinator.process(
            video_path=video_path,
            question=question,
            atomic_ops=atomic_ops,
            constraints=None
        )

        # 5. 输出详细结果
        print("\n" + "="*70)
        print(" 详细结果分析 ".center(70, "="))
        print("="*70 + "\n")

        if session.success:
            print("✓ 任务执行成功\n")

            # 工具设计分析
            print("📦 Tool Creator 设计的工具:")
            print("─" * 70)
            for i, tool in enumerate(session.designed_tools, 1):
                print(f"\n{i}. {tool.tool_name}")
                print(f"   目的: {tool.purpose}")
                print(f"   原子操作: {', '.join(tool.atomic_operations)}")
                print(f"\n   Prompt模板预览:")
                prompt_lines = tool.prompt_template.split('\n')[:5]
                for line in prompt_lines:
                    print(f"   {line}")
                if len(tool.prompt_template.split('\n')) > 5:
                    print(f"   ... (共 {len(tool.prompt_template.split('\\n'))} 行)")
                print(f"\n   System Prompt:")
                print(f"   {tool.system_prompt[:100]}...")

            # 执行计划分析
            print("\n\n📋 Tool User 的执行计划:")
            print("─" * 70)
            if session.execution_plan:
                print(f"推理: {session.execution_plan.reasoning}\n")

                for i, step in enumerate(session.execution_plan.steps, 1):
                    status_icon = "✓" if step.status == "completed" else "✗"
                    print(f"{i}. [{status_icon}] {step.tool_name}")
                    print(f"   预期输出: {step.expected_output}")
                    print(f"   状态: {step.status}")
                    if step.actual_output:
                        output_str = str(step.actual_output)
                        if len(output_str) > 150:
                            print(f"   实际输出: {output_str[:150]}...")
                        else:
                            print(f"   实际输出: {output_str}")
                    print()

            # 最终答案
            print("\n💬 最终答案:")
            print("─" * 70)
            if isinstance(session.final_result, str):
                print(session.final_result)
            elif isinstance(session.final_result, dict):
                for key, value in session.final_result.items():
                    print(f"{key}: {value}")
            else:
                print(session.final_result)

            # Agent行动追踪
            print("\n\n🔍 Agent行动追踪:")
            print("─" * 70)
            print(f"\nTool Creator 行动 ({len(session.tool_creator_actions)} 个):")
            for i, action in enumerate(session.tool_creator_actions, 1):
                print(f"  {i}. [{action.action_type.value}] {action.reasoning[:60]}...")
                print(f"     Tokens: {action.tokens_used}, Cost: ${action.cost_usd:.4f}")

            print(f"\nTool User 行动 ({len(session.tool_user_actions)} 个):")
            for i, action in enumerate(session.tool_user_actions, 1):
                print(f"  {i}. [{action.action_type.value}] {action.reasoning[:60]}...")
                print(f"     Tokens: {action.tokens_used}, Cost: ${action.cost_usd:.4f}")

        else:
            print("✗ 任务执行失败")
            print(f"错误: {session.final_result}")

        # 保存会话记录（可选）
        save_session_record(session)

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def save_session_record(session):
    """保存会话记录到JSON文件"""
    import json
    from datetime import datetime

    output_dir = Path("data/sessions")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"session_{session.session_id}_{timestamp}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)

    print(f"\n💾 会话记录已保存: {output_file}")


def test_simple_task():
    """
    测试简单任务（不需要视频）
    """
    print("\n" + "="*70)
    print(" Multi-Agent System 测试 - 简单任务 ".center(70, "="))
    print("="*70 + "\n")

    task_description = """
任务类型: 文本分析

任务: 分析一段文本并提取关键信息。

文本: "人工智能正在改变世界。从自动驾驶到医疗诊断，AI技术的应用越来越广泛。"

要求:
1. 识别主题
2. 提取关键实体
3. 总结主要观点
"""

    data = {
        "text": "人工智能正在改变世界。从自动驾驶到医疗诊断，AI技术的应用越来越广泛。"
    }

    try:
        # 初始化
        mllm_config = MLLMClientConfig()
        mllm_client = MLLMClient(mllm_config)
        atomic_ops = AtomicOperationsImplementation(mllm_client=mllm_client)

        # 创建协调器
        coordinator = MultiAgentCoordinator(mllm_client=mllm_client)

        # 执行任务
        session = coordinator.process_simple(
            task_description=task_description,
            data=data,
            atomic_ops=atomic_ops
        )

        # 输出结果
        print(f"\n任务状态: {'✓ 成功' if session.success else '✗ 失败'}")
        print(f"设计工具数: {len(session.designed_tools)}")
        print(f"\n最终结果:")
        print(session.final_result)

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 测试1: 视频问答（主要测试）
    test_multi_agent_videoqa()

    # 测试2: 简单任务（可选）
    # test_simple_task()
