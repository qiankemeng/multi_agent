# Multi-Agent架构重设计方案

## 当前问题分析

### 现有架构的问题
```python
# 当前是固定流程，没有agent自主决策
def run_video_qa(video, question):
    # 固定步骤1: 提取元数据
    meta = extract_metadata(video)
    # 固定步骤2: 分段
    segments = segment(meta)
    # 固定步骤3: 分析每个segment
    for seg in segments:
        analyze(seg)
    # 固定步骤4: 回答问题
    answer = qa(question)
```

**问题**：
1. ❌ 流程固定，无法适应不同任务
2. ❌ 没有真正的agent决策
3. ❌ Prompt硬编码，无法动态优化
4. ❌ 无法根据任务设计专门的工具

---

## 新架构设计

### 核心理念

**Two-Agent System**:

```
┌─────────────────────────────────────────────────────────┐
│                        用户任务                          │
│  "分析这个视频并回答：视频中发生了什么？"                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
         ┌──────────────┐
         │ Tool Creator │  设计工具
         │    Agent     │
         └──────┬───────┘
                │ 输出: 工具集
                │ - segment_analyzer_tool
                │ - frame_captioner_tool
                │ - qa_answerer_tool
                │
                ▼
         ┌──────────────┐
         │  Tool User   │  执行工具
         │    Agent     │
         └──────┬───────┘
                │
                ▼
            最终答案
```

---

## 数据结构设计

### 1. Tool（工具定义）

```python
@dataclass
class Tool:
    """
    工具定义 - 由Tool Creator Agent设计
    """
    tool_id: str                    # 工具唯一标识
    tool_name: str                  # 工具名称
    description: str                # 工具描述

    # 核心：Prompt设计
    purpose: str                    # 工具目的
    prompt_template: str            # Prompt模板（包含占位符）
    system_prompt: str              # 系统提示

    # 参数定义
    parameters: Dict[str, ToolParameter]  # 输入参数
    output_schema: Dict[str, Any]         # 输出格式

    # 使用的原子操作
    atomic_operations: List[str]    # 如 ["SAMPLE", "CALL_MODEL"]

    # 使用指南
    usage_example: str              # 使用示例
    best_practices: List[str]       # 最佳实践

    # 元数据
    created_by: str                 # 创建者（agent_id）
    created_at: str
    version: str
```

**示例**:
```python
Tool(
    tool_id="segment_analyzer_v1",
    tool_name="Segment Video Analyzer",
    description="分析视频片段，生成结构化描述",

    purpose="理解视频片段的内容、场景、事件和对象",

    prompt_template="""分析视频片段 [{start_sec}s - {end_sec}s]。

以下是从该片段采样的{num_frames}帧关键画面。

请提供：
1. 场景描述：这个片段展示了什么场景？
2. 主要事件：发生了什么事情？按时间顺序列出。
3. 关键对象：画面中有哪些重要的人物、物体？
4. 情感/氛围：整体氛围如何（紧张、欢乐、平静等）？

输出格式：
Scene: [场景描述]
Events: [事件1, 事件2, ...]
Objects: [对象1, 对象2, ...]
Mood: [情感/氛围]""",

    system_prompt="你是一个专业的视频内容分析师，擅长从视频帧中理解故事情节和场景细节。",

    parameters={
        "segment": ToolParameter("segment", "Segment", required=True),
        "num_frames": ToolParameter("num_frames", "int", default=5),
        "detail_level": ToolParameter("detail_level", "str", default="medium")
    },

    atomic_operations=["SAMPLE", "CALL_MODEL"],

    usage_example="tool.execute(segment=seg1, num_frames=3)",

    created_by="tool_creator_agent_001"
)
```

### 2. AgentAction（Agent行动记录）

```python
@dataclass
class AgentAction:
    """
    Agent的单次行动记录
    """
    action_id: str
    agent_id: str
    agent_type: str         # "tool_creator" or "tool_user"

    action_type: str        # "design_tool", "use_tool", "plan", "reason"

    # 行动内容
    tool: Optional[Tool]    # 设计的工具或使用的工具
    inputs: Dict[str, Any]  # 输入参数
    outputs: Dict[str, Any] # 输出结果

    # 推理过程
    reasoning: str          # Agent的思考过程
    confidence: float       # 置信度

    # 统计
    tokens_used: int
    cost_usd: float
    duration_ms: float

    timestamp: str
```

### 3. AgentPlan（执行计划）

