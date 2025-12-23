# 视频QA任务实现差距分析

**分析日期**: 2025-12-18
**当前状态**: MVP基础架构完成，缺少视频处理实现

## 完整视频QA任务流程

一个完整的视频QA任务需要以下步骤：

```
输入：视频文件(source.mp4) + 问题("视频中发生了什么?")
    ↓
1. 提取视频元数据 → VideoMeta
    ↓
2. 视频分段 → List[Segment]
    ↓
3. 对每个片段提取关键帧 → List[Frame]
    ↓
4. 使用MLLM分析帧/片段 → SegmentCaption
    ↓
5. 整合所有片段理解 → VideoUnderstanding
    ↓
6. 基于理解回答问题 → Answer
    ↓
输出：问题的答案
```

## 当前已完成 ✅

### 1. 数据结构定义 ✅
**文件**: `experiments/video_variables.py`

- ✅ `VideoMeta` - 视频元数据
- ✅ `Segment` - 视频片段
- ✅ `Frame` - 视频帧
- ✅ `TimeSpan` - 时间跨度
- ✅ `FrameCaption` - 帧描述
- ✅ `SegmentCaption` - 片段描述
- ✅ `VideoUnderstanding` - 完整视频理解
- ✅ `MLLMRequest/Response` - MLLM API交互
- ✅ `ModelResponse` - 统一模型响应
- ✅ `VideoExperimentRun` - 实验追踪

### 2. 原子操作定义 ✅
**文件**: `experiments/video_variables.py` + `docs/ATOMIC_OPERATIONS.md`

- ✅ SAMPLE - 采样操作定义
- ✅ SEGMENT - 分段操作定义
- ✅ CALL_MODEL - 模型调用定义
- ✅ BBOX - 边界框定义

### 3. MLLM API封装 ✅
**文件**: `agents/mllm_client.py`

- ✅ `MLLMClient` - OpenAI API调用
- ✅ Token统计和成本计算
- ✅ 错误处理

### 4. Agent实现 ✅
**文件**: `agents/tool_creator_agent.py`, `agents/tool_user_agent.py`

- ✅ Tool Creator Agent - 生成工具代码
- ✅ Tool User Agent - 视频分析（帧描述、片段分析、QA）

### 5. 配置系统 ✅
**文件**: `config/settings.py`, `config/interaction_config.py`, `config/tool_config.py`

- ✅ 全局配置管理
- ✅ Agent交互协议
- ✅ 工具配置系统

## 当前缺失 ❌

### 1. 视频预处理模块 ❌ (最关键)

**缺失内容**：

#### 1.1 视频元数据提取
```python
# 需要实现
def extract_video_metadata(video_path: str) -> VideoMeta:
    """
    从视频文件提取元数据

    需要的库：opencv-cv (cv2) 或 ffmpeg-python

    提取内容：
    - duration_sec
    - fps
    - num_frames
    - width
    - height
    - codec
    """
    pass
```

**依赖**：
- `opencv-python` 或 `ffmpeg-python`
- 需要读取视频文件基本信息

#### 1.2 视频分段实现
```python
# 需要实现
def segment_video(
    video_meta: VideoMeta,
    strategy: str,  # "fixed_duration" | "scene_change" | "custom"
    params: Dict[str, Any]
) -> List[Segment]:
    """
    将视频分割成片段

    策略实现：
    1. fixed_duration: 按固定时长分段（简单）
    2. scene_change: 基于场景变化检测（需要PySceneDetect）
    3. custom: 按自定义时间点分段（简单）
    """
    pass
```

**依赖**：
- 固定时长：无额外依赖
- 场景检测：`scenedetect[opencv]` 或 `opencv-python` + 自定义算法
- 自定义断点：无额外依赖

#### 1.3 帧提取和采样
```python
# 需要实现
def sample_frames(
    video_path: str,
    segment: Optional[Segment],
    method: str,  # "uniform" | "keyframe" | "timestamps"
    params: Dict[str, Any]
) -> List[Frame]:
    """
    从视频或片段中提取帧

    方法实现：
    1. uniform: 均匀采样N帧（简单，用cv2）
    2. keyframe: 基于内容变化检测关键帧（复杂）
    3. timestamps: 在指定时间点提取（简单，用cv2）

    输出：
    - 保存帧图像到临时文件
    - 返回Frame对象列表（包含image_path）
    """
    pass
```

**依赖**：
- `opencv-python` (cv2.VideoCapture)
- 图像保存：`cv2.imwrite()` 或 `PIL`

#### 1.4 边界框绘制
```python
# 需要实现
def draw_bounding_boxes(
    frame: Frame,
    boxes: List[Dict[str, Any]]
) -> Frame:
    """
    在帧上绘制边界框

    输入boxes格式：
    [{
        "bbox": [x, y, w, h],
        "label": str,
        "confidence": float,
        "color": str
    }]

    输出：
    - 保存标注后的图像到新文件
    - 返回新的Frame对象（新image_path）
    """
    pass
```

**依赖**：
- `opencv-python` (cv2.rectangle, cv2.putText)
- 或 `PIL` (ImageDraw)

### 2. 原子操作的实际实现 ❌

**当前状态**: 只有定义，没有可执行的实现

**需要创建**: `processors/atomic_operations_impl.py`

```python
class AtomicOperationsImplementation:
    """
    原子操作的实际实现

    将4个原子操作定义转换为可执行的Python函数
    """

    def sample(self, ...):
        """调用sample_frames()"""
        pass

    def segment(self, ...):
        """调用segment_video()"""
        pass

    def call_model(self, ...):
        """调用MLLMClient或ASR API"""
        pass

    def bbox(self, ...):
        """调用draw_bounding_boxes()"""
        pass
```

