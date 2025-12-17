# MVP实验变量表文档

## 概述

本文档定义了最小可行实验（MVP）所需的所有数据变量。这些变量独立于系统配置，专门用于实验数据的定义和管理。

**设计原则**：
- ✅ 所有实验数据变量集中在 `experiments/mvp_variables.py`
- ✅ 修改变量只需更新此文件或本MD文档
- ✅ 变量定义清晰，易于理解和扩展
- ✅ 不需要高动态性，结构稳定

## 实验场景

### MVP实验目标
验证多Agent系统（工具创建Agent + 工具使用Agent）的可行性

### 实验流程
```
1. [初始化] 创建实验运行记录
    ↓
2. [工具请求] 工具使用Agent创建工具请求
    ↓
3. [工具创建] 工具创建Agent生成工具
    ↓
4. [工具执行] 工具使用Agent执行任务
    ↓
5. [结果验证] 验证执行结果
    ↓
6. [完成] 记录实验指标
```

## 变量表定义

### 1. ToolCreationRequest - 工具创建请求

**用途**: 工具使用Agent向工具创建Agent发送的工具创建请求

**字段定义**:
```python
ToolCreationRequest(
    request_id: str              # 请求唯一标识
    tool_type: ToolType          # 工具类型（枚举）
    tool_name: str               # 工具名称
    description: str             # 工具描述
    requirements: Dict           # 功能需求（键值对）
    input_spec: Dict             # 输入参数规格
    output_spec: Dict            # 输出规格
    requester_id: str            # 请求者Agent ID
    created_at: str              # 创建时间（自动生成）
    priority: int                # 优先级 1-5，默认2
)
```

**示例**:
```python
request = ToolCreationRequest(
    request_id="req_001",
    tool_type=ToolType.STRING_TRANSFORM,
    tool_name="string_reverser",
    description="反转输入的字符串",
    requirements={
        "function": "reverse_string",
        "complexity": "simple"
    },
    input_spec={"text": "string"},
    output_spec={"reversed_text": "string"},
    requester_id="tool_user_001"
)
```

**修改方式**:
- 添加新字段：在 `mvp_variables.py` 的 `ToolCreationRequest` 类中添加
- 修改字段类型：直接修改字段定义

---

### 2. CreatedTool - 创建的工具

**用途**: 工具创建Agent创建的工具实例

**字段定义**:
```python
CreatedTool(
    tool_id: str                 # 工具唯一标识
    request_id: str              # 对应的请求ID
    tool_name: str               # 工具名称
    tool_type: ToolType          # 工具类型
    implementation_code: str     # 实现代码（字符串形式）
    implementation_function: Any # 实现函数（可调用对象）
    input_parameters: Dict       # 输入参数定义
    output_format: Dict          # 输出格式定义
    creator_id: str              # 创建者Agent ID
    created_at: str              # 创建时间（自动生成）
    version: str                 # 版本号，默认"1.0.0"
    test_cases: List[Dict]       # 测试用例列表
)
```

**示例**:
```python
tool = CreatedTool(
    tool_id="tool_001",
    request_id="req_001",
    tool_name="string_reverser",
    tool_type=ToolType.STRING_TRANSFORM,
    implementation_code="def reverse(text): return text[::-1]",
    implementation_function=lambda text: text[::-1],
    input_parameters={"text": "string"},
    output_format={"reversed_text": "string"},
    creator_id="tool_creator_001"
)
```

---

### 3. TaskData - 任务数据

**用途**: 需要使用工具处理的输入数据

**字段定义**:
```python
TaskData(
    task_id: str                 # 任务唯一标识
    data_type: str               # 数据类型（text, number, json等）
    input_data: Any              # 输入数据
    tool_name: str               # 要使用的工具名称
    parameters: Dict             # 额外参数
    created_at: str              # 创建时间（自动生成）
    source: str                  # 数据来源
    description: str             # 任务描述
    expected_output: Any         # 期望输出（用于验证）
)
```

**示例**:
```python
task = TaskData(
    task_id="task_001",
    data_type="text",
    input_data="Hello World",
    tool_name="string_reverser",
    parameters={},
    source="user_input",
    description="反转字符串测试",
    expected_output="dlroW olleH"
)
```

---

### 4. TaskExecution - 任务执行记录

**用途**: 记录工具执行任务的过程和结果

