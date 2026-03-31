#!/usr/bin/env python3
"""
重复代码检测工具

功能：检测项目中的重复代码块
用途：识别需要重构的重复代码，提高代码复用性

使用方式：
    python duplicate_detector.py --path <目录> --min-lines 5 --min-similarity 0.8

参数说明：
    --path: 要分析的目录路径（必需）
    --min-lines: 最小重复行数阈值（默认：5）
    --min-similarity: 最小相似度阈值，范围 0-1（默认：0.8）
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from difflib import SequenceMatcher


def normalize_code(code: str) -> str:
    """
    规范化代码（移除空白字符、注释等）
    
    Args:
        code: 原始代码
    
    Returns:
        规范化后的代码
    """
    lines = []
    for line in code.split('\n'):
        # 移除前后空白
        stripped = line.strip()
        # 跳过空行和单行注释
        if stripped and not stripped.startswith('#'):
            lines.append(stripped)
    return '\n'.join(lines)


def calculate_similarity(code1: str, code2: str) -> float:
    """
    计算两段代码的相似度
    
    Args:
        code1: 第一段代码
        code2: 第二段代码
    
    Returns:
        相似度（0-1）
    """
    normalized1 = normalize_code(code1)
    normalized2 = normalize_code(code2)
    
    if not normalized1 or not normalized2:
        return 0.0
    
    return SequenceMatcher(None, normalized1, normalized2).ratio()


def extract_code_blocks(file_path: Path, min_lines: int = 5) -> List[Dict[str, Any]]:
    """
    从文件中提取代码块
    
    Args:
        file_path: 文件路径
        min_lines: 最小行数阈值
    
    Returns:
        代码块列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception:
        return []
    
    blocks = []
    current_block = []
    start_line = 1
    
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        
        # 跳过空行和注释
        if stripped and not stripped.startswith('#'):
            if not current_block:
                start_line = i
            current_block.append(line)
        else:
            # 当遇到空行或注释时，检查当前块是否足够长
            if len(current_block) >= min_lines:
                blocks.append({
                    "file": str(file_path),
                    "start_line": start_line,
                    "end_line": i - 1,
                    "code": ''.join(current_block),
                    "line_count": len(current_block)
                })
            current_block = []
    
    # 检查最后一个块
    if len(current_block) >= min_lines:
        blocks.append({
            "file": str(file_path),
            "start_line": start_line,
            "end_line": len(lines),
            "code": ''.join(current_block),
            "line_count": len(current_block)
        })
    
    return blocks


def find_duplicates(
    path: str, 
    min_lines: int = 5, 
    min_similarity: float = 0.8
) -> Dict[str, Any]:
    """
    查找重复代码
    
    Args:
        path: 目录路径
        min_lines: 最小重复行数
        min_similarity: 最小相似度
    
    Returns:
        重复代码报告
    """
    result = {
        "path": path,
        "min_lines": min_lines,
        "min_similarity": min_similarity,
        "duplicates": [],
        "summary": {
            "total_blocks": 0,
            "duplicate_groups": 0,
            "total_duplicate_lines": 0
        }
    }
    
    path_obj = Path(path)
    if not path_obj.is_dir():
        result["error"] = "路径必须是目录"
        return result
    
    # 收集所有代码块
    all_blocks = []
    python_files = list(path_obj.rglob("*.py"))
    
    for py_file in python_files:
        blocks = extract_code_blocks(py_file, min_lines)
        all_blocks.extend(blocks)
    
    result["summary"]["total_blocks"] = len(all_blocks)
    
    # 查找相似代码块
    checked = set()
    duplicate_groups = []
    
    for i, block1 in enumerate(all_blocks):
        if i in checked:
            continue
        
        similar_blocks = [block1]
        
        for j, block2 in enumerate(all_blocks[i+1:], start=i+1):
            if j in checked:
                continue
            
            # 确保来自不同文件
            if block1["file"] == block2["file"]:
                continue
            
            similarity = calculate_similarity(block1["code"], block2["code"])
            
            if similarity >= min_similarity:
                similar_blocks.append(block2)
                checked.add(j)
        
        if len(similar_blocks) > 1:
            duplicate_groups.append({
                "similarity": calculate_similarity(similar_blocks[0]["code"], similar_blocks[1]["code"]),
                "blocks": similar_blocks,
                "total_lines": sum(b["line_count"] for b in similar_blocks)
            })
            checked.add(i)
    
    # 按相似度排序
    duplicate_groups.sort(key=lambda x: x["similarity"], reverse=True)
    
    result["duplicates"] = duplicate_groups
    result["summary"]["duplicate_groups"] = len(duplicate_groups)
    result["summary"]["total_duplicate_lines"] = sum(g["total_lines"] for g in duplicate_groups)
    
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
    
    lines = [f"重复代码检测: {result['path']}", ""]
    lines.append(f"最小行数阈值: {result['min_lines']}")
    lines.append(f"最小相似度: {result['min_similarity']}")
    lines.append("")
    
    lines.append("统计信息:")
    lines.append(f"  代码块总数: {result['summary']['total_blocks']}")
    lines.append(f"  重复组数: {result['summary']['duplicate_groups']}")
    lines.append(f"  重复代码总行数: {result['summary']['total_duplicate_lines']}")
    lines.append("")
    
    if result['duplicates']:
        lines.append("重复代码详情:")
        for i, group in enumerate(result['duplicates'], start=1):
            lines.append(f"\n  重复组 {i} (相似度: {group['similarity']:.2%}):")
            for block in group['blocks']:
                lines.append(
                    f"    - {Path(block['file']).name}: 行 {block['start_line']}-{block['end_line']} "
                    f"({block['line_count']} 行)"
                )
    
    return "\n".join(lines)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="重复代码检测工具")
    parser.add_argument("--path", required=True, help="要分析的目录路径")
    parser.add_argument("--min-lines", type=int, default=5,
                       help="最小重复行数阈值（默认：5）")
    parser.add_argument("--min-similarity", type=float, default=0.8,
                       help="最小相似度阈值（默认：0.8）")
    parser.add_argument("--output", choices=["json", "text"], default="json",
                       help="输出格式（默认：json）")
    
    args = parser.parse_args()
    
    # 验证路径存在
    if not Path(args.path).exists():
        print(f"错误: 路径不存在: {args.path}", file=sys.stderr)
        sys.exit(1)
    
    # 验证参数范围
    if not 0 <= args.min_similarity <= 1:
        print("错误: 相似度阈值必须在 0-1 之间", file=sys.stderr)
        sys.exit(1)
    
    # 执行分析
    result = find_duplicates(args.path, args.min_lines, args.min_similarity)
    
    # 输出结果
    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_text_output(result))


if __name__ == "__main__":
    main()
