# 配置架构分析与重构方案

## 当前问题分析

### 问题描述
当前`.env`配置文件中混合了三种不同性质的配置：
1. **全局配置**：如API keys、超时时间（应该是静态的）
2. **默认值**：如每段帧数、分段时长（应该作为默认值，但可被覆盖）
3. **工具参数**：这些实际上应该在Tool User Agent调用工具时动态指定

### 错误示例
```env
# 当前设计 - 问题：这些应该是工具调用时的参数，不是全局配置
FRAMES_PER_SEGMENT=5          # ❌ 应该是SAMPLE操作的动态参数
VIDEO_SEGMENT_DURATION=30     # ❌ 应该是SEGMENT操作的动态参数
FRAME_SAMPLING_METHOD=uniform # ❌ 应该是SAMPLE操作的动态参数
```

## 正确的架构设计

### 三层参数体系

```
Layer 1: 全局配置 (.env)
    ├── API Keys (OPENAI_API_KEY)
    ├── API超时 (MLLM_REQUEST_TIMEOUT)
    ├── 重试次数 (MLLM_MAX_RETRIES)
    └── 成本限制 (MAX_REQUEST_COST)

Layer 2: 默认值 (.env - 带DEFAULT前缀)
    ├── DEFAULT_FRAMES_PER_SEGMENT=5
    ├── DEFAULT_SEGMENT_DURATION=30
    └── DEFAULT_SAMPLING_METHOD="uniform"

Layer 3: 运行时参数 (Tool调用时传递)
    ├── Tool Creator创建工具时定义参数
    └── Tool User调用工具时传递具体值
```

## 当前实现检查

### ✅ 原子操作已经支持动态参数

```python
# AtomicOperationsImplementation已经正确实现了参数化
def sample(self, source, method: str, params: Dict[str, Any]):
    # method和params都是动态传递的！
    if method == "uniform":
        num_frames = params.get("num_frames", 5)  # 可以动态指定
    elif method == "timestamps":
        timestamps = params.get("timestamps", [])  # 可以动态指定

def segment(self, video_meta, strategy: str, params: Dict[str, Any]):
    # strategy和params都是动态传递的！
    if strategy == "fixed_duration":
        duration_sec = params.get("duration_sec", 30.0)  # 可以动态指定
```

### ❌ VideoQAPipeline固化了配置

```python
# 当前问题：VideoQAPipeline在初始化时固化了这些参数
class VideoQAPipeline:
    def __init__(self, atomic_ops, config):
        self.config = {
            "segment_duration_sec": 30.0,  # ❌ 固化
            "frames_per_segment": 5,        # ❌ 固化
            "sampling_method": "uniform",   # ❌ 固化
        }
```

### ❌ .env配置名称误导

```env
# 当前问题：看起来像全局配置，但实际应该是默认值
FRAMES_PER_SEGMENT=5           # 应该改名为 DEFAULT_FRAMES_PER_SEGMENT
VIDEO_SEGMENT_DURATION=30      # 应该改名为 DEFAULT_SEGMENT_DURATION
FRAME_SAMPLING_METHOD=uniform  # 应该改名为 DEFAULT_SAMPLING_METHOD
```

## 修复方案

### 方案1: 重新组织.env配置

```env
# ==================== 全局配置（不可在运行时更改）====================

# API Keys
OPENAI_API_KEY=your-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# API行为配置
MLLM_REQUEST_TIMEOUT=60        # 超时时间
MLLM_MAX_RETRIES=3             # 最大重试
MLLM_RETRY_DELAY=1.0           # 重试延迟

# 成本控制
MAX_REQUEST_COST=0             # 单次请求最大成本
MAX_DAILY_COST=0               # 每日最大成本

# 数据存储路径
DATA_DIR=./data
VIDEO_DIR=./data/videos
TEMP_DIR=./data/temp

# ==================== 默认值（可在运行时覆盖）====================

# 原子操作默认值
DEFAULT_SEGMENT_DURATION=30           # SEGMENT操作的默认分段时长
DEFAULT_SEGMENT_STRATEGY=fixed_duration  # SEGMENT操作的默认策略

DEFAULT_SAMPLING_METHOD=uniform       # SAMPLE操作的默认采样方法
DEFAULT_FRAMES_PER_SEGMENT=5          # SAMPLE操作的默认帧数

DEFAULT_MLLM_MODEL=gpt-4-vision-preview  # CALL_MODEL操作的默认模型
DEFAULT_MLLM_TEMPERATURE=0.7            # CALL_MODEL操作的默认温度
DEFAULT_MLLM_MAX_TOKENS=1000            # CALL_MODEL操作的默认token数

# VideoQAPipeline默认配置
DEFAULT_MAX_SEGMENTS=100              # Pipeline默认最大处理片段数
```

### 方案2: 原子操作使用默认值

