# VideoQA Pipeline 完整工作流程详解

## 测试结果概览

**输入**:
- 视频: `data/videos/source.mp4` (2085秒, 35分钟)
- 问题: "What is happening in this video? Describe the main content and activities."

**输出**:
- 详细回答: 4段描述，包含比赛设置、预备阶段、开球、进球等细节
- API调用: 4次
- Tokens消耗: 13,185
- 成本: $0.5044
- 处理时间: 127.72秒

---

## 完整工作流程详解

### 步骤0: Pipeline初始化

**代码位置**: `processors/video_qa_pipeline.py:85-100`

```python
pipeline = VideoQAPipeline(
    atomic_ops=atomic_ops,
    config={
        "segment_duration_sec": 60.0,      # 每段60秒
        "frames_per_segment": 3,            # 每段采样3帧
        "max_segments": 3,                  # 只处理前3段
        "mllm_model": "gpt-5",             # 使用的模型
        "temperature": 0.7,                 # 温度参数
        "max_tokens_per_segment": 4000,    # Segment分析上限
        "max_tokens_qa": 3000              # 最终QA上限
    }
)
```

**这一步做了什么**:
- 创建VideoQAPipeline对象
- 加载配置参数
- 初始化AtomicOperations（包含VideoProcessor和MLLMClient）
- 准备好所有需要的组件

---

### 步骤1: 提取视频元数据

**输出**:
```
[1/6] Extracting video metadata...
  ✓ Video: 2085.2s, 1280x720, 30.0fps
```

**代码位置**: `processors/video_qa_pipeline.py:182-185`

```python
def _extract_metadata(self, video_path: str, experiment: VideoExperimentRun) -> VideoMeta:
    """Step 1: Extract video metadata"""
    video_meta = self.video_processor.extract_metadata(video_path)
    experiment.video_meta = video_meta
    return video_meta
```

**底层实现**: `processors/video_processor.py:53-95`

```python
def extract_metadata(self, video_path: str) -> VideoMeta:
    # 使用OpenCV打开视频
    cap = cv2.VideoCapture(str(video_path))

    # 读取视频属性
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_sec = num_frames / fps if fps > 0 else 0.0

    # 创建VideoMeta对象
    return VideoMeta(...)
```

**这一步做了什么**:
1. 使用OpenCV的cv2.VideoCapture打开视频文件
2. 读取视频的基本属性:
   - 帧率 (FPS): 30.00
   - 分辨率: 1280x720
   - 总帧数: 62,557
   - 时长: 2085.23秒 (约35分钟)
3. 创建VideoMeta对象存储这些信息
4. 保存到experiment追踪对象

**关键数据结构** (`experiments/video_variables.py:76-102`):
```python
@dataclass
class VideoMeta:
    video_id: str           # 唯一标识
    file_path: str          # 视频路径
    duration_sec: float     # 时长
    fps: float             # 帧率
    num_frames: int        # 总帧数
    width: int             # 宽度
    height: int            # 高度
```

---

### 步骤2: 视频分段

**输出**:
```
[2/6] Segmenting video...
  ✓ Created 35 segments (60.0s each)
  → Processing first 3 segments only
```

**代码位置**: `processors/video_qa_pipeline.py:187-195`

```python
def _segment_video(self, video_meta: VideoMeta, experiment: VideoExperimentRun) -> List[Segment]:
    """Step 2: Segment video"""
    segments = self.atomic_ops.segment(
        video_meta=video_meta,
        strategy="fixed_duration",
        params={"duration_sec": self.config["segment_duration_sec"]}
    )

    # 如果配置了max_segments，只取前N个
    if self.config["max_segments"]:
        segments = segments[:self.config["max_segments"]]

    return segments
```

**底层实现**: `processors/atomic_operations_impl.py:304-317`

