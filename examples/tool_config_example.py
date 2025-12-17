"""
工具配置示例
演示如何使用config模块定义和管理工具

这个文件展示了：
1. 如何创建新工具
2. 如何注册工具到全局注册表
3. 如何查询和修改工具
4. 如何删除工具
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import (
    ToolConfig,
    ToolParameter,
    ToolCategory,
    ToolExecutionConfig,
    ParameterType,
    ToolStatus,
    TOOL_REGISTRY,
    register_tool,
    get_tool_config,
    list_all_tools,
    ToolDefaults
)


# ==================== 示例1: 创建一个简单的文件读取工具 ====================

def create_file_reader_tool():
    """创建文件读取工具"""
    file_reader = ToolConfig(
        name="file_reader",
        display_name="文件读取器",
        description="读取指定路径的文件内容",
        category=ToolCategory.FILE_OPERATION,
        version="1.0.0",

        # 定义参数
        parameters=[
            ToolParameter(
                name="file_path",
                type=ParameterType.STRING,
                description="要读取的文件路径",
                required=True
            ),
            ToolParameter(
                name="encoding",
                type=ParameterType.STRING,
                description="文件编码",
                required=False,
                default="utf-8",
                enum=["utf-8", "gbk", "ascii"]
            ),
            ToolParameter(
                name="max_lines",
                type=ParameterType.INTEGER,
                description="最大读取行数",
                required=False,
                default=None,
                min_value=1
            )
        ],

        # 返回值定义
        return_type=ParameterType.STRING,
        return_description="文件内容",

        # 执行配置
        execution_config=ToolExecutionConfig(
            timeout=10,
            max_retries=2,
            enable_cache=True,
            cache_ttl=ToolDefaults.SHORT_CACHE_TTL
        ),

        # 元数据
        tags=["file", "io", "read"],
        status=ToolStatus.ACTIVE,

        # 使用示例
        examples=[
            {
                "description": "读取文本文件",
                "input": {"file_path": "/path/to/file.txt"},
                "output": "文件内容..."
            },
            {
                "description": "读取前100行",
                "input": {"file_path": "/path/to/file.txt", "max_lines": 100},
                "output": "前100行内容..."
            }
        ]
    )

    # 注册工具
    register_tool(file_reader)
    return file_reader


# ==================== 示例2: 创建一个API调用工具 ====================

def create_api_caller_tool():
    """创建API调用工具"""
    api_caller = ToolConfig(
        name="http_request",
        display_name="HTTP请求器",
        description="发送HTTP请求到指定URL",
        category=ToolCategory.API_CALL,
        version="1.0.0",

        parameters=[
            ToolParameter(
                name="url",
                type=ParameterType.STRING,
                description="请求的URL",
                required=True,
                pattern=r"^https?://.+"
            ),
            ToolParameter(
                name="method",
                type=ParameterType.STRING,
                description="HTTP方法",
                required=False,
                default="GET",
                enum=["GET", "POST", "PUT", "DELETE", "PATCH"]
            ),
            ToolParameter(
                name="headers",
                type=ParameterType.OBJECT,
                description="请求头",
                required=False,
                default={}
            ),
            ToolParameter(
                name="body",
                type=ParameterType.OBJECT,
                description="请求体",
                required=False
            ),
            ToolParameter(
                name="timeout",
                type=ParameterType.INTEGER,
                description="超时时间（秒）",
                required=False,
                default=30,
                min_value=1,
                max_value=300
            )
        ],

        return_type=ParameterType.OBJECT,
        return_description="API响应对象",

        execution_config=ToolExecutionConfig(
            timeout=60,
            max_retries=3,
            retry_delay=2.0,
            enable_cache=False,
            async_execution=True
        ),

        tags=["api", "http", "network"],
        status=ToolStatus.ACTIVE,
        requires_auth=False,
        rate_limit=60  # 每分钟最多60次
    )

    register_tool(api_caller)
    return api_caller


# ==================== 示例3: 创建一个数据处理工具 ====================

def create_json_parser_tool():
    """创建JSON解析工具"""
    json_parser = ToolConfig(
        name="json_parser",
        display_name="JSON解析器",
        description="解析JSON字符串并提取指定字段",
        category=ToolCategory.DATA_PROCESSING,

        parameters=[
            ToolParameter(
                name="json_string",
                type=ParameterType.STRING,
                description="JSON格式的字符串",
                required=True
            ),
            ToolParameter(
                name="key_path",
                type=ParameterType.STRING,
                description="要提取的字段路径，如'data.user.name'",
                required=False
            ),
            ToolParameter(
                name="strict_mode",
                type=ParameterType.BOOLEAN,
                description="是否使用严格模式解析",
                required=False,
                default=True
            )
        ],

        return_type=ParameterType.ANY,
        return_description="解析后的数据或提取的字段值",

        execution_config=ToolExecutionConfig(
            timeout=ToolDefaults.QUICK_TIMEOUT,
            enable_cache=True,
            cache_ttl=ToolDefaults.MEDIUM_CACHE_TTL
        ),

        tags=["json", "parse", "data"],
        status=ToolStatus.ACTIVE
    )

    register_tool(json_parser)
    return json_parser


# ==================== 示例4: 创建一个计算工具 ====================

def create_calculator_tool():
    """创建计算器工具"""
    calculator = ToolConfig(
        name="calculator",
        display_name="数学计算器",
        description="执行数学表达式计算",
        category=ToolCategory.CALCULATION,

        parameters=[
            ToolParameter(
                name="expression",
                type=ParameterType.STRING,
                description="数学表达式，如'2 + 3 * 4'",
                required=True
            ),
            ToolParameter(
                name="precision",
                type=ParameterType.INTEGER,
                description="小数精度",
                required=False,
                default=2,
                min_value=0,
                max_value=10
            )
        ],

        return_type=ParameterType.FLOAT,
        return_description="计算结果",

        execution_config=ToolExecutionConfig(
            timeout=5,
            max_retries=0,
            enable_cache=True,
            log_execution=False
        ),

        tags=["math", "calculation"],
        status=ToolStatus.ACTIVE,
        permission_level=ToolDefaults.PUBLIC
    )

    register_tool(calculator)
    return calculator


# ==================== 管理工具的示例函数 ====================

def demo_tool_management():
    """演示如何管理工具"""

    print("=" * 60)
    print("工具管理示例")
    print("=" * 60)

    # 1. 创建并注册工具
    print("\n1. 创建并注册工具...")
    create_file_reader_tool()
    create_api_caller_tool()
    create_json_parser_tool()
    create_calculator_tool()

    # 2. 列出所有工具
    print(f"\n2. 当前注册的工具数量: {TOOL_REGISTRY.count()}")
    all_tools = list_all_tools()
    for tool in all_tools:
        print(f"   - {tool.name}: {tool.description}")

    # 3. 按类别查询工具
    print("\n3. 查询文件操作类工具:")
    file_tools = TOOL_REGISTRY.list_by_category(ToolCategory.FILE_OPERATION)
    for tool in file_tools:
        print(f"   - {tool.name}")

    # 4. 按标签查询工具
    print("\n4. 查询带有'api'标签的工具:")
    api_tools = TOOL_REGISTRY.list_by_tag("api")
    for tool in api_tools:
        print(f"   - {tool.name}")

    # 5. 搜索工具
    print("\n5. 搜索包含'json'关键词的工具:")
    search_results = TOOL_REGISTRY.search("json")
    for tool in search_results:
        print(f"   - {tool.name}: {tool.description}")

    # 6. 获取特定工具的配置
    print("\n6. 获取file_reader工具的详细配置:")
    file_reader = get_tool_config("file_reader")
    if file_reader:
        print(f"   名称: {file_reader.display_name}")
        print(f"   描述: {file_reader.description}")
        print(f"   参数数量: {len(file_reader.parameters)}")
        print(f"   参数列表:")
        for param in file_reader.parameters:
            required_str = "必需" if param.required else "可选"
            print(f"      - {param.name} ({param.type.value}): {param.description} [{required_str}]")

    # 7. 修改工具配置
    print("\n7. 修改calculator工具的描述...")
    success = TOOL_REGISTRY.update(
        "calculator",
        description="高级数学计算器，支持复杂表达式"
    )
    if success:
        updated_tool = get_tool_config("calculator")
        print(f"   更新后的描述: {updated_tool.description}")

    # 8. 将工具配置导出为字典
    print("\n8. 导出json_parser工具配置为字典:")
    json_parser = get_tool_config("json_parser")
    if json_parser:
        config_dict = json_parser.to_dict()
        print(f"   {config_dict}")

    # 9. 删除工具
    print("\n9. 删除calculator工具...")
    TOOL_REGISTRY.unregister("calculator")
    print(f"   删除后的工具数量: {TOOL_REGISTRY.count()}")

    print("\n" + "=" * 60)


# ==================== 如何快速添加新工具 ====================

def quick_add_tool_example():
    """演示如何快速添加一个新工具"""

    # 方式1: 完整定义（推荐用于复杂工具）
    new_tool = ToolConfig(
        name="my_new_tool",
        display_name="我的新工具",
        description="这是一个新工具",
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
    register_tool(new_tool)

    # 方式2: 最小化定义（只需提供必需字段，其他使用默认值）
    simple_tool = ToolConfig(
        name="simple_tool",
        display_name="简单工具",
        description="一个简单的工具",
        category=ToolCategory.CUSTOM
    )
    register_tool(simple_tool)


# ==================== 主函数 ====================

if __name__ == "__main__":
    # 运行演示
    demo_tool_management()

    print("\n提示: 你可以轻松地:")
    print("  - 添加工具: 创建ToolConfig对象并调用register_tool()")
    print("  - 删除工具: 调用TOOL_REGISTRY.unregister(tool_name)")
    print("  - 修改工具: 调用TOOL_REGISTRY.update(tool_name, **kwargs)")
    print("  - 查询工具: 使用list_by_category(), list_by_tag(), search()等方法")