```python
# processors/atomic_operations_impl.py

class AtomicOperationsImplementation:
    def __init__(self, video_processor, config=None):
        self.video_processor = video_processor
        # 从环境变量加载默认值
        self.defaults = {
            "segment_duration": float(os.getenv("DEFAULT_SEGMENT_DURATION", 30)),
            "sampling_method": os.getenv("DEFAULT_SAMPLING_METHOD", "uniform"),
            "frames_per_segment": int(os.getenv("DEFAULT_FRAMES_PER_SEGMENT", 5)),
            # ...
        }

    def sample(self, source, method: str = None, params: Dict[str, Any] = None):
        # 使用传入的method，否则使用默认值
        method = method or self.defaults["sampling_method"]
        params = params or {}

        # 如果params中没有num_frames，使用默认值
        if "num_frames" not in params and method == "uniform":
            params["num_frames"] = self.defaults["frames_per_segment"]

        # 继续原有逻辑...
```

### 方案3: VideoQAPipeline不固化参数

```python
# processors/video_qa_pipeline.py

class VideoQAPipeline:
    def run_video_qa(
        self,
        video_path: str,
        question: str,
        # 添加可选的运行时参数
        segment_params: Optional[Dict] = None,
        sample_params: Optional[Dict] = None,
        mllm_params: Optional[Dict] = None,
        context: Optional[str] = None
    ):
        """
        运行VideoQA Pipeline

        Args:
            segment_params: SEGMENT操作参数，如 {"strategy": "fixed_duration", "duration_sec": 60}
            sample_params: SAMPLE操作参数，如 {"method": "uniform", "num_frames": 3}
            mllm_params: CALL_MODEL操作参数，如 {"temperature": 0.7, "max_tokens": 500}
        """
        # 使用传入的参数，或使用默认值
        segment_params = segment_params or {
            "strategy": "fixed_duration",
            "duration_sec": self.atomic_ops.defaults["segment_duration"]
        }

        sample_params = sample_params or {
            "method": self.atomic_ops.defaults["sampling_method"],
            "num_frames": self.atomic_ops.defaults["frames_per_segment"]
        }

        # 继续原有逻辑...
```

## Tool Creator和Tool User的正确使用方式

### Tool Creator Agent创建工具

```python
# Tool Creator Agent应该生成这样的工具代码：

def analyze_video_segment(
    video_path: str,
    start_sec: float,
    end_sec: float,
    num_frames: int = 5,          # 工具参数！
    sampling_method: str = "uniform",  # 工具参数！
    question: str = None
) -> Dict:
    """
    分析视频片段

    参数在工具定义中暴露，由Tool User调用时指定！
    """
    # 创建segment
    segment = create_segment(video_path, start_sec, end_sec)

    # 采样帧 - 使用调用者传入的参数
    frames = atomic_ops.sample(
        source=segment,
        method=sampling_method,    # 来自工具调用参数
        params={"num_frames": num_frames}  # 来自工具调用参数
    )

    # 调用MLLM分析
    result = atomic_ops.call_model(...)

    return result
```

### Tool User Agent调用工具

```python
# Tool User Agent根据任务需求动态指定参数

# 场景1: 需要高质量分析 - 采样更多帧
result1 = analyze_video_segment(
    video_path="video.mp4",
    start_sec=0,
    end_sec=60,
    num_frames=10,           # 动态指定：需要更多帧
    sampling_method="uniform"
)

# 场景2: 快速预览 - 采样少量帧
result2 = analyze_video_segment(
    video_path="video.mp4",
    start_sec=60,
    end_sec=120,
    num_frames=2,            # 动态指定：只需要少量帧
    sampling_method="uniform"
)

# 场景3: 关键帧采样
result3 = analyze_video_segment(
    video_path="video.mp4",
    start_sec=120,
    end_sec=180,
    num_frames=5,
    sampling_method="keyframe"  # 动态指定：使用关键帧采样
)
```

## 修复优先级

### 高优先级（影响架构设计）
1. ✅ **原子操作已支持动态参数** - 无需修改
2. 🔄 **重命名.env中的配置** - 添加DEFAULT_前缀，避免误导
3. 🔄 **更新文档说明** - 明确参数传递机制

### 中优先级（改进用户体验）
4. **VideoQAPipeline添加参数覆盖支持** - 允许运行时指定参数
5. **添加示例代码** - 展示如何在不同场景下传递不同参数

### 低优先级（锦上添花）
6. **AtomicOperations从.env读取默认值** - 提供fallback
7. **参数验证** - 检查参数有效性

## 总结

### 核心思想
**参数应该在调用时指定，而不是在配置文件中固化**

```
❌ 错误：.env固化参数 → 所有调用使用相同参数
✅ 正确：.env提供默认值 → 调用时可以覆盖 → 灵活性最大
```

### 好消息
**原子操作的实现已经是正确的！** 它们完全支持动态参数。
主要问题在于：
1. `.env`配置名称容易误导
2. `VideoQAPipeline`固化了参数（这个可以改进，但不影响核心功能）
3. 文档没有充分说明参数传递机制

### 立即可做的改进
1. 重命名`.env`中的配置，添加`DEFAULT_`前缀
2. 更新文档，说明参数可以在运行时动态指定
3. 添加示例代码，展示不同参数的使用场景
