# 长视频理解变量表文档

**最后更新**: 2025-12-17

## 概述

本文档定义了长视频理解任务所需的所有数据变量。这些变量专门针对长视频处理和MLLM API调用场景设计。

**核心任务**: 将长视频分段后，通过M

LLM API理解每个片段，最终整合生成完整的视频理解。

## 变量分类

### 1. 基础视频变量
描述视频本身的元数据和结构

### 2. 视频理解结果变量
存储MLLM生成的理解结果

### 3. MLLM API交互变量
封装与多模态大语言模型的API交互

### 4. 原子操作变量
定义视频处理的基本操作单元

### 5. 实验运行变量
记录完整的实验过程和结果

---

## 一、基础视频变量

### 1.1 VideoMeta - 视频元数据

**用途**: 描述视频的基本信息

**字段定义**:
```python
VideoMeta(
    video_id: str              # 视频唯一标识
    file_path: str             # 视频文件路径
    duration_sec: float        # 视频时长（秒）
    fps: float                 # 帧率
    num_frames: int            # 总帧数
    width: int                 # 视频宽度
    height: int                # 视频高度
    format: VideoFormat        # 视频格式
    has_audio: bool            # 是否包含音频
    file_size_mb: float        # 文件大小
    source: str                # 视频来源
    description: str           # 视频描述
    tags: List[str]            # 标签
)
```

**示例**:
```python
video = VideoMeta(
    video_id="vid_001",
    file_path="/data/videos/sample.mp4",
    duration_sec=300.5,        # 5分钟
    fps=30.0,
    num_frames=9015,
    width=1920,
    height=1080,
    format=VideoFormat.MP4,
    source="youtube",
    description="产品介绍视频"
)
```

---

### 1.2 TimeSpan - 时间跨度

**用途**: 描述视频中的一个时间段

**字段定义**:
```python
TimeSpan(
    start_sec: float           # 开始时间（秒）
    end_sec: float             # 结束时间（秒）
)

# 属性
duration: float                # 时间跨度长度（自动计算）
```

**示例**:
```python
span = TimeSpan(start_sec=0.0, end_sec=30.0)  # 前30秒
print(span.duration)  # 30.0
```

---

### 1.3 Segment - 视频分段

**用途**: 将长视频切分为多个片段便于处理

**字段定义**:
```python
Segment(
    segment_id: str            # 分段唯一标识
    video_id: str              # 所属视频ID
    time_span: TimeSpan        # 时间跨度
    segment_index: int         # 分段索引（从0开始）
    total_segments: int        # 总分段数
    start_frame: int           # 起始帧号
    end_frame: int             # 结束帧号
    num_frames: int            # 该段帧数
    strategy: SegmentationStrategy  # 分段策略
)
```

**示例**:
```python
segment = Segment(
    segment_id="seg_001",
    video_id="vid_001",
    time_span=TimeSpan(start_sec=0.0, end_sec=30.0),
    segment_index=0,
    total_segments=10,
    start_frame=0,
    end_frame=900,
    num_frames=900,
    strategy=SegmentationStrategy.FIXED_DURATION
)
```

---

### 1.4 Frame - 视频帧

**用途**: 单个视频帧的信息

**字段定义**:
```python
Frame(
    frame_id: str              # 帧唯一标识
    video_id: str              # 所属视频ID
    segment_id: str            # 所属分段ID
    frame_index: int           # 帧索引
    timestamp_sec: float       # 时间戳（秒）
    image_path: str            # 帧图像文件路径
    image_base64: str          # 帧图像base64编码（用于API）
    width: int
    height: int
)
```

**示例**:
```python
frame = Frame(
    frame_id="frame_001",
    video_id="vid_001",
    segment_id="seg_001",
    frame_index=450,           # 第450帧
    timestamp_sec=15.0,        # 15秒处
    image_path="/tmp/frame_450.jpg",
    width=1920,
    height=1080
)
```

---

## 二、视频理解结果变量

### 2.1 FrameCaption - 帧描述

**用途**: 单个帧的文本描述（由MLLM生成）

**字段定义**:
```python
FrameCaption(
    caption_id: str            # 描述唯一标识
    frame_id: str              # 关联的帧ID
    caption: str               # 描述文本
    confidence: float          # 置信度 0-1
    model_name: str            # 使用的模型名称
    generated_at: str          # 生成时间
    generation_time_ms: float  # 生成耗时
    detected_objects: List[str]  # 检测到的对象
    detected_actions: List[str]  # 检测到的动作
    scene_type: str            # 场景类型
)
```