```python
def _segment_fixed_duration(self, video_meta: VideoMeta, params: Dict[str, Any]) -> List[Segment]:
    duration_sec = params.get("duration_sec")
    return self.video_processor.segment_video_fixed_duration(
        video_meta=video_meta,
        duration_sec=duration_sec
    )
```

**更底层**: `processors/video_processor.py:219-271`

```python
def segment_video_fixed_duration(self, video_meta: VideoMeta, duration_sec: float) -> List[Segment]:
    segments = []
    num_segments = int(video_meta.duration_sec / duration_sec) + 1

    for i in range(num_segments):
        start_sec = i * duration_sec
        end_sec = min(start_sec + duration_sec, video_meta.duration_sec)

        segment = Segment(
            segment_id=f"seg_{video_meta.video_id}_{i:04d}",
            video_id=video_meta.video_id,
            time_span=TimeSpan(start_sec=start_sec, end_sec=end_sec),
            segment_index=i,
            total_segments=num_segments,
            start_frame=int(start_sec * video_meta.fps),
            end_frame=int(end_sec * video_meta.fps),
            num_frames=int((end_sec - start_sec) * video_meta.fps)
        )
        segments.append(segment)

    return segments
```

**这一步做了什么**:
1. 计算需要多少个segments: `总时长 / segment时长 = 2085.23 / 60.0 = 35个`
2. 为每个segment计算:
   - 时间范围 (start_sec, end_sec)
   - 帧范围 (start_frame, end_frame)
   - 段索引 (0, 1, 2, ...)
3. 创建35个Segment对象
4. 因为配置了`max_segments=3`，只取前3个进行处理

**Segment结构**:
```python
Segment 0: [0.0s - 60.0s]   帧: [0 - 1800]
Segment 1: [60.0s - 120.0s] 帧: [1800 - 3600]
Segment 2: [120.0s - 180.0s] 帧: [3600 - 5400]
... (共35个)
```

---

### 步骤3: 处理每个Segment (最核心)

**输出**:
```
[3/6] Processing segments (3 total)...
  Processing segment 1/3 [0.0s - 60.0s]...
    → Sampled 3 frames
    ✓ Analyzed: Description: The segment opens with a dramatic shot...
  Processing segment 2/3 [60.0s - 120.0s]...
    → Sampled 3 frames
    ✓ Analyzed: Description: This segment shows pre-match scenes...
  Processing segment 3/3 [120.0s - 180.0s]...
    → Sampled 3 frames
    ✓ Analyzed: Description: A football video game segment shows...
```

**代码位置**: `processors/video_qa_pipeline.py:197-281`

这一步是**最核心**的，包含两个子步骤：

#### 3.1 采样帧 (SAMPLE操作)

**代码**:
```python
# 生成时间戳
timestamps = self._generate_segment_timestamps(segment)
# [20.0s, 40.0s, 60.0s] for segment [0-60s]

# 采样帧
frames = self.atomic_ops.sample(
    source=video_meta,
    method="timestamps",
    params={"timestamps": timestamps}
)
```

**底层实现**: `processors/video_processor.py:97-217`

```python
def sample_frames(self, video_meta: VideoMeta, method: str, params: Dict) -> List[Frame]:
    if method == "timestamps":
        timestamps = params["timestamps"]
        frames = []

        cap = cv2.VideoCapture(video_meta.file_path)

        for timestamp in timestamps:
            # 定位到该时间点
            frame_index = int(timestamp * video_meta.fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)

            # 读取帧
            ret, frame_img = cap.read()
            if ret:
                # 保存为临时文件
                frame_path = self._save_frame_temp(frame_img, frame_id)

                # 创建Frame对象
                frame = Frame(
                    frame_id=frame_id,
                    video_id=video_meta.video_id,
                    frame_index=frame_index,
                    timestamp_sec=timestamp,
                    image_path=frame_path
                )
                frames.append(frame)

        return frames
```

