# 交互配置系统文档

## 概述

这是多Agent系统的核心配置模块，定义了Agent之间、工具之间交互所需的所有数据结构和协议。这些变量是整个系统运行的基础。

## 为什么交互变量最重要？

在多Agent系统中，**交互变量定义了系统的通信语言**。它们决定了：
1. Agent如何相互通信
2. 工具如何被调用和响应
3. 上下文如何在多次交互中保持连贯
4. 系统状态如何被追踪和管理

**工具配置** 定义了"有哪些工具"，而 **交互配置** 定义了"如何使用这些工具"。

## 核心数据结构

### 1. Message - 消息

**用途**: Agent之间通信的基本单位

**关键字段**:
```python
Message(
    message_id: str                    # 唯一标识
    message_type: MessageType          # 消息类型（请求/响应/通知等）
    sender_id: str                     # 发送者ID
    receiver_id: str                   # 接收者ID
    content: Any                       # 消息内容
    context_id: str                    # 关联的上下文ID
    priority: Priority                 # 优先级
    parent_message_id: str             # 父消息ID（用于追踪对话链）
)
```

**使用场景**:
- 工具使用Agent请求工具创建Agent创建新工具
- Agent之间传递任务和结果
- 发送通知和事件
- 错误信息传递

**示例**:
```python
# 请求消息
request = Message(
    message_type=MessageType.REQUEST,
    sender_id="tool_user_001",
    sender_role=AgentRole.TOOL_USER,
    receiver_id="tool_creator_001",
    receiver_role=AgentRole.TOOL_CREATOR,
    content={"action": "create_tool", "tool_name": "calculator"}
)

# 响应消息
response = Message(
    message_type=MessageType.RESPONSE,
    sender_id="tool_creator_001",
    receiver_id="tool_user_001",
    content={"status": "success"},
    parent_message_id=request.message_id  # 关联到请求
)
```

### 2. ToolCallRequest - 工具调用请求

**用途**: 当Agent需要调用工具时发送的请求

**关键字段**:
```python
ToolCallRequest(
    request_id: str                    # 请求唯一标识
    tool_name: str                     # 工具名称
    parameters: Dict[str, Any]         # 工具参数
    caller_id: str                     # 调用者ID
    context_id: str                    # 上下文ID
    timeout_seconds: int               # 超时时间
    priority: Priority                 # 优先级
    max_retries: int                   # 最大重试次数
)
```

**使用场景**:
- 调用已创建的工具
- 带参数执行特定功能
- 需要追踪调用来源和上下文

**示例**:
```python
request = ToolCallRequest(
    tool_name="calculator",
    parameters={"expression": "2+3*4", "precision": 2},
    caller_id="tool_user_001",
    context_id="ctx_001",
    timeout_seconds=10
)
```

### 3. ToolCallResponse - 工具调用响应

**用途**: 工具执行后返回的结果

**关键字段**:
```python
ToolCallResponse(
    response_id: str                   # 响应唯一标识
    request_id: str                    # 对应的请求ID
    status: ExecutionStatus            # 执行状态（成功/失败/超时等）
    result: Any                        # 执行结果
    error_message: str                 # 错误信息（如果失败）
    execution_time_ms: float           # 执行时间
    resource_usage: Dict               # 资源使用情况
)
```

**使用场景**:
- 返回工具执行结果
- 报告执行错误
- 追踪性能指标

**示例**:
```python
# 成功响应
response = ToolCallResponse(
    request_id=request.request_id,
    status=ExecutionStatus.SUCCESS,
    result=14,
    execution_time_ms=50.2
)

# 失败响应
error_response = ToolCallResponse(
    request_id=request.request_id,
    status=ExecutionStatus.FAILED,
    error_message="除零错误",
    error_type="ZeroDivisionError"
)
```

### 4. Context - 上下文

**用途**: 贯穿整个交互过程的上下文信息，这是多Agent系统的"记忆"

**关键字段**:
```python
Context(
    context_id: str                    # 上下文唯一标识
    session_id: str                    # 会话ID
    message_history: List[Message]     # 消息历史
    tool_call_history: List[Dict]      # 工具调用历史
    shared_state: Dict[str, Any]       # Agent间共享的状态
    variables: Dict[str, Any]          # 上下文变量
    participants: List[str]            # 参与的Agent列表
    max_history_length: int            # 最大历史长度
)
```

