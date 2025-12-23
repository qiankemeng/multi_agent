# 长视频理解多Agent系统

## 项目目标

本项目设计一套基于多Agent的**长视频理解**框架，包含：
- **工具创建Agent**: 通过MLLM API动态创建视频处理工具
- **工具使用Agent**: 通过MLLM API使用工具处理视频数据

**核心任务**: 对长视频进行分段处理，通过多模态大语言模型（MLLM）理解每个片段，最终整合生成完整的视频理解。

**重点关注**:
- 上下文管理（跨片段信息传递）
- MLLM API调用和成本控制
- 多Agent之间的协作
- 代码易于维护和修改

## 项目结构

```
multi_agent/
├── config/                      # 配置模块（核心）
│   ├── __init__.py             # 模块入口
│   ├── settings.py             # 全局配置管理（新）
│   ├── tool_config.py          # 工具配置定义
│   └── interaction_config.py   # 交互配置定义（最重要）
├── agents/                      # Agent实现模块
│   ├── __init__.py             # 模块入口
│   ├── mllm_client.py          # MLLM API调用封装
│   ├── tool_creator_agent.py   # 工具创建Agent
│   └── tool_user_agent.py      # 工具使用Agent
├── experiments/                 # 实验模块
│   ├── __init__.py             # 模块入口
│   └── video_variables.py      # 长视频理解变量定义
├── visualization/               # 可视化模块
│   ├── __init__.py             # 模块入口
│   ├── visualizer.py           # 核心可视化引擎
│   ├── generate_visualization.py  # 可视化生成脚本
│   ├── template.html           # HTML模板
│   ├── README.md               # 可视化文档
│   └── USAGE.md                # 详细使用指南
├── examples/                    # 示例代码
│   ├── tool_config_example.py  # 工具配置使用示例
│   ├── interaction_example.py  # 交互配置使用示例
│   └── agents_example.py       # Agent使用示例
├── tests/                       # 测试代码
│   ├── test_tool_config.py     # 工具配置测试
│   ├── test_interaction_config.py  # 交互配置测试
│   └── test_agents.py          # Agent测试
├── docs/                        # 文档目录
│   ├── PROJECT_TASK.md         # 项目任务说明文档（重要）
│   ├── VIDEO_VARIABLES.md      # 长视频理解变量表文档（重要）
│   ├── INTERACTION_CONFIG_GUIDE.md  # 交互配置系统详细文档
│   ├── TOOL_CONFIG_GUIDE.md    # 工具配置系统详细文档
│   ├── CONFIGURATION.md        # 配置指南（新）
│   ├── VARIABLE_ORGANIZATION.md  # 变量组织总结
│   └── REFACTOR_SUMMARY.md     # 重构完成总结
├── .env.example                 # 配置模板（新）
├── .env                         # 实际配置（不提交，新）
├── .gitignore                   # Git忽略文件
├── CLAUDE.md                    # Claude Code开发指南
└── readme.md                    # 项目说明（本文件）
```

## 已完成

✅ **项目任务定义** - 明确长视频理解的核心任务

- 任务领域：长视频理解与分析
- Agent实现：通过MLLM API（GPT-4V, Claude, Gemini等）
- 系统架构：多Agent协作框架

详见: [docs/PROJECT_TASK.md](./docs/PROJECT_TASK.md)

---

✅ **交互配置系统** - 多Agent交互的核心变量定义

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

详见: [docs/INTERACTION_CONFIG_GUIDE.md](./docs/INTERACTION_CONFIG_GUIDE.md)

---

✅ **工具配置系统** - 定义和管理工具的配置

核心特性：
- 灵活的配置结构（使用dataclass）
- 类型安全（类型提示 + 枚举）
- 参数验证机制
- 全局注册表管理
- 支持增删改查操作

详见: [docs/TOOL_CONFIG_GUIDE.md](./docs/TOOL_CONFIG_GUIDE.md)

