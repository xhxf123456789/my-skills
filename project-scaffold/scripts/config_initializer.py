#!/usr/bin/env python3
"""
配置初始化器

功能：生成项目配置文件
用途：创建各类配置文件（package.json、tsconfig.json 等）

使用方式：
    python config_initializer.py --type python --output ./my-project

参数说明：
    --type: 项目类型（python/nodejs/react）
    --output: 输出目录（必需）
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any


class ConfigInitializer:
    """配置初始化器"""
    
    def __init__(self, project_type: str, output_dir: str):
        """
        初始化
        
        Args:
            project_type: 项目类型
            output_dir: 输出目录
        """
        self.project_type = project_type
        self.output_dir = Path(output_dir)
        self.configs = self.get_configs(project_type)
    
    def get_configs(self, project_type: str) -> Dict[str, str]:
        """
        获取配置文件
        
        Args:
            project_type: 项目类型
        
        Returns:
            配置文件字典
        """
        configs = {
            "python": {
                "pyproject.toml": """[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-project"
version = "0.1.0"
description = "A Python project"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
requires-python = ">=3.8"

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=22.0.0",
    "pylint>=2.15.0",
]

[tool.black]
line-length = 100
target-version = ['py38']

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
""",
                ".prettierrc": """{
  "printWidth": 100,
  "tabWidth": 4,
  "useTabs": false,
  "semi": false,
  "singleQuote": true
}
""",
                ".editorconfig": """root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.py]
indent_style = space
indent_size = 4

[*.md]
trim_trailing_whitespace = false
"""
            },
            "nodejs": {
                ".prettierrc": json.dumps({
                    "semi": True,
                    "singleQuote": True,
                    "tabWidth": 2,
                    "printWidth": 100
                }, indent=2),
                ".editorconfig": """root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.js]
indent_style = space
indent_size = 2

[*.json]
indent_style = space
indent_size = 2
"""
            },
            "react": {
                ".prettierrc": json.dumps({
                    "semi": True,
                    "singleQuote": True,
                    "tabWidth": 2,
                    "printWidth": 100,
                    "trailingComma": "es5"
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
                "webpack.config.js": """const path = require('path');

module.exports = {
  entry: './src/index.tsx',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js',
  },
  module: {
    rules: [
      {
        test: /\\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
      {
        test: /\\.css$/,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
  },
  devServer: {
    contentBase: './dist',
  },
};
"""
            }
        }
        
        return configs.get(project_type, configs["python"])
    
    def initialize(self) -> Dict[str, Any]:
        """
        初始化配置文件
        
        Returns:
            初始化结果
        """
        if not self.output_dir.exists():
            return {
                "success": False,
                "error": f"目录不存在: {self.output_dir}"
            }
        
        created_files = []
        
        try:
            for filename, content in self.configs.items():
                file_path = self.output_dir / filename
                
                # 不覆盖已存在的文件
                if not file_path.exists():
                    file_path.write_text(content, encoding='utf-8')
                    created_files.append(filename)
            
            return {
                "success": True,
                "project_type": self.project_type,
                "output_dir": str(self.output_dir),
                "created_files": created_files,
                "message": f"已创建 {len(created_files)} 个配置文件"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"创建配置文件失败: {str(e)}"
            }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="配置初始化器")
    parser.add_argument("--type", choices=["python", "nodejs", "react"], default="python",
                       help="项目类型（默认：python）")
    parser.add_argument("--output", required=True, help="输出目录")
    
    args = parser.parse_args()
    
    # 初始化配置
    initializer = ConfigInitializer(args.type, args.output)
    result = initializer.initialize()
    
    # 输出结果
    if result["success"]:
        print(f"✓ {result['message']}")
        if result['created_files']:
            print("\n创建的配置文件:")
            for filename in result['created_files']:
                print(f"  - {filename}")
    else:
        print(f"错误: {result['error']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
