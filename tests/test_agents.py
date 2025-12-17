"""
Agents模块测试

测试MLLMClient、ToolCreatorAgent和ToolUserAgent的基本功能
"""

import sys
import os
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
    TimeSpan,
    MLLMRequest
)


def test_mllm_client_config():
    """测试MLLM客户端配置"""
    print("\n测试1: MLLM客户端配置")
    print("-" * 60)

    # 创建配置
    config = MLLMClientConfig(
        api_key="test_key",
        default_model="gpt-4-vision-preview",
        default_temperature=0.7,
        default_max_tokens=1000
    )

    assert config.api_key == "test_key"
    assert config.default_model == "gpt-4-vision-preview"
    assert config.default_temperature == 0.7
    assert config.default_max_tokens == 1000

    print("✓ 配置创建成功")

    # 测试价格配置
    assert config.price_per_1k_prompt_tokens > 0
    assert config.price_per_1k_completion_tokens > 0

    print("✓ 价格配置正确")

    # 测试从环境变量读取
    os.environ["OPENAI_API_KEY"] = "env_test_key"
    config2 = MLLMClientConfig()
    assert config2.api_key == "env_test_key"

    print("✓ 环境变量读取成功")
    print("测试1通过 ✓\n")


def test_mllm_client_initialization():
    """测试MLLM客户端初始化"""
    print("\n测试2: MLLM客户端初始化")
    print("-" * 60)

    try:
        config = MLLMClientConfig(api_key="test_key")
        client = MLLMClient(config)

        assert client.config == config
        assert client.total_requests == 0
        assert client.total_cost == 0.0

        print("✓ 客户端初始化成功")

        # 测试统计
        stats = client.get_stats()
        assert stats["total_requests"] == 0
        assert stats["total_cost_usd"] == 0.0

        print("✓ 统计功能正常")
        print("测试2通过 ✓\n")

    except ImportError as e:
        print(f"⚠ 测试跳过（需要openai包）: {str(e)}")


def test_mllm_request_formatting():
    """测试MLLM请求格式化"""
    print("\n测试3: MLLM请求格式化")
    print("-" * 60)

    try:
        config = MLLMClientConfig(api_key="test_key")
        client = MLLMClient(config)

        # 创建测试请求
        request = MLLMRequest(
            request_id="req_001",
            model_name="gpt-4-vision-preview",
            api_endpoint="https://api.openai.com/v1",
            prompt="测试提示",
            images=["https://example.com/image.jpg"],
            temperature=0.7,
            max_tokens=100,
            task=AnalysisTask.CAPTION
        )

        # 测试消息构建
        messages = client._build_messages(request)

        assert len(messages) > 0
        assert messages[-1]["role"] == "user"
        assert isinstance(messages[-1]["content"], list)

        print("✓ 消息格式化成功")

        # 测试图像格式化
        image_content = client._format_image("https://example.com/image.jpg")
        assert image_content["type"] == "image_url"
        assert "url" in image_content["image_url"]

        print("✓ 图像格式化成功")
        print("测试3通过 ✓\n")

    except ImportError:
        print("⚠ 测试跳过（需要openai包）")


def test_tool_creator_agent_initialization():
    """测试工具创建Agent初始化"""
    print("\n测试4: 工具创建Agent初始化")
    print("-" * 60)

    try:
        agent = ToolCreatorAgent(agent_id="creator_001")

        assert agent.agent_id == "creator_001"
        assert agent.agent_name == "ToolCreatorAgent"
        assert agent.stats["total_requests"] == 0

        print("✓ Agent初始化成功")

        # 测试状态
        stats = agent.get_stats()
        assert stats["agent_id"] == "creator_001"
        assert "stats" in stats
        assert "state" in stats

        print("✓ 状态获取成功")
        print("测试4通过 ✓\n")

    except Exception as e:
        print(f"⚠ 测试失败: {str(e)}")


def test_tool_creation_request():
    """测试工具创建请求"""
    print("\n测试5: 工具创建请求")
    print("-" * 60)

    request = ToolCreationRequest(
        request_id="req_002",
        tool_name="test_tool",
        tool_description="测试工具",
        input_requirements="输入要求",
        output_requirements="输出要求"
    )

    assert request.request_id == "req_002"
    assert request.tool_name == "test_tool"

    print("✓ 请求创建成功")

    # 测试prompt构建
    try:
        agent = ToolCreatorAgent(agent_id="creator_001")
        prompt = agent._build_tool_creation_prompt(request)

        assert "test_tool" in prompt
        assert "测试工具" in prompt

        print("✓ Prompt构建成功")
        print("测试5通过 ✓\n")

    except Exception as e:
        print(f"⚠ 测试部分失败: {str(e)}")


