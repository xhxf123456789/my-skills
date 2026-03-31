# 测试模式参考

## 目录
- [概览](#概览)
- [基础测试模式](#基础测试模式)
- [参数化测试](#参数化测试)
- [Mock 和 Fixture](#mock-和-fixture)
- [异常测试](#异常测试)
- [集成测试](#集成测试)
- [测试最佳实践](#测试最佳实践)

## 概览
本文档提供 Python 单元测试的常用模式和最佳实践，帮助编写高质量的测试代码。

## 基础测试模式

### AAA 模式（Arrange-Act-Assert）

```python
def test_calculate_discount():
    # Arrange: 准备测试数据
    price = 100.0
    discount_rate = 0.2
    expected_result = 80.0
    
    # Act: 执行被测函数
    result = calculate_discount(price, discount_rate)
    
    # Assert: 验证结果
    assert result == expected_result
```

### 测试类组织

```python
class TestCalculator:
    """计算器测试类"""
    
    def test_add_positive_numbers(self):
        """测试正数相加"""
        result = add(2, 3)
        assert result == 5
    
    def test_add_negative_numbers(self):
        """测试负数相加"""
        result = add(-2, -3)
        assert result == -5
    
    def test_add_zero(self):
        """测试与零相加"""
        result = add(5, 0)
        assert result == 5
```

## 参数化测试

### 使用 pytest.mark.parametrize

```python
import pytest

@pytest.mark.parametrize("price,rate,expected", [
    (100.0, 0.2, 80.0),    # 正常折扣
    (100.0, 0.0, 100.0),   # 零折扣
    (100.0, 1.0, 0.0),     # 全额折扣
    (0.0, 0.2, 0.0),       # 零价格
])
def test_calculate_discount_scenarios(price, rate, expected):
    """测试不同折扣场景"""
    result = calculate_discount(price, rate)
    assert result == expected
```

### 参数化测试类

```python
@pytest.mark.parametrize("input,expected", [
    ([1, 2, 3], 6),
    ([], 0),
    ([-1, -2, -3], -6),
    ([10], 10),
])
class TestSum:
    def test_sum_function(self, input, expected):
        assert sum(input) == expected
```

## Mock 和 Fixture

### 使用 Fixture

```python
import pytest

@pytest.fixture
def sample_data():
    """提供测试数据"""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "age": 25
    }

def test_user_creation(sample_data):
    """测试用户创建"""
    user = User(**sample_data)
    assert user.name == "Test User"
    assert user.email == "test@example.com"
```

### 使用 Mock

```python
from unittest.mock import Mock, patch

def test_send_email():
    """测试发送邮件（使用 Mock）"""
    # 创建 Mock 对象
    mock_smtp = Mock()
    mock_smtp.send_message.return_value = True
    
    # 使用 Mock 测试
    with patch('smtplib.SMTP', return_value=mock_smtp):
        result = send_email("to@example.com", "Subject", "Body")
        assert result is True
        mock_smtp.send_message.assert_called_once()
```

### Mock 数据库

```python
@pytest.fixture
def mock_db():
    """Mock 数据库连接"""
    mock = Mock()
    mock.query.return_value = [{"id": 1, "name": "Test"}]
    return mock

def test_get_user(mock_db):
    """测试获取用户"""
    user = get_user(mock_db, user_id=1)
    assert user["name"] == "Test"
    mock_db.query.assert_called_once_with("SELECT * FROM users WHERE id = 1")
```

## 异常测试

### 测试异常抛出

```python
import pytest

def test_divide_by_zero():
    """测试除零异常"""
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_invalid_input():
    """测试无效输入异常"""
    with pytest.raises(ValueError, match="Invalid input"):
        process_input(-1)

def test_specific_exception_message():
    """测试异常消息"""
    with pytest.raises(ValueError) as exc_info:
        validate_age(-5)
    assert "年龄不能为负数" in str(exc_info.value)
```

### 异常类型匹配

```python
@pytest.mark.parametrize("input,exception", [
    (-1, ValueError),
    (None, TypeError),
    ("abc", TypeError),
])
def test_invalid_inputs(input, exception):
    """测试不同类型的异常"""
    with pytest.raises(exception):
        process(input)
```

## 集成测试

### 测试数据库操作

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="module")
def db_session():
    """创建测试数据库会话"""
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 创建表
    Base.metadata.create_all(engine)
    
    yield session
    
    # 清理
    session.close()

def test_save_user(db_session):
    """测试保存用户"""
    user = User(name="Test", email="test@example.com")
    db_session.add(user)
    db_session.commit()
    
    saved_user = db_session.query(User).filter_by(name="Test").first()
    assert saved_user is not None
    assert saved_user.email == "test@example.com"
```

### 测试 API 调用

```python
from fastapi.testclient import TestClient

def test_api_endpoint():
    """测试 API 端点"""
    client = TestClient(app)
    
    response = client.get("/api/users/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
```

## 测试最佳实践

### 命名规范

| 类型 | 命名规则 | 示例 |
|-----|---------|------|
| 测试文件 | `test_<module>.py` | `test_calculator.py` |
| 测试类 | `Test<Feature>` | `TestCalculator` |
| 测试函数 | `test_<function>_<scenario>` | `test_add_positive_numbers` |

### 测试覆盖维度

1. **正常路径**：验证预期行为
   ```python
   def test_add_normal():
       assert add(2, 3) == 5
   ```

2. **边界情况**：测试边界值
   ```python
   def test_add_zero():
       assert add(5, 0) == 5
   ```

3. **异常情况**：验证错误处理
   ```python
   def test_add_invalid_type():
       with pytest.raises(TypeError):
           add("a", "b")
   ```

4. **性能测试**：验证性能要求
   ```python
   def test_performance():
       import time
       start = time.time()
       large_operation()
       assert time.time() - start < 1.0
   ```

### 测试独立性原则

```python
# ✗ 错误：依赖其他测试
def test_create_user():
    user = User.objects.create(name="Test")

def test_delete_user():  # 依赖上一个测试创建的用户
    user = User.objects.get(name="Test")
    user.delete()

# ✓ 正确：每个测试独立
def test_create_user():
    user = User.objects.create(name="Test")
    assert user.id is not None

def test_delete_user():
    user = User.objects.create(name="Test")  # 独立创建
    user_id = user.id
    user.delete()
    assert not User.objects.filter(id=user_id).exists()
```

### 测试数据管理

```python
# 使用 Factory 创建测试数据
class UserFactory:
    @staticmethod
    def create(**kwargs):
        defaults = {
            "name": "Test User",
            "email": "test@example.com",
            "age": 25
        }
        defaults.update(kwargs)
        return User(**defaults)

def test_user_age():
    user = UserFactory.create(age=30)
    assert user.age == 30
```

### 清理测试数据

```python
@pytest.fixture(autouse=True)
def cleanup_database(db_session):
    """每个测试后自动清理数据库"""
    yield
    db_session.rollback()
```

## 常见测试场景

### 测试列表操作

```python
def test_list_operations():
    items = [1, 2, 3]
    
    # 测试添加
    items.append(4)
    assert len(items) == 4
    
    # 测试删除
    items.remove(2)
    assert 2 not in items
    
    # 测试排序
    items.sort(reverse=True)
    assert items[0] == 4
```

### 测试字典操作

```python
def test_dict_operations():
    data = {"a": 1, "b": 2}
    
    # 测试访问
    assert data["a"] == 1
    
    # 测试更新
    data["c"] = 3
    assert "c" in data
    
    # 测试删除
    del data["b"]
    assert "b" not in data
```

### 测试文件操作

```python
import tempfile
import os

def test_file_operations():
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test content")
        temp_path = f.name
    
    try:
        # 测试读取
        with open(temp_path, 'r') as f:
            content = f.read()
            assert content == "test content"
    finally:
        # 清理
        os.unlink(temp_path)
```
