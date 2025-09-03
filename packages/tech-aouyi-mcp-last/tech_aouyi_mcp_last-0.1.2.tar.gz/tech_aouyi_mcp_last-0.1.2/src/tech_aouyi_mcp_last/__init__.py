"""
智能代码分析 MCP 服务器

专注于代码质量分析和安全检查的开发者工具
运行命令: python main.py
"""

import os
import json
import re
import time
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# 创建MCP服务器
mcp = FastMCP("智能代码分析助手")

# 安全配置
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'.py', '.js', '.ts', '.java', '.json', '.md', '.txt'}

def validate_path(path_str: str) -> bool:
    """验证路径安全性"""
    try:
        path = Path(path_str).resolve()
        return not str(path).startswith(('/', 'C:\\Windows', 'C:\\System32'))
    except:
        return False

@mcp.tool()
def analyze_code(file_path: str) -> dict:
    """智能代码分析 - 核心功能"""
    try:
        if not validate_path(file_path):
            return {"error": "路径不安全"}
        
        path = Path(file_path)
        if not path.is_absolute():
            path = Path.cwd() / path
        
        if not path.exists():
            available_files = [f.name for f in Path.cwd().iterdir() 
                             if f.is_file() and f.suffix in ALLOWED_EXTENSIONS]
            return {
                "error": f"文件不存在: {file_path}",
                "可分析文件": available_files[:10]
            }
        
        if path.stat().st_size > MAX_FILE_SIZE:
            return {"error": "文件过大，超过5MB限制"}
        
        if path.suffix not in ALLOWED_EXTENSIONS:
            return {"error": f"不支持的文件类型: {path.suffix}"}
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # 基本统计
        analysis = {
            "文件信息": {
                "路径": str(path),
                "大小": f"{path.stat().st_size:,} bytes",
                "行数": len(lines),
                "非空行数": len([line for line in lines if line.strip()]),
                "字符数": len(content)
            }
        }
        
        # 语言特定分析
        if path.suffix == '.py':
            analysis["Python分析"] = analyze_python(content)
        elif path.suffix in ['.js', '.ts']:
            analysis["JavaScript分析"] = analyze_javascript(content)
        elif path.suffix == '.json':
            analysis["JSON分析"] = analyze_json(content)
        
        # 安全检查
        analysis["安全检查"] = security_check(content)

        return analysis

    except Exception as e:
        return {"error": f"分析失败: {str(e)}"}

def analyze_python(content: str) -> dict:
    """Python代码分析"""
    imports = len(re.findall(r'^\s*(?:import|from)\s+', content, re.MULTILINE))
    functions = len(re.findall(r'^\s*def\s+\w+', content, re.MULTILINE))
    classes = len(re.findall(r'^\s*class\s+\w+', content, re.MULTILINE))
    
    return {
        "导入语句": imports,
        "函数定义": functions,
        "类定义": classes,
        "复杂度": "高" if functions > 10 else "中" if functions > 5 else "低"
    }

def analyze_javascript(content: str) -> dict:
    """JavaScript代码分析"""
    functions = len(re.findall(r'function\s+\w+|=>\s*{|\w+:\s*function', content))
    variables = len(re.findall(r'\b(var|let|const)\s+\w+', content))
    
    return {
        "函数定义": functions,
        "变量声明": variables,
        "ES6特性": "是" if "=>" in content or "const" in content else "否"
    }

def analyze_json(content: str) -> dict:
    """JSON文件分析"""
    try:
        data = json.loads(content)
        return {
            "JSON有效性": "✅ 有效",
            "数据类型": type(data).__name__,
            "键数量": len(data) if isinstance(data, dict) else "N/A"
        }
    except:
        return {"JSON有效性": "❌ 无效"}

def security_check(content: str) -> dict:
    """安全检查"""
    issues = []
    
    # 检查硬编码密码
    if re.search(r'password\s*=\s*["\'][^"\']*["\']', content, re.IGNORECASE):
        issues.append("发现硬编码密码")
    
    # 检查API密钥
    if re.search(r'api[_-]?key\s*=\s*["\'][^"\']*["\']', content, re.IGNORECASE):
        issues.append("发现硬编码API密钥")
    
    # 检查危险函数
    if 'eval(' in content:
        issues.append("使用了危险的eval()函数")
    
    if 'innerHTML' in content:
        issues.append("可能存在XSS风险")
    
    return {
        "风险等级": "高" if len(issues) > 2 else "中" if issues else "低",
        "发现问题": issues if issues else ["未发现安全问题"],
        "建议": "请修复发现的安全问题" if issues else "代码安全性良好"
    }

