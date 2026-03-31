# 分支策略

## 目录
- [概览](#概览)
- [分支类型](#分支类型)
- [工作流程](#工作流程)
- [分支命名规范](#分支命名规范)
- [合并策略](#合并策略)
- [最佳实践](#最佳实践)

## 概览
本文档定义了 Git 分支管理的标准策略，确保团队协作高效、代码质量可控。

## 分支类型

### 主要分支

#### main/master 分支
- **用途**：生产环境代码
- **特点**：
  - 始终保持可部署状态
  - 受保护，禁止直接提交
  - 所有发布都从这里发布
- **命名**：`main` 或 `master`
- **保护规则**：
  - 必须通过 Pull Request 合并
  - 至少 1 人审核
  - 通过所有自动化测试

#### develop 分支
- **用途**：开发主分支
- **特点**：
  - 集成所有功能分支
  - 下一个版本的代码
  - 可能有未发布的功能
- **命名**：`develop`
- **合并规则**：
  - 从 feature 分支合并
  - 定期合并到 main

### 辅助分支

#### feature 分支
- **用途**：开发新功能
- **特点**：
  - 从 develop 创建
  - 合并回 develop
  - 完成后删除
- **命名**：`feature/<feature-name>`
- **示例**：
  ```
  feature/user-authentication
  feature/payment-system
  feature/dashboard-ui
  ```

#### release 分支
- **用途**：准备发布
- **特点**：
  - 从 develop 创建
  - 合并到 main 和 develop
  - 只做 Bug 修复和文档更新
- **命名**：`release/<version>`
- **示例**：
  ```
  release/1.0.0
  release/2.1.0
  ```

#### hotfix 分支
- **用途**：紧急修复生产问题
- **特点**：
  - 从 main 创建
  - 合并到 main 和 develop
  - 修复完成后立即删除
- **命名**：`hotfix/<issue-description>`
- **示例**：
  ```
  hotfix/login-error
  hotfix/security-patch
  ```

#### bugfix 分支
- **用途**：修复开发中的 Bug
- **特点**：
  - 从 develop 创建
  - 合并回 develop
- **命名**：`bugfix/<bug-description>`
- **示例**：
  ```
  bugfix/validation-error
  bugfix/api-timeout
  ```

## 工作流程

### Git Flow 工作流

```
main (生产)
  └─ release/1.0.0 ──┐
                     │
develop (开发)       │
  ├─ feature/auth ───┤
  ├─ feature/api ────┤
  └─ feature/ui ─────┘
```

**流程步骤**：

1. **创建功能分支**
   ```bash
   git checkout develop
   git checkout -b feature/user-auth
   ```

2. **开发功能**
   ```bash
   # 编写代码、提交
   git add .
   git commit -m "feat: 添加用户认证功能"
   ```

3. **合并到 develop**
   ```bash
   git checkout develop
   git merge --no-ff feature/user-auth
   git branch -d feature/user-auth
   ```

4. **创建发布分支**
   ```bash
   git checkout -b release/1.0.0 develop
   ```

5. **发布到 main**
   ```bash
   git checkout main
   git merge --no-ff release/1.0.0
   git tag -a v1.0.0
   ```

6. **合并回 develop**
   ```bash
   git checkout develop
   git merge --no-ff release/1.0.0
   ```

### GitHub Flow 工作流（简化版）

```
main (生产)
  └─ feature/new-feature ── Pull Request ──→ main
```

**流程步骤**：

1. **从 main 创建分支**
   ```bash
   git checkout -b feature/new-feature main
   ```

2. **开发和提交**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   git push origin feature/new-feature
   ```

3. **创建 Pull Request**
   - 在 GitHub 上创建 PR
   - 团队成员审核
   - 通过测试后合并

4. **合并后删除分支**
   ```bash
   git checkout main
   git pull
   git branch -d feature/new-feature
   ```

## 分支命名规范

### 命名格式
```
<type>/<description>
```

### 命名规则
- 使用小写字母
- 使用连字符分隔单词
- 简洁明了
- 反映分支目的

### 命名示例

| 类型 | 命名 | 说明 |
|-----|------|------|
| feature | `feature/user-authentication` | 用户认证功能 |
| feature | `feature/payment-integration` | 支付集成 |
| bugfix | `bugfix/login-validation` | 登录验证修复 |
| hotfix | `hotfix/security-vulnerability` | 安全漏洞修复 |
| release | `release/2.0.0` | 2.0.0 版本发布 |

## 合并策略

### 合并方式

#### 1. Fast-Forward（快进合并）
```bash
git merge feature/branch
```
- 适用场景：线性历史
- 优点：历史简洁
- 缺点：丢失分支信息

#### 2. No-Fast-Forward（非快进合并）
```bash
git merge --no-ff feature/branch
```
- 适用场景：保留分支历史
- 优点：保留分支信息
- 缺点：历史较复杂

#### 3. Squash（压缩合并）
```bash
git merge --squash feature/branch
git commit -m "feat: 完成功能开发"
```
- 适用场景：清理提交历史
- 优点：历史简洁
- 缺点：丢失详细提交

### 合并建议

| 场景 | 推荐方式 | 原因 |
|-----|---------|------|
| feature → develop | `--no-ff` | 保留功能开发历史 |
| develop → main | `--no-ff` | 保留版本发布历史 |
| hotfix → main | `--no-ff` | 保留紧急修复历史 |
| feature（清理后）→ main | `squash` | 简化历史 |

### 冲突解决

**步骤1：拉取最新代码**
```bash
git checkout develop
git pull origin develop
```

**步骤2：合并分支**
```bash
git checkout feature/my-feature
git merge develop
```

**步骤3：解决冲突**
```bash
# 查看冲突文件
git status

# 手动编辑冲突文件
# 选择保留的代码

# 标记为已解决
git add <resolved-file>
```

**步骤4：完成合并**
```bash
git commit -m "merge: 解决合并冲突"
```

## 最佳实践

### 1. 保持分支短小
- 一个分支只做一件事
- 尽快合并或删除
- 避免长期存活的分支

### 2. 定期同步
```bash
# 定期从 develop 拉取更新
git checkout develop
git pull
git checkout feature/my-feature
git merge develop
```

### 3. 使用标签
```bash
# 发布版本时打标签
git checkout main
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 4. 保护重要分支
```bash
# 设置分支保护规则（GitHub）
# Settings → Branches → Add rule
# - Require pull request reviews
# - Require status checks
# - Require signed commits
```

### 5. 清理已合并分支
```bash
# 删除本地已合并分支
git branch --merged | grep -v "\*" | xargs -n 1 git branch -d

# 删除远程已合并分支
git branch -r --merged | grep -v "main\|develop" | sed 's/origin\///' | xargs -n 1 git push --delete origin
```

### 6. 使用 .gitignore
```gitignore
# 忽略不需要版本控制的文件
node_modules/
*.pyc
.env
.DS_Store
```

## 常见问题

### Q1: 分支太多怎么办？
**A**: 定期清理已合并的分支，保持分支列表整洁。

### Q2: 如何处理长期功能分支？
**A**: 定期从 develop 合并更新，避免偏离太远。

### Q3: 合并冲突频繁怎么办？
**A**: 
- 减少分支存活时间
- 更频繁地同步 develop
- 改善团队沟通

### Q4: 如何回滚错误的合并？
**A**: 
```bash
# 回滚最近一次合并
git revert -m 1 <merge-commit-hash>
```

## 团队协作建议

### 分支权限
- **main**：仅管理员可合并
- **develop**：团队负责人可合并
- **feature**：开发者自行管理

### 代码审查
- 所有合并到 main 的 PR 必须审核
- 至少 1 人审核通过
- 通过所有自动化测试

### 发布流程
1. 从 develop 创建 release 分支
2. 进行全面测试
3. 合并到 main 并打标签
4. 部署到生产环境
5. 合并回 develop
