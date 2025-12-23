"""
Phase 3 VideoQA Pipeline独立测试

测试VideoQAPipeline的所有组件和工作流
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from processors import (
    VideoProcessor,
    AtomicOperationsImplementation,
    VideoQAPipeline
)


def test_1_video_processor():
    """测试1: VideoProcessor基础功能"""
    print("\n" + "="*60)
    print("测试1: VideoProcessor基础功能")
    print("="*60)

    video_path = "data/videos/source.mp4"
    if not os.path.exists(video_path):
        print(f"✗ 测试视频不存在: {video_path}")
        return False

    try:
        processor = VideoProcessor()

        # 测试元数据提取
        print("\n[1.1] 测试元数据提取...")
        video_meta = processor.extract_metadata(video_path)
        print(f"  ✓ 视频ID: {video_meta.video_id}")
        print(f"  ✓ 时长: {video_meta.duration_sec:.2f}秒")
        print(f"  ✓ 分辨率: {video_meta.width}x{video_meta.height}")
        print(f"  ✓ 帧率: {video_meta.fps:.2f}fps")

        # 测试分段
        print("\n[1.2] 测试视频分段...")
        segments = processor.segment_video_fixed_duration(video_meta, duration_sec=60.0)
        print(f"  ✓ 生成分段: {len(segments)}个")
        print(f"  ✓ 第一段: {segments[0].time_span.start_sec}s - {segments[0].time_span.end_sec}s")

        # 测试帧采样
        print("\n[1.3] 测试帧采样...")
        frames = processor.sample_frames_uniform(
            video_path, video_meta, num_frames=3, segment=segments[0]
        )
        print(f"  ✓ 采样帧数: {len(frames)}帧")
        print(f"  ✓ 第一帧: {frames[0].timestamp_sec:.2f}s")

        # 验证帧文件存在
        for frame in frames:
            if not os.path.exists(frame.image_path):
                print(f"  ✗ 帧文件不存在: {frame.image_path}")
                return False
        print(f"  ✓ 所有帧文件已保存")

        print("\n✓ VideoProcessor测试通过")
        return True

    except Exception as e:
        print(f"\n✗ VideoProcessor测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_2_atomic_operations():
    """测试2: AtomicOperations基础功能"""
    print("\n" + "="*60)
    print("测试2: AtomicOperations基础功能")
    print("="*60)

    video_path = "data/videos/source.mp4"
    if not os.path.exists(video_path):
        print(f"✗ 测试视频不存在: {video_path}")
        return False

    try:
        processor = VideoProcessor()
        atomic_ops = AtomicOperationsImplementation(video_processor=processor)

        # 获取视频元数据
        video_meta = processor.extract_metadata(video_path)

        # 测试SEGMENT操作
        print("\n[2.1] 测试SEGMENT操作...")
        segments = atomic_ops.segment(
            video_meta=video_meta,
            strategy="fixed_duration",
            params={"duration_sec": 60.0}
        )
        print(f"  ✓ SEGMENT操作: 生成{len(segments)}个片段")

        # 测试SAMPLE操作
        print("\n[2.2] 测试SAMPLE操作...")
        # 从VideoMeta采样（使用timestamps方法）
        timestamps = [30.0, 60.0, 90.0]  # 在30s, 60s, 90s采样
        frames = atomic_ops.sample(
            source=video_meta,
            method="timestamps",
            params={"timestamps": timestamps}
        )
        print(f"  ✓ SAMPLE操作: 采样{len(frames)}帧")

        # 测试BBOX操作
        print("\n[2.3] 测试BBOX操作...")
        boxes = [
            {
                "bbox": [100, 100, 200, 200],
                "label": "测试对象",
                "confidence": 0.95,
                "color": "red"
            }
        ]
        annotated_frame = atomic_ops.bbox(frame=frames[0], boxes=boxes)
        print(f"  ✓ BBOX操作: 标注完成")
        print(f"  ✓ 输出路径: {annotated_frame.image_path}")

        # 测试CALL_MODEL操作（dry-run）
        print("\n[2.4] 测试CALL_MODEL操作（dry-run）...")
        response = atomic_ops.call_model(
            model_type="mllm",
            model_name="gpt-4-vision-preview",
            inputs={
                "prompt": "描述这张图片",
                "frames": [frames[0]],
                "system_prompt": "你是一个视频分析助手"
            },
            params={
                "temperature": 0.7,
                "max_tokens": 100
            }
        )
        print(f"  ✓ CALL_MODEL操作: {'成功' if response.success else '失败（预期）'}")
        if not response.success:
            print(f"  ℹ 错误信息: {response.error_message[:100]}...")

        print("\n✓ AtomicOperations测试通过")
        return True

    except Exception as e:
        print(f"\n✗ AtomicOperations测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_3_pipeline_configuration():
    """测试3: Pipeline配置系统"""
    print("\n" + "="*60)
    print("测试3: Pipeline配置系统")
    print("="*60)

    try:
        processor = VideoProcessor()
        atomic_ops = AtomicOperationsImplementation(video_processor=processor)

        # 测试默认配置
        print("\n[3.1] 测试默认配置...")
        pipeline1 = VideoQAPipeline(atomic_ops=atomic_ops)
        config1 = pipeline1.get_config()
        print(f"  ✓ 默认分段时长: {config1['segment_duration_sec']}秒")
        print(f"  ✓ 默认帧数: {config1['frames_per_segment']}帧/段")
        print(f"  ✓ 默认模型: {config1['mllm_model']}")

        # 测试自定义配置
        print("\n[3.2] 测试自定义配置...")
        custom_config = {
            "segment_duration_sec": 45.0,
            "frames_per_segment": 4,
            "max_segments": 5,
            "temperature": 0.5
        }
        pipeline2 = VideoQAPipeline(
            atomic_ops=atomic_ops,
            config=custom_config
        )
        config2 = pipeline2.get_config()
        print(f"  ✓ 自定义分段时长: {config2['segment_duration_sec']}秒")
        print(f"  ✓ 自定义帧数: {config2['frames_per_segment']}帧/段")
        print(f"  ✓ 最大片段数: {config2['max_segments']}")

        # 测试配置更新
        print("\n[3.3] 测试配置更新...")
        pipeline2.update_config({"temperature": 0.8})
        config3 = pipeline2.get_config()
        print(f"  ✓ 更新后温度: {config3['temperature']}")

        print("\n✓ Pipeline配置测试通过")
        return True

    except Exception as e:
        print(f"\n✗ Pipeline配置测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_4_pipeline_workflow_dryrun():
    """测试4: Pipeline完整工作流（Dry-run模式）"""
    print("\n" + "="*60)
    print("测试4: Pipeline完整工作流（Dry-run）")
    print("="*60)

    video_path = "data/videos/source.mp4"
    if not os.path.exists(video_path):
        print(f"✗ 测试视频不存在: {video_path}")
        return False

    try:
        processor = VideoProcessor()
        atomic_ops = AtomicOperationsImplementation(video_processor=processor)

        # 创建Pipeline（限制处理片段数以加快测试）
        pipeline = VideoQAPipeline(
            atomic_ops=atomic_ops,
            config={
                "segment_duration_sec": 60.0,
                "frames_per_segment": 2,
                "max_segments": 2,  # 只处理2个片段
                "max_tokens_per_segment": 100,
                "max_tokens_qa": 200
            }
        )

        question = "视频中发生了什么？"

        print(f"\n问题: {question}")
        print(f"视频: {video_path}")
        print("\n开始Pipeline测试...")

        # 运行Pipeline
        answer, experiment = pipeline.run_video_qa(
            video_path=video_path,
            question=question
        )

        # 验证结果
        print("\n[4.1] 验证实验记录...")
        print(f"  ✓ Run ID: {experiment.run_id}")
        print(f"  ✓ 状态: {experiment.status.value}")
        print(f"  ✓ 视频ID: {experiment.video_meta.video_id if experiment.video_meta else 'N/A'}")
        print(f"  ✓ 处理片段数: {len(experiment.segments)}")
        print(f"  ✓ 提取帧数: {len(experiment.frames)}")
        print(f"  ✓ API调用次数: {experiment.total_api_calls}")
        print(f"  ✓ Token使用: {experiment.total_tokens_used}")
        print(f"  ✓ 成本: ${experiment.total_cost_usd:.4f}")

        print("\n[4.2] 验证答案...")
        print(f"  ✓ 答案长度: {len(answer)}字符")
        print(f"  ✓ 答案内容: {answer[:100]}...")

        # 验证数据完整性
        assert experiment.run_id, "run_id不能为空"
        assert experiment.video_meta is not None, "video_meta不能为空"
        assert len(experiment.segments) > 0, "segments不能为空"
        assert len(experiment.frames) > 0, "frames不能为空"
        assert experiment.total_api_calls > 0, "API调用次数应该大于0"
        assert len(answer) > 0, "答案不能为空"

        print("\n✓ Pipeline工作流测试通过")
        return True

    except Exception as e:
        print(f"\n✗ Pipeline工作流测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_5_experiment_tracking():
    """测试5: 实验追踪系统"""
    print("\n" + "="*60)
    print("测试5: 实验追踪系统")
    print("="*60)

    video_path = "data/videos/source.mp4"
    if not os.path.exists(video_path):
        print(f"✗ 测试视频不存在: {video_path}")
        return False

    try:
        from experiments import VideoExperimentRun, ProcessingStatus
        from datetime import datetime

        processor = VideoProcessor()
        atomic_ops = AtomicOperationsImplementation(video_processor=processor)
        pipeline = VideoQAPipeline(
            atomic_ops=atomic_ops,
            config={"max_segments": 1, "frames_per_segment": 1}
        )

        print("\n[5.1] 运行实验...")
        answer, experiment = pipeline.run_video_qa(
            video_path=video_path,
            question="测试问题"
        )

        print("\n[5.2] 验证实验追踪数据...")

        # 检查必需字段
        assert experiment.run_id, "✗ run_id缺失"
        print(f"  ✓ run_id: {experiment.run_id}")

        assert experiment.experiment_name, "✗ experiment_name缺失"
        print(f"  ✓ experiment_name: {experiment.experiment_name}")

        assert experiment.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED], "✗ status错误"
        print(f"  ✓ status: {experiment.status.value}")

        assert experiment.start_time, "✗ start_time缺失"
        print(f"  ✓ start_time: {experiment.start_time}")

        assert experiment.end_time, "✗ end_time缺失"
        print(f"  ✓ end_time: {experiment.end_time}")

        # 检查统计数据
        print(f"  ✓ total_api_calls: {experiment.total_api_calls}")
        print(f"  ✓ total_tokens_used: {experiment.total_tokens_used}")
        print(f"  ✓ total_cost_usd: ${experiment.total_cost_usd:.4f}")

        # 检查处理数据
        print(f"  ✓ segments: {len(experiment.segments)}个")
        print(f"  ✓ frames: {len(experiment.frames)}个")

        # 验证时间逻辑
        if experiment.total_duration_ms:
            print(f"  ✓ total_duration_ms: {experiment.total_duration_ms:.2f}ms")
            start = datetime.fromisoformat(experiment.start_time)
            end = datetime.fromisoformat(experiment.end_time)
            duration_calculated = (end - start).total_seconds() * 1000
            assert abs(experiment.total_duration_ms - duration_calculated) < 100, "✗ 时长计算错误"

        print("\n✓ 实验追踪系统测试通过")
        return True

    except AssertionError as e:
        print(f"\n✗ 实验追踪系统测试失败: {str(e)}")
        return False
    except Exception as e:
        print(f"\n✗ 实验追踪系统测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("Phase 3 VideoQA Pipeline 独立测试套件")
    print("="*60)

    tests = [
        ("VideoProcessor基础功能", test_1_video_processor),
        ("AtomicOperations基础功能", test_2_atomic_operations),
        ("Pipeline配置系统", test_3_pipeline_configuration),
        ("Pipeline完整工作流", test_4_pipeline_workflow_dryrun),
        ("实验追踪系统", test_5_experiment_tracking),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name}异常: {str(e)}")
            results.append((test_name, False))

    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {test_name}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 所有测试通过！Phase 3实现完整且正确。")
    else:
        print(f"\n⚠️  有{total - passed}个测试失败，需要修复。")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
