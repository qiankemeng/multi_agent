"""
MVP原子操作示例

演示4个核心原子操作的基本使用
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from experiments import (
    VideoMeta,
    Segment,
    Frame,
    AtomicOperations
)


def example_print_operations():
    """打印所有原子操作的摘要"""
    print("\n" + "="*60)
    print("MVP原子操作示例")
    print("="*60 + "\n")

    AtomicOperations.print_operations_summary()


def example_operations_info():
    """获取操作信息"""
    print("\n所有操作:")
    for op in AtomicOperations.get_all_operations():
        print(f"  - {op}")

    print("\n支持的模型:")
    models = AtomicOperations.get_supported_models()
    for model_type, model_list in models.items():
        print(f"  {model_type}:")
        for model in model_list:
            print(f"    - {model}")

    print("\n操作签名示例:")
    print(f"  SAMPLE: {AtomicOperations.get_operation_signature('sample')}")
    print(f"  SEGMENT: {AtomicOperations.get_operation_signature('segment')}")
    print(f"  CALL_MODEL: {AtomicOperations.get_operation_signature('call_model')}")
    print(f"  BBOX: {AtomicOperations.get_operation_signature('bbox')}")


if __name__ == "__main__":
    example_print_operations()
    example_operations_info()
