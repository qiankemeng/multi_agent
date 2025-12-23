# 原子操作文档

> 长视频理解系统的4个核心原子操作

---

## 概述

原子操作是系统中不可再分的基本操作单元，Tool Creator Agent通过组合这些原子操作来创建各种功能工具。

**设计原则**：
- **单一表达**：每种数据类型只有唯一的标准表达方式
- **确定性输出**：每个操作的返回类型固定
- **最小化选项**：只保留核心的、不可相互替代的选项
- **易于组合**：操作之间可以无缝连接

**核心数据流**：
```
VideoMeta → SEGMENT → List[Segment]
          ↓
Segment/VideoMeta → SAMPLE → List[Frame]
          ↓
List[Frame] → CALL_MODEL → ModelResponse
          ↓
Frame → BBOX → Frame (标注后)
```

---

## 数据类型定义

### Frame（帧）
```python
@dataclass
class Frame:
    frame_id: str           # 帧唯一标识
    video_id: str           # 所属视频ID
    segment_id: str         # 所属片段ID（可选）

    # 时间信息
    timestamp_sec: float    # 时间戳（秒）
    frame_index: int        # 帧索引

    # 图像信息
    image_path: str         # 图像文件路径（总是存在）
    width: int              # 图像宽度
    height: int             # 图像高度
```

**关键特性**：
- `image_path` 总是有值，指向临时文件
- Frame是操作之间传递的标准单位

### Segment（片段）
```python
@dataclass
class Segment:
    segment_id: str         # 片段唯一标识
    video_id: str           # 所属视频ID

    # 时间范围
    time_span: TimeSpan     # {start_sec, end_sec, duration}

    # 索引信息
    segment_index: int      # 片段索引（从0开始）
    total_segments: int     # 总片段数

    # 帧范围
    start_frame: int        # 起始帧号
    end_frame: int          # 结束帧号
    num_frames: int         # 该段帧数
```

### ModelResponse（模型响应）
```python
@dataclass
class ModelResponse:
    response_id: str
    request_id: str

    # 模型信息
    model_type: str         # "mllm" 或 "asr"
    model_name: str

    # 响应状态
    success: bool
    error_message: str

    # 输出内容
    output: Union[str, Dict]
    # - mllm: str (生成的文本)
    # - asr: Dict {"text": str, "segments": List[Dict]}

    # 使用统计
    total_tokens: int
    cost_usd: float
    response_time_ms: float
```

---

## 原子操作

## 1. SAMPLE - 采样

**功能**：从视频或片段中提取帧图像

### 输入

```python
{
    "source": Union[VideoMeta, Segment],  # 数据源
    "method": str,                        # 采样方法
    "params": Dict[str, Any]              # 方法参数
}
```

### 采样方法

#### uniform - 均匀采样
从源中均匀提取N帧

```python
params = {
    "num_frames": int              # 采样帧数
}
```

**示例**：
```python
frames = SAMPLE(
    source=video_meta,
    method="uniform",
    params={"num_frames": 10}
)
# 返回: 10个均匀分布的Frame对象
```

#### keyframe - 关键帧采样
基于内容变化检测关键帧

```python
params = {
    "threshold": float,            # 变化阈值 0-1
    "max_frames": int              # 最多采样帧数
}
```

**示例**：
```python
frames = SAMPLE(
    source=segment,
    method="keyframe",
    params={"threshold": 0.3, "max_frames": 20}
)
# 返回: 最多20个关键帧
```

#### timestamps - 指定时间点
按指定的时间戳提取帧

```python
params = {
    "timestamps": List[float]      # 时间戳列表（秒）
}
```

**示例**：
```python
frames = SAMPLE(
    source=video_meta,
    method="timestamps",
    params={"timestamps": [0, 30.5, 120.0, 180.5]}
)
# 返回: 4个指定时间点的Frame对象
```

### 输出

```python
List[Frame]  # 每个Frame.image_path总是有值
```

---

## 2. SEGMENT - 分段

**功能**：将视频按策略分割成多个片段

### 输入

```python
{
    "video_meta": VideoMeta,       # 视频元数据
    "strategy": str,               # 分段策略
    "params": Dict[str, Any]       # 策略参数
}
```

### 分段策略

#### fixed_duration - 固定时长
按固定时长分割视频

```python
params = {
    "duration_sec": float          # 每段时长（秒）
}
```

**示例**：
```python
segments = SEGMENT(
    video_meta=video,
    strategy="fixed_duration",
    params={"duration_sec": 30.0}
)
# 返回: 每30秒一个Segment
```

#### scene_change - 场景变化
基于场景变化检测分割

```python
params = {
    "threshold": float,            # 场景变化阈值 0-1
    "min_duration": float          # 最小片段时长（秒）
}
```

**示例**：
```python
segments = SEGMENT(
    video_meta=video,
    strategy="scene_change",
    params={"threshold": 0.3, "min_duration": 10.0}
)
# 返回: 根据场景变化自动分割的Segment列表
```

#### custom - 自定义断点
按指定的时间点分割

```python
params = {
    "breakpoints": List[float]     # 分段点时间戳（秒）
}
```

