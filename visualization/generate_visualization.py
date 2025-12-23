#!/usr/bin/env python3
"""
生成项目可视化
运行此脚本生成完整的项目可视化网页
"""

import sys
import os
from pathlib import Path
import shutil
import webbrowser

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from visualization.visualizer import VideoQAVisualizer


def main():
    """生成可视化"""
    print("=" * 60)
    print("🎬 视频问答Multi-Agent系统 - 可视化生成器")
    print("=" * 60)
    print()

    # 项目根目录
    project_root_path = Path(__file__).parent.parent
    print(f"📂 项目根目录: {project_root_path}")

    # 输出目录
    output_dir = project_root_path / "visualization" / "output"
    data_dir = output_dir / "data"

    # 清理旧数据
    if output_dir.exists():
        print("🗑️  清理旧的可视化数据...")
        shutil.rmtree(output_dir)

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 输出目录: {output_dir}")
    print()

    # 创建可视化器
    print("🔨 创建视频问答系统可视化器...")
    visualizer = VideoQAVisualizer(str(project_root_path))

    # 导出所有数据
    print("💾 导出可视化数据...")
    print("-" * 60)
    visualizer.export_all(data_dir)
    print("-" * 60)
    print()

    # 复制HTML模板
    print("📄 复制HTML模板...")
    template_path = project_root_path / "visualization" / "template.html"
    output_html = output_dir / "index.html"

    if template_path.exists():
        shutil.copy(template_path, output_html)
        print(f"✅ HTML文件已生成: {output_html}")
    else:
        print(f"⚠️  警告: 模板文件不存在: {template_path}")
        print("    请先创建template.html文件")
    print()

    # 完成
    print("=" * 60)
    print("✨ 可视化生成完成！")
    print("=" * 60)
    print()
    print(f"📍 可视化文件位置:")
    print(f"   - HTML: {output_html}")
    print(f"   - 数据: {data_dir}")
    print()
    print("🌐 打开方式:")
    print(f"   - 在浏览器中打开: file://{output_html}")
    print(f"   - 或运行: python -m http.server -d {output_dir} 8000")
    print()

    # 询问是否自动打开（仅在交互模式下）
    if sys.stdin.isatty():
        try:
            response = input("是否现在在浏览器中打开？(y/n): ").lower().strip()
            if response == 'y' and output_html.exists():
                print("🚀 正在打开浏览器...")
                webbrowser.open(f"file://{output_html}")
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 已取消")
    else:
        print("💡 提示: 运行完成，可以手动打开HTML文件查看可视化")


if __name__ == "__main__":
    main()
