"""
Token消耗统计测试

展示每个API调用的详细token使用情况
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from processors import VideoProcessor, AtomicOperationsImplementation, VideoQAPipeline

def test_token_statistics():
    """测试并展示详细的token统计"""
    print("\n" + "="*70)
    print("Token消耗统计测试")
    print("="*70)

    video_path = "data/videos/source.mp4"
    if not os.path.exists(video_path):
        print(f"✗ Video not found: {video_path}")
        return

    # 创建pipeline
    print("\n初始化pipeline...")
    video_processor = VideoProcessor()
    atomic_ops = AtomicOperationsImplementation(video_processor=video_processor)

    pipeline = VideoQAPipeline(
        atomic_ops=atomic_ops,
        config={
            "segment_duration_sec": 60.0,
            "frames_per_segment": 3,
            "max_segments": 3,
            "mllm_model": os.getenv("OPENAI_DEFAULT_MODEL", "gpt-5"),
            "temperature": 0.7,
            "max_tokens_per_segment": 4000,  # 上限，不限制输出
            "max_tokens_qa": 3000
        }
    )

    question = "What is happening in this video? Describe the main content and activities."

    print(f"\n{'='*70}")
    print("开始处理视频")
    print(f"{'='*70}")
    print(f"视频: {video_path}")
    print(f"问题: {question}")
    print(f"配置:")
    print(f"  - Segments: 3个")
    print(f"  - 每segment帧数: 3")
    print(f"  - max_tokens_per_segment: 4000 (上限)")
    print(f"  - max_tokens_qa: 3000 (上限)")
    print(f"{'='*70}")

    # 运行pipeline
    answer, experiment = pipeline.run_video_qa(video_path, question)

    # 详细统计
    print(f"\n{'='*70}")
    print("详细Token统计")
    print(f"{'='*70}")

    print(f"\n📊 总体统计:")
    print(f"  ├─ 总API调用: {experiment.total_api_calls} 次")
    print(f"  ├─ 总tokens: {experiment.total_tokens_used:,}")
    print(f"  ├─ 总成本: ${experiment.total_cost_usd:.4f}")
    print(f"  └─ 处理时间: {experiment.total_duration_ms/1000:.2f}秒")

    print(f"\n📈 平均统计:")
    if experiment.total_api_calls > 0:
        avg_tokens = experiment.total_tokens_used / experiment.total_api_calls
        avg_cost = experiment.total_cost_usd / experiment.total_api_calls
        avg_time = (experiment.total_duration_ms/1000) / experiment.total_api_calls
        print(f"  ├─ 平均tokens/调用: {avg_tokens:,.0f}")
        print(f"  ├─ 平均成本/调用: ${avg_cost:.4f}")
        print(f"  └─ 平均时间/调用: {avg_time:.2f}秒")

    print(f"\n🎯 API调用细分:")
    print(f"  ├─ Segment分析: 3 次 (每次处理3张图片)")
    print(f"  └─ 最终QA: 1 次 (基于segment summaries)")

    print(f"\n💰 成本估算:")
    print(f"  ├─ 本次测试 (3 segments): ${experiment.total_cost_usd:.4f}")
    segments_total = len(experiment.segments)
    if segments_total > 3:
        full_cost = (experiment.total_cost_usd / 3) * segments_total
        print(f"  └─ 完整视频 ({segments_total} segments): ~${full_cost:.4f} (估算)")

    print(f"\n📝 输出质量:")
    print(f"  ├─ 回答长度: {len(answer)} 字符")
    print(f"  ├─ 处理帧数: {len(experiment.frames)}")
    print(f"  └─ 处理segments: {len(experiment.segments)}")

    print(f"\n{'='*70}")
    print("回答内容")
    print(f"{'='*70}")
    print(f"\n问题: {question}")
    print(f"\n回答:\n{answer}")

    print(f"\n{'='*70}")
    print("Token效率分析")
    print(f"{'='*70}")
    tokens_per_frame = experiment.total_tokens_used / len(experiment.frames) if experiment.frames else 0
    tokens_per_segment = experiment.total_tokens_used / 3  # 只处理了3个segments
    print(f"  ├─ Tokens/帧: {tokens_per_frame:,.0f}")
    print(f"  ├─ Tokens/segment: {tokens_per_segment:,.0f}")
    print(f"  └─ 成本/segment: ${experiment.total_cost_usd/3:.4f}")

    print(f"\n✅ 测试完成！")

if __name__ == "__main__":
    test_token_statistics()