**核心方法**:
```python
context.add_message(msg)                      # 添加消息到历史
context.add_tool_call(request, response)      # 添加工具调用记录
context.update_state(key, value)              # 更新共享状态
context.get_state(key, default)               # 获取共享状态
context.get_recent_messages(count)            # 获取最近N条消息
```

**使用场景**:
- 维护对话历史
- 在多次交互间传递状态
- 追踪工具调用历史
- Agent间共享信息

**示例**:
```python
context = Context(
    max_history_length=100,
    participants=["tool_user_001", "tool_creator_001"]
)

# 添加消息
context.add_message(message)

# 共享状态
context.update_state("current_tool", "calculator")
current_tool = context.get_state("current_tool")

# 记录工具调用
context.add_tool_call(tool_request, tool_response)
```

### 5. AgentState - Agent状态

**用途**: 描述和追踪Agent的当前状态

**关键字段**:
```python
AgentState(
    agent_id: str                      # Agent唯一标识
    agent_name: str                    # Agent名称
    agent_role: AgentRole              # Agent角色
    status: AgentStatus                # 当前状态（空闲/忙碌/等待等）
    current_task_id: str               # 当前任务ID
    pending_tasks: List[Dict]          # 待处理任务队列
    capabilities: List[str]            # Agent能力列表
    available_tools: List[str]         # 可用工具列表
    total_tasks_completed: int         # 完成任务数
)
```

**核心方法**:
```python
agent.update_status(status, message)   # 更新状态
agent.is_available()                   # 判断是否可用
```

**使用场景**:
- 监控Agent运行状态
- 负载均衡和任务调度
- 性能追踪
- 故障诊断

**示例**:
```python
agent = AgentState(
    agent_id="tool_creator_001",
    agent_name="工具创建器",
    agent_role=AgentRole.TOOL_CREATOR,
    capabilities=["create_tool", "modify_tool"],
    status=AgentStatus.IDLE
)

# 开始任务
agent.update_status(AgentStatus.BUSY, "正在创建工具")

# 任务完成
agent.update_status(AgentStatus.IDLE, "任务完成")
agent.total_tasks_completed += 1
```

### 6. InteractionConfig - 交互配置

**用途**: 系统级别的交互规则和参数配置

**关键字段**:
```python
InteractionConfig(
    # 消息配置
    message_queue_size: int            # 消息队列大小
    message_timeout_seconds: int       # 消息超时时间

    # 重试配置
    default_max_retries: int           # 默认最大重试次数
    retry_delay_seconds: float         # 重试延迟
    exponential_backoff: bool          # 是否指数退避

    # 超时配置
    tool_call_timeout_seconds: int     # 工具调用超时
    context_idle_timeout_seconds: int  # 上下文空闲超时

    # 并发控制
    max_concurrent_tool_calls: int     # 最大并发工具调用数
    max_concurrent_agents: int         # 最大并发Agent数

    # 监控和安全
    enable_detailed_logging: bool      # 是否详细日志
    enable_message_validation: bool    # 是否验证消息
)
```

**使用场景**:
- 系统初始化配置
- 性能调优
- 资源限制
- 安全策略

## 枚举类型

### MessageType - 消息类型
```python
REQUEST      # 请求
RESPONSE     # 响应
NOTIFICATION # 通知
COMMAND      # 命令
EVENT        # 事件
ERROR        # 错误
```

### AgentRole - Agent角色
```python
TOOL_CREATOR  # 工具创建者
TOOL_USER     # 工具使用者
COORDINATOR   # 协调者
MONITOR       # 监控者
```

### AgentStatus - Agent状态
```python
IDLE     # 空闲
BUSY     # 忙碌
WAITING  # 等待
ERROR    # 错误
OFFLINE  # 离线
```

### ExecutionStatus - 执行状态
```python
PENDING   # 待执行
RUNNING   # 执行中
SUCCESS   # 成功
FAILED    # 失败
TIMEOUT   # 超时
CANCELLED # 已取消
```

### Priority - 优先级
```python
LOW     = 1  # 低
NORMAL  = 2  # 普通
HIGH    = 3  # 高
URGENT  = 4  # 紧急
```

## 典型交互流程

### 场景1: 创建并使用工具

