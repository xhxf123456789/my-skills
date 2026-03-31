---
name: project-scaffold
description: 多语言项目脚手架生成器；支持Python/Node.js/React等项目类型，自动生成标准目录结构、配置文件、README文档；当用户需要创建新项目或初始化项目结构时使用
---

# 项目脚手架生成器

## 任务目标
- 本 Skill 用于：快速生成标准项目结构
- 能力包含：目录结构生成、配置文件创建、README 模板、开发环境初始化
- 触发条件：用户请求"创建新项目"、"初始化项目结构"、"生成项目模板"

## 前置准备
- 依赖说明：仅使用 Python 标准库，无需额外安装
- 目标目录应不存在或为空

## 操作步骤

### 流程 A：创建新项目

**步骤1：选择项目类型**
- Python 项目：标准 Python 应用
- Node.js 项目：Node.js 后端应用
- React 项目：React 前端应用

**步骤2：生成项目结构**
```bash
python scripts/scaffold_generator.py --type python --name my-project --output ./my-project
```

**步骤3：初始化配置文件**
```bash
python scripts/config_initializer.py --type python --output ./my-project
```

### 流程 B：快速创建

**一键生成**：
```bash
# 交互式创建
python scripts/scaffold_generator.py --interactive

# 或指定所有参数
python scripts/scaffold_generator.py \
  --type python \
  --name my-project \
  --output ./my-project \
  --init-git \
  --init-config
```

## 资源索引
- 脚手架生成脚本：[scripts/scaffold_generator.py](scripts/scaffold_generator.py)（生成目录结构）
- 配置初始化脚本：[scripts/config_initializer.py](scripts/config_initializer.py)（生成配置文件）
- 项目模板：[assets/templates/](assets/templates/)（各类型项目模板）

## 支持的项目类型

### 1. Python 项目
```
my-project/
├── src/
│   └── myproject/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── docs/
│   └── README.md
├── requirements.txt
├── setup.py
├── .gitignore
└── README.md
```

### 2. Node.js 项目
```
my-project/
├── src/
│   └── index.js
├── tests/
│   └── index.test.js
├── package.json
├── .eslintrc
├── .gitignore
└── README.md
```

### 3. React 项目
```
my-project/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   ├── App.tsx
│   └── index.tsx
├── package.json
├── tsconfig.json
├── .eslintrc
├── .gitignore
└── README.md
```

## 注意事项
- 目标目录不应已存在重要文件
- 生成后需根据实际需求调整配置
- Python 项目建议先创建虚拟环境
- Node.js 项目需要运行 `npm install`

## 使用示例

### 示例1：创建 Python 项目
**用户请求**："创建一个名为 data-processor 的 Python 项目"

**执行步骤**：
```bash
python scripts/scaffold_generator.py \
  --type python \
  --name data-processor \
  --output ./data-processor
```

**输出**：
```
data-processor/
├── src/data_processor/
│   ├── __init__.py
│   └── main.py
├── tests/
├── requirements.txt
├── setup.py
└── README.md

✓ 项目结构已生成
✓ 配置文件已创建
✓ README 已生成
```

### 示例2：创建 React 项目
**用户请求**："创建一个 React 前端项目"

**执行步骤**：
```bash
python scripts/scaffold_generator.py \
  --type react \
  --name my-app \
  --output ./my-app
```

**输出**：
```
my-app/
├── public/
├── src/
│   ├── components/
│   ├── App.tsx
│   └── index.tsx
├── package.json
├── tsconfig.json
└── README.md

✓ 项目结构已生成
下一步：
1. cd my-app
2. npm install
3. npm start
```

### 示例3：交互式创建
**用户请求**："帮我创建一个新项目"

**执行步骤**：
```bash
python scripts/scaffold_generator.py --interactive
```

**交互流程**：
```
请选择项目类型：
1. Python
2. Node.js
3. React
选择 [1-3]: 1

项目名称: my-project
项目描述: 一个 Python 项目
作者: Your Name

✓ 配置完成，正在生成...
✓ 项目已创建: ./my-project
```

## 生成的文件说明

### README.md
- 项目名称和描述
- 安装指南
- 使用方法
- 开发指南
- 许可证

### requirements.txt / package.json
- 核心依赖
- 开发依赖
- 版本约束

### .gitignore
- Python/Node.js 标准忽略规则
- IDE 配置文件
- 系统文件

### 配置文件
- Python: setup.py, pyproject.toml
- Node.js: .eslintrc, .prettierrc
- React: tsconfig.json, webpack.config.js

## 自定义模板

可以通过修改 `assets/templates/` 下的模板文件来自定义生成内容：

- `python/`：Python 项目模板
- `nodejs/`：Node.js 项目模板
- `react/`：React 项目模板

模板文件支持变量替换：
- `{{PROJECT_NAME}}`：项目名称
- `{{PROJECT_DESCRIPTION}}`：项目描述
- `{{AUTHOR}}`：作者
- `{{YEAR}}`：当前年份
