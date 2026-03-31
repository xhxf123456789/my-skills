---
name: test-generator
description: Python单元测试生成与覆盖率分析；智能生成测试用例、执行测试、收集覆盖率数据、生成测试报告；当用户需要为代码生成测试、分析测试覆盖率或识别未测试代码时使用
dependency:
  python:
    - pytest==8.1.1
    - pytest-cov==5.0.0
    - coverage==7.4.4
---

# 测试生成器

## 任务目标
- 本 Skill 用于：Python 单元测试生成与覆盖率分析
- 能力包含：测试用例生成、测试执行、覆盖率分析、测试报告生成
- 触发条件：用户请求"为函数生成测试"、"分析测试覆盖率"、"识别未测试代码"

## 前置准备
- 依赖说明：scripts 脚本所需的依赖包及版本
  ```
  pytest==8.1.1
  pytest-cov==5.0.0
  coverage==7.4.4
  ```

## 操作步骤

### 流程 A：生成单元测试（智能体执行）

**步骤1：分析代码结构**
- 读取目标代码文件
- 识别函数/方法签名、参数、返回值
- 理解代码逻辑和业务规则

**步骤2：设计测试用例**
根据 [测试模式参考](references/test-patterns.md) 设计测试：
- 正常情况：验证预期行为
- 边界情况：测试边界值
- 异常情况：验证错误处理
- 特殊情况：根据业务逻辑设计

**步骤3：编写测试代码**
遵循以下原则：
```python
# 测试文件命名：test_<module_name>.py
# 测试函数命名：test_<function_name>_<scenario>

def test_calculate_discount_normal():
    """测试正常折扣计算"""
    # Arrange: 准备测试数据
    price = 100.0
    discount_rate = 0.2
    
    # Act: 执行被测函数
    result = calculate_discount(price, discount_rate)
    
    # Assert: 验证结果
    assert result == 80.0

def test_calculate_discount_zero_price():
    """测试价格为0的边界情况"""
    result = calculate_discount(0, 0.2)
    assert result == 0.0

def test_calculate_discount_invalid_rate():
    """测试无效折扣率的异常处理"""
    with pytest.raises(ValueError):
        calculate_discount(100, -0.1)
```

**步骤4：保存测试文件**
- 测试文件放在 `tests/` 目录
- 文件名遵循 `test_<module_name>.py` 格式

### 流程 B：执行测试并分析覆盖率

**步骤1：运行测试**
```bash
python scripts/test_runner.py --path ./tests --verbose
```

**步骤2：收集覆盖率数据**
```bash
python scripts/coverage_analyzer.py --source ./myproject --tests ./tests
```

**步骤3：生成测试报告**
```bash
python scripts/test_reporter.py --format markdown
```

## 资源索引
- 测试执行脚本：[scripts/test_runner.py](scripts/test_runner.py)（执行测试并收集结果）
- 覆盖率分析脚本：[scripts/coverage_analyzer.py](scripts/coverage_analyzer.py)（分析代码覆盖率）
- 测试报告脚本：[scripts/test_reporter.py](scripts/test_reporter.py)（生成测试报告）
- 测试模式参考：[references/test-patterns.md](references/test-patterns.md)（常用测试模式）
- 覆盖率指南：[references/coverage-guide.md](references/coverage-guide.md)（覆盖率最佳实践）

## 注意事项
- 测试生成由智能体完成，充分利用代码理解能力
- 测试执行和覆盖率分析由脚本完成，确保准确性
- 建议测试覆盖率达到 80% 以上
- 关注边界情况和异常处理
- 定期运行测试并更新覆盖率报告

## 使用示例

### 示例1：为函数生成测试
**用户请求**："为 calculate_discount 函数生成单元测试"

**智能体执行**：
1. 读取函数代码
2. 分析参数：price (float), discount_rate (float)
3. 设计测试用例：
   - 正常情况：price=100, discount_rate=0.2
   - 边界情况：price=0, price=负数
   - 异常情况：discount_rate < 0 或 > 1
4. 生成测试文件 `test_discount.py`

### 示例2：分析测试覆盖率
**用户请求**："分析项目的测试覆盖率"

**执行步骤**：
1. 运行 `coverage_analyzer.py`
2. 解析覆盖率报告
3. 识别未覆盖的代码行
4. 提供改进建议

### 示例3：生成测试报告
**用户请求**："生成测试报告"

**执行步骤**：
1. 运行 `test_runner.py` 执行所有测试
2. 运行 `coverage_analyzer.py` 收集覆盖率
3. 运行 `test_reporter.py` 生成报告
4. 智能体解读报告并提供改进建议

## 测试生成最佳实践

### 测试命名规范
- 测试文件：`test_<module_name>.py`
- 测试类：`Test<ClassName>`
- 测试函数：`test_<function_name>_<scenario>`

### 测试结构（AAA 模式）
1. **Arrange**：准备测试数据和依赖
2. **Act**：执行被测函数
3. **Assert**：验证结果

### 测试覆盖率目标
- 总体覆盖率：≥ 80%
- 关键路径：100%
- 异常处理：≥ 70%

### 常见测试模式
参考 [references/test-patterns.md](references/test-patterns.md) 了解：
- 参数化测试
- Mock 和 Fixture
- 异常测试
- 集成测试