**示例**：
```python
segments = SEGMENT(
    video_meta=video,
    strategy="custom",
    params={"breakpoints": [0, 45.5, 120.0, 180.5, 300.0]}
)
# 返回: 4个自定义范围的Segment
```

### 输出

```python
List[Segment]
```

---

## 3. CALL_MODEL - 调用模型

**功能**：统一的模型调用接口

### 输入

```python
{
    "model_type": str,             # 模型类型
    "model_name": str,             # 模型名称
    "inputs": Dict[str, Any],      # 输入数据
    "params": Dict[str, Any]       # 模型参数
}
```

### 模型类型

#### mllm - 多模态大语言模型

**输入**：
```python
inputs = {
    "prompt": str,                     # 文本提示
    "frames": List[Frame],             # Frame列表（自动读取image_path）
    "system_prompt": Optional[str]     # 系统提示（可选）
}

params = {
    "temperature": float,              # 温度参数 0-2
    "max_tokens": int                  # 最大生成token数
}
```

**支持的模型**：
- `gpt-4o`, `gpt-4o-mini`
- `claude-3-5-sonnet`, `claude-3-haiku`
- `gemini-1.5-pro`, `gemini-1.5-flash`

**示例**：
```python
response = CALL_MODEL(
    model_type="mllm",
    model_name="gpt-4o",
    inputs={
        "prompt": "Describe what you see in these frames.",
        "frames": [frame1, frame2, frame3],
        "system_prompt": "You are a video analyst."
    },
    params={
        "temperature": 0.7,
        "max_tokens": 300
    }
)
# response.output: "I see three scenes from..."
```

#### asr - 语音识别

**输入**：
```python
inputs = {
    "audio_path": str,                 # 音频文件路径
    "language": Optional[str]          # 语言代码（可选）
}

params = {
    "with_timestamps": bool            # 是否返回时间戳
}
```

**支持的模型**：
- `whisper-large-v3`
- `whisper-medium`

**示例**：
```python
response = CALL_MODEL(
    model_type="asr",
    model_name="whisper-large-v3",
    inputs={
        "audio_path": "/tmp/audio.wav",
        "language": "en"
    },
    params={
        "with_timestamps": True
    }
)
# response.output: {
#     "text": "Hello world...",
#     "segments": [
#         {"start": 0.0, "end": 2.5, "text": "Hello world"}
#     ]
# }
```

### 输出

```python
ModelResponse
```

---

## 4. BBOX - 边界框

**功能**：在帧图像上绘制边界框和标注

### 输入

```python
{
    "frame": Frame,                # 输入帧
    "boxes": List[Dict]            # 边界框列表
}
```

### 边界框格式

```python
box = {
    "bbox": [x, y, width, height],     # 边界框坐标
    "label": str,                      # 标签文本
    "confidence": Optional[float],     # 置信度（可选）
    "color": Optional[str]             # 颜色（可选，默认随机）
}
```

### 输出

```python
Frame  # 新的Frame对象，image_path指向标注后的图像
```

### 示例

```python
annotated_frame = BBOX(
    frame=original_frame,
    boxes=[
        {"bbox": [100, 200, 50, 80], "label": "person", "confidence": 0.95},
        {"bbox": [300, 150, 60, 70], "label": "car", "confidence": 0.88, "color": "red"}
    ]
)
# annotated_frame.image_path: "/tmp/annotated_xyz.jpg"
# 返回的Frame可以继续传递给其他操作
```

---

## 工具组合示例

### 示例1：单帧快速分析

```python
def quick_frame_analysis(video: VideoMeta, timestamp: float) -> str:
    """分析指定时间点的单帧"""

    # 采样指定时间点
    frames = SAMPLE(
        source=video,
        method="timestamps",
        params={"timestamps": [timestamp]}
    )

    # 调用MLLM分析
    response = CALL_MODEL(
        model_type="mllm",
        model_name="gpt-4o",
        inputs={
            "prompt": "Describe this frame in detail.",
            "frames": frames
        },
        params={"temperature": 0.7, "max_tokens": 200}
    )

    return response.output
```

### 示例2：完整视频理解

```python
def understand_video(video: VideoMeta) -> Dict:
    """完整的视频理解流程"""

    # 1. 分段
    segments = SEGMENT(
        video_meta=video,
        strategy="fixed_duration",
        params={"duration_sec": 30.0}
    )

    results = []

    # 2. 逐段处理
    for seg in segments:
        # 2a. 采样关键帧
        frames = SAMPLE(
            source=seg,
            method="uniform",
            params={"num_frames": 3}
        )

        # 2b. 视觉理解
        response = CALL_MODEL(
            model_type="mllm",
            model_name="gpt-4o",
            inputs={
                "prompt": "Describe the visual content.",
                "frames": frames
            },
            params={"temperature": 0.7, "max_tokens": 200}
        )

        results.append({
            "time": f"{seg.time_span.start_sec}-{seg.time_span.end_sec}s",
            "description": response.output
        })

    return {"segments": results}
```

### 示例3：多模态理解（视觉+语音）

