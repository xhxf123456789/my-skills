# 提交规范

## 目录
- [概览](#概览)
- [提交信息格式](#提交信息格式)
- [类型说明](#类型说明)
- [作用域](#作用域)
- [最佳实践](#最佳实践)
- [示例](#示例)

## 概览
本文档定义了 Git 提交信息的标准格式和最佳实践，确保提交历史清晰、可读、易于追溯。

## 提交信息格式

### 基本格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### 格式说明
- **type**（必需）：提交类型
- **scope**（可选）：影响范围
- **subject**（必需）：简短描述
- **body**（可选）：详细描述
- **footer**（可选）：页脚信息

## 类型说明

### 主要类型

| 类型 | 说明 | 示例 |
|-----|------|------|
| **feat** | 新功能 | feat: 添加用户登录功能 |
| **fix** | 修复 Bug | fix: 修复登录验证错误 |
| **docs** | 文档更新 | docs: 更新 API 文档 |
| **refactor** | 代码重构 | refactor: 重构用户模块 |
| **perf** | 性能优化 | perf: 优化查询性能 |
| **test** | 测试相关 | test: 添加单元测试 |
| **chore** | 构建/工具 | chore: 更新依赖版本 |
| **style** | 代码格式 | style: 格式化代码 |
| **ci** | CI/CD 相关 | ci: 更新构建配置 |
| **revert** | 回滚提交 | revert: 回滚用户登录功能 |

### 类型选择指南

**何时使用 feat**：
- 新增功能模块
- 添加新的 API 接口
- 实现新的业务逻辑

**何时使用 fix**：
- 修复 Bug
- 修正错误行为
- 解决已知问题

**何时使用 refactor**：
- 代码结构优化
- 变量/函数重命名
- 提取公共方法

**何时使用 perf**：
- 性能优化
- 减少资源消耗
- 提升响应速度

## 作用域

### 常见作用域

| 作用域 | 说明 | 示例 |
|-------|------|------|
| api | API 相关 | feat(api): 添加用户接口 |
| ui | 界面相关 | fix(ui): 修复按钮样式 |
| db | 数据库相关 | refactor(db): 优化查询语句 |
| auth | 认证相关 | feat(auth): 添加 JWT 认证 |
| config | 配置相关 | chore(config): 更新配置文件 |
| utils | 工具类 | refactor(utils): 提取公共方法 |

### 作用域命名规范
- 使用小写字母
- 使用连字符分隔
- 保持简洁明了
- 反映影响的模块

## 最佳实践

### 1. 使用祈使语气

✅ **正确**：
```
feat: 添加用户登录功能
fix: 修复登录验证错误
refactor: 重构用户模块
```

❌ **错误**：
```
feat: 添加了用户登录功能
fix: 修复了登录验证错误
refactor: 重构了用户模块
```

### 2. 首字母小写

✅ **正确**：
```
feat: add user login feature
```

❌ **错误**：
```
feat: Add user login feature
```

### 3. 限制长度

- **subject**：不超过 50 字符
- **body**：每行不超过 72 字符

### 4. 说明原因

在 body 中说明：
- **为什么**做这个变更
- **做了什么**变更
- **有什么影响**

### 5. 关联 Issue

在 footer 中关联：
```
Closes #123
Related #456
```

### 6. 破坏性变更

标记破坏性变更：
```
feat: 重构用户认证系统

BREAKING CHANGE: 
- 旧的认证接口已废弃
- 需要迁移到新的认证方式

Migration Guide:
1. 更新配置文件
2. 调用新的认证接口
```

## 示例

### 示例1：新功能
```
feat(auth): 添加 JWT 认证功能

- 实现 JWT token 生成和验证
- 添加登录接口
- 编写单元测试

Closes #123
```

### 示例2：Bug 修复
```
fix(api): 修复用户查询接口的分页问题

问题：当页码为 0 时，返回错误的数据
解决：添加页码校验，默认从第 1 页开始

Fixes #456
```

### 示例3：重构
```
refactor(user): 重构用户模块代码结构

- 提取用户服务类
- 分离数据访问层
- 优化代码可读性

无功能变更
```

### 示例4：性能优化
```
perf(db): 优化用户查询性能

- 添加数据库索引
- 优化查询语句
- 实现缓存机制

性能提升约 50%
```

### 示例5：文档更新
```
docs(api): 更新用户接口文档

- 添加认证说明
- 更新请求示例
- 补充错误码说明
```

### 示例6：破坏性变更
```
feat(api): 重构用户接口

- 统一响应格式
- 更新错误码体系

BREAKING CHANGE: 
响应格式已变更，需要客户端同步更新

旧格式：
{
  "code": 0,
  "data": {}
}

新格式：
{
  "success": true,
  "data": {},
  "message": ""
}
```

## 提交模板

### Git 配置
```bash
# 配置提交模板
git config --global commit.template ~/.gitmessage

# 创建模板文件
cat > ~/.gitmessage << 'EOF'
<type>(<scope>): <subject>

<body>

<footer>
EOF
```

### 使用模板
```bash
# 使用模板编辑提交信息
git commit
```

## 工具集成

### commitlint
```bash
# 安装 commitlint
npm install -g @commitlint/cli @commitlint/config-conventional

# 配置规则
echo "module.exports = {extends: ['@commitlint/config-conventional']}" > commitlint.config.js

# 使用
commitlint --edit
```

### Git Hooks
```bash
# .git/hooks/commit-msg
#!/bin/sh
# 验证提交信息格式
commit_regex='^(feat|fix|docs|refactor|perf|test|chore|style|ci|revert)(\(.+\))?: .{1,50}'

if ! grep -qE "$commit_regex" "$1"; then
    echo "提交信息格式错误！"
    echo "格式：<type>(<scope>): <subject>"
    exit 1
fi
```

## 常见问题

### Q1: 提交信息太长怎么办？
**A**: 使用 body 详细说明，subject 保持简洁。

### Q2: 一个提交包含多个类型怎么办？
**A**: 拆分为多个提交，每个提交只做一件事。

### Q3: 如何处理紧急修复？
**A**: 使用 `fix` 类型，在 body 中说明紧急性。

### Q4: 临时提交怎么办？
**A**: 使用 `chore` 或 `wip` 标记，后续整理后删除。

## 团队规范

### 提交前检查
- [ ] 提交信息格式正确
- [ ] 类型选择准确
- [ ] subject 长度合规
- [ ] body 说明清晰
- [ ] 关联相关 Issue

### 代码审查要点
- [ ] 提交信息是否清晰
- [ ] 是否符合规范
- [ ] 是否需要拆分
- [ ] 是否关联 Issue
