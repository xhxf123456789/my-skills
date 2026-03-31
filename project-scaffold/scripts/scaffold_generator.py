#!/usr/bin/env python3
"""
项目脚手架生成器

功能：生成标准项目结构
用途：快速创建新项目，包含目录结构和基础文件

使用方式：
    python scaffold_generator.py --type python --name my-project --output ./my-project

参数说明：
    --type: 项目类型（python/nodejs/react）
    --name: 项目名称（必需）
    --output: 输出目录（默认：当前目录）
    --interactive: 交互式模式
    --init-git: 初始化 Git 仓库
    --init-config: 生成配置文件
"""

import argparse
import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ScaffoldGenerator:
    """脚手架生成器"""
    
    def __init__(self, project_type: str, project_name: str, output_dir: str):
        """
        初始化
        
        Args:
            project_type: 项目类型
            project_name: 项目名称
            output_dir: 输出目录
        """
        self.project_type = project_type
        self.project_name = project_name
        self.output_dir = Path(output_dir)
        self.project_dir = self.output_dir / self.project_name
        
        self.structure = self.get_structure(project_type)
        self.templates = self.get_templates(project_type)
    
    def get_structure(self, project_type: str) -> Dict[str, List[str]]:
        """
        获取项目结构
        
        Args:
            project_type: 项目类型
        
        Returns:
            目录结构字典
        """
        structures = {
            "python": {
                "directories": [
                    "src/{project_name}",
                    "tests",
                    "docs",
                    "scripts"
                ],
                "files": [
                    "src/{project_name}/__init__.py",
                    "src/{project_name}/main.py",
                    "tests/__init__.py",
                    "tests/test_main.py",
                    ".gitignore",
                    "README.md",
                    "requirements.txt",
                    "setup.py"
                ]
            },
            "nodejs": {
                "directories": [
                    "src",
                    "tests",
                    "lib"
                ],
                "files": [
                    "src/index.js",
                    "tests/index.test.js",
                    ".gitignore",
                    "README.md",
                    "package.json",
                    ".eslintrc"
                ]
            },
            "react": {
                "directories": [
                    "public",
                    "src/components",
                    "src/pages",
                    "src/utils",
                    "src/assets"
                ],
                "files": [
                    "public/index.html",
                    "src/index.tsx",
                    "src/App.tsx",
                    "src/App.css",
                    ".gitignore",
                    "README.md",
                    "package.json",
                    "tsconfig.json",
                    ".eslintrc"
                ]
            }
        }
        
        return structures.get(project_type, structures["python"])
    
    def get_templates(self, project_type: str) -> Dict[str, str]:
        """
        获取文件模板
        
        Args:
            project_type: 项目类型
        
        Returns:
            模板字典
        """
        year = datetime.now().year
        
        templates = {
            "python": {
                "README.md": f"""# {self.project_name}

## 简介

{self.project_name} 是一个 Python 项目。

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
python -m {self.project_name}
```

## 开发

```bash
# 安装开发依赖
pip install -r requirements.txt

# 运行测试
pytest tests/

# 代码格式化
black src/
```

## 许可证

MIT License

Copyright (c) {year}
""",
                "requirements.txt": """# 核心依赖
requests>=2.28.0

# 开发依赖
pytest>=7.0.0
black>=22.0.0
pylint>=2.15.0
""",
                "setup.py": f"""from setuptools import setup, find_packages

setup(
    name="{self.project_name}",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={{"": "src"}},
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={{
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "pylint>=2.15.0",
        ]
    }},
)
""",
                "src/{project_name}/main.py": '''"""主模块"""


def main():
    """主函数"""
    print("Hello, World!")


if __name__ == "__main__":
    main()
''',
                ".gitignore": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Tests
.pytest_cache/
.coverage
htmlcov/
"""
            },
            "nodejs": {
                "package.json": json.dumps({
                    "name": self.project_name,
                    "version": "1.0.0",
                    "description": "A Node.js project",
                    "main": "src/index.js",
                    "scripts": {
                        "start": "node src/index.js",
                        "test": "jest",
                        "lint": "eslint src/"
                    },
                    "keywords": [],
                    "author": "",
                    "license": "MIT",
                    "dependencies": {},
                    "devDependencies": {
                        "jest": "^29.0.0",
                        "eslint": "^8.0.0"
                    }
                }, indent=2),
                ".eslintrc": json.dumps({
                    "env": {
                        "node": True,
                        "es2021": True
                    },
                    "extends": "eslint:recommended",
                    "parserOptions": {
                        "ecmaVersion": "latest",
                        "sourceType": "module"
                    }
                }, indent=2),
                "README.md": f"""# {self.project_name}

## 安装

```bash
npm install
```

## 使用

```bash
npm start
```

## 开发

```bash
# 运行测试
npm test

# 代码检查
npm run lint
```

## 许可证

MIT
""",
                "src/index.js": """/**
 * 主模块
 */

function main() {
  console.log('Hello, World!');
}

main();

module.exports = { main };
""",
                ".gitignore": """# Dependencies
node_modules/

# Build
dist/
build/

# Logs
*.log
npm-debug.log*

# Environment
.env
.env.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
"""
            },
            "react": {
                "package.json": json.dumps({
                    "name": self.project_name,
                    "version": "1.0.0",
                    "private": True,
                    "dependencies": {
                        "react": "^18.0.0",
                        "react-dom": "^18.0.0",
                        "react-scripts": "5.0.0"
                    },
                    "devDependencies": {
                        "@types/react": "^18.0.0",
                        "@types/react-dom": "^18.0.0",
                        "typescript": "^5.0.0",
                        "eslint": "^8.0.0"
                    },
                    "scripts": {
                        "start": "react-scripts start",
                        "build": "react-scripts build",
                        "test": "react-scripts test",
                        "eject": "react-scripts eject"
                    }
                }, indent=2),
                "tsconfig.json": json.dumps({
                    "compilerOptions": {
                        "target": "ES2020",
                        "lib": ["dom", "dom.iterable", "esnext"],
                        "allowJs": True,
                        "skipLibCheck": True,
                        "esModuleInterop": True,
                        "allowSyntheticDefaultImports": True,
                        "strict": True,
                        "forceConsistentCasingInFileNames": True,
                        "module": "esnext",
                        "moduleResolution": "node",
                        "resolveJsonModule": True,
                        "isolatedModules": True,
                        "jsx": "react-jsx"
                    },
                    "include": ["src"]
                }, indent=2),
                "README.md": f"""# {self.project_name}

## 安装

```bash
npm install
```

## 开发

```bash
npm start
```

## 构建

```bash
npm run build
```

## 测试

```bash
npm test
```

## 许可证

MIT
""",
                "public/index.html": f"""<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{self.project_name}</title>
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
""",
                "src/index.tsx": """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
""",
                "src/App.tsx": """import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header>
        <h1>Welcome to React</h1>
      </header>
    </div>
  );
}

