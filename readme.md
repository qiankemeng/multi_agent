# Multi-Agent 系统

## 项目目标

本项目设计一套多智能体系统，包含：
- **工具创建Agent**: 负责动态创建工具
- **工具使用Agent**: 负责使用已创建的工具

重点关注：
- 上下文管理
- API参数设计
- 多Agent之间的交互
- 代码易于维护和修改

## 项目结构

```
multi_agent/
├── config/                      # 配置模块（核心）
│   ├── __init__.py             # 模块入口
│   ├── tool_config.py          # 工具配置定义
│   └── interaction_config.py   # 交互配置定义（最重要）
├── examples/                    # 示例代码
│   ├── tool_config_example.py  # 工具配置使用示例
│   └── interaction_example.py  # 交互配置使用示例
├── tests/                       # 测试代码
│   ├── test_tool_config.py     # 工具配置测试
│   └── test_interaction_config.py  # 交互配置测试
├── CLAUDE.md                    # Claude Code开发指南
├── TOOL_CONFIG_GUIDE.md         # 工具配置系统详细文档
├── INTERACTION_CONFIG_GUIDE.md  # 交互配置系统详细文档（重要）
└── readme.md                    # 项目说明（本文件）
```

## 已完成

✅ **工具配置系统** - 定义和管理工具的配置

核心特性：
- 灵活的配置结构（使用dataclass）
- 类型安全（类型提示 + 枚举）
- 参数验证机制
- 全局注册表管理
- 支持增删改查操作
- 易于扩展和维护

详见: [TOOL_CONFIG_GUIDE.md](./TOOL_CONFIG_GUIDE.md)

✅ **交互配置系统** - 多Agent交互的核心变量定义（**最重要**）

核心数据结构：
- **Message**: Agent之间通信的基本单位
- **ToolCallRequest/Response**: 工具调用的请求和响应
- **Context**: 维护对话/任务的历史和状态（系统的"记忆"）
- **AgentState**: 追踪Agent的运行状态
- **InteractionConfig**: 系统级交互配置

这些变量定义了：
- Agent如何相互通信
- 工具如何被调用和响应
- 上下文如何在多次交互中保持连贯
- 系统状态如何被追踪和管理

详见: [INTERACTION_CONFIG_GUIDE.md](./INTERACTION_CONFIG_GUIDE.md)

## 快速开始

### 1. 查看交互配置示例（推荐先看这个）

```bash
python examples/interaction_example.py
```

这个示例展示了：
- Agent之间如何发送消息
- 如何发起和响应工具调用
- 如何管理上下文
- 完整的多Agent交互场景

### 2. 查看工具配置示例

```bash
python examples/tool_config_example.py
```

### 3. 运行测试

```bash
# 测试交互配置
python tests/test_interaction_config.py

# 测试工具配置
python tests/test_tool_config.py
```

### 4. 使用交互配置系统

```python
from config import (
    Message, MessageType, AgentRole,
    ToolCallRequest, ToolCallResponse, ExecutionStatus,
    Context, AgentState
)

# 创建上下文
context = Context(participants=["agent1", "agent2"])

# 发送消息
message = Message(
    message_type=MessageType.REQUEST,
    sender_id="agent1",
    receiver_id="agent2",
    content={"action": "create_tool"},
    context_id=context.context_id
)
context.add_message(message)

# 调用工具
request = ToolCallRequest(
    tool_name="calculator",
    parameters={"expression": "1+1"},
    caller_id="agent1",
    context_id=context.context_id
)

# 处理响应
response = ToolCallResponse(
    request_id=request.request_id,
    status=ExecutionStatus.SUCCESS,
    result=2
)

# 记录到上下文
context.add_tool_call(request, response)
```

### 5. 使用工具配置系统

```python
from config import ToolConfig, ToolCategory, ToolParameter, ParameterType, register_tool

# 创建工具
my_tool = ToolConfig(
    name="my_tool",
    display_name="我的工具",
    description="工具描述",
    category=ToolCategory.CUSTOM,
    parameters=[
        ToolParameter(
            name="input",
            type=ParameterType.STRING,
            description="输入参数",
            required=True
        )
    ]
)

# 注册工具
register_tool(my_tool)
```

## 下一步计划

- [ ] 实现消息路由系统
- [ ] 实现工具创建Agent
- [ ] 实现工具使用Agent
- [ ] 构建Agent间协调机制
- [ ] 添加持久化支持
- [ ] 集成测试

## 文档

- [CLAUDE.md](./CLAUDE.md) - Claude Code开发指南
- [INTERACTION_CONFIG_GUIDE.md](./INTERACTION_CONFIG_GUIDE.md) - **交互配置系统详细文档（重要）**
- [TOOL_CONFIG_GUIDE.md](./TOOL_CONFIG_GUIDE.md) - 工具配置系统详细文档

## 贡献

欢迎提出改进建议！