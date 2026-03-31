# 项目模板资产

本目录包含各类项目的标准模板文件。

## 目录结构

```
templates/
├── python/          # Python 项目模板
├── nodejs/          # Node.js 项目模板
└── react/           # React 项目模板
```

## 使用说明

这些模板文件会被 `scaffold_generator.py` 脚本使用，生成标准项目结构。

### 模板变量

模板文件支持以下变量替换：

- `{{PROJECT_NAME}}` - 项目名称
- `{{PROJECT_DESCRIPTION}}` - 项目描述
- `{{AUTHOR}}` - 作者信息
- `{{YEAR}}` - 当前年份

### 自定义模板

您可以通过修改此目录下的文件来自定义生成的项目结构。

## Python 项目模板

### 目录结构
```
python/
├── src/
│   └── main.py
├── tests/
│   └── test_main.py
├── requirements.txt
├── setup.py
└── README.md
```

### 核心文件
- **requirements.txt** - Python 依赖
- **setup.py** - 包安装配置
- **README.md** - 项目说明文档

## Node.js 项目模板

### 目录结构
```
nodejs/
├── src/
│   └── index.js
├── tests/
├── package.json
└── README.md
```

### 核心文件
- **package.json** - Node.js 包配置
- **.eslintrc** - ESLint 配置
- **README.md** - 项目说明文档

## React 项目模板

### 目录结构
```
react/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   ├── App.tsx
│   └── index.tsx
├── package.json
├── tsconfig.json
└── README.md
```

### 核心文件
- **package.json** - React 项目配置
- **tsconfig.json** - TypeScript 配置
- **README.md** - 项目说明文档