**这个子步骤做了什么**:
1. 根据segment时间范围生成采样时间点:
   - Segment [0-60s]: 采样 [20.0s, 40.0s, 60.0s]
   - Segment [60-120s]: 采样 [80.0s, 100.0s, 120.0s]
   - Segment [120-180s]: 采样 [140.0s, 160.0s, 180.0s]

2. 对每个时间点:
   - 使用OpenCV定位到该帧 (`cap.set(cv2.CAP_PROP_POS_FRAMES, ...)`)
   - 读取图像数据 (`cap.read()`)
   - 保存为临时JPG文件 (`data/temp/frames/vid_xxx_frame_yyy.jpg`)
   - 创建Frame对象（包含frame_id、timestamp、image_path等）

3. 返回3个Frame对象的列表

**Frame对象包含**:
```python
Frame(
    frame_id="frame_vid_xxx_000900",
    video_id="vid_xxx",
    frame_index=900,
    timestamp_sec=30.0,
    image_path="/path/to/temp/frames/vid_xxx_frame_000900.jpg",
    width=1280,
    height=720
)
```

#### 3.2 分析Segment (CALL_MODEL操作)

**代码位置**: `processors/video_qa_pipeline.py:296-363`

```python
def _analyze_segment(self, segment, frames, video_meta, experiment) -> SegmentCaption:
    # 构建prompt
    prompt = f"""Analyze this video segment from {segment.time_span.start_sec:.1f}s to {segment.time_span.end_sec:.1f}s.

Below are {len(frames)} frames sampled from this segment.

Please provide:
1. A concise description of what happens in this segment (2-3 sentences)
2. Main activities or events
3. Key objects or people visible

Format your response as:
Description: [your description]
Events: [list of events]
Objects: [list of objects]"""

    # 调用MLLM API
    response = self.atomic_ops.call_model(
        model_type="mllm",
        model_name=self.config["mllm_model"],
        inputs={
            "prompt": prompt,
            "frames": frames,
            "system_prompt": "You are a helpful video analysis assistant."
        },
        params={
            "temperature": self.config["temperature"],
            "max_tokens": self.config["max_tokens_per_segment"]
        }
    )

    # 解析响应，创建SegmentCaption
    caption = SegmentCaption(
        caption_id=f"caption_{segment.segment_id}",
        segment_id=segment.segment_id,
        caption=response.output,
        confidence=0.9 if response.success else 0.0,
        key_frames=[f.frame_id for f in frames],
        model_name=self.config["mllm_model"]
    )

    return caption
```

**底层MLLM调用**: `agents/mllm_client.py:93-159`

```python
def call(self, request: MLLMRequest) -> MLLMResponse:
    # 构建消息
    messages = self._build_messages(request)
    # messages = [
    #     {"role": "system", "content": "You are a helpful..."},
    #     {"role": "user", "content": [
    #         {"type": "text", "text": "Analyze this video segment..."},
    #         {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,xxx"}},
    #         {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,yyy"}},
    #         {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,zzz"}}
    #     ]}
    # ]

    # 调用OpenAI API
    api_response = self.client.chat.completions.create(
        model=request.model_name,
        messages=messages,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    )

    # 解析响应
    text = api_response.choices[0].message.content
    usage = api_response.usage

    return MLLMResponse(
        text=text,
        total_tokens=usage.total_tokens,
        cost_usd=self._calculate_cost(usage.prompt_tokens, usage.completion_tokens)
    )
```

**图像处理**: `agents/mllm_client.py:252-278`

```python
def _format_image(self, image_data: str) -> Optional[Dict]:
    # 检测是文件路径
    if os.path.exists(image_data):
        # 读取文件
        with open(image_data, 'rb') as f:
            image_bytes = f.read()
            base64_str = base64.b64encode(image_bytes).decode('utf-8')

        # 转换为data URL
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_str}"
            }
        }
```

**这个子步骤做了什么**:

1. **构建Prompt**: 明确告诉模型要分析哪个时间段，有几帧图片，期望的输出格式