```python
@dataclass
class AgentPlan:
    """
    Tool User Agent的执行计划
    """
    plan_id: str
    task_description: str

    # 计划步骤
    steps: List[PlanStep]

    # 可用资源
    available_tools: List[Tool]

    # 执行状态
    current_step: int
    status: str  # "planning", "executing", "completed"

    reasoning: str  # 为什么这样规划

@dataclass
class PlanStep:
    """计划中的单个步骤"""
    step_id: str
    tool_name: str
    inputs: Dict[str, Any]
    expected_output: str
    dependencies: List[str]  # 依赖哪些步骤
```

---

## Agent设计

### Agent 1: Tool Creator Agent

**职责**：根据任务需求设计工具

**输入**：
- 任务描述（如"分析视频并回答问题"）
- 可用的原子操作（SAMPLE, SEGMENT, CALL_MODEL, BBOX）
- 约束条件（成本、时间等）

**输出**：
- 工具集（List[Tool]）
- 设计说明

**工作流程**：
```python
class ToolCreatorAgent:
    def design_tools(self, task_description: str) -> List[Tool]:
        # Step 1: 理解任务
        task_analysis = self._analyze_task(task_description)

        # Step 2: 识别子任务
        subtasks = self._decompose_task(task_analysis)

        # Step 3: 为每个子任务设计工具
        tools = []
        for subtask in subtasks:
            tool = self._design_tool(subtask)
            tools.append(tool)

        # Step 4: 优化工具集
        optimized_tools = self._optimize_toolset(tools)

        return optimized_tools

    def _design_tool(self, subtask: dict) -> Tool:
        # 使用MLLM设计工具的prompt
        design_prompt = f"""你是一个工具设计专家。

任务描述: {subtask['description']}
输入数据: {subtask['inputs']}
期望输出: {subtask['outputs']}

请设计一个工具来完成这个任务：

1. 工具名称和描述
2. 设计一个清晰、有效的Prompt模板
3. 定义输入参数
4. 定义输出格式
5. 选择需要的原子操作

输出JSON格式的工具定义。"""

        # 调用MLLM
        response = self.mllm_client.call(design_prompt)

        # 解析并创建Tool对象
        tool = self._parse_tool_design(response)

        return tool
```

**关键能力**：
- ✅ 任务分解
- ✅ Prompt设计（最核心）
- ✅ 参数定义
- ✅ 工具优化

### Agent 2: Tool User Agent

**职责**：使用工具完成任务

**输入**：
- 任务描述
- 可用工具集（Tool Creator设计的）
- 输入数据（视频、问题等）

**输出**：
- 任务结果
- 执行记录

**工作流程**：
```python
class ToolUserAgent:
    def execute_task(self, task: str, tools: List[Tool], data: dict) -> dict:
        # Step 1: 规划执行步骤
        plan = self._create_plan(task, tools, data)

        # Step 2: 执行计划
        results = {}
        for step in plan.steps:
            # 选择工具
            tool = self._select_tool(step.tool_name, tools)

            # 准备输入
            inputs = self._prepare_inputs(step, results)

            # 执行工具
            output = self._execute_tool(tool, inputs)

            # 记录结果
            results[step.step_id] = output

        # Step 3: 整合结果
        final_result = self._aggregate_results(results)

        return final_result

    def _create_plan(self, task: str, tools: List[Tool], data: dict) -> AgentPlan:
        # 使用MLLM进行规划
        planning_prompt = f"""你是一个任务规划专家。

任务: {task}

可用工具:
{self._format_tools(tools)}

输入数据: {data}

请创建一个执行计划：
1. 列出需要的步骤
2. 每步使用哪个工具
3. 步骤之间的依赖关系
4. 预期的输出

输出JSON格式的执行计划。"""

        response = self.mllm_client.call(planning_prompt)
        plan = self._parse_plan(response)

        return plan

    def _execute_tool(self, tool: Tool, inputs: dict) -> dict:
        # 根据tool定义执行原子操作
        if "SAMPLE" in tool.atomic_operations:
            frames = self.atomic_ops.sample(...)

        if "CALL_MODEL" in tool.atomic_operations:
            # 使用tool的prompt_template
            prompt = tool.prompt_template.format(**inputs)
            response = self.atomic_ops.call_model(
                prompt=prompt,
                system_prompt=tool.system_prompt,
                ...
            )

        return response
```

**关键能力**：
- ✅ 任务规划
- ✅ 工具选择
- ✅ 执行协调
- ✅ 结果整合

---

## 协作机制

### 完整工作流程

