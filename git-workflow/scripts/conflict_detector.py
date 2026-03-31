#!/usr/bin/env python3
"""
冲突检测器

功能：检测合并冲突
用途：在合并前检测可能的冲突、识别冲突文件

使用方式：
    python conflict_detector.py --target-branch main
    python conflict_detector.py --target-branch develop --source-branch feature

参数说明：
    --target-branch: 目标分支（必需）
    --source-branch: 源分支（可选，默认当前分支）
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


def check_merge_conflicts(target_branch: str, source_branch: str = None) -> Dict[str, Any]:
    """检查合并冲突"""
    if not is_git_repo():
        return {"success": False, "error": "当前目录不是 Git 仓库"}
    
    # 确定源分支
    if not source_branch:
        source_branch = get_current_branch()
    
    # 获取当前分支状态
    status_result = run_git_command(["status", "--porcelain"])
    if status_result["stdout"]:
        return {
            "success": False,
            "error": "当前工作区有未提交的变更，请先提交或暂存",
            "has_uncommitted_changes": True
        }
    
    # 尝试模拟合并（不实际合并）
    merge_result = run_git_command([
        "merge", "--no-commit", "--no-ff", target_branch
    ])
    
    # 获取冲突文件
    conflicts = []
    if not merge_result["success"]:
        # 检查是否有冲突
        status_result = run_git_command(["status", "--porcelain"])
        
        for line in status_result["stdout"].split('\n'):
            if not line:
                continue
            
            # UU 表示未合并的冲突文件
            if line.startswith('UU') or line.startswith('AA') or line.startswith('DD'):
                filename = line[3:].strip()
                conflicts.append({
                    "filename": filename,
                    "status": line[:2]
                })
    
    # 取消合并
    run_git_command(["merge", "--abort"])
    
    return {
        "success": True,
        "source_branch": source_branch,
        "target_branch": target_branch,
        "has_conflicts": len(conflicts) > 0,
        "conflicts": conflicts,
        "conflict_count": len(conflicts),
        "message": f"发现 {len(conflicts)} 个冲突文件" if conflicts else "未发现冲突"
    }


def get_conflict_details(filename: str) -> Dict[str, Any]:
    """获取冲突文件的详细信息"""
    result = run_git_command(["diff", "--check", filename])
    
    return {
        "filename": filename,
        "markers": result["stdout"],
        "has_conflicts": bool(result["stdout"])
    }


def detect_file_conflicts() -> Dict[str, Any]:
    """检测当前工作区的冲突文件"""
    if not is_git_repo():
        return {"success": False, "error": "当前目录不是 Git 仓库"}
    
    status_result = run_git_command(["status", "--porcelain"])
    
    conflicts = []
    for line in status_result["stdout"].split('\n'):
        if not line:
            continue
        
        status = line[:2]
        filename = line[3:].strip()
        
        # 冲突状态标记
        if status in ['UU', 'AA', 'DD', 'AU', 'UA', 'UD', 'DU', 'DU']:
            conflicts.append({
                "filename": filename,
                "status": status,
                "description": get_conflict_status_description(status)
            })
    
    return {
        "success": True,
        "has_conflicts": len(conflicts) > 0,
        "conflicts": conflicts,
        "conflict_count": len(conflicts),
        "message": f"发现 {len(conflicts)} 个冲突文件" if conflicts else "未发现冲突"
    }


def get_conflict_status_description(status: str) -> str:
    """获取冲突状态描述"""
    descriptions = {
        'UU': '双方都修改了同一文件',
        'AA': '双方都添加了同名文件',
        'DD': '双方都删除了同一文件',
        'AU': '一方添加，另一方修改',
        'UA': '一方修改，另一方添加',
        'UD': '一方修改，另一方删除',
        'DU': '一方删除，另一方修改'
    }
    return descriptions.get(status, '未知冲突类型')


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="冲突检测器")
    parser.add_argument("--target-branch", help="目标分支")
    parser.add_argument("--source-branch", help="源分支（可选）")
    parser.add_argument("--check-current", action="store_true",
                       help="检查当前工作区的冲突")
    parser.add_argument("--output", choices=["json", "text"], default="json",
                       help="输出格式（默认：json）")
    
    args = parser.parse_args()
    
    # 执行检测
    if args.check_current:
        result = detect_file_conflicts()
    elif args.target_branch:
        result = check_merge_conflicts(args.target_branch, args.source_branch)
    else:
        print("错误: 请指定 --target-branch 或使用 --check-current", file=sys.stderr)
        sys.exit(1)
    
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
    
    lines = ["冲突检测结果", ""]
    
    if result.get("has_conflicts"):
        lines.append(f"状态: 发现 {result['conflict_count']} 个冲突文件")
        lines.append("")
        lines.append("冲突文件列表:")
        
        for conflict in result.get("conflicts", []):
            filename = conflict.get("filename", "")
            description = conflict.get("description", "")
            lines.append(f"  - {filename}: {description}")
        
        # 添加解决建议
        lines.append("")
        lines.append("解决建议:")
        lines.append("1. 手动编辑冲突文件，解决冲突标记")
        lines.append("2. 使用 'git add <file>' 标记为已解决")
        lines.append("3. 使用 'git commit' 完成合并")
    else:
        lines.append("状态: 未发现冲突 ✓")
    
    return "\n".join(lines)


if __name__ == "__main__":
    main()
