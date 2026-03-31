#!/usr/bin/env python3
"""
依赖图生成器

功能：生成依赖关系图
用途：可视化模块依赖关系，支持 Mermaid 和 Graphviz 格式

使用方式：
    python graph_generator.py --dependency-data dependencies.json --format mermaid --output graph.md

参数说明：
    --dependency-data: 依赖关系数据文件（必需）
    --format: 输出格式（mermaid/graphviz，默认：mermaid）
    --output: 输出文件路径（可选）
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any


def generate_mermaid_graph(dependencies: Dict[str, List[str]], title: str = "依赖关系图") -> str:
    """
    生成 Mermaid 格式的依赖图
    
    Args:
        dependencies: 依赖关系字典
        title: 图表标题
    
    Returns:
        Mermaid 格式的图表
    """
    lines = [
        f"# {title}",
        "",
        "```mermaid",
        "graph TD"
    ]
    
    # 添加节点和边
    added_edges = set()
    
    for module, deps in dependencies.items():
        # 简化模块名（只取最后一部分）
        module_short = module.split('.')[-1]
        
        for dep in deps:
            dep_short = dep.split('.')[-1]
            edge = f"{module_short} --> {dep_short}"
            
            if edge not in added_edges:
                lines.append(f"    {module_short} --> {dep_short}")
                added_edges.add(edge)
    
    lines.append("```")
    
    return "\n".join(lines)


def generate_graphviz_graph(dependencies: Dict[str, List[str]], title: str = "依赖关系图") -> str:
    """
    生成 Graphviz 格式的依赖图
    
    Args:
        dependencies: 依赖关系字典
        title: 图表标题
    
    Returns:
        Graphviz 格式的图表
    """
    lines = [
        f'digraph "{title}" {{',
        '    rankdir=TB;',
        '    node [shape=box, style=filled, color=lightblue];',
        '    edge [color=gray];',
        ''
    ]
    
    # 添加节点和边
    added_edges = set()
    nodes = set()
    
    for module, deps in dependencies.items():
        module_short = module.split('.')[-1]
        nodes.add(module_short)
        
        for dep in deps:
            dep_short = dep.split('.')[-1]
            nodes.add(dep_short)
            edge = f'    "{module_short}" -> "{dep_short}";'
            
            if edge not in added_edges:
                lines.append(edge)
                added_edges.add(edge)
    
    # 添加节点定义
    node_lines = []
    for node in sorted(nodes):
        node_lines.append(f'    "{node}" [label="{node}"];')
    
    lines = [lines[0]] + lines[1:3] + node_lines + lines[3:]
    lines.append('}')
    
    return "\n".join(lines)


def generate_dependency_matrix(dependencies: Dict[str, List[str]]) -> str:
    """
    生成依赖矩阵（文本格式）
    
    Args:
        dependencies: 依赖关系字典
    
    Returns:
        依赖矩阵表格
    """
    # 收集所有模块
    all_modules = set(dependencies.keys())
    for deps in dependencies.values():
        all_modules.update(deps)
    
    all_modules = sorted(list(all_modules))
    
    # 构建矩阵
    lines = ["# 依赖矩阵", ""]
    lines.append("| 模块 | 依赖数 | 依赖项 |")
    lines.append("|------|--------|--------|")
    
    for module in all_modules:
        deps = dependencies.get(module, [])
        deps_str = ", ".join(deps) if deps else "-"
        lines.append(f"| {module} | {len(deps)} | {deps_str} |")
    
    return "\n".join(lines)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="依赖图生成器")
    parser.add_argument("--dependency-data", required=True, help="依赖关系数据文件")
    parser.add_argument("--format", choices=["mermaid", "graphviz", "matrix"], default="mermaid",
                       help="输出格式（默认：mermaid）")
    parser.add_argument("--output", help="输出文件路径（可选）")
    parser.add_argument("--title", default="依赖关系图", help="图表标题")
    
    args = parser.parse_args()
    
    # 读取依赖数据
    data_file = Path(args.dependency_data)
    if not data_file.exists():
        print(f"错误: 文件不存在: {args.dependency_data}", file=sys.stderr)
        sys.exit(1)
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    dependencies = data.get("dependencies", {})
    
    # 生成图表
    if args.format == "mermaid":
        graph = generate_mermaid_graph(dependencies, args.title)
    elif args.format == "graphviz":
        graph = generate_graphviz_graph(dependencies, args.title)
    elif args.format == "matrix":
        graph = generate_dependency_matrix(dependencies)
    
    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(graph)
        print(f"图表已保存到: {args.output}")
    else:
        print(graph)


if __name__ == "__main__":
    main()
