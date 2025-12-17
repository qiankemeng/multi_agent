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
│   ├── tool_config.py          # 工具配置定义
│   └── interaction_config.py   # 交互配置定义（最重要）
├── experiments/                 # 实验模块
│   ├── __init__.py             # 模块入口
│   └── video_variables.py      # 长视频理解变量定义
├── examples/                    # 示例代码
│   ├── tool_config_example.py  # 工具配置使用示例
│   └── interaction_example.py  # 交互配置使用示例
├── tests/                       # 测试代码
│   ├── test_tool_config.py     # 工具配置测试
│   └── test_interaction_config.py  # 交互配置测试
├── docs/                        # 文档目录
│   ├── PROJECT_TASK.md         # 项目任务说明文档（重要）
│   ├── VIDEO_VARIABLES.md      # 长视频理解变量表文档（重要）
│   ├── INTERACTION_CONFIG_GUIDE.md  # 交互配置系统详细文档
│   ├── TOOL_CONFIG_GUIDE.md    # 工具配置系统详细文档
│   ├── VARIABLE_ORGANIZATION.md  # 变量组织总结
│   └── REFACTOR_SUMMARY.md     # 重构完成总结
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

## 快速开始

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
```

### 4. 使用长视频理解变量

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

### 当前阶段：基础设施完成 ✅
- [x] 定义项目核心任务（长视频理解）
- [x] 定义交互配置变量
- [x] 定义工具配置变量
- [x] 定义长视频理解数据变量
- [x] 定义原子操作

### 下一阶段：实现MVP实验
- [ ] 实现视频预处理模块（提取元数据、分段、帧采样）
- [ ] 实现MLLM API调用封装
- [ ] 实现工具创建Agent（基于MLLM）
- [ ] 实现工具使用Agent（基于MLLM）
- [ ] 运行端到端实验
- [ ] 验证和评估结果

### 后续计划
- [ ] 优化分段策略
- [ ] 实现多种MLLM支持
- [ ] 成本优化和缓存机制
- [ ] 添加更多视频理解任务
- [ ] 性能优化和并行处理

## 文档

### 核心文档（必读）
- **[docs/PROJECT_TASK.md](./docs/PROJECT_TASK.md)** - 项目任务说明（明确长视频理解任务）
- **[docs/VIDEO_VARIABLES.md](./docs/VIDEO_VARIABLES.md)** - 长视频理解变量表文档
- **[docs/INTERACTION_CONFIG_GUIDE.md](./docs/INTERACTION_CONFIG_GUIDE.md)** - 交互配置系统详细文档

### 参考文档
- [CLAUDE.md](./CLAUDE.md) - Claude Code开发指南
- [docs/TOOL_CONFIG_GUIDE.md](./docs/TOOL_CONFIG_GUIDE.md) - 工具配置系统详细文档
- [docs/VARIABLE_ORGANIZATION.md](./docs/VARIABLE_ORGANIZATION.md) - 变量组织总结
- [docs/REFACTOR_SUMMARY.md](./docs/REFACTOR_SUMMARY.md) - 重构完成总结

## 技术栈

- **语言**: Python 3.12+
- **MLLM API**: GPT-4V / Claude / Gemini（待集成）
- **视频处理**: OpenCV / ffmpeg（待集成）
- **配置管理**: dataclass + Enum
- **测试**: pytest

## 贡献

欢迎提出改进建议！

---

**注意**: 本项目专注于长视频理解任务，通过多Agent协作和MLLM API调用实现视频内容的深度理解。
