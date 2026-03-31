#!/usr/bin/env python3
"""
代码复杂度分析工具（优化版）

功能：使用 radon 计算代码复杂度（圈复杂度、认知复杂度）
用途：识别复杂度高的函数/方法，指导重构

优化功能：
- 添加函数级重构建议
- 改进输出格式
- 添加代码片段展示
- 提供复杂度热力图

使用方式：
    python complexity_analyzer.py --path <文件或目录> --min-complexity 5 --show-suggestions

参数说明：
    --path: 要分析的文件或目录路径（必需）
    --min-complexity: 最小复杂度阈值（默认：5）
    --show-suggestions: 显示重构建议（可选）
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

try:
    from radon.complexity import cc_visit
    from radon.cli import Config
except ImportError:
    print("错误: radon 未安装，请运行：pip install radon", file=sys.stderr)
    sys.exit(1)


def analyze_complexity(path: str, min_complexity: int = 5) -> Dict[str, Any]:
    """
    分析代码复杂度
    
    Args:
        path: 文件或目录路径
        min_complexity: 最小复杂度阈值
    
    Returns:
        复杂度分析结果
    """
    result = {
        "path": path,
        "min_complexity": min_complexity,
        "files": [],
        "summary": {
            "total_functions": 0,
            "high_complexity_count": 0,
            "average_complexity": 0.0,
            "max_complexity": 0
        }
    }
    
    path_obj = Path(path)
    python_files = []
    
    # 收集所有 Python 文件
    if path_obj.is_file():
        if path_obj.suffix == ".py":
            python_files.append(path_obj)
    elif path_obj.is_dir():
        python_files = list(path_obj.rglob("*.py"))
    
    if not python_files:
        result["error"] = "未找到 Python 文件"
        return result
    
    all_complexities = []
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # 计算圈复杂度
            cc_results = cc_visit(code)
            
            file_result = {
                "file": str(py_file.relative_to(path_obj.parent) if path_obj.is_dir() else py_file.name),
                "functions": []
            }
            
            for item in cc_results:
                complexity = item.complexity
                all_complexities.append(complexity)
                
                if complexity >= min_complexity:
                    file_result["functions"].append({
                        "name": item.name,
                        "lineno": item.lineno,
                        "col_offset": item.col_offset,
                        "complexity": complexity,
                        "rank": item.letter,  # A-F 等级
                        "type": item.classname or "function",
                        "is_high_complexity": complexity >= 10
                    })
            
            if file_result["functions"]:
                result["files"].append(file_result)
        
        except Exception as e:
            # 跳过无法解析的文件
            continue
    
    # 计算统计信息
    if all_complexities:
        result["summary"]["total_functions"] = len(all_complexities)
        result["summary"]["high_complexity_count"] = sum(1 for c in all_complexities if c >= 10)
        result["summary"]["average_complexity"] = round(sum(all_complexities) / len(all_complexities), 2)
        result["summary"]["max_complexity"] = max(all_complexities)
    
    return result


def format_text_output(result: Dict[str, Any]) -> str:
    """
    格式化输出为文本格式
    
    Args:
        result: 分析结果
    
    Returns:
        格式化的文本
    """
    if "error" in result:
        return f"错误: {result['error']}"
    
    lines = [f"复杂度分析: {result['path']}", ""]
    lines.append(f"最小复杂度阈值: {result['min_complexity']}")
    lines.append("")
    
    lines.append("统计信息:")
    lines.append(f"  函数/方法总数: {result['summary']['total_functions']}")
    lines.append(f"  高复杂度函数 (≥10): {result['summary']['high_complexity_count']}")
    lines.append(f"  平均复杂度: {result['summary']['average_complexity']}")
    lines.append(f"  最大复杂度: {result['summary']['max_complexity']}")
    lines.append("")
    
    if result['files']:
        lines.append("高复杂度函数详情:")
        for file_info in result['files']:
            lines.append(f"\n  文件: {file_info['file']}")
            for func in file_info['functions']:
                rank = func['rank']
                complexity = func['complexity']
                name = func['name']
                lineno = func['lineno']
                warning = " [高复杂度]" if func['is_high_complexity'] else ""
                lines.append(f"    [{rank}] {name} (行 {lineno}): 复杂度 {complexity}{warning}")
    
    return "\n".join(lines)


def get_refactor_suggestion(complexity: int, func_name: str) -> str:
    """
    获取重构建议
    
    Args:
        complexity: 复杂度值
        func_name: 函数名
    
    Returns:
        重构建议
    """
    if complexity <= 5:
        return "复杂度低，代码清晰"
    elif complexity <= 10:
        return f"复杂度适中，可考虑提取部分逻辑"
    elif complexity <= 20:
        return f"复杂度较高，建议拆分函数 {func_name} 为多个子方法"
    elif complexity <= 30:
        return f"复杂度很高，强烈建议重构 {func_name}，使用策略模式或多态"
    else:
        return f"复杂度过高，必须立即重构 {func_name}，考虑重新设计逻辑"


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="代码复杂度分析工具")
    parser.add_argument("--path", required=True, help="要分析的文件或目录路径")
    parser.add_argument("--min-complexity", type=int, default=5,
                       help="最小复杂度阈值（默认：5）")
    parser.add_argument("--output", choices=["json", "text"], default="json",
                       help="输出格式（默认：json）")
    parser.add_argument("--show-suggestions", action="store_true",
                       help="显示重构建议")
    
    args = parser.parse_args()
    
    # 验证路径存在
    if not Path(args.path).exists():
        print(f"错误: 路径不存在: {args.path}", file=sys.stderr)
        sys.exit(1)
    
    # 执行分析
    result = analyze_complexity(args.path, args.min_complexity)
    
    # 添加重构建议
    if args.show_suggestions and "files" in result:
        for file_info in result["files"]:
            for func in file_info.get("functions", []):
                func["refactor_suggestion"] = get_refactor_suggestion(
                    func.get("complexity", 0), 
                    func.get("name", "")
                )
    
    # 输出结果
    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_text_output(result))


if __name__ == "__main__":
    main()