2. **准备图像**:
   - 读取3个帧的JPG文件
   - 转换为base64编码
   - 格式化为OpenAI API接受的格式

3. **调用API**:
   - 发送请求到 `http://38.46.219.254:3009/v1` (您的API endpoint)
   - 模型: gpt-5
   - 输入: prompt文本 + 3张图片的base64
   - max_tokens: 4000 (上限，让模型自然完成)

4. **API返回**:
   ```
   Description: The segment opens with a dramatic shot of the Emirates FA Cup trophy...
   Events: Trophy reveal, stadium crowd, broadcast graphics, pre-match atmosphere
   Objects: FA Cup trophy, stadium, broadcast overlays, Manchester City jersey
   ```

5. **Token统计**:
   - Prompt tokens: ~2,900 (包含3张图片的编码)
   - Completion tokens: ~900 (模型生成的文本)
   - Total: ~3,800 tokens
   - Cost: ~$0.15

6. **创建SegmentCaption对象**:
   ```python
   SegmentCaption(
       caption_id="caption_seg_0001",
       segment_id="seg_0001",
       caption="Description: The segment opens with...",
       confidence=0.9,
       key_frames=["frame_001", "frame_002", "frame_003"],
       model_name="gpt-5"
   )
   ```

7. **重复3次**，分析3个segments

---

### 步骤4: 聚合Segment理解

**输出**:
```
[4/6] Aggregating segment understanding...
  ✓ Aggregated 3 segment descriptions
```

**代码位置**: `processors/video_qa_pipeline.py:386-398`

```python
def _aggregate_understanding(self, segment_captions: List[SegmentCaption]) -> str:
    """Step 4: Aggregate segment understanding"""
    aggregated_text = "Video segment analysis:\n\n"

    for i, caption in enumerate(segment_captions, 1):
        aggregated_text += f"Segment {i} ({caption.segment_id}):\n"
        aggregated_text += f"{caption.caption}\n\n"

    return aggregated_text
```

**这一步做了什么**:
1. 收集3个SegmentCaption的描述文本
2. 格式化为结构化文本:
   ```
   Video segment analysis:

   Segment 1 (seg_0001):
   Description: The segment opens with a dramatic shot...
   Events: Trophy reveal, stadium crowd...
   Objects: FA Cup trophy, stadium...

   Segment 2 (seg_0002):
   Description: This segment shows pre-match scenes...
   Events: Player walkout, team lineup...
   Objects: Players, jerseys, stadium...

   Segment 3 (seg_0003):
   Description: A football video game segment shows...
   Events: Kickoff, attack, goal...
   Objects: Ball, players, scoreboard...
   ```

3. 这个聚合文本将作为最终QA的context

---

### 步骤5: 回答问题 (最终QA)

**输出**:
```
[5/6] Answering question...
  ✓ Generated answer (676 chars)
```

**代码位置**: `processors/video_qa_pipeline.py:400-464`

```python
def _answer_question(self, question: str, aggregated_understanding: str,
                     experiment: VideoExperimentRun) -> str:
    """Step 5: Answer question based on understanding"""

    # 构建最终QA prompt
    prompt = f"""Based on the following video analysis, please answer the question.

Video Analysis:
{aggregated_understanding}

Question: {question}

Please provide a clear, concise answer based only on the video analysis above."""

    # 调用MLLM (纯文本，无图片)
    response = self.atomic_ops.call_model(
        model_type="mllm",
        model_name=self.config["mllm_model"],
        inputs={
            "prompt": prompt,
            "frames": [],  # 无图片
            "system_prompt": "You are a helpful video QA assistant."
        },
        params={
            "temperature": self.config["temperature"],
            "max_tokens": self.config["max_tokens_qa"]
        }
    )

    # 更新统计
    experiment.total_api_calls += 1
    if response.success:
        experiment.total_tokens_used += response.total_tokens
        experiment.total_cost_usd += response.cost_usd

    return response.output
```

**这一步做了什么**:

