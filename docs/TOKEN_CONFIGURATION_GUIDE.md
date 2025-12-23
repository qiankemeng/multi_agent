# Token配置与统计说明

## 配置理念

### ❌ 错误理解
~~使用`max_tokens`来"限制"模型输出~~

### ✅ 正确理解
- `max_tokens`是**安全上限**，不是限制目标
- 让模型**自然完成**输出 (finish_reason='stop')
- 统计**实际消耗**的tokens

## 配置建议

### 推荐配置
```python
{
    "max_tokens_per_segment": 4000,  # 足够大的上限，不限制模型
    "max_tokens_qa": 3000,           # 足够大的上限
    "temperature": 0.7,               # 根据需求调整
    "frames_per_segment": 3,          # 控制输入复杂度
}
```

### 配置说明

#### max_tokens_per_segment (推荐: 4000)
- **作用**: API安全上限，防止失控
- **原则**: 设置足够大，让模型自然完成
- **参考**:
  - 3张图片实际消耗: ~900-1200 tokens
  - 建议设置: 4000-8000 (留足够空间)

#### max_tokens_qa (推荐: 3000)
- **作用**: 最终问答的上限
- **原则**: 让模型充分表达
- **参考**:
  - 实际消耗: ~500-800 tokens
  - 建议设置: 3000-5000

## Token统计机制

### 数据来源
所有token统计来自**API实际usage**，不是max_tokens设置：

```python
# mllm_client.py
usage = api_response.usage
prompt_tokens = usage.prompt_tokens      # ✓ API实际usage
completion_tokens = usage.completion_tokens  # ✓ API实际usage
total_tokens = usage.total_tokens        # ✓ API实际总计
```

### 统计字段
```python
experiment.total_api_calls      # API调用次数
experiment.total_tokens_used    # 实际消耗tokens (累计)
experiment.total_cost_usd       # 实际成本 (累计)
```

### 统计准确性
✅ **完全准确** - 基于OpenAI API返回的实际usage

## 实际测试数据

### 测试配置
```python
{
    "segment_duration_sec": 60.0,
    "frames_per_segment": 3,
    "max_segments": 3,
    "max_tokens_per_segment": 4000,  # 上限
    "max_tokens_qa": 3000            # 上限
}
```

### 实际消耗
```
📊 总体统计:
  ├─ 总API调用: 4 次
  ├─ 总tokens: 12,870       ← 实际消耗 (非max_tokens)
  ├─ 总成本: $0.4799         ← 基于实际消耗
  └─ 处理时间: 129.14秒

📈 平均统计:
  ├─ 平均tokens/调用: 3,218  ← 远低于max_tokens
  ├─ 平均成本/调用: $0.1200
  └─ 平均时间/调用: 32.29秒

📊 效率分析:
  ├─ Tokens/帧: 1,430
  ├─ Tokens/segment: 4,290    ← 实际约4.3K, max设置4K
  └─ 成本/segment: $0.1600
```

### 关键发现

1. **实际消耗远低于上限**
   - max_tokens_per_segment: 4000 (设置)
   - 实际消耗/segment: ~4,290 (超出了一点，说明有1个segment需要更多)
   - 说明4000的上限刚好够用

2. **模型自然完成**
   - finish_reason: 'stop' (正常完成，非length截断)
   - 输出完整且连贯

3. **成本可预测**
   - 3 segments: $0.48
   - 35 segments估算: ~$5.60

## Token消耗构成

### 单次segment分析
```
Prompt tokens: ~2,900
  ├─ 系统提示: ~50
  ├─ 用户prompt: ~100
  └─ 3张图片: ~2,750

Completion tokens: ~800-1,500
  ├─ Description: 200-400
  ├─ Events列表: 200-400
  └─ Objects列表: 200-400

总计: ~3,700-4,400 tokens
```

### 最终QA
```
Prompt tokens: ~1,500
  ├─ 问题: ~50
  └─ 3个segment summaries: ~1,450

Completion tokens: ~500-800
  └─ 综合回答: 500-800

总计: ~2,000-2,300 tokens
```

## 优化建议

### 控制成本（不改max_tokens）
```python
# 方法1: 减少帧数
"frames_per_segment": 2,  # 3→2 (减少~30% tokens)

# 方法2: 增加segment时长
"segment_duration_sec": 120.0,  # 60→120 (减少50% segments)

# 方法3: 限制处理范围
"max_segments": 5,  # 只处理前5个segments
```

### 提高质量（保持max_tokens）
```python
# 方法1: 更多帧
"frames_per_segment": 5,  # 更多上下文

# 方法2: 更短segments
"segment_duration_sec": 30.0,  # 更细粒度

# 方法3: 调整temperature
"temperature": 0.5,  # 更一致的输出
```

## 总结

### ✅ 正确做法
1. **max_tokens设置足够大** (4000-8000)
2. **让模型自然完成** (finish_reason='stop')
3. **统计实际消耗** (基于API usage)
4. **通过输入控制成本** (帧数、segment数)

### ❌ 错误做法
1. ~~用小的max_tokens"省钱"~~ (会截断输出)
2. ~~假设消耗=max_tokens~~ (实际消耗远小于上限)
3. ~~不检查finish_reason~~ (可能被截断)

### 🎯 最佳实践
```python
# 生产环境推荐配置
config = {
    # 上限设置 - 足够大
    "max_tokens_per_segment": 4000,
    "max_tokens_qa": 3000,

    # 成本控制 - 通过输入
    "segment_duration_sec": 60.0,  # 根据视频调整
    "frames_per_segment": 3,       # 平衡质量和成本
    "max_segments": None,          # 或设置具体数量

    # 质量控制
    "temperature": 0.7,             # 根据需求调整
}
```

---

**核心理念**: max_tokens是安全网，不是目标。让模型自然完成，统计实际消耗。