```python
def multimodal_understanding(video: VideoMeta) -> Dict:
    """视觉+语音的完整理解"""

    # 1. 分段
    segments = SEGMENT(
        video_meta=video,
        strategy="fixed_duration",
        params={"duration_sec": 30.0}
    )

    results = []

    for seg in segments:
        # 2. 视觉分析
        frames = SAMPLE(
            source=seg,
            method="uniform",
            params={"num_frames": 3}
        )

        visual = CALL_MODEL(
            model_type="mllm",
            model_name="gpt-4o",
            inputs={"prompt": "Describe what you see.", "frames": frames},
            params={"temperature": 0.7, "max_tokens": 200}
        )

        # 3. 语音转写
        audio = CALL_MODEL(
            model_type="asr",
            model_name="whisper-large-v3",
            inputs={"audio_path": f"/tmp/seg_{seg.segment_id}.wav"},
            params={"with_timestamps": True}
        )

        results.append({
            "time_range": f"{seg.time_span.start_sec}-{seg.time_span.end_sec}s",
            "visual": visual.output,
            "transcript": audio.output["text"]
        })

    return results
```

### 示例4：关键帧提取与标注

```python
def extract_and_annotate(video: VideoMeta) -> List[Frame]:
    """提取关键帧并标注重要区域"""

    # 1. 提取关键帧
    keyframes = SAMPLE(
        source=video,
        method="keyframe",
        params={"threshold": 0.3, "max_frames": 20}
    )

    annotated_frames = []

    # 2. 对每个关键帧进行标注
    for frame in keyframes:
        # 使用MLLM识别需要标注的区域（这里简化）
        annotated = BBOX(
            frame=frame,
            boxes=[
                {"bbox": [100, 100, 200, 200], "label": "主要对象"}
            ]
        )
        annotated_frames.append(annotated)

    return annotated_frames
```

### 示例5：场景级别分析

```python
def scene_level_analysis(video: VideoMeta) -> List[Dict]:
    """基于场景变化的分析"""

    # 1. 按场景变化分段
    scenes = SEGMENT(
        video_meta=video,
        strategy="scene_change",
        params={"threshold": 0.3, "min_duration": 5.0}
    )

    scene_descriptions = []

    # 2. 分析每个场景
    for scene in scenes:
        # 采样第一帧作为场景代表
        frames = SAMPLE(
            source=scene,
            method="uniform",
            params={"num_frames": 1}
        )

        # 描述场景
        response = CALL_MODEL(
            model_type="mllm",
            model_name="gpt-4o",
            inputs={
                "prompt": "Describe this scene: location, objects, atmosphere.",
                "frames": frames
            },
            params={"temperature": 0.7, "max_tokens": 150}
        )

        scene_descriptions.append({
            "scene_id": scene.segment_id,
            "start_time": scene.time_span.start_sec,
            "duration": scene.time_span.duration,
            "description": response.output
        })

    return scene_descriptions
```

---

## 组合模式

### 模式1：线性流水线
```
SAMPLE → CALL_MODEL
```
适用于：单帧/单片段快速分析

### 模式2：批量处理
```
SEGMENT → (SAMPLE → CALL_MODEL) × N
```
适用于：完整视频理解

### 模式3：多模态融合
```
SAMPLE → CALL_MODEL(mllm) + CALL_MODEL(asr)
```
适用于：视觉+听觉理解

### 模式4：标注流程
```
SAMPLE → BBOX → CALL_MODEL
```
适用于：可视化分析、标注验证

### 模式5：自适应分析
```
SEGMENT(scene_change) → SAMPLE → CALL_MODEL
```
适用于：基于内容的自适应处理

---

## 快速参考

### 操作总览

| 操作 | 输入 | 输出 | 方法/策略 |
|------|------|------|-----------|
| **SAMPLE** | VideoMeta/Segment | List[Frame] | uniform, keyframe, timestamps |
| **SEGMENT** | VideoMeta | List[Segment] | fixed_duration, scene_change, custom |
| **CALL_MODEL** | 输入+参数 | ModelResponse | mllm, asr |
| **BBOX** | Frame+boxes | Frame | - |

### 支持的模型

**MLLM**：
- gpt-4o, gpt-4o-mini
- claude-3-5-sonnet, claude-3-haiku
- gemini-1.5-pro, gemini-1.5-flash

**ASR**：
- whisper-large-v3
- whisper-medium

---

## 使用建议

### 1. 成本控制
- 通过调整 `num_frames` 控制采样数量
- 使用较小的模型（如 gpt-4o-mini）降低成本
- 减少 `max_tokens` 限制输出长度

### 2. 质量优化
- 对重要片段增加采样帧数
- 使用 `keyframe` 方法自动识别关键内容
- 使用更大的模型（如 gpt-4o）提高准确度

### 3. 性能优化
- 并行处理多个segment
- 批量调用MLLM（多个frames一次调用）
- 缓存中间结果避免重复计算

### 4. 错误处理
- 检查 `ModelResponse.success` 状态
- 处理 `error_message` 并进行重试
- 验证Frame的 `image_path` 是否存在
