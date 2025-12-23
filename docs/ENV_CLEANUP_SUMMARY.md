# .env配置精简总结

**日期**: 2025-12-18
**操作**: 删除所有伪全局配置，只保留真正的系统级配置

## 删除的配置（15项）

### ❌ MLLM参数配置（应在调用时指定）
- `MLLM_DEFAULT_TEMPERATURE` → 调用时传递: `params={"temperature": 0.7}`
- `MLLM_DEFAULT_MAX_TOKENS` → 调用时传递: `params={"max_tokens": 1000}`

### ❌ Agent配置（应在调用时指定）
- `TOOL_CREATOR_MODEL` → 已有 `OPENAI_DEFAULT_MODEL`
- `TOOL_CREATOR_TEMPERATURE` → 调用时传递
- `TOOL_CREATOR_MAX_TOKENS` → 调用时传递
- `TOOL_USER_MODEL` → 已有 `OPENAI_DEFAULT_MODEL`
- `TOOL_USER_TEMPERATURE` → 调用时传递
- `TOOL_USER_MAX_TOKENS` → 调用时传递

### ❌ 视频处理参数（应在调用时指定）
- `VIDEO_SEGMENTATION_STRATEGY` → 调用时传递: `strategy="fixed_duration"`
- `VIDEO_SEGMENT_DURATION` → 调用时传递: `params={"duration_sec": 60}`
- `VIDEO_MAX_SEGMENTS` → 调用时传递: Pipeline配置
- `FRAME_SAMPLING_METHOD` → 调用时传递: `method="uniform"`
- `FRAMES_PER_SEGMENT` → 调用时传递: `params={"num_frames": 5}`
- `MAX_IMAGE_SIZE` → 调用时传递或硬编码

### ❌ 实验配置（应在运行时指定）
- `EXPERIMENT_NAME` → 运行时传递
- `SAVE_INTERMEDIATE_RESULTS` → 运行时传递
- `VERBOSE` → 运行时传递

## 保留的配置（真正的全局配置）

### ✅ API配置（系统级）
- `OPENAI_API_KEY` - API密钥
- `OPENAI_BASE_URL` - API端点
- `OPENAI_DEFAULT_MODEL` - 默认模型名称
- `CLAUDE_*`, `GEMINI_*` - 其他API配置

### ✅ API行为配置（系统级）
- `MLLM_REQUEST_TIMEOUT` - 请求超时时间
- `MLLM_MAX_RETRIES` - 最大重试次数
- `MLLM_RETRY_DELAY` - 重试延迟

### ✅ 成本控制（系统级）
- `OPENAI_PRICE_*` - 价格配置
- `MAX_REQUEST_COST` - 单次请求成本限制
- `MAX_DAILY_COST` - 每日成本限制

### ✅ 数据存储（系统级）
- `DATA_DIR`, `VIDEO_DIR`, `OUTPUT_DIR`, `CACHE_DIR`, `TEMP_DIR`

### ✅ 日志配置（系统级）
- `LOG_LEVEL`, `LOG_FILE`, `LOG_FORMAT`, `LOG_TO_CONSOLE`

### ✅ 性能配置（系统级）
- `MAX_CONCURRENT_REQUESTS`
- `ENABLE_CACHE`, `CACHE_EXPIRY`

### ✅ 环境配置（系统级）
- `ENVIRONMENT`, `DEBUG`, `MOCK_MODE`, `PYTHON_VERSION`

## 新的使用方式

### 原子操作调用

**SAMPLE操作**:
```python
# 不再从.env读取FRAMES_PER_SEGMENT
# 直接在调用时指定
atomic_ops.sample(
    source=video_meta,
    method="uniform",  # 不再从.env读取FRAME_SAMPLING_METHOD
    params={"num_frames": 10}  # 动态指定
)
```

**SEGMENT操作**:
```python
# 不再从.env读取VIDEO_SEGMENT_DURATION
# 直接在调用时指定
atomic_ops.segment(
    video_meta=video_meta,
    strategy="fixed_duration",  # 不再从.env读取VIDEO_SEGMENTATION_STRATEGY
    params={"duration_sec": 60}  # 动态指定
)
```

**CALL_MODEL操作**:
```python
# 不再从.env读取MLLM_DEFAULT_TEMPERATURE等
# 直接在调用时指定
atomic_ops.call_model(
    model_type="mllm",
    model_name="gpt-5",  # 可以覆盖OPENAI_DEFAULT_MODEL
    inputs={...},
    params={
        "temperature": 0.7,  # 动态指定
        "max_tokens": 1000   # 动态指定
    }
)
```

### Tool Creator创建工具

```python
def video_analysis_tool(
    video_path: str,
    num_frames: int = 5,          # 参数暴露
    segment_duration: float = 60,  # 参数暴露
    temperature: float = 0.7       # 参数暴露
):
    """工具应该暴露所有可调参数"""
    segments = atomic_ops.segment(
        video_meta=meta,
        strategy="fixed_duration",
        params={"duration_sec": segment_duration}  # 使用传入的参数
    )

    frames = atomic_ops.sample(
        source=meta,
        method="uniform",
        params={"num_frames": num_frames}  # 使用传入的参数
    )

    result = atomic_ops.call_model(
        model_type="mllm",
        model_name=os.getenv("OPENAI_DEFAULT_MODEL"),  # 使用系统配置
        inputs={...},
        params={"temperature": temperature, "max_tokens": 1000}  # 使用传入的参数
    )
```

### Tool User调用工具

```python
# 场景1：快速预览
result1 = video_analysis_tool(
    video_path="video.mp4",
    num_frames=2,          # 少帧数
    segment_duration=120,  # 大片段
    temperature=0.7
)

# 场景2：详细分析
result2 = video_analysis_tool(
    video_path="video.mp4",
    num_frames=10,         # 多帧数
    segment_duration=30,   # 小片段
    temperature=0.5        # 更确定
)
```

## 验证结果

✅ **所有测试通过**（5/5）
```
✓ VideoProcessor基础功能
✓ AtomicOperations基础功能
✓ Pipeline配置系统
✓ Pipeline完整工作流
✓ 实验追踪系统
```

## 架构优势

### ✅ 清晰度提升
- 配置文件只包含真正的系统级配置
- 不会误导开发者认为某些参数是固定的
- 配置文件从154行减少到120行

### ✅ 灵活性最大化
- 所有业务参数都在调用时动态指定
- Tool User Agent可以根据任务需求自由调整
- 符合Multi-Agent系统的设计理念

### ✅ 无breaking changes
- 原子操作API本来就支持动态参数
- 代码无需修改
- 测试全部通过

## 对比

### 修改前
```env
# 看起来像全局配置，实际应该是动态参数
FRAMES_PER_SEGMENT=5
VIDEO_SEGMENT_DURATION=30
FRAME_SAMPLING_METHOD=uniform
```

### 修改后
```python
# 直接在调用时指定，灵活性最大
atomic_ops.sample(method="uniform", params={"num_frames": 5})
atomic_ops.segment(strategy="fixed_duration", params={"duration_sec": 30})
```

## 总结

**核心原则**: 配置文件只应包含系统级的全局配置，所有业务逻辑参数应在运行时动态传递。

**删除的15项配置** 全部改为在调用时动态指定，提升了系统的灵活性和清晰度。

**系统架构更合理**:
- 全局配置在`.env`
- 业务参数在调用时传递
- 完全符合Multi-Agent设计理念

✅ **配置精简完成！系统更清晰、更灵活！**
