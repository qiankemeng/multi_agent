# 可视化系统使用指南

## 🎯 详细使用说明

本文档提供可视化系统的详细使用方法和高级功能。

## 📖 目录

1. [基础使用](#基础使用)
2. [界面功能详解](#界面功能详解)
3. [数据文件说明](#数据文件说明)
4. [高级用法](#高级用法)
5. [API参考](#api参考)
6. [常见问题](#常见问题)

## 基础使用

### 步骤1: 生成可视化数据

```bash
cd /path/to/multi_agent
python visualization/generate_visualization.py
```

脚本会执行以下操作：

1. ✅ 扫描项目所有Python文件
2. ✅ 解析类、函数、模块
3. ✅ 分析依赖关系
4. ✅ 生成JSON数据文件
5. ✅ 复制HTML模板
6. ✅ 生成统计报告

### 步骤2: 查看可视化

```bash
# 方式1: 直接打开（简单快速）
open visualization/output/index.html

# 方式2: HTTP服务器（推荐，避免CORS问题）
python -m http.server -d visualization/output 8000
# 然后访问 http://localhost:8000
```

## 界面功能详解

### 1. 📊 项目概览

**功能**:
- 显示项目整体统计（模块数、类数、函数数、代码行数）
- 模块卡片列表，每个模块显示：
  - 模块名称
  - 代码行数
  - 类数量
  - 函数数量

**操作**:
- 点击模块卡片可高亮显示
- 自动按模块大小排序

### 2. 📦 模块详情

**功能**:
- 显示所有模块的详细信息
- 包含docstring、导入导出统计
- 实时搜索过滤

**操作**:
- 在搜索框输入关键词过滤模块
- 搜索支持模块名、路径、docstring
- 点击模块卡片展开详情

**搜索示例**:
```
config          # 显示所有config模块
interaction     # 显示interaction相关模块
video           # 显示视频相关模块
```

### 3. 🏗️ 类结构浏览

**功能**:
- 列出所有类及其详细信息
- 显示类型（Dataclass/Enum/Class）
- 列出所有属性和方法
- 显示文件位置和行号

**操作**:
- 搜索框过滤类
- 点击类卡片展开/折叠
- 类型徽章颜色区分：
  - 🔵 蓝色: Dataclass
  - 🟠 橙色: Enum
  - 🟣 紫色: 普通Class

**信息说明**:
```
VideoMeta                    # 类名
Dataclass                    # 类型徽章
视频元数据描述视频的基本信息    # docstring

📋 属性 (10)                 # 属性列表
video_id, file_path, ...

⚡ 方法 (1)                  # 方法列表
to_dict()

📁 experiments/video_variables.py:75  # 文件位置
```

### 4. 🔗 关系图谱

**功能**:
- 交互式力导向图
- 展示类之间的继承关系
- 节点大小反映类的复杂度（属性+方法数量）

**操作**:
- **拖拽节点**: 鼠标拖动节点调整位置
- **缩放**: 鼠标滚轮缩放画布
- **平移**: 拖拽空白区域移动整个图
- **悬停**: 鼠标悬停显示类详情
- **🔄 重置视图**: 重置节点位置
- **🏷️ 切换标签**: 显示/隐藏类名标签

**颜色说明**:
- 🔵 蓝色圆圈: Dataclass
- 🟠 橙色圆圈: Enum
- 🟣 紫色圆圈: Class

**线条说明**:
- 灰色线条: 继承关系（从子类指向父类）

### 5. 🎬 视频工作流

**功能**:
- 展示长视频理解的完整处理流程
- 6个处理阶段的线性展示
- 每个阶段包含：
  - 阶段名称
  - 核心类列表
  - 主要操作列表

**工作流阶段**:

```
1. 视频输入
   类: VideoMeta
   操作: extract_metadata
   ↓
2. 视频分段
   类: Segment, TimeSpan
   操作: segment_video
   ↓
3. 帧提取
   类: Frame
   操作: extract_frames, sample_frames
   ↓
4. MLLM分析
   类: MLLMRequest, MLLMResponse
   操作: call_mllm_api, analyze_frame, analyze_segment
   ↓
5. 生成描述
   类: FrameCaption, SegmentCaption
   操作: generate_frame_caption, generate_segment_caption
   ↓
6. 整合理解
   类: VideoUnderstanding
   操作: merge_captions, generate_summary
```

### 6. 📁 文件树

**功能**:
- 项目文件结构树形展示
- 显示每个文件的代码行数
- 区分文件夹和文件

**图标说明**:
- 📁 文件夹
- 📄 Python文件

## 数据文件说明

所有数据存储在 `visualization/output/data/` 目录：

### modules.json
```json
{
  "config.interaction_config": {
    "name": "config.interaction_config",
    "file_path": "/path/to/file.py",
    "docstring": "...",
    "classes": ["Message", "Context", ...],
    "functions": ["func1", ...],
    "imports": ["typing", "datetime", ...],
    "exports": ["Message", "Context", ...],
    "line_count": 491
  }
}
```

### classes.json
```json
{
  "config.interaction_config.Message": {
    "name": "Message",
    "module": "config.interaction_config",
    "file_path": "/path/to/file.py",
    "line_number": 70,
    "docstring": "...",
    "methods": ["to_dict", ...],
    "attributes": ["message_id", "sender_id", ...],
    "base_classes": [],
    "is_dataclass": true,
    "is_enum": false
  }
}
```

### data_flow.json
```json
{
  "nodes": [
    {
      "id": "config.interaction_config.Message",
      "name": "Message",
      "type": "dataclass",
      "module": "config.interaction_config",
      "group": "config",
      "attributes_count": 15,
      "methods_count": 2
    }
  ],
  "links": [
    {
      "source": "SubClass",
      "target": "BaseClass",
      "type": "inherits"
    }
  ]
}
```

## 高级用法

### 1. 仅更新特定模块

修改 `generate_visualization.py`:

```python
# 在分析前过滤文件
def should_analyze(file_path):
    return 'config' in str(file_path)  # 只分析config目录

# 在 _analyze_file 中添加过滤
if not should_analyze(file_path):
    return
```

### 2. 添加自定义统计

在 `visualizer.py` 中添加方法：

```python
def get_custom_stats(self) -> Dict[str, Any]:
    """自定义统计"""
    return {
        'dataclass_count': sum(1 for c in self.classes.values() if c.is_dataclass),
        'enum_count': sum(1 for c in self.classes.values() if c.is_enum),
        'avg_methods': sum(len(c.methods) for c in self.classes.values()) / len(self.classes)
    }
```

### 3. 导出为其他格式

```python
# 导出为CSV
import csv

def export_to_csv(visualizer, output_path):
    with open(output_path / 'classes.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Module', 'Type', 'Attributes', 'Methods'])
        for cls in visualizer.classes.values():
            writer.writerow([
                cls.name,
                cls.module,
                'Dataclass' if cls.is_dataclass else 'Class',
                len(cls.attributes),
                len(cls.methods)
            ])
```

### 4. 程序化访问数据

```python
from visualization.visualizer import ProjectVisualizer

# 创建可视化器
visualizer = ProjectVisualizer('/path/to/project')
visualizer.analyze_project()

# 访问数据
for class_name, class_node in visualizer.classes.items():
    if class_node.is_dataclass:
        print(f"Dataclass: {class_name}")
        print(f"  Attributes: {', '.join(class_node.attributes)}")

# 获取统计
stats = visualizer.get_module_stats()
print(f"Total classes: {stats['total_classes']}")
```

## API参考

### ProjectVisualizer

**主要方法**:

```python
class ProjectVisualizer:
    def __init__(self, project_root: str):
        """初始化可视化器"""

    def analyze_project(self) -> None:
        """分析整个项目"""

    def get_class_hierarchy(self) -> Dict[str, Any]:
        """获取类层次结构"""

    def get_data_flow_graph(self) -> Dict[str, Any]:
        """获取数据流图"""

    def get_module_stats(self) -> Dict[str, Any]:
        """获取模块统计信息"""

    def get_video_workflow_data(self) -> Dict[str, Any]:
        """获取视频工作流数据"""

    def export_to_json(self, output_dir: str) -> None:
        """导出所有数据为JSON"""
```

**数据结构**:

```python
@dataclass
class ClassNode:
    name: str
    module: str
    file_path: str
    line_number: int
    docstring: str
    methods: List[str]
    attributes: List[str]
    base_classes: List[str]
    is_dataclass: bool
    is_enum: bool

@dataclass
class ModuleNode:
    name: str
    file_path: str
    docstring: str
    classes: List[str]
    functions: List[str]
    imports: List[str]
    exports: List[str]
    line_count: int
```

## 常见问题

### Q1: 为什么某些类没有显示？

**A**: 可能原因：
1. 文件解析失败（检查语法错误）
2. 在跳过目录中（如`__pycache__`）
3. 不是`.py`文件

**解决**:
```bash
# 查看生成日志
python visualization/generate_visualization.py 2>&1 | grep "解析文件失败"
```

### Q2: 关系图太密集怎么办？

**A**:
1. 使用鼠标滚轮缩放
2. 点击"切换标签"隐藏类名
3. 拖拽节点调整布局
4. 点击"重置视图"重新布局

### Q3: 如何只显示特定模块？

**A**: 在对应标签页使用搜索框过滤。

### Q4: 可视化数据如何更新？

**A**: 重新运行生成脚本：
```bash
python visualization/generate_visualization.py
```

### Q5: 能否在CI/CD中使用？

**A**: 可以！示例GitHub Actions:
```yaml
- name: Generate Visualization
  run: python visualization/generate_visualization.py

- name: Upload Visualization
  uses: actions/upload-artifact@v2
  with:
    name: visualization
    path: visualization/output/
```

### Q6: 大型项目性能问题？

**A**:
1. 使用HTTP服务器而非直接打开HTML
2. 过滤不需要的文件
3. 减小图谱节点数量

## 💡 最佳实践

1. **定期更新**: 代码变更后重新生成可视化
2. **版本控制**: 将`visualization/output/`添加到`.gitignore`
3. **文档同步**: 可视化作为项目文档的补充
4. **团队分享**: 通过HTTP服务器分享给团队成员
5. **CI集成**: 在CI中自动生成并部署

## 🔗 更多资源

- [主README](./README.md)
- [项目文档](../readme.md)
- [D3.js文档](https://d3js.org/)

---

**有问题？欢迎提Issue！** 🎉
