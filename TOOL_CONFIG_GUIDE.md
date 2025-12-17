# 工具配置系统使用说明

## 概述

这是一个灵活、易维护的工具配置管理系统，专为多智能体项目设计。该系统允许你轻松地定义、注册、查询、修改和删除工具配置。

## 目录结构

```
multi_agent/
├── config/                      # 配置模块
│   ├── __init__.py             # 模块入口
│   └── tool_config.py          # 工具配置定义
├── examples/                    # 示例代码
│   └── tool_config_example.py  # 工具配置使用示例
└── tests/                       # 测试代码
    └── test_tool_config.py     # 配置系统测试
```

## 核心组件

### 1. 枚举类型

- **ToolCategory**: 工具分类（文件操作、数据处理、API调用等）
- **ParameterType**: 参数类型（字符串、整数、浮点数、布尔值等）
- **ToolStatus**: 工具状态（活跃、未激活、已废弃、测试中）

### 2. 配置类

#### ToolParameter - 工具参数定义
定义工具函数的输入参数，包括：
- 名称、类型、描述
- 是否必需、默认值
- 验证规则（枚举值、范围、长度、正则表达式）

#### ToolExecutionConfig - 执行配置
控制工具的执行行为：
- 超时时间
- 重试次数和延迟
- 缓存策略
- 异步执行
- 用户确认
- 日志记录

#### ToolConfig - 完整工具配置
定义工具的所有属性：
- 基本信息（名称、描述、分类、版本）
- 参数定义
- 返回值定义
- 执行配置
- 权限和安全设置
- 元数据（标签、作者、时间、示例）
- 依赖和限制

### 3. 注册表管理

**ToolRegistry** 提供工具的集中管理：
- `register()` - 注册工具
- `unregister()` - 注销工具
- `get()` - 获取工具
- `list_all()` - 列出所有工具
- `list_by_category()` - 按分类列出
- `list_by_tag()` - 按标签列出
- `search()` - 搜索工具
- `update()` - 更新工具
- `clear()` - 清空注册表

## 快速开始

### 1. 创建一个简单工具

```python
from config import (
    ToolConfig,
    ToolParameter,
    ToolCategory,
    ParameterType,
    register_tool
)

# 创建工具配置
my_tool = ToolConfig(
    name="my_tool",
    display_name="我的工具",
    description="这是一个示例工具",
    category=ToolCategory.CUSTOM,
    parameters=[
        ToolParameter(
            name="input",
            type=ParameterType.STRING,
            description="输入内容",
            required=True
        )
    ]
)

# 注册工具
register_tool(my_tool)
```

### 2. 查询工具

```python
from config import get_tool_config, TOOL_REGISTRY

# 获取特定工具
tool = get_tool_config("my_tool")

# 列出所有工具
all_tools = TOOL_REGISTRY.list_all()

# 按分类查询
file_tools = TOOL_REGISTRY.list_by_category(ToolCategory.FILE_OPERATION)

# 按标签查询
api_tools = TOOL_REGISTRY.list_by_tag("api")

# 搜索工具
results = TOOL_REGISTRY.search("json")
```

### 3. 修改工具

```python
# 更新工具配置
TOOL_REGISTRY.update(
    "my_tool",
    description="更新后的描述",
    tags=["新标签"]
)
```

### 4. 删除工具

```python
# 删除工具
TOOL_REGISTRY.unregister("my_tool")
```

## 高级特性

### 参数验证

```python
param = ToolParameter(
    name="age",
    type=ParameterType.INTEGER,
    description="年龄",
    min_value=0,
    max_value=150
)

# 验证参数值
is_valid = param.validate(25)  # True
is_valid = param.validate(-5)  # False
```

### 执行配置

```python
from config import ToolExecutionConfig, ToolDefaults

execution_config = ToolExecutionConfig(
    timeout=60,
    max_retries=3,
    retry_delay=2.0,
    enable_cache=True,
    cache_ttl=ToolDefaults.MEDIUM_CACHE_TTL,
    async_execution=True
)
```

### 权限控制

```python
tool = ToolConfig(
    name="admin_tool",
    display_name="管理员工具",
    description="仅管理员可用",
    category=ToolCategory.CUSTOM,
    requires_auth=True,
    permission_level=ToolDefaults.ADMIN,
    allowed_users=["admin1", "admin2"]
)
```

### 导出配置

```python
tool = get_tool_config("my_tool")
config_dict = tool.to_dict()  # 转换为字典格式
```

## 设计优势

1. **类型安全**: 使用dataclass和枚举，提供完整的类型提示
2. **易于扩展**: 添加新字段只需修改配置类
3. **集中管理**: 全局注册表统一管理所有工具
4. **参数验证**: 内置参数验证机制，确保数据正确性
5. **灵活查询**: 支持多种查询方式（名称、分类、标签、关键词）
6. **默认值**: 所有配置都有合理的默认值
7. **文档化**: 每个配置项都有详细说明

## 运行示例和测试

```bash
# 运行示例
python examples/tool_config_example.py

# 运行测试
python tests/test_tool_config.py
```

## 增删改操作示例

### 增加新工具

```python
new_tool = ToolConfig(
    name="new_tool",
    display_name="新工具",
    description="这是新增的工具",
    category=ToolCategory.CUSTOM
)
register_tool(new_tool)
```

### 修改工具配置

```python
TOOL_REGISTRY.update(
    "new_tool",
    description="修改后的描述",
    status=ToolStatus.BETA
)
```

### 删除工具

```python
TOOL_REGISTRY.unregister("new_tool")
```

## 常见问题

**Q: 如何添加自定义的工具分类？**
A: 在`ToolCategory`枚举中添加新的类别即可。

**Q: 如何验证参数是否符合要求？**
A: 使用`ToolParameter.validate(value)`方法进行验证。

**Q: 是否支持异步执行？**
A: 是的，在`ToolExecutionConfig`中设置`async_execution=True`。

**Q: 如何实现工具的实际功能？**
A: 可以在`ToolConfig`的`implementation`字段传入实现函数。

## 下一步

1. 定义你的项目所需的具体工具
2. 根据需求调整执行配置
3. 实现工具的具体功能
4. 在多智能体系统中集成这些工具

## 贡献

欢迎提出改进建议和bug报告！
