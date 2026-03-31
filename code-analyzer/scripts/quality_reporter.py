#!/usr/bin/env python3
"""
综合质量报告生成器

功能：整合所有分析结果，生成综合质量报告
用途：计算代码质量评分、生成优先级改进建议、输出可视化报告

使用方式：
    python quality_reporter.py --static static.json --complexity complexity.json --duplicate duplicate.json --security security.json --format html

参数说明：
    --static: 静态分析结果文件
    --complexity: 复杂度分析结果文件
    --duplicate: 重复检测结果文件
    --security: 安全扫描结果文件
    --format: 输出格式（markdown/html）
    --output: 输出文件路径（可选）
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


def calculate_quality_score(
    static_result: Optional[Dict] = None,
    complexity_result: Optional[Dict] = None,
    duplicate_result: Optional[Dict] = None,
    security_result: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    计算代码质量评分（0-100）
    
    评分维度：
    1. 静态分析（40%）：问题数量、严重程度
    2. 复杂度（30%）：平均复杂度、高复杂度函数比例
    3. 重复代码（20%）：重复代码比例
    4. 安全性（10%）：安全问题数量、严重程度
    
    Returns:
        评分详情
    """
    scores = {
        "static": 100,
        "complexity": 100,
        "duplicate": 100,
        "security": 100
    }
    
    # 静态分析评分（40%）
    if static_result and "stats" in static_result:
        stats = static_result["stats"]
        total_issues = stats.get("error", 0) * 3 + stats.get("warning", 0) * 2 + stats.get("convention", 0)
        total_lines = static_result.get("total_lines", 1000)
        error_rate = total_issues / max(total_lines / 100, 1)
        scores["static"] = max(0, 100 - error_rate * 5)
    
    # 复杂度评分（30%）
    if complexity_result and "summary" in complexity_result:
        summary = complexity_result["summary"]
        avg_complexity = summary.get("average_complexity", 0)
        high_ratio = summary.get("high_complexity_count", 0) / max(summary.get("total_functions", 1), 1)
        scores["complexity"] = max(0, 100 - (avg_complexity * 3 + high_ratio * 30))
    
    # 重复代码评分（20%）
    if duplicate_result and "summary" in duplicate_result:
        summary = duplicate_result["summary"]
        duplicate_ratio = summary.get("total_duplicate_lines", 0) / max(summary.get("total_blocks", 1), 1)
        scores["duplicate"] = max(0, 100 - duplicate_ratio * 2)
    
    # 安全性评分（10%）
    if security_result and "stats" in security_result:
        stats = security_result["stats"]
        security_issues = stats.get("high", 0) * 5 + stats.get("medium", 0) * 2 + stats.get("low", 0)
        scores["security"] = max(0, 100 - security_issues * 5)
    
    # 计算总分
    total_score = (
        scores["static"] * 0.4 +
        scores["complexity"] * 0.3 +
        scores["duplicate"] * 0.2 +
        scores["security"] * 0.1
    )
    
    return {
        "total_score": round(total_score, 1),
        "dimension_scores": {
            "static_analysis": round(scores["static"], 1),
            "complexity": round(scores["complexity"], 1),
            "duplicate_code": round(scores["duplicate"], 1),
            "security": round(scores["security"], 1)
        },
        "grade": get_grade(total_score)
    }


def get_grade(score: float) -> str:
    """根据评分获取等级"""
    if score >= 90:
        return "A+"
    elif score >= 85:
        return "A"
    elif score >= 80:
        return "B+"
    elif score >= 75:
        return "B"
    elif score >= 70:
        return "C+"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    else:
        return "F"


