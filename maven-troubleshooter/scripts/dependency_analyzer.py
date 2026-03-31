#!/usr/bin/env python3
"""
Maven 依赖分析器

功能：
1. 解析 pom.xml 文件
2. 构建依赖树
3. 检测版本冲突
4. 识别重复依赖
5. 检查依赖更新
6. 扫描安全漏洞

使用方式：
    python dependency_analyzer.py --pom ./pom.xml --output ./report.json
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from xml.etree import ElementTree as ET
from collections import defaultdict


class DependencyAnalyzer:
    """依赖分析器"""
    
    def __init__(self, pom_path: str):
        """
        初始化
        
        Args:
            pom_path: pom.xml 文件路径
        """
        self.pom_path = Path(pom_path)
        self.dependencies = []
        self.dependency_tree = {}
        self.conflicts = []
        self.duplicates = []
        
    def parse_pom(self) -> Dict[str, Any]:
        """
        解析 pom.xml 文件
        
        Returns:
            解析结果
        """
        if not self.pom_path.exists():
            return {
                "success": False,
                "error": f"pom.xml 文件不存在: {self.pom_path}"
            }
        
        try:
            tree = ET.parse(self.pom_path)
            root = tree.getroot()
            
            # Maven POM 命名空间
            ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
            
            result = {
                "success": True,
                "project": {},
                "dependencies": [],
                "dependencyManagement": [],
                "repositories": []
            }
            
            # 解析项目信息
            groupId = root.find('m:groupId', ns)
            artifactId = root.find('m:artifactId', ns)
            version = root.find('m:version', ns)
            
            if groupId is not None:
                result['project']['groupId'] = groupId.text
            if artifactId is not None:
                result['project']['artifactId'] = artifactId.text
            if version is not None:
                result['project']['version'] = version.text
            
            # 解析依赖
            dependencies = root.findall('.//m:dependencies/m:dependency', ns)
            for dep in dependencies:
                dep_info = self._parse_dependency(dep, ns)
                if dep_info:
                    result['dependencies'].append(dep_info)
            
            # 解析 dependencyManagement
            dep_mgmt = root.findall('.//m:dependencyManagement/m:dependencies/m:dependency', ns)
            for dep in dep_mgmt:
                dep_info = self._parse_dependency(dep, ns)
                if dep_info:
                    result['dependencyManagement'].append(dep_info)
            
            # 解析仓库
            repositories = root.findall('.//m:repositories/m:repository', ns)
            for repo in repositories:
                repo_info = {
                    'id': repo.find('m:id', ns).text if repo.find('m:id', ns) is not None else None,
                    'url': repo.find('m:url', ns).text if repo.find('m:url', ns) is not None else None
                }
                if repo_info['id'] and repo_info['url']:
                    result['repositories'].append(repo_info)
            
            self.dependencies = result['dependencies']
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"解析 pom.xml 失败: {str(e)}"
            }
    
    def _parse_dependency(self, dep_element, ns: dict) -> Optional[Dict[str, str]]:
        """解析单个依赖元素"""
        try:
            dep_info = {
                'groupId': dep_element.find('m:groupId', ns).text if dep_element.find('m:groupId', ns) is not None else None,
                'artifactId': dep_element.find('m:artifactId', ns).text if dep_element.find('m:artifactId', ns) is not None else None,
                'version': dep_element.find('m:version', ns).text if dep_element.find('m:version', ns) is not None else None,
                'scope': dep_element.find('m:scope', ns).text if dep_element.find('m:scope', ns) is not None else 'compile',
                'optional': dep_element.find('m:optional', ns).text if dep_element.find('m:optional', ns) is not None else 'false'
            }
            
            if dep_info['groupId'] and dep_info['artifactId']:
                return dep_info
            return None
        except Exception:
            return None
    
    def analyze_dependencies(self) -> Dict[str, Any]:
        """
        分析依赖树和冲突
        
        Returns:
            分析结果
        """
        # 使用 Maven 命令获取依赖树
        try:
            result = subprocess.run(
                ['mvn', 'dependency:tree', '-DoutputType=dot'],
                cwd=self.pom_path.parent,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                dependency_tree_output = result.stdout
                self._parse_dependency_tree(dependency_tree_output)
            else:
                # 如果 Maven 命令失败，使用基础解析
                self._build_simple_tree()
                
        except Exception as e:
            # Maven 命令失败，使用基础解析
            self._build_simple_tree()
        
        # 检测冲突
        self._detect_conflicts()
        
        # 检测重复
        self._detect_duplicates()
        
        return {
            "success": True,
            "total_dependencies": len(self.dependencies),
            "conflicts": self.conflicts,
            "duplicates": self.duplicates,
            "dependency_tree": self.dependency_tree
        }
    
    def _parse_dependency_tree(self, output: str):
        """解析 Maven 依赖树输出"""
        # 简化的依赖树解析
        lines = output.split('\n')
        for line in lines:
            # 提取依赖信息: groupId:artifactId:version:scope
            match = re.search(r'([a-zA-Z0-9_.-]+):([a-zA-Z0-9_.-]+):([a-zA-Z0-9_.-]+)', line)
            if match:
                dep_key = f"{match.group(1)}:{match.group(2)}"
                version = match.group(3)
                
                if dep_key not in self.dependency_tree:
                    self.dependency_tree[dep_key] = []
                if version not in self.dependency_tree[dep_key]:
                    self.dependency_tree[dep_key].append(version)
    
    def _build_simple_tree(self):
        """构建简单依赖树"""
        for dep in self.dependencies:
            dep_key = f"{dep['groupId']}:{dep['artifactId']}"
            if dep['version']:
                if dep_key not in self.dependency_tree:
                    self.dependency_tree[dep_key] = []
                if dep['version'] not in self.dependency_tree[dep_key]:
                    self.dependency_tree[dep_key].append(dep['version'])
    
    def _detect_conflicts(self):
        """检测版本冲突"""
        for dep_key, versions in self.dependency_tree.items():
            if len(versions) > 1:
                self.conflicts.append({
                    "dependency": dep_key,
                    "versions": versions,
                    "severity": "HIGH" if len(versions) > 2 else "MEDIUM",
                    "recommendation": f"在 dependencyManagement 中统一 {dep_key} 的版本"
                })
    
    def _detect_duplicates(self):
        """检测重复依赖"""
        seen = {}
        for dep in self.dependencies:
            key = f"{dep['groupId']}:{dep['artifactId']}"
            if key in seen:
                self.duplicates.append({
                    "dependency": key,
                    "occurrences": [seen[key], dep],
                    "recommendation": "移除重复的依赖声明"
                })
            else:
                seen[key] = dep
    
    def check_updates(self) -> Dict[str, Any]:
        """
        检查依赖更新
        
        Returns:
            更新检查结果
        """
        updates = []
        
        try:
            result = subprocess.run(
                ['mvn', 'versions:display-dependency-updates'],
                cwd=self.pom_path.parent,
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result.returncode == 0:
                # 解析输出，提取可更新的依赖
                output = result.stdout
                lines = output.split('\n')
                
                for line in lines:
                    # 提取更新信息
                    match = re.search(r'([a-zA-Z0-9_.-]+):([a-zA-Z0-9_.-]+) .* (\d+\.\d+\.\d+) -> (\d+\.\d+\.\d+)', line)
                    if match:
                        updates.append({
                            "groupId": match.group(1),
                            "artifactId": match.group(2),
                            "current_version": match.group(3),
                            "available_version": match.group(4)
                        })
        
        except Exception:
            pass
        
        return {
            "success": True,
            "updates_available": len(updates),
            "updates": updates
        }
    
    def check_vulnerabilities(self) -> Dict[str, Any]:
        """
        检查安全漏洞（使用 OWASP Dependency Check）
        
        Returns:
            漏洞检查结果
        """
        vulnerabilities = []
        
        try:
            # 尝试运行 OWASP Dependency Check
            result = subprocess.run(
                ['mvn', 'org.owasp:dependency-check-maven:check'],
                cwd=self.pom_path.parent,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # 解析结果（简化版）
            if result.returncode != 0:
                vulnerabilities.append({
                    "note": "OWASP Dependency Check 未安装或配置，建议安装以进行安全检查",
                    "recommendation": "添加 dependency-check-maven 插件到 pom.xml"
                })
        
        except Exception as e:
            vulnerabilities.append({
                "note": f"安全检查失败: {str(e)}",
                "recommendation": "手动检查依赖的安全性，或安装 OWASP Dependency Check 插件"
            })
        
        return {
            "success": True,
            "vulnerabilities_found": len(vulnerabilities),
            "vulnerabilities": vulnerabilities
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """
        生成完整报告
        
        Returns:
            完整分析报告
        """
        # 解析 pom.xml
        pom_result = self.parse_pom()
        if not pom_result['success']:
            return pom_result
        
        # 分析依赖
        analysis_result = self.analyze_dependencies()
        
        report = {
            "success": True,
            "timestamp": self._get_timestamp(),
            "project": pom_result['project'],
            "summary": {
                "total_dependencies": analysis_result['total_dependencies'],
                "conflicts_found": len(self.conflicts),
                "duplicates_found": len(self.duplicates)
            },
            "dependencies": pom_result['dependencies'],
            "conflicts": self.conflicts,
            "duplicates": self.duplicates,
            "dependency_tree": self.dependency_tree,
            "repositories": pom_result['repositories'],
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """生成改进建议"""
        recommendations = []
        
        # 冲突建议
        if self.conflicts:
            recommendations.append({
                "type": "CONFLICT",
                "priority": "HIGH",
                "message": f"发现 {len(self.conflicts)} 个依赖版本冲突",
                "action": "在 dependencyManagement 中统一版本，或使用 exclusion 排除冲突依赖"
            })
        
        # 重复建议
        if self.duplicates:
            recommendations.append({
                "type": "DUPLICATE",
                "priority": "MEDIUM",
                "message": f"发现 {len(self.duplicates)} 个重复依赖",
                "action": "移除重复的依赖声明"
            })
        
        # 仓库建议
        recommendations.append({
            "type": "PERFORMANCE",
            "priority": "LOW",
            "message": "建议配置镜像仓库以加速依赖下载",
            "action": "在 settings.xml 中配置阿里云或华为云镜像"
        })
        
        return recommendations
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Maven 依赖分析器")
    parser.add_argument("--pom", required=True, help="pom.xml 文件路径")
    parser.add_argument("--output", default="dependency-report.json", help="输出报告路径")
    parser.add_argument("--check-updates", action="store_true", help="检查依赖更新")
    parser.add_argument("--check-vulnerabilities", action="store_true", help="检查安全漏洞")
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = DependencyAnalyzer(args.pom)
    
    # 生成报告
    report = analyzer.generate_report()
    
    # 检查更新
    if args.check_updates:
        updates = analyzer.check_updates()
        report['updates'] = updates
    
    # 检查漏洞
    if args.check_vulnerabilities:
        vulnerabilities = analyzer.check_vulnerabilities()
        report['security'] = vulnerabilities
    
    # 保存报告
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # 输出摘要
    if report['success']:
        print(f"\n✓ 分析完成")
        print(f"项目: {report['project'].get('groupId', 'N/A')}:{report['project'].get('artifactId', 'N/A')}")
        print(f"总依赖数: {report['summary']['total_dependencies']}")
        print(f"版本冲突: {report['summary']['conflicts_found']}")
        print(f"重复依赖: {report['summary']['duplicates_found']}")
        print(f"\n报告已保存: {output_path}")
        
        if report['conflicts']:
            print(f"\n⚠ 发现冲突:")
            for conflict in report['conflicts'][:3]:
                print(f"  - {conflict['dependency']}: {', '.join(conflict['versions'])}")
    else:
        print(f"✗ 分析失败: {report.get('error', '未知错误')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