@mcp.tool()
def format_json(json_string: str) -> dict:
    """JSON格式化工具"""
    try:
        if not json_string or len(json_string) > 100000:  # 100KB限制
            return {"error": "JSON字符串为空或过大"}
        
        parsed = json.loads(json_string)
        formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
        
        return {
            "格式化结果": formatted,
            "验证状态": "✅ JSON格式正确",
            "原始大小": len(json_string),
            "格式化大小": len(formatted)
        }
    except json.JSONDecodeError as e:
        return {
            "error": f"JSON格式错误: {str(e)}",
            "建议": "请检查JSON语法，确保括号和引号匹配"
        }

@mcp.tool()
def list_files(directory: str = ".") -> dict:
    """列出目录文件"""
    try:
        if not validate_path(directory):
            return {"error": "路径不安全"}
        
        path = Path(directory)
        if not path.is_absolute():
            path = Path.cwd() / path
        
        if not path.exists():
            return {"error": f"目录不存在: {directory}"}
        
        files = []
        for item in path.iterdir():
            if item.is_file() and item.suffix in ALLOWED_EXTENSIONS:
                files.append({
                    "名称": item.name,
                    "大小": f"{item.stat().st_size:,} bytes",
                    "类型": item.suffix
                })
        
        return {
            "目录": str(path),
            "文件数量": len(files),
            "文件列表": files[:20]  # 限制显示20个
        }
        
    except Exception as e:
        return {"error": f"列出文件失败: {str(e)}"}

@mcp.tool()
def get_system_stats() -> dict:
    """获取系统运行统计"""
    # 模拟统计数据（实际应用中可以使用全局变量记录）
    return {
        "分析统计": {
            "总分析文件数": 0,
            "发现安全问题数": 0,
            "平均分析时间": "0.00s",
            "风险分布": {"低": 0, "中": 0, "高": 0, "严重": 0}
        },
        "系统状态": {
            "支持文件类型": list(ALLOWED_EXTENSIONS),
            "最大文件大小": f"{MAX_FILE_SIZE:,} bytes",
            "分析超时限制": "30s"
        }
    }

@mcp.tool()
def get_project_info() -> dict:
    """获取项目详细信息和健康度评估"""
    cwd = Path.cwd()
    
    # 深度文件统计
    file_stats = {}
    total_files = 0
    total_size = 0
    
    for ext in ALLOWED_EXTENSIONS:
        files = list(cwd.glob(f'**/*{ext}'))
        count = len(files)
        size = sum(f.stat().st_size for f in files if f.is_file())
        
        if count > 0:
            file_stats[ext] = {
                "数量": count,
                "总大小": f"{size:,} bytes",
                "平均大小": f"{size//count:,} bytes"
            }
            total_files += count
            total_size += size
    
    # 项目健康度评估
    health_score = 100
    health_issues = []
    
    # 检查项目结构
    has_readme = any(f.name.lower().startswith('readme') for f in cwd.iterdir())
    has_gitignore = (cwd / '.gitignore').exists()
    has_config = any(f.name in ['package.json', 'pyproject.toml', 'requirements.txt'] 
                    for f in cwd.iterdir())
    
    if not has_readme:
        health_score -= 15
        health_issues.append("缺少README文档")
    if not has_gitignore:
        health_score -= 10
        health_issues.append("缺少.gitignore文件")
    if not has_config:
        health_score -= 10
        health_issues.append("缺少项目配置文件")
    
    return {
        "项目概览": {
            "路径": str(cwd),
            "名称": cwd.name,
            "总文件数": total_files,
            "项目大小": f"{total_size:,} bytes"
        },
        "文件统计": file_stats,
        "项目健康度": {
            "健康分数": max(0, health_score),
            "等级": "优秀" if health_score >= 90 else "良好" if health_score >= 70 else "需改进",
            "发现问题": health_issues or ["项目结构良好"]
        }
    }