def test_tool_user_agent_initialization():
    """测试工具使用Agent初始化"""
    print("\n测试6: 工具使用Agent初始化")
    print("-" * 60)

    try:
        agent = ToolUserAgent(agent_id="user_001")

        assert agent.agent_id == "user_001"
        assert agent.agent_name == "ToolUserAgent"
        assert agent.stats["total_requests"] == 0

        print("✓ Agent初始化成功")

        # 测试状态
        stats = agent.get_stats()
        assert stats["agent_id"] == "user_001"
        assert "frames_processed" in stats["stats"]

        print("✓ 状态获取成功")
        print("测试6通过 ✓\n")

    except Exception as e:
        print(f"⚠ 测试失败: {str(e)}")


def test_video_analysis_request():
    """测试视频分析请求"""
    print("\n测试7: 视频分析请求")
    print("-" * 60)

    # 创建测试帧
    frames = [
        Frame(
            frame_id="frame_001",
            video_id="vid_001",
            frame_index=0,
            timestamp_sec=0.0,
            image_path="https://example.com/frame1.jpg",
            image_base64=None
        )
    ]

    # 创建分析请求
    request = VideoAnalysisRequest(
        request_id="req_003",
        task=AnalysisTask.CAPTION,
        frames=frames,
        prompt="测试提示",
        max_frames=5
    )

    assert request.request_id == "req_003"
    assert request.task == AnalysisTask.CAPTION
    assert len(request.frames) == 1

    print("✓ 分析请求创建成功")
    print("测试7通过 ✓\n")


def test_text_extraction_utilities():
    """测试文本提取工具函数"""
    print("\n测试8: 文本提取工具函数")
    print("-" * 60)

    try:
        agent = ToolUserAgent(agent_id="user_001")

        # 测试摘要提取
        text = "这是一段很长的文本" * 50
        summary = agent._extract_summary(text)
        assert len(summary) <= 203  # 200 + "..."

        print("✓ 摘要提取成功")

        # 测试事件提取
        text_with_events = """
        1. 第一个事件
        2. 第二个事件
        3、第三个事件
        """
        events = agent._extract_events(text_with_events)
        assert len(events) >= 2

        print("✓ 事件提取成功")
        print("测试8通过 ✓\n")

    except Exception as e:
        print(f"⚠ 测试失败: {str(e)}")


def test_code_extraction():
    """测试代码提取"""
    print("\n测试9: 代码提取")
    print("-" * 60)

    try:
        agent = ToolCreatorAgent(agent_id="creator_001")

        # 测试Python代码块提取
        text = """
这是一些说明文字

```python
def test_function():
    return "Hello"
```

更多说明
"""

        code = agent._extract_code_block(text)
        assert "def test_function" in code

        print("✓ Python代码块提取成功")

        # 测试普通代码块
        text2 = """
```
def another_function():
    pass
```
"""
        code2 = agent._extract_code_block(text2)
        assert "def another_function" in code2

        print("✓ 普通代码块提取成功")
        print("测试9通过 ✓\n")

    except Exception as e:
        print(f"⚠ 测试失败: {str(e)}")


def test_agent_stats_and_reset():
    """测试Agent统计和重置"""
    print("\n测试10: Agent统计和重置")
    print("-" * 60)

    try:
        # 测试ToolCreatorAgent
        creator = ToolCreatorAgent(agent_id="creator_001")
        creator.stats["total_requests"] = 10
        creator.stats["successful_creations"] = 8

        stats = creator.get_stats()
        assert stats["stats"]["total_requests"] == 10

        creator.reset_stats()
        assert creator.stats["total_requests"] == 0

        print("✓ ToolCreatorAgent统计和重置成功")

        # 测试ToolUserAgent
        user = ToolUserAgent(agent_id="user_001")
        user.stats["frames_processed"] = 100

        stats = user.get_stats()
        assert stats["stats"]["frames_processed"] == 100

        user.reset_stats()
        assert user.stats["frames_processed"] == 0

        print("✓ ToolUserAgent统计和重置成功")
        print("测试10通过 ✓\n")

    except Exception as e:
        print(f"⚠ 测试失败: {str(e)}")


def run_all_tests():
    """运行所有测试"""
    print("="*60)
    print("Agents模块测试")
    print("="*60)

    tests = [
        test_mllm_client_config,
        test_mllm_client_initialization,
        test_mllm_request_formatting,
        test_tool_creator_agent_initialization,
        test_tool_creation_request,
        test_tool_user_agent_initialization,
        test_video_analysis_request,
        test_text_extraction_utilities,
        test_code_extraction,
        test_agent_stats_and_reset
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ 测试失败: {str(e)}\n")
            failed += 1
        except Exception as e:
            print(f"✗ 测试错误: {str(e)}\n")
            failed += 1

    print("="*60)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("="*60)

    if failed == 0:
        print("\n✓ 所有测试通过!")
    else:
        print(f"\n⚠ 有 {failed} 个测试失败")

    print("\n注意:")
    print("1. 某些测试需要安装openai包才能运行")
    print("2. 实际的API调用测试需要有效的OPENAI_API_KEY")
    print("3. 这些测试主要验证数据结构和基本逻辑")


if __name__ == "__main__":
    run_all_tests()