**字段定义**:
```python
TaskExecution(
    execution_id: str            # 执行唯一标识
    task_id: str                 # 关联的任务ID
    tool_id: str                 # 使用的工具ID
    tool_name: str               # 工具名称
    status: TaskStatus           # 执行状态（枚举）
    start_time: str              # 开始时间（自动生成）
    end_time: str                # 结束时间
    duration_ms: float           # 执行时长（毫秒）
    output_data: Any             # 输出数据
    error_message: str           # 错误信息（如果失败）
    executor_id: str             # 执行者Agent ID
    retry_count: int             # 重试次数，默认0
)
```

**示例**:
```python
execution = TaskExecution(
    execution_id="exec_001",
    task_id="task_001",
    tool_id="tool_001",
    tool_name="string_reverser",
    status=TaskStatus.COMPLETED,
    duration_ms=50.2,
    output_data="dlroW olleH",
    executor_id="tool_user_001"
)
```

---

### 5. ExperimentRun - 实验运行记录

**用途**: 记录一次完整的MVP实验运行

**字段定义**:
```python
ExperimentRun(
    run_id: str                  # 运行唯一标识
    experiment_name: str         # 实验名称
    start_time: str              # 开始时间（自动生成）
    end_time: str                # 结束时间
    total_duration_ms: float     # 总时长
    current_phase: ExperimentPhase  # 当前阶段（枚举）
    phases_completed: List[str]  # 已完成的阶段列表
    agents: Dict[str, str]       # 参与的Agent {id: name}
    tool_requests: List[str]     # 请求ID列表
    created_tools: List[str]     # 创建的工具ID列表
    tasks: List[str]             # 任务ID列表
    executions: List[str]        # 执行ID列表
    success: bool                # 实验是否成功，默认False
    total_tasks: int             # 总任务数，默认0
    successful_tasks: int        # 成功任务数，默认0
    failed_tasks: int            # 失败任务数，默认0
    metrics: Dict                # 性能指标
    description: str             # 实验描述
    notes: List[str]             # 备注列表
)
```

**示例**:
```python
experiment = ExperimentRun(
    run_id="run_001",
    experiment_name="string_reverser_test",
    current_phase=ExperimentPhase.INITIALIZATION,
    agents={
        "tool_user_001": "工具使用Agent",
        "tool_creator_001": "工具创建Agent"
    },
    description="测试字符串反转工具的创建和使用"
)
```

---

### 6. ValidationResult - 验证结果

**用途**: 验证实验结果是否符合预期

**字段定义**:
```python
ValidationResult(
    validation_id: str           # 验证唯一标识
    execution_id: str            # 关联的执行ID
    passed: bool                 # 是否通过验证
    expected_output: Any         # 期望输出
    actual_output: Any           # 实际输出
    match_score: float           # 匹配分数 0.0-1.0，默认0.0
    differences: List[str]       # 差异列表
    validated_at: str            # 验证时间（自动生成）
    validator_id: str            # 验证者ID
)
```

**示例**:
```python
validation = ValidationResult(
    validation_id="val_001",
    execution_id="exec_001",
    passed=True,
    expected_output="dlroW olleH",
    actual_output="dlroW olleH",
    match_score=1.0,
    differences=[]
)
```

---

## 枚举类型

### ToolType - 工具类型
```python
STRING_TRANSFORM   # 字符串转换
TEXT_ANALYSIS      # 文本分析
DATA_VALIDATION    # 数据验证
CUSTOM             # 自定义
```

### TaskStatus - 任务状态
```python
PENDING      # 待处理
PROCESSING   # 处理中
COMPLETED    # 已完成
FAILED       # 失败
```

### ExperimentPhase - 实验阶段
```python
INITIALIZATION      # 初始化
TOOL_REQUEST        # 工具请求
TOOL_CREATION       # 工具创建
TOOL_EXECUTION      # 工具执行
RESULT_VALIDATION   # 结果验证
COMPLETED           # 完成
```

---

## 实验配置常量

```python
ExperimentConfig.DEFAULT_TIMEOUT_SECONDS = 30
ExperimentConfig.DEFAULT_MAX_RETRIES = 3
ExperimentConfig.TOOL_CREATION_TIMEOUT = 10
ExperimentConfig.TASK_EXECUTION_TIMEOUT = 5
ExperimentConfig.VALIDATION_THRESHOLD = 0.95
```

---