---

✅ **长视频理解变量系统** - 视频处理的数据变量定义

**核心变量**:

**基础视频变量**:
- **VideoMeta**: 视频元数据（video_id, duration, fps, frames, width, height）
- **Segment**: 视频分段（time_span, segment_index）
- **Frame**: 视频帧（frame_index, timestamp, image_data）
- **TimeSpan**: 时间跨度（start_sec, end_sec）

**视频理解结果**:
- **FrameCaption**: 帧描述
- **SegmentCaption**: 分段描述
- **VideoUnderstanding**: 完整视频理解

**MLLM API交互**:
- **MLLMRequest**: MLLM API请求（prompt, images, model_name）
- **MLLMResponse**: MLLM API响应（text, tokens, cost）

**原子操作**:
- **AtomicOperation**: 原子操作定义
- **AtomicOperations**: 预定义操作（视频分段、帧提取、描述生成等）

**实验记录**:
- **VideoExperimentRun**: 实验运行记录（追踪API调用次数、token使用、成本）

详见: [docs/VIDEO_VARIABLES.md](./docs/VIDEO_VARIABLES.md)

---

✅ **Agent实现** - 完成两个核心Agent的实现

**MLLM API封装**:
- **MLLMClient**: OpenAI API调用封装，支持文本和图像输入
- **MLLMClientConfig**: 客户端配置（API key、模型、温度等）
- 自动token统计和成本计算
- 错误处理和重试机制

**ToolCreatorAgent (工具创建Agent)**:
- 通过MLLM API动态生成Python工具代码
- 输入：工具需求描述、参数要求、约束条件
- 输出：完整的可执行Python代码
- 自动代码提取和验证

**ToolUserAgent (工具使用Agent)**:
- 通过MLLM Vision API分析视频内容
- 支持多种分析任务：帧描述、片段分析、摘要生成、问答
- 自动提取关键信息（事件、对象、场景）
- 上下文管理和多轮对话支持

详见示例: `python examples/agents_example.py`

---

✅ **项目可视化系统** - 动态可视化项目架构

**核心功能**:
- 自动分析项目结构（18个模块、50个类、49个函数、5834行代码）
- 交互式Web界面展示类关系图谱
- 6个可视化视图：项目概览、模块详情、类结构、关系图谱、视频工作流、文件树
- D3.js力导向图展示类继承关系
- 实时搜索和过滤功能

**快速使用**:
```bash
# 生成可视化
python visualization/generate_visualization.py

# 启动本地服务器查看
python -m http.server -d visualization/output 8000
# 访问 http://localhost:8000
```

详见: [visualization/README.md](./visualization/README.md)

---

✅ **配置管理系统** - 统一的配置管理

**核心功能**:
- 基于`.env`文件的配置管理
- 分层配置：OpenAI、Claude、Gemini API配置
- Agent特定配置：工具创建Agent和工具使用Agent
- 视频处理配置：分段策略、帧采样等
- 成本控制和性能配置

**配置文件**:
- `.env.example` - 配置模板（包含所有可用选项）
- `.env` - 实际配置（不会提交到git）
- `config/settings.py` - 配置加载和管理

**快速配置**:
```bash
# 1. 复制配置模板
cp .env.example .env

# 2. 编辑配置文件，设置API密钥
# OPENAI_API_KEY=your-api-key-here

# 3. 验证配置
python config/settings.py
```

详见: [docs/CONFIGURATION.md](./docs/CONFIGURATION.md)

## 快速开始

### 0. 可视化项目架构（推荐首先查看）

```bash
# 生成项目可视化
python visualization/generate_visualization.py

# 在浏览器中查看（推荐使用HTTP服务器）
python -m http.server -d visualization/output 8000
# 访问 http://localhost:8000
```

可视化界面包含：
- 📊 项目统计信息
- 🏗️ 类结构浏览
- 🔗 交互式关系图谱
- 🎬 视频理解工作流展示
- 📁 项目文件树

