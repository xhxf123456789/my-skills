#!/usr/bin/env python3
"""
Maven 仓库健康检查工具

功能：
1. 检查本地仓库状态
2. 清理损坏的依赖
3. 识别快照版本问题
4. 验证镜像配置

使用方式：
    python repository_checker.py --action check --output ./repo-health.json
    python repository_checker.py --action clean --dependency groupId:artifactId:version
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class RepositoryChecker:
    """仓库健康检查工具"""
    
    def __init__(self):
        """初始化"""
        self.repo_path = self._get_local_repo_path()
        self.settings_path = self._get_settings_path()
        self.health_issues = []
        
    def _get_local_repo_path(self) -> Path:
        """获取本地仓库路径"""
        # 默认路径
        default_path = Path.home() / '.m2' / 'repository'
        
        # 检查环境变量
        m2_repo = os.environ.get('M2_REPO')
        if m2_repo:
            return Path(m2_repo)
        
        # 检查 settings.xml
        settings_path = Path.home() / '.m2' / 'settings.xml'
        if settings_path.exists():
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(settings_path)
                root = tree.getroot()
                local_repo = root.find('.//localRepository')
                if local_repo is not None:
                    return Path(local_repo.text)
            except Exception:
                pass
        
        return default_path
    
    def _get_settings_path(self) -> Path:
        """获取 settings.xml 路径"""
        return Path.home() / '.m2' / 'settings.xml'
    
    def check_repository(self) -> Dict[str, Any]:
        """
        检查仓库健康状态
        
        Returns:
            健康检查结果
        """
        result = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "repository_path": str(self.repo_path),
            "repository_exists": self.repo_path.exists(),
            "statistics": {},
            "issues": [],
            "recommendations": []
        }
        
        if not self.repo_path.exists():
            result['success'] = False
            result['issues'].append({
                "type": "REPOSITORY_NOT_FOUND",
                "severity": "CRITICAL",
                "message": f"本地仓库不存在: {self.repo_path}",
                "solution": "运行 Maven 命令创建仓库，或检查配置"
            })
            return result
        
        # 统计仓库信息
        result['statistics'] = self._collect_statistics()
        
        # 检查损坏的依赖
        corrupted = self._check_corrupted_dependencies()
        if corrupted:
            result['issues'].append({
                "type": "CORRUPTED_DEPENDENCIES",
                "severity": "HIGH",
                "count": len(corrupted),
                "dependencies": corrupted[:10],
                "solution": "清理损坏的依赖: python repository_checker.py --action clean"
            })
        
        # 检查快照版本
        snapshots = self._check_snapshot_versions()
        if snapshots['old_snapshots']:
            result['issues'].append({
                "type": "OLD_SNAPSHOTS",
                "severity": "MEDIUM",
                "count": len(snapshots['old_snapshots']),
                "snapshots": snapshots['old_snapshots'][:10],
                "solution": "更新快照版本: mvn clean install -U"
            })
        
        # 检查磁盘空间
        disk_space = self._check_disk_space()
        if disk_space['usage_percent'] > 80:
            result['issues'].append({
                "type": "DISK_SPACE_WARNING",
                "severity": "LOW",
                "message": f"磁盘使用率: {disk_space['usage_percent']}%",
                "solution": "清理未使用的依赖，或扩展磁盘空间"
            })
        
        # 检查 settings.xml
        settings_check = self._check_settings()
        if not settings_check['valid']:
            result['issues'].append({
                "type": "SETTINGS_ISSUE",
                "severity": "MEDIUM",
                "message": settings_check['message'],
                "solution": settings_check['solution']
            })
        
        # 生成建议
        result['recommendations'] = self._generate_recommendations(result['issues'])
        
        return result
    
    def _collect_statistics(self) -> Dict[str, Any]:
        """收集仓库统计信息"""
        stats = {
            "total_files": 0,
            "total_size_mb": 0,
            "group_count": 0,
            "artifact_count": 0,
            "snapshot_count": 0
        }
        
        try:
            # 统计文件和目录
            for root, dirs, files in os.walk(self.repo_path):
                stats['total_files'] += len(files)
                
                # 统计快照版本
                if 'SNAPSHOT' in root:
                    stats['snapshot_count'] += 1
            
            # 计算总大小
            total_size = sum(f.stat().st_size for f in self.repo_path.rglob('*') if f.is_file())
            stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
            
            # 统计 groupId 数量（一级目录）
            stats['group_count'] = len([d for d in self.repo_path.iterdir() if d.is_dir()])
            
        except Exception as e:
            stats['error'] = str(e)
        
        return stats
    
    def _check_corrupted_dependencies(self) -> List[str]:
        """检查损坏的依赖"""
        corrupted = []
        
        # 检查常见的损坏标志
        for pom_file in self.repo_path.rglob('*.pom'):
            # 检查是否有对应的 jar 文件
            jar_file = pom_file.with_suffix('.jar')
            if not jar_file.exists():
                # 可能是 pom-only 的依赖，检查是否明确标记
                try:
                    with open(pom_file, 'r') as f:
                        content = f.read()
                        if '<packaging>pom</packaging>' not in content:
                            corrupted.append(str(pom_file.relative_to(self.repo_path)))
                except Exception:
                    corrupted.append(str(pom_file.relative_to(self.repo_path)))
        
        # 检查是否有 .lastUpdated 文件（下载失败标记）
        for last_updated in self.repo_path.rglob('*.lastUpdated'):
            corrupted.append(str(last_updated.relative_to(self.repo_path)))
        
        return corrupted
    
    def _check_snapshot_versions(self) -> Dict[str, List[str]]:
        """检查快照版本"""
        result = {
            "total_snapshots": 0,
            "old_snapshots": []
        }
        
        # 查找所有快照目录
        for snapshot_dir in self.repo_path.rglob('*SNAPSHOT*'):
            if snapshot_dir.is_dir():
                result['total_snapshots'] += 1
                
                # 检查最后修改时间
                try:
                    mtime = datetime.fromtimestamp(snapshot_dir.stat().st_mtime)
                    days_old = (datetime.now() - mtime).days
                    
                    if days_old > 30:  # 超过30天未更新
                        result['old_snapshots'].append({
                            "path": str(snapshot_dir.relative_to(self.repo_path)),
                            "days_old": days_old
                        })
                except Exception:
                    pass
        
        return result
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """检查磁盘空间"""
        try:
            total, used, free = shutil.disk_usage(self.repo_path)
            return {
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "usage_percent": round(used / total * 100, 2)
            }
        except Exception:
            return {
                "total_gb": 0,
                "used_gb": 0,
                "free_gb": 0,
                "usage_percent": 0
            }
    
    def _check_settings(self) -> Dict[str, Any]:
        """检查 settings.xml 配置"""
        result = {
            "valid": True,
            "message": "",
            "solution": ""
        }
        
        if not self.settings_path.exists():
            result['valid'] = False
            result['message'] = "settings.xml 不存在"
            result['solution'] = "创建 settings.xml 并配置镜像仓库"
            return result
        
        # 检查镜像配置
        try:
            with open(self.settings_path, 'r') as f:
                content = f.read()
                
                if '<mirror>' not in content:
                    result['valid'] = False
                    result['message'] = "未配置镜像仓库"
                    result['solution'] = "在 settings.xml 中配置阿里云或华为云镜像以加速下载"
        
        except Exception as e:
            result['valid'] = False
            result['message'] = f"解析 settings.xml 失败: {str(e)}"
            result['solution'] = "检查 settings.xml 格式"
        
        return result
    
    def _generate_recommendations(self, issues: List[Dict]) -> List[Dict[str, str]]:
        """生成改进建议"""
        recommendations = []
        
        for issue in issues:
            rec = {
                "type": issue['type'],
                "severity": issue['severity'],
                "recommendation": issue.get('solution', '')
            }
            recommendations.append(rec)
        
        # 添加通用建议
        if not any(i['type'] == 'DISK_SPACE_WARNING' for i in issues):
            recommendations.append({
                "type": "MAINTENANCE",
                "severity": "LOW",
                "recommendation": "定期清理未使用的依赖: mvn dependency:purge-local-repository"
            })
        
        return recommendations
    
    def clean_dependency(self, dependency: str) -> Dict[str, Any]:
        """
        清理指定依赖
        
        Args:
            dependency: 依赖坐标（groupId:artifactId:version）
        
        Returns:
            清理结果
        """
        result = {
            "success": True,
            "dependency": dependency,
            "cleaned_files": [],
            "cleaned_size_mb": 0
        }
        
        try:
            # 解析依赖坐标
            parts = dependency.split(':')
            if len(parts) < 2:
                result['success'] = False
                result['error'] = "无效的依赖坐标格式，应为 groupId:artifactId:version"
                return result
            
            group_id = parts[0].replace('.', os.sep)
            artifact_id = parts[1]
            
            # 构建依赖路径
            dep_path = self.repo_path / group_id / artifact_id
            
            if len(parts) >= 3:
                version = parts[2]
                dep_path = dep_path / version
            
            # 删除依赖
            if dep_path.exists():
                # 计算大小
                total_size = sum(f.stat().st_size for f in dep_path.rglob('*') if f.is_file())
                result['cleaned_size_mb'] = round(total_size / (1024 * 1024), 2)
                
                # 记录删除的文件
                result['cleaned_files'] = [str(f.relative_to(self.repo_path)) for f in dep_path.rglob('*')]
                
                # 执行删除
                shutil.rmtree(dep_path)
            else:
                result['success'] = False
                result['error'] = f"依赖不存在: {dep_path}"
        
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
        
        return result
    
    def clean_all_corrupted(self) -> Dict[str, Any]:
        """
        清理所有损坏的依赖
        
        Returns:
            清理结果
        """
        result = {
            "success": True,
            "cleaned_count": 0,
            "cleaned_size_mb": 0,
            "cleaned_dependencies": []
        }
        
        # 查找损坏的依赖
        corrupted = self._check_corrupted_dependencies()
        
        for item in corrupted:
            # 获取父目录（依赖目录）
            item_path = self.repo_path / item
            
            if item_path.suffix == '.lastUpdated':
                # 删除 lastUpdated 文件
                try:
                    item_path.unlink()
                    result['cleaned_count'] += 1
                except Exception:
                    pass
            else:
                # 删除整个依赖目录
                parent = item_path.parent
                if parent.exists():
                    try:
                        total_size = sum(f.stat().st_size for f in parent.rglob('*') if f.is_file())
                        result['cleaned_size_mb'] += round(total_size / (1024 * 1024), 2)
                        
                        shutil.rmtree(parent)
                        result['cleaned_count'] += 1
                        result['cleaned_dependencies'].append(str(parent.relative_to(self.repo_path)))
                    except Exception:
                        pass
        
        return result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Maven 仓库健康检查工具")
    parser.add_argument("--action", choices=['check', 'clean'], default='check', help="操作类型")
    parser.add_argument("--dependency", help="要清理的依赖（groupId:artifactId:version）")
    parser.add_argument("--output", default="repo-health.json", help="报告输出路径")
    
    args = parser.parse_args()
    
    # 创建检查器
    checker = RepositoryChecker()
    
    if args.action == 'check':
        # 执行健康检查
        result = checker.check_repository()
        
        # 保存报告
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # 输出摘要
        print(f"\n✓ 仓库健康检查完成")
        print(f"仓库路径: {result['repository_path']}")
        print(f"仓库大小: {result['statistics'].get('total_size_mb', 0)} MB")
        print(f"文件总数: {result['statistics'].get('total_files', 0)}")
        print(f"快照版本: {result['statistics'].get('snapshot_count', 0)}")
        
        if result['issues']:
            print(f"\n⚠ 发现问题: {len(result['issues'])} 个")
            for issue in result['issues']:
                print(f"  - [{issue['severity']}] {issue['type']}")
        
        print(f"\n详细报告: {args.output}")
    
    elif args.action == 'clean':
        if args.dependency:
            # 清理指定依赖
            result = checker.clean_dependency(args.dependency)
            
            if result['success']:
                print(f"\n✓ 依赖已清理: {args.dependency}")
                print(f"清理文件: {len(result['cleaned_files'])} 个")
                print(f"释放空间: {result['cleaned_size_mb']} MB")
            else:
                print(f"\n✗ 清理失败: {result.get('error', '未知错误')}", file=sys.stderr)
                sys.exit(1)
        else:
            # 清理所有损坏的依赖
            result = checker.clean_all_corrupted()
            
            if result['success']:
                print(f"\n✓ 损坏依赖已清理")
                print(f"清理数量: {result['cleaned_count']}")
                print(f"释放空间: {result['cleaned_size_mb']} MB")
            else:
                print(f"\n✗ 清理失败", file=sys.stderr)
                sys.exit(1)


if __name__ == "__main__":
    main()