```python
# 1. 创建上下文
context = Context(participants=["user", "creator"])

# 2. 工具使用Agent发送创建请求
create_msg = Message(
    message_type=MessageType.REQUEST,
    sender_id="user",
    receiver_id="creator",
    content={"action": "create_tool", "tool_name": "calculator"},
    context_id=context.context_id
)
context.add_message(create_msg)

# 3. 工具创建Agent响应
create_response = Message(
    message_type=MessageType.RESPONSE,
    sender_id="creator",
    receiver_id="user",
    content={"status": "success", "tool_name": "calculator"},
    parent_message_id=create_msg.message_id
)
context.add_message(create_response)

# 4. 调用工具
tool_request = ToolCallRequest(
    tool_name="calculator",
    parameters={"expression": "1+1"},
    caller_id="user",
    context_id=context.context_id
)

# 5. 工具执行
tool_response = ToolCallResponse(
    request_id=tool_request.request_id,
    status=ExecutionStatus.SUCCESS,
    result=2
)

# 6. 记录到上下文
context.add_tool_call(tool_request, tool_response)
```

### 场景2: 错误处理和重试

```python
# 发起调用
request = ToolCallRequest(
    tool_name="unreliable_tool",
    max_retries=3,
    timeout_seconds=10
)

# 第一次失败
response1 = ToolCallResponse(
    request_id=request.request_id,
    status=ExecutionStatus.FAILED,
    error_message="网络错误"
)

# 重试后成功
response2 = ToolCallResponse(
    request_id=request.request_id,
    status=ExecutionStatus.SUCCESS,
    result="success"
)
```

## 变量组织原则

### 1. 分层组织
```
交互配置 (interaction_config.py)
├── 消息层：Message, MessageType
├── 调用层：ToolCallRequest, ToolCallResponse
├── 上下文层：Context
├── Agent层：AgentState, AgentRole
└── 系统层：InteractionConfig, InteractionProtocol
```

### 2. 数据流向
```
发送者Agent
    ↓ 创建Message
消息队列
    ↓ 路由
接收者Agent
    ↓ 处理
创建ToolCallRequest
    ↓ 执行
ToolCallResponse
    ↓ 记录
Context
```

### 3. 扩展性设计
所有数据结构都包含：
- `metadata: Dict[str, Any]` - 可扩展的元数据字段
- `to_dict()` 方法 - 便于序列化
- 默认值 - 简化使用

## 最佳实践

### 1. 始终使用上下文
```python
# ✓ 好的做法
context = Context()
message.context_id = context.context_id
context.add_message(message)

# ✗ 不推荐
# 不关联上下文会丢失历史
```

### 2. 追踪消息链
```python
# ✓ 响应消息关联请求
response.parent_message_id = request.message_id
```

### 3. 正确处理错误
```python
# ✓ 提供详细错误信息
response = ToolCallResponse(
    status=ExecutionStatus.FAILED,
    error_message="具体的错误描述",
    error_type="ErrorClassName",
    error_traceback="完整堆栈"
)
```

### 4. 状态同步
```python
# ✓ 及时更新Agent状态
agent.update_status(AgentStatus.BUSY, "执行任务X")
# ... 执行任务
agent.update_status(AgentStatus.IDLE, "任务完成")
```

## 运行示例

```bash
# 查看完整交互示例
python examples/interaction_example.py

# 运行测试验证
python tests/test_interaction_config.py
```

## 常见问题

**Q: Message和ToolCallRequest有什么区别？**
A: Message是通用的通信单位，可以传递任何信息。ToolCallRequest专门用于工具调用，包含工具特定的字段（如参数、超时等）。

**Q: 为什么需要Context？**
A: Context维护了整个对话/任务的历史和状态，使得Agent可以理解之前发生了什么，做出更智能的决策。

**Q: 如何实现消息路由？**
A: 使用Message中的sender_id和receiver_id字段，结合InteractionConfig中的路由策略。

**Q: 上下文历史会一直增长吗？**
A: 不会，Context有max_history_length限制，会自动清理旧消息。

**Q: 如何追踪一个完整的对话链？**
A: 使用parent_message_id字段，可以追溯到最初的请求消息。

## 下一步

基于这些交互变量，你可以：
1. 实现Agent的具体逻辑
2. 构建消息路由系统
3. 实现工具执行引擎
4. 添加监控和日志
5. 实现持久化和恢复

这些变量定义了系统的"骨架"，在此基础上可以灵活地实现各种功能。