@mcp.tool()
def generate_code_review_prompt(file_path: str, focus_area: str = "全面", severity_level: str = "标准") -> dict:
    """生成专业代码审查提示词"""
    
    # 获取文件类型和语言特定检查项
    file_ext = Path(file_path).suffix.lower()
    language_checks = {
        '.py': [
            "检查PEP 8编码规范遵循情况",
            "验证异常处理机制的完整性",
            "分析导入语句的安全性和必要性",
            "检查是否使用了不安全的函数如eval(), exec()"
        ],
        '.js': [
            "检查JavaScript最佳实践和ES6+特性使用",
            "验证XSS防护和输入验证",
            "分析异步操作和Promise处理",
            "检查DOM操作的安全性"
        ],
        '.ts': [
            "检查TypeScript类型定义的准确性",
            "验证接口和类型安全",
            "分析泛型使用的合理性"
        ],
        '.java': [
            "检查Java编码规范和设计模式",
            "验证内存管理和资源释放",
            "分析并发处理和线程安全"
        ]
    }
    
    # 关注领域的详细检查项
    focus_details = {
        "安全": {
            "描述": "重点关注安全漏洞、数据泄露风险、输入验证",
            "检查项": [
                "硬编码敏感信息（密码、API密钥、访问令牌）",
                "SQL注入、XSS、CSRF等常见漏洞",
                "输入验证和输出编码的完整性",
                "权限控制和身份验证机制",
                "文件上传和路径遍历防护"
            ]
        },
        "性能": {
            "描述": "重点关注算法效率、内存使用、并发处理",
            "检查项": [
                "算法复杂度和数据结构选择",
                "内存泄露和资源释放问题",
                "数据库查询优化和N+1问题",
                "缓存策略和异步处理",
                "大数据量处理和分页机制"
            ]
        },
        "维护性": {
            "描述": "重点关注代码结构、注释质量、模块化设计",
            "检查项": [
                "代码结构和分层架构的合理性",
                "函数和类的单一职责原则",
                "注释和文档的完整性和准确性",
                "命名规范和代码可读性",
                "错误处理和日志记录机制"
            ]
        },
        "全面": {
            "描述": "进行全方位综合评估，包括安全、性能、维护性等各个方面",
            "检查项": [
                "代码质量和编码规范遵循情况",
                "安全漏洞和风险点识别",
                "性能瓶颈和优化机会",
                "架构设计和模块化程度",
                "测试覆盖率和质量保证"
            ]
        }
    }
    
    # 严重程度级别
    severity_configs = {
        "宽松": "重点关注严重问题和明显的改进机会",
        "标准": "按照行业标准进行全面审查",
        "严格": "采用高标准，对细节问题也要指出和改进"
    }
    
    # 构建提示词内容
    focus_info = focus_details.get(focus_area, focus_details["全面"])
    lang_specific = language_checks.get(file_ext, [])
    
    prompt_content = f"""# 代码审查报告 - {file_path}

## 审查配置
- **目标文件**: {file_path}
- **关注领域**: {focus_area}
- **严重程度**: {severity_level}
- **文件类型**: {file_ext}

## 审查重点
{focus_info['描述']}

### 主要检查项目
"""
    
    for i, item in enumerate(focus_info["检查项"], 1):
        prompt_content += f"{i}. {item}\n"
    
    if lang_specific:
        prompt_content += f"\n### {file_ext}语言特定检查\n"
        for i, item in enumerate(lang_specific, 1):
            prompt_content += f"{i}. {item}\n"
    
    prompt_content += f"""\n## 审查标准
{severity_configs[severity_level]}

## 输出要求
请按以下结构提供审查结果：

### 1. 总体评估
- 代码质量评分（A/B/C/D）
- 主要优点和问题总结

### 2. 问题清单
每个问题包括：
- **位置**: 具体行号或函数名
- **类型**: 安全/性能/维护性/规范
- **严重程度**: 严重/中等/轻微
- **描述**: 问题的详细说明
- **建议**: 具体的修复方案

### 3. 改进建议
- 优先级排序的改进项目
- 最佳实践推荐
- 重构建议（如需要）

请对代码进行全面而专业的审查。"""
    
    return {
        "提示词类型": "代码审查",
        "目标文件": file_path,
        "关注领域": focus_area,
        "严重程度": severity_level,
        "文件类型": file_ext,
        "提示词内容": prompt_content
    }

