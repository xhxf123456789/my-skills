#!/usr/bin/env python3
"""
Maven 性能分析工具

功能：
1. 分析构建时间
2. 识别慢速模块
3. 识别耗时插件
4. 生成优化建议

使用方式：
    python performance_analyzer.py --log build-time.log --output ./performance-report.json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict


class PerformanceAnalyzer:
    """性能分析工具"""
    
    def __init__(self, log_path: str):
        """
        初始化
        
        Args:
            log_path: 构建日志文件路径
        """
        self.log_path = Path(log_path)
        self.log_content = ""
        self.modules = {}
        self.plugins = {}
        self.phases = {}
        
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
    
    def analyze(self) -> Dict[str, Any]:
        """
        分析性能
        
        Returns:
            分析结果
        """
        if not self.log_content:
            return {
                "success": False,
                "error": "日志内容为空"
            }
        
        # 解析构建时间
        self._parse_build_times()
        
        # 解析模块时间
        self._parse_module_times()
        
        # 解析插件时间
        self._parse_plugin_times()
        
        # 解析下载时间
        download_stats = self._parse_download_times()
        
        # 生成报告
        report = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "total_build_time": self._parse_total_time(),
            "statistics": {
                "module_count": len(self.modules),
                "plugin_executions": len(self.plugins),
                "total_downloads": download_stats['total_downloads'],
                "download_size_mb": download_stats['download_size_mb']
            },
            "modules": self.modules,
            "plugins": self.plugins,
            "phases": self.phases,
            "downloads": download_stats,
            "bottlenecks": self._identify_bottlenecks(),
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _parse_total_time(self) -> str:
        """解析总构建时间"""
        match = re.search(r'Total time:\s+([\d:]+)', self.log_content)
        if match:
            return match.group(1)
        return "Unknown"
    
    def _parse_build_times(self):
        """解析各阶段构建时间"""
        # 解析 Maven 阶段时间
        phase_pattern = re.compile(r'\[INFO\] -+< (.+?) >-+')
        time_pattern = re.compile(r'([\d\.]+)\s*s')
        
        lines = self.log_content.split('\n')
        
        for i, line in enumerate(lines):
            # 检测阶段开始
            phase_match = phase_pattern.search(line)
            if phase_match:
                phase_name = phase_match.group(1)
                
                # 查找该阶段的时间
                for j in range(i, min(i + 50, len(lines))):
                    time_match = time_pattern.search(lines[j])
                    if time_match:
                        time_seconds = float(time_match.group(1))
                        if phase_name not in self.phases:
                            self.phases[phase_name] = time_seconds
                        break
    
    def _parse_module_times(self):
        """解析模块构建时间"""
        # 匹配模块构建信息
        pattern = re.compile(r'Building\s+(.+?)\s+([\d\.]+)')
        
        for match in pattern.finditer(self.log_content):
            module_name = match.group(1)
            module_version = match.group(2)
            
            # 查找该模块的构建时间
            start_pos = match.end()
            end_pos = self.log_content.find('Building', start_pos)
            if end_pos == -1:
                end_pos = len(self.log_content)
            
            module_log = self.log_content[start_pos:end_pos]
            
            # 提取时间
            time_match = re.search(r'([\d\.]+)\s*s', module_log)
            if time_match:
                time_seconds = float(time_match.group(1))
                
                if module_name not in self.modules:
                    self.modules[module_name] = {
                        "version": module_version,
                        "time_seconds": time_seconds,
                        "time_formatted": self._format_time(time_seconds)
                    }
    
    def _parse_plugin_times(self):
        """解析插件执行时间"""
        # 匹配插件执行
        plugin_pattern = re.compile(r'\[INFO\] --- (.+?):(.+?):(.+?) \((.+?)\) @ (.+?) ---')
        
        for match in plugin_pattern.finditer(self.log_content):
            group_id = match.group(1)
            artifact_id = match.group(2)
            version = match.group(3)
            goal = match.group(4)
            module = match.group(5)
            
            plugin_key = f"{artifact_id}:{goal}"
            
            # 查找该插件执行的时间
            start_pos = match.end()
            time_match = re.search(r'([\d\.]+)\s*s', self.log_content[start_pos:start_pos + 500])
            
            if time_match:
                time_seconds = float(time_match.group(1))
                
                if plugin_key not in self.plugins:
                    self.plugins[plugin_key] = {
                        "group_id": group_id,
                        "version": version,
                        "total_time_seconds": 0,
                        "executions": []
                    }
                
                self.plugins[plugin_key]['total_time_seconds'] += time_seconds
                self.plugins[plugin_key]['executions'].append({
                    "module": module,
                    "time_seconds": time_seconds
                })
    
    def _parse_download_times(self) -> Dict[str, Any]:
        """解析下载统计"""
        stats = {
            "total_downloads": 0,
            "download_size_mb": 0,
            "downloaded_artifacts": []
        }
        
        # 匹配下载信息
        download_pattern = re.compile(r'Downloaded from .+?: (.+?) \(([\d\.]+)\s*(KB|MB)\)')
        
        for match in download_pattern.finditer(self.log_content):
            artifact = match.group(1)
            size = float(match.group(2))
            unit = match.group(3)
            
            # 转换为 MB
            if unit == 'KB':
                size_mb = size / 1024
            else:
                size_mb = size
            
            stats['total_downloads'] += 1
            stats['download_size_mb'] += size_mb
            
            if stats['total_downloads'] <= 20:  # 只记录前20个
                stats['downloaded_artifacts'].append({
                    "artifact": artifact.split('/')[-1],
                    "size_mb": round(size_mb, 2)
                })
        
        stats['download_size_mb'] = round(stats['download_size_mb'], 2)
        
        return stats
    
    def _identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """识别性能瓶颈"""
        bottlenecks = []
        
        # 识别慢速模块
        slow_modules = sorted(
            [(k, v) for k, v in self.modules.items()],
            key=lambda x: x[1]['time_seconds'],
            reverse=True
        )[:5]
        
        if slow_modules and slow_modules[0][1]['time_seconds'] > 30:
            bottlenecks.append({
                "type": "SLOW_MODULE",
                "severity": "HIGH",
                "details": [
                    {"module": m[0], "time": m[1]['time_formatted']}
                    for m in slow_modules
                ],
                "suggestion": "考虑模块拆分或优化构建流程"
            })
        
        # 识别慢速插件
        slow_plugins = sorted(
            [(k, v) for k, v in self.plugins.items()],
            key=lambda x: x[1]['total_time_seconds'],
            reverse=True
        )[:5]
        
        if slow_plugins and slow_plugins[0][1]['total_time_seconds'] > 20:
            bottlenecks.append({
                "type": "SLOW_PLUGIN",
                "severity": "MEDIUM",
                "details": [
                    {
                        "plugin": p[0],
                        "time": self._format_time(p[1]['total_time_seconds']),
                        "executions": len(p[1]['executions'])
                    }
                    for p in slow_plugins
                ],
                "suggestion": "优化插件配置或跳过不必要的执行"
            })
        
        # 识别下载瓶颈
        downloads = self._parse_download_times()
        if downloads['download_size_mb'] > 50:
            bottlenecks.append({
                "type": "LARGE_DOWNLOADS",
                "severity": "MEDIUM",
                "details": {
                    "count": downloads['total_downloads'],
                    "size_mb": downloads['download_size_mb']
                },
                "suggestion": "配置镜像仓库加速下载，或使用本地仓库缓存"
            })
        
        return bottlenecks
    
    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """生成优化建议"""
        recommendations = []
        
        # 并行构建建议
        if len(self.modules) > 1:
            recommendations.append({
                "type": "PARALLEL_BUILD",
                "priority": "HIGH",
                "recommendation": "启用并行构建: mvn -T 4 clean install",
                "expected_improvement": "构建时间可减少 30-50%"
            })
        
        # 离线模式建议
        downloads = self._parse_download_times()
        if downloads['total_downloads'] > 0:
            recommendations.append({
                "type": "OFFLINE_MODE",
                "priority": "MEDIUM",
                "recommendation": "依赖稳定后使用离线模式: mvn -o clean install",
                "expected_improvement": "跳过网络检查，加快构建"
            })
        
        # 镜像配置建议
        recommendations.append({
            "type": "MIRROR_CONFIG",
            "priority": "HIGH",
            "recommendation": "配置阿里云镜像加速下载",
            "expected_improvement": "下载速度提升 5-10 倍"
        })
        
        # 跳过测试建议
        test_time = self.plugins.get('maven-surefire-plugin:test', {}).get('total_time_seconds', 0)
        if test_time > 60:
            recommendations.append({
                "type": "SKIP_TESTS",
                "priority": "LOW",
                "recommendation": "开发阶段跳过测试: mvn -DskipTests clean install",
                "expected_improvement": f"节省约 {self._format_time(test_time)}"
            })
        
        # 内存优化建议
        recommendations.append({
            "type": "MEMORY_CONFIG",
            "priority": "MEDIUM",
            "recommendation": "增加 Maven 内存: export MAVEN_OPTS=\"-Xmx2048m\"",
            "expected_improvement": "避免内存不足导致的构建失败"
        })
        
        return recommendations
    
    def _format_time(self, seconds: float) -> str:
        """格式化时间"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        else:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m {secs:.1f}s"
    
    def save_report(self, output_path: str):
        """保存分析报告"""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        report = self.analyze()
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Maven 性能分析工具")
    parser.add_argument("--log", required=True, help="构建日志文件路径")
    parser.add_argument("--output", default="performance-report.json", help="报告输出路径")
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = PerformanceAnalyzer(args.log)
    
    # 读取日志
    if not analyzer.read_log():
        print(f"✗ 无法读取日志文件: {args.log}", file=sys.stderr)
        sys.exit(1)
    
    # 执行分析并保存
    report = analyzer.save_report(args.output)
    
    # 输出摘要
    if report['success']:
        print(f"\n✓ 性能分析完成")
        print(f"总构建时间: {report['total_build_time']}")
        print(f"模块数量: {report['statistics']['module_count']}")
        print(f"插件执行: {report['statistics']['plugin_executions']}")
        print(f"下载文件: {report['statistics']['total_downloads']} ({report['statistics']['download_size_mb']} MB)")
        
        if report['bottlenecks']:
            print(f"\n⚠ 性能瓶颈:")
            for bottleneck in report['bottlenecks']:
                print(f"  - [{bottleneck['severity']}] {bottleneck['type']}")
        
        if report['recommendations']:
            print(f"\n💡 优化建议:")
            for rec in report['recommendations'][:3]:
                print(f"  - [{rec['priority']}] {rec['recommendation']}")
        
        print(f"\n详细报告: {args.output}")
    else:
        print(f"✗ 分析失败: {report.get('error', '未知错误')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
