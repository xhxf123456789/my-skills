#!/usr/bin/env python3
"""
安全漏洞扫描工具（优化版）

功能：使用 bandit 进行安全漏洞扫描
用途：检测代码中的安全风险，如 SQL 注入、硬编码密码等

优化功能：
- 添加漏洞详细说明
- 提供修复建议
- OWASP Top 10 映射
- 按严重性排序

使用方式：
    python security_scanner.py --path <文件或目录> --severity medium --show-fixes

参数说明：
    --path: 要扫描的文件或目录路径（必需）
    --severity: 最低严重级别，可选值：low/medium/high（默认：low）
    --show-fixes: 显示修复建议（可选）
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any


def run_bandit(path: str, severity: str = "low") -> Dict[str, Any]:
    """
    运行 bandit 进行安全扫描
    
    Args:
        path: 文件或目录路径
        severity: 最低严重级别（low/medium/high）
    
    Returns:
        扫描结果字典
    """
    try:
        # 映射严重级别到 bandit 参数
        severity_map = {
            "low": "low",
            "medium": "medium",
            "high": "high"
        }
        
        severity_level = severity_map.get(severity, "low")
        
        # 运行 bandit
        cmd = [
            "bandit",
            "-r", path,
            "-f", "json",
            "-l" if severity_level == "low" else "",
            "--severity-level", severity_level
        ]
        
        # 移除空参数
        cmd = [arg for arg in cmd if arg]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # 解析 JSON 输出
        if result.stdout:
            try:
                bandit_result = json.loads(result.stdout)
            except json.JSONDecodeError:
                return {
                    "path": path,
                    "error": "无法解析 bandit 输出"
                }
        else:
            return {
                "path": path,
                "error": "bandit 未返回结果"
            }
        
        # 格式化结果
        issues = []
        stats = {
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for issue in bandit_result.get("results", []):
            issue_severity = issue.get("issue_severity", "LOW").lower()
            if issue_severity in stats:
                stats[issue_severity] += 1
            
            issues.append({
                "file": issue.get("filename", ""),
                "line": issue.get("line_number", 0),
                "severity": issue_severity,
                "confidence": issue.get("issue_confidence", "").lower(),
                "test_id": issue.get("test_id", ""),
                "test_name": issue.get("test_name", ""),
                "message": issue.get("issue_text", ""),
                "code_snippet": issue.get("code", "").strip()
            })
        
        return {
            "path": path,
            "severity_filter": severity,
            "stats": stats,
            "issues": issues,
            "total_issues": len(issues)
        }
        
    except subprocess.TimeoutExpired:
        return {
            "path": path,
            "error": "扫描超时，请检查项目大小或指定具体文件"
        }
    except FileNotFoundError:
        return {
            "path": path,
            "error": "bandit 未安装，请运行：pip install bandit"
        }
    except Exception as e:
        return {
            "path": path,
            "error": f"扫描失败: {str(e)}"
        }


def format_text_output(result: Dict[str, Any]) -> str:
    """
    格式化输出为文本格式
    
    Args:
        result: 扫描结果
    
    Returns:
        格式化的文本
    """
    if "error" in result:
        return f"错误: {result['error']}"
    
    lines = [f"安全扫描: {result['path']}", ""]
    lines.append(f"最低严重级别: {result['severity_filter']}")
    lines.append("")
    
    lines.append("问题统计:")
    lines.append(f"  高危 (High): {result['stats']['high']}")
    lines.append(f"  中危 (Medium): {result['stats']['medium']}")
    lines.append(f"  低危 (Low): {result['stats']['low']}")
    lines.append(f"  总计: {result['total_issues']}")
    lines.append("")
    
    if result['issues']:
        lines.append("安全问题详情:")
        for issue in result['issues']:
            severity_label = issue['severity'].upper()
            lines.append(
                f"\n  [{severity_label}] {issue['test_id']} - {issue['test_name']}"
            )
            lines.append(f"    文件: {Path(issue['file']).name}:{issue['line']}")
            lines.append(f"    消息: {issue['message']}")
            lines.append(f"    置信度: {issue['confidence']}")
            if issue['code_snippet']:
                lines.append(f"    代码: {issue['code_snippet']}")
    
    return "\n".join(lines)


def get_security_fix(test_id: str) -> Dict[str, str]:
    """
    获取安全修复建议
    
    Args:
        test_id: Bandit 测试 ID
    
    Returns:
        修复建议和 OWASP 映射
    """
    fixes = {
        "B101": {
            "fix": "避免使用 assert 语句进行业务逻辑判断，改用 if 语句或 unittest 断言",
            "owasp": "A03:2021 - Injection",
            "risk": "assert 语句在 Python -O 模式下会被优化掉，导致安全检查失效"
        },
        "B105": {
            "fix": "使用环境变量或配置文件存储密码，不要硬编码在代码中",
            "owasp": "A07:2021 - Identification and Authentication Failures",
            "risk": "硬编码密码容易被泄露，导致未授权访问"
        },
        "B107": {
            "fix": "使用 tempfile 模块创建临时文件，避免可预测的文件名",
            "owasp": "A01:2021 - Broken Access Control",
            "risk": "可预测的临时文件名可能导致符号链接攻击"
        },
        "B301": {
            "fix": "使用 JSON、YAML 等安全格式替代 pickle",
            "owasp": "A08:2021 - Software and Data Integrity Failures",
            "risk": "pickle 反序列化可能导致远程代码执行"
        },
        "B601": {
            "fix": "使用参数化查询，避免字符串拼接 SQL 语句",
            "owasp": "A03:2021 - Injection",
            "risk": "SQL 注入可能导致数据泄露或篡改"
        },
        "B602": {
            "fix": "避免使用 shell=True，使用列表传参",
            "owasp": "A03:2021 - Injection",
            "risk": "shell 注入可能导致任意命令执行"
        }
    }
    return fixes.get(test_id, {
        "fix": "参考 OWASP 安全最佳实践",
        "owasp": "未知",
        "risk": "需要进一步评估风险"
    })


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="安全漏洞扫描工具")
    parser.add_argument("--path", required=True, help="要扫描的文件或目录路径")
    parser.add_argument("--severity", choices=["low", "medium", "high"], default="low",
                       help="最低严重级别（默认：low）")
    parser.add_argument("--output", choices=["json", "text"], default="json",
                       help="输出格式（默认：json）")
    parser.add_argument("--show-fixes", action="store_true",
                       help="显示修复建议")
    
    args = parser.parse_args()
    
    # 验证路径存在
    if not Path(args.path).exists():
        print(f"错误: 路径不存在: {args.path}", file=sys.stderr)
        sys.exit(1)
    
    # 执行扫描
    result = run_bandit(args.path, args.severity)
    
    # 添加修复建议和 OWASP 映射
    if args.show_fixes and "issues" in result:
        for issue in result["issues"]:
            fix_info = get_security_fix(issue.get("test_id", ""))
            issue["fix_suggestion"] = fix_info["fix"]
            issue["owasp_mapping"] = fix_info["owasp"]
            issue["risk_description"] = fix_info["risk"]
    
    # 输出结果
    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_text_output(result))


if __name__ == "__main__":
    main()
