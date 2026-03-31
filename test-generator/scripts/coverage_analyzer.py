#!/usr/bin/env python3
"""
覆盖率分析器

功能：使用 pytest-cov 收集代码覆盖率数据
用途：分析测试覆盖率、识别未覆盖代码、生成覆盖率报告

使用方式：
    python coverage_analyzer.py --source ./myproject --tests ./tests --min-coverage 80

参数说明：
    --source: 源码目录路径（必需）
    --tests: 测试目录路径（必需）
    --min-coverage: 最低覆盖率阈值（默认：0）
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any
import xml.etree.ElementTree as ET


def run_coverage(source: str, tests: str, min_coverage: int = 0) -> Dict[str, Any]:
    """
    执行覆盖率分析
    
    Args:
        source: 源码目录路径
        tests: 测试目录路径
        min_coverage: 最低覆盖率阈值
    
    Returns:
        覆盖率分析结果
    """
    try:
        # 生成覆盖率报告
        cmd = [
            "pytest",
            tests,
            f"--cov={source}",
            "--cov-report=json:coverage.json",
            "--cov-report=term-missing",
            "--cov-report=xml:coverage.xml",
            "-q"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # 读取 JSON 报告
        coverage_file = Path("coverage.json")
        if coverage_file.exists():
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
        else:
            coverage_data = {}
        
        # 解析覆盖率数据
        summary = parse_coverage_data(coverage_data, source)
        
        # 检查是否达到阈值
        meets_threshold = summary['percent_covered'] >= min_coverage
        
        # 清理临时文件
        for temp_file in ["coverage.json", "coverage.xml"]:
            if Path(temp_file).exists():
                Path(temp_file).unlink()
        
        return {
            "source": source,
            "tests": tests,
            "min_coverage": min_coverage,
            "meets_threshold": meets_threshold,
            "summary": summary,
            "files": coverage_data.get("files", {}),
            "output": result.stdout + result.stderr
        }
        
    except subprocess.TimeoutExpired:
        return {
            "source": source,
            "tests": tests,
            "error": "覆盖率分析超时（超过 5 分钟）"
        }
    except FileNotFoundError:
        return {
            "source": source,
            "tests": tests,
            "error": "pytest 或 pytest-cov 未安装，请运行：pip install pytest pytest-cov"
        }
    except Exception as e:
        return {
            "source": source,
            "tests": tests,
            "error": f"覆盖率分析失败: {str(e)}"
        }


def parse_coverage_data(data: Dict, source: str) -> Dict[str, Any]:
    """
    解析覆盖率数据
    
    Args:
        data: coverage.json 数据
        source: 源码路径
    
    Returns:
        覆盖率摘要
    """
    if not data:
        return {
            "total_lines": 0,
            "covered_lines": 0,
            "percent_covered": 0.0,
            "missing_lines": []
        }
    
    totals = data.get("totals", {})
    
    return {
        "total_lines": totals.get("num_statements", 0),
        "covered_lines": totals.get("covered_lines", 0),
        "percent_covered": round(totals.get("percent_covered", 0), 2),
        "missing_lines": find_missing_lines(data, source)
    }


def find_missing_lines(data: Dict, source: str) -> List[Dict[str, Any]]:
    """
    查找未覆盖的代码行
    
    Args:
        data: coverage.json 数据
        source: 源码路径
    
    Returns:
        未覆盖代码行列表
    """
    missing = []
    
    files = data.get("files", {})
    for file_path, file_data in files.items():
        # 只处理指定源码目录下的文件
        if not file_path.startswith(source):
            continue
        
        executed_lines = file_data.get("executed_lines", [])
        summary = file_data.get("summary", {})
        missing_count = summary.get("missing_lines", 0)
        
        if missing_count > 0:
            # 找出缺失的行号
            all_lines = set(range(1, summary.get("num_statements", 0) + 1))
            executed = set(executed_lines)
            missing_line_nums = sorted(all_lines - executed)
            
            missing.append({
                "file": file_path,
                "missing_count": missing_count,
                "missing_lines": missing_line_nums[:10]  # 只返回前 10 行
            })
    
    return missing


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
    
    status = "✓ 达标" if result['meets_threshold'] else "✗ 未达标"
    lines = [f"覆盖率分析: {result['source']}", ""]
    lines.append(f"最低覆盖率要求: {result['min_coverage']}%")
    lines.append(f"状态: {status}")
    lines.append("")
    
    summary = result['summary']
    lines.append("覆盖率统计:")
    lines.append(f"  总代码行数: {summary['total_lines']}")
    lines.append(f"  已覆盖行数: {summary['covered_lines']}")
    lines.append(f"  覆盖率: {summary['percent_covered']}%")
    lines.append("")
    
    if summary['missing_lines']:
        lines.append("未覆盖代码:")
        for file_info in summary['missing_lines'][:5]:  # 只显示前 5 个文件
            lines.append(f"\n  {file_info['file']}:")
            lines.append(f"    缺失 {file_info['missing_count']} 行")
            if file_info['missing_lines']:
                lines.append(f"    行号: {file_info['missing_lines']}")
    
    return "\n".join(lines)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="覆盖率分析器")
    parser.add_argument("--source", required=True, help="源码目录路径")
    parser.add_argument("--tests", required=True, help="测试目录路径")
    parser.add_argument("--min-coverage", type=float, default=0,
                       help="最低覆盖率阈值（默认：0）")
    parser.add_argument("--output", choices=["json", "text"], default="json",
                       help="输出格式（默认：json）")
    
    args = parser.parse_args()
    
    # 验证路径存在
    if not Path(args.source).exists():
        print(f"错误: 源码路径不存在: {args.source}", file=sys.stderr)
        sys.exit(1)
    
    if not Path(args.tests).exists():
        print(f"错误: 测试路径不存在: {args.tests}", file=sys.stderr)
        sys.exit(1)
    
    # 执行覆盖率分析
    result = run_coverage(args.source, args.tests, args.min_coverage)
    
    # 输出结果
    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_text_output(result))
    
    # 如果未达到阈值，返回错误码
    if not result.get("meets_threshold", True):
        sys.exit(1)


if __name__ == "__main__":
    main()
