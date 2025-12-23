# 原子操作总结

## 当前设计

本系统定义了**4个核心原子操作**，用于长视频理解任务：

### 1. SAMPLE - 采样
从视频或片段中提取帧图像

**方法**：
- `uniform`: 均匀采样N帧
- `keyframe`: 基于内容变化检测关键帧
- `timestamps`: 按指定时间点提取

**输出**：`List[Frame]`

### 2. SEGMENT - 分段
将视频按策略分割成多个片段

**策略**：
- `fixed_duration`: 固定时长分段
- `scene_change`: 场景变化检测分段
- `custom`: 自定义断点分段

**输出**：`List[Segment]`

### 3. CALL_MODEL - 调用模型
统一的模型调用接口

**模型类型**：
- `mllm`: 多模态大语言模型（GPT-4o, Claude, Gemini等）
- `asr`: 语音识别（Whisper）

**输出**：`ModelResponse`

### 4. BBOX - 边界框
在帧图像上绘制边界框和标注

**输入**：Frame + 边界框列表
**输出**：Frame（标注后的新Frame对象）

## 设计原则

1. **单一表达**：Frame总是包含`image_path`，不再有`image_base64`
2. **确定性输出**：每个操作的返回类型固定，不依赖参数选择
3. **最小化选项**：只保留核心的、不可相互替代的功能
4. **易于组合**：操作之间可以无缝连接

## 数据流

```
VideoMeta (前置步骤)
    ↓
SEGMENT → List[Segment]
    ↓
SAMPLE → List[Frame]
    ↓
CALL_MODEL → ModelResponse
    ↓
BBOX → Frame (可选)
```

## 核心变量

### Frame
```python
Frame {
    frame_id: str
    video_id: str
    timestamp_sec: float
    image_path: str      # 总是有值
    width: int
    height: int
}
```

### Segment
```python
Segment {
    segment_id: str
    video_id: str
    time_span: TimeSpan
    segment_index: int
    total_segments: int
}
```

### ModelResponse
```python
ModelResponse {
    response_id: str
    model_type: str      # "mllm" 或 "asr"
    model_name: str
    success: bool
    output: Union[str, Dict]
    total_tokens: int
    cost_usd: float
}
```

## 工具组合示例

### 单帧分析
```
SAMPLE (timestamps) → CALL_MODEL (mllm)
```

### 完整视频理解
```
SEGMENT → (SAMPLE → CALL_MODEL) × N → 聚合
```

### 多模态理解
```
SEGMENT → SAMPLE → CALL_MODEL(mllm) + CALL_MODEL(asr)
```

### 可视化分析
```
SAMPLE → BBOX → CALL_MODEL
```

## 文档

完整规范见：`docs/ATOMIC_OPERATIONS.md`

代码定义见：`experiments/video_variables.py` 中的 `AtomicOperations` 类

示例代码见：`examples/atomic_operations_example.py`
