# Multi-Agent System 核心模块说明

## 模块概览

本目录包含多Agent系统的核心实现，每个文件都是一个独立的功能模块。

---

## 📦 types.py - 核心数据结构

### 功能说明
定义了整个系统的核心数据结构，包括：
- `Tool` - 工具定义（包含prompt模板、参数、原子操作）
- `ToolParameter` - 工具参数定义
- `AgentAction` - Agent行动记录
- `AgentPlan` - 执行计划（包含步骤和依赖关系）
- `PlanStep` - 计划步骤
- `MultiAgentSession` - 完整会话记录

### 独立测试
```bash
python agents/multi_agent_system/types.py
```

### 测试样例
```python
from agents.multi_agent_system.types import Tool, ToolParameter, AgentPlan, PlanStep

# 创建工具定义
tool = Tool(
    tool_id="tool_001",
    tool_name="analyze_video",
    description="Analyze video content",
    purpose="Extract key information from video frames",
    prompt_template="Analyze the following frames: {frames}",
    parameters={"frames": ToolParameter(name="frames", type="List[Frame]")}
)

# 创建执行计划
plan = AgentPlan(
    plan_id="plan_001",
    task_description="Analyze video and answer question",
    steps=[PlanStep(step_id="step_1", tool_name="analyze_video", tool_id="tool_001")]
)
```

---

## 🔧 tool_creator.py - 工具创建Agent

### 功能说明
**Tool Creator Agent** 负责动态创建视频处理工具：
1. 分析用户任务需求
2. 将任务分解为子任务
3. 为每个子任务设计专门的工具（包含定制化的prompt模板）
4. 选择合适的原子操作组合

**核心特性：**
- **动态Prompt设计**：使用MLLM设计每个工具的prompt，而不是硬编码
- **任务分解能力**：自动识别任务类型并分解为可管理的子任务
- **英文输出**：所有prompts和输出都是英文
- **max_tokens=16000**：不限制MLLM输出长度

### 独立测试
```bash
python -c "
from agents.multi_agent_system.tool_creator import ToolCreatorAgent
from agents.mllm_client import MLLMClient, MLLMClientConfig

# 初始化
client = MLLMClient(MLLMClientConfig())
agent = ToolCreatorAgent(mllm_client=client)

# 设计工具
task = '''
Task: Simple Video Question Answering
Video: test.mp4 (30 seconds)
Question: What is the main action in the video?
'''

tools = agent.design_tools(task)
print(f'Designed {len(tools)} tools')
for tool in tools:
    print(f'  - {tool.tool_name}: {tool.purpose[:80]}...')
"
```

### 主要方法
- `design_tools(task_description)` - 分析任务并设计工具
- `_analyze_task(task)` - 分析任务类型和关键要素
- `_decompose_task(task, analysis)` - 分解任务为子任务
- `_design_tool(subtask)` - 为单个子任务设计工具

---

## 🎯 tool_user.py - 工具使用Agent

### 功能说明
**Tool User Agent** 负责规划和执行工具使用：
1. 根据任务和可用工具创建执行计划
2. 处理步骤之间的依赖关系（使用 `{from_step_X}` 引用）
3. 跟踪执行进度和结果
4. 统计tokens使用和成本

**核心特性：**
- **智能规划**：考虑工具依赖关系和数据流
- **依赖追踪**：自动处理步骤间的数据传递
- **成本统计**：精确跟踪每个API调用的tokens和成本

### 独立测试
```bash
python -c "
from agents.multi_agent_system.tool_user import ToolUserAgent
from agents.multi_agent_system.types import Tool, ToolParameter
from agents.mllm_client import MLLMClient, MLLMClientConfig

# 初始化
client = MLLMClient(MLLMClientConfig())
agent = ToolUserAgent(mllm_client=client)

# 创建测试工具
tools = [
    Tool(
        tool_id='tool_1',
        tool_name='analyze_video',
        description='Analyze video content',
        purpose='Extract information from video',
        prompt_template='Analyze: {video_path}',
        parameters={'video_path': ToolParameter(name='video_path', type='str')}
    )
]

# 创建执行计划
plan = agent._create_plan(
    task='Analyze the video',
    tools=tools,
    data={'video_path': 'test.mp4'}
)

print(f'Plan created with {len(plan.steps)} steps')
print(f'Reasoning: {plan.reasoning[:100]}...')
"
```

### 主要方法
- `_create_plan(task, tools, data)` - 创建执行计划
- `execute_plan(plan)` - 执行计划（依次执行所有步骤）

---

## ⚙️ tool_executor.py - 工具执行引擎

### 功能说明
**Tool Executor** 负责实际执行工具定义：
1. 验证工具输入参数
2. 填充prompt模板中的占位符（`{variable}`）
3. 执行原子操作（SAMPLE, SEGMENT, CALL_MODEL, BBOX）
4. 调用MLLM API获取结果
5. 返回执行结果

**核心特性：**
- **Prompt模板填充**：自动替换模板中的变量
- **原子操作执行**：支持多种基础操作
- **MLLM调用**：包含重试机制的API调用