def generate_prioritized_recommendations(
    static_result: Optional[Dict] = None,
    complexity_result: Optional[Dict] = None,
    duplicate_result: Optional[Dict] = None,
    security_result: Optional[Dict] = None
) -> List[Dict[str, Any]]:
    """
    生成优先级改进建议
    
    Returns:
        按优先级排序的建议列表
    """
    recommendations = []
    
    # 安全问题（最高优先级）
    if security_result and "issues" in security_result:
        for issue in security_result["issues"]:
            if issue.get("severity") == "high":
                recommendations.append({
                    "priority": 1,
                    "category": "安全",
                    "severity": "高",
                    "issue": issue.get("message", ""),
                    "file": issue.get("file", ""),
                    "line": issue.get("line", 0),
                    "suggestion": get_security_fix_suggestion(issue.get("test_id", ""))
                })
    
    # 错误级别问题
    if static_result and "issues" in static_result:
        for issue in static_result["issues"]:
            if issue.get("type") == "error":
                recommendations.append({
                    "priority": 2,
                    "category": "错误",
                    "severity": "高",
                    "issue": issue.get("message", ""),
                    "file": issue.get("module", ""),
                    "line": issue.get("line", 0),
                    "suggestion": get_pylint_fix_suggestion(issue.get("symbol", ""))
                })
    
    # 高复杂度函数
    if complexity_result and "files" in complexity_result:
        for file_info in complexity_result["files"]:
            for func in file_info.get("functions", []):
                if func.get("is_high_complexity"):
                    recommendations.append({
                        "priority": 3,
                        "category": "复杂度",
                        "severity": "中",
                        "issue": f"函数 {func.get('name', '')} 复杂度过高 ({func.get('complexity', 0)})",
                        "file": file_info.get("file", ""),
                        "line": func.get("lineno", 0),
                        "suggestion": "考虑拆分函数或提取子方法"
                    })
    
    # 重复代码
    if duplicate_result and "duplicates" in duplicate_result:
        for dup in duplicate_result["duplicates"][:5]:  # 只取前5个
            recommendations.append({
                "priority": 4,
                "category": "重复代码",
                "severity": "低",
                "issue": f"发现重复代码（相似度 {dup.get('similarity', 0):.0%}）",
                "files": [b.get("file", "") for b in dup.get("blocks", [])],
                "suggestion": "考虑提取公共方法或使用继承"
            })
    
    # 按优先级排序
    recommendations.sort(key=lambda x: x.get("priority", 5))
    
    return recommendations


def get_security_fix_suggestion(test_id: str) -> str:
    """获取安全问题修复建议"""
    suggestions = {
        "B101": "避免使用 assert 语句进行业务逻辑判断，使用 unittest 断言",
        "B105": "不要硬编码密码，使用环境变量或配置文件",
        "B107": "使用 tempfile 模块创建临时文件",
        "B301": "避免使用 pickle，使用 JSON 等安全格式",
        "B601": "使用参数化查询，避免 SQL 注入",
        "B602": "避免使用 shell=True，使用列表传参"
    }
    return suggestions.get(test_id, "参考 OWASP 安全最佳实践")


def get_pylint_fix_suggestion(symbol: str) -> str:
    """获取 Pylint 问题修复建议"""
    suggestions = {
        "unused-import": "删除未使用的导入",
        "undefined-variable": "检查变量是否已定义",
        "redefined-outer-name": "重命名变量避免与外部变量冲突",
        "too-many-arguments": "考虑使用参数对象或拆分函数",
        "too-many-locals": "提取部分逻辑到子方法",
        "too-many-branches": "使用多态或策略模式替代复杂分支"
    }
    return suggestions.get(symbol, "参考 Pylint 文档")


def generate_markdown_report(
    score_result: Dict,
    recommendations: List[Dict],
    static_result: Optional[Dict] = None,
    complexity_result: Optional[Dict] = None,
    duplicate_result: Optional[Dict] = None,
    security_result: Optional[Dict] = None
) -> str:
    """生成 Markdown 格式报告"""
    lines = [
        "# 代码质量分析报告",
        "",
        f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]
    
    # 质量评分
    lines.extend([
        "## 质量评分",
        "",
        f"### 总分：{score_result['total_score']} 分（{score_result['grade']}）",
        ""
    ])
    
    # 各维度评分
    lines.extend([
        "| 维度 | 评分 | 权重 |",
        "|------|------|------|",
        f"| 静态分析 | {score_result['dimension_scores']['static_analysis']} | 40% |",
        f"| 代码复杂度 | {score_result['dimension_scores']['complexity']} | 30% |",
        f"| 重复代码 | {score_result['dimension_scores']['duplicate_code']} | 20% |",
        f"| 安全性 | {score_result['dimension_scores']['security']} | 10% |",
        ""
    ])
    
    # 改进建议
    lines.extend([
        "## 优先改进建议",
        ""
    ])
    
    for i, rec in enumerate(recommendations[:10], 1):  # 只显示前10条
        priority_emoji = {1: "🔴", 2: "🟠", 3: "🟡", 4: "🟢"}.get(rec.get("priority", 5), "⚪")
        lines.append(f"{i}. {priority_emoji} **{rec.get('category', '')}**: {rec.get('issue', '')}")
        if rec.get("file"):
            lines.append(f"   - 文件：{rec.get('file')}" + (f":{rec.get('line')}" if rec.get("line") else ""))
        if rec.get("suggestion"):
            lines.append(f"   - 建议：{rec.get('suggestion')}")
        lines.append("")
    
    # 统计信息
    if static_result:
        lines.extend([
            "## 静态分析统计",
            ""
        ])
        stats = static_result.get("stats", {})
        lines.append(f"- 错误：{stats.get('error', 0)}")
        lines.append(f"- 警告：{stats.get('warning', 0)}")
        lines.append(f"- 重构：{stats.get('refactor', 0)}")
        lines.append(f"- 约定：{stats.get('convention', 0)}")
        lines.append("")
    
    if complexity_result:
        lines.extend([
            "## 复杂度统计",
            ""
        ])
        summary = complexity_result.get("summary", {})
        lines.append(f"- 函数总数：{summary.get('total_functions', 0)}")
        lines.append(f"- 平均复杂度：{summary.get('average_complexity', 0)}")
        lines.append(f"- 高复杂度函数：{summary.get('high_complexity_count', 0)}")
        lines.append("")
    
    if duplicate_result:
        lines.extend([
            "## 重复代码统计",
            ""
        ])
        summary = duplicate_result.get("summary", {})
        lines.append(f"- 代码块总数：{summary.get('total_blocks', 0)}")
        lines.append(f"- 重复组数：{summary.get('duplicate_groups', 0)}")
        lines.append(f"- 重复代码行数：{summary.get('total_duplicate_lines', 0)}")
        lines.append("")
    
    if security_result:
        lines.extend([
            "## 安全问题统计",
            ""
        ])
        stats = security_result.get("stats", {})
        lines.append(f"- 高危：{stats.get('high', 0)}")
        lines.append(f"- 中危：{stats.get('medium', 0)}")
        lines.append(f"- 低危：{stats.get('low', 0)}")
        lines.append("")
    
    return "\n".join(lines)