export default App;
""",
                ".gitignore": """# Dependencies
node_modules/

# Build
build/
dist/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Testing
coverage/
"""
            }
        }
        
        return templates.get(project_type, templates["python"])
    
    def generate(self) -> Dict[str, Any]:
        """
        生成项目结构
        
        Returns:
            生成结果
        """
        if self.project_dir.exists():
            return {
                "success": False,
                "error": f"目录已存在: {self.project_dir}"
            }
        
        created_dirs = []
        created_files = []
        
        try:
            # 创建目录
            for dir_path in self.structure.get("directories", []):
                full_path = self.project_dir / dir_path.format(project_name=self.project_name)
                full_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(str(full_path.relative_to(self.output_dir)))
            
            # 创建文件
            for file_path in self.structure.get("files", []):
                formatted_path = file_path.format(project_name=self.project_name)
                full_path = self.project_dir / formatted_path
                
                # 获取模板内容
                template_key = file_path.split('/')[-1]  # 取文件名
                content = self.templates.get(template_key, "")
                
                # 特殊处理路径模板
                if file_path in self.templates:
                    content = self.templates[file_path]
                else:
                    content = self.templates.get(template_key, "")
                
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding='utf-8')
                created_files.append(str(full_path.relative_to(self.output_dir)))
            
            return {
                "success": True,
                "project_path": str(self.project_dir),
                "project_type": self.project_type,
                "project_name": self.project_name,
                "created_directories": created_dirs,
                "created_files": created_files,
                "message": f"项目 {self.project_name} 已创建"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"创建项目失败: {str(e)}"
            }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="项目脚手架生成器")
    parser.add_argument("--type", choices=["python", "nodejs", "react"], default="python",
                       help="项目类型（默认：python）")
    parser.add_argument("--name", help="项目名称")
    parser.add_argument("--output", default=".", help="输出目录（默认：当前目录）")
    parser.add_argument("--interactive", action="store_true", help="交互式模式")
    parser.add_argument("--init-git", action="store_true", help="初始化 Git 仓库")
    parser.add_argument("--init-config", action="store_true", help="生成配置文件")
    
    args = parser.parse_args()
    
    project_name = args.name
    project_type = args.type
    
    # 交互式模式
    if args.interactive:
        print("请选择项目类型：")
        print("1. Python")
        print("2. Node.js")
        print("3. React")
        choice = input("选择 [1-3]: ").strip()
        
        type_map = {"1": "python", "2": "nodejs", "3": "react"}
        project_type = type_map.get(choice, "python")
        
        project_name = input("项目名称: ").strip()
    
    if not project_name:
        print("错误: 请提供项目名称", file=sys.stderr)
        sys.exit(1)
    
    # 生成项目
    generator = ScaffoldGenerator(project_type, project_name, args.output)
    result = generator.generate()
    
    # 输出结果
    if result["success"]:
        print(f"\n✓ {result['message']}")
        print(f"\n项目路径: {result['project_path']}")
        print(f"项目类型: {result['project_type']}")
        print(f"\n创建的目录 ({len(result['created_directories'])} 个):")
        for dir_path in result['created_directories'][:5]:
            print(f"  - {dir_path}")
        
        print(f"\n创建的文件 ({len(result['created_files'])} 个):")
        for file_path in result['created_files'][:5]:
            print(f"  - {file_path}")
        
        print(f"\n下一步:")
        if project_type == "python":
            print(f"  cd {project_name}")
            print("  python -m venv venv")
            print("  source venv/bin/activate  # Linux/Mac")
            print("  pip install -r requirements.txt")
        elif project_type in ["nodejs", "react"]:
            print(f"  cd {project_name}")
            print("  npm install")
            print("  npm start")
    else:
        print(f"错误: {result['error']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
