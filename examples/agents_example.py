"""
Agents使用示例

演示如何使用ToolCreatorAgent和ToolUserAgent
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import (
    MLLMClient,
    MLLMClientConfig,
    ToolCreatorAgent,
    ToolCreationRequest,
    ToolUserAgent,
    VideoAnalysisRequest
)

from experiments import (
    AnalysisTask,
    Frame,
    Segment,
    TimeSpan
)


def example_1_mllm_client():
    """示例1: MLLM客户端基本使用"""
    print("\n" + "="*60)
    print("示例1: MLLM客户端基本使用")
    print("="*60)

    # 检查API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠ 跳过示例（需要OPENAI_API_KEY环境变量）")
        print("设置方法: export OPENAI_API_KEY='your-api-key'")
        return

    # 创建客户端
    client = MLLMClient(MLLMClientConfig(
        api_key=os.getenv("OPENAI_API_KEY"),
        default_model=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4-turbo-preview")
    ))

    # 创建一个简单的请求
    from experiments import MLLMRequest

    request = MLLMRequest(
        request_id="req_001",
        model_name=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4-turbo-preview"),
        api_endpoint="https://api.openai.com/v1",
        prompt="请用一句话解释什么是多智能体系统？",
        temperature=0.7,
        max_tokens=200,
        task=AnalysisTask.OTHER
    )

    print(f"\n发送请求: {request.prompt}")
    print("注意: 这需要有效的OPENAI_API_KEY环境变量")

    # 调用API（需要有效的API key）
    try:
        response = client.call(request)

        if response.success:
            print(f"\n响应: {response.text}")
            print(f"Token使用: {response.total_tokens}")
            print(f"成本: ${response.cost_usd:.4f}")
        else:
            print(f"\n错误: {response.error_message}")

        # 获取统计
        stats = client.get_stats()
        print(f"\n客户端统计: {stats}")

    except Exception as e:
        print(f"\n示例跳过（需要API key）: {str(e)}")


def example_2_tool_creator_agent():
    """示例2: 工具创建Agent"""
    print("\n" + "="*60)
    print("示例2: 工具创建Agent")
    print("="*60)

    # 创建Agent（不需要API key也能演示结构）
    try:
        agent = ToolCreatorAgent(agent_id="creator_001")

        # 创建工具请求
        request = ToolCreationRequest(
            request_id="req_002",
            tool_name="extract_keyframes",
            tool_description="从视频中提取关键帧",
            input_requirements="输入：视频文件路径，采样间隔（秒）",
            output_requirements="输出：关键帧列表，每帧包含时间戳和图像数据",
            example_usage="extract_keyframes('video.mp4', interval=2.0)",
            constraints="支持常见视频格式（mp4, avi, mov）"
        )

        print(f"\n请求创建工具: {request.tool_name}")
        print(f"描述: {request.tool_description}")
        print("\n注意: 实际调用需要OPENAI_API_KEY")

        # 实际调用（需要API key）
        # result = agent.create_tool(request)
        # if result.success:
        #     print(f"\n生成的代码:\n{result.tool_code}")
        # else:
        #     print(f"\n错误: {result.error_message}")

        # 显示Agent状态
        stats = agent.get_stats()
        print(f"\nAgent状态:")
        print(f"  Agent ID: {stats['agent_id']}")
        print(f"  Agent名称: {stats['agent_name']}")
        print(f"  统计: {stats['stats']}")

    except Exception as e:
        print(f"\n示例跳过: {str(e)}")


def example_3_tool_user_agent():
    """示例3: 工具使用Agent - 帧分析"""
    print("\n" + "="*60)
    print("示例3: 工具使用Agent - 帧分析")
    print("="*60)

    try:
        agent = ToolUserAgent(agent_id="user_001")

        # 创建模拟帧数据
        frames = [
            Frame(
                frame_id="frame_001",
                video_id="vid_001",
                frame_index=0,
                timestamp_sec=0.0,
                image_path="https://example.com/frame1.jpg"  # 示例URL
            ),
            Frame(
                frame_id="frame_002",
                video_id="vid_001",
                frame_index=30,
                timestamp_sec=1.0,
                image_path="https://example.com/frame2.jpg"
            )
        ]

        # 创建分析请求
        request = VideoAnalysisRequest(
            request_id="req_003",
            task=AnalysisTask.CAPTION,
            frames=frames,
            prompt="请描述画面中的主要内容",
            temperature=0.7,
            max_tokens=500,
            max_frames=2
        )

        print(f"\n请求分析 {len(frames)} 帧")
        print(f"任务类型: {request.task.value}")
        print("\n注意: 实际调用需要OPENAI_API_KEY和有效的图像")

        # 实际调用（需要API key和真实图像）
        # result = agent.analyze(request)
        # if result.success:
        #     print(f"\n分析结果:")
        #     for caption in result.frame_captions:
        #         print(f"  帧{caption.frame_id}: {caption.caption}")
        # else:
        #     print(f"\n错误: {result.error_message}")

        # 显示Agent状态
        stats = agent.get_stats()
        print(f"\nAgent状态:")
        print(f"  Agent ID: {stats['agent_id']}")
        print(f"  统计: {stats['stats']}")

    except Exception as e:
        print(f"\n示例跳过: {str(e)}")


def example_4_tool_user_agent_segment():
    """示例4: 工具使用Agent - 片段分析"""
    print("\n" + "="*60)
    print("示例4: 工具使用Agent - 片段分析")
    print("="*60)

    try:
        agent = ToolUserAgent(agent_id="user_002")

        # 创建片段
        segment = Segment(
            segment_id="seg_001",
            video_id="vid_001",
            time_span=TimeSpan(start_sec=0.0, end_sec=10.0),
            segment_index=0,
            total_segments=10,
            start_frame=0,
            end_frame=300,
            num_frames=300
        )

        # 创建片段的关键帧
        frames = [
            Frame(
                frame_id=f"frame_{i:03d}",
                video_id="vid_001",
                frame_index=i * 100,
                timestamp_sec=i * 3.33,
                image_path=f"https://example.com/frame{i}.jpg"
            )
            for i in range(3)  # 3个关键帧
        ]

        # 创建分析请求
        request = VideoAnalysisRequest(
            request_id="req_004",
            task=AnalysisTask.CAPTION,
            segment=segment,
            frames=frames,
            prompt="",
            context_info="这是视频的第一个片段",
            temperature=0.7,
            max_tokens=1000,
            max_frames=5
        )

        print(f"\n请求分析片段:")
        print(f"  时间范围: {segment.time_span.start_sec}s - {segment.time_span.end_sec}s")
        print(f"  关键帧数: {len(frames)}")
        print("\n注意: 实际调用需要OPENAI_API_KEY和有效的图像")

        # 实际调用（需要API key和真实图像）
        # result = agent.analyze(request)
        # if result.success and result.segment_caption:
        #     caption = result.segment_caption
        #     print(f"\n片段描述: {caption.caption}")
        #     print(f"摘要: {caption.summary}")
        #     print(f"主要事件: {caption.main_events}")
        # else:
        #     print(f"\n错误: {result.error_message}")

    except Exception as e:
        print(f"\n示例跳过: {str(e)}")


def example_5_complete_workflow():
    """示例5: 完整工作流程"""
    print("\n" + "="*60)
    print("示例5: 完整工作流程（概念演示）")
    print("="*60)

    print("""
