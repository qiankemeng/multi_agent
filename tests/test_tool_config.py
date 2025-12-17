"""
工具配置系统测试
验证配置定义和管理功能的正确性
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import (
    ToolConfig,
    ToolParameter,
    ToolCategory,
    ParameterType,
    ToolStatus,
    TOOL_REGISTRY,
    register_tool,
    get_tool_config
)


def test_parameter_validation():
    """测试参数验证功能"""
    print("\n测试参数验证...")

    # 测试必需参数
    param1 = ToolParameter(
        name="required_param",
        type=ParameterType.STRING,
        description="必需参数",
        required=True
    )
    assert param1.validate("value") == True
    assert param1.validate(None) == False
    print("  ✓ 必需参数验证通过")

    # 测试枚举值
    param2 = ToolParameter(
        name="enum_param",
        type=ParameterType.STRING,
        description="枚举参数",
        enum=["option1", "option2", "option3"]
    )
    assert param2.validate("option1") == True
    assert param2.validate("invalid") == False
    print("  ✓ 枚举值验证通过")

    # 测试数值范围
    param3 = ToolParameter(
        name="number_param",
        type=ParameterType.INTEGER,
        description="数值参数",
        min_value=0,
        max_value=100
    )
    assert param3.validate(50) == True
    assert param3.validate(-1) == False
    assert param3.validate(101) == False
    print("  ✓ 数值范围验证通过")

    # 测试长度限制
    param4 = ToolParameter(
        name="string_param",
        type=ParameterType.STRING,
        description="字符串参数",
        min_length=3,
        max_length=10
    )
    assert param4.validate("hello") == True
    assert param4.validate("ab") == False
    assert param4.validate("this is too long") == False
    print("  ✓ 长度限制验证通过")


def test_tool_registry():
    """测试工具注册表功能"""
    print("\n测试工具注册表...")

    # 清空注册表
    TOOL_REGISTRY.clear()

    # 创建测试工具
    tool1 = ToolConfig(
        name="test_tool_1",
        display_name="测试工具1",
        description="这是第一个测试工具",
        category=ToolCategory.FILE_OPERATION,
        tags=["test", "file"]
    )

    tool2 = ToolConfig(
        name="test_tool_2",
        display_name="测试工具2",
        description="这是第二个测试工具",
        category=ToolCategory.API_CALL,
        tags=["test", "api"]
    )

    # 测试注册
    register_tool(tool1)
    register_tool(tool2)
    assert TOOL_REGISTRY.count() == 2
    print("  ✓ 工具注册通过")

    # 测试查询
    retrieved_tool = get_tool_config("test_tool_1")
    assert retrieved_tool is not None
    assert retrieved_tool.name == "test_tool_1"
    print("  ✓ 工具查询通过")

    # 测试按类别查询
    file_tools = TOOL_REGISTRY.list_by_category(ToolCategory.FILE_OPERATION)
    assert len(file_tools) == 1
    assert file_tools[0].name == "test_tool_1"
    print("  ✓ 按类别查询通过")

    # 测试按标签查询
    api_tools = TOOL_REGISTRY.list_by_tag("api")
    assert len(api_tools) == 1
    assert api_tools[0].name == "test_tool_2"
    print("  ✓ 按标签查询通过")

    # 测试搜索
    search_results = TOOL_REGISTRY.search("第一个")
    assert len(search_results) == 1
    assert search_results[0].name == "test_tool_1"
    print("  ✓ 搜索功能通过")

    # 测试更新
    success = TOOL_REGISTRY.update("test_tool_1", description="更新后的描述")
    assert success == True
    updated_tool = get_tool_config("test_tool_1")
    assert updated_tool.description == "更新后的描述"
    print("  ✓ 工具更新通过")

    # 测试删除
    success = TOOL_REGISTRY.unregister("test_tool_1")
    assert success == True
    assert TOOL_REGISTRY.count() == 1
    print("  ✓ 工具删除通过")


def test_tool_config_to_dict():
    """测试工具配置转字典功能"""
    print("\n测试配置转字典...")

    tool = ToolConfig(
        name="dict_test_tool",
        display_name="字典测试工具",
        description="用于测试转字典功能",
        category=ToolCategory.CUSTOM,
        parameters=[
            ToolParameter(
                name="param1",
                type=ParameterType.STRING,
                description="参数1",
                required=True
            )
        ],
        tags=["test"]
    )

    config_dict = tool.to_dict()

    assert config_dict["name"] == "dict_test_tool"
    assert config_dict["display_name"] == "字典测试工具"
    assert config_dict["category"] == "custom"
    assert len(config_dict["parameters"]) == 1
    assert config_dict["parameters"][0]["name"] == "param1"

    print("  ✓ 配置转字典功能通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始运行工具配置系统测试")
    print("=" * 60)

    try:
        test_parameter_validation()
        test_tool_registry()
        test_tool_config_to_dict()

        print("\n" + "=" * 60)
        print("✓ 所有测试通过!")
        print("=" * 60)
        return True

    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
