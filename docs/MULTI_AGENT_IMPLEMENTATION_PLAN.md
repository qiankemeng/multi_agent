# Multi-Agent系统重构实施计划

## 项目状态

### ✅ 已完成

#### 1. 架构设计 (`docs/MULTI_AGENT_REDESIGN.md`)
- ✅ 核心理念定义
- ✅ Two-Agent System设计
- ✅ 数据结构设计（Tool, AgentAction, AgentPlan）
- ✅ 工作流程设计
- ✅ 完整文档编写

#### 2. 核心数据结构 (`agents/multi_agent_system/types.py`)
- ✅ `Tool`: 工具定义（包含prompt_template, parameters等）
- ✅ `ToolParameter`: 参数定义
- ✅ `AgentAction`: Agent行动记录
- ✅ `AgentPlan`: 执行计划
- ✅ `PlanStep`: 计划步骤
- ✅ `MultiAgentSession`: 完整会话记录
- ✅ 所有枚举类型（AgentType, ActionType, PlanStatus）

---

## 🚧 待实现

### Phase 1: Agent实现 (核心)

#### 1.1 Tool Creator Agent (`agents/multi_agent_system/tool_creator.py`)

**职责**：
- 分析任务需求
- 分解为子任务
- 为每个子任务设计工具（**核心是prompt设计**）
- 优化工具集

**关键方法**：
```python
class ToolCreatorAgent:
    def design_tools(self, task_description: str) -> List[Tool]:
        # 主入口
        pass

    def _analyze_task(self, task_description: str) -> Dict:
        # 使用MLLM分析任务
        pass

    def _decompose_task(self, task_analysis: Dict) -> List[Dict]:
        # 分解为子任务
        pass

    def _design_tool(self, subtask: Dict) -> Tool:
        # 为子任务设计工具（含prompt）
        # 最核心的方法！
        pass

    def _optimize_toolset(self, tools: List[Tool]) -> List[Tool]:
        # 优化工具集
        pass
```

**Prompt设计示例**：
```python
# Tool Creator设计prompt的prompt
design_prompt = """你是AI工具设计专家，擅长设计高质量Prompt。

子任务：{subtask_description}

请设计一个工具：
1. Prompt模板（使用{var}占位符）
2. System Prompt
3. 参数定义
4. 输出格式

输出JSON格式的工具定义。"""
```

#### 1.2 Tool User Agent (`agents/multi_agent_system/tool_user.py`)

**职责**：
- 接收任务和工具集
- 规划执行步骤
- 选择和调用工具
- 整合结果

**关键方法**：
```python
class ToolUserAgent:
    def execute_task(self, task: str, tools: List[Tool], data: Dict) -> Dict:
        # 主入口
        pass

    def _create_plan(self, task: str, tools: List[Tool]) -> AgentPlan:
        # 使用MLLM规划执行步骤
        pass

    def _select_tool(self, step: PlanStep, tools: List[Tool]) -> Tool:
        # 选择合适的工具
        pass

    def _execute_tool(self, tool: Tool, inputs: Dict) -> Dict:
        # 执行工具（调用原子操作）
        pass

    def _prepare_inputs(self, step: PlanStep, results: Dict) -> Dict:
        # 准备工具输入
        pass

    def _aggregate_results(self, results: Dict) -> Dict:
        # 整合所有结果
        pass
```

**规划Prompt示例**：
```python
planning_prompt = """你是任务规划专家。

任务：{task}

可用工具：
{tools_description}

请创建执行计划：
1. 列出执行步骤
2. 每步使用哪个工具
3. 步骤依赖关系

输出JSON格式计划。"""
```

### Phase 2: 工具执行引擎 (`agents/multi_agent_system/tool_executor.py`)

**职责**：
- 解释Tool定义
- 调用原子操作
- 格式化输入输出

**关键方法**：
```python
class ToolExecutor:
    def execute(self, tool: Tool, inputs: Dict, atomic_ops: AtomicOperations) -> Dict:
        # 执行工具
        outputs = {}

        # 根据tool定义执行原子操作
        if "SAMPLE" in tool.atomic_operations:
            frames = atomic_ops.sample(...)
            outputs["frames"] = frames

        if "CALL_MODEL" in tool.atomic_operations:
            # 使用tool的prompt_template
            prompt = tool.prompt_template.format(**inputs)
            response = atomic_ops.call_model(
                prompt=prompt,
                system_prompt=tool.system_prompt,
                frames=outputs.get("frames"),
                ...
            )
            outputs["response"] = response.output

        return outputs
```

### Phase 3: 协调器 (`agents/multi_agent_system/coordinator.py`)

**职责**：
- 协调Tool Creator和Tool User
- 管理会话
- 追踪统计

