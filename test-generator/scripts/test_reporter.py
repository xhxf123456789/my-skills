#!/usr/bin/env python3
"""
测试报告生成器

功能：生成综合测试报告
用途：整合测试结果和覆盖率数据，生成 Markdown/HTML 报告

使用方式：
    python test_reporter.py --test-result test_result.json --coverage coverage.json --format markdown

参数说明：
    --test-result: 测试结果文件路径（可选）
    --coverage: 覆盖率文件路径（可选）
    --format: 报告格式，可选值：markdown/html（默认：markdown）
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


def generate_markdown_report(
    test_result: Optional[Dict] = None,
    coverage_result: Optional[Dict] = None
) -> str:
    """
    生成 Markdown 格式的测试报告
    
    Args:
        test_result: 测试结果数据
        coverage_result: 覆盖率数据
    
    Returns:
        Markdown 格式的报告
    """
    lines = [
        "# 测试报告",
        "",
        f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]
    
    # 测试结果部分
    if test_result:
        lines.extend(generate_test_section(test_result))
    
    # 覆盖率部分
    if coverage_result:
        lines.extend(generate_coverage_section(coverage_result))
    
    # 建议
    lines.extend(generate_recommendations(test_result, coverage_result))
    
    return "\n".join(lines)


def generate_test_section(result: Dict) -> List[str]:
    """生成测试结果部分"""
    lines = [
        "## 测试结果",
        ""
    ]
    
    if "error" in result:
        lines.append(f"**错误**: {result['error']}")
        return lines
    
    stats = result.get("stats", {})
    status = "✓ 通过" if result.get("success") else "✗ 失败"
    
    lines.extend([
        f"**状态**: {status}",
        "",
        "### 统计信息",
        "",
        "| 指标 | 数量 |",
        "|------|------|",
        f"| 总计 | {stats.get('total', 0)} |",
        f"| 通过 | {stats.get('passed', 0)} |",
        f"| 失败 | {stats.get('failed', 0)} |",
        f"| 跳过 | {stats.get('skipped', 0)} |",
        f"| 错误 | {stats.get('errors', 0)} |",
        f"| 耗时 | {stats.get('duration', '0s')} |",
        ""
    ])
    
    return lines


def generate_coverage_section(result: Dict) -> List[str]:
    """生成覆盖率部分"""
    lines = [
        "## 覆盖率分析",
        ""
    ]
    
    if "error" in result:
        lines.append(f"**错误**: {result['error']}")
        return lines
    
    summary = result.get("summary", {})
    status = "✓ 达标" if result.get("meets_threshold") else "✗ 未达标"
    min_coverage = result.get("min_coverage", 0)
    
    lines.extend([
        f"**最低覆盖率要求**: {min_coverage}%",
        f"**状态**: {status}",
        "",
        "### 覆盖率统计",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| 总代码行数 | {summary.get('total_lines', 0)} |",
        f"| 已覆盖行数 | {summary.get('covered_lines', 0)} |",
        f"| 覆盖率 | {summary.get('percent_covered', 0)}% |",
        ""
    ])
    
    # 未覆盖代码
    missing = summary.get("missing_lines", [])
    if missing:
        lines.extend([
            "### 未覆盖代码",
            ""
        ])
        
        for file_info in missing[:10]:  # 只显示前 10 个文件
            lines.append(f"- **{file_info['file']}**: 缺失 {file_info['missing_count']} 行")
            if file_info.get('missing_lines'):
                lines.append(f"  - 行号: {file_info['missing_lines']}")
        
        lines.append("")
    
    return lines


def generate_recommendations(
    test_result: Optional[Dict],
    coverage_result: Optional[Dict]
) -> List[str]:
    """生成改进建议"""
    lines = [
        "## 改进建议",
        ""
    ]
    
    recommendations = []
    
    if test_result:
        stats = test_result.get("stats", {})
        if stats.get("failed", 0) > 0:
            recommendations.append("修复失败的测试用例")
        if stats.get("errors", 0) > 0:
            recommendations.append("解决测试错误")
    
    if coverage_result:
        summary = coverage_result.get("summary", {})
        coverage = summary.get("percent_covered", 0)
        
        if coverage < 50:
            recommendations.append("测试覆盖率过低，建议添加更多测试用例")
        elif coverage < 80:
            recommendations.append("测试覆盖率中等，建议补充关键路径的测试")
        
        if summary.get("missing_lines"):
            recommendations.append("为未覆盖的代码添加测试用例")
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"{i}. {rec}")
    else:
        lines.append("暂无改进建议")
    
    lines.append("")
    
    return lines


def generate_html_report(
    test_result: Optional[Dict] = None,
    coverage_result: Optional[Dict] = None
) -> str:
    """生成 HTML 格式的测试报告"""
    markdown = generate_markdown_report(test_result, coverage_result)
    
    # 简单的 HTML 包装
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试报告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <!-- Markdown 内容转换为 HTML -->
    <pre>{markdown}</pre>
</body>
</html>"""
    
    return html


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="测试报告生成器")
    parser.add_argument("--test-result", help="测试结果文件路径")
    parser.add_argument("--coverage", help="覆盖率文件路径")
    parser.add_argument("--format", choices=["markdown", "html"], default="markdown",
                       help="报告格式（默认：markdown）")
    parser.add_argument("--output", help="输出文件路径（可选）")
    
    args = parser.parse_args()
    
    # 读取测试结果
    test_result = None
    if args.test_result and Path(args.test_result).exists():
        try:
            with open(args.test_result, 'r', encoding='utf-8') as f:
                test_result = json.load(f)
        except Exception as e:
            print(f"警告: 无法读取测试结果文件: {e}", file=sys.stderr)
    
    # 读取覆盖率数据
    coverage_result = None
    if args.coverage and Path(args.coverage).exists():
        try:
            with open(args.coverage, 'r', encoding='utf-8') as f:
                coverage_result = json.load(f)
        except Exception as e:
            print(f"警告: 无法读取覆盖率文件: {e}", file=sys.stderr)
    
    # 生成报告
    if args.format == "markdown":
        report = generate_markdown_report(test_result, coverage_result)
    else:
        report = generate_html_report(test_result, coverage_result)
    
    # 输出报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"报告已保存到: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