完整的长视频理解工作流程：

1. 视频预处理
   - 提取视频元数据（分辨率、帧率、时长等）
   - 将视频分段（每段10-30秒）
   - 从每段提取关键帧

2. 工具创建（可选）
   - 使用ToolCreatorAgent根据需求创建自定义工具
   - 例如：特定场景检测、对象追踪等

3. 片段分析
   - 使用ToolUserAgent分析每个片段
   - 为每个片段生成描述（SegmentCaption）
   - 提取关键信息（事件、对象、场景类型）

4. 整合理解
   - 收集所有片段的描述
   - 使用ToolUserAgent生成整体摘要
   - 构建完整的VideoUnderstanding对象

5. 交互式问答（可选）
   - 基于视频理解回答用户问题
   - 使用AnalysisTask.QA模式

成本考虑：
- GPT-4 Vision: ~$0.01/1K输入tokens, ~$0.03/1K输出tokens
- 一个10分钟视频（10个片段，每段5帧）
  预估: 100K输入tokens, 10K输出tokens
  成本: ~$1.3

优化策略：
- 减少每段的关键帧数量
- 使用较小的模型进行初步筛选
- 缓存重复的分析结果
- 批量处理以提高效率
""")


def main():
    """运行所有示例"""
    print("="*60)
    print("Agents使用示例")
    print("="*60)

    # 运行示例
    example_1_mllm_client()
    example_2_tool_creator_agent()
    example_3_tool_user_agent()
    example_4_tool_user_agent_segment()
    example_5_complete_workflow()

    print("\n" + "="*60)
    print("示例完成")
    print("="*60)
    print("\n注意:")
    print("1. 实际使用需要设置OPENAI_API_KEY环境变量")
    print("2. 需要安装openai包: pip install openai")
    print("3. 需要准备真实的视频帧数据")
    print("4. 注意API调用成本")


if __name__ == "__main__":
    main()
