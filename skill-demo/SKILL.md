---
name: skill-demo
description: 展示Skill的核心实现机制与标准结构；当用户需要了解Skill如何实现、Skill结构规范或创建Skill示例时使用
---

# Skill 实现机制演示

## 任务目标
- 本 Skill 用于：演示 Skill 的标准实现方式和核心组件
- 能力包含：展示目录结构、SKILL.md 规范、脚本调用方式、参考文档使用
- 触发条件：用户询问"Skill 如何实现"、"Skill 结构"、"创建 Skill 示例"

## 前置准备
- 无特殊依赖
- 本 Skill 为演示用途，所有组件均为示例

## Skill 核心实现机制

### 1. 目录结构（必需）
```
skill-demo/
├── SKILL.md           # 必需：入口文档，包含 YAML 前言区和 Markdown 正文
├── scripts/           # 可选：可执行脚本
├── references/        # 可选：参考文档
└── assets/            # 可选：静态资源
```

### 2. SKILL.md 结构（必需）
- **YAML 前言区**：定义元数据（name、description、dependency）
- **Markdown 正文**：提供执行指导和资源索引

### 3. 实现方式选择原则
- **使用脚本**：文件格式处理、API 调用、复杂计算、系统级操作
- **使用自然语言指导**：内容创作、分析推理、知识咨询、多模态任务

### 4. 脚本调用示例
调用 `scripts/text_formatter.py` 处理文本格式化任务：
```bash
python scripts/text_formatter.py --input "输入文本" --format uppercase
```

### 5. 参考文档使用
当需要了解输入格式规范时，读取 [references/input-format.md](references/input-format.md)

## 操作步骤
- 标准流程：
  1. 智能体加载 SKILL.md，读取前言区和正文指导
  2. 根据任务类型选择实现方式（脚本或自然语言指导）
  3. 若使用脚本，按参数要求调用；若使用自然语言指导，按文档描述执行
  4. 验证输出结果

## 资源索引
- 示例脚本：[scripts/text_formatter.py](scripts/text_formatter.py)（文本格式化工具）
- 输入规范：[references/input-format.md](references/input-format.md)（格式定义与示例）

## 注意事项
- Skill 是能力扩展包，不是独立应用程序
- 脚本应为纯函数式工具，不包含 web server 或交互式循环
- 充分利用智能体已有能力，避免重复建设

## 使用示例
**场景1：文本格式化**
- 功能：将文本转换为大写格式
- 执行方式：调用脚本 `scripts/text_formatter.py`
- 参数：`--input "hello world" --format uppercase`
- 输出：`HELLO WORLD`

**场景2：内容分析（自然语言指导）**
- 功能：分析文本情感
- 执行方式：智能体直接处理
- 指导：阅读文本，识别情感倾向（积极/消极/中性），提取关键词

**场景3：格式验证**
- 功能：验证输入是否符合规范
- 执行方式：读取 `references/input-format.md` 后验证