```python
class MultiAgentCoordinator:
    def __init__(self):
        self.tool_creator = ToolCreatorAgent()
        self.tool_user = ToolUserAgent()
        self.tool_executor = ToolExecutor()

    def process(self, video_path: str, question: str) -> Dict:
        # 创建会话
        session = MultiAgentSession(...)

        # Phase 1: Tool Creation
        task_description = f"分析视频{video_path}并回答：{question}"
        tools = self.tool_creator.design_tools(task_description)
        session.designed_tools = tools

        # Phase 2: Tool Usage
        result = self.tool_user.execute_task(
            task=task_description,
            tools=tools,
            data={"video_path": video_path, "question": question}
        )
        session.final_result = result

        return session
```

### Phase 4: 集成和测试

#### 4.1 更新`__init__.py` (`agents/multi_agent_system/__init__.py`)

```python
from .types import (
    Tool, ToolParameter,
    AgentAction, AgentPlan, PlanStep,
    MultiAgentSession,
    AgentType, ActionType, PlanStatus
)
from .tool_creator import ToolCreatorAgent
from .tool_user import ToolUserAgent
from .tool_executor import ToolExecutor
from .coordinator import MultiAgentCoordinator

__all__ = [
    # Types
    'Tool', 'ToolParameter',
    'AgentAction', 'AgentPlan', 'PlanStep',
    'MultiAgentSession',
    'AgentType', 'ActionType', 'PlanStatus',

    # Agents
    'ToolCreatorAgent',
    'ToolUserAgent',
    'ToolExecutor',
    'MultiAgentCoordinator'
]
```

#### 4.2 创建测试示例 (`examples/multi_agent_example.py`)

```python
from agents.multi_agent_system import MultiAgentCoordinator

def test_multi_agent_videoqa():
    # 创建协调器
    coordinator = MultiAgentCoordinator()

    # 执行任务
    result = coordinator.process(
        video_path="data/videos/source.mp4",
        question="What is happening in this video?"
    )

    # 输出结果
    print("\n=== Tool Creator 设计的工具 ===")
    for tool in result.designed_tools:
        print(f"\n工具: {tool.tool_name}")
        print(f"目的: {tool.purpose}")
        print(f"Prompt: {tool.prompt_template[:100]}...")

    print("\n=== Tool User 执行计划 ===")
    for step in result.execution_plan.steps:
        print(f"\n步骤: {step.tool_name}")
        print(f"状态: {step.status}")

    print("\n=== 最终结果 ===")
    print(result.final_result)

    print("\n=== 统计 ===")
    print(f"Tokens: {result.total_tokens}")
    print(f"成本: ${result.total_cost:.4f}")

if __name__ == "__main__":
    test_multi_agent_videoqa()
```

---

## 实现顺序

### 优先级1: 核心Agent（必须）

1. **Tool Creator Agent** - 最核心
   - 任务分析
   - 任务分解
   - **Prompt设计** ← 最关键！
   - 工具生成

2. **Tool User Agent** - 次核心
   - 任务规划
   - 工具选择
   - 执行协调

3. **Tool Executor** - 辅助
   - 工具执行引擎
   - 原子操作调用

### 优先级2: 协调和测试

4. **Coordinator** - 集成
   - 两个Agent协调
   - 会话管理

5. **测试和示例** - 验证
   - 端到端测试
   - 对比旧系统

---

## 关键设计点

### 1. Prompt设计能力（最核心）

Tool Creator Agent的核心能力是设计高质量的prompt。

**示例1: Segment分析工具的Prompt**

Tool Creator可能设计：
```
Prompt Template:
\"\"\"分析视频片段 [{start_sec}s - {end_sec}s]。

以下是从该片段采样的{num_frames}帧关键画面。

请提供：
1. 场景描述：这个片段展示了什么场景？
2. 主要事件：发生了什么事情？按时间顺序列出。
3. 关键对象：画面中有哪些重要的人物、物体？
4. 情感/氛围：整体氛围如何？

输出格式：
Scene: [场景描述]
Events: [事件1, 事件2, ...]
Objects: [对象1, 对象2, ...]
Mood: [情感/氛围]
\"\"\"

System Prompt:
"你是专业的视频内容分析师，擅长从视频帧中理解故事情节和场景细节。"
```

**vs 旧的硬编码prompt**:
```python
# 旧系统：硬编码
prompt = f"Analyze this segment from {start}s to {end}s..."
```

### 2. 动态工具适应

不同任务可能需要不同工具：

**场景A：标准问答**
```
Tool Creator 设计：
- segment_video_tool
- analyze_segment_tool
- answer_question_tool
```

**场景B：情感分析**
```
Tool Creator 设计：
- emotion_analyzer_tool
- mood_tracker_tool
- sentiment_summarizer_tool
```

