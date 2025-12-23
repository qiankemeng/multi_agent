"""
测试API的视觉功能

验证配置的API是否支持图像输入
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import MLLMClient, MLLMClientConfig
from experiments import MLLMRequest, AnalysisTask, Frame
import base64


def test_text_only():
    """测试1: 纯文本API调用"""
    print("\n" + "="*60)
    print("测试1: 纯文本API调用")
    print("="*60)

    client = MLLMClient(MLLMClientConfig(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        default_model=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-5")
    ))

    request = MLLMRequest(
        request_id="test_text",
        model_name=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-5"),
        api_endpoint=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        prompt="请回答：1+1等于几？",
        temperature=0.0,
        max_tokens=50,
        task=AnalysisTask.OTHER
    )

    print(f"模型: {request.model_name}")
    print(f"端点: {request.api_endpoint}")
    print(f"问题: {request.prompt}")

    try:
        response = client.call(request)

        if response.success:
            print(f"\n✓ 调用成功")
            print(f"  答案: {response.text}")
            print(f"  Tokens: {response.total_tokens}")
            print(f"  成本: ${response.cost_usd:.4f}")
            return True
        else:
            print(f"\n✗ 调用失败")
            print(f"  错误: {response.error_message}")
            return False

    except Exception as e:
        print(f"\n✗ 异常: {str(e)}")
        return False


def test_vision_with_image():
    """测试2: 带图像的API调用"""
    print("\n" + "="*60)
    print("测试2: 视觉API调用（带图像）")
    print("="*60)

    # 查找一个测试帧
    frames_dir = Path("data/temp/frames")
    if not frames_dir.exists():
        print("✗ 帧目录不存在")
        return False

    frame_files = list(frames_dir.glob("*.jpg"))
    if not frame_files:
        print("✗ 没有找到帧文件")
        return False

    test_frame_path = frame_files[0]
    print(f"测试图片: {test_frame_path}")

    # 创建Frame对象
    frame = Frame(
        frame_id="test_frame",
        video_id="test_video",
        frame_index=0,
        timestamp_sec=0.0,
        image_path=str(test_frame_path)
    )

    client = MLLMClient(MLLMClientConfig(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        default_model=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-5")
    ))

    request = MLLMRequest(
        request_id="test_vision",
        model_name=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-5"),
        api_endpoint=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        prompt="请描述这张图片中你看到了什么。",
        images=[frame.image_path],  # Pass image path string, not Frame object
        temperature=0.7,
        max_tokens=500,  # 增加到500，避免token限制
        task=AnalysisTask.CAPTION
    )

    print(f"模型: {request.model_name}")
    print(f"端点: {request.api_endpoint}")
    print(f"图片: {len(request.images)}张")

    try:
        response = client.call(request)

        if response.success:
            print(f"\n✓ 调用成功")
            print(f"  答案: {response.text}")
            print(f"  Tokens: {response.total_tokens}")
            print(f"  成本: ${response.cost_usd:.4f}")
            return True
        else:
            print(f"\n✗ 调用失败")
            print(f"  错误: {response.error_message}")
            return False

    except Exception as e:
        print(f"\n✗ 异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("API视觉功能测试")
    print("="*60)

    print(f"\n配置信息:")
    print(f"  API Key: {os.getenv('OPENAI_API_KEY', 'NOT SET')[:20]}...")
    print(f"  Base URL: {os.getenv('OPENAI_BASE_URL', 'NOT SET')}")
    print(f"  Model: {os.getenv('OPENAI_DEFAULT_MODEL', 'NOT SET')}")

    results = []

    # 测试1: 纯文本
    result1 = test_text_only()
    results.append(("纯文本API", result1))

    # 测试2: 视觉功能
    result2 = test_vision_with_image()
    results.append(("视觉API（带图像）", result2))

    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)

    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {test_name}")

    if all(r for _, r in results):
        print("\n✓ 所有测试通过！API支持视觉功能。")
    elif results[0][1]:
        print("\n⚠️  API支持文本但不支持视觉功能。")
        print("    这可能是因为：")
        print("    1. 模型不支持视觉功能（需要vision模型如gpt-4-vision-preview）")
        print("    2. API端点配置错误")
        print("    3. API提供商不支持vision功能")
    else:
        print("\n✗ API调用失败，请检查配置。")


if __name__ == "__main__":
    main()