@mcp.tool()
def generate_security_audit_prompt(project_path: str = "当前项目", audit_scope: str = "全面", compliance_standard: str = "OWASP") -> dict:
    """生成安全审计提示词"""
    
    # 审计范围配置
    scope_configs = {
        "代码安全": {
            "描述": "专注于源代码的安全漏洞和风险点",
            "检查项": [
                "静态代码分析和漏洞扫描",
                "输入验证和输出编码检查",
                "身份验证和授权机制审查",
                "加密和数据保护实现",
                "危险函数和不安全的API调用"
            ]
        },
        "依赖安全": {
            "描述": "检查第三方库和组件的安全风险",
            "检查项": [
                "第三方依赖库的已知漏洞扫描",
                "依赖版本管理和更新策略",
                "依赖来源的可信度验证",
                "许可证兼容性和法律风险",
                "依赖链攻击防护机制"
            ]
        },
        "配置安全": {
            "描述": "审查系统配置和部署安全",
            "检查项": [
                "敏感信息和凭据的存储和传输",
                "环境变量和配置文件安全",
                "数据库连接和访问控制",
                "网络安全和防火墙配置",
                "日志记录和监控机制"
            ]
        },
        "架构安全": {
            "描述": "评估系统架构设计的安全性",
            "检查项": [
                "安全架构设计和威胁建模",
                "数据流和信任边界分析",
                "容灾和灾难恢复机制",
                "微服务和分布式系统安全",
                "API安全和服务间通信加密"
            ]
        },
        "全面": {
            "描述": "对项目进行全方位的安全审计",
            "检查项": [
                "代码安全漏洞和风险点识别",
                "第三方依赖库安全性评估",
                "系统配置和部署安全检查",
                "架构设计安全性分析",
                "安全测试和渗透测试建议"
            ]
        }
    }
    
    # 合规标准配置
    compliance_configs = {
        "OWASP": {
            "名称": "OWASP Top 10",
            "描述": "基于OWASP Top 10最常见的Web应用安全风险",
            "重点": [
                "A01:2021 - 访问控制失效",
                "A02:2021 - 加密失效",
                "A03:2021 - 注入攻击",
                "A04:2021 - 不安全设计",
                "A05:2021 - 安全配置错误",
                "A06:2021 - 易受攻击的组件",
                "A07:2021 - 身份验证和认证失效",
                "A08:2021 - 软件和数据完整性失效",
                "A09:2021 - 安全日志和监控失效",
                "A10:2021 - 服务器端请求伪造"
            ]
        },
        "ISO27001": {
            "名称": "ISO/IEC 27001",
            "描述": "基于ISO 27001信息安全管理体系标准",
            "重点": [
                "信息安全策略和管理",
                "风险评估和处理",
                "访问控制和身份管理",
                "事件响应和业务连续性"
            ]
        },
        "PCI-DSS": {
            "名称": "PCI DSS",
            "描述": "支付卡行业数据安全标准",
            "重点": [
                "持卡人数据保护",
                "网络安全控制",
                "访问控制和身份管理",
                "安全测试和监控"
            ]
        }
    }
    
    # 获取配置信息
    scope_info = scope_configs.get(audit_scope, scope_configs["全面"])
    compliance_info = compliance_configs.get(compliance_standard, compliance_configs["OWASP"])
    
    # 构建提示词内容
    prompt_content = f"""# 项目安全审计报告 - {project_path}

## 审计配置
- **目标项目**: {project_path}
- **审计范围**: {audit_scope}
- **合规标准**: {compliance_info['名称']}
- **审计日期**: {time.strftime('%Y-%m-%d')}

## 审计范围说明
{scope_info['描述']}

### 主要检查项目
"""
    
    for i, item in enumerate(scope_info["检查项"], 1):
        prompt_content += f"{i}. {item}\n"
    
    prompt_content += f"""\n## 合规标准要求
{compliance_info['描述']}

### 重点关注项目
"""
    
    for i, item in enumerate(compliance_info["重点"], 1):
        prompt_content += f"{i}. {item}\n"
    
    prompt_content += f"""\n## 审计方法
1. **自动化扫描**: 使用安全扫描工具进行初步检测
2. **手工代码审查**: 对关键代码进行深入分析
3. **配置检查**: 验证系统配置的安全性
4. **渗透测试**: 模拟攻击者行为验证安全控制
5. **合规性检查**: 对照标准要求进行对比分析

## 输出要求
请按以下结构提供安全审计报告：

### 1. 执行摘要
- 审计范围和方法说明
- 总体安全状态评估
- 关键发现和建议概述

### 2. 安全风险清单
每个风险包括：
- **风险ID**: 唯一标识符
- **风险类型**: 按照OWASP或其他标准分类
- **严重程度**: 严重/高/中/低
- **影响范围**: 受影响的系统组件
- **漏洞描述**: 详细的技术说明
- **利用方式**: 攻击者可能的利用方法
- **修复建议**: 具体的解决方案
- **修复优先级**: 按照风险等级排序

### 3. 合规性评估
- 对照选定标准的符合情况
- 不符合项的详细说明
- 整改建议和时间计划

### 4. 安全改进路线图
- 短期修复项目（1-3个月）
- 中期改进项目（3-12个月）
- 长期安全策略（12个月以上）

### 5. 监控和持续改进建议
- 安全监控机制建议
- 安全培训和意识提升
- 定期安全评估计划

请进行全面而专业的安全审计。"""
    
    return {
        "提示词类型": "安全审计",
        "目标项目": project_path,
        "审计范围": audit_scope,
        "合规标准": compliance_standard,
        "提示词内容": prompt_content
    }

def main() -> None:
    mcp.run(transport="stdio")