**示例**:
```python
frame_caption = FrameCaption(
    caption_id="cap_f_001",
    frame_id="frame_001",
    caption="一个人正在办公桌前工作，屏幕上显示着代码",
    confidence=0.95,
    model_name="gpt-4-vision",
    generation_time_ms=1500,
    detected_objects=["person", "desk", "computer", "code"],
    detected_actions=["working", "typing"],
    scene_type="office"
)
```

---

### 2.2 SegmentCaption - 分段描述

**用途**: 视频片段的文本描述

**字段定义**:
```python
SegmentCaption(
    caption_id: str            # 描述唯一标识
    segment_id: str            # 关联的分段ID
    caption: str               # 分段描述文本
    summary: str               # 摘要
    key_frames: List[str]      # 关键帧ID列表
    frame_captions: List[str]  # 帧描述ID列表
    main_events: List[str]     # 主要事件
    key_objects: List[str]     # 关键对象
    key_actions: List[str]     # 关键动作
    model_name: str            # 使用的模型
    confidence: float          # 置信度
)
```

**示例**:
```python
segment_caption = SegmentCaption(
    caption_id="cap_s_001",
    segment_id="seg_001",
    caption="这个片段展示了软件开发工作环境，一名程序员正在编写代码...",
    summary="程序员编码场景",
    key_frames=["frame_001", "frame_450", "frame_900"],
    main_events=["开始编码", "调试程序", "提交代码"],
    key_objects=["程序员", "电脑", "代码编辑器"],
    key_actions=["typing", "debugging", "reviewing"],
    model_name="gpt-4-vision",
    confidence=0.92
)
```

---

### 2.3 VideoUnderstanding - 完整视频理解

**用途**: 整合所有片段的理解结果

**字段定义**:
```python
VideoUnderstanding(
    understanding_id: str      # 理解结果唯一标识
    video_id: str              # 关联的视频ID
    overall_caption: str       # 整体描述
    summary: str               # 视频摘要
    title: str                 # 视频标题（如果生成）
    segment_captions: List[str]  # 分段描述ID列表
    timeline_events: List[Dict]  # 时间线事件
    main_topics: List[str]     # 主要话题
    key_entities: List[str]    # 关键实体
    narrative_structure: str   # 叙事结构分析
    model_name: str            # 使用的模型
    processing_time_ms: float  # 处理总耗时
)
```

**示例**:
```python
understanding = VideoUnderstanding(
    understanding_id="und_001",
    video_id="vid_001",
    overall_caption="这是一个关于软件开发的教程视频...",
    summary="从环境搭建到代码实现的完整开发流程",
    title="Python Web开发入门教程",
    segment_captions=["cap_s_001", "cap_s_002", ...],
    timeline_events=[
        {"time": 0, "event": "介绍开发环境"},
        {"time": 60, "event": "演示代码编写"},
        ...
    ],
    main_topics=["Python", "Web开发", "Django框架"],
    key_entities=["Python", "Django", "VS Code"],
    narrative_structure="教程型：介绍 → 演示 → 实践",
    model_name="gpt-4-vision"
)
```

---

## 三、MLLM API交互变量

### 3.1 MLLMRequest - MLLM API请求

**用途**: 封装对多模态大语言模型的API调用

**字段定义**:
```python
MLLMRequest(
    request_id: str            # 请求唯一标识
    model_name: str            # 模型名称 (e.g., "gpt-4-vision")
    api_endpoint: str          # API端点
    api_key: str               # API密钥
    prompt: str                # 文本提示
    images: List[str]          # 图像列表（base64或URL）
    video_frames: List[str]    # 视频帧列表
    temperature: float         # 温度参数
    max_tokens: int            # 最大token数
    top_p: float               # top_p采样
    task: AnalysisTask         # 任务类型
    timeout_seconds: int       # 超时时间
    retry_count: int           # 重试次数
)
```

**示例**:
```python
request = MLLMRequest(
    request_id="req_001",
    model_name="gpt-4-vision-preview",
    api_endpoint="https://api.openai.com/v1/chat/completions",
    prompt="请描述这个视频帧中发生的事情",
    images=["data:image/jpeg;base64,/9j/4AAQ..."],
    temperature=0.7,
    max_tokens=300,
    task=AnalysisTask.CAPTION,
    timeout_seconds=30
)
```

