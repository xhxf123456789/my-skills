---
name: maven-troubleshooter
description: Maven构建问题高级诊断与解决；提供依赖冲突分析、构建错误诊断、仓库健康检查、性能优化；当用户遇到Maven构建失败、依赖冲突、仓库损坏或构建性能问题时使用
dependency:
  python:
    - lxml==5.1.0
    - requests==2.31.0
---

# Maven 问题解决专家

## 任务目标
- 本 Skill 用于：Maven 构建问题的深度诊断与解决
- 能力包含：依赖冲突分析、构建错误诊断、仓库健康检查、插件配置验证、性能优化
- 触发条件：用户报告 Maven 构建失败、依赖冲突、仓库问题或构建缓慢

## 前置准备
- 依赖说明：scripts 脚本所需的依赖包及版本
  ```
  lxml==5.1.0
  requests==2.31.0
  ```
- 系统要求：Maven 3.6+ 已安装并配置到 PATH

## 操作步骤

### 流程 A：依赖冲突诊断

**场景**：构建时报错 `NoSuchMethodError`、`ClassNotFoundException` 或版本冲突

**步骤1：分析依赖树**
```bash
python scripts/dependency_analyzer.py --pom ./pom.xml --output ./dependency-report.json
```

**步骤2：解读报告**
智能体根据报告内容：
1. 识别冲突的依赖项
2. 分析版本差异
3. 提供解决建议：
   - 使用 `<exclusion>` 排除冲突依赖
   - 使用 `<dependencyManagement>` 统一版本
   - 升级/降级依赖版本

**步骤3：应用修复**
智能体生成修复后的 pom.xml 片段

### 流程 B：构建失败诊断

**场景**：Maven 构建失败，需要分析错误原因

**步骤1：捕获错误日志**
```bash
mvn clean install 2>&1 | tee build-error.log
```

**步骤2：诊断错误**
```bash
python scripts/build_diagnostics.py --log build-error.log --output ./diagnosis.json
```

**步骤3：智能分析**
智能体根据诊断结果，参考 [常见问题手册](references/maven-common-issues.md)：
1. 分类错误类型（编译错误、测试失败、依赖缺失等）
2. 提供解决方案
3. 给出修复步骤

**步骤4：修复验证**
修复后重新构建验证

### 流程 C：仓库健康检查

**场景**：依赖下载失败、仓库损坏、构建异常

**步骤1：检查仓库状态**
```bash
python scripts/repository_checker.py --action check --output ./repo-health.json
```

**步骤2：清理损坏的依赖**
```bash
python scripts/repository_checker.py --action clean --dependency groupId:artifactId:version
```

**步骤3：验证镜像配置**
检查 settings.xml 中的镜像配置，参考 [settings.xml 模板](assets/settings-template.xml)

### 流程 D：构建性能优化

**场景**：构建缓慢，需要优化

**步骤1：性能分析**
```bash
python scripts/performance_analyzer.py --log build-time.log --output ./performance-report.json
```

**步骤2：识别瓶颈**
智能体分析报告，识别：
- 慢速模块
- 耗时插件
- 网络下载瓶颈

**步骤3：优化建议**
参考 [最佳实践指南](references/maven-best-practices.md) 提供优化方案

## 资源索引
- 依赖分析脚本：[scripts/dependency_analyzer.py](scripts/dependency_analyzer.py)
- 构建诊断脚本：[scripts/build_diagnostics.py](scripts/build_diagnostics.py)
- 仓库检查脚本：[scripts/repository_checker.py](scripts/repository_checker.py)
- 性能分析脚本：[scripts/performance_analyzer.py](scripts/performance_analyzer.py)
- 常见问题手册：[references/maven-common-issues.md](references/maven-common-issues.md)
- 最佳实践指南：[references/maven-best-practices.md](references/maven-best-practices.md)
- Settings 模板：[assets/settings-template.xml](assets/settings-template.xml)

## 典型问题解决示例

### 示例1：依赖版本冲突

**问题描述**：
```
java.lang.NoSuchMethodError: com.google.gson.Gson.toJson(Ljava/lang/Object;)Ljava/lang/String;
```

**诊断步骤**：
```bash
python scripts/dependency_analyzer.py --pom ./pom.xml --output ./conflict-report.json
```

**智能体分析**：
报告显示 `com.google.gson:gson` 存在多个版本：
- 项目依赖：2.8.9
- 某框架传递依赖：2.7

**解决方案**：
```xml
<dependency>
    <groupId>com.google.gson</groupId>
    <artifactId>gson</artifactId>
    <version>2.8.9</version>
</dependency>

<!-- 或排除冲突传递 -->
<dependency>
    <groupId>some.framework</groupId>
    <artifactId>framework-core</artifactId>
    <version>1.0.0</version>
    <exclusions>
        <exclusion>
            <groupId>com.google.gson</groupId>
            <artifactId>gson</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

### 示例2：依赖下载失败

**问题描述**：
```
Could not resolve dependencies for project com.example:app:jar:1.0:
Failed to collect dependencies at org.springframework.boot:spring-boot-starter-web:jar:2.7.0
```

**诊断步骤**：
```bash
python scripts/repository_checker.py --action check --output ./repo-check.json
```

**智能体分析**：
1. 检查网络连接
2. 验证仓库配置
3. 清理本地缓存

**解决方案**：
```bash
# 清理特定依赖缓存
python scripts/repository_checker.py --action clean --dependency org.springframework.boot:spring-boot-starter-web:2.7.0

# 或清理整个缓存
rm -rf ~/.m2/repository/org/springframework/boot/
mvn clean install -U
```

### 示例3：构建缓慢

**问题描述**：完整构建耗时 15 分钟

**诊断步骤**：
```bash
mvn clean install -Dmaven.profile.log=true 2>&1 | tee build-time.log
python scripts/performance_analyzer.py --log build-time.log --output ./perf-report.json
```

**智能体分析**：
报告显示瓶颈：
- 下载依赖：8 分钟
- 测试执行：5 分钟
- 编译：2 分钟

**优化建议**：
1. 配置镜像加速（阿里云/华为云）
2. 启用并行构建：`mvn -T 4 clean install`
3. 跳过测试（开发阶段）：`mvn -DskipTests`
4. 使用本地仓库缓存

## 注意事项
- 分析前确保 pom.xml 格式正确
- 仓库清理操作会删除本地缓存，谨慎使用
- 性能优化需在多次构建后验证效果
- 大型项目建议分模块诊断
- 使用 `-X` 参数获取详细日志：`mvn -X clean install`

## 高级功能

### 批量依赖更新检查
```bash
python scripts/dependency_analyzer.py --pom ./pom.xml --check-updates --output ./updates.json
```

### 安全漏洞扫描
```bash
python scripts/dependency_analyzer.py --pom ./pom.xml --check-vulnerabilities --output ./security-report.json
```

### 多模块项目分析
```bash
python scripts/dependency_analyzer.py --pom ./parent-pom.xml --multi-module --output ./full-report.json
```
