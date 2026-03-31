---
name: code-analyzer
description: Python代码质量分析与安全检测（优化版）；提供静态分析、复杂度计算、重复代码检测、安全漏洞扫描、综合质量报告；当用户需要分析代码质量、检查安全问题、计算复杂度、检测重复代码或生成质量报告时使用
dependency:
  python:
    - radon==6.0.1
    - pylint==3.1.0
    - bandit==1.7.8
---

# 代码分析器（优化版）

## 任务目标
- 本 Skill 用于：Python 代码质量分析与安全检测
- 能力包含：静态代码分析、复杂度计算、重复代码检测、安全漏洞扫描、**综合质量报告**
- 触发条件：用户请求"分析代码质量"、"检查安全问题"、"计算复杂度"、"检测重复代码"、"生成质量报告"

## 新增功能（优化版）
1. **代码质量评分**：基于多维度计算 0-100 分的质量评分
2. **优先级改进建议**：按严重程度排序的改进建议
3. **修复建议**：为常见问题提供详细的修复建议
4. **OWASP 映射**：安全问题映射到 OWASP Top 10
5. **可视化报告**：生成 Markdown/HTML 格式的综合报告

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
     - 静态分析：调用 `scripts/static_analyzer.py`（新增：质量评分、修复建议）
     - 复杂度分析：调用 `scripts/complexity_analyzer.py`（新增：重构建议）
     - 重复检测：调用 `scripts/duplicate_detector.py`
     - 安全扫描：调用 `scripts/security_scanner.py`（新增：OWASP 映射）
     - **质量报告**：调用 `scripts/quality_reporter.py`（新增功能）
  3. **执行分析**：根据脚本参数要求传入路径和配置
  4. **解读结果**：智能体分析 JSON 输出，提供改进建议

- 可选分支：
  - 当需要全面分析：依次执行所有分析脚本，最后生成质量报告
  - 当关注代码质量：执行静态分析 + 复杂度分析
  - 当关注安全性：执行安全扫描
  - **当需要质量报告**：使用 `quality_reporter.py` 生成综合报告

## 资源索引
- 静态分析脚本：[scripts/static_analyzer.py](scripts/static_analyzer.py)（集成 pylint，新增质量评分）
- 复杂度分析脚本：[scripts/complexity_analyzer.py](scripts/complexity_analyzer.py)（新增重构建议）
- 重复检测脚本：[scripts/duplicate_detector.py](scripts/duplicate_detector.py)（检测重复代码块）
- 安全扫描脚本：[scripts/security_scanner.py](scripts/security_scanner.py)（新增 OWASP 映射）
- **质量报告脚本**：[scripts/quality_reporter.py](scripts/quality_reporter.py)（**新增**：综合质量报告）
- 配置说明：[references/analysis-config.md](references/analysis-config.md)（分析规则配置）
- 指标说明：[references/metrics-guide.md](references/metrics-guide.md)（复杂度指标详解）

## 注意事项
- 所有脚本输出 JSON 格式，便于解析和处理
- **新增参数**：`--show-suggestions` 显示修复建议，`--show-fixes` 显示安全修复
- 分析大型项目时可能耗时较长，建议指定具体文件或目录
- 复杂度阈值可根据项目特点调整（默认 min_complexity=5）
- 安全扫描分为低/中/高三个严重级别

## 使用示例

### 示例1：静态代码分析（优化版）
```bash
python scripts/static_analyzer.py --path ./myproject --show-suggestions
```
**输出**：包含错误、警告、约定、**质量评分**、**修复建议**的 JSON 报告

### 示例2：复杂度分析（优化版）
```bash
python scripts/complexity_analyzer.py --path ./myproject --min-complexity 8 --show-suggestions
```
**输出**：包含函数/方法复杂度、**重构建议**的 JSON 报告

### 示例3：安全扫描（优化版）
```bash
python scripts/security_scanner.py --path ./myproject --severity medium --show-fixes
```
**输出**：包含安全问题、**修复建议**、**OWASP 映射**的 JSON 报告

### 示例4：生成质量报告（新增）
```bash
# 先运行各分析脚本并保存结果
python scripts/static_analyzer.py --path ./myproject > static.json
python scripts/complexity_analyzer.py --path ./myproject > complexity.json
python scripts/duplicate_detector.py --path ./myproject > duplicate.json
python scripts/security_scanner.py --path ./myproject > security.json

# 生成综合报告
python scripts/quality_reporter.py \
  --static static.json \
  --complexity complexity.json \
  --duplicate duplicate.json \
  --security security.json \
  --format html \
  --output report.html
```
**输出**：包含**质量评分**、**优先级改进建议**、**可视化报告**的 HTML 文件

### 示例5：全面分析（智能体执行）
当用户请求"全面分析这个项目"时：
1. 依次调用 4 个分析脚本（使用优化参数）
2. 调用 `quality_reporter.py` 生成综合报告
3. 智能体解析结果，生成综合分析报告，包含：
   - **代码质量评分（0-100分）**
   - **优先级改进建议（按严重程度排序）**
   - 复杂度热点
   - 重复代码位置
   - 安全风险等级及 OWASP 映射
   - **修复建议和代码示例**

## 质量评分说明

### 评分维度（总分 100 分）
| 维度 | 权重 | 说明 |
|-----|------|------|
| 静态分析 | 40% | 基于错误、警告数量计算 |
| 代码复杂度 | 30% | 基于平均复杂度和高复杂度函数比例 |
| 重复代码 | 20% | 基于重复代码比例 |
| 安全性 | 10% | 基于安全问题数量和严重程度 |

### 质量等级
| 分数 | 等级 | 说明 |
|-----|------|------|
| 90-100 | A+ | 优秀，代码质量极高 |
| 85-89 | A | 良好，代码质量高 |
| 80-84 | B+ | 较好，代码质量良好 |
| 75-79 | B | 一般，有改进空间 |
| 70-74 | C+ | 及格，需要改进 |
| 60-69 | C | 较差，需要较多改进 |
| 50-59 | D | 差，需要大量改进 |
| 0-49 | F | 不合格，必须重构 |
