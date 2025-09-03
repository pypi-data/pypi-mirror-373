"""
脚本分析器 - 基于MD和项目路径分析功能
负责解析使用说明文档，识别项目的所有功能点和调用方式
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional

from loguru import logger


@dataclass
class FunctionInfo:
    """功能信息"""
    name: str
    description: str
    parameters: List[Dict[str, Any]]
    command_template: str
    expected_output: str
    examples: List[str]
    script_type: str  # python, shell, node, etc.
    cli_mappings: Optional[Dict[str, Any]] = None  # CLI参数映射


@dataclass  
class ProjectAnalysis:
    """项目分析结果 - 专注于AutoAPI功能包装"""
    project_name: str
    project_path: str
    main_language: str  # 从调用方式推断的主要语言
    functions: List[FunctionInfo]  # 可调用的功能列表

    
    # 简化的运行时信息（仅包含执行必需信息）
    runtime_environment: Optional[Dict[str, Any]] = None  # 仅保留执行相关的环境信息
    main_entry: Optional[str] = None  # 主要入口点（如果有的话）


class ScriptAnalyzer:
    """脚本分析器"""
    
    def __init__(self, llm_provider):
        """
        初始化分析器
        
        Args:
            llm_provider: LLM提供者实例（必传），用于智能分析
        """
        if llm_provider is None:
            raise ValueError("llm_provider 是必传参数，AutoAPI 需要 LLM 进行智能分析")
        self.llm_provider = llm_provider

    async def analyze_project(self, usage_md: str, project_path: str) -> ProjectAnalysis:
        """
        分析项目功能 - 基于项目路径和使用说明进行智能分析
        
        Args:
            usage_md: 使用说明MD内容 (主要信息源)
            project_path: 项目绝对路径（必传参数）
            
        Returns:
            ProjectAnalysis: 项目分析结果
        """
        logger.info(f"开始智能分析项目，路径: {project_path}")

        # 基础项目信息
        project_name = Path(project_path).name

        # LLM智能综合分析 - 基于usage_md、项目结构和README
        llm_analysis = await self._llm_comprehensive_analyze(project_path, usage_md)
        
        return ProjectAnalysis(
            project_name=project_name,
            project_path=project_path,
            main_language=llm_analysis.get('main_language', 'python'),
            functions=llm_analysis.get('functions', []),
            runtime_environment=llm_analysis.get('runtime_environment'),
            main_entry=llm_analysis.get('main_entry', None)
        )
    
    
    
    async def _infer_project_name_from_usage(self, usage_md: str, max_length: int = 20) -> str:
        """
        从usage_md中推断项目名称，使用LLM生成简洁、适合路由的格式
        
        Args:
            usage_md: 使用说明MD内容
            max_length: 最大长度限制
            
        Returns:
            str: 推断出的项目名称（简洁格式）
        """
        try:
            # 使用LLM生成项目名称
            prompt = f"""
Based on the following usage documentation, generate a concise project name suitable for URL routing.

Usage Documentation:
{usage_md}

Requirements:
1. Maximum length: {max_length} characters
2. Use only lowercase letters, numbers, and hyphens
3. Focus on the main functionality or purpose of the project
4. Be concise and descriptive
5. Avoid generic words like "tool", "script", "project", "app"

Examples of good project names:
- "image-resize" for an image resizing tool
- "log-parser" for a log parsing utility  
- "data-sync" for a data synchronization service
- "file-convert" for a file conversion tool

