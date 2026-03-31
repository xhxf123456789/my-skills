#!/usr/bin/env python3
"""
测试执行器

功能：执行 pytest 测试并收集结果
用途：运行测试、统计通过/失败、收集测试时间

使用方式：
    python test_runner.py --path ./tests --verbose

参数说明：
    --path: 测试文件或目录路径（必需）
    --verbose: 详细输出模式（可选）
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any


def run_tests(path: str, verbose: bool = False) -> Dict[str, Any]:
    """
    执行测试并收集结果
    
    Args:
        path: 测试文件或目录路径
        verbose: 是否详细输出
    
    Returns:
        测试结果字典
    """
    try:
        # 构建 pytest 命令
        cmd = ["pytest", path, "-v" if verbose else "", "--tb=short", "-q"]
        cmd = [arg for arg in cmd if arg]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # 解析输出
        output = result.stdout + result.stderr
        
        # 提取统计信息
        stats = parse_test_output(output)
        
        return {
            "path": path,
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stats": stats,
            "output": output,
            "verbose": verbose
        }
        
    except subprocess.TimeoutExpired:
        return {
            "path": path,
            "success": False,
            "error": "测试执行超时（超过 5 分钟）"
        }
    except FileNotFoundError:
        return {
            "path": path,
            "success": False,
            "error": "pytest 未安装，请运行：pip install pytest"
        }
    except Exception as e:
        return {
            "path": path,
            "success": False,
            "error": f"测试执行失败: {str(e)}"
        }


def parse_test_output(output: str) -> Dict[str, Any]:
    """
    解析 pytest 输出提取统计信息
    
    Args:
        output: pytest 输出文本
    
    Returns:
        统计信息字典
    """
    stats = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": 0,
        "duration": "0s"
    }
    
    lines = output.split('\n')
    
    for line in lines:
        # 解析测试结果行
        # 格式：X passed, Y failed, Z skipped in Ts
        if 'passed' in line or 'failed' in line or 'skipped' in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part == 'passed' and i > 0:
                    try:
                        stats['passed'] = int(parts[i-1])
                    except (ValueError, IndexError):
                        pass
                elif part == 'failed' and i > 0:
                    try:
                        stats['failed'] = int(parts[i-1])
                    except (ValueError, IndexError):
                        pass
                elif part == 'skipped' and i > 0:
                    try:
                        stats['skipped'] = int(parts[i-1])
                    except (ValueError, IndexError):
                        pass
                elif part == 'error' or part == 'errors' and i > 0:
                    try:
                        stats['errors'] = int(parts[i-1])
                    except (ValueError, IndexError):
                        pass
        
        # 提取执行时间
        if 'in' in line and ('s' in line or 'ms' in line):
            try:
                time_idx = line.index('in')
                stats['duration'] = line[time_idx+2:].strip().split()[0]
            except (ValueError, IndexError):
                pass
    
    stats['total'] = stats['passed'] + stats['failed'] + stats['skipped'] + stats['errors']
    
    return stats


def format_text_output(result: Dict[str, Any]) -> str:
    """
    格式化输出为文本格式
    
    Args:
        result: 测试结果
    
    Returns:
        格式化的文本
    """
    if "error" in result:
        return f"错误: {result['error']}"
    
    status = "✓ 通过" if result['success'] else "✗ 失败"
    lines = [f"测试执行: {result['path']}", ""]
    lines.append(f"状态: {status}")
    lines.append("")
    
    stats = result['stats']
    lines.append("测试统计:")
    lines.append(f"  总计: {stats['total']}")
    lines.append(f"  通过: {stats['passed']}")
    lines.append(f"  失败: {stats['failed']}")
    lines.append(f"  跳过: {stats['skipped']}")
    lines.append(f"  错误: {stats['errors']}")
    lines.append(f"  耗时: {stats['duration']}")
    
    if result['verbose'] and result.get('output'):
        lines.append("")
        lines.append("详细输出:")
        lines.append(result['output'])
    
    return "\n".join(lines)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="测试执行器")
    parser.add_argument("--path", required=True, help="测试文件或目录路径")
    parser.add_argument("--verbose", action="store_true", help="详细输出模式")
    parser.add_argument("--output", choices=["json", "text"], default="json",
                       help="输出格式（默认：json）")
    
    args = parser.parse_args()
    
    # 验证路径存在
    if not Path(args.path).exists():
        print(f"错误: 路径不存在: {args.path}", file=sys.stderr)
        sys.exit(1)
    
    # 执行测试
    result = run_tests(args.path, args.verbose)
    
    # 输出结果
    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_text_output(result))
    
    # 返回测试结果状态码
    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main()
