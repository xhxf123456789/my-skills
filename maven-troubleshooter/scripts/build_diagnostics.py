#!/usr/bin/env python3
"""
Maven 构建诊断工具

功能：
1. 解析构建错误日志
2. 分类错误类型
3. 提供解决建议
4. 生成诊断报告

使用方式：
    python build_diagnostics.py --log build-error.log --output ./diagnosis.json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class BuildDiagnostics:
    """构建诊断工具"""
    
    def __init__(self, log_path: str):
        """
        初始化
        
        Args:
            log_path: 日志文件路径
        """
        self.log_path = Path(log_path)
        self.log_content = ""
        self.errors = []
        self.warnings = []
        self.diagnosis = {}
        
        # 错误模式定义
        self.error_patterns = {
            "COMPILATION_ERROR": {
                "patterns": [
                    r"COMPILATION ERROR",
                    r"\[ERROR\] .*\.java\[\d+,\d+\]",
                    r"cannot find symbol",
                    r"package .* does not exist"
                ],
                "category": "编译错误",
                "severity": "HIGH"
            },
            "DEPENDENCY_MISSING": {
                "patterns": [
                    r"Could not resolve dependencies",
                    r"Could not find artifact",
                    r"Failed to collect dependencies",
                    r"Cannot resolve .* dependency"
                ],
                "category": "依赖缺失",
                "severity": "HIGH"
            },
            "TEST_FAILURE": {
                "patterns": [
                    r"Tests run:.*Failures: \d+",
                    r"BUILD FAILURE.*test",
                    r"Failed tests:",
                    r"AssertionError"
                ],
                "category": "测试失败",
                "severity": "MEDIUM"
            },
            "PLUGIN_ERROR": {
                "patterns": [
                    r"Failed to execute goal.*plugin",
                    r"Plugin .* or one of its dependencies could not be resolved",
                    r"Error assembling EJB"
                ],
                "category": "插件错误",
                "severity": "HIGH"
            },
            "VERSION_CONFLICT": {
                "patterns": [
                    r"NoSuchMethodError",
                    r"ClassNotFoundException",
                    r"NoClassDefFoundError",
                    r"conflicts with"
                ],
                "category": "版本冲突",
                "severity": "HIGH"
            },
            "PERMISSION_ERROR": {
                "patterns": [
                    r"Permission denied",
                    r"Access is denied",
                    r"Cannot write to directory"
                ],
                "category": "权限错误",
                "severity": "HIGH"
            },
            "NETWORK_ERROR": {
                "patterns": [
                    r"Connection timed out",
                    r"Unknown host",
                    r"Could not transfer artifact",
                    r"Remote host terminated the handshake"
                ],
                "category": "网络错误",
                "severity": "MEDIUM"
            },
            "OUT_OF_MEMORY": {
                "patterns": [
                    r"OutOfMemoryError",
                    r"Java heap space",
                    r"GC overhead limit exceeded"
                ],
                "category": "内存不足",
                "severity": "HIGH"
            },
            "DUPLICATE_CLASS": {
                "patterns": [
                    r"duplicate class",
                    r"Duplicate class declaration",
                    r"class file has wrong version"
                ],
                "category": "类冲突",
                "severity": "MEDIUM"
            }
        }
        
        # 解决方案数据库
        self.solutions = {
            "COMPILATION_ERROR": [
                "检查 Java 版本是否匹配（pom.xml 中的 maven.compiler.source/target）",
                "确保所有依赖已正确声明",
                "检查源代码语法错误",
                "清理并重新构建: mvn clean compile"
            ],
            "DEPENDENCY_MISSING": [
                "检查依赖坐标是否正确（groupId、artifactId、version）",
                "检查仓库配置（settings.xml）",
                "尝试强制更新: mvn clean install -U",
                "检查网络连接和镜像配置"
            ],
            "TEST_FAILURE": [
                "检查测试用例代码",
                "运行单个测试定位问题: mvn test -Dtest=TestClassName",
                "检查测试依赖和配置",
                "跳过测试验证构建: mvn install -DskipTests"
            ],
            "PLUGIN_ERROR": [
                "检查插件版本兼容性",
                "清理本地缓存: mvn dependency:purge-local-repository",
                "检查插件配置参数",
                "更新插件版本: mvn versions:display-plugin-updates"
            ],
            "VERSION_CONFLICT": [
                "使用 mvn dependency:tree 查看依赖树",
                "在 dependencyManagement 中统一版本",
                "使用 exclusion 排除冲突依赖",
                "检查传递依赖版本"
            ],
            "PERMISSION_ERROR": [
                "检查文件和目录权限",
                "以管理员身份运行（Windows）",
                "检查文件是否被其他进程占用",
                "清理锁定文件: rm -rf ~/.m2/repository/.locks"
            ],
            "NETWORK_ERROR": [
                "检查网络连接",
                "配置镜像仓库（阿里云/华为云）",
                "检查防火墙和代理设置",
                "使用离线模式: mvn -o clean install（需先下载依赖）"
            ],
            "OUT_OF_MEMORY": [
                "增加 Maven 内存: export MAVEN_OPTS=\"-Xmx1024m\"",
                "使用并行构建: mvn -T 4 clean install",
                "减少构建范围: mvn -pl module1,module2",
                "清理本地仓库缓存"
            ],
            "DUPLICATE_CLASS": [
                "检查依赖是否有冲突",
                "使用 dependency:tree 查看依赖树",
                "排除重复的依赖",
                "检查 shaded 插件配置"
            ]
        }
    
    def read_log(self) -> bool:
        """
        读取日志文件
        
        Returns:
            是否成功读取
        """
        if not self.log_path.exists():
            return False
        
        try:
            with open(self.log_path, 'r', encoding='utf-8', errors='ignore') as f:
                self.log_content = f.read()
            return True
        except Exception:
            return False
    
    def diagnose(self) -> Dict[str, Any]:
        """
        诊断构建问题
        
        Returns:
            诊断结果
        """
        if not self.log_content:
            return {
                "success": False,
                "error": "日志内容为空"
            }
        
        # 提取错误信息
        self._extract_errors()
        
        # 匹配错误模式
        matched_errors = self._match_patterns()
        
        # 生成诊断结果
        diagnosis = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "log_file": str(self.log_path),
            "summary": {
                "total_errors": len(self.errors),
                "total_warnings": len(self.warnings),
                "error_categories": len(matched_errors)
            },
            "errors_by_category": matched_errors,
            "recommendations": self._generate_recommendations(matched_errors),
            "raw_errors": self.errors[:20],  # 限制输出
            "build_info": self._extract_build_info()
        }
        
        self.diagnosis = diagnosis
        return diagnosis
    
    def _extract_errors(self):
        """提取错误和警告信息"""
        lines = self.log_content.split('\n')
        
        for i, line in enumerate(lines):
            # 提取错误
            if '[ERROR]' in line:
                error_info = {
                    "line_number": i + 1,
                    "content": line.strip(),
                    "context": self._get_context(lines, i, 2)
                }
                self.errors.append(error_info)
            
            # 提取警告
            elif '[WARNING]' in line:
                warning_info = {
                    "line_number": i + 1,
                    "content": line.strip()
                }
                self.warnings.append(warning_info)
    
    def _get_context(self, lines: List[str], index: int, context_size: int) -> List[str]:
        """获取错误上下文"""
        start = max(0, index - context_size)
        end = min(len(lines), index + context_size + 1)
        return lines[start:end]
    
    def _match_patterns(self) -> Dict[str, Any]:
        """匹配错误模式"""
        matched = {}
        
        for error_type, config in self.error_patterns.items():
            matches = []
            for pattern in config['patterns']:
                regex = re.compile(pattern, re.IGNORECASE)
                for error in self.errors:
                    if regex.search(error['content']):
                        matches.append(error)
            
            if matches:
                matched[error_type] = {
                    "category": config['category'],
                    "severity": config['severity'],
                    "count": len(matches),
                    "solutions": self.solutions.get(error_type, []),
                    "sample_errors": matches[:3]  # 只显示前3个示例
                }
        
        return matched
    
    def _generate_recommendations(self, matched_errors: Dict[str, Any]) -> List[Dict[str, str]]:
        """生成改进建议"""
        recommendations = []
        
        # 按严重程度排序
        high_priority = []
        medium_priority = []
        
        for error_type, info in matched_errors.items():
            rec = {
                "type": error_type,
                "category": info['category'],
                "severity": info['severity'],
                "count": info['count'],
                "solutions": info['solutions']
            }
            
            if info['severity'] == 'HIGH':
                high_priority.append(rec)
            else:
                medium_priority.append(rec)
        
        recommendations.extend(high_priority)
        recommendations.extend(medium_priority)
        
        return recommendations
    
    def _extract_build_info(self) -> Dict[str, str]:
        """提取构建信息"""
        info = {}
        
        # 提取项目坐标
        project_match = re.search(r'Building ([^\s]+) ([\d\.]+)', self.log_content)
        if project_match:
            info['project_name'] = project_match.group(1)
            info['project_version'] = project_match.group(2)
        
        # 提取 Maven 版本
        maven_match = re.search(r'Apache Maven ([\d\.]+)', self.log_content)
        if maven_match:
            info['maven_version'] = maven_match.group(1)
        
        # 提取 Java 版本
        java_match = re.search(r'Java version: ([\d\._]+)', self.log_content)
        if java_match:
            info['java_version'] = java_match.group(1)
        
        # 提取构建时间
        time_match = re.search(r'Total time: ([\d:]+)', self.log_content)
        if time_match:
            info['build_time'] = time_match.group(1)
        
        return info
    
    def save_report(self, output_path: str):
        """保存诊断报告"""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(self.diagnosis, f, indent=2, ensure_ascii=False)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Maven 构建诊断工具")
    parser.add_argument("--log", required=True, help="构建日志文件路径")
    parser.add_argument("--output", default="diagnosis.json", help="诊断报告输出路径")
    
    args = parser.parse_args()
    
    # 创建诊断工具
    diagnostics = BuildDiagnostics(args.log)
    
    # 读取日志
    if not diagnostics.read_log():
        print(f"✗ 无法读取日志文件: {args.log}", file=sys.stderr)
        sys.exit(1)
    
    # 执行诊断
    result = diagnostics.diagnose()
    
    # 保存报告
    diagnostics.save_report(args.output)
    
    # 输出摘要
    if result['success']:
        print(f"\n✓ 诊断完成")
        print(f"错误总数: {result['summary']['total_errors']}")
        print(f"警告总数: {result['summary']['total_warnings']}")
        print(f"错误分类: {result['summary']['error_categories']}")
        
        if result['recommendations']:
            print(f"\n⚠ 高优先级问题:")
            for rec in result['recommendations'][:3]:
                print(f"  - [{rec['severity']}] {rec['category']}: {rec['count']} 个错误")
                if rec['solutions']:
                    print(f"    建议: {rec['solutions'][0]}")
        
        print(f"\n详细报告: {args.output}")
    else:
        print(f"✗ 诊断失败: {result.get('error', '未知错误')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
