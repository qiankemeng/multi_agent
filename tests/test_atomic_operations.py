"""
测试精简后的原子操作

演示MVP核心操作的使用
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments import (
    AtomicOperation,
    AtomicOperations,
    ProcessingStatus
)


def test_atomic_operations():
    """测试原子操作"""
    print("="*60)
    print("原子操作测试（MVP精简版）")
    print("="*60)

    # 1. 获取所有操作
    print("\n【所有原子操作】")
    operations = AtomicOperations.get_all_operations()
    print(f"共{len(operations)}个核心操作:")
    for i, op in enumerate(operations, 1):
        desc = AtomicOperations.get_operation_description(op)
        print(f"  {i}. {op}")
        print(f"     └─ {desc}")

    # 2. 创建操作实例
    print("\n【创建操作实例】")

    # 操作1: 视频分段
    op1 = AtomicOperation(
        operation_id="op_001",
        operation_name="segment_video_001",
        operation_type=AtomicOperations.SEGMENT_VIDEO,
        input_spec={"video_path": "string", "segment_duration": "int"},
        output_spec={"segments": "List[Segment]"},
        parameters={"duration": 30, "strategy": "fixed"}
    )
    print(f"✓ 创建操作: {op1.operation_name}")
    print(f"  类型: {op1.operation_type}")
    print(f"  状态: {op1.status.value}")

    # 操作2: 帧采样
    op2 = AtomicOperation(
        operation_id="op_002",
        operation_name="sample_frames_001",
        operation_type=AtomicOperations.SAMPLE_FRAMES,
        input_spec={"segment": "Segment"},
        output_spec={"frames": "List[Frame]"},
        parameters={"method": "uniform", "count": 5}
    )
    print(f"✓ 创建操作: {op2.operation_name}")

    # 操作3: 调用MLLM
    op3 = AtomicOperation(
        operation_id="op_003",
        operation_name="call_mllm_001",
        operation_type=AtomicOperations.CALL_MLLM_API,
        input_spec={"frames": "List[Frame]", "prompt": "string"},
        output_spec={"response": "MLLMResponse"}
    )
    print(f"✓ 创建操作: {op3.operation_name}")

    # 操作4: 生成描述
    op4 = AtomicOperation(
        operation_id="op_004",
        operation_name="generate_caption_001",
        operation_type=AtomicOperations.GENERATE_CAPTION,
        input_spec={"mllm_response": "MLLMResponse"},
        output_spec={"caption": "SegmentCaption"}
    )
    print(f"✓ 创建操作: {op4.operation_name}")

    # 操作5: 合并结果
    op5 = AtomicOperation(
        operation_id="op_005",
        operation_name="merge_results_001",
        operation_type=AtomicOperations.MERGE_RESULTS,
        input_spec={"captions": "List[SegmentCaption]"},
        output_spec={"understanding": "VideoUnderstanding"}
    )
    print(f"✓ 创建操作: {op5.operation_name}")

    # 3. 模拟执行流程
    print("\n【模拟执行流程】")
    operations_list = [op1, op2, op3, op4, op5]

    for i, op in enumerate(operations_list, 1):
        print(f"\n步骤{i}: {op.operation_name}")
        print(f"  操作类型: {op.operation_type}")
        print(f"  描述: {AtomicOperations.get_operation_description(op.operation_type)}")
        print(f"  输入: {list(op.input_spec.keys())}")
        print(f"  输出: {list(op.output_spec.keys())}")
        print(f"  参数: {op.parameters}")

    # 4. 完整工作流
    print("\n" + "="*60)
    print("MVP长视频理解工作流")
    print("="*60)
    print("""
1. 前置步骤（非原子操作）
   └─ 提取视频元数据 (VideoMeta)

2. SEGMENT_VIDEO
   └─ 将视频分割成多个片段

3. 对每个片段:
   ├─ SAMPLE_FRAMES
   │  └─ 从片段中采样关键帧
   │
   ├─ CALL_MLLM_API
   │  └─ 调用MLLM分析帧
   │
   └─ GENERATE_CAPTION
      └─ 生成片段描述

4. MERGE_RESULTS
   └─ 合并所有片段结果

5. 输出: VideoUnderstanding
""")

    print("="*60)
    print("测试完成 ✓")
    print("="*60)
    print("\n说明:")
    print("- 原子操作从16个精简到5个核心操作")
    print("- 视频元数据提取不再是原子操作（每个任务的前置步骤）")
    print("- 专注于MVP实验的最小必要操作集")


if __name__ == "__main__":
    test_atomic_operations()