## 预定义实验场景

### 场景1: 字符串反转工具
```python
scenario = MVPScenarios.get_string_reverser_scenario()
# 返回：工具请求配置 + 测试数据
```

### 场景2: 大写转换工具
```python
scenario = MVPScenarios.get_uppercase_converter_scenario()
```

### 场景3: 单词计数工具
```python
scenario = MVPScenarios.get_word_counter_scenario()
```

---

## 如何使用这些变量

### 1. 导入变量
```python
from experiments import (
    ToolCreationRequest,
    CreatedTool,
    TaskData,
    TaskExecution,
    ExperimentRun,
    ValidationResult,
    ToolType,
    TaskStatus,
    ExperimentPhase,
    MVPScenarios
)
```

### 2. 创建实验
```python
# 获取预定义场景
scenario = MVPScenarios.get_string_reverser_scenario()

# 创建实验运行
experiment = ExperimentRun(
    run_id="run_001",
    experiment_name=scenario["name"],
    description=scenario["description"]
)

# 创建工具请求
request = ToolCreationRequest(
    request_id="req_001",
    **scenario["tool_request"]
)

# 创建任务数据
tasks = []
for i, test_case in enumerate(scenario["test_data"]):
    task = TaskData(
        task_id=f"task_{i:03d}",
        data_type="text",
        input_data=test_case["input"],
        expected_output=test_case["expected"]
    )
    tasks.append(task)
```

### 3. 记录执行
```python
execution = TaskExecution(
    execution_id="exec_001",
    task_id=task.task_id,
    tool_id=tool.tool_id,
    tool_name=tool.tool_name,
    status=TaskStatus.PROCESSING
)

# 执行后更新
execution.status = TaskStatus.COMPLETED
execution.output_data = result
execution.duration_ms = 50.2
```

### 4. 验证结果
```python
validation = ValidationResult(
    validation_id="val_001",
    execution_id=execution.execution_id,
    expected_output=task.expected_output,
    actual_output=execution.output_data,
    passed=(task.expected_output == execution.output_data),
    match_score=1.0 if passed else 0.0
)
```

---

## 如何修改变量

### 方式1: 修改Python代码（推荐用于结构性修改）
直接编辑 `experiments/mvp_variables.py` 文件：

```python
@dataclass
class ToolCreationRequest:
    # 添加新字段
    new_field: str = ""

    # 修改字段类型
    priority: float = 2.0  # 改为浮点数
```

### 方式2: 修改MD文档（推荐用于文档更新）
更新本文档，然后根据文档内容更新Python代码。

### 方式3: 扩展预定义场景
在 `MVPScenarios` 类中添加新场景：

```python
@staticmethod
def get_new_scenario() -> Dict[str, Any]:
    """场景4: 新场景"""
    return {
        "name": "new_scenario",
        "description": "新场景描述",
        "tool_request": {...},
        "test_data": [...]
    }
```

---

## 最佳实践

### 1. 变量命名
- 使用清晰的英文命名
- ID字段统一使用 `_id` 后缀
- 时间字段使用 `_time` 或 `_at` 后缀

### 2. 数据验证
- 所有必需字段都要填写
- 使用枚举类型限制固定选项
- 期望输出字段用于自动验证

### 3. 实验记录
- 每次实验创建唯一的 `run_id`
- 及时更新实验阶段
- 记录详细的指标数据

### 4. 错误处理
- 失败时填写 `error_message`
- 记录 `retry_count`
- 保存完整的执行记录

---

## 变量关系图

```
ExperimentRun (实验运行)
    ├── agents (参与的Agent)
    ├── tool_requests (工具请求列表)
    │   └── ToolCreationRequest
    │       └── CreatedTool (创建的工具)
    ├── tasks (任务列表)
    │   └── TaskData
    │       └── TaskExecution (执行记录)
    │           └── ValidationResult (验证结果)
    └── metrics (性能指标)
```

---

## 总结

这套变量定义系统的特点：

1. **集中管理**: 所有实验变量在一个文件中定义
2. **类型安全**: 使用dataclass和枚举保证类型正确
3. **易于修改**: 修改变量只需编辑一处
4. **完整追溯**: 通过ID关联所有相关数据
5. **预定义场景**: 提供开箱即用的测试场景

这些变量独立于系统交互配置，专门用于实验数据管理，使得MVP实验可以快速启动和验证。
