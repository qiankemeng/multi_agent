"""
工具配置模块
定义所有工具相关的变量、参数和配置

设计原则：
1. 使用dataclass定义配置结构，便于扩展和维护
2. 使用枚举管理固定选项，防止拼写错误
3. 提供注册表机制，方便动态增删改工具
4. 所有配置都有默认值和类型提示
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum


# ==================== 枚举定义 ====================

class ToolCategory(Enum):
    """工具分类"""
    FILE_OPERATION = "file_operation"      # 文件操作类
    DATA_PROCESSING = "data_processing"    # 数据处理类
    API_CALL = "api_call"                  # API调用类
    CALCULATION = "calculation"            # 计算类
    TEXT_PROCESSING = "text_processing"    # 文本处理类
    WEB_SCRAPING = "web_scraping"         # 网页抓取类
    DATABASE = "database"                  # 数据库操作类
    CUSTOM = "custom"                      # 自定义类


class ParameterType(Enum):
    """参数类型"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    ANY = "any"


class ToolStatus(Enum):
    """工具状态"""
    ACTIVE = "active"          # 活跃可用
    INACTIVE = "inactive"      # 未激活
    DEPRECATED = "deprecated"  # 已废弃
    BETA = "beta"             # 测试中


# ==================== 配置类定义 ====================

@dataclass
class ToolParameter:
    """
    工具参数定义
    用于描述工具函数的输入参数
    """
    name: str                              # 参数名称
    type: ParameterType                    # 参数类型
    description: str                       # 参数描述
    required: bool = True                  # 是否必需
    default: Any = None                    # 默认值
    enum: Optional[List[Any]] = None       # 枚举值（如果参数只能是特定值）
    min_value: Optional[float] = None      # 最小值（数值类型）
    max_value: Optional[float] = None      # 最大值（数值类型）
    min_length: Optional[int] = None       # 最小长度（字符串/数组）
    max_length: Optional[int] = None       # 最大长度（字符串/数组）
    pattern: Optional[str] = None          # 正则表达式（字符串类型）

    def validate(self, value: Any) -> bool:
        """验证参数值是否符合定义"""
        # 检查必需参数
        if self.required and value is None:
            return False

        if value is None:
            return True

        # 检查枚举值
        if self.enum and value not in self.enum:
            return False

        # 检查数值范围
        if self.type in [ParameterType.INTEGER, ParameterType.FLOAT]:
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False

        # 检查长度
        if self.type in [ParameterType.STRING, ParameterType.ARRAY]:
            length = len(value)
            if self.min_length is not None and length < self.min_length:
                return False
            if self.max_length is not None and length > self.max_length:
                return False

        return True


@dataclass
class ToolExecutionConfig:
    """
    工具执行配置
    控制工具的执行行为
    """
    timeout: int = 30                      # 执行超时时间（秒）
    max_retries: int = 3                   # 最大重试次数
    retry_delay: float = 1.0               # 重试延迟（秒）
    enable_cache: bool = True              # 是否启用缓存
    cache_ttl: int = 3600                  # 缓存过期时间（秒）
    async_execution: bool = False          # 是否异步执行
    require_confirmation: bool = False     # 是否需要用户确认
    log_execution: bool = True             # 是否记录执行日志


@dataclass
class ToolConfig:
    """
    工具完整配置
    定义一个工具的所有属性和行为
    """
    # 基本信息
    name: str                              # 工具名称（唯一标识）
    display_name: str                      # 显示名称
    description: str                       # 工具描述
    category: ToolCategory                 # 工具分类
    version: str = "1.0.0"                 # 版本号

    # 参数定义
    parameters: List[ToolParameter] = field(default_factory=list)

    # 返回值定义
    return_type: ParameterType = ParameterType.ANY
    return_description: str = ""

    # 执行配置
    execution_config: ToolExecutionConfig = field(default_factory=ToolExecutionConfig)

    # 权限和安全
    requires_auth: bool = False            # 是否需要认证
    permission_level: int = 0              # 权限级别（0-10，越高越严格）
    allowed_users: Optional[List[str]] = None  # 允许使用的用户列表

    # 元数据
    status: ToolStatus = ToolStatus.ACTIVE
    tags: List[str] = field(default_factory=list)  # 标签，便于搜索和分类
    author: str = ""                       # 作者
    created_at: str = ""                   # 创建时间
    updated_at: str = ""                   # 更新时间
    examples: List[Dict[str, Any]] = field(default_factory=list)  # 使用示例

    # 依赖和限制
    dependencies: List[str] = field(default_factory=list)  # 依赖的其他工具
    rate_limit: Optional[int] = None       # 速率限制（每分钟调用次数）

    # 实现相关（可选）
    implementation: Optional[Callable] = None  # 工具的实际实现函数

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "category": self.category.value,
            "version": self.version,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type.value,
                    "description": p.description,
                    "required": p.required,
                    "default": p.default
                } for p in self.parameters
            ],
            "return_type": self.return_type.value,
            "status": self.status.value,
            "tags": self.tags
        }


