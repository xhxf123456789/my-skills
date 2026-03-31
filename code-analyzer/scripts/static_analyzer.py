#!/usr/bin/env python3
"""
静态代码分析工具

功能：使用 pylint 进行静态代码分析，检测代码质量问题
用途：分析代码规范、潜在错误、代码异味

使用方式：
    python static_analyzer.py --path <文件或目录> --output json

参数说明：
    --path: 要分析的文件或目录路径（必需）
    --output: 输出格式，可选值：json/text（默认：json）
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any


def run_pylint(path: str) -> Dict[str, Any]:
    """
    运行 pylint 进行静态分析
    
    Args:
        path: 文件或目录路径
    
    Returns:
        分析结果字典
    """
    try:
        # 使用 pylint 的 JSON 输出格式
        result = subprocess.run(
            ["pylint", path, "--output-format=json", "--disable=C0114,C0115,C0116"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # pylint 返回码：0=无问题，1=致命错误，2=错误，3=警告，4=重构建议，5=约定，6=信息
        # 我们需要解析输出，无论返回码是什么
        
        if result.stdout:
            try:
                issues = json.loads(result.stdout)
            except json.JSONDecodeError:
                issues = []
        else:
            issues = []
        
        # 统计各类问题数量
        stats = {
            "error": 0,
            "warning": 0,
            "refactor": 0,
            "convention": 0,
            "info": 0
        }
        
        formatted_issues = []
        for issue in issues:
            issue_type = issue.get("type", "unknown")
            if issue_type in stats:
                stats[issue_type] += 1
            
            formatted_issues.append({
                "type": issue_type,
                "module": issue.get("module", ""),
                "line": issue.get("line", 0),
                "column": issue.get("column", 0),
                "message": issue.get("message", ""),
                "symbol": issue.get("symbol", "")
            })
        
        return {
            "path": path,
            "stats": stats,
            "issues": formatted_issues,
            "total_issues": len(formatted_issues)
        }
        
    except subprocess.TimeoutExpired:
        return {
            "path": path,
            "error": "分析超时，请检查项目大小或指定具体文件"
        }
    except FileNotFoundError:
        return {
            "path": path,
            "error": "pylint 未安装，请运行：pip install pylint"
        }
    except Exception as e:
        return {
            "path": path,
            "error": f"分析失败: {str(e)}"
        }


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
    
    lines = [f"分析路径: {result['path']}", ""]
    lines.append("问题统计:")
    lines.append(f"  错误 (Error): {result['stats']['error']}")
    lines.append(f"  警告 (Warning): {result['stats']['warning']}")
    lines.append(f"  重构 (Refactor): {result['stats']['refactor']}")
    lines.append(f"  约定 (Convention): {result['stats']['convention']}")
    lines.append(f"  信息 (Info): {result['stats']['info']}")
    lines.append(f"  总计: {result['total_issues']}")
    lines.append("")
    
    if result['issues']:
        lines.append("详细问题:")
        for issue in result['issues']:
            lines.append(
                f"  [{issue['type'].upper()}] {issue['module']}:{issue['line']}:{issue['column']} - "
                f"{issue['message']} ({issue['symbol']})"
            )
    
    return "\n".join(lines)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="静态代码分析工具")
    parser.add_argument("--path", required=True, help="要分析的文件或目录路径")
    parser.add_argument("--output", choices=["json", "text"], default="json",
                       help="输出格式（默认：json）")
    
    args = parser.parse_args()
    
    # 验证路径存在
    if not Path(args.path).exists():
        print(f"错误: 路径不存在: {args.path}", file=sys.stderr)
        sys.exit(1)
    
    # 执行分析
    result = run_pylint(args.path)
    
    # 输出结果
    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_text_output(result))


if __name__ == "__main__":
    main()
