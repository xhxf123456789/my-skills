#!/usr/bin/env python3
"""
Git 操作封装

功能：封装常用 Git 操作
用途：执行 Git 命令（status、add、commit、push、pull）

使用方式：
    python git_operations.py --action status
    python git_operations.py --action add --files .
    python git_operations.py --action commit --message "提交信息"
    python git_operations.py --action push

参数说明：
    --action: 操作类型（status/add/commit/push/pull）
    --files: 要添加的文件（仅 add 操作）
    --message: 提交信息（仅 commit 操作）
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


def run_git_command(args: List[str], check: bool = True) -> Dict[str, Any]:
    """
    执行 Git 命令
    
    Args:
        args: Git 命令参数列表
        check: 是否检查返回码
    
    Returns:
        命令执行结果
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=False
        )
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }
        
    except FileNotFoundError:
        return {
            "success": False,
            "error": "Git 未安装或不在 PATH 中"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"执行 Git 命令失败: {str(e)}"
        }


def is_git_repo() -> bool:
    """检查当前目录是否是 Git 仓库"""
    result = run_git_command(["rev-parse", "--git-dir"], check=False)
    return result["success"]


def git_status() -> Dict[str, Any]:
    """获取 Git 状态"""
    if not is_git_repo():
        return {"error": "当前目录不是 Git 仓库"}
    
    result = run_git_command(["status", "--porcelain"])
    if not result["success"]:
        return {"error": result.get("stderr", "获取状态失败")}
    
    # 解析状态
    files = {
        "staged": [],
        "modified": [],
        "untracked": [],
        "deleted": []
    }
    
    for line in result["stdout"].split('\n'):
        if not line:
            continue
        
        status = line[:2]
        filename = line[3:].strip()
        
        if status.startswith('M') or status.startswith('A'):
            files["staged"].append(filename)
        elif 'M' in status:
            files["modified"].append(filename)
        elif status.strip() == '??':
            files["untracked"].append(filename)
        elif 'D' in status:
            files["deleted"].append(filename)
    
    return {
        "success": True,
        "files": files,
        "has_changes": any(files.values())
    }


def git_add(files: List[str]) -> Dict[str, Any]:
    """添加文件到暂存区"""
    if not is_git_repo():
        return {"error": "当前目录不是 Git 仓库"}
    
    result = run_git_command(["add"] + files)
    
    return {
        "success": result["success"],
        "files": files,
        "message": "文件已添加到暂存区" if result["success"] else result.get("stderr", "添加失败")
    }


def git_commit(message: str) -> Dict[str, Any]:
    """提交变更"""
    if not is_git_repo():
        return {"error": "当前目录不是 Git 仓库"}
    
    result = run_git_command(["commit", "-m", message])
    
    if result["success"]:
        # 获取提交哈希
        hash_result = run_git_command(["rev-parse", "HEAD"])
        commit_hash = hash_result["stdout"] if hash_result["success"] else "unknown"
        
        return {
            "success": True,
            "commit_hash": commit_hash,
            "message": "提交成功"
        }
    else:
        return {
            "success": False,
            "error": result.get("stderr", "提交失败")
        }


def git_push(remote: str = "origin", branch: str = None) -> Dict[str, Any]:
    """推送到远程仓库"""
    if not is_git_repo():
        return {"error": "当前目录不是 Git 仓库"}
    
    # 获取当前分支
    if not branch:
        branch_result = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
        branch = branch_result["stdout"] if branch_result["success"] else "main"
    
    result = run_git_command(["push", remote, branch])
    
    return {
        "success": result["success"],
        "remote": remote,
        "branch": branch,
        "message": "推送成功" if result["success"] else result.get("stderr", "推送失败")
    }


def git_pull(remote: str = "origin", branch: str = None) -> Dict[str, Any]:
    """拉取远程变更"""
    if not is_git_repo():
        return {"error": "当前目录不是 Git 仓库"}
    
    # 获取当前分支
    if not branch:
        branch_result = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
        branch = branch_result["stdout"] if branch_result["success"] else "main"
    
    result = run_git_command(["pull", remote, branch])
    
    return {
        "success": result["success"],
        "remote": remote,
        "branch": branch,
        "message": "拉取成功" if result["success"] else result.get("stderr", "拉取失败")
    }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Git 操作封装")
    parser.add_argument("--action", required=True,
                       choices=["status", "add", "commit", "push", "pull"],
                       help="操作类型")
    parser.add_argument("--files", nargs="+", help="要添加的文件")
    parser.add_argument("--message", help="提交信息")
    parser.add_argument("--remote", default="origin", help="远程仓库名称")
    parser.add_argument("--branch", help="分支名称")
    parser.add_argument("--output", choices=["json", "text"], default="json",
                       help="输出格式（默认：json）")
    
    args = parser.parse_args()
    
    # 执行操作
    if args.action == "status":
        result = git_status()
    elif args.action == "add":
        if not args.files:
            print("错误: add 操作需要指定文件", file=sys.stderr)
            sys.exit(1)
        result = git_add(args.files)
    elif args.action == "commit":
        if not args.message:
            print("错误: commit 操作需要提交信息", file=sys.stderr)
            sys.exit(1)
        result = git_commit(args.message)
    elif args.action == "push":
        result = git_push(args.remote, args.branch)
    elif args.action == "pull":
        result = git_pull(args.remote, args.branch)
    
    # 输出结果
    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if "error" in result:
            print(f"错误: {result['error']}")
        else:
            print(f"成功: {result.get('message', '操作完成')}")
    
    # 返回状态码
    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main()
