# 配置指南

本项目使用`.env`文件和`config`模块进行统一的配置管理。

## 快速开始

### 1. 复制配置模板

```bash
cp .env.example .env
```

### 2. 编辑配置文件

打开`.env`文件，至少需要设置：

```bash
# 必需：OpenAI API密钥
OPENAI_API_KEY=your-api-key-here

# 可选：其他配置使用默认值即可
```

### 3. 验证配置

```bash
# 查看当前配置
python config/settings.py

# 或在代码中
python -c "from config import settings; settings.print_summary()"
```

## 配置说明

### MLLM API配置

#### OpenAI (必需)

```bash
# API密钥（必需）
OPENAI_API_KEY=sk-your-key-here

# API基础URL（可选，默认官方API）
OPENAI_BASE_URL=https://api.openai.com/v1

# 默认模型（可选）
OPENAI_DEFAULT_MODEL=gpt-4-vision-preview

# 组织ID（可选）
OPENAI_ORGANIZATION_ID=

# 价格配置（美元/1K tokens）
OPENAI_PRICE_PROMPT_1K=0.01
OPENAI_PRICE_COMPLETION_1K=0.03
```

#### Claude (未来支持)

```bash
CLAUDE_API_KEY=your-claude-key
CLAUDE_BASE_URL=https://api.anthropic.com
CLAUDE_DEFAULT_MODEL=claude-3-opus-20240229
```

#### Gemini (未来支持)

```bash
GEMINI_API_KEY=your-gemini-key
GEMINI_BASE_URL=https://generativelanguage.googleapis.com
GEMINI_DEFAULT_MODEL=gemini-pro-vision
```

### MLLM调用参数

```bash
# 默认温度 (0.0-2.0，越低越确定)
MLLM_DEFAULT_TEMPERATURE=0.7

# 默认最大token数
MLLM_DEFAULT_MAX_TOKENS=1000

# 请求超时（秒）
MLLM_REQUEST_TIMEOUT=60

# 最大重试次数
MLLM_MAX_RETRIES=3

# 重试延迟（秒）
MLLM_RETRY_DELAY=1.0
```

### Agent配置

```bash
# 工具创建Agent
TOOL_CREATOR_MODEL=gpt-4-turbo-preview
TOOL_CREATOR_TEMPERATURE=0.3
TOOL_CREATOR_MAX_TOKENS=2000

# 工具使用Agent
TOOL_USER_MODEL=gpt-4-vision-preview
TOOL_USER_TEMPERATURE=0.7
TOOL_USER_MAX_TOKENS=1000
```

### 视频处理配置

```bash
# 分段策略 (fixed_duration, scene_detection, adaptive)
VIDEO_SEGMENTATION_STRATEGY=fixed_duration

# 固定时长分段（秒）
VIDEO_SEGMENT_DURATION=30

# 最大片段数
VIDEO_MAX_SEGMENTS=100

# 帧采样方法 (uniform, keyframe, adaptive)
FRAME_SAMPLING_METHOD=uniform

# 每个片段采样帧数
FRAMES_PER_SEGMENT=5

# 最大图像尺寸（像素）
MAX_IMAGE_SIZE=1024
```

### 路径配置

```bash
# 数据目录
DATA_DIR=./data

# 视频目录
VIDEO_DIR=./data/videos

# 输出目录
OUTPUT_DIR=./data/output

# 缓存目录
CACHE_DIR=./data/cache

# 临时文件目录
TEMP_DIR=./data/temp
```

### 日志配置

```bash
# 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# 日志文件路径
LOG_FILE=./logs/app.log

# 日志格式
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# 是否在控制台输出
LOG_TO_CONSOLE=true
```

### 成本控制

```bash
# 单次请求最大成本限制（美元，0表示不限制）
MAX_REQUEST_COST=0

# 每日最大成本限制（美元，0表示不限制）
MAX_DAILY_COST=0
```

### 实验配置

```bash
# 实验名称
EXPERIMENT_NAME=default_experiment

# 实验ID
EXPERIMENT_ID=

# 是否保存中间结果
SAVE_INTERMEDIATE_RESULTS=true

# 是否启用详细日志
VERBOSE=false
```

### 性能配置