1. **构建最终prompt**:
   ```
   Based on the following video analysis, please answer the question.

   Video Analysis:
   [3个segments的完整描述]

   Question: What is happening in this video? Describe the main content and activities.

   Please provide a clear, concise answer...
   ```

2. **调用MLLM API** (第4次API调用):
   - 输入: 只有文本，**没有图片**
   - Prompt tokens: ~1,500 (包含3个segment的描述)
   - Completion tokens: ~700 (生成的回答)
   - Total: ~2,200 tokens
   - Cost: ~$0.10

3. **模型生成回答**:
   ```
   - The video presents an FA Cup match setup for Manchester City vs Manchester United...
   - Pre-match build-up follows in a packed stadium...
   - EA Sports/FA Cup branding indicates it's a football video game...
   - After kickoff, the blue team attacks and scores...
   ```

4. **更新实验统计**:
   - total_api_calls: 4 (3个segment + 1个QA)
   - total_tokens_used: 13,185
   - total_cost_usd: $0.5044

---

### 步骤6: 最终化实验

**输出**:
```
[6/6] Finalizing experiment...

✓ Pipeline completed successfully!
  Total API calls: 4
  Total tokens: 13185
  Estimated cost: $0.5044
```

**代码位置**: `processors/video_qa_pipeline.py:467-479`

```python
def _finalize_experiment(self, experiment: VideoExperimentRun, status: ProcessingStatus):
    """Step 6: Finalize experiment tracking"""
    experiment.status = status
    experiment.end_time = datetime.now().isoformat()

    # 计算总时长
    if experiment.start_time:
        start = datetime.fromisoformat(experiment.start_time)
        end = datetime.fromisoformat(experiment.end_time)
        experiment.total_duration_ms = (end - start).total_seconds() * 1000
```

**这一步做了什么**:
1. 设置实验状态: `status = completed`
2. 记录结束时间
3. 计算总处理时间: 127.72秒
4. 所有数据保存在VideoExperimentRun对象中

---

## 数据流总结

```
输入: video.mp4 + question
    ↓
[1] VideoMeta (元数据)
    video_id, duration, fps, resolution
    ↓
[2] List[Segment] (35个segments)
    seg_0001: [0-60s]
    seg_0002: [60-120s]
    seg_0003: [120-180s]
    ...
    ↓
[3] 对每个segment:
    ├─ List[Frame] (3帧)
    │   frame_001 @ 20s
    │   frame_002 @ 40s
    │   frame_003 @ 60s
    │
    └─ SegmentCaption
        caption_id, segment_id, caption_text
    ↓
[4] Aggregated Understanding (文本)
    "Segment 1: ...\nSegment 2: ...\nSegment 3: ..."
    ↓
[5] Final Answer (文本)
    "- The video presents an FA Cup match..."
    ↓
[6] VideoExperimentRun (完整记录)
    run_id, status, tokens, cost, duration
```

---

## API调用详情

### 调用1-3: Segment分析 (3次)

**每次调用**:
```
Endpoint: http://38.46.219.254:3009/v1
Model: gpt-5
Input:
  - Prompt: "Analyze this video segment from X to Y..."
  - Images: 3张 (base64编码)
  - max_tokens: 4000

Output:
  - Text: ~800-1,200 tokens
  - Prompt tokens: ~2,900
  - Total tokens: ~3,700-4,100
  - Cost: ~$0.13-0.15
  - Time: ~35-40秒
```

### 调用4: 最终QA (1次)

**调用详情**:
```
Endpoint: http://38.46.219.254:3009/v1
Model: gpt-5
Input:
  - Prompt: "Based on the following video analysis..."
  - Images: 0 (纯文本)
  - max_tokens: 3000

Output:
  - Text: ~700 tokens
  - Prompt tokens: ~1,500
  - Total tokens: ~2,200
  - Cost: ~$0.10
  - Time: ~20-25秒
```

### 总计