**场景C：对象追踪**
```
Tool Creator 设计：
- object_detector_tool
- object_tracker_tool
- trajectory_analyzer_tool
```

### 3. Agent决策可追踪

所有Agent决策都被记录：

```python
AgentAction(
    agent_id="tool_creator_001",
    action_type=ActionType.DESIGN_TOOL,
    reasoning="用户需要分析视频段落，设计一个专门的segment分析工具",
    tool=segment_analyzer_tool,
    tokens_used=3200,
    cost_usd=0.12
)
```

可以查看：
- 为什么设计这个工具？
- Prompt是怎么设计的？
- 花费了多少成本？

---

## 预期效果对比

### 旧系统（固定流程）

```python
# 固定步骤，无法改变
def run_video_qa(video, question):
    meta = extract_metadata(video)  # 固定
    segments = segment(meta, 60.0)  # 固定60秒
    for seg in segments:
        analyze(seg)  # 固定prompt
    answer = qa(question)  # 固定prompt
    return answer
```

**缺点**：
- ❌ 无法适应不同任务
- ❌ Prompt硬编码，难以优化
- ❌ 无agent自主决策

### 新系统（Multi-Agent）

```python
# 动态适应，灵活决策
coordinator = MultiAgentCoordinator()
result = coordinator.process(video, question)

# 内部流程：
# 1. Tool Creator 分析任务，设计3-5个专门工具
# 2. Tool User 规划执行步骤，选择工具
# 3. Tool Executor 执行工具，调用原子操作
# 4. 返回结果
```

**优点**：
- ✅ 根据任务设计专门工具
- ✅ Prompt由Agent动态设计
- ✅ 有真正的agent决策
- ✅ 可追踪推理过程
- ✅ 易于扩展新任务类型

---

## 下一步行动

### 立即实现（Phase 1）

1. **实现Tool Creator Agent** (`tool_creator.py`)
   - 重点：Prompt设计能力
   - 预计：500-800行代码
   - 时间：2-3小时

2. **实现Tool User Agent** (`tool_user.py`)
   - 重点：任务规划和工具选择
   - 预计：600-900行代码
   - 时间：2-3小时

3. **实现Tool Executor** (`tool_executor.py`)
   - 重点：工具执行引擎
   - 预计：200-300行代码
   - 时间：1小时

### 集成测试（Phase 2）

4. **实现Coordinator** (`coordinator.py`)
   - 协调两个Agent
   - 预计：200-300行代码
   - 时间：1小时

5. **创建示例和测试** (`examples/multi_agent_example.py`)
   - 端到端测试
   - 与旧系统对比
   - 时间：1-2小时

### 总预计时间：8-12小时

---

## 文件结构

```
agents/
├── multi_agent_system/          # 新的multi-agent系统
│   ├── __init__.py              # 导出
│   ├── types.py                 # ✅ 数据结构（已完成）
│   ├── tool_creator.py          # 🚧 Tool Creator Agent
│   ├── tool_user.py             # 🚧 Tool User Agent
│   ├── tool_executor.py         # 🚧 Tool Executor
│   └── coordinator.py           # 🚧 Coordinator
│
├── mllm_client.py               # 复用
├── tool_creator_agent.py        # 旧实现（保留）
└── tool_user_agent.py           # 旧实现（保留）

examples/
├── multi_agent_example.py       # 🚧 新系统示例
└── video_qa_pipeline_example.py # 旧系统（对比）

docs/
├── MULTI_AGENT_REDESIGN.md      # ✅ 设计文档（已完成）
└── MULTI_AGENT_IMPLEMENTATION_PLAN.md  # ← 本文档
```

---

## 成功标准

### 功能性

1. ✅ Tool Creator能够分析任务并设计工具
2. ✅ 设计的工具包含高质量的prompt
3. ✅ Tool User能够规划执行步骤
4. ✅ Tool User能够选择和调用工具
5. ✅ 整个流程能完成视频问答任务

### 质量

6. ✅ 所有Agent决策可追踪（reasoning字段）
7. ✅ Token和成本统计准确
8. ✅ 错误处理完善
9. ✅ 代码结构清晰，易于扩展

### 效果

10. ✅ 输出质量不低于旧系统
11. ✅ 可以处理旧系统无法处理的任务类型
12. ✅ Prompt质量明显提升

---

## 总结

**当前状态**：
- ✅ 架构设计完成
- ✅ 核心数据结构完成
- 🚧 Agent实现待完成

**下一步**：
1. 实现Tool Creator Agent（最核心）
2. 实现Tool User Agent
3. 实现Tool Executor
4. 集成测试

**预期效果**：
- 从固定流程 → 真正的Multi-Agent系统
- 从硬编码Prompt → 动态Prompt设计
- 从单一任务 → 多种任务适应

**开始实现！** 🚀
