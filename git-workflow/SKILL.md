---
name: git-workflow
description: Git操作流程管理与智能提交信息生成；提供分支管理、代码变更分析、冲突检测、提交信息生成；当用户需要生成提交信息、管理分支、分析变更或检测冲突时使用
---

# Git 工作流管理器

## 任务目标
- 本 Skill 用于：Git 操作流程管理与智能提交信息生成
- 能力包含：分支管理、代码变更分析、冲突检测、提交信息生成
- 触发条件：用户请求"生成提交信息"、"管理分支"、"分析代码变更"、"检测冲突"

## 前置准备
- 依赖说明：Git 命令行工具（系统级依赖）
- 当前工作目录必须是一个 Git 仓库

## 操作步骤

### 流程 A：生成提交信息（智能体执行）

**步骤1：分析代码变更**
```bash
python scripts/change_analyzer.py --range staged
```

**步骤2：智能体生成提交信息**
基于变更分析结果，智能体生成符合规范的提交信息：

1. **分析变更类型**：
   - 新功能：`feat:`
   - 修复 Bug：`fix:`
   - 文档更新：`docs:`
   - 代码重构：`refactor:`
   - 性能优化：`perf:`
   - 测试相关：`test:`
   - 构建/工具：`chore:`

2. **生成提交信息**：
```
<type>(<scope>): <subject>

<body>

<footer>
```

**步骤3：执行提交**
```bash
python scripts/git_operations.py --action commit --message "生成的提交信息"
```

### 流程 B：分支管理

**创建新分支**：
```bash
python scripts/branch_manager.py --branch feature/new-feature --action create
```

**切换分支**：
```bash
python scripts/branch_manager.py --branch develop --action switch
```

**合并分支**：
```bash
python scripts/branch_manager.py --branch feature/new-feature --action merge
```

**删除分支**：
```bash
python scripts/branch_manager.py --branch old-feature --action delete
```

### 流程 C：代码变更分析

**分析暂存区变更**：
```bash
python scripts/change_analyzer.py --range staged
```

**分析最近 N 次提交**：
```bash
python scripts/change_analyzer.py --range last-n --count 5
```

**分析两个分支差异**：
```bash
python scripts/change_analyzer.py --range branches --base main --target feature
```

### 流程 D：冲突检测

**检测与目标分支的冲突**：
```bash
python scripts/conflict_detector.py --target-branch main
```

## 资源索引
- Git 操作脚本：[scripts/git_operations.py](scripts/git_operations.py)（封装 Git 命令）
- 变更分析脚本：[scripts/change_analyzer.py](scripts/change_analyzer.py)（分析代码变更）
- 分支管理脚本：[scripts/branch_manager.py](scripts/branch_manager.py)（管理分支）
- 冲突检测脚本：[scripts/conflict_detector.py](scripts/conflict_detector.py)（检测合并冲突）
- 提交规范：[references/commit-conventions.md](references/commit-conventions.md)（提交信息规范）
- 分支策略：[references/branching-strategy.md](references/branching-strategy.md)（分支管理策略）

## 注意事项
- 提交信息生成由智能体完成，确保语义准确
- Git 操作执行前会进行安全检查
- 分支合并前建议先检测冲突
- 遵循团队的分支管理策略
- 提交信息必须符合规范（参考 commit-conventions.md）

## 使用示例

### 示例1：生成提交信息
**用户请求**："生成提交信息"

**智能体执行**：
1. 调用 `change_analyzer.py` 分析暂存区变更
2. 分析变更类型（新增功能/修复 Bug/重构等）
3. 生成提交信息：
   ```
   feat: 添加用户登录功能
   
   - 实现用户登录接口
   - 添加 JWT 认证
   - 编写单元测试
   ```
4. 调用 `git_operations.py` 执行提交

### 示例2：创建功能分支
**用户请求**："创建一个新分支开发用户管理功能"

**执行步骤**：
```bash
# 1. 创建分支
python scripts/branch_manager.py --branch feature/user-management --action create

# 2. 切换到新分支
python scripts/branch_manager.py --branch feature/user-management --action switch
```

### 示例3：合并前检测冲突
**用户请求**："合并前检测是否有冲突"

**执行步骤**：
```bash
# 1. 检测冲突
python scripts/conflict_detector.py --target-branch develop

# 2. 如果无冲突，执行合并
python scripts/branch_manager.py --branch feature/user-management --action merge
```

### 示例4：查看代码变更
**用户请求**："查看最近的代码变更"

**执行步骤**：
```bash
# 分析最近 5 次提交
python scripts/change_analyzer.py --range last-n --count 5
```

## 提交信息生成指南

### 提交信息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### 类型说明
| 类型 | 说明 | 示例 |
|-----|------|------|
| feat | 新功能 | feat: 添加用户登录功能 |
| fix | 修复 Bug | fix: 修复登录验证错误 |
| docs | 文档更新 | docs: 更新 API 文档 |
| refactor | 代码重构 | refactor: 重构用户模块 |
| perf | 性能优化 | perf: 优化查询性能 |
| test | 测试相关 | test: 添加单元测试 |
| chore | 构建/工具 | chore: 更新依赖版本 |

### 最佳实践
1. **使用祈使语气**：使用 "添加" 而不是 "添加了"
2. **首字母小写**：subject 首字母小写
3. **限制长度**：subject 不超过 50 字符
4. **说明原因**：body 说明变更原因和影响
5. **关联 Issue**：footer 关联相关 Issue

详见 [references/commit-conventions.md](references/commit-conventions.md)
