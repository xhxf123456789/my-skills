#!/usr/bin/env python3
"""
代码变更分析器

功能：分析代码变更详情
用途：分析 Git diff、统计变更、生成变更报告

使用方式：
    python change_analyzer.py --range staged
    python change_analyzer.py --range last-n --count 5
    python change_analyzer.py --range branches --base main --target feature

参数说明：
    --range: 分析范围（staged/last-n/branches/diff）
    --count: 最近 N 次提交（仅 last-n 模式）
    --base: 基准分支（仅 branches 模式）
    --target: 目标分支（仅 branches 模式）
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import re


def run_git_command(args: List[str]) -> Dict[str, Any]:
    """执行 Git 命令"""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=False
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def is_git_repo() -> bool:
    """检查是否是 Git 仓库"""
    result = run_git_command(["rev-parse", "--git-dir"])
    return result["success"]


def analyze_staged_changes() -> Dict[str, Any]:
    """分析暂存区变更"""
    if not is_git_repo():
        return {"error": "当前目录不是 Git 仓库"}
    
    # 获取暂存区文件列表
    result = run_git_command(["diff", "--cached", "--name-status"])
    if not result["success"]:
        return {"error": "获取暂存区文件失败"}
    
    files = []
    for line in result["stdout"].split('\n'):
        if not line:
            continue
        
        parts = line.split('\t')
        if len(parts) >= 2:
            status = parts[0]
            filename = parts[1]
            files.append({
                "status": status,
                "filename": filename,
                "change_type": get_change_type(status)
            })
    
    # 获取变更统计
    stats_result = run_git_command(["diff", "--cached", "--stat"])
    stats = parse_stats(stats_result["stdout"])
    
    # 获取详细 diff
    diff_result = run_git_command(["diff", "--cached"])
    
    return {
        "success": True,
        "range": "staged",
        "files": files,
        "stats": stats,
        "diff": diff_result["stdout"],
        "has_changes": len(files) > 0
    }


def analyze_last_n_commits(count: int = 5) -> Dict[str, Any]:
    """分析最近 N 次提交"""
    if not is_git_repo():
        return {"error": "当前目录不是 Git 仓库"}
    
    # 获取最近 N 次提交
    result = run_git_command([
        "log", f"-{count}",
        "--pretty=format:%H|%an|%ae|%ad|%s",
        "--date=iso"
    ])
    
    if not result["success"]:
        return {"error": "获取提交历史失败"}
    
    commits = []
    for line in result["stdout"].split('\n'):
        if not line:
            continue
        
        parts = line.split('|', 4)
        if len(parts) >= 5:
            commits.append({
                "hash": parts[0],
                "author": parts[1],
                "email": parts[2],
                "date": parts[3],
                "message": parts[4]
            })
    
    # 获取每次提交的文件变更统计
    for commit in commits:
        stats_result = run_git_command([
            "show", "--stat", "--pretty=format:", commit["hash"]
        ])
        commit["stats"] = parse_stats(stats_result["stdout"])
    
    return {
        "success": True,
        "range": f"last-{count}",
        "commits": commits,
        "count": len(commits)
    }


def analyze_branch_diff(base: str, target: str) -> Dict[str, Any]:
    """分析两个分支的差异"""
    if not is_git_repo():
        return {"error": "当前目录不是 Git 仓库"}
    
    # 获取文件变更列表
    result = run_git_command([
        "diff", "--name-status", f"{base}...{target}"
    ])
    
    if not result["success"]:
        return {"error": f"比较分支失败: {result.get('stderr', '未知错误')}"}
    
    files = []
    for line in result["stdout"].split('\n'):
        if not line:
            continue
        
        parts = line.split('\t')
        if len(parts) >= 2:
            status = parts[0]
            filename = parts[1]
            files.append({
                "status": status,
                "filename": filename,
                "change_type": get_change_type(status)
            })
    
    # 获取变更统计
    stats_result = run_git_command([
        "diff", "--stat", f"{base}...{target}"
    ])
    stats = parse_stats(stats_result["stdout"])
    
    return {
        "success": True,
        "range": "branches",
        "base": base,
        "target": target,
        "files": files,
        "stats": stats,
        "has_changes": len(files) > 0
    }


def analyze_diff(commit1: str = None, commit2: str = None) -> Dict[str, Any]:
    """分析两次提交之间的差异"""
    if not is_git_repo():
        return {"error": "当前目录不是 Git 仓库"}
    
    # 构建比较范围
    if commit1 and commit2:
        range_spec = f"{commit1}...{commit2}"
    elif commit1:
        range_spec = commit1
    else:
        range_spec = "HEAD"
    
    # 获取文件变更
    result = run_git_command(["diff", "--name-status", range_spec])
    if not result["success"]:
        return {"error": "获取变更失败"}
    
    files = []
    for line in result["stdout"].split('\n'):
        if not line:
            continue
        
        parts = line.split('\t')
        if len(parts) >= 2:
            status = parts[0]
            filename = parts[1]
            files.append({
                "status": status,
                "filename": filename,
                "change_type": get_change_type(status)
            })
    
    # 获取统计信息
    stats_result = run_git_command(["diff", "--stat", range_spec])
    stats = parse_stats(stats_result["stdout"])
    
    return {
        "success": True,
        "range": range_spec,
        "files": files,
        "stats": stats
    }


def get_change_type(status: str) -> str:
    """获取变更类型"""
    status_map = {
        'A': '新增',
        'M': '修改',
        'D': '删除',
        'R': '重命名',
        'C': '复制',
        'T': '类型变更'
    }
    return status_map.get(status[0], '未知')


def parse_stats(stats_text: str) -> Dict[str, int]:
    """解析统计信息"""
    stats = {
        "files_changed": 0,
        "insertions": 0,
        "deletions": 0
    }
    
    # 匹配统计行，如：3 files changed, 10 insertions(+), 5 deletions(-)
    match = re.search(r'(\d+) files? changed', stats_text)
    if match:
        stats["files_changed"] = int(match.group(1))
    
    match = re.search(r'(\d+) insertions?\(\+\)', stats_text)
    if match:
        stats["insertions"] = int(match.group(1))
    
    match = re.search(r'(\d+) deletions?\(-\)', stats_text)
    if match:
        stats["deletions"] = int(match.group(1))
    
    return stats


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="代码变更分析器")
    parser.add_argument("--range", required=True,
                       choices=["staged", "last-n", "branches", "diff"],
                       help="分析范围")
    parser.add_argument("--count", type=int, default=5,
                       help="最近 N 次提交（默认：5）")
    parser.add_argument("--base", help="基准分支")
    parser.add_argument("--target", help="目标分支")
    parser.add_argument("--commit1", help="起始提交")
    parser.add_argument("--commit2", help="结束提交")
    parser.add_argument("--output", choices=["json", "text"], default="json",
                       help="输出格式（默认：json）")
    
    args = parser.parse_args()
    
    # 执行分析
    if args.range == "staged":
        result = analyze_staged_changes()
    elif args.range == "last-n":
        result = analyze_last_n_commits(args.count)
    elif args.range == "branches":
        if not args.base or not args.target:
            print("错误: branches 模式需要 --base 和 --target 参数", file=sys.stderr)
            sys.exit(1)
        result = analyze_branch_diff(args.base, args.target)
    elif args.range == "diff":
        result = analyze_diff(args.commit1, args.commit2)
    
    # 输出结果
    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_text_output(result))
    
    sys.exit(0 if result.get("success", False) else 1)


def format_text_output(result: Dict[str, Any]) -> str:
    """格式化文本输出"""
    if "error" in result:
        return f"错误: {result['error']}"
    
    lines = ["代码变更分析", ""]
    
    if result.get("range") == "staged":
        lines.append("暂存区变更:")
        for file_info in result.get("files", []):
            lines.append(f"  {file_info['change_type']}: {file_info['filename']}")
        
        stats = result.get("stats", {})
        if stats.get("files_changed", 0) > 0:
            lines.append("")
            lines.append(f"统计: {stats['files_changed']} 文件, "
                        f"+{stats['insertions']} -{stats['deletions']}")
    
    elif result.get("range", "").startswith("last-"):
        lines.append(f"最近 {result.get('count', 0)} 次提交:")
        for commit in result.get("commits", []):
            lines.append(f"\n  [{commit['hash'][:7]}] {commit['message']}")
            lines.append(f"  作者: {commit['author']} <{commit['email']}>")
            lines.append(f"  日期: {commit['date']}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    main()