Return only the project name, nothing else.
"""
            
            response = await self.llm_provider.generate_completion_async(
                system_prompt="You are an expert at creating concise, descriptive project names for API routing. Generate names that clearly indicate the project's main purpose.",
                user_prompt=prompt,
                json_format=False
            )
            
            if response and isinstance(response, str):
                # 清理LLM返回的结果
                generated_name = response.strip().lower()
                # 移除引号和其他可能的包装字符
                generated_name = generated_name.strip('"\'`')
                # 清理和验证名称
                clean_name = self._clean_and_limit_name(generated_name, max_length)
                
                if clean_name and len(clean_name) >= 2:
                    logger.info(f"LLM生成项目名称: {clean_name}")
                    return clean_name
            
            # LLM生成失败，回退到规则方法
            logger.warning("LLM生成项目名称失败，回退到规则方法")
            return self._fallback_rule_based_name_inference(usage_md, max_length)
            
        except Exception as e:
            logger.warning(f"LLM项目名称生成失败: {e}，回退到规则方法")
            return self._fallback_rule_based_name_inference(usage_md, max_length)
    
    def _fallback_rule_based_name_inference(self, usage_md: str, max_length: int = 20) -> str:
        """
        回退的基于规则的项目名称推断方法（原始逻辑）
        
        Args:
            usage_md: 使用说明MD内容
            max_length: 最大长度限制
            
        Returns:
            str: 推断出的项目名称（简洁格式）
        """
        try:
            lines = usage_md.strip().split('\n')
            
            # 优先级1: 从标题中提取关键词
            for line in lines:
                if line.strip().startswith('#'):
                    title = line.strip().lstrip('#').strip()
                    if title and not title.lower().startswith('usage'):
                        # 提取关键词并优化
                        name = self._extract_key_name_from_title(title, max_length)
                        if name:
                            return name
            
            # 优先级2: 从安装命令中提取包名
            for line in lines:
                if any(cmd in line.lower() for cmd in ['pip install', 'npm install', 'docker run']):
                    words = line.split()
                    for i, word in enumerate(words):
                        if word in ['install', 'run'] and i + 1 < len(words):
                            candidate = words[i + 1].strip()
                            if candidate and not candidate.startswith('-'):
                                # 清理包名并截取核心部分
                                clean_name = candidate.split(':')[0].split('/')[-1]  # 移除docker标签和路径
                                return self._clean_and_limit_name(clean_name, max_length)
            
            # 优先级3: 从执行命令中提取工具名
            for line in lines:
                # 查找可执行命令（非安装命令）
                if any(indicator in line.lower() for indicator in ['python', 'node', 'npm run', 'yarn', 'conda run']):
                    words = line.split()
                    for word in words:
                        if len(word) >= 3 and word.isalnum():
                            clean_name = self._clean_and_limit_name(word, max_length)
                            if clean_name and clean_name not in ['python', 'node', 'npm', 'yarn', 'conda', 'run']:
                                return clean_name
            
            # 默认名称
            return 'unknown-project'
            
        except Exception as e:
            logger.warning(f"规则方法推断项目名称失败: {e}")
            return 'unknown-project'
    
    def _extract_key_name_from_title(self, title: str, max_length: int) -> str:
        """从标题中提取关键名称"""
        # 移除常见无关词汇
        noise_words = [
            '工具', '使用', '指南', '教程', '文档', '说明', 'usage', 'guide', 'tutorial', 
            'documentation', 'how', 'to', 'with', 'using', 'for', 'and', 'the', 'a', 'an',
            'https', 'http', 'github', 'com', 'www', 'git', 'repo'
        ]
        
        # 分词并过滤
        words = []
        # 支持中英文分词
        import re
        # 分离中英文和特殊字符
        tokens = re.findall(r'[a-zA-Z0-9]+|[\u4e00-\u9fff]+', title.lower())
        
        for token in tokens:
            if len(token) >= 2 and token not in noise_words:
                # 如果是URL片段，提取最有意义的部分
                if 'github' in token or 'http' in token:
                    continue
                words.append(token)
                if len(words) >= 2:  # 最多取2个关键词
                    break
        
        if words:
            # 组合关键词
            result = '-'.join(words)
            return self._clean_and_limit_name(result, max_length)
        
        return ''
    
    def _clean_and_limit_name(self, name: str, max_length: int) -> str:
        """清理和限制名称长度"""
        # 移除特殊字符，只保留字母数字和连字符
        cleaned = ''.join(c for c in name if c.isalnum() or c in ['-', '_'])
        cleaned = cleaned.replace('_', '-').lower()
        
        # 移除连续的连字符
        import re
        cleaned = re.sub(r'-+', '-', cleaned).strip('-')
        
        # 长度限制
        if len(cleaned) > max_length:
            # 尝试在连字符处截断，保持完整性
            if '-' in cleaned[:max_length]:
                last_dash = cleaned[:max_length].rfind('-')
                cleaned = cleaned[:last_dash]
            else:
                cleaned = cleaned[:max_length]
        
        return cleaned if len(cleaned) >= 2 else ''
    
    async def _llm_comprehensive_analyze(self, project_path: str, usage_md: str, has_real_path: bool = True) -> Dict[str, Any]:
        """使用LLM进行综合项目分析 - 包含项目结构和README内容"""
        try:
            from .prompts import COMPREHENSIVE_PROJECT_ANALYSIS_PROMPT

            # 始终有真实项目路径（因为现在是必传参数）
            main_language = self._detect_project_main_language(project_path)
            project_structure = self._get_project_structure_summary(project_path)
            readme_section = self._get_readme_section(project_path)

            prompt = COMPREHENSIVE_PROJECT_ANALYSIS_PROMPT.format(
                project_path=project_path,
                usage_md=usage_md,
                project_structure=project_structure,
            ) + readme_section
            
            response = await self.llm_provider.generate_completion_async(
                system_prompt="You are an expert software analyst. Analyze projects based primarily on their usage documentation, then validate with project structure. Do not limit yourself to predefined project types.",
                user_prompt=prompt,
                json_format=True
            )
            
            # 解析功能信息
            functions = []
            functions_data = response.get('functions', [])
            
            for func_data in functions_data:
                function_info = FunctionInfo(
                    name=func_data.get('name', 'unknown'),
                    description=func_data.get('description', ''),
                    parameters=func_data.get('parameters', []),
                    command_template=func_data.get('command_template', ''),
                    expected_output=func_data.get('expected_output', ''),
                    examples=func_data.get('examples', []),
                    script_type=func_data.get('script_type', 'shell'),
                    cli_mappings=func_data.get('cli_mappings', {})
                )
                functions.append(function_info)
            
            logger.info(f"LLM综合分析出 {len(functions)} 个功能，项目类型：{response.get('project_type', 'unknown')}")
            

            # 后处理：规范化runtime_environment格式以确保与EnvironmentRegistry兼容
            runtime_env = response.get('runtime_environment', {})
            normalized_runtime_env = self._normalize_runtime_environment(runtime_env, usage_md)

            # 运行时环境已经规范化，可以直接使用
            
            return {
                'project_type': response.get('project_type', 'unknown'),
                'main_language': main_language,  # 从调用方式推断的主要语言
                'functions': functions,
                'main_entry': response.get('main_entry', None),
                'runtime_environment': normalized_runtime_env
            }
            
        except Exception as e:
            logger.error(f"LLM综合分析失败: {e}")
            # 返回空结果，让调用方回退到规则分析
            return {}
    


    def _detect_project_main_language(self, project_path: str) -> str:
        """
        检测项目的主要编程语言
        
        Args:
            project_path: 项目路径
            
        Returns:
            str: 主要语言 (python, javascript, java, go, etc.)
        """
        try:
            project_path = Path(project_path)
            
            # 语言检测策略
            language_indicators = {
                'python': {
                    'config_files': ['requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile', 'poetry.lock'],
                    'extensions': ['.py'],
                    'dirs': ['venv', '.venv', '__pycache__']
                },
                'javascript': {
                    'config_files': ['package.json', 'yarn.lock', 'package-lock.json'],
                    'extensions': ['.js', '.jsx', '.ts', '.tsx'],
                    'dirs': ['node_modules', 'dist', 'build']
                },
                'java': {
                    'config_files': ['pom.xml', 'build.gradle', 'gradle.properties'],
                    'extensions': ['.java'],
                    'dirs': ['target', 'build', 'src/main/java']
                },
                'go': {
                    'config_files': ['go.mod', 'go.sum'],
                    'extensions': ['.go'],
                    'dirs': ['vendor']
                },
                'rust': {
                    'config_files': ['Cargo.toml', 'Cargo.lock'],
                    'extensions': ['.rs'],
                    'dirs': ['target']
                },
                'csharp': {
                    'config_files': ['.csproj', '.sln'],
                    'extensions': ['.cs'],
                    'dirs': ['bin', 'obj']
                }
            }
            
            language_scores = {}
            
            # 检查配置文件存在性（强指示器）
            for lang, indicators in language_indicators.items():
                score = 0
                
                # 配置文件检查（权重最高）
                for config_file in indicators['config_files']:
                    if (project_path / config_file).exists():
                        score += 50
                        
                # 特定目录检查
                for dir_name in indicators['dirs']:
                    if (project_path / dir_name).exists():
                        score += 20
                
                # 文件扩展名统计
                file_count = 0
                try:
                    for ext in indicators['extensions']:
                        file_count += len(list(project_path.rglob(f"*{ext}")))
                    score += min(file_count * 2, 100)  # 每个文件2分，最多100分
                except Exception:
                    pass
                    
                if score > 0:
                    language_scores[lang] = score
            
            if language_scores:
                main_language = max(language_scores.items(), key=lambda x: x[1])[0]
                max_score = language_scores[main_language]
                logger.debug(f"项目主要语言检测: {main_language} (得分: {max_score})")
                logger.debug(f"所有语言得分: {language_scores}")
                return main_language
            else:
                logger.debug("未能检测到明确的项目主要语言，默认使用 python")
                return 'python'  # 默认
                
        except Exception as e:
            logger.warning(f"项目主要语言检测失败: {e}")
            return 'python'  # 安全默认值
    @staticmethod
    def _get_readme_section(project_path: str) -> str:
        """
        获取项目 README 文件内容组成的 section 用于拼接 prompt
        
        Args:
            project_path: 项目路径
            
        Returns:
            str: README section
        """
        try:
            project_path = Path(project_path).resolve()

            # 常见的 README 文件名
            readme_names = [
                'README.md', 'readme.md', 'Readme.md',
                'README.rst', 'readme.rst', 'Readme.rst',
                'README.txt', 'readme.txt', 'Readme.txt',
                'README', 'readme', 'Readme'
            ]

            # 在项目根目录查找 README 文件
            for readme_name in readme_names:
                readme_path = project_path / readme_name
                if readme_path.exists() and readme_path.is_file():
                    try:
                        # 尝试以UTF-8编码读取
                        content = readme_path.read_text(encoding='utf-8')
                        logger.debug(f"成功读取 README 文件: {readme_path}")
                        readme_content = content
                        break
                    except Exception as e:
                        logger.warning(f"读取 README 文件失败 {readme_path}: {e}")
                        continue
            else:
                logger.debug(f"项目 {project_path} 中未找到 README 文件")
                readme_content = ""

        except Exception as e:
            logger.warning(f"获取 README 内容失败: {e}")
            readme_content = ""

        # 构建包含README的提示词
        if readme_content:
            readme_section = f"""

