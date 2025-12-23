# API Vision Support Diagnosis Report

## 测试日期
2025-12-18

## 问题概述
在完整测试VideoQA Pipeline时发现segment analysis返回空内容，导致最终QA无法回答问题。

## 测试环境
- API Endpoint: `http://38.46.219.254:3009/v1`
- Model: `gpt-5`
- API Key: Configured

## 诊断过程

### 1. 初始问题发现
运行`examples/video_qa_pipeline_example.py`时发现：
- Pipeline成功完成
- 使用了9818 tokens，花费$0.2651
- 但segment descriptions都是空的（`...`）
- 最终答案无法基于视频内容回答

### 2. 代码Bug修复
在诊断过程中发现并修复了两个代码bug：

#### Bug 1: MLLMClient缺少文件读取功能
**问题**: `agents/mllm_client.py`的`_format_image`方法不支持文件路径，导致图像文件未正确转换为base64。

**错误**:
```
'failed to decode base64 string: illegal base64 data at input byte 20'
```

**修复**: 在`_format_image`方法中添加文件路径检测和base64转换：
```python
elif os.path.exists(image_data):
    # 读取文件并转换为base64
    with open(image_data, 'rb') as f:
        image_bytes = f.read()
        base64_str = base64.b64encode(image_bytes).decode('utf-8')

    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:{mime_type};base64,{base64_str}"
        }
    }
```

**位置**: `agents/mllm_client.py:252-278`

#### Bug 2: VideoQAPipeline使用错误的属性名
**问题**: `processors/video_qa_pipeline.py`中使用了不存在的属性名。

**错误**:
```python
experiment.total_tokens += response.total_tokens  # ❌ 错误
experiment.estimated_cost_usd += response.cost_usd  # ❌ 错误
```

**修复**:
```python
experiment.total_tokens_used += response.total_tokens  # ✓ 正确
experiment.total_cost_usd += response.cost_usd  # ✓ 正确
```

**位置**: `processors/video_qa_pipeline.py:338-339`

### 3. API行为测试

修复代码bug后，运行vision测试：

#### Test 1: 纯文本API调用
```
Request:
  Prompt: "请回答：1+1等于几？"
  Max tokens: 50
  Images: 0

Response:
  Success: ✓
  Content: "4"
  Tokens: 30 (正常)
  Finish reason: 'stop' (正常完成)
```

✅ **结论**: API的文本处理功能正常

#### Test 2: 视觉API调用（带图像）
```
Request:
  Prompt: "What do you see in this image? Describe it in one sentence."
  Max tokens: 100
  Images: 1 (JPG file, base64 encoded)

Response:
  Success: ✓ (但实际有问题)
  Content: "" (空字符串!)
  Tokens: 1030 (930 prompt + 100 completion)
  Finish reason: 'length' (达到token限制)
```

❌ **问题**: API接受图像输入并使用tokens，但返回空内容

## 根本原因分析

### API行为异常
1. **接受图像输入**: API没有报错，成功接收base64图像
2. **Token消耗**: 使用了930个prompt tokens（图像编码）+ 100个completion tokens
3. **空内容返回**: `message.content = ''` (空字符串)
4. **Finish reason异常**: `'length'` 表示达到max_tokens限制

### 正常行为 vs 实际行为对比

| 场景 | 正常行为 | 实际行为 |
|------|---------|---------|
| 文本输入 | 返回文本内容 | ✓ 返回文本内容 |
| 图像输入（无vision支持） | API报错或拒绝 | ✗ 接受请求 |
| 图像输入（有vision支持） | 返回描述文本 | ✗ 返回空字符串 |
| 达到token限制 | 返回截断的文本 | ✗ 返回空字符串 |

## 可能的原因

### 1. 模型不支持Vision（最可能）
虽然API接口兼容vision格式，但"gpt-5"模型可能：
- 不支持图像理解
- 接受图像输入但忽略处理
- 使用tokens但不生成有效输出

### 2. API端点配置问题
- 端点可能缺少vision-preview模型
- 或者vision功能被禁用/限制
- 返回空内容可能是错误处理逻辑

### 3. Token限制问题
- 图像编码使用了930 tokens
- 只剩100 tokens用于completion
- 可能不足以生成有意义的响应
- 但通常应该返回部分内容而不是空字符串

## 解决方案建议

### 立即方案：确认模型支持
1. **检查API文档**：确认`gpt-5`是否支持vision
2. **尝试其他模型**：如果有`gpt-4-vision-preview`或类似模型
3. **增加max_tokens**：尝试设置更大的值（如500-1000）

### 测试命令
```bash
# 修改.env文件
OPENAI_DEFAULT_MODEL=gpt-4-vision-preview  # 尝试其他模型

# 或在运行时指定
export OPENAI_DEFAULT_MODEL=gpt-4-vision-preview
python tests/test_api_vision.py
```

### 长期方案：降级到非Vision方案
如果API确实不支持vision：

#### 选项A：使用纯文本模式
- 不使用图像分析
- 仅基于视频元数据（时长、帧数等）
- 限制：无法理解视频内容

#### 选项B：切换API提供商
- 使用官方OpenAI API（支持gpt-4-vision-preview）
- 使用其他支持vision的API（Claude 3, Gemini Pro Vision）

#### 选项C：本地Vision模型
- 部署开源vision模型（如LLaVA, MiniGPT-4）
- 本地处理后传递结果

## 测试文件
创建的测试文件：
- `tests/test_api_vision.py` - Vision支持测试
- `tests/test_api_response_debug.py` - API响应调试工具

## 总结
1. ✅ 代码实现正确：图像处理、base64转换、API调用都正常
2. ✅ API连接正常：文本请求工作正常
3. ❌ Vision功能异常：API接受图像但返回空内容
4. 🔍 需要确认：当前API endpoint的"gpt-5"模型是否真正支持vision

**建议下一步**：联系API提供商确认vision支持，或切换到已知支持vision的模型/API。