# ==================== 工具注册表 ====================

class ToolRegistry:
    """
    工具注册表
    用于管理所有工具的注册、查询、删除等操作
    """
    def __init__(self):
        self._tools: Dict[str, ToolConfig] = {}

    def register(self, tool: ToolConfig) -> None:
        """注册一个工具"""
        if tool.name in self._tools:
            print(f"警告: 工具 '{tool.name}' 已存在，将被覆盖")
        self._tools[tool.name] = tool

    def unregister(self, tool_name: str) -> bool:
        """注销一个工具"""
        if tool_name in self._tools:
            del self._tools[tool_name]
            return True
        return False

    def get(self, tool_name: str) -> Optional[ToolConfig]:
        """获取工具配置"""
        return self._tools.get(tool_name)

    def list_all(self) -> List[ToolConfig]:
        """列出所有工具"""
        return list(self._tools.values())

    def list_by_category(self, category: ToolCategory) -> List[ToolConfig]:
        """按分类列出工具"""
        return [tool for tool in self._tools.values() if tool.category == category]

    def list_by_tag(self, tag: str) -> List[ToolConfig]:
        """按标签列出工具"""
        return [tool for tool in self._tools.values() if tag in tool.tags]

    def search(self, keyword: str) -> List[ToolConfig]:
        """搜索工具（根据名称和描述）"""
        keyword = keyword.lower()
        return [
            tool for tool in self._tools.values()
            if keyword in tool.name.lower() or keyword in tool.description.lower()
        ]

    def update(self, tool_name: str, **kwargs) -> bool:
        """更新工具配置"""
        if tool_name not in self._tools:
            return False

        tool = self._tools[tool_name]
        for key, value in kwargs.items():
            if hasattr(tool, key):
                setattr(tool, key, value)
        return True

    def clear(self) -> None:
        """清空所有工具"""
        self._tools.clear()

    def count(self) -> int:
        """返回工具总数"""
        return len(self._tools)


# ==================== 全局注册表实例 ====================

TOOL_REGISTRY = ToolRegistry()


# ==================== 便捷函数 ====================

def register_tool(tool: ToolConfig) -> None:
    """注册工具的便捷函数"""
    TOOL_REGISTRY.register(tool)


def get_tool_config(tool_name: str) -> Optional[ToolConfig]:
    """获取工具配置的便捷函数"""
    return TOOL_REGISTRY.get(tool_name)


def list_all_tools() -> List[ToolConfig]:
    """列出所有工具的便捷函数"""
    return TOOL_REGISTRY.list_all()


# ==================== 常用工具配置常量 ====================

class ToolDefaults:
    """工具默认配置常量"""

    # 超时时间
    DEFAULT_TIMEOUT = 30
    QUICK_TIMEOUT = 5
    LONG_TIMEOUT = 300

    # 重试配置
    DEFAULT_MAX_RETRIES = 3
    NO_RETRY = 0
    AGGRESSIVE_RETRY = 5

    # 缓存配置
    SHORT_CACHE_TTL = 300      # 5分钟
    MEDIUM_CACHE_TTL = 3600    # 1小时
    LONG_CACHE_TTL = 86400     # 1天

    # 权限级别
    PUBLIC = 0                 # 公开
    USER = 3                   # 需要用户认证
    ADMIN = 7                  # 需要管理员权限
    SYSTEM = 10                # 系统级别


# ==================== 导出 ====================

__all__ = [
    'ToolCategory',
    'ParameterType',
    'ToolStatus',
    'ToolParameter',
    'ToolExecutionConfig',
    'ToolConfig',
    'ToolRegistry',
    'TOOL_REGISTRY',
    'register_tool',
    'get_tool_config',
    'list_all_tools',
    'ToolDefaults'
]
