# 依赖模式参考

## 目录
- [概览](#概览)
- [依赖类型](#依赖类型)
- [循环依赖](#循环依赖)
- [分层架构](#分层架构)
- [依赖注入](#依赖注入)
- [最佳实践](#最佳实践)

## 概览
本文档说明常见的依赖模式、问题和解决方案，帮助设计清晰的项目结构。

## 依赖类型

### 1. 直接依赖
模块 A 直接导入模块 B。

```python
# module_a.py
import module_b

def function_a():
    module_b.function_b()
```

**特点**：
- 最常见的依赖形式
- 清晰明确
- 易于理解和维护

### 2. 间接依赖
模块 A 依赖模块 B，模块 B 依赖模块 C。

```python
# module_a.py
import module_b

# module_b.py
import module_c

# A → B → C（A 间接依赖 C）
```

**特点**：
- 形成依赖链
- 需要注意依赖传递性
- 可能导致耦合度过高

### 3. 循环依赖
模块 A 依赖模块 B，模块 B 也依赖模块 A。

```python
# module_a.py
import module_b

# module_b.py
import module_a

# A ↔ B（循环依赖）
```

**问题**：
- 可能导致导入错误
- 代码难以理解和维护
- 增加测试难度

## 循环依赖

### 问题场景

**场景1：函数级别循环**
```python
# a.py
from b import func_b

def func_a():
    func_b()

# b.py
from a import func_a

def func_b():
    func_a()  # 循环调用
```

**场景2：类级别循环**
```python
# user.py
from order import Order

class User:
    def get_orders(self):
        return Order.query_by_user(self.id)

# order.py
from user import User

class Order:
    def get_user(self):
        return User.query_by_id(self.user_id)
```

### 解决方案

**方案1：延迟导入**
```python
# a.py
def func_a():
    from b import func_b  # 在函数内部导入
    func_b()

# b.py
def func_b():
    from a import func_a
    func_a()
```

**方案2：提取公共模块**
```python
# 创建新模块 c.py
def common_function():
    pass

# a.py
from c import common_function

# b.py
from c import common_function
# A → C ← B（打破循环）
```

**方案3：依赖注入**
```python
# a.py
class User:
    def get_orders(self, order_class):  # 注入依赖
        return order_class.query_by_user(self.id)

# b.py
class Order:
    pass

# 使用
user = User()
orders = user.get_orders(Order)
```

## 分层架构

### 标准分层

```
┌─────────────────────────┐
│  表示层 (Presentation)   │  ← 用户界面
├─────────────────────────┤
│  业务逻辑层 (Business)   │  ← 核心逻辑
├─────────────────────────┤
│  数据访问层 (Data Access)│  ← 数据库操作
├─────────────────────────┤
│  数据层 (Data)          │  ← 数据模型
└─────────────────────────┘
```

### 依赖规则

**单向依赖**：
- 上层依赖下层
- 下层不依赖上层
- 同层模块尽量独立

**示例**：
```python
# 表示层 (ui.py)
from business import UserService

def show_user(user_id):
    service = UserService()
    user = service.get_user(user_id)
    print(user.name)

# 业务逻辑层 (business.py)
from dao import UserDao

class UserService:
    def get_user(self, user_id):
        dao = UserDao()
        return dao.query(user_id)

# 数据访问层 (dao.py)
from models import User

class UserDao:
    def query(self, user_id):
        return User.query.filter_by(id=user_id).first()

# 数据层 (models.py)
class User:
    # 数据模型定义
    pass
```

## 依赖注入

### 概念
依赖注入（Dependency Injection，DI）是一种设计模式，将依赖关系从代码内部移到外部。

### 实现方式

**方式1：构造函数注入**
```python
class UserService:
    def __init__(self, user_dao):
        self.user_dao = user_dao  # 注入依赖
    
    def get_user(self, user_id):
        return self.user_dao.query(user_id)

# 使用
dao = UserDao()
service = UserService(dao)  # 注入依赖
```

**方式2：属性注入**
```python
class UserService:
    def __init__(self):
        self.user_dao = None
    
    def set_dao(self, user_dao):
        self.user_dao = user_dao  # 注入依赖

# 使用
service = UserService()
service.set_dao(UserDao())  # 注入依赖
```

**方式3：接口注入**
```python
from abc import ABC, abstractmethod

class IUserDao(ABC):
    @abstractmethod
    def query(self, user_id):
        pass

class UserService:
    def __init__(self, user_dao: IUserDao):
        self.user_dao = user_dao
```

### 优势

1. **降低耦合**：模块之间松耦合
2. **便于测试**：可以注入 Mock 对象
3. **灵活配置**：运行时决定具体实现

## 最佳实践

### 1. 模块职责单一
每个模块只负责一件事，减少不必要的依赖。

```python
# ✓ 好的设计
class UserValidator:
    def validate(self, user):
        # 只负责验证
        pass

class UserRepository:
    def save(self, user):
        # 只负责存储
        pass

class UserService:
    def __init__(self, validator, repository):
        self.validator = validator
        self.repository = repository
    
    def create_user(self, user):
        self.validator.validate(user)
        self.repository.save(user)

# ✗ 差的设计
class UserManager:
    def validate(self, user):
        pass
    
    def save(self, user):
        pass
    
    def send_email(self, user):
        pass
    
    def do_everything(self, user):
        pass
```

### 2. 接口编程
依赖抽象接口而非具体实现。

```python
# ✓ 依赖接口
from abc import ABC, abstractmethod

class ILogger(ABC):
    @abstractmethod
    def log(self, message):
        pass

class UserService:
    def __init__(self, logger: ILogger):
        self.logger = logger

# ✗ 依赖具体实现
class UserService:
    def __init__(self):
        from file_logger import FileLogger
        self.logger = FileLogger()
```

### 3. 依赖倒置原则
高层模块不依赖低层模块，两者都依赖抽象。

```python
# ✓ 依赖倒置
class IUserRepository(ABC):
    @abstractmethod
    def get(self, user_id):
        pass

class UserService:
    def __init__(self, repo: IUserRepository):
        self.repo = repo

class MySQLUserRepository(IUserRepository):
    def get(self, user_id):
        # MySQL 实现
        pass

class MongoUserRepository(IUserRepository):
    def get(self, user_id):
        # MongoDB 实现
        pass
```

### 4. 避免过度依赖
减少不必要的导入，只导入真正需要的模块。

```python
# ✓ 只导入需要的
from datetime import datetime

def get_timestamp():
    return datetime.now()

# ✗ 导入整个模块
import datetime

def get_timestamp():
    return datetime.datetime.now()
```

### 5. 组织导入顺序
按标准顺序组织导入：标准库、第三方库、本地模块。

```python
# 标准库
import os
import sys
from datetime import datetime

# 第三方库
import requests
import pandas as pd

# 本地模块
from myproject.utils import helper
from myproject.models import User
```

## 常见问题

### Q1: 如何判断依赖是否合理？
**A**: 
- 是否符合分层架构原则
- 是否存在循环依赖
- 依赖深度是否合理（建议不超过 3 层）

### Q2: 大型项目如何管理依赖？
**A**: 
- 使用依赖注入容器
- 明确模块边界
- 定期审查依赖关系

### Q3: 如何重构循环依赖？
**A**: 
1. 识别循环依赖路径
2. 提取公共逻辑到新模块
3. 使用依赖注入或延迟导入
4. 重新设计模块职责

## 工具推荐

1. **pydeps**：可视化 Python 依赖
2. **import-linter**：检查导入规则
3. **modulegraph**：分析模块依赖图
4. **dependency-mapper**：本 Skill 提供的依赖分析工具