### 3. 端到端Pipeline ❌

**缺失内容**: 串联所有步骤的完整pipeline

**需要创建**: `processors/video_qa_pipeline.py`

```python
class VideoQAPipeline:
    """
    完整的视频QA Pipeline

    功能：
    1. 输入视频文件和问题
    2. 自动执行完整流程
    3. 返回答案和实验记录
    """

    def __init__(
        self,
        tool_user_agent: ToolUserAgent,
        atomic_ops: AtomicOperationsImplementation,
        config: Dict[str, Any]
    ):
        pass

    def run_video_qa(
        self,
        video_path: str,
        question: str
    ) -> Tuple[str, VideoExperimentRun]:
        """
        运行完整的视频QA任务

        步骤：
        1. extract_video_metadata()
        2. segment_video()
        3. 对每个segment:
           a. sample_frames()
           b. tool_user_agent.analyze(segment + frames)
        4. 整合所有segment_captions
        5. tool_user_agent.analyze(task=QA, context=全部理解, prompt=问题)
        6. 返回答案
        """
        pass
```

### 4. 依赖包安装 ❌

**需要安装的Python包**：

```bash
# 视频处理（必需）
pip install opencv-python

# 场景检测（可选，用于scene_change分段）
pip install scenedetect[opencv]

# 已安装的
# - openai (MLLM API)
# - python-dotenv (配置管理)
```

### 5. 测试视频和QA数据 ❌

**当前状态**：
- ✅ 有测试视频：`data/videos/source.mp4`
- ❌ 没有QA测试数据

**需要准备**：

```json
// data/qa_examples.json
{
  "video_id": "source",
  "video_path": "data/videos/source.mp4",
  "qa_pairs": [
    {
      "question": "视频中发生了什么？",
      "expected_answer": "..."
    },
    {
      "question": "视频中有哪些主要角色？",
      "expected_answer": "..."
    }
  ]
}
```

## 实现优先级

### Phase 1: 基础视频处理 (最高优先级) ✅ **已完成**
1. **实现视频元数据提取** - 使用opencv读取基本信息 ✅
2. **实现固定时长分段** - 最简单的分段策略 ✅
3. **实现均匀帧采样** - 最简单的采样方法 ✅

**实现文件**: `processors/video_processor.py`
**测试示例**: `examples/video_processor_example.py`
**实际测试**: ✅ 已通过测试（2085秒视频，分成209个片段，提取12帧）

### Phase 2: 原子操作实现 ✅ **已完成**
4. **实现AtomicOperationsImplementation** - 封装Phase 1的函数 ✅
5. **集成MLLM Client到CALL_MODEL操作** ✅
6. **实现边界框绘制** ✅

**实现文件**: `processors/atomic_operations_impl.py`
**测试示例**: `examples/atomic_operations_impl_example.py`
**实际测试**: ✅ 已通过测试（4个原子操作全部实现）

**功能清单**:
- SAMPLE操作: uniform, keyframe(placeholder), timestamps ✅
- SEGMENT操作: fixed_duration, scene_change(placeholder), custom ✅
- CALL_MODEL操作: mllm(完整实现), asr(placeholder) ✅
- BBOX操作: 边界框绘制 ✅

### Phase 3: 端到端Pipeline ✅ **已完成**
7. **实现VideoQAPipeline** - 串联所有步骤 ✅
8. **添加实验追踪** - VideoExperimentRun记录 ✅
9. **错误处理和重试机制** ✅

**实现文件**: `processors/video_qa_pipeline.py`
**测试示例**: `examples/video_qa_pipeline_example.py`
**实际测试**: ✅ 已通过测试（2085秒视频，16.94秒处理完成）

**功能清单**:
- 完整的6步workflow（元数据→分段→采样→分析→整合→QA）✅
- VideoExperimentRun实验追踪 ✅
- 配置系统（分段策略、采样参数、MLLM设置）✅
- 错误处理（Pipeline级别、片段级别、API级别）✅
- Dry-run模式支持 ✅

### Phase 4: 测试和优化
10. **创建端到端测试** - 使用source.mp4
11. **成本分析** - 计算实际API成本
12. **优化策略** - 减少帧数、缓存等

**预计工作量**: 2-3小时

## 最小可运行示例

实现Phase 1-3后，可以运行：

```python
from processors import VideoQAPipeline, VideoProcessor, AtomicOperationsImplementation
from agents import ToolUserAgent

# 1. 初始化组件
video_processor = VideoProcessor()
atomic_ops = AtomicOperationsImplementation(video_processor)
agent = ToolUserAgent(agent_id="qa_agent")

# 2. 创建Pipeline
pipeline = VideoQAPipeline(
    tool_user_agent=agent,
    atomic_ops=atomic_ops,
    config={
        "segment_strategy": "fixed_duration",
        "segment_duration": 10.0,  # 每段10秒
        "frames_per_segment": 5,    # 每段5帧
        "sampling_method": "uniform"
    }
)

# 3. 运行QA任务
answer, experiment = pipeline.run_video_qa(
    video_path="data/videos/source.mp4",
    question="视频中发生了什么？"
)

print(f"答案: {answer}")
print(f"成本: ${experiment.estimated_cost_usd:.2f}")
print(f"Token使用: {experiment.total_tokens}")
```

## 总结

**核心缺失**: 视频预处理模块（元数据提取、分段、帧采样）

**预计总工作量**: 6-10小时

**关键依赖**: opencv-python

**下一步行动**:
1. 安装opencv-python
2. 实现VideoProcessor类（Phase 1）
3. 测试基本的视频读取和帧提取
4. 逐步实现完整Pipeline
