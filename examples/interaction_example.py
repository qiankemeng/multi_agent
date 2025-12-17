"""
交互配置示例
演示多Agent系统中如何使用交互变量进行通信

这个文件展示了：
1. 如何创建和发送消息
2. 如何发起工具调用请求和处理响应
3. 如何管理上下文
4. 如何追踪Agent状态
5. 完整的交互流程示例
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import (
    # 枚举
    MessageType,
    AgentRole,
    AgentStatus,
    ExecutionStatus,
    Priority,

    # 核心数据结构
    Message,
    ToolCallRequest,
    ToolCallResponse,
    Context,
    AgentState,
    InteractionConfig,

    # 协议
    InteractionProtocol
)
import json
import time


# ==================== 示例1: 消息传递 ====================

def demo_message_passing():
    """演示Agent之间的消息传递"""
    print("\n" + "=" * 60)
    print("示例1: 消息传递")
    print("=" * 60)

    # 创建一条从工具使用Agent发送给工具创建Agent的请求消息
    message = Message(
        message_type=MessageType.REQUEST,
        sender_id="tool_user_001",
        sender_role=AgentRole.TOOL_USER,
        receiver_id="tool_creator_001",
        receiver_role=AgentRole.TOOL_CREATOR,
        content={
            "action": "create_tool",
            "tool_type": "calculator",
            "requirements": "需要一个能进行数学计算的工具"
        },
        priority=Priority.HIGH,
        requires_response=True,
        timeout_seconds=30
    )

    print(f"\n创建的消息:")
    print(f"  消息ID: {message.message_id}")
    print(f"  类型: {message.message_type.value}")
    print(f"  发送者: {message.sender_id} ({message.sender_role.value})")
    print(f"  接收者: {message.receiver_id} ({message.receiver_role.value})")
    print(f"  优先级: {message.priority.value}")
    print(f"  内容: {json.dumps(message.content, ensure_ascii=False, indent=2)}")

    # 创建响应消息
    response_message = Message(
        message_type=MessageType.RESPONSE,
        sender_id="tool_creator_001",
        sender_role=AgentRole.TOOL_CREATOR,
        receiver_id="tool_user_001",
        receiver_role=AgentRole.TOOL_USER,
        content={
            "status": "success",
            "tool_name": "calculator",
            "message": "计算器工具已创建"
        },
        parent_message_id=message.message_id  # 关联到原始请求
    )

    print(f"\n响应消息:")
    print(f"  消息ID: {response_message.message_id}")
    print(f"  父消息ID: {response_message.parent_message_id}")
    print(f"  内容: {json.dumps(response_message.content, ensure_ascii=False, indent=2)}")


# ==================== 示例2: 工具调用流程 ====================

def demo_tool_call_flow():
    """演示完整的工具调用流程"""
    print("\n" + "=" * 60)
    print("示例2: 工具调用流程")
    print("=" * 60)

    # 1. 创建工具调用请求
    request = ToolCallRequest(
        tool_name="calculator",
        parameters={
            "expression": "2 + 3 * 4",
            "precision": 2
        },
        caller_id="tool_user_001",
        caller_role=AgentRole.TOOL_USER,
        context_id="ctx_001",
        priority=Priority.NORMAL,
        timeout_seconds=10
    )

    print(f"\n工具调用请求:")
    print(f"  请求ID: {request.request_id}")
    print(f"  工具名称: {request.tool_name}")
    print(f"  参数: {json.dumps(request.parameters, ensure_ascii=False, indent=2)}")
    print(f"  调用者: {request.caller_id}")
    print(f"  超时时间: {request.timeout_seconds}秒")

    # 2. 模拟工具执行
    print(f"\n执行工具...")
    start_time = time.time()
    time.sleep(0.1)  # 模拟执行时间
    result = 14  # 2 + 3 * 4 = 14
    end_time = time.time()
    execution_time = (end_time - start_time) * 1000  # 转换为毫秒

    # 3. 创建工具调用响应（成功）
    response = ToolCallResponse(
        request_id=request.request_id,
        status=ExecutionStatus.SUCCESS,
        result=result,
        execution_time_ms=execution_time,
        start_time=str(start_time),
        end_time=str(end_time)
    )

    print(f"\n工具调用响应:")
    print(f"  响应ID: {response.response_id}")
    print(f"  请求ID: {response.request_id}")
    print(f"  状态: {response.status.value}")
    print(f"  结果: {response.result}")
    print(f"  执行时间: {response.execution_time_ms:.2f}毫秒")
    print(f"  是否成功: {response.is_success()}")

    # 4. 演示失败情况
    print(f"\n演示失败情况:")
    error_response = ToolCallResponse(
        request_id=request.request_id,
        status=ExecutionStatus.FAILED,
        error_message="除零错误",
        error_type="ZeroDivisionError",
        error_traceback="Traceback (most recent call last):\n  ..."
    )

    print(f"  状态: {error_response.status.value}")
    print(f"  错误消息: {error_response.error_message}")
    print(f"  错误类型: {error_response.error_type}")
    print(f"  是否成功: {error_response.is_success()}")


# ==================== 示例3: 上下文管理 ====================

def demo_context_management():
    """演示上下文管理"""
    print("\n" + "=" * 60)
    print("示例3: 上下文管理")
    print("=" * 60)

    # 1. 创建上下文
    context = Context(
        max_history_length=5,  # 为了演示，设置较小的值
        participants=["tool_user_001", "tool_creator_001"]
    )

    print(f"\n创建上下文:")
    print(f"  上下文ID: {context.context_id}")
    print(f"  会话ID: {context.session_id}")
    print(f"  参与者: {context.participants}")

    # 2. 添加消息到上下文
    print(f"\n添加消息到上下文...")
    for i in range(3):
        msg = Message(
            message_type=MessageType.REQUEST if i % 2 == 0 else MessageType.RESPONSE,
            sender_id=f"agent_{i}",
            receiver_id=f"agent_{i+1}",
            content=f"这是第{i+1}条消息"
        )
        context.add_message(msg)
        print(f"  添加消息 {i+1}: {msg.content}")

    print(f"\n当前消息历史数量: {len(context.message_history)}")

    # 3. 更新共享状态
    print(f"\n更新共享状态...")
    context.update_state("current_tool", "calculator")
    context.update_state("task_progress", 0.5)
    context.update_state("last_result", 14)

    print(f"  共享状态: {json.dumps(context.shared_state, ensure_ascii=False, indent=2)}")

    # 4. 获取状态
    current_tool = context.get_state("current_tool")
    print(f"\n获取状态 'current_tool': {current_tool}")

    # 5. 添加工具调用记录
    request = ToolCallRequest(
        tool_name="calculator",
        parameters={"expression": "1+1"},
        caller_id="tool_user_001",
        context_id=context.context_id
    )
    response = ToolCallResponse(
        request_id=request.request_id,
        status=ExecutionStatus.SUCCESS,
        result=2
    )
    context.add_tool_call(request, response)

    print(f"\n工具调用历史数量: {len(context.tool_call_history)}")

    # 6. 获取最近消息
    recent_messages = context.get_recent_messages(count=2)
    print(f"\n最近2条消息:")
    for msg in recent_messages:
        print(f"  - {msg.content}")

    # 7. 导出上下文信息
    print(f"\n上下文摘要:")
    context_dict = context.to_dict()
    print(f"  {json.dumps(context_dict, ensure_ascii=False, indent=2)}")


# ==================== 示例4: Agent状态管理 ====================

def demo_agent_state():
    """演示Agent状态管理"""
    print("\n" + "=" * 60)
    print("示例4: Agent状态管理")
    print("=" * 60)

    # 1. 创建工具创建Agent的状态
    creator_state = AgentState(
        agent_id="tool_creator_001",
        agent_name="工具创建器",
        agent_role=AgentRole.TOOL_CREATOR,
        capabilities=["create_tool", "modify_tool", "delete_tool"],
        available_tools=[]
    )

    print(f"\n工具创建Agent:")
    print(f"  ID: {creator_state.agent_id}")
    print(f"  名称: {creator_state.agent_name}")
    print(f"  角色: {creator_state.agent_role.value}")
    print(f"  状态: {creator_state.status.value}")
    print(f"  能力: {creator_state.capabilities}")

    # 2. 创建工具使用Agent的状态
    user_state = AgentState(
        agent_id="tool_user_001",
        agent_name="工具使用器",
        agent_role=AgentRole.TOOL_USER,
        capabilities=["call_tool", "query_tool"],
        available_tools=["calculator", "file_reader"]
    )

    print(f"\n工具使用Agent:")
    print(f"  ID: {user_state.agent_id}")
    print(f"  名称: {user_state.agent_name}")
    print(f"  可用工具: {user_state.available_tools}")

    # 3. 更新Agent状态
    print(f"\n更新Agent状态...")
    user_state.update_status(AgentStatus.BUSY, "正在调用calculator工具")
    user_state.current_task_id = "task_001"
    user_state.current_task_description = "计算数学表达式"

    print(f"  状态: {user_state.status.value}")
    print(f"  状态消息: {user_state.status_message}")
    print(f"  当前任务: {user_state.current_task_description}")

    # 4. 检查可用性
    print(f"\n检查Agent可用性:")
    print(f"  creator_state.is_available(): {creator_state.is_available()}")
    print(f"  user_state.is_available(): {user_state.is_available()}")

    # 5. 任务完成后更新
    user_state.update_status(AgentStatus.IDLE, "任务完成")
    user_state.total_tasks_completed += 1
    user_state.current_task_id = None

    print(f"\n任务完成后:")
    print(f"  状态: {user_state.status.value}")
    print(f"  完成任务数: {user_state.total_tasks_completed}")


# ==================== 示例5: 完整交互场景 ====================

def demo_complete_interaction():
    """演示完整的多Agent交互场景"""
    print("\n" + "=" * 60)
    print("示例5: 完整的多Agent交互场景")
    print("=" * 60)

    print("\n场景: 工具使用Agent请求工具创建Agent创建一个新工具，然后使用它")

    # 1. 初始化上下文
    context = Context(
        participants=["tool_user_001", "tool_creator_001"]
    )
    print(f"\n[1] 创建会话上下文: {context.context_id}")

    # 2. 初始化Agent状态
    creator = AgentState(
        agent_id="tool_creator_001",
        agent_name="工具创建器",
        agent_role=AgentRole.TOOL_CREATOR
    )
    user = AgentState(
        agent_id="tool_user_001",
        agent_name="工具使用器",
        agent_role=AgentRole.TOOL_USER
    )
    print(f"[2] 初始化两个Agent: {creator.agent_name}, {user.agent_name}")

    # 3. 用户Agent发送工具创建请求
    user.update_status(AgentStatus.WAITING, "等待工具创建")
    create_request_msg = Message(
        message_type=MessageType.REQUEST,
        sender_id=user.agent_id,
        sender_role=user.agent_role,
        receiver_id=creator.agent_id,
        receiver_role=creator.agent_role,
        content={
            "action": "create_tool",
            "tool_name": "string_reverser",
            "description": "反转字符串的工具"
        },
        context_id=context.context_id
    )
    context.add_message(create_request_msg)
    print(f"\n[3] {user.agent_name} -> {creator.agent_name}: 请求创建工具")
    print(f"    消息内容: {create_request_msg.content}")

    # 4. 创建Agent处理请求并响应
    creator.update_status(AgentStatus.BUSY, "正在创建工具")
    time.sleep(0.1)  # 模拟创建时间
    creator.available_tools.append("string_reverser")
    creator.update_status(AgentStatus.IDLE, "工具创建完成")

    create_response_msg = Message(
        message_type=MessageType.RESPONSE,
        sender_id=creator.agent_id,
        sender_role=creator.agent_role,
        receiver_id=user.agent_id,
        receiver_role=user.agent_role,
        content={
            "status": "success",
            "tool_name": "string_reverser",
            "message": "工具已成功创建"
        },
        context_id=context.context_id,
        parent_message_id=create_request_msg.message_id
    )
    context.add_message(create_response_msg)
    print(f"[4] {creator.agent_name} -> {user.agent_name}: 工具创建完成")

    # 5. 用户Agent调用新创建的工具
    user.update_status(AgentStatus.BUSY, "调用工具")
    user.available_tools.append("string_reverser")

    tool_call_request = ToolCallRequest(
        tool_name="string_reverser",
        parameters={"input": "Hello World"},
        caller_id=user.agent_id,
        context_id=context.context_id
    )
    print(f"\n[5] {user.agent_name} 调用工具: {tool_call_request.tool_name}")
    print(f"    参数: {tool_call_request.parameters}")

    # 6. 工具执行
    time.sleep(0.05)  # 模拟执行
    tool_call_response = ToolCallResponse(
        request_id=tool_call_request.request_id,
        status=ExecutionStatus.SUCCESS,
        result="dlroW olleH",
        execution_time_ms=50
    )
    context.add_tool_call(tool_call_request, tool_call_response)
    print(f"[6] 工具执行完成")
    print(f"    结果: {tool_call_response.result}")

    # 7. 更新状态
    user.update_status(AgentStatus.IDLE, "任务完成")
    user.total_tasks_completed += 1
    context.update_state("last_tool_result", tool_call_response.result)

    # 8. 输出最终状态
    print(f"\n[7] 交互完成")
    print(f"    上下文消息数: {len(context.message_history)}")
    print(f"    工具调用次数: {len(context.tool_call_history)}")
    print(f"    用户Agent完成任务数: {user.total_tasks_completed}")
    print(f"    创建器Agent可用工具: {creator.available_tools}")


# ==================== 示例6: 交互配置 ====================

def demo_interaction_config():
    """演示交互配置的使用"""
    print("\n" + "=" * 60)
    print("示例6: 交互配置")
    print("=" * 60)

    # 创建自定义交互配置
    config = InteractionConfig(
        message_queue_size=500,
        message_timeout_seconds=30,
        default_max_retries=5,
        tool_call_timeout_seconds=60,
        max_concurrent_tool_calls=20,
        enable_detailed_logging=True,
        routing_strategy="priority_based"
    )

    print(f"\n交互配置:")
    config_dict = config.to_dict()
    for key, value in config_dict.items():
        print(f"  {key}: {value}")


# ==================== 主函数 ====================

def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("多Agent交互配置示例")
    print("=" * 60)

    demo_message_passing()
    demo_tool_call_flow()
    demo_context_management()
    demo_agent_state()
    demo_complete_interaction()
    demo_interaction_config()

    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)

    print("\n关键要点:")
    print("  1. Message - Agent间通信的基本单位")
    print("  2. ToolCallRequest/Response - 工具调用的请求和响应")
    print("  3. Context - 维护对话/任务的历史和状态")
    print("  4. AgentState - 追踪Agent的运行状态")
    print("  5. InteractionConfig - 系统级交互配置")


if __name__ == "__main__":
    main()
