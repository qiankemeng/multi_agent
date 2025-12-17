"""
MVP实验变量测试
验证实验变量定义的正确性
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from experiments import (
    ToolCreationRequest,
    CreatedTool,
    TaskData,
    TaskExecution,
    ExperimentRun,
    ValidationResult,
    ToolType,
    TaskStatus,
    ExperimentPhase,
    MVPScenarios
)


def test_tool_creation_request():
    """测试工具创建请求"""
    print("\n测试工具创建请求...")

    request = ToolCreationRequest(
        request_id="req_001",
        tool_type=ToolType.STRING_TRANSFORM,
        tool_name="string_reverser",
        description="反转输入的字符串",
        requirements={"function": "reverse_string"},
        input_spec={"text": "string"},
        output_spec={"reversed_text": "string"},
        requester_id="tool_user_001"
    )

    assert request.request_id == "req_001"
    assert request.tool_type == ToolType.STRING_TRANSFORM
    assert request.tool_name == "string_reverser"
    print("  ✓ 工具创建请求测试通过")

    # 测试to_dict
    request_dict = request.to_dict()
    assert request_dict["tool_type"] == "string_transform"
    print("  ✓ to_dict测试通过")


def test_created_tool():
    """测试创建的工具"""
    print("\n测试创建的工具...")

    tool = CreatedTool(
        tool_id="tool_001",
        request_id="req_001",
        tool_name="string_reverser",
        tool_type=ToolType.STRING_TRANSFORM,
        implementation_code="def reverse(text): return text[::-1]",
        implementation_function=lambda text: text[::-1],
        input_parameters={"text": "string"},
        output_format={"reversed_text": "string"},
        creator_id="tool_creator_001"
    )

    assert tool.tool_id == "tool_001"
    assert tool.tool_name == "string_reverser"
    assert tool.implementation_function("Hello") == "olleH"
    print("  ✓ 创建工具测试通过")
    print("  ✓ 工具函数执行测试通过")


def test_task_data():
    """测试任务数据"""
    print("\n测试任务数据...")

    task = TaskData(
        task_id="task_001",
        data_type="text",
        input_data="Hello World",
        tool_name="string_reverser",
        description="反转字符串测试",
        expected_output="dlroW olleH"
    )

    assert task.task_id == "task_001"
    assert task.input_data == "Hello World"
    assert task.expected_output == "dlroW olleH"
    print("  ✓ 任务数据测试通过")


def test_task_execution():
    """测试任务执行"""
    print("\n测试任务执行...")

    execution = TaskExecution(
        execution_id="exec_001",
        task_id="task_001",
        tool_id="tool_001",
        tool_name="string_reverser",
        status=TaskStatus.COMPLETED,
        duration_ms=50.2,
        output_data="dlroW olleH",
        executor_id="tool_user_001"
    )

    assert execution.execution_id == "exec_001"
    assert execution.status == TaskStatus.COMPLETED
    assert execution.output_data == "dlroW olleH"
    print("  ✓ 任务执行测试通过")


def test_experiment_run():
    """测试实验运行"""
    print("\n测试实验运行...")

    experiment = ExperimentRun(
        run_id="run_001",
        experiment_name="string_reverser_test",
        description="测试字符串反转工具",
        agents={
            "tool_user_001": "工具使用Agent",
            "tool_creator_001": "工具创建Agent"
        }
    )

    assert experiment.run_id == "run_001"
    assert experiment.current_phase == ExperimentPhase.INITIALIZATION
    assert len(experiment.agents) == 2
    print("  ✓ 实验运行测试通过")

    # 更新阶段
    experiment.current_phase = ExperimentPhase.TOOL_REQUEST
    experiment.phases_completed.append("initialization")
    assert ExperimentPhase.TOOL_REQUEST == experiment.current_phase
    print("  ✓ 阶段更新测试通过")


def test_validation_result():
    """测试验证结果"""
    print("\n测试验证结果...")

    validation = ValidationResult(
        validation_id="val_001",
        execution_id="exec_001",
        expected_output="dlroW olleH",
        actual_output="dlroW olleH",
        passed=True,
        match_score=1.0
    )

    assert validation.validation_id == "val_001"
    assert validation.passed == True
    assert validation.match_score == 1.0
    print("  ✓ 验证结果测试通过")


def test_mvp_scenarios():
    """测试预定义场景"""
    print("\n测试预定义场景...")

    # 场景1: 字符串反转
    scenario1 = MVPScenarios.get_string_reverser_scenario()
    assert scenario1["name"] == "string_reverser"
    assert len(scenario1["test_data"]) == 3
    assert scenario1["test_data"][0]["input"] == "Hello"
    assert scenario1["test_data"][0]["expected"] == "olleH"
    print("  ✓ 字符串反转场景测试通过")

    # 场景2: 大写转换
    scenario2 = MVPScenarios.get_uppercase_converter_scenario()
    assert scenario2["name"] == "uppercase_converter"
    assert scenario2["test_data"][0]["input"] == "hello"
    assert scenario2["test_data"][0]["expected"] == "HELLO"
    print("  ✓ 大写转换场景测试通过")

    # 场景3: 单词计数
    scenario3 = MVPScenarios.get_word_counter_scenario()
    assert scenario3["name"] == "word_counter"
    assert scenario3["test_data"][0]["input"] == "Hello World"
    assert scenario3["test_data"][0]["expected"] == 2
    print("  ✓ 单词计数场景测试通过")


def test_complete_workflow():
    """测试完整的工作流程"""
    print("\n测试完整工作流程...")

    # 1. 创建实验
    experiment = ExperimentRun(
        run_id="run_workflow",
        experiment_name="complete_test"
    )
    print("  ✓ 步骤1: 创建实验")

    # 2. 创建工具请求
    request = ToolCreationRequest(
        request_id="req_workflow",
        tool_type=ToolType.STRING_TRANSFORM,
        tool_name="test_tool",
        description="测试工具",
        requirements={},
        input_spec={"text": "string"},
        output_spec={"result": "string"}
    )
    experiment.tool_requests.append(request.request_id)
    print("  ✓ 步骤2: 创建工具请求")

    # 3. 创建工具
    tool = CreatedTool(
        tool_id="tool_workflow",
        request_id=request.request_id,
        tool_name=request.tool_name,
        tool_type=request.tool_type,
        implementation_code="lambda x: x",
        input_parameters=request.input_spec,
        output_format=request.output_spec
    )
    experiment.created_tools.append(tool.tool_id)
    print("  ✓ 步骤3: 创建工具")

    # 4. 创建任务
    task = TaskData(
        task_id="task_workflow",
        data_type="text",
        input_data="test",
        tool_name=tool.tool_name,
        expected_output="test"
    )
    experiment.tasks.append(task.task_id)
    print("  ✓ 步骤4: 创建任务")

    # 5. 执行任务
    execution = TaskExecution(
        execution_id="exec_workflow",
        task_id=task.task_id,
        tool_id=tool.tool_id,
        tool_name=tool.tool_name,
        status=TaskStatus.COMPLETED,
        output_data="test"
    )
    experiment.executions.append(execution.execution_id)
    print("  ✓ 步骤5: 执行任务")

    # 6. 验证结果
    validation = ValidationResult(
        validation_id="val_workflow",
        execution_id=execution.execution_id,
        expected_output=task.expected_output,
        actual_output=execution.output_data,
        passed=True,
        match_score=1.0
    )
    print("  ✓ 步骤6: 验证结果")

    # 验证实验记录完整性
    assert len(experiment.tool_requests) == 1
    assert len(experiment.created_tools) == 1
    assert len(experiment.tasks) == 1
    assert len(experiment.executions) == 1
    print("  ✓ 完整工作流程测试通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始运行MVP实验变量测试")
    print("=" * 60)

    try:
        test_tool_creation_request()
        test_created_tool()
        test_task_data()
        test_task_execution()
        test_experiment_run()
        test_validation_result()
        test_mvp_scenarios()
        test_complete_workflow()

        print("\n" + "=" * 60)
        print("✓ 所有测试通过!")
        print("=" * 60)
        return True

    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
