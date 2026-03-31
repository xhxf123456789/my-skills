#!/usr/bin/env python3
"""
循环依赖检测器

功能：检测 Python 项目中的循环依赖
用途：识别可能导致问题的循环引用

使用方式：
    python cycle_detector.py --dependency-data dependencies.json

参数说明：
    --dependency-data: 依赖关系数据文件（必需）
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict


class CycleDetector:
    """循环依赖检测器"""
    
    def __init__(self, dependencies: Dict[str, List[str]]):
        """
        初始化
        
        Args:
            dependencies: 依赖关系字典
        """
        self.dependencies = defaultdict(set)
        for module, deps in dependencies.items():
            self.dependencies[module] = set(deps)
    
    def find_cycles(self) -> List[List[str]]:
        """
        查找所有循环依赖
        
        Returns:
            循环依赖路径列表
        """
        cycles = []
        visited = set()
        rec_stack = []
        rec_stack_set = set()
        
        def dfs(node: str):
            """深度优先搜索"""
            visited.add(node)
            rec_stack.append(node)
            rec_stack_set.add(node)
            
            for neighbor in self.dependencies.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack_set:
                    # 找到循环
                    cycle_start = rec_stack.index(neighbor)
                    cycle = rec_stack[cycle_start:] + [neighbor]
                    cycles.append(cycle)
            
            rec_stack.pop()
            rec_stack_set.remove(node)
        
        # 遍历所有节点
        for node in list(self.dependencies.keys()):
            if node not in visited:
                dfs(node)
        
        return cycles
    
    def get_modules_with_cycles(self) -> Set[str]:
        """
        获取所有参与循环的模块
        
        Returns:
            参与循环的模块集合
        """
        cycles = self.find_cycles()
        modules = set()
        for cycle in cycles:
            modules.update(cycle)
        return modules


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="循环依赖检测器")
    parser.add_argument("--dependency-data", required=True, help="依赖关系数据文件")
    parser.add_argument("--output", choices=["json", "text"], default="json",
                       help="输出格式（默认：json）")
    
    args = parser.parse_args()
    
    # 读取依赖数据
    data_file = Path(args.dependency_data)
    if not data_file.exists():
        print(f"错误: 文件不存在: {args.dependency_data}", file=sys.stderr)
        sys.exit(1)
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    dependencies = data.get("dependencies", {})
    
    # 执行检测
    detector = CycleDetector(dependencies)
    cycles = detector.find_cycles()
    modules_with_cycles = detector.get_modules_with_cycles()
    
    result = {
        "has_cycles": len(cycles) > 0,
        "cycle_count": len(cycles),
        "cycles": cycles,
        "modules_with_cycles": sorted(list(modules_with_cycles)),
        "message": f"发现 {len(cycles)} 个循环依赖" if cycles else "未发现循环依赖"
    }
    
    # 输出结果
    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"循环依赖检测: {result['message']}")
        print()
        
        if cycles:
            print("循环依赖详情:")
            for i, cycle in enumerate(cycles, 1):
                cycle_str = " → ".join(cycle)
                print(f"  {i}. {cycle_str}")
                print()
        else:
            print("✓ 未发现循环依赖")
        
        if modules_with_cycles:
            print(f"\n涉及模块 ({len(modules_with_cycles)} 个):")
            for module in sorted(modules_with_cycles):
                print(f"  - {module}")


if __name__ == "__main__":
    main()