---

### 3.2 MLLMResponse - MLLM API响应

**用途**: 模型返回的结果

**字段定义**:
```python
MLLMResponse(
    response_id: str           # 响应唯一标识
    request_id: str            # 对应的请求ID
    text: str                  # 文本响应
    confidence: float          # 置信度
    success: bool              # 是否成功
    error_message: str         # 错误信息
    prompt_tokens: int         # 提示token数
    completion_tokens: int     # 完成token数
    total_tokens: int          # 总token数
    response_time_ms: float    # 响应时间
    model_name: str            # 实际使用的模型
    finish_reason: str         # 完成原因
)
```

**示例**:
```python
response = MLLMResponse(
    response_id="resp_001",
    request_id="req_001",
    text="这个场景中，一名程序员正坐在办公桌前...",
    confidence=0.95,
    success=True,
    prompt_tokens=150,
    completion_tokens=80,
    total_tokens=230,
    response_time_ms=1500,
    model_name="gpt-4-vision-preview",
    finish_reason="stop"
)
```

---

## 四、原子操作变量

### 4.1 AtomicOperation - 原子操作

**用途**: 定义视频处理的基本操作单元

**字段定义**:
```python
AtomicOperation(
    operation_id: str          # 操作唯一标识
    operation_name: str        # 操作名称
    operation_type: str        # 操作类型
    input_spec: Dict           # 输入规格
    output_spec: Dict          # 输出规格
    parameters: Dict           # 操作参数
    status: ProcessingStatus   # 执行状态
    start_time: str
    end_time: str
    duration_ms: float
    result: Any                # 执行结果
    error: str                 # 错误信息
)
```

---

### 4.2 AtomicOperations - 预定义原子操作（MVP核心）

**重要说明**:
- 原子操作只包含MVP实验的核心操作
- 视频元数据提取不是原子操作，而是每个任务的前置步骤
- 精简设计，专注于最小可行实验

**核心视频处理操作**:
- `SEGMENT_VIDEO`: 视频分段（按时间或场景分割长视频）
- `SAMPLE_FRAMES`: 帧采样（从片段中提取关键帧用于分析）

**MLLM交互操作**:
- `CALL_MLLM_API`: 调用MLLM API（发送图像+文本进行理解）

**结果生成操作**:
- `GENERATE_CAPTION`: 生成描述（帧描述或片段描述）
- `MERGE_RESULTS`: 合并结果（将多个片段结果整合为完整理解）

**工具方法**:
```python
# 获取所有操作
operations = AtomicOperations.get_all_operations()
# ['segment_video', 'sample_frames', 'call_mllm_api', 'generate_caption', 'merge_results']

# 获取操作描述
desc = AtomicOperations.get_operation_description('segment_video')
# '将长视频分割成多个片段，便于分段处理'
```

---

## 五、实验运行变量

### 5.1 VideoExperimentRun - 视频理解实验运行记录

**用途**: 记录一次完整的长视频理解实验

**字段定义**:
```python
VideoExperimentRun(
    run_id: str                # 运行唯一标识
    experiment_name: str       # 实验名称
    video_meta: VideoMeta      # 视频元数据
    segments: List[str]        # 分段ID列表
    frames: List[str]          # 提取的帧ID列表
    operations: List[str]      # 执行的操作ID列表
    mllm_requests: List[str]   # MLLM请求ID列表
    mllm_responses: List[str]  # MLLM响应ID列表
    frame_captions: List[str]  # 帧描述ID列表
    segment_captions: List[str]  # 分段描述ID列表
    video_understanding: str   # 最终理解结果ID
    status: ProcessingStatus   # 实验状态
    current_stage: str         # 当前阶段
    start_time: str
    end_time: str
    total_duration_ms: float
    total_api_calls: int       # API调用总次数
    total_tokens_used: int     # 使用token总数
    total_cost_usd: float      # 总成本（美元）
    description: str
    notes: List[str]
)
```

---

## 使用示例

### 完整的长视频理解流程