```bash
# 并发请求数
MAX_CONCURRENT_REQUESTS=3

# 启用缓存
ENABLE_CACHE=true

# 缓存过期时间（秒）
CACHE_EXPIRY=3600
```

### 开发配置

```bash
# 环境模式 (development, production, testing)
ENVIRONMENT=development

# 是否启用调试模式
DEBUG=false

# 是否启用模拟模式（不实际调用API）
MOCK_MODE=false
```

## 在代码中使用配置

### 基本使用

```python
from config import settings

# 访问配置
api_key = settings.openai.api_key
model = settings.agent.tool_creator_model
temperature = settings.mllm.default_temperature

# 打印配置摘要
settings.print_summary()

# 验证配置
errors = settings.validate()
if errors:
    for error in errors:
        print(f"Error: {error}")
```

### Agent自动使用配置

Agent会自动从配置中读取默认值：

```python
from agents import ToolCreatorAgent, ToolUserAgent

# 自动使用配置中的模型和参数
creator = ToolCreatorAgent(agent_id="creator_001")
# 使用 settings.agent.tool_creator_model
# 使用 settings.agent.tool_creator_temperature
# 使用 settings.agent.tool_creator_max_tokens

user = ToolUserAgent(agent_id="user_001")
# 使用 settings.agent.tool_user_model
# 使用 settings.agent.tool_user_temperature
# 使用 settings.agent.tool_user_max_tokens
```

### 覆盖配置

如果需要使用不同的配置：

```python
from agents import MLLMClient, MLLMClientConfig

# 手动指定配置
custom_config = MLLMClientConfig(
    api_key="custom-key",
    default_model="gpt-4",
    default_temperature=0.5
)

client = MLLMClient(custom_config)
```

### 重新加载配置

```python
from config import reload_settings

# 修改.env文件后重新加载
settings = reload_settings()
```

## 配置优先级

配置值的优先级顺序（从高到低）：

1. 代码中显式指定的值
2. 环境变量
3. `.env`文件中的值
4. 默认值

## 最佳实践

### 1. 不要提交`.env`文件

`.env`文件已在`.gitignore`中，包含敏感信息，不应提交到版本控制。

### 2. 使用`.env.example`作为模板

`.env.example`文件可以提交，用于说明需要哪些配置项。

### 3. 不同环境使用不同配置

```bash
# 开发环境
cp .env.example .env.development

# 生产环境
cp .env.example .env.production

# 加载指定配置
export ENV_FILE=.env.production
```

### 4. 验证配置

在运行重要任务前，验证配置：

```python
from config import settings

errors = settings.validate()
if errors:
    print("Configuration errors:")
    for error in errors:
        print(f"  - {error}")
    exit(1)

# 继续执行...
```

### 5. 成本控制

设置成本限制避免意外费用：

```bash
# 单次请求不超过$0.10
MAX_REQUEST_COST=0.1

# 每日总成本不超过$10
MAX_DAILY_COST=10.0
```

## 常见问题

### Q: 为什么提示"OPENAI_API_KEY not set"？

A: 需要在`.env`文件中设置API密钥：

```bash
OPENAI_API_KEY=sk-your-key-here
```

或者使用mock模式进行测试：

```bash
MOCK_MODE=true
```

### Q: 如何使用不同的模型？

A: 修改`.env`文件中的模型配置：

```bash
# 使用GPT-4
TOOL_CREATOR_MODEL=gpt-4
TOOL_USER_MODEL=gpt-4-vision-preview
```

### Q: 如何降低成本？

A: 可以通过以下方式：

1. 使用更便宜的模型
2. 降低max_tokens
3. 减少每段的采样帧数
4. 启用缓存
5. 设置成本限制

```bash
TOOL_CREATOR_MAX_TOKENS=1000
FRAMES_PER_SEGMENT=3
ENABLE_CACHE=true
MAX_DAILY_COST=5.0
```

### Q: 配置修改后是否需要重启？

A: 是的，配置在程序启动时加载。修改后需要重启程序或调用`reload_settings()`。

## 相关文档

- `.env.example` - 配置模板
- `config/settings.py` - 配置管理代码
- `agents/mllm_client.py` - API客户端实现
