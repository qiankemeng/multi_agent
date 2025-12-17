"""
交互配置测试
验证交互相关数据结构的正确性
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import (
    MessageType,
    AgentRole,
    AgentStatus,
    ExecutionStatus,
    Priority,
    Message,
    ToolCallRequest,
    ToolCallResponse,
    Context,
    AgentState,
    InteractionConfig
)


def test_message_creation():
    """测试消息创建和基本属性"""
    print("\n测试消息创建...")

    msg = Message(
        message_type=MessageType.REQUEST,
        sender_id="agent_1",
        sender_role=AgentRole.TOOL_USER,
        receiver_id="agent_2",
        receiver_role=AgentRole.TOOL_CREATOR,
        content={"action": "test"},
        priority=Priority.HIGH
    )

    assert msg.message_id is not None
    assert msg.message_type == MessageType.REQUEST
    assert msg.sender_id == "agent_1"
    assert msg.receiver_id == "agent_2"
    assert msg.priority == Priority.HIGH
    assert msg.requires_response == True
    print("  ✓ 消息创建测试通过")

    # 测试to_dict
    msg_dict = msg.to_dict()
    assert msg_dict["message_type"] == "request"
    assert msg_dict["sender_id"] == "agent_1"
    print("  ✓ 消息转字典测试通过")


def test_tool_call_request():
    """测试工具调用请求"""
    print("\n测试工具调用请求...")

    request = ToolCallRequest(
        tool_name="calculator",
        parameters={"x": 1, "y": 2},
        caller_id="user_agent",
        context_id="ctx_001",
        timeout_seconds=10
    )

    assert request.request_id is not None
    assert request.tool_name == "calculator"
    assert request.parameters["x"] == 1
    assert request.caller_id == "user_agent"
    assert request.timeout_seconds == 10
    print("  ✓ 工具调用请求创建测试通过")

    request_dict = request.to_dict()
    assert request_dict["tool_name"] == "calculator"
    print("  ✓ 请求转字典测试通过")


def test_tool_call_response():
    """测试工具调用响应"""
    print("\n测试工具调用响应...")

    # 成功响应
    success_response = ToolCallResponse(
        request_id="req_001",
        status=ExecutionStatus.SUCCESS,
        result=42,
        execution_time_ms=100
    )

    assert success_response.response_id is not None
    assert success_response.request_id == "req_001"
    assert success_response.status == ExecutionStatus.SUCCESS
    assert success_response.result == 42
    assert success_response.is_success() == True
    print("  ✓ 成功响应测试通过")

    # 失败响应
    error_response = ToolCallResponse(
        request_id="req_002",
        status=ExecutionStatus.FAILED,
        error_message="工具执行失败",
        error_type="RuntimeError"
    )

    assert error_response.status == ExecutionStatus.FAILED
    assert error_response.is_success() == False
    assert error_response.error_message == "工具执行失败"
    print("  ✓ 失败响应测试通过")


def test_context_management():
    """测试上下文管理"""
    print("\n测试上下文管理...")

    context = Context(
        max_history_length=5,
        participants=["agent_1", "agent_2"]
    )

    assert context.context_id is not None
    assert len(context.message_history) == 0
    assert len(context.participants) == 2
    print("  ✓ 上下文创建测试通过")

    # 添加消息
    for i in range(3):
        msg = Message(
            sender_id=f"agent_{i}",
            receiver_id=f"agent_{i+1}",
            content=f"message_{i}"
        )
        context.add_message(msg)

    assert len(context.message_history) == 3
    print("  ✓ 添加消息测试通过")

    # 测试历史限制
    for i in range(5):
        msg = Message(content=f"msg_{i}")
        context.add_message(msg)

    assert len(context.message_history) == 5  # 应该被限制在max_history_length
    print("  ✓ 历史长度限制测试通过")

    # 获取最近消息
    recent = context.get_recent_messages(count=2)
    assert len(recent) == 2
    print("  ✓ 获取最近消息测试通过")

    # 状态管理
    context.update_state("key1", "value1")
    assert context.get_state("key1") == "value1"
    assert context.get_state("nonexistent", "default") == "default"
    print("  ✓ 状态管理测试通过")

    # 工具调用记录
    request = ToolCallRequest(
        tool_name="test_tool",
        caller_id="agent_1",
        context_id=context.context_id
    )
    response = ToolCallResponse(
        request_id=request.request_id,
        status=ExecutionStatus.SUCCESS,
        result="ok"
    )
    context.add_tool_call(request, response)
    assert len(context.tool_call_history) == 1
    print("  ✓ 工具调用记录测试通过")


def test_agent_state():
    """测试Agent状态"""
    print("\n测试Agent状态...")

    agent = AgentState(
        agent_id="agent_001",
        agent_name="测试Agent",
        agent_role=AgentRole.TOOL_USER,
        capabilities=["cap1", "cap2"],
        available_tools=["tool1"]
    )

    assert agent.agent_id == "agent_001"
    assert agent.status == AgentStatus.IDLE
    assert len(agent.capabilities) == 2
    print("  ✓ Agent状态创建测试通过")

    # 更新状态
    agent.update_status(AgentStatus.BUSY, "正在工作")
    assert agent.status == AgentStatus.BUSY
    assert agent.status_message == "正在工作"
    print("  ✓ 状态更新测试通过")

    # 可用性检查
    assert agent.is_available() == False
    agent.update_status(AgentStatus.IDLE)
    assert agent.is_available() == True
    print("  ✓ 可用性检查测试通过")

    # 转字典
    agent_dict = agent.to_dict()
    assert agent_dict["agent_id"] == "agent_001"
    assert agent_dict["status"] == "idle"
    print("  ✓ Agent转字典测试通过")


def test_interaction_config():
    """测试交互配置"""
    print("\n测试交互配置...")

    config = InteractionConfig(
        message_queue_size=1000,
        message_timeout_seconds=30,
        max_concurrent_tool_calls=10
    )

    assert config.message_queue_size == 1000
    assert config.message_timeout_seconds == 30
    assert config.max_concurrent_tool_calls == 10
    print("  ✓ 交互配置创建测试通过")

    config_dict = config.to_dict()
    assert config_dict["message_queue_size"] == 1000
    print("  ✓ 配置转字典测试通过")


def test_message_chaining():
    """测试消息链"""
    print("\n测试消息链...")

    # 创建消息链
    msg1 = Message(
        message_type=MessageType.REQUEST,
        sender_id="agent_1",
        receiver_id="agent_2",
        content="请求1"
    )

    msg2 = Message(
        message_type=MessageType.RESPONSE,
        sender_id="agent_2",
        receiver_id="agent_1",
        content="响应1",
        parent_message_id=msg1.message_id
    )

    msg3 = Message(
        message_type=MessageType.REQUEST,
        sender_id="agent_1",
        receiver_id="agent_2",
        content="请求2",
        parent_message_id=msg2.message_id
    )

    assert msg2.parent_message_id == msg1.message_id
    assert msg3.parent_message_id == msg2.message_id
    print("  ✓ 消息链测试通过")


def test_context_session_isolation():
    """测试上下文会话隔离"""
    print("\n测试上下文会话隔离...")

    ctx1 = Context()
    ctx2 = Context()

    # 不同的上下文应该有不同的ID
    assert ctx1.context_id != ctx2.context_id
    assert ctx1.session_id != ctx2.session_id
    print("  ✓ 上下文隔离测试通过")

    # 向不同上下文添加消息
    ctx1.add_message(Message(content="ctx1 message"))
    ctx2.add_message(Message(content="ctx2 message"))

    assert len(ctx1.message_history) == 1
    assert len(ctx2.message_history) == 1
    assert ctx1.message_history[0].content != ctx2.message_history[0].content
    print("  ✓ 上下文消息隔离测试通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始运行交互配置测试")
    print("=" * 60)

    try:
        test_message_creation()
        test_tool_call_request()
        test_tool_call_response()
        test_context_management()
        test_agent_state()
        test_interaction_config()
        test_message_chaining()
        test_context_session_isolation()

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