```python
from experiments import (
    VideoMeta, TimeSpan, Segment, Frame,
    FrameCaption, SegmentCaption, VideoUnderstanding,
    MLLMRequest, MLLMResponse,
    AtomicOperation, AtomicOperations,
    VideoExperimentRun, ProcessingStatus
)

# 1. 创建实验
experiment = VideoExperimentRun(
    run_id="exp_001",
    experiment_name="长视频理解测试"
)

# 2. 提取视频元数据
video = VideoMeta(
    video_id="vid_001",
    file_path="/data/videos/sample.mp4",
    duration_sec=300.0,
    fps=30.0,
    num_frames=9000,
    width=1920,
    height=1080
)
experiment.video_meta = video

# 3. 视频分段
segments = []
for i in range(10):  # 分成10段
    seg = Segment(
        segment_id=f"seg_{i:03d}",
        video_id=video.video_id,
        time_span=TimeSpan(start_sec=i*30, end_sec=(i+1)*30),
        segment_index=i,
        total_segments=10,
        start_frame=i*900,
        end_frame=(i+1)*900,
        num_frames=900
    )
    segments.append(seg)
    experiment.segments.append(seg.segment_id)

# 4. 对每个片段处理
for seg in segments:
    # 4.1 提取关键帧
    frame = Frame(
        frame_id=f"frame_{seg.segment_index}_key",
        video_id=video.video_id,
        segment_id=seg.segment_id,
        frame_index=seg.start_frame + 450,  # 中间帧
        timestamp_sec=seg.time_span.start_sec + 15,
        image_path=f"/tmp/frame_{seg.segment_index}.jpg"
    )
    experiment.frames.append(frame.frame_id)

    # 4.2 调用MLLM API分析
    mllm_request = MLLMRequest(
        request_id=f"req_{seg.segment_index}",
        model_name="gpt-4-vision",
        prompt="请详细描述这个视频片段中发生的事情",
        images=[frame.image_base64],
        task=AnalysisTask.CAPTION
    )
    experiment.mllm_requests.append(mllm_request.request_id)

    # 4.3 获取响应
    mllm_response = MLLMResponse(
        response_id=f"resp_{seg.segment_index}",
        request_id=mllm_request.request_id,
        text="在这个片段中...",
        success=True,
        total_tokens=200
    )
    experiment.mllm_responses.append(mllm_response.response_id)
    experiment.total_api_calls += 1
    experiment.total_tokens_used += mllm_response.total_tokens

    # 4.4 生成分段描述
    seg_caption = SegmentCaption(
        caption_id=f"cap_seg_{seg.segment_index}",
        segment_id=seg.segment_id,
        caption=mllm_response.text,
        model_name=mllm_request.model_name
    )
    experiment.segment_captions.append(seg_caption.caption_id)

# 5. 整合生成完整理解
understanding = VideoUnderstanding(
    understanding_id="und_001",
    video_id=video.video_id,
    overall_caption="这个视频展示了...",
    summary="视频摘要",
    segment_captions=experiment.segment_captions
)
experiment.video_understanding = understanding.understanding_id

# 6. 完成实验
experiment.status = ProcessingStatus.COMPLETED
experiment.end_time = datetime.now().isoformat()

print(f"实验完成：{experiment.run_id}")
print(f"API调用次数：{experiment.total_api_calls}")
print(f"Token使用总数：{experiment.total_tokens_used}")
```

---

## 变量关系图

```
VideoMeta (视频元数据)
    ↓
Segment (视频分段) × N
    ↓
Frame (关键帧) × M
    ↓
MLLMRequest (MLLM请求)
    ↓
MLLMResponse (MLLM响应)
    ↓
FrameCaption (帧描述)
    ↓
SegmentCaption (分段描述)
    ↓
VideoUnderstanding (完整理解)
    ↓
VideoExperimentRun (实验记录)
```

---

## 修改指南

### 添加新变量字段
直接在 `experiments/video_variables.py` 的对应dataclass中添加：

```python
@dataclass
class VideoMeta:
    # ... 现有字段

    # 新增字段
    thumbnail_path: str = ""   # 缩略图路径
    language: str = "zh"       # 视频语言
```

### 添加新的原子操作
在 `AtomicOperations` 类中添加新常量：

```python
class AtomicOperations:
    # ... 现有操作

    # 新操作
    DETECT_EMOTIONS = "detect_emotions"  # 情绪检测
```

---

## 总结

这套变量系统的特点：

1. **针对长视频理解**: 所有变量设计都围绕长视频处理场景
2. **支持MLLM API**: 专门的MLLMRequest/Response变量
3. **完整追溯**: 通过ID关联所有相关数据
4. **成本可控**: 记录API调用次数和token使用量
5. **易于扩展**: 清晰的结构便于添加新功能

这些变量构成了长视频理解多Agent系统的数据基础。
