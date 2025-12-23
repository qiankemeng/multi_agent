"""
动态参数传递示例

展示如何在不同场景下使用不同的参数调用原子操作

关键点：
1. .env中的DEFAULT_*配置仅作为默认值
2. 原子操作完全支持动态参数
3. Tool User Agent可以根据任务需求传递不同参数
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from processors import VideoProcessor, AtomicOperationsImplementation


def scenario_1_quick_preview():
    """
    场景1：快速预览 - 使用少量帧，快速获得视频概览

    适用于：快速浏览视频内容，初步了解
    """
    print("\n" + "="*60)
    print("场景1：快速预览模式")
    print("="*60)

    video_path = "data/videos/source.mp4"
    if not os.path.exists(video_path):
        print(f"视频文件不存在: {video_path}")
        return

    processor = VideoProcessor()
    atomic_ops = AtomicOperationsImplementation(video_processor=processor)

    # 提取元数据
    video_meta = processor.extract_metadata(video_path)
    print(f"\n视频: {video_meta.duration_sec:.1f}秒")

    # 快速预览配置：
    # - 大片段（120秒）
    # - 少量帧（2帧/段）
    # - 只处理前3段

    print("\n快速预览配置：")
    print("  - 分段: 120秒/段")
    print("  - 采样: 2帧/段")
    print("  - 处理: 前3段")

    # SEGMENT操作 - 动态指定分段时长为120秒
    segments = atomic_ops.segment(
        video_meta=video_meta,
        strategy="fixed_duration",
        params={"duration_sec": 120.0}  # 覆盖默认值30秒
    )
    print(f"\n✓ 分段: 生成{len(segments)}个片段（120秒/段）")

    # 只处理前3段
    segments = segments[:3]

    # SAMPLE操作 - 动态指定采样2帧
    for i, segment in enumerate(segments, 1):
        frames = atomic_ops.sample(
            source=video_meta,
            method="timestamps",
            params={
                "timestamps": [
                    segment.time_span.start_sec + 30,  # 段开始后30秒
                    segment.time_span.end_sec - 30     # 段结束前30秒
                ]
            }
        )
        print(f"  片段{i} [{segment.time_span.start_sec:.0f}s-{segment.time_span.end_sec:.0f}s]: {len(frames)}帧")

    print("\n✓ 快速预览完成 - 6帧覆盖360秒视频")


def scenario_2_detailed_analysis():
    """
    场景2：详细分析 - 使用更多帧，深入理解内容

    适用于：需要精确理解视频内容的场景
    """
    print("\n" + "="*60)
    print("场景2：详细分析模式")
    print("="*60)

    video_path = "data/videos/source.mp4"
    if not os.path.exists(video_path):
        print(f"视频文件不存在: {video_path}")
        return

    processor = VideoProcessor()
    atomic_ops = AtomicOperationsImplementation(video_processor=processor)

    video_meta = processor.extract_metadata(video_path)
    print(f"\n视频: {video_meta.duration_sec:.1f}秒")

    # 详细分析配置：
    # - 小片段（30秒）
    # - 大量帧（10帧/段）
    # - 处理更多片段

    print("\n详细分析配置：")
    print("  - 分段: 30秒/段")
    print("  - 采样: 10帧/段")
    print("  - 处理: 前5段")

    # SEGMENT操作 - 动态指定分段时长为30秒
    segments = atomic_ops.segment(
        video_meta=video_meta,
        strategy="fixed_duration",
        params={"duration_sec": 30.0}  # 小片段，更细粒度
    )
    print(f"\n✓ 分段: 生成{len(segments)}个片段（30秒/段）")

    # 处理前5段
    segments = segments[:5]

    # SAMPLE操作 - 动态指定采样10帧
    for i, segment in enumerate(segments, 1):
        # 方法1：均匀采样10帧
        frames = atomic_ops.sample(
            source=video_meta,
            method="uniform",
            params={"num_frames": 10}  # 覆盖默认值5帧
        )
        print(f"  片段{i} [{segment.time_span.start_sec:.0f}s-{segment.time_span.end_sec:.0f}s]: {len(frames)}帧（均匀采样）")

    print("\n✓ 详细分析完成 - 50帧覆盖150秒视频")


def scenario_3_adaptive_sampling():
    """
    场景3：自适应采样 - 根据内容动态调整采样策略

    适用于：不同片段可能需要不同采样策略
    """
    print("\n" + "="*60)
    print("场景3：自适应采样模式")
    print("="*60)

    video_path = "data/videos/source.mp4"
    if not os.path.exists(video_path):
        print(f"视频文件不存在: {video_path}")
        return

    processor = VideoProcessor()
    atomic_ops = AtomicOperationsImplementation(video_processor=processor)

    video_meta = processor.extract_metadata(video_path)
    print(f"\n视频: {video_meta.duration_sec:.1f}秒")

    print("\n自适应采样配置：")
    print("  - 分段: 60秒/段")
    print("  - 采样: 根据片段位置动态调整")
    print("  - 处理: 前6段")

    # SEGMENT操作
    segments = atomic_ops.segment(
        video_meta=video_meta,
        strategy="fixed_duration",
        params={"duration_sec": 60.0}
    )
    print(f"\n✓ 分段: 生成{len(segments)}个片段（60秒/段）")

    # 处理前6段，根据位置动态调整采样策略
    segments = segments[:6]

    for i, segment in enumerate(segments, 1):
        # 自适应策略：
        # - 开头和结尾：多采样（重要信息通常在这里）
        # - 中间：少采样（可能是过渡内容）

        if i <= 2 or i >= 5:  # 开头或结尾
            num_frames = 8
            sampling_desc = "密集采样（开头/结尾）"
        else:  # 中间
            num_frames = 3
            sampling_desc = "稀疏采样（中间）"

        frames = atomic_ops.sample(
            source=video_meta,
            method="uniform",
            params={"num_frames": num_frames}  # 动态调整帧数
        )

        print(f"  片段{i} [{segment.time_span.start_sec:.0f}s-{segment.time_span.end_sec:.0f}s]: "
              f"{len(frames)}帧 - {sampling_desc}")

    print("\n✓ 自适应采样完成 - 31帧覆盖360秒视频")


def scenario_4_custom_timestamps():
    """
    场景4：自定义时间戳 - 精确指定需要分析的时间点

    适用于：已知关键时刻，需要精确分析特定时间点
    """
    print("\n" + "="*60)
    print("场景4：自定义时间戳模式")
    print("="*60)

    video_path = "data/videos/source.mp4"
    if not os.path.exists(video_path):
        print(f"视频文件不存在: {video_path}")
        return

    processor = VideoProcessor()
    atomic_ops = AtomicOperationsImplementation(video_processor=processor)

    video_meta = processor.extract_metadata(video_path)
    print(f"\n视频: {video_meta.duration_sec:.1f}秒")

    # 假设我们已知这些是关键时刻
    key_moments = [
        ("视频开始", 0.0),
        ("第一个转折", 120.0),
        ("重要场景", 300.0),
        ("高潮部分", 600.0),
        ("结尾总结", 900.0),
    ]

    print("\n自定义时间戳配置：")
    print("  - 精确指定5个关键时刻")
    print("  - 每个时刻采样前后各1秒的3帧")

    for label, timestamp in key_moments:
        # 为每个关键时刻采样3帧：时刻前1秒、时刻、时刻后1秒
        timestamps = [
            max(0, timestamp - 1.0),
            timestamp,
            min(video_meta.duration_sec, timestamp + 1.0)
        ]

        frames = atomic_ops.sample(
            source=video_meta,
            method="timestamps",
            params={"timestamps": timestamps}  # 精确指定时间戳
        )

        print(f"  {label} ({timestamp:.0f}s): {len(frames)}帧")

    print("\n✓ 自定义时间戳采样完成 - 15帧覆盖关键时刻")


def scenario_5_custom_segmentation():
    """
    场景5：自定义分段 - 根据内容结构自定义分段点

    适用于：视频有明确的结构（如章节、场景）
    """
    print("\n" + "="*60)
    print("场景5：自定义分段模式")
    print("="*60)

    video_path = "data/videos/source.mp4"
    if not os.path.exists(video_path):
        print(f"视频文件不存在: {video_path}")
        return

    processor = VideoProcessor()
    atomic_ops = AtomicOperationsImplementation(video_processor=processor)

    video_meta = processor.extract_metadata(video_path)
    print(f"\n视频: {video_meta.duration_sec:.1f}秒")

    # 假设视频有这样的结构
    chapter_breaks = [
        ("开场", 0, 180),      # 0-3分钟：开场
        ("主题1", 180, 480),   # 3-8分钟：第一个主题
        ("主题2", 480, 780),   # 8-13分钟：第二个主题
        ("主题3", 780, 1080),  # 13-18分钟：第三个主题
        ("总结", 1080, 1380),  # 18-23分钟：总结
    ]

    print("\n自定义分段配置：")
    print("  - 按章节结构分段（5个章节）")
    print("  - 每章节采样5帧")

    # SEGMENT操作 - 使用自定义断点
    custom_breakpoints = [break_time for _, break_time, _ in chapter_breaks[1:]]
    segments = atomic_ops.segment(
        video_meta=video_meta,
        strategy="custom",
        params={"breakpoints": custom_breakpoints}
    )

    print(f"\n✓ 分段: 生成{len(segments)}个片段（按章节）\n")

    # 为每个章节采样
    for (chapter_name, _, _), segment in zip(chapter_breaks, segments):
        frames = atomic_ops.sample(
            source=video_meta,
            method="uniform",
            params={"num_frames": 5}
        )

        duration = segment.time_span.end_sec - segment.time_span.start_sec
        print(f"  {chapter_name} [{segment.time_span.start_sec:.0f}s-{segment.time_span.end_sec:.0f}s, {duration:.0f}s]: {len(frames)}帧")

    print("\n✓ 自定义分段完成 - 25帧覆盖5个章节")


def main():
    """运行所有场景示例"""
    print("\n" + "="*80)
    print("动态参数传递示例 - 展示5种不同的使用场景")
    print("="*80)
    print("\n核心思想：相同的原子操作，不同的参数 → 适应不同的任务需求")

    try:
        scenario_1_quick_preview()       # 快速预览：大片段，少帧数
        scenario_2_detailed_analysis()   # 详细分析：小片段，多帧数
        scenario_3_adaptive_sampling()   # 自适应：根据位置动态调整
        scenario_4_custom_timestamps()   # 自定义：精确指定时间点
        scenario_5_custom_segmentation() # 自定义：按内容结构分段

        print("\n" + "="*80)
        print("总结")
        print("="*80)
        print("\n✓ 所有场景演示完成！")
        print("\n关键要点：")
        print("  1. ✅ 原子操作完全支持动态参数")
        print("  2. ✅ .env中的DEFAULT_*仅作为默认值")
        print("  3. ✅ Tool User Agent可以根据任务需求自由调整参数")
        print("  4. ✅ 同一个视频，不同的参数 → 不同的处理策略")
        print("  5. ✅ 灵活性最大化，适应各种场景")

        print("\n" + "="*80)
        print("参数传递优先级")
        print("="*80)
        print("\n调用时传递的params > .env中的DEFAULT_* > 代码中的硬编码默认值")
        print("\n示例：")
        print("  atomic_ops.sample(")
        print("      method=\"uniform\",")
        print("      params={\"num_frames\": 10}  ← 这个参数优先级最高")
        print("  )")

    except Exception as e:
        print(f"\n✗ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
