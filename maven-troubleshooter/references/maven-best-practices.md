# Maven 最佳实践指南

本文档整理了 Maven 使用的最佳实践，帮助团队构建高效、可维护的项目。

## 目录

1. [项目结构最佳实践](#项目结构最佳实践)
2. [依赖管理最佳实践](#依赖管理最佳实践)
3. [构建配置最佳实践](#构建配置最佳实践)
4. [多模块项目最佳实践](#多模块项目最佳实践)
5. [性能优化最佳实践](#性能优化最佳实践)
6. [安全最佳实践](#安全最佳实践)

---

## 项目结构最佳实践

### 1. 标准目录结构

```
my-project/
├── pom.xml
├── src/
│   ├── main/
│   │   ├── java/           # Java 源代码
│   │   ├── resources/      # 资源文件
│   │   ├── webapp/         # Web 应用资源（WAR 项目）
│   │   └── filters/        # 资源过滤文件
│   └── test/
│       ├── java/           # 测试代码
│       └── resources/      # 测试资源
├── docs/                   # 项目文档
├── scripts/                # 构建脚本
└── README.md
```

### 2. POM 文件组织

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                             http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <!-- 基本信息 -->
    <groupId>com.example</groupId>
    <artifactId>my-project</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>
    
    <!-- 项目描述 -->
    <name>My Project</name>
    <description>项目描述</description>
    <url>https://example.com/project</url>
    
    <!-- 许可证 -->
    <licenses>
        <license>
            <name>Apache License 2.0</name>
            <url>https://www.apache.org/licenses/LICENSE-2.0</url>
        </license>
    </licenses>
    
    <!-- 开发者信息 -->
    <developers>
        <developer>
            <id>developer1</id>
            <name>Developer Name</name>
            <email>dev@example.com</email>
        </developer>
    </developers>
    
    <!-- 属性定义 -->
    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <java.version>11</java.version>
        <maven.compiler.source>${java.version}</maven.compiler.source>
        <maven.compiler.target>${java.version}</maven.compiler.target>
        
        <!-- 依赖版本统一管理 -->
        <spring.version>5.3.23</spring.version>
        <junit.version>5.9.2</junit.version>
    </properties>
</project>
```

---

## 依赖管理最佳实践

### 3. 使用 dependencyManagement

```xml
<!-- 在父 POM 中统一管理版本 -->
<dependencyManagement>
    <dependencies>
        <!-- Spring BOM -->
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-framework-bom</artifactId>
            <version>${spring.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
        
        <!-- 统一版本声明 -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>${junit.version}</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<!-- 子模块无需指定版本 -->
<dependencies>
    <dependency>
        <groupId>org.springframework</groupId>
        <artifactId>spring-context</artifactId>
        <!-- 版本由 dependencyManagement 管理 -->
    </dependency>
</dependencies>
```

### 4. 依赖范围最佳实践

| Scope | 编译 | 测试 | 运行 | 打包 | 使用场景 |
|-------|------|------|------|------|---------|
| compile | ✓ | ✓ | ✓ | ✓ | 默认值，大部分依赖 |
| provided | ✓ | ✓ | ✗ | ✗ | Servlet API, Lombok |
| runtime | ✗ | ✓ | ✓ | ✓ | JDBC 驱动 |
| test | ✗ | ✓ | ✗ | ✗ | JUnit, Mockito |
| system | ✓ | ✓ | ✗ | ✗ | 本地 JAR（不推荐） |

```xml
<dependencies>
    <!-- 编译时需要，运行时由容器提供 -->
    <dependency>
        <groupId>javax.servlet</groupId>
        <artifactId>javax.servlet-api</artifactId>
        <version>4.0.1</version>
        <scope>provided</scope>
    </dependency>
    
    <!-- 仅测试时需要 -->
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <scope>test</scope>
    </dependency>
    
    <!-- 编译时不需要，运行时需要 -->
    <dependency>
        <groupId>mysql</groupId>
        <artifactId>mysql-connector-java</artifactId>
        <version>8.0.33</version>
        <scope>runtime</scope>
    </dependency>
</dependencies>
```

### 5. 排除传递依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <exclusions>
        <!-- 排除默认日志框架 -->
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-logging</artifactId>
        </exclusion>
    </exclusions>
</dependency>

<!-- 使用其他日志框架 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-log4j2</artifactId>
</dependency>
```

### 6. 依赖分析

```bash
# 分析未使用的依赖
mvn dependency:analyze

# 输出示例：
# Used undeclared dependencies: 需要显式声明
# Unused declared dependencies: 可以移除
```

---

## 构建配置最佳实践

### 7. 编译器配置

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.11.0</version>
            <configuration>
                <source>${java.version}</source>
                <target>${java.version}</target>
                <encoding>${project.build.sourceEncoding}</encoding>
                
                <!-- 启用编译器警告 -->
                <compilerArgs>
                    <arg>-Xlint:unchecked</arg>
                    <arg>-Xlint:deprecation</arg>
                </compilerArgs>
                
                <!-- 显示警告 -->
                <showWarnings>true</showWarnings>
                <showDeprecation>true</showDeprecation>
            </configuration>
        </plugin>
    </plugins>
</build>
```

### 8. 资源过滤

```xml
<build>
    <resources>
        <resource>
            <directory>src/main/resources</directory>
            <filtering>true</filtering>
            <includes>
                <include>**/application*.properties</include>
                <include>**/application*.yml</include>
            </includes>
        </resource>
        <resource>
            <directory>src/main/resources</directory>
            <filtering>false</filtering>
            <excludes>
                <exclude>**/application*.properties</exclude>
                <exclude>**/application*.yml</exclude>
            </excludes>
        </resource>
    </resources>
</build>

<!-- application.properties -->
# 变量会被替换
app.version=${project.version}
app.name=${project.name}
```

### 9. Profile 配置

```xml
<profiles>
    <!-- 开发环境 -->
    <profile>
        <id>dev</id>
        <activation>
            <activeByDefault>true</activeByDefault>
        </activation>
        <properties>
            <env>dev</env>
            <db.url>jdbc:mysql://localhost:3306/dev_db</db.url>
        </properties>
    </profile>
    
    <!-- 生产环境 -->
    <profile>
        <id>prod</id>
        <properties>
            <env>prod</env>
            <db.url>jdbc:mysql://prod-db:3306/prod_db</db.url>
        </properties>
    </profile>
</profiles>

<!-- 使用方式：mvn clean install -Pprod -->
```

---

## 多模块项目最佳实践

### 10. 父 POM 配置

```xml
<!-- parent-pom/pom.xml -->
<project>
    <groupId>com.example</groupId>
    <artifactId>parent-pom</artifactId>
    <version>1.0.0</version>
    <packaging>pom</packaging>
    
    <modules>
        <module>common</module>
        <module>service</module>
        <module>web</module>
    </modules>
    
    <!-- 统一管理依赖版本 -->
    <dependencyManagement>
        <!-- ... -->
    </dependencyManagement>
    
    <!-- 统一管理插件版本 -->
    <pluginManagement>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
            </plugin>
        </plugins>
    </pluginManagement>
    
    <!-- 全局插件配置 -->
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <configuration>
                    <source>11</source>
                    <target>11</target>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

### 11. 子模块配置

```xml
<!-- web/pom.xml -->
<project>
    <parent>
        <groupId>com.example</groupId>
        <artifactId>parent-pom</artifactId>
        <version>1.0.0</version>
    </parent>
    
    <artifactId>web</artifactId>
    <packaging>war</packaging>
    
    <dependencies>
        <!-- 内部依赖 -->
        <dependency>
            <groupId>com.example</groupId>
            <artifactId>common</artifactId>
            <version>${project.version}</version>
        </dependency>
        
        <!-- 外部依赖（版本由父 POM 管理） -->
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-webmvc</artifactId>
        </dependency>
    </dependencies>
</project>
```

### 12. 模块间依赖原则

```
最佳实践：
- web 依赖 service
- service 依赖 common
- common 不依赖其他模块（基础模块）
- 模块依赖应该是单向的，避免循环依赖
```

---

## 性能优化最佳实践

### 13. 并行构建

```bash
# 使用 4 个线程并行构建
mvn -T 4 clean install

# 根据 CPU 核心数自动分配
mvn -T 1C clean install

# 在 .mvn/maven.config 中配置
-T 4
```

### 14. 增量构建

```bash
# 仅构建指定模块及其依赖
mvn -pl web -am clean install

# 仅构建指定模块及其被依赖的模块
mvn -pl common -amd clean install

# 离线模式（依赖已下载）
mvn -o clean install
```

### 15. 跳过耗时操作

```bash
# 跳过测试
mvn clean install -DskipTests

# 跳过测试编译
mvn clean install -Dmaven.test.skip=true

# 跳过 Javadoc 生成
mvn clean install -Dmaven.javadoc.skip=true

# 跳过 Checkstyle
mvn clean install -Dcheckstyle.skip=true
```

### 16. 构建缓存

```xml
<!-- 配置构建缓存插件 -->
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-build-cache-plugin</artifactId>
    <version>1.0.0</version>
    <configuration>
        <enabled>true</enabled>
    </configuration>
</plugin>
```

---

## 安全最佳实践

### 17. 加密敏感信息

```xml
<!-- 使用 Maven 加密功能 -->
<!-- 1. 创建主密码 -->
mvn --encrypt-master-password <password>

<!-- 2. 在 ~/.m2/settings-security.xml 中存储 -->
<settingsSecurity>
    <master>{加密后的主密码}</master>
</settingsSecurity>

<!-- 3. 加密服务器密码 -->
mvn --encrypt-password <password>

<!-- 4. 在 settings.xml 中使用 -->
<server>
    <id>private-repo</id>
    <username>user</username>
    <password>{加密后的密码}</password>
</server>
```

### 18. 依赖安全检查

```xml
<!-- 使用 OWASP Dependency Check -->
<plugin>
    <groupId>org.owasp</groupId>
    <artifactId>dependency-check-maven</artifactId>
    <version>8.2.1</version>
    <configuration>
        <failBuildOnCVSS>7</failBuildOnCVSS>
    </configuration>
    <executions>
        <execution>
            <goals>
                <goal>check</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

### 19. 签名验证

```xml
<!-- 验证依赖签名 -->
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-gpg-plugin</artifactId>
    <version>3.1.0</version>
    <executions>
        <execution>
            <id>sign-artifacts</id>
            <phase>verify</phase>
            <goals>
                <goal>sign</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

---

## CI/CD 最佳实践

### 20. Maven Wrapper

```bash
# 使用 Maven Wrapper 确保版本一致性
mvn wrapper:wrapper

# 生成的文件
.mvn/wrapper/maven-wrapper.jar
.mvn/wrapper/maven-wrapper.properties
mvnw
mvnw.cmd

# 使用 wrapper 构建项目
./mvnw clean install
```

### 21. 构建参数推荐

```bash
# CI 环境推荐参数
./mvnw clean verify \
  -DskipTests=false \
  -Dmaven.test.failure.ignore=false \
  -Dmaven.javadoc.skip=true \
  -T 2C \
  --batch-mode \
  --no-transfer-progress
```

---

## 常用命令速查

```bash
# 清理构建
mvn clean

# 编译
mvn compile

# 打包
mvn package

# 安装到本地仓库
mvn install

# 部署到远程仓库
mvn deploy

# 查看依赖树
mvn dependency:tree

# 分析依赖
mvn dependency:analyze

# 更新快照
mvn clean install -U

# 查看有效 POM
mvn help:effective-pom

# 查看活动 Profile
mvn help:active-profiles

# 运行特定主类
mvn exec:java -Dexec.mainClass="com.example.Main"

# 生成项目站点
mvn site
```

---

## 总结

遵循这些最佳实践可以：
- ✅ 提高构建速度和稳定性
- ✅ 减少依赖冲突
- ✅ 提升代码质量
- ✅ 简化团队协作
- ✅ 增强安全性

定期审查和优化 Maven 配置，保持项目的健康状态。
