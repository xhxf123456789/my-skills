#!/usr/bin/env python3
"""
分支管理器

功能：管理 Git 分支
用途：创建、切换、合并、删除分支

使用方式：
    python branch_manager.py --branch feature/new-feature --action create
    python branch_manager.py --branch develop --action switch
    python branch_manager.py --branch feature/new-feature --action merge
    python branch_manager.py --branch old-feature --action delete

参数说明：
    --branch: 分支名称
    --action: 操作类型（create/switch/merge/delete/list）
"""

import argparse
import json
import subprocess
import sys
from typing import Dict, List, Any


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


def get_current_branch() -> str:
    """获取当前分支名"""
    result = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
    return result["stdout"] if result["success"] else "unknown"


def branch_exists(branch_name: str) -> bool:
    """检查分支是否存在"""
    result = run_git_command(["branch", "--list", branch_name])
    return branch_name in result["stdout"]


def create_branch(branch_name: str, base_branch: str = None) -> Dict[str, Any]:
    """创建新分支"""
    if not is_git_repo():
        return {"success": False, "error": "当前目录不是 Git 仓库"}
    
    if branch_exists(branch_name):
        return {"success": False, "error": f"分支 '{branch_name}' 已存在"}
    
    # 创建分支
    if base_branch:
        result = run_git_command(["checkout", "-b", branch_name, base_branch])
    else:
        result = run_git_command(["checkout", "-b", branch_name])
    
    if result["success"]:
        return {
            "success": True,
            "branch": branch_name,
            "base_branch": base_branch or get_current_branch(),
            "message": f"分支 '{branch_name}' 创建成功"
        }
    else:
        return {
            "success": False,
            "error": result.get("stderr", "创建分支失败")
        }


def switch_branch(branch_name: str) -> Dict[str, Any]:
    """切换分支"""
    if not is_git_repo():
        return {"success": False, "error": "当前目录不是 Git 仓库"}
    
    if not branch_exists(branch_name):
        return {"success": False, "error": f"分支 '{branch_name}' 不存在"}
    
    current_branch = get_current_branch()
    if current_branch == branch_name:
        return {
            "success": True,
            "branch": branch_name,
            "message": f"已在分支 '{branch_name}' 上"
        }
    
    result = run_git_command(["checkout", branch_name])
    
    if result["success"]:
        return {
            "success": True,
            "previous_branch": current_branch,
            "current_branch": branch_name,
            "message": f"已切换到分支 '{branch_name}'"
        }
    else:
        return {
            "success": False,
            "error": result.get("stderr", "切换分支失败")
        }


def merge_branch(branch_name: str, target_branch: str = None) -> Dict[str, Any]:
    """合并分支"""
    if not is_git_repo():
        return {"success": False, "error": "当前目录不是 Git 仓库"}
    
    if not branch_exists(branch_name):
        return {"success": False, "error": f"分支 '{branch_name}' 不存在"}
    
    # 确定目标分支
    if not target_branch:
        target_branch = get_current_branch()
    
    # 切换到目标分支
    if get_current_branch() != target_branch:
        switch_result = switch_branch(target_branch)
        if not switch_result["success"]:
            return switch_result
    
    # 执行合并
    result = run_git_command(["merge", branch_name, "--no-ff", "-m", f"Merge branch '{branch_name}'"])
    
    if result["success"]:
        return {
            "success": True,
            "source_branch": branch_name,
            "target_branch": target_branch,
            "message": f"分支 '{branch_name}' 已合并到 '{target_branch}'"
        }
    else:
        # 检查是否有冲突
        if "CONFLICT" in result["stdout"] or "CONFLICT" in result["stderr"]:
            return {
                "success": False,
                "error": "合并冲突",
                "has_conflicts": True,
                "details": result["stderr"]
            }
        else:
            return {
                "success": False,
                "error": result.get("stderr", "合并失败")
            }


def delete_branch(branch_name: str, force: bool = False) -> Dict[str, Any]:
    """删除分支"""
    if not is_git_repo():
        return {"success": False, "error": "当前目录不是 Git 仓库"}
    
    if not branch_exists(branch_name):
        return {"success": False, "error": f"分支 '{branch_name}' 不存在"}
    
    current_branch = get_current_branch()
    if current_branch == branch_name:
        return {"success": False, "error": "无法删除当前所在分支"}
    
    # 删除分支
    flag = "-D" if force else "-d"
    result = run_git_command(["branch", flag, branch_name])
    
    if result["success"]:
        return {
            "success": True,
            "branch": branch_name,
            "message": f"分支 '{branch_name}' 已删除"
        }
    else:
        return {
            "success": False,
            "error": result.get("stderr", "删除分支失败"),
            "hint": "如果分支未合并，使用 --force 强制删除"
        }


def list_branches() -> Dict[str, Any]:
    """列出所有分支"""
    if not is_git_repo():
        return {"success": False, "error": "当前目录不是 Git 仓库"}
    
    # 获取本地分支
    local_result = run_git_command(["branch", "--list"])
    local_branches = []
    current_branch = None
    
    for line in local_result["stdout"].split('\n'):
        if not line:
            continue
        
        is_current = line.startswith('*')
        branch_name = line.strip().lstrip('* ')
        
        if is_current:
            current_branch = branch_name
        
        local_branches.append({
            "name": branch_name,
            "is_current": is_current
        })
    
    # 获取远程分支
    remote_result = run_git_command(["branch", "-r", "--list"])
    remote_branches = []
    
    for line in remote_result["stdout"].split('\n'):
        if not line or "HEAD" in line:
            continue
        
        branch_name = line.strip()
        remote_branches.append(branch_name)
    
    return {
        "success": True,
        "current_branch": current_branch,
        "local_branches": local_branches,
        "remote_branches": remote_branches
    }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="分支管理器")
    parser.add_argument("--branch", help="分支名称")
    parser.add_argument("--action", required=True,
                       choices=["create", "switch", "merge", "delete", "list"],
                       help="操作类型")
    parser.add_argument("--base-branch", help="基准分支（创建时使用）")
    parser.add_argument("--target-branch", help="目标分支（合并时使用）")
    parser.add_argument("--force", action="store_true", help="强制删除")
    parser.add_argument("--output", choices=["json", "text"], default="json",
                       help="输出格式（默认：json）")
    
    args = parser.parse_args()
    
    # list 操作不需要分支名
    if args.action != "list" and not args.branch:
        print("错误: 此操作需要指定分支名称", file=sys.stderr)
        sys.exit(1)
    
    # 执行操作
    if args.action == "create":
        result = create_branch(args.branch, args.base_branch)
    elif args.action == "switch":
        result = switch_branch(args.branch)
    elif args.action == "merge":
        result = merge_branch(args.branch, args.target_branch)
    elif args.action == "delete":
        result = delete_branch(args.branch, args.force)
    elif args.action == "list":
        result = list_branches()
    
    # 输出结果
    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if "error" in result:
            print(f"错误: {result['error']}")
        else:
            print(f"成功: {result.get('message', '操作完成')}")
    
    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main()