### 独立测试
```bash
python -c "
from agents.multi_agent_system.tool_executor import ToolExecutor
from agents.multi_agent_system.types import Tool, ToolParameter
from agents.mllm_client import MLLMClient, MLLMClientConfig
from processors.atomic_operations_impl import AtomicOperations

# 初始化
client = MLLMClient(MLLMClientConfig())
atomic_ops = AtomicOperations()
executor = ToolExecutor(mllm_client=client, atomic_ops=atomic_ops)

# 创建工具
tool = Tool(
    tool_id='tool_1',
    tool_name='test_tool',
    description='Test tool',
    purpose='For testing',
    prompt_template='Analyze this: {input_text}',
    system_prompt='You are a test assistant',
    parameters={'input_text': ToolParameter(name='input_text', type='str')},
    atomic_operations=['CALL_MODEL']
)

# 执行工具
result = executor.execute(tool, {'input_text': 'Hello world'}, atomic_ops)
print(f'Execution result: {result}')
"
```

### 主要方法
- `execute(tool, inputs, atomic_ops)` - 执行工具
- `_fill_prompt_template(template, inputs)` - 填充prompt模板
- `_execute_atomic_operations(operations, inputs, atomic_ops)` - 执行原子操作

---

## 🎼 coordinator.py - 多Agent协调器

### 功能说明
**Multi-Agent Coordinator** 协调Tool Creator和Tool User的工作流程：
1. 接收用户任务
2. 调用Tool Creator设计工具
3. 将工具传递给Tool User进行规划和执行
4. 收集和返回最终结果
5. 记录完整的会话历史

**核心特性：**
- **端到端执行**：自动完成从工具设计到执行的全流程
- **会话管理**：记录所有Agent行动和结果
- **错误处理**：处理各阶段可能的失败情况

### 独立测试
```bash
python -c "
from agents.multi_agent_system.coordinator import MultiAgentCoordinator
from agents.mllm_client import MLLMClient, MLLMClientConfig
from processors.atomic_operations_impl import AtomicOperations

# 初始化
client = MLLMClient(MLLMClientConfig())
atomic_ops = AtomicOperations()
coordinator = MultiAgentCoordinator(
    mllm_client=client,
    atomic_ops=atomic_ops
)

# 执行任务
task = 'Analyze video and answer: What happens in the video?'
data = {'video_path': 'test.mp4', 'question': 'What happens in the video?'}

session = coordinator.run_task(task, data)
print(f'Session {session.session_id}')
print(f'Designed tools: {len(session.designed_tools)}')
print(f'Success: {session.success}')
"
```

### 主要方法
- `run_task(task_description, input_data)` - 执行完整任务
- `_create_session(task_description)` - 创建新会话
- `_finalize_session(session, success, result)` - 完成会话

---

## 🧪 完整系统测试

### 测试整个Multi-Agent工作流

```bash
python tests/test_complete_workflow.py
```

这个测试展示了完整的工作流程：
1. 初始化所有Agent和Client
2. Tool Creator分析任务并设计工具
3. Tool User创建执行计划
4. 输出完整的工具定义和计划

### 测试规划功能

```bash
python tests/test_planning.py
```

测试Tool User Agent的规划能力。

---

## 📊 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                Multi-Agent Coordinator                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐         ┌──────────────────┐     │
│  │  Tool Creator    │ designs │   Tool User      │     │
│  │     Agent        │────────▶│     Agent        │     │
│  │                  │  tools  │                  │     │
│  │  - Analyzes      │         │  - Plans         │     │
│  │  - Decomposes    │         │  - Executes      │     │
│  │  - Designs       │         │  - Tracks        │     │
│  └────────┬─────────┘         └────────┬─────────┘     │
│           │                            │                │
│           ▼                            ▼                │
│  ┌────────────────────────────────────────────┐        │
│  │        Tool Executor (executes tools)       │        │
│  └────────────────────────────────────────────┘        │
│           │                            │                │
│           ▼                            ▼                │
│  ┌────────────────────────────────────────────┐        │
│  │    MLLM Client (GPT-4V, Claude, etc.)      │        │
│  │    - max_tokens: 16000                     │        │
│  │    - English prompts                       │        │
│  └────────────────────────────────────────────┘        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 💡 关键设计原则

1. **动态Prompt设计**：所有工具的prompt都由MLLM动态生成，不是硬编码
2. **完全英文**：所有prompts、输出和文档都是英文（提高JSON稳定性）
3. **无Token限制**：max_tokens=16000，让MLLM自由表达
4. **可追溯性**：所有Agent行动都被记录，包含reasoning
5. **模块化**：每个文件都是独立的功能模块，可以单独测试
6. **成本意识**：精确跟踪每个API调用的tokens和成本

---

## 📝 开发建议

### 添加新的Agent

1. 在 `types.py` 中添加新的 `AgentType`
2. 创建新的Agent类，实现核心方法
3. 在Coordinator中集成新Agent
4. 添加独立测试代码

### 添加新的原子操作

1. 在 `processors/atomic_operations_impl.py` 中实现
2. 在Tool设计时可以使用新操作
3. Tool Executor会自动支持

### 调试技巧

- 查看Agent输出：所有Agent都有详细的print输出
- 检查JSON响应：使用 `[Debug] API response` 查看原始响应
- 验证Prompt：检查填充后的prompt是否符合预期
- 成本监控：关注tokens_used和cost_usd

---

## 🔗 相关文档

- `docs/PROJECT_TASK.md` - 项目任务定义
- `docs/COMPLETE_WORKFLOW_TEST_RESULTS.md` - 完整工作流测试结果
- `docs/TOKEN_LIMIT_REMOVAL.md` - Token限制移除说明
- `docs/TOOL_CREATOR_ENGLISH.md` - 英文化修改记录
