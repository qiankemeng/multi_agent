# 项目可视化系统

## 📖 简介

这是一个为 Multi-Agent 长视频理解系统设计的**动态可视化工具**。它能够自动分析项目代码结构，生成交互式可视化界面，帮助开发者直观地理解项目架构、类关系和数据流。

## ✨ 特性

### 🎯 核心功能

1. **项目结构分析**
   - 自动解析所有Python文件
   - 提取类、函数、模块信息
   - 分析导入导出关系
   - 统计代码行数

2. **类关系图谱**
   - 交互式力导向图
   - 展示类之间的继承关系
   - 区分Dataclass、Enum和普通类
   - 支持缩放、拖拽、搜索

3. **视频工作流可视化**
   - 展示长视频理解的完整流程
   - 从视频输入到最终理解的6个阶段
   - 展示每个阶段的核心类和操作

4. **模块详情浏览**
   - 列出所有模块及其统计信息
   - 支持实时搜索和过滤
   - 显示类、函数、导入导出数量

5. **交互式HTML界面**
   - 现代化UI设计
   - 响应式布局
   - 多标签页切换
   - 实时搜索过滤

## 🚀 快速开始

### 1. 生成可视化

```bash
# 进入项目根目录
cd /path/to/multi_agent

# 运行可视化生成脚本
python visualization/generate_visualization.py
```

### 2. 查看结果

生成完成后，有两种查看方式：

**方式1: 直接打开HTML文件**
```bash
# 在浏览器中打开
open visualization/output/index.html  # macOS
# 或
xdg-open visualization/output/index.html  # Linux
# 或直接双击 index.html 文件
```

**方式2: 启动本地服务器**
```bash
# 使用Python内置服务器
python -m http.server -d visualization/output 8000

# 然后在浏览器访问
# http://localhost:8000
```

## 📁 文件结构

```
visualization/
├── visualizer.py              # 核心可视化器类
├── generate_visualization.py  # 生成脚本
├── template.html             # HTML模板
├── README.md                 # 本文档
├── USAGE.md                  # 详细使用说明
└── output/                   # 生成的输出（自动创建）
    ├── index.html           # 可视化主页面
    ├── REPORT.md            # 统计报告
    └── data/                # JSON数据文件
        ├── modules.json     # 模块数据
        ├── classes.json     # 类数据
        ├── functions.json   # 函数数据
        ├── relationships.json  # 关系数据
        ├── data_flow.json   # 数据流图数据
        ├── video_workflow.json  # 视频工作流数据
        ├── file_tree.json   # 文件树数据
        └── stats.json       # 统计信息
```

## 🎨 可视化界面

### 1. 项目概览
- 显示项目整体统计
- 模块列表及基本信息
- 代码行数、类数、函数数

### 2. 模块详情
- 所有模块的详细信息
- 包含docstring、导入导出
- 支持搜索过滤

### 3. 类结构浏览
- 所有类的详细信息
- 属性、方法列表
- 文件位置和行号
- 区分Dataclass、Enum、Class

### 4. 关系图谱
- 交互式力导向图
- 展示类之间的继承关系
- 可以拖拽节点
- 鼠标悬停显示详情

### 5. 视频工作流
- 长视频理解的6个处理阶段
- 每个阶段的核心类和操作
- 清晰的数据流向

### 6. 文件树
- 项目文件结构
- 显示行数信息
- 文件夹层级展示

## 🔧 自定义扩展

### 添加新的可视化类型

在 `visualizer.py` 中添加新方法：

```python
def get_custom_data(self) -> Dict[str, Any]:
    """自定义数据提取"""
    # 你的逻辑
    return custom_data
```

在 `generate_visualization.py` 中导出：

```python
# 导出自定义数据
with open(output_path / 'custom.json', 'w', encoding='utf-8') as f:
    json.dump(visualizer.get_custom_data(), f, indent=2)
```

在 `template.html` 中添加显示逻辑。

### 修改样式

编辑 `template.html` 中的 `<style>` 部分，或添加外部CSS文件。

## 📊 统计报告

生成过程会自动创建 `REPORT.md` 统计报告，包含：

- 整体统计数据
- 模块详情表格
- 核心类统计
- 关系统计
- 架构亮点分析
- 后续扩展建议

## 🎯 使用场景

1. **项目文档**
   - 自动生成项目架构文档
   - 新成员快速了解项目结构

2. **代码审查**
   - 可视化代码关系
   - 发现设计问题

3. **重构参考**
   - 了解类之间的依赖关系
   - 规划重构方案

4. **教学演示**
   - 向他人展示项目架构
   - 教学材料制作

## 🔍 技术实现

- **后端**: Python 3.x
  - `ast` 模块: 解析Python代码
  - `dataclasses`: 数据结构定义
  - `json`: 数据导出

- **前端**: 纯HTML + CSS + JavaScript
  - **D3.js**: 力导向图绘制
  - 响应式设计
  - 现代化UI

## 📝 注意事项

1. **文件编码**: 确保所有Python文件使用UTF-8编码
2. **依赖**: 不需要额外安装依赖（除了Python标准库）
3. **浏览器**: 推荐使用Chrome、Firefox、Edge等现代浏览器
4. **性能**: 大型项目（1000+类）可能加载较慢

## 🐛 问题排查

### 生成失败
```bash
# 检查Python版本（需要3.7+）
python --version

# 检查文件权限
ls -l visualization/
```

### 浏览器打不开
```bash
# 使用本地服务器
python -m http.server -d visualization/output 8000
```

### 关系图显示异常
- 尝试点击"重置视图"按钮
- 刷新页面
- 检查浏览器控制台错误

## 🤝 贡献

欢迎提交问题和改进建议！

## 📄 许可

与主项目相同。

## 🔗 相关文档

- [项目主文档](../readme.md)
- [详细使用说明](./USAGE.md)
- [交互配置指南](../INTERACTION_CONFIG_GUIDE.md)
- [视频变量文档](../VIDEO_VARIABLES.md)

---

**Happy Visualizing! 🎉**