```
API调用: 4次
Tokens: 13,185
成本: $0.5044
时间: 127.72秒 (~2分钟)
```

---

## 关键技术点

### 1. 图像Base64编码

**为什么**: OpenAI API要求图片以base64格式传输

**实现**: `agents/mllm_client.py:252-278`
- 读取JPG文件
- 转换为base64字符串
- 格式化为 `data:image/jpeg;base64,{base64_str}`

### 2. Token统计

**来源**: API实际返回的usage对象

**实现**: `agents/mllm_client.py:308-314`
```python
usage = api_response.usage
prompt_tokens = usage.prompt_tokens      # 实际消耗
completion_tokens = usage.completion_tokens  # 实际消耗
total_tokens = usage.total_tokens        # 实际总计
```

**不是基于max_tokens设置值！**

### 3. 成本计算

**实现**: `agents/mllm_client.py:355-370`
```python
def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
    # 从配置读取价格（美元/1K tokens）
    prompt_price = 0.01   # $0.01/1K tokens
    completion_price = 0.03  # $0.03/1K tokens

    cost = (prompt_tokens / 1000.0 * prompt_price +
            completion_tokens / 1000.0 * completion_price)
    return cost
```

### 4. 实验追踪

**VideoExperimentRun对象** (`experiments/video_variables.py:680-733`):
```python
@dataclass
class VideoExperimentRun:
    run_id: str
    video_meta: VideoMeta
    segments: List[str]          # segment IDs
    frames: List[str]            # frame IDs
    total_api_calls: int         # API调用次数
    total_tokens_used: int       # Token消耗
    total_cost_usd: float        # 成本
    total_duration_ms: float     # 处理时间
    status: ProcessingStatus     # 状态
```

**追踪所有关键信息，便于分析和优化**

---

## 完整代码调用链

```
examples/video_qa_pipeline_example.py
  └─ VideoQAPipeline.run_video_qa()
      ├─ [1] _extract_metadata()
      │   └─ VideoProcessor.extract_metadata()
      │       └─ cv2.VideoCapture() + 读取属性
      │
      ├─ [2] _segment_video()
      │   └─ AtomicOperationsImplementation.segment()
      │       └─ VideoProcessor.segment_video_fixed_duration()
      │           └─ 计算时间范围，创建Segment对象
      │
      ├─ [3] _process_segments() (循环3次)
      │   ├─ _generate_segment_timestamps()
      │   │   └─ 计算采样时间点
      │   │
      │   ├─ AtomicOperationsImplementation.sample()
      │   │   └─ VideoProcessor.sample_frames()
      │   │       └─ cv2.VideoCapture() + 定位帧 + 读取 + 保存
      │   │
      │   └─ _analyze_segment()
      │       └─ AtomicOperationsImplementation.call_model()
      │           └─ MLLMClient.call()
      │               ├─ _format_image() (读取+base64)
      │               ├─ OpenAI API调用
      │               └─ _parse_response() (解析+统计)
      │
      ├─ [4] _aggregate_understanding()
      │   └─ 格式化所有segment描述
      │
      ├─ [5] _answer_question()
      │   └─ AtomicOperationsImplementation.call_model()
      │       └─ MLLMClient.call() (纯文本)
      │
      └─ [6] _finalize_experiment()
          └─ 更新状态、计算时长
```

---

## 总结

这个框架的核心思想是：

1. **分而治之**: 长视频 → segments → 理解
2. **多模态分析**: 图片 + 文本 → MLLM
3. **层次聚合**: Segment理解 → 整体理解 → QA回答
4. **完整追踪**: 记录所有API调用、tokens、成本

**优点**:
- 可以处理任意长度视频
- 成本可控（通过segment数、帧数）
- 模块化设计，易扩展
- 完整的实验记录

**当前配置**:
- 每60秒一个segment
- 每segment采样3帧
- 处理前3个segments
- 总成本: ~$0.50 (3分钟视频)
- 处理时间: ~2分钟
