# Maven 常见问题手册

本文档整理了 Maven 构建过程中最常见的 50+ 问题及其解决方案。

## 目录

1. [依赖相关问题](#依赖相关问题)
2. [构建失败问题](#构建失败问题)
3. [插件配置问题](#插件配置问题)
4. [仓库与网络问题](#仓库与网络问题)
5. [性能优化问题](#性能优化问题)
6. [多模块问题](#多模块问题)
7. [版本管理问题](#版本管理问题)

---

## 依赖相关问题

### 1. NoSuchMethodError / ClassNotFoundException

**问题现象**：
```
java.lang.NoSuchMethodError: com.example.Class.method()V
java.lang.ClassNotFoundException: com.example.Class
```

**原因分析**：
- 依赖版本冲突
- 类加载顺序问题
- 传递依赖版本不一致

**解决方案**：
```bash
# 1. 查看依赖树
mvn dependency:tree -Dverbose

# 2. 在 dependencyManagement 中统一版本
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.example</groupId>
            <artifactId>example-lib</artifactId>
            <version>2.0.0</version>
        </dependency>
    </dependencies>
</dependencyManagement>

# 3. 排除冲突依赖
<dependency>
    <groupId>com.framework</groupId>
    <artifactId>framework-core</artifactId>
    <exclusions>
        <exclusion>
            <groupId>com.example</groupId>
            <artifactId>example-lib</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

### 2. 依赖下载失败

**问题现象**：
```
Could not resolve dependencies for project com.example:app:jar:1.0
Could not transfer artifact com.example:lib:jar:1.0 from/to central
```

**原因分析**：
- 网络连接问题
- 仓库配置错误
- 依赖不存在或版本错误

**解决方案**：
```bash
# 1. 强制更新依赖
mvn clean install -U

# 2. 检查仓库配置
cat ~/.m2/settings.xml

# 3. 清理本地缓存
rm -rf ~/.m2/repository/com/example/

# 4. 使用镜像仓库
<mirror>
    <id>aliyun</id>
    <mirrorOf>central</mirrorOf>
    <name>Aliyun Maven Mirror</name>
    <url>https://maven.aliyun.com/repository/public</url>
</mirror>
```

### 3. 依赖版本范围不明确

**问题现象**：
```
Dependency version is managed by parent but not specified
```

**解决方案**：
```xml
<!-- 方案1：明确指定版本 -->
<dependency>
    <groupId>com.example</groupId>
    <artifactId>lib</artifactId>
    <version>1.0.0</version>
</dependency>

<!-- 方案2：使用属性管理 -->
<properties>
    <lib.version>1.0.0</lib.version>
</properties>

<dependency>
    <groupId>com.example</groupId>
    <artifactId>lib</artifactId>
    <version>${lib.version}</version>
</dependency>
```

### 4. 重复依赖声明

**问题现象**：
```
omitted for duplicate
```

**解决方案**：
```xml
<!-- 检查并移除重复声明 -->
<!-- 错误示例 -->
<dependencies>
    <dependency>
        <groupId>com.example</groupId>
        <artifactId>lib</artifactId>
        <version>1.0.0</version>
    </dependency>
    <!-- 重复声明 -->
    <dependency>
        <groupId>com.example</groupId>
        <artifactId>lib</artifactId>
        <version>1.0.0</version>
        <scope>test</scope>
    </dependency>
</dependencies>

<!-- 正确示例 -->
<dependencies>
    <dependency>
        <groupId>com.example</groupId>
        <artifactId>lib</artifactId>
        <version>1.0.0</version>
        <scope>compile</scope> <!-- 默认值 -->
    </dependency>
</dependencies>
```

### 5. 快照版本问题

**问题现象**：
```
SNAPSHOT dependencies not updating
```

**解决方案**：
```bash
# 强制更新快照版本
mvn clean install -U

# 或在 pom.xml 中配置更新策略
<repository>
    <id>snapshots</id>
    <url>https://repo.example.com/snapshots</url>
    <releases>
        <enabled>false</enabled>
    </releases>
    <snapshots>
        <enabled>true</enabled>
        <updatePolicy>always</updatePolicy>
    </snapshots>
</repository>
```

---

## 构建失败问题

### 6. 编译错误 - 源版本不匹配

**问题现象**：
```
Source option 5 is no longer supported. Use 6 or later.
```

**解决方案**：
```xml
<properties>
    <maven.compiler.source>11</maven.compiler.source>
    <maven.compiler.target>11</maven.compiler.target>
    <java.version>11</java.version>
</properties>
```

### 7. 编码问题

**问题现象**：
```
unmappable character for encoding UTF-8
```

**解决方案**：
```xml
<properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
</properties>

<!-- 或在编译插件中配置 -->
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <configuration>
        <encoding>UTF-8</encoding>
    </configuration>
</plugin>
```

### 8. 测试失败

**问题现象**：
```
Tests run: 10, Failures: 2, Errors: 1, Skipped: 0
```

**解决方案**：
```bash
# 1. 运行单个测试定位问题
mvn test -Dtest=TestClassName

# 2. 查看详细输出
mvn test -X

# 3. 跳过测试验证构建
mvn install -DskipTests

# 4. 排除特定测试
mvn test -Dtest=!SlowTest
```

### 9. 打包失败 - 资源文件缺失

**问题现象**：
```
Failed to execute goal org.apache.maven.plugins:maven-resources-plugin
```

**解决方案**：
```xml
<!-- 配置资源目录 -->
<build>
    <resources>
        <resource>
            <directory>src/main/resources</directory>
            <includes>
                <include>**/*.properties</include>
                <include>**/*.xml</include>
            </includes>
            <filtering>true</filtering> <!-- 启用变量替换 -->
        </resource>
    </resources>
</build>
```

### 10. 内存不足

**问题现象**：
```
OutOfMemoryError: Java heap space
```

**解决方案**：
```bash
# 方案1：设置环境变量
export MAVEN_OPTS="-Xmx2048m -XX:MaxMetaspaceSize=512m"

# 方案2：在 .mavenrc 文件中配置
echo 'MAVEN_OPTS="-Xmx2048m"' > ~/.mavenrc

# 方案3：使用并行构建减少内存占用
mvn -T 4 clean install
```

---

## 插件配置问题

### 11. 插件版本未指定

**问题现象**：
```
Plugin version not specified, using latest
```

**解决方案**：
```xml
<build>
    <pluginManagement>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
            </plugin>
        </plugins>
    </pluginManagement>
</build>
```

### 12. Surefire 插件测试配置

**问题现象**：
```
No tests were executed
```

**解决方案**：
```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <version>3.0.0</version>
    <configuration>
        <includes>
            <include>**/*Test.java</include>
            <include>**/*Tests.java</include>
        </includes>
        <parallel>methods</parallel>
        <threadCount>4</threadCount>
    </configuration>
</plugin>
```

### 13. JAR 插件配置错误

**问题现象**：
```
JAR will be empty - no content was marked for inclusion
```

**解决方案**：
```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-jar-plugin</artifactId>
    <version>3.3.0</version>
    <configuration>
        <archive>
            <manifest>
                <mainClass>com.example.Main</mainClass>
                <addClasspath>true</addClasspath>
            </manifest>
        </archive>
    </configuration>
</plugin>
```

### 14. Shade 插件类冲突

**问题现象**：
```
Duplicate class found during shading
```

**解决方案**：
```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-shade-plugin</artifactId>
    <configuration>
        <relocations>
            <relocation>
                <pattern>com.google.common</pattern>
                <shadedPattern>shaded.com.google.common</shadedPattern>
            </relocation>
        </relocations>
        <filters>
            <filter>
                <artifact>*:*</artifact>
                <excludes>
                    <exclude>META-INF/*.SF</exclude>
                    <exclude>META-INF/*.DSA</exclude>
                    <exclude>META-INF/*.RSA</exclude>
                </excludes>
            </filter>
        </filters>
    </configuration>
</plugin>
```

---

## 仓库与网络问题

### 15. 无法连接中央仓库

**问题现象**：
```
Connection refused to https://repo.maven.apache.org
```

**解决方案**：
```xml
<!-- 配置镜像仓库 -->
<mirrors>
    <mirror>
        <id>aliyun</id>
        <mirrorOf>central</mirrorOf>
        <name>Aliyun Maven Mirror</name>
        <url>https://maven.aliyun.com/repository/public</url>
    </mirror>
</mirrors>
```

### 16. 私服认证失败

**问题现象**：
```
Authentication failed for https://repo.example.com
```

**解决方案**：
```xml
<!-- 在 settings.xml 中配置认证信息 -->
<servers>
    <server>
        <id>private-repo</id>
        <username>your-username</username>
        <password>your-password</password>
    </server>
</servers>
```

### 17. 代理配置

**问题现象**：
```
Unable to tunnel through proxy
```

**解决方案**：
```xml
<!-- 在 settings.xml 中配置代理 -->
<proxies>
    <proxy>
        <id>company-proxy</id>
        <active>true</active>
        <protocol>https</protocol>
        <host>proxy.example.com</host>
        <port>8080</port>
        <username>proxyuser</username>
        <password>proxypass</password>
    </proxy>
</proxies>
```

### 18. 本地仓库损坏

**问题现象**：
```
Invalid CEN header (bad signature)
```

**解决方案**：
```bash
# 1. 清理特定依赖
rm -rf ~/.m2/repository/com/example/

# 2. 清理所有缓存
mvn dependency:purge-local-repository

# 3. 删除并重建仓库
rm -rf ~/.m2/repository
mvn clean install
```

---

## 性能优化问题

### 19. 构建缓慢

**问题现象**：
构建耗时超过 10 分钟

**解决方案**：
```bash
# 1. 启用并行构建
mvn -T 4 clean install

# 2. 使用离线模式
mvn -o clean install

# 3. 构建指定模块
mvn -pl module1,module2 clean install

# 4. 跳过不必要的步骤
mvn clean install -DskipTests -Dmaven.javadoc.skip=true
```

### 20. 依赖下载缓慢

**解决方案**：
```xml
<!-- 配置多个镜像 -->
<mirrors>
    <mirror>
        <id>aliyun</id>
        <mirrorOf>central</mirrorOf>
        <url>https://maven.aliyun.com/repository/public</url>
    </mirror>
    <mirror>
        <id>huawei</id>
        <mirrorOf>central</mirrorOf>
        <url>https://repo.huaweicloud.com/repository/maven/</url>
    </mirror>
</mirrors>
```

---

## 多模块问题

### 21. 模块依赖顺序

**问题现象**：
```
Could not resolve dependencies for module
```

**解决方案**：
```xml
<!-- 确保正确的模块顺序 -->
<modules>
    <module>common</module>
    <module>service</module>
    <module>web</module>
</modules>

<!-- 在子模块中正确声明依赖 -->
<dependencies>
    <dependency>
        <groupId>com.example</groupId>
        <artifactId>common</artifactId>
        <version>${project.version}</version>
    </dependency>
</dependencies>
```

### 22. 版本不一致

**问题现象**：
```
Version mismatch between parent and child
```

**解决方案**：
```xml
<!-- 父 pom -->
<properties>
    <project.version>1.0.0</project.version>
</properties>

<!-- 子模块 -->
<parent>
    <groupId>com.example</groupId>
    <artifactId>parent</artifactId>
    <version>${project.version}</version>
</parent>
```

---

## 版本管理问题

### 23. 版本更新检查

**解决方案**：
```bash
# 检查依赖更新
mvn versions:display-dependency-updates

# 检查插件更新
mvn versions:display-plugin-updates

# 批量更新版本
mvn versions:use-latest-releases
```

### 24. 版本回退

**解决方案**：
```bash
# 设置指定版本
mvn versions:set -DnewVersion=1.0.1

# 回退版本更改
mvn versions:revert

# 确认版本更改
mvn versions:commit
```

---

## 高级问题

### 25. 自定义 Archetype 创建失败

**解决方案**：
```bash
# 创建 archetype
mvn archetype:create-from-project

# 安装 archetype
cd target/generated-sources/archetype
mvn install

# 使用 archetype
mvn archetype:generate \
  -DarchetypeGroupId=com.example \
  -DarchetypeArtifactId=my-archetype \
  -DarchetypeVersion=1.0.0 \
  -DgroupId=com.example \
  -DartifactId=new-project
```

### 26. Profile 不生效

**解决方案**：
```xml
<profiles>
    <profile>
        <id>dev</id>
        <activation>
            <activeByDefault>true</activeByDefault>
            <property>
                <name>env</name>
                <value>dev</value>
            </property>
        </activation>
        <properties>
            <db.url>jdbc:mysql://dev-db:3306/app</db.url>
        </properties>
    </profile>
</profiles>

<!-- 激活方式 -->
<!-- mvn clean install -Pdev -->
<!-- 或 mvn clean install -Denv=dev -->
```

### 27. Site 生成失败

**解决方案**：
```xml
<reporting>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-site-plugin</artifactId>
            <version>3.12.1</version>
        </plugin>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-project-info-reports-plugin</artifactId>
            <version>3.4.5</version>
        </plugin>
    </plugins>
</reporting>
```

---

## 快速诊断命令

```bash
# 查看依赖树
mvn dependency:tree

# 查看有效 POM
mvn help:effective-pom

# 查看活动 Profile
mvn help:active-profiles

# 分析依赖
mvn dependency:analyze

# 检查依赖范围
mvn dependency:analyze-only

# 查看插件信息
mvn help:describe -Dplugin=compiler

# 详细日志输出
mvn clean install -X

# 调试模式
mvn clean install -e
```

---

## 常见错误代码对照表

| 错误类型 | 常见原因 | 快速解决方案 |
|---------|---------|-------------|
| COMPILATION_ERROR | Java 版本不匹配 | 检查 maven.compiler.source/target |
| DEPENDENCY_MISSING | 依赖不存在或网络问题 | 检查仓库配置，强制更新 -U |
| TEST_FAILURE | 测试用例失败 | 运行单个测试定位问题 |
| PLUGIN_ERROR | 插件配置错误 | 检查插件版本和配置 |
| VERSION_CONFLICT | 依赖版本冲突 | 使用 dependencyManagement |
| OUT_OF_MEMORY | JVM 内存不足 | 设置 MAVEN_OPTS |
| PERMISSION_ERROR | 文件权限问题 | 检查文件权限和占用 |
| NETWORK_ERROR | 网络连接问题 | 配置镜像仓库 |
