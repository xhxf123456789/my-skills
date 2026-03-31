#!/usr/bin/env python3
"""
依赖解析器

功能：解析 Python 模块的 import 语句
用途：分析项目依赖关系、识别模块引用

使用方式：
    python dependency_parser.py --path ./myproject --exclude venv,tests

参数说明：
    --path: 项目路径（必需）
    --exclude: 排除目录（可选，逗号分隔）
"""

import argparse
import ast
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict


class DependencyParser:
    """依赖解析器"""
    
    def __init__(self, exclude_dirs: List[str] = None):
        """
        初始化
        
        Args:
            exclude_dirs: 要排除的目录列表
        """
        self.exclude_dirs = set(exclude_dirs or [])
        self.dependencies = defaultdict(set)
        self.reverse_dependencies = defaultdict(set)
        self.module_files = {}
    
    def parse_file(self, file_path: Path, project_root: Path) -> Set[str]:
        """
        解析单个文件的依赖
        
        Args:
            file_path: 文件路径
            project_root: 项目根目录
        
        Returns:
            依赖模块集合
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            imports = set()
            
            for node in ast.walk(tree):
                # 解析 import 语句
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                
                # 解析 from ... import 语句
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module = node.module.split('.')[0]
                        imports.add(module)
            
            # 过滤标准库和第三方库
            project_modules = set()
            for imp in imports:
                # 检查是否是项目内部模块
                module_path = project_root / imp.replace('.', os.sep)
                if module_path.exists() or (project_root / f"{imp}.py").exists():
                    project_modules.add(imp)
            
            return project_modules
        
        except Exception as e:
            print(f"警告: 无法解析文件 {file_path}: {e}", file=sys.stderr)
            return set()
    
    def parse_project(self, project_path: str) -> Dict[str, Any]:
        """
        解析整个项目的依赖
        
        Args:
            project_path: 项目路径
        
        Returns:
            依赖关系数据
        """
        project_root = Path(project_path)
        if not project_root.exists():
            return {"error": f"路径不存在: {project_path}"}
        
        # 收集所有 Python 文件
        python_files = []
        for py_file in project_root.rglob("*.py"):
            # 排除指定目录
            relative_path = py_file.relative_to(project_root)
            if not any(excluded in relative_path.parts for excluded in self.exclude_dirs):
                python_files.append(py_file)
        
        # 解析每个文件的依赖
        for py_file in python_files:
            relative_path = str(py_file.relative_to(project_root))
            
            # 获取模块名
            module_name = str(py_file.relative_to(project_root).with_suffix('')).replace(os.sep, '.')
            if module_name.endswith('.__init__'):
                module_name = module_name[:-9]
            
            self.module_files[module_name] = relative_path
            
            # 解析依赖
            imports = self.parse_file(py_file, project_root)
            if imports:
                self.dependencies[module_name] = imports
                
                # 构建反向依赖
                for imp in imports:
                    self.reverse_dependencies[imp].add(module_name)
        
        return {
            "project_path": project_path,
            "total_modules": len(self.module_files),
            "dependencies": {k: sorted(list(v)) for k, v in self.dependencies.items()},
            "reverse_dependencies": {k: sorted(list(v)) for k, v in self.reverse_dependencies.items()},
            "module_files": self.module_files
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="依赖解析器")
    parser.add_argument("--path", required=True, help="项目路径")
    parser.add_argument("--exclude", default="venv,env,node_modules,__pycache__,.git",
                       help="排除目录（逗号分隔）")
    parser.add_argument("--output", choices=["json", "text"], default="json",
                       help="输出格式（默认：json）")
    
    args = parser.parse_args()
    
    # 解析排除目录
    exclude_dirs = [d.strip() for d in args.exclude.split(',')]
    
    # 执行解析
    parser_instance = DependencyParser(exclude_dirs)
    result = parser_instance.parse_project(args.path)
    
    # 输出结果
    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"项目: {result['project_path']}")
        print(f"模块总数: {result['total_modules']}")
        print("\n依赖关系:")
        for module, deps in result['dependencies'].items():
            print(f"  {module}:")
            for dep in deps:
                print(f"    → {dep}")


if __name__ == "__main__":
    main()