def generate_html_report(
    score_result: Dict,
    recommendations: List[Dict],
    static_result: Optional[Dict] = None,
    complexity_result: Optional[Dict] = None,
    duplicate_result: Optional[Dict] = None,
    security_result: Optional[Dict] = None
) -> str:
    """生成 HTML 格式报告"""
    markdown = generate_markdown_report(
        score_result, recommendations,
        static_result, complexity_result, duplicate_result, security_result
    )
    
    # 简单转换为 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>代码质量分析报告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .score {{
            font-size: 48px;
            font-weight: bold;
            color: #3498db;
            text-align: center;
            margin: 20px 0;
        }}
        .grade {{
            font-size: 36px;
            color: #27ae60;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .priority-high {{ color: #e74c3c; }}
        .priority-medium {{ color: #f39c12; }}
        .priority-low {{ color: #27ae60; }}
        .recommendation {{
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #3498db;
        }}
    </style>
</head>
<body>
    <pre style="white-space: pre-wrap; font-family: inherit;">{markdown}</pre>
</body>
</html>"""
    
    return html


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="综合质量报告生成器")
    parser.add_argument("--static", help="静态分析结果文件")
    parser.add_argument("--complexity", help="复杂度分析结果文件")
    parser.add_argument("--duplicate", help="重复检测结果文件")
    parser.add_argument("--security", help="安全扫描结果文件")
    parser.add_argument("--format", choices=["markdown", "html"], default="markdown",
                       help="输出格式（默认：markdown）")
    parser.add_argument("--output", help="输出文件路径（可选）")
    
    args = parser.parse_args()
    
    # 读取分析结果
    static_result = None
    complexity_result = None
    duplicate_result = None
    security_result = None
    
    if args.static and Path(args.static).exists():
        with open(args.static, 'r', encoding='utf-8') as f:
            static_result = json.load(f)
    
    if args.complexity and Path(args.complexity).exists():
        with open(args.complexity, 'r', encoding='utf-8') as f:
            complexity_result = json.load(f)
    
    if args.duplicate and Path(args.duplicate).exists():
        with open(args.duplicate, 'r', encoding='utf-8') as f:
            duplicate_result = json.load(f)
    
    if args.security and Path(args.security).exists():
        with open(args.security, 'r', encoding='utf-8') as f:
            security_result = json.load(f)
    
    # 计算质量评分
    score_result = calculate_quality_score(
        static_result, complexity_result, duplicate_result, security_result
    )
    
    # 生成改进建议
    recommendations = generate_prioritized_recommendations(
        static_result, complexity_result, duplicate_result, security_result
    )
    
    # 生成报告
    if args.format == "html":
        report = generate_html_report(
            score_result, recommendations,
            static_result, complexity_result, duplicate_result, security_result
        )
    else:
        report = generate_markdown_report(
            score_result, recommendations,
            static_result, complexity_result, duplicate_result, security_result
        )
    
    # 输出报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"报告已保存到: {args.output}")
    else:
        print(report)
    
    # 输出评分 JSON
    print("\n" + json.dumps(score_result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