**PROJECT README (CONTEXT ONLY - DO NOT EXTRACT FUNCTIONS FROM HERE):**
```markdown
{readme_content}
```

**REMINDER: README is provided for understanding project context and implementation details only. All functions MUST come from the usage_md above. Do not create any functions based on README content.**"""
        else:
            readme_section = "\n**PROJECT README:** Not found or empty"

        return readme_section

    def _get_project_structure_summary(self, project_path: str, max_depth: int = 10) -> str:
        """获取项目结构摘要 - 使用pathlib，最多4层深度"""
        try:
            project_path = Path(project_path).resolve()
            structure_lines = []
            
            def add_path(path: Path, prefix: str = "", depth: int = 0):
                """递归添加路径结构"""
                if depth >= max_depth:
                    return
                
                try:
                    # 过滤并排序项目
                    items = []
                    for item in path.iterdir():
                        # 跳过隐藏文件和常见的忽略目录
                        if item.name.startswith('.'):
                            continue
                        if item.name in ['__pycache__', 'node_modules', '.git', 'venv', '.venv']:
                            continue
                        items.append(item)
                    
                    # 排序：目录在前，文件在后，按名称排序
                    items.sort(key=lambda p: (p.is_file(), p.name.lower()))
                    
                    # 限制每层最多显示20个项目
                    items = items[:20]
                    
                    for i, item in enumerate(items):
                        is_last = i == len(items) - 1
                        current_prefix = "└── " if is_last else "├── "
                        structure_lines.append(f"{prefix}{current_prefix}{item.name}")
                        
                        # 如果是目录且未达到最大深度，继续递归
                        if item.is_dir() and depth < max_depth - 1:
                            next_prefix = prefix + ("    " if is_last else "│   ")
                            add_path(item, next_prefix, depth + 1)
                            
                except PermissionError:
                    structure_lines.append(f"{prefix}├── [Permission Denied]")
                except Exception as e:
                    logger.debug(f"访问目录失败: {path} - {e}")
            
            # 添加根目录名称
            structure_lines.append(project_path.name + "/")
            add_path(project_path)
            
            # 限制总行数，避免输出过长
            return "\n".join(structure_lines[:100])
            
        except Exception as e:
            logger.warning(f"获取项目结构失败: {e}")
            return f"项目路径: {project_path}"
    
    def _normalize_runtime_environment(self, runtime_env: Dict[str, Any], usage_md: str = "") -> Dict[str, Any]:
        """
        规范化runtime_environment格式以确保与EnvironmentRegistry兼容
        
        Args:
            runtime_env: 来自LLM的原始runtime_environment
            usage_md: 原始usage_md文档，用于推断缺失信息
            
        Returns:
            Dict[str, Any]: 规范化的runtime_environment
        """
        if not runtime_env or not isinstance(runtime_env, dict):
            logger.warning("runtime_environment为空或格式错误，使用默认值")
            return {
                'type': 'system',
                'name': None,
                'activation_command': None,
                'python_interpreter': 'python',
                'confidence': 'low',
                'indicators': []
            }
        
        # 确保必需字段存在
        normalized = {
            'type': runtime_env.get('type', 'system'),
            'name': runtime_env.get('name'),
            'activation_command': runtime_env.get('activation_command'),
            'python_interpreter': runtime_env.get('python_interpreter'),
            'confidence': runtime_env.get('confidence', 'medium'),
            'indicators': runtime_env.get('indicators', [])
        }
        
        # 验证和修复type字段
        valid_types = ['conda', 'uv', 'poetry', 'venv', 'system', 'docker']
        if normalized['type'] not in valid_types:
            logger.warning(f"无效的环境类型: {normalized['type']}，回退到system")
            normalized['type'] = 'system'
        
        # 根据类型设置默认值
        env_type = normalized['type']
        if env_type == 'conda':
            if not normalized['name']:
                normalized['name'] = 'base'
            if not normalized['activation_command']:
                normalized['activation_command'] = f"conda activate {normalized['name']}"
        elif env_type == 'uv':
            if not normalized['activation_command']:
                normalized['activation_command'] = 'uv run'
        elif env_type == 'poetry':
            if not normalized['activation_command']:
                normalized['activation_command'] = 'poetry run'
        elif env_type == 'venv':
            if not normalized['name']:
                normalized['name'] = '.venv'
            if not normalized['activation_command']:
                normalized['activation_command'] = f"source {normalized['name']}/bin/activate"
        elif env_type == 'docker':
            # Docker环境特殊处理
            pass
        else:  # system
            if not normalized['python_interpreter']:
                normalized['python_interpreter'] = 'python'
        
        # 从usage_md推断缺失的信息
        if not normalized['python_interpreter'] and usage_md:
            python_path = self._extract_python_path_from_usage(usage_md)
            if python_path:
                normalized['python_interpreter'] = python_path
                
        if not normalized['indicators'] and usage_md:
            normalized['indicators'] = self._extract_environment_indicators(usage_md)
        
        logger.debug(f"runtime_environment规范化完成: {normalized['type']} (置信度: {normalized['confidence']})")
        return normalized
    
    def _extract_python_path_from_usage(self, usage_md: str) -> Optional[str]:
        """从usage_md中提取Python解释器路径"""
        try:
            import re
            # 查找形如 /opt/conda/bin/python 的路径
            python_path_pattern = r'(/[^\s]*python[0-9.]*(?:\.[0-9]+)*)'
            matches = re.findall(python_path_pattern, usage_md)
            if matches:
                return matches[0]
        except Exception as e:
            logger.debug(f"从usage_md提取Python路径失败: {e}")
        return None
    
    def _extract_environment_indicators(self, usage_md: str) -> List[str]:
        """从usage_md中提取环境指示器"""
        indicators = []
        try:
            usage_lower = usage_md.lower()
            if 'conda activate' in usage_lower:
                indicators.append('conda activate command')
            if 'uv run' in usage_lower:
                indicators.append('uv run command')
            if 'poetry run' in usage_lower:
                indicators.append('poetry run command')
            if 'source .venv' in usage_lower or 'source venv' in usage_lower:
                indicators.append('venv activation')
            if 'docker run' in usage_lower:
                indicators.append('docker run command')
        except Exception as e:
            logger.debug(f"提取环境指示器失败: {e}")
        return indicators


# 工厂函数
def create_script_analyzer(llm_provider) -> ScriptAnalyzer:
    """
    创建脚本分析器实例
    
    Args:
        llm_provider: LLM提供者实例（必传）
        
    Returns:
        ScriptAnalyzer: 脚本分析器实例
    """
    return ScriptAnalyzer(llm_provider)