### 1. 查看交互配置示例

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

# 测试Agent实现
python tests/test_agents.py
```

### 4. 使用Agent（需要OPENAI_API_KEY）

```bash
# 查看Agent使用示例
python examples/agents_example.py

# 设置API key
export OPENAI_API_KEY='your-api-key'
```

示例代码：

```python
from agents import (
    ToolCreatorAgent,
    ToolUserAgent,
    ToolCreationRequest,
    VideoAnalysisRequest
)
from experiments import AnalysisTask, Frame

# 创建工具创建Agent
creator = ToolCreatorAgent(agent_id="creator_001")

# 请求创建工具
request = ToolCreationRequest(
    request_id="req_001",
    tool_name="extract_keyframes",
    tool_description="从视频中提取关键帧",
    input_requirements="视频路径，采样间隔",
    output_requirements="关键帧列表"
)

result = creator.create_tool(request)
print(result.tool_code)

# 创建工具使用Agent
user = ToolUserAgent(agent_id="user_001")

# 分析视频帧
frames = [...]  # Frame对象列表
analysis_request = VideoAnalysisRequest(
    request_id="req_002",
    task=AnalysisTask.CAPTION,
    frames=frames
)

analysis_result = user.analyze(analysis_request)
print(analysis_result.frame_captions)
```

### 5. 使用长视频理解变量

```python
from experiments import (
    VideoMeta, Segment, TimeSpan,
    FrameCaption, SegmentCaption,
    MLLMRequest, MLLMResponse,
    VideoExperimentRun
)

# 创建视频元数据
video = VideoMeta(
    video_id="vid_001",
    file_path="/data/videos/sample.mp4",
    duration_sec=300.0,
    fps=30.0,
    num_frames=9000,
    width=1920,
    height=1080
)

# 创建分段
segment = Segment(
    segment_id="seg_001",
    video_id=video.video_id,
    time_span=TimeSpan(start_sec=0.0, end_sec=30.0),
    segment_index=0,
    total_segments=10,
    start_frame=0,
    end_frame=900,
    num_frames=900
)

# 调用MLLM API
mllm_request = MLLMRequest(
    request_id="req_001",
    model_name="gpt-4-vision",
    prompt="请描述这个视频片段中发生的事情",
    images=["base64_image_data"],
    task=AnalysisTask.CAPTION
)
```

## 长视频理解工作流程

```
1. 视频输入
    ↓
2. 提取视频元数据 (VideoMeta)
    ↓
3. 视频分段 (Segment × N)
    ↓
4. 对每个片段:
    - 提取关键帧 (Frame)
    - 调用MLLM API (MLLMRequest)
    - 生成片段描述 (SegmentCaption)
    ↓
5. 整合所有片段理解
    ↓
