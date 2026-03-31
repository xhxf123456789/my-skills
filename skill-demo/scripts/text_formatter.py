#!/usr/bin/env python3
"""
文本格式化工具 - Skill 脚本示例

功能：演示 Skill 中脚本的标准实现方式
用途：将输入文本转换为指定格式（uppercase/lowercase/title）

使用方式：
    python text_formatter.py --input "文本内容" --format uppercase

参数说明：
    --input: 要格式化的文本内容（必需）
    --format: 格式类型，可选值：uppercase/lowercase/title（必需）
"""

import argparse
import sys


def format_text(text: str, format_type: str) -> str:
    """
    格式化文本
    
    Args:
        text: 输入文本
        format_type: 格式类型（uppercase/lowercase/title）
    
    Returns:
        格式化后的文本
    
    Raises:
        ValueError: 不支持的格式类型
    """
    if format_type == "uppercase":
        return text.upper()
    elif format_type == "lowercase":
        return text.lower()
    elif format_type == "title":
        return text.title()
    else:
        raise ValueError(f"不支持的格式类型: {format_type}，请使用 uppercase/lowercase/title")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="文本格式化工具")
    parser.add_argument("--input", required=True, help="要格式化的文本内容")
    parser.add_argument("--format", required=True, 
                       choices=["uppercase", "lowercase", "title"],
                       help="格式类型：uppercase/lowercase/title")
    
    args = parser.parse_args()
    
    try:
        result = format_text(args.input, args.format)
        print(result)
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
