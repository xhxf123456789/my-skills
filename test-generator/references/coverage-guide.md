# 覆盖率指南

## 目录
- [概览](#概览)
- [覆盖率基础](#覆盖率基础)
- [覆盖率类型](#覆盖率类型)
- [覆盖率工具](#覆盖率工具)
- [覆盖率目标](#覆盖率目标)
- [提高覆盖率](#提高覆盖率)
- [覆盖率最佳实践](#覆盖率最佳实践)

## 概览
本文档说明代码覆盖率的概念、工具使用和最佳实践，帮助团队建立有效的测试覆盖率管理流程。

## 覆盖率基础

### 什么是代码覆盖率
代码覆盖率是衡量测试完整性的指标，表示测试执行过程中被执行到的代码比例。

### 为什么需要覆盖率
- 量化测试完整性
- 发现未测试的代码
- 评估测试质量
- 指导测试改进

### 覆盖率计算
```
覆盖率 = (已执行代码行数 / 总代码行数) × 100%
```

## 覆盖率类型

### 行覆盖率（Line Coverage）
最常见的覆盖率类型，统计被执行的代码行。

**示例**：
```python
def calculate(a, b, operation):
    if operation == "add":        # 行 1
        return a + b              # 行 2（如果执行 add）
    elif operation == "subtract": # 行 3
        return a - b              # 行 4（如果执行 subtract）
    else:
        return None               # 行 5（其他情况）
```

如果只测试 add 操作：
- 执行行：1, 2
- 未执行行：3, 4, 5
- 行覆盖率：2/5 = 40%

### 分支覆盖率（Branch Coverage）
统计所有分支是否被测试覆盖。

**示例**：
```python
if a > 0 and b > 0:  # 2 个分支
    result = a + b
```

分支覆盖率要求测试：
1. `a > 0 and b > 0` 为 True
2. `a > 0 and b > 0` 为 False

### 函数覆盖率（Function Coverage）
统计被调用的函数比例。

**示例**：
```python
class Calculator:
    def add(self, a, b):      # 函数 1
        return a + b
    
    def subtract(self, a, b): # 函数 2
        return a - b
```

如果只测试 add：
- 函数覆盖率：1/2 = 50%

### 条件覆盖率（Condition Coverage）
统计每个条件的 True/False 是否都被测试。

**示例**：
```python
if a > 0 or b > 0:  # 2 个条件
    result = a + b
```

条件覆盖率要求测试：
| a > 0 | b > 0 | 组合 |
|-------|-------|------|
| True | True | 测试 |
| True | False | 测试 |
| False | True | 测试 |
| False | False | 测试 |

## 覆盖率工具

### pytest-cov

**安装**：
```bash
pip install pytest-cov
```

**基本使用**：
```bash
# 运行测试并显示覆盖率
pytest --cov=myproject tests/

# 生成 HTML 报告
pytest --cov=myproject --cov-report=html tests/

# 生成 XML 报告
pytest --cov=myproject --cov-report=xml tests/

# 设置最低覆盖率要求
pytest --cov=myproject --cov-fail-under=80 tests/
```

**配置文件（pytest.ini）**：
```ini
[pytest]
addopts = --cov=myproject --cov-report=term-missing --cov-report=html
testpaths = tests
```

### coverage.py

**安装**：
```bash
pip install coverage
```

**基本使用**：
```bash
# 收集覆盖率数据
coverage run -m pytest tests/

# 生成报告
coverage report

# 生成 HTML 报告
coverage html

# 清理数据
coverage erase
```

**配置文件（.coveragerc）**：
```ini
[run]
source = myproject
omit = 
    */tests/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## 覆盖率目标

### 行业标准

| 项目类型 | 最低覆盖率 | 建议覆盖率 |
|---------|-----------|-----------|
| 关键系统 | 90% | 95%+ |
| 一般项目 | 80% | 85%+ |
| 快速迭代 | 70% | 80%+ |
| 原型项目 | 50% | 70%+ |

### 分层目标

| 代码层次 | 覆盖率目标 | 原因 |
|---------|-----------|------|
| 核心业务逻辑 | 95%+ | 关键路径必须测试 |
| 工具函数 | 90%+ | 工具函数影响范围大 |
| API 接口 | 85%+ | 确保接口正确性 |
| UI 层 | 70%+ | UI 变化频繁 |
| 配置文件 | 50%+ | 配置测试价值低 |

## 提高覆盖率

### 识别未覆盖代码

**方法1：使用覆盖率报告**
```bash
pytest --cov=myproject --cov-report=term-missing tests/
```

输出示例：
```
Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
myproject/calculator.py      45      5    89%   23-27
myproject/utils.py           30     10    67%   15, 20-25
```

**方法2：查看 HTML 报告**
```bash
pytest --cov=myproject --cov-report=html tests/
open htmlcov/index.html
```

### 常见未覆盖原因

| 原因 | 解决方案 |
|-----|---------|
| 缺少测试用例 | 添加测试用例 |
| 异常处理分支 | 模拟异常情况 |
| 条件分支未覆盖 | 添加边界测试 |
| 死代码 | 删除无用代码 |

### 提高覆盖率策略

**策略1：补充测试用例**
```python
# 原有测试
def test_add():
    assert add(2, 3) == 5

# 补充边界测试
def test_add_zero():
    assert add(0, 0) == 0

def test_add_negative():
    assert add(-1, -2) == -3
```

**策略2：测试异常处理**
```python
def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

**策略3：参数化测试**
```python
@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, -2, -3),
    (100, -50, 50),
])
def test_add_scenarios(a, b, expected):
    assert add(a, b) == expected
```

## 覆盖率最佳实践

### 1. 设置合理目标

```ini
# pytest.ini
[pytest]
addopts = --cov=myproject --cov-fail-under=80
```

### 2. 排除不需要测试的代码

```ini
# .coveragerc
[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if __name__ == .__main__.:
```

### 3. 持续监控覆盖率

**CI/CD 集成**：
```yaml
# .github/workflows/test.yml
- name: Run tests with coverage
  run: pytest --cov=myproject --cov-fail-under=80

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
```

### 4. 定期审查覆盖率报告

- 每周审查低覆盖率模块
- 优先提高核心模块覆盖率
- 关注覆盖率下降趋势

### 5. 避免覆盖率陷阱

**陷阱1：高覆盖率 ≠ 高质量**
```python
# ✗ 高覆盖率但低质量
def test_add():
    add(2, 3)  # 没有断言！

# ✓ 正确的测试
def test_add():
    result = add(2, 3)
    assert result == 5
```

**陷阱2：为了覆盖率而测试**
```python
# ✗ 无意义的测试
def test_getter():
    obj = MyClass()
    obj.get_name()  # 仅为了覆盖

# ✓ 有价值的测试
def test_getter():
    obj = MyClass(name="Test")
    assert obj.get_name() == "Test"
```

**陷阱3：忽略边界测试**
```python
# ✗ 只测试正常情况
def test_divide():
    assert divide(10, 2) == 5

# ✓ 包含边界测试
def test_divide():
    assert divide(10, 2) == 5
    assert divide(0, 5) == 0
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

### 6. 团队协作

**代码审查要求**：
- 新代码覆盖率 ≥ 80%
- 修复 Bug 必须添加测试
- 重构代码保持覆盖率不下降

**文档化**：
```markdown
## 测试覆盖率要求

- 新功能：≥ 85%
- Bug 修复：添加回归测试
- 核心模块：≥ 90%
```

## 覆盖率报告解读

### HTML 报告

**颜色标识**：
- 🟢 绿色：已覆盖
- 🔴 红色：未覆盖
- 🟡 黄色：部分覆盖

**关键指标**：
- **Stmts**：语句总数
- **Miss**：未执行语句数
- **Cover**：覆盖率百分比
- **Missing**：未覆盖行号

### 终端报告

```
Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
myproject/__init__.py         1      0   100%
myproject/calculator.py      45      5    89%   23-27
myproject/utils.py           30     10    67%   15, 20-25
-------------------------------------------------------
TOTAL                        76     15    80%
```

### XML 报告

用于 CI/CD 集成和覆盖率服务：
```xml
<coverage line-rate="0.8" branch-rate="0.75">
  <packages>
    <package name="myproject" line-rate="0.8">
      <classes>
        <class name="calculator.py" line-rate="0.89"/>
      </classes>
    </package>
  </packages>
</coverage>
```

## 常见问题

### Q1: 覆盖率多少合适？
**A**: 根据项目类型和风险等级决定：
- 关键系统：95%+
- 一般项目：80%+
- 快速迭代：70%+

### Q2: 如何处理无法测试的代码？
**A**: 使用 pragma 标记：
```python
if debug:  # pragma: no cover
    print("Debug mode")
```

### Q3: 覆盖率下降了怎么办？
**A**: 
1. 查看覆盖率报告找出未覆盖代码
2. 补充测试用例
3. 检查是否引入了新代码但未添加测试

### Q4: 如何提高分支覆盖率？
**A**: 为每个分支设计测试用例：
```python
if a > 0 and b > 0:
    result = a + b

# 需要 4 个测试用例：
# 1. a > 0, b > 0 (True)
# 2. a > 0, b <= 0 (False)
# 3. a <= 0, b > 0 (False)
# 4. a <= 0, b <= 0 (False)
```
