---
name: code-analyzer
description: Python代码质量分析与安全检测；提供静态分析、复杂度计算、重复代码检测、安全漏洞扫描；当用户需要分析代码质量、检查安全问题、计算复杂度或检测重复代码时使用
dependency:
  python:
    - radon==6.0.1
    - pylint==3.1.0
    - bandit==1.7.8
---

# 代码分析器

## 任务目标
- 本 Skill 用于：Python 代码质量分析与安全检测
- 能力包含：静态代码分析、复杂度计算、重复代码检测、安全漏洞扫描
- 触发条件：用户请求"分析代码质量"、"检查安全问题"、"计算复杂度"、"检测重复代码"

## 前置准备
- 依赖说明：scripts 脚本所需的依赖包及版本
  ```
  radon==6.0.1
  pylint==3.1.0
  bandit==1.7.8
  ```

## 操作步骤
- 标准流程：
  1. **确定分析目标**：明确要分析的文件或目录路径
  2. **选择分析类型**：
     - 静态分析：调用 `scripts/static_analyzer.py`
     - 复杂度分析：调用 `scripts/complexity_analyzer.py`
     - 重复检测：调用 `scripts/duplicate_detector.py`
     - 安全扫描：调用 `scripts/security_scanner.py`
  3. **执行分析**：根据脚本参数要求传入路径和配置
  4. **解读结果**：智能体分析 JSON 输出，提供改进建议

- 可选分支：
  - 当需要全面分析：依次执行所有分析脚本
  - 当关注代码质量：执行静态分析 + 复杂度分析
  - 当关注安全性：执行安全扫描

## 资源索引
- 静态分析脚本：[scripts/static_analyzer.py](scripts/static_analyzer.py)（集成 pylint）
- 复杂度分析脚本：[scripts/complexity_analyzer.py](scripts/complexity_analyzer.py)（计算圈复杂度）
- 重复检测脚本：[scripts/duplicate_detector.py](scripts/duplicate_detector.py)（检测重复代码块）
- 安全扫描脚本：[scripts/security_scanner.py](scripts/security_scanner.py)（集成 bandit）
- 配置说明：[references/analysis-config.md](references/analysis-config.md)（分析规则配置）
- 指标说明：[references/metrics-guide.md](references/metrics-guide.md)（复杂度指标详解）

## 注意事项
- 所有脚本输出 JSON 格式，便于解析和处理
- 分析大型项目时可能耗时较长，建议指定具体文件或目录
- 复杂度阈值可根据项目特点调整（默认 min_complexity=5）
- 安全扫描分为低/中/高三个严重级别

## 使用示例

### 示例1：静态代码分析
```bash
python scripts/static_analyzer.py --path ./myproject --output json
```
**输出**：包含错误、警告、约定的 JSON 报告

### 示例2：复杂度分析
```bash
python scripts/complexity_analyzer.py --path ./myproject --min-complexity 5
```
**输出**：包含函数/方法复杂度的 JSON 报告

### 示例3：重复代码检测
```bash
python scripts/duplicate_detector.py --path ./myproject --min-lines 5
```
**输出**：包含重复代码块的 JSON 报告

### 示例4：安全漏洞扫描
```bash
python scripts/security_scanner.py --path ./myproject --severity medium
```
**输出**：包含安全问题的 JSON 报告

### 示例5：全面分析（智能体执行）
当用户请求"全面分析这个项目"时：
1. 依次调用 4 个分析脚本
2. 智能体解析 JSON 结果
3. 生成综合分析报告，包含：
   - 代码质量评分
   - 复杂度热点
   - 重复代码位置
   - 安全风险等级
   - 改进建议