6. 生成完整视频理解 (VideoUnderstanding)
```

## 下一步计划

### 当前阶段：Agent实现完成 ✅
- [x] 定义项目核心任务（长视频理解）
- [x] 定义交互配置变量
- [x] 定义工具配置变量
- [x] 定义长视频理解数据变量
- [x] 定义原子操作
- [x] 实现MLLM API调用封装
- [x] 实现工具创建Agent（基于MLLM）
- [x] 实现工具使用Agent（基于MLLM）

### 下一阶段：视频处理与端到端实验
- [ ] 实现视频预处理模块（提取元数据、分段、帧采样）
- [ ] 集成OpenCV/ffmpeg进行视频处理
- [ ] 实现完整的视频理解pipeline
- [ ] 运行端到端实验
- [ ] 验证和评估结果
- [ ] 成本分析和优化

### 后续计划
- [ ] 优化分段策略
- [ ] 实现多种MLLM支持
- [ ] 成本优化和缓存机制
- [ ] 添加更多视频理解任务
- [ ] 性能优化和并行处理

## 文档

### 核心文档（必读）
- **[docs/PROJECT_TASK.md](./docs/PROJECT_TASK.md)** - 项目任务说明（明确长视频理解任务）
- **[docs/ATOMIC_OPERATIONS.md](./docs/ATOMIC_OPERATIONS.md)** - 4个核心原子操作的完整规范
- **[docs/VIDEO_VARIABLES.md](./docs/VIDEO_VARIABLES.md)** - 长视频理解变量表文档
- **[docs/INTERACTION_CONFIG_GUIDE.md](./docs/INTERACTION_CONFIG_GUIDE.md)** - 交互配置系统详细文档
- **[visualization/README.md](./visualization/README.md)** - 项目可视化系统文档

### 参考文档
- [CLAUDE.md](./CLAUDE.md) - Claude Code开发指南
- [docs/TOOL_CONFIG_GUIDE.md](./docs/TOOL_CONFIG_GUIDE.md) - 工具配置系统详细文档
- [docs/CONFIGURATION.md](./docs/CONFIGURATION.md) - 配置管理指南
- [visualization/USAGE.md](./visualization/USAGE.md) - 可视化系统详细使用指南

## 技术栈

- **语言**: Python 3.12+
- **MLLM API**: GPT-4V / Claude / Gemini（待集成）
- **视频处理**: OpenCV / ffmpeg（待集成）
- **配置管理**: dataclass + Enum
- **测试**: pytest

## Python文件说明

### 核心模块

#### config/ - 配置模块
- **`config/__init__.py`** - 统一导出所有配置类
- **`config/settings.py`** - 全局配置管理系统（基于.env文件）
  - 管理OpenAI、Claude、Gemini API配置
  - Agent特定配置（Tool Creator、Tool User）
  - 视频处理、成本控制、性能配置
- **`config/interaction_config.py`** - 多Agent交互配置（核心）
  - `Message`: Agent间通信消息
  - `ToolCallRequest/Response`: 工具调用协议
  - `Context`: 上下文管理（系统记忆）
  - `AgentState`: Agent状态追踪
  - `InteractionConfig`: 系统级交互配置
- **`config/tool_config.py`** - 工具配置系统
  - `ToolConfig`: 工具定义
  - `ToolParameter`: 参数定义和验证
  - `ToolRegistry`: 全局工具注册表

#### experiments/ - 实验模块
- **`experiments/__init__.py`** - 导出所有视频理解变量
- **`experiments/video_variables.py`** - 长视频理解核心变量定义
  - **基础视频变量**: `VideoMeta`, `Segment`, `Frame`, `TimeSpan`
  - **视频理解结果**: `FrameCaption`, `SegmentCaption`, `VideoUnderstanding`
  - **MLLM API交互**: `MLLMRequest`, `MLLMResponse`, `ModelResponse`
  - **原子操作**: `AtomicOperations` (4个核心操作：SAMPLE, SEGMENT, CALL_MODEL, BBOX)
  - **实验追踪**: `VideoExperimentRun`

#### agents/ - Agent实现模块
- **`agents/__init__.py`** - 导出所有Agent组件
- **`agents/mllm_client.py`** - MLLM API调用封装
  - `MLLMClient`: 统一的MLLM API客户端
  - `MLLMClientConfig`: 客户端配置
  - 支持OpenAI API，自动token统计和成本计算
- **`agents/tool_creator_agent.py`** - 工具创建Agent
  - 通过MLLM API动态生成Python工具代码
  - 根据需求描述组合原子操作
  - 返回完整可执行代码
- **`agents/tool_user_agent.py`** - 工具使用Agent
  - 通过MLLM Vision API分析视频内容
  - 支持任务：帧描述、片段分析、摘要生成、问答
  - 自动提取关键信息（事件、对象、场景）

#### processors/ - 视频处理模块 ✅ (Phase 1&2 完成)
- **`processors/__init__.py`** - 导出视频处理组件
- **`processors/video_processor.py`** - 视频处理核心实现 ✅ (Phase 1)
  - `VideoProcessor`: 视频预处理类
  - 元数据提取：使用opencv读取视频信息（时长、FPS、分辨率等）
  - 视频分段：固定时长分段、自定义断点分段
  - 帧采样：均匀采样、指定时间戳提取
  - 帧保存：自动保存到临时目录
- **`processors/atomic_operations_impl.py`** - 原子操作实现 ✅ (Phase 2)
  - `AtomicOperationsImplementation`: 4个核心原子操作
  - SAMPLE操作：帧采样（uniform, keyframe, timestamps）
  - SEGMENT操作：视频分段（fixed_duration, scene_change, custom）
  - CALL_MODEL操作：模型调用（MLLM, ASR）- 集成MLLMClient
  - BBOX操作：边界框标注
- **`processors/video_qa_pipeline.py`** - 端到端VideoQA Pipeline ✅ (Phase 3)
  - `VideoQAPipeline`: 完整的视频问答流程
  - 6步工作流：元数据提取 → 分段 → 采样 → 分析 → 整合 → 回答
  - 集成Phase 1和Phase 2所有功能
  - VideoExperimentRun实验追踪系统
  - 灵活的配置系统和错误处理
  - 支持Dry-run模式（无API key测试）

#### visualization/ - 可视化模块
- **`visualization/__init__.py`** - 导出可视化组件
- **`visualization/visualizer.py`** - 项目可视化核心引擎
  - 自动分析项目结构
  - 生成类关系图谱
  - 支持多种视图展示
- **`visualization/generate_visualization.py`** - 可视化生成脚本
  - 一键生成交互式Web可视化页面

### 示例和测试

#### examples/ - 使用示例
- **`examples/interaction_example.py`** - 交互配置使用示例
  - 演示Agent间消息传递
  - 演示工具调用流程
  - 演示上下文管理
- **`examples/tool_config_example.py`** - 工具配置使用示例
  - 演示工具定义和注册
  - 演示参数验证
- **`examples/agents_example.py`** - Agent使用示例
  - 演示MLLM客户端使用
  - 演示工具创建Agent
  - 演示工具使用Agent
  - 演示完整视频理解工作流
- **`examples/atomic_operations_example.py`** - 原子操作示例
  - 演示4个核心原子操作的使用
- **`examples/video_processor_example.py`** - 视频处理示例 ✅ (Phase 1)
  - 演示视频元数据提取
  - 演示视频分段（固定时长、自定义断点）
  - 演示帧采样（均匀采样、指定时间戳）
  - 完整的端到端测试
- **`examples/atomic_operations_impl_example.py`** - 原子操作示例 ✅ (Phase 2)
  - 演示SAMPLE操作（uniform, timestamps）
  - 演示SEGMENT操作（fixed_duration, custom）
  - 演示CALL_MODEL操作（MLLM集成）
  - 演示BBOX操作（边界框绘制）
  - 演示组合工作流
- **`examples/video_qa_pipeline_example.py`** - VideoQA Pipeline示例 ✅ (Phase 3)
  - 演示完整端到端VideoQA流程
  - 4个示例场景：基本QA、自定义配置、多问题、元数据预览
  - 展示实验追踪和成本估算
  - 支持无API key的Dry-run模式
  - 完整的错误处理和进度输出
- **`examples/dynamic_parameters_example.py`** - 动态参数传递示例 ✅
  - 演示5种不同使用场景的参数传递
  - 场景1：快速预览（大片段，少帧数）
  - 场景2：详细分析（小片段，多帧数）
  - 场景3：自适应采样（根据位置动态调整）
  - 场景4：自定义时间戳（精确指定关键时刻）
  - 场景5：自定义分段（按章节结构分段）
  - 验证原子操作的参数灵活性
  - 运行: `python examples/dynamic_parameters_example.py`

#### tests/ - 测试代码
- **`tests/test_interaction_config.py`** - 交互配置测试
- **`tests/test_tool_config.py`** - 工具配置测试
- **`tests/test_agents.py`** - Agent实现测试
- **`tests/test_atomic_operations.py`** - 原子操作测试
- **`tests/test_video_qa_pipeline.py`** - VideoQA Pipeline独立测试套件 ✅
  - 测试VideoProcessor基础功能
  - 测试AtomicOperations所有操作
  - 测试Pipeline配置系统
  - 测试完整工作流（Dry-run）
  - 测试实验追踪系统
  - 运行: `python tests/test_video_qa_pipeline.py`

### 配置和文档

- **`.env.example`** - 配置模板 ✅ **重要更新**
  - 重新组织配置结构（全局配置 vs 默认值）
  - 添加`DEFAULT_`前缀区分可覆盖的默认值
  - 详细注释说明参数传递优先级
  - 支持动态参数传递（调用时参数 > 默认值 > 硬编码）
- **`.env`** - 实际配置文件（不提交到git）
- **`CLAUDE.md`** - Claude Code开发指南
- **`readme.md`** - 项目说明（本文件）

#### 配置架构说明 ⭐

系统采用**三层参数体系**：

1. **全局配置**（Global Settings）- 系统级，不可运行时更改
   - API Keys: `OPENAI_API_KEY`
   - API行为: `MLLM_REQUEST_TIMEOUT`, `MLLM_MAX_RETRIES`
   - 成本控制: `MAX_REQUEST_COST`, `MAX_DAILY_COST`
   - 数据路径: `DATA_DIR`, `VIDEO_DIR`, `TEMP_DIR`

2. **默认值**（Default Values）- 可在运行时被覆盖
   - 原子操作默认值（带`DEFAULT_`前缀）
   - `DEFAULT_SEGMENT_DURATION=30` - 分段时长默认值
   - `DEFAULT_FRAMES_PER_SEGMENT=5` - 采样帧数默认值
   - `DEFAULT_SAMPLING_METHOD=uniform` - 采样方法默认值

3. **运行时参数**（Runtime Parameters）- 调用时动态指定
   - Tool Creator创建工具时暴露参数
   - Tool User调用时传递具体值
   - 示例: `atomic_ops.sample(params={"num_frames": 10})`

**参数优先级**: 调用时参数 > .env默认值 > 硬编码默认值

**查看完整说明**: `docs/CONFIG_ARCHITECTURE_ANALYSIS.md`

#### docs/ - 实现文档
- **`docs/GAP_ANALYSIS.md`** - 差距分析文档（Phase 1-4规划）
- **`docs/PHASE1_SUMMARY.md`** - Phase 1实现总结（视频处理基础）✅
- **`docs/PHASE2_SUMMARY.md`** - Phase 2实现总结（原子操作）✅
- **`docs/PHASE3_SUMMARY.md`** - Phase 3实现总结（端到端Pipeline）✅
- **`docs/PHASE3_TEST_REPORT.md`** - Phase 3独立测试报告（5/5通过）✅
- **`docs/CONFIG_ARCHITECTURE_ANALYSIS.md`** - 配置架构分析与重构方案 ✅
- **`docs/CONFIG_FIX_SUMMARY.md`** - 配置架构修复总结 ✅
- **`docs/PROJECT_TASK.md`** - 项目任务定义
- **`docs/VIDEO_VARIABLES.md`** - 视频变量参考
- **`docs/INTERACTION_CONFIG_GUIDE.md`** - 交互配置指南
- **`docs/TOOL_CONFIG_GUIDE.md`** - 工具配置指南
- **`docs/ATOMIC_OPERATIONS.md`** - 原子操作文档

## 贡献

欢迎提出改进建议！

---

**注意**: 本项目专注于长视频理解任务，通过多Agent协作和MLLM API调用实现视频内容的深度理解。