```python
class MultiAgentVideoQA:
    def __init__(self):
        self.tool_creator = ToolCreatorAgent()
        self.tool_user = ToolUserAgent()
        self.atomic_ops = AtomicOperationsImplementation()

    def process(self, video_path: str, question: str):
        # Phase 1: Tool Creation
        task_description = f"""
        任务类型: 视频问答
        视频: {video_path}
        问题: {question}

        需要分析视频内容并回答用户问题。
        """

        tools = self.tool_creator.design_tools(task_description)

        print(f"✓ Tool Creator设计了{len(tools)}个工具:")
        for tool in tools:
            print(f"  - {tool.tool_name}: {tool.description}")

        # Phase 2: Tool Usage
        result = self.tool_user.execute_task(
            task=task_description,
            tools=tools,
            data={"video_path": video_path, "question": question}
        )

        return result
```

---

## 示例场景

### 场景1: 标准视频问答

**用户输入**:
```
视频: "soccer_game.mp4"
问题: "比赛中发生了什么？"
```

**Tool Creator设计工具**:
```python
tools = [
    Tool(
        name="segment_video",
        purpose="将视频分段以便分析",
        prompt_template="将视频分成有意义的段落..."
    ),
    Tool(
        name="analyze_segment",
        purpose="分析单个视频段落",
        prompt_template="分析这个视频片段[{start}-{end}]，描述场景、事件、对象..."
    ),
    Tool(
        name="answer_question",
        purpose="基于分析结果回答问题",
        prompt_template="基于以下视频分析：\n{analysis}\n\n回答问题：{question}"
    )
]
```

**Tool User执行**:
```python
plan = [
    Step1: segment_video(video) → segments
    Step2: for seg in segments: analyze_segment(seg) → analyses
    Step3: answer_question(analyses, question) → answer
]

执行结果: "比赛开始时，蓝队快速进攻..."
```

### 场景2: 详细场景分析

**用户输入**:
```
视频: "movie_clip.mp4"
问题: "这个场景的情感氛围是什么？"
```

**Tool Creator可能设计**:
```python
tools = [
    Tool(
        name="emotion_analyzer",
        purpose="分析视频情感和氛围",
        prompt_template="分析这些画面的情感氛围：\n- 人物表情\n- 场景光线\n- 动作节奏..."
    ),
    Tool(
        name="audio_mood_analyzer",  # 如果支持音频
        purpose="分析音频情感",
        prompt_template="根据音乐、对话语调分析情感..."
    )
]
```

---

## 优势

### vs 固定流程

| 特性 | 固定流程 | Multi-Agent |
|------|---------|-------------|
| 灵活性 | ❌ 固定步骤 | ✅ 动态适应 |
| Prompt质量 | ❌ 硬编码 | ✅ 专门设计 |
| 任务适应性 | ❌ 单一任务 | ✅ 多种任务 |
| 可扩展性 | ❌ 难以扩展 | ✅ 易于添加工具 |
| 可解释性 | ⚠️ 一般 | ✅ 有推理过程 |

### 新架构优势

1. **动态工具设计**：根据任务设计专门的工具
2. **Prompt优化**：Tool Creator专注于设计高质量prompt
3. **灵活执行**：Tool User根据情况选择工具
4. **可追踪**：记录Agent的推理和决策过程
5. **可扩展**：轻松添加新的原子操作和工具类型

---

## 实现计划

### Phase 1: 核心数据结构
- [ ] Tool数据类
- [ ] AgentAction数据类
- [ ] AgentPlan数据类

### Phase 2: Tool Creator Agent
- [ ] 任务分析能力
- [ ] Prompt设计能力
- [ ] 工具定义生成

### Phase 3: Tool User Agent
- [ ] 任务规划能力
- [ ] 工具选择逻辑
- [ ] 执行协调

### Phase 4: 协作机制
- [ ] Agent通信
- [ ] 工具注册和查询
- [ ] 执行追踪

### Phase 5: 测试和优化
- [ ] 端到端测试
- [ ] Prompt优化
- [ ] 性能调优

---

## 总结

**核心改变**：
```
Before: 固定流程
video → extract → segment → analyze → qa → answer

After: Multi-Agent
task → [Tool Creator designs tools] → [Tool User uses tools] → answer
```

**关键创新**：
1. **Tool Creator设计prompt** - 不再硬编码
2. **Tool User自主规划** - 不再固定步骤
3. **工具化封装** - 可复用、可组合
4. **完整追踪** - 知道"为什么"这样做

**下一步**：实现这个新架构！
