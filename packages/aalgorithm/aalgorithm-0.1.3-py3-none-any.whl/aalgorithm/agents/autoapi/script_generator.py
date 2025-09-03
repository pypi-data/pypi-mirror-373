"""
脚本生成器 - 简化版，生成包装脚本调用已部署项目
根据功能分析结果生成可执行的调用脚本
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional

from loguru import logger

from .script_analyzer import FunctionInfo, ProjectAnalysis, ScriptAnalyzer

@dataclass
class GeneratedScript:
    """生成的脚本信息"""
    function_name: str
    script_path: str
    script_type: str
    parameters: List[Dict[str, Any]]
    command_template: str
    test_cases: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class ScriptGenerator:
    """脚本生成器 - 根据项目特性生成最优的包装脚本，支持原生调用方式"""
    
    def __init__(self, llm_provider):
        """
        初始化脚本生成器
        
        Args:
            llm_provider: LLM提供者实例（必传），用于智能生成包装脚本
        """
        if llm_provider is None:
            raise ValueError("llm_provider 是必传参数，AutoAPI 需要 LLM 进行智能脚本生成")
        self.llm_provider = llm_provider

    async def generate_scripts(self, analysis: ProjectAnalysis, output_dir: str, usage_md: str = "") -> List[GeneratedScript]:
        """
        为项目分析结果生成最优的包装脚本
        
        Args:
            analysis: 项目分析结果
            output_dir: 脚本输出目录
            usage_md: 原始usage_md文档（包含环境信息）
            
        Returns:
            List[GeneratedScript]: 生成的包装脚本列表
        """
        logger.info(f"开始为项目 {analysis.project_name} 生成 {len(analysis.functions)} 个包装脚本")
        
        scripts = []
        for function_info in analysis.functions:
            script = await self.generate_single_script(function_info, analysis, output_dir, usage_md)
            if script:
                scripts.append(script)
        
        logger.info(f"成功生成 {len(scripts)}/{len(analysis.functions)} 个脚本")
        return scripts
    
    async def generate_single_script(self, function_info: FunctionInfo, 
                               project_analysis: ProjectAnalysis, 
                               output_dir: str, usage_md: str = "") -> Optional[GeneratedScript]:
        """生成单个最优包装脚本"""
        try:
            logger.info(f"开始生成包装脚本: {function_info.name}")


            # 步骤1: 获取README内容作为实现参考
            readme_content = ScriptAnalyzer._get_readme_section(project_analysis.project_path)

            # 步骤2: 生成功能脚本
            script_response = await self._generate_optimal_script(
                function_info, project_analysis, usage_md, readme_content
            )
            
            if not script_response:
                logger.error("脚本生成失败")
                return None
            
            # 创建输出目录
            output_path = Path(output_dir).resolve()
            output_path.mkdir(parents=True, exist_ok=True)

            # 获取脚本内容和类型
            script_content = script_response.get('script_content', '')
            script_type = script_response.get('script_type', 'python')

            # 确定文件扩展名
            file_ext = self._get_file_extension(script_type)
            script_path = output_path / f"{function_info.name}{file_ext}"
            
            # 保存脚本文件
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)

            # 设置执行权限
            if os.name == 'posix':
                os.chmod(script_path, 0o755)

            logger.info(f"生成{script_type}脚本完成: {script_path}")
            
            return GeneratedScript(
                function_name=function_info.name,
                script_path=str(script_path.resolve()),
                script_type=script_type,
                parameters=function_info.parameters,
                command_template=function_info.command_template,
                test_cases=[],  # 测试用例将在第3步独立生成
                metadata={
                    'project_path': project_analysis.project_path,
                    'parameters': function_info.parameters,
                    'cli_mappings': function_info.cli_mappings or {},
                    'runtime_environment': project_analysis.runtime_environment,
                    # 脚本分析信息
                    'api_analysis': script_response.get('api_analysis', {
                        'implementation_approach': 'readme_based',
                        'llm_generated': True
                    }),
                    # 简化的元数据
                    'portable_metadata': {
                        'project_key': project_analysis.project_name.lower(),
                        'script_file': f"{function_info.name}{file_ext}",
                        'script_type': script_type
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"生成脚本失败: {e}")
            return None


    async def _generate_optimal_script(self, function_info: FunctionInfo,
                                       project_analysis: ProjectAnalysis,
                                       usage_md: str = "",
                                       readme_content: str = "") -> Optional[Dict[str, Any]]:
        """基于README内容生成功能脚本"""
        try:
            import json
            from .prompts import ENHANCED_SCRIPT_GENERATION_PROMPT
            
            logger.info(f"使用LLM生成脚本: {function_info.name}")
            
            # 简化的参数传递，只保留核心信息
            prompt = ENHANCED_SCRIPT_GENERATION_PROMPT.format(
                function_name=function_info.name,
                function_description=function_info.description,
                command_template=function_info.command_template,
                function_parameters=json.dumps(function_info.parameters, indent=2, ensure_ascii=False),
                expected_output=function_info.expected_output,
                function_examples=json.dumps(function_info.examples, indent=2, ensure_ascii=False),
                usage_md=usage_md,
                readme_content=readme_content
            )
            
            # 调用LLM生成脚本
            response = await self.llm_provider.generate_completion_async(
                system_prompt="你是开源项目包装脚本专家。生成完全自包含的Python脚本，严格禁止使用需要外部API密钥或服务的参数（如--use_llm）。硬编码参数必须是项目原生功能，无需额外配置。绝对禁止环境激活代码，确保脚本可以独立运行。",
                user_prompt=prompt,
                json_format=True,
                model='claude-sonnet-4-20250514',
                max_tokens=8000
            )
            
            if not response or "script_content" not in response:
                logger.error("LLM 未返回有效的脚本内容")
                return None
            
            logger.info(f"脚本生成完成: {function_info.name}")
            logger.debug(f"实现方式: {response.get('implementation_approach', 'unknown')}")
            
            return {
                "script_content": response.get("script_content", ""),
                "script_type": response.get("script_type", "python"),
                "api_analysis": {
                    "implementation_approach": response.get("implementation_approach", "readme_based"),
                    "output_format_handling": response.get("output_format_handling", ""),
                    "parameter_constraints": response.get("parameter_constraints", "text和file_path限制"),
                    "llm_generated": True
                },
                "notes": response.get("notes", "")
            }
            
        except Exception as e:
            logger.error(f"LLM脚本生成失败: {e}")
            return None
    
    def _get_file_extension(self, script_type: str) -> str:
        """根据脚本类型获取文件扩展名"""
        extension_map = {
            'python': '.py',
            'shell': '.sh', 
            'bash': '.sh',
            'node': '.js',
            'javascript': '.js',
            'typescript': '.ts'
        }
        return extension_map.get(script_type, '.py')


    
    
    async def generate_test_cases(self, script: 'GeneratedScript', project_analysis: ProjectAnalysis, usage_md: str = "") -> List[Dict[str, Any]]:
        """为脚本生成最多2个测试用例，使用真实项目文件"""
        try:
            logger.info(f"为脚本 {script.function_name} 生成测试用例")
            
            # 扫描项目文件，为测试用例提供真实文件
            available_files = self._scan_project_files(project_analysis.project_path)
            
            # 使用environment_manager生成正确的执行命令模板
            from .environment_manager import create_environment_registry
            env_registry = create_environment_registry()
            
            # 从项目分析结果创建环境信息
            if project_analysis.runtime_environment:
                env_info = env_registry.create_environment_from_analysis(project_analysis.runtime_environment)
                # 生成基础命令（python script.py）的执行命令模板
                base_command = f"python {script.script_path}"
                execution_command_template = env_registry.get_execution_command(env_info, base_command)
            else:
                execution_command_template = f"python {script.script_path}"
            
            # 调用LLM生成测试用例
            from .prompts import SIMPLE_TEST_CASE_PROMPT
            
            prompt = SIMPLE_TEST_CASE_PROMPT.format(
                function_name=script.function_name,
                script_path=script.script_path,
                available_files=available_files,
                parameters=script.parameters,
                runtime_environment=project_analysis.runtime_environment,
                execution_command_template=execution_command_template
            )
            
            response = await self.llm_provider.generate_completion_async(
                system_prompt="你是测试专家。生成使用标准化参数格式的测试用例：位置参数（输入内容或文件路径）+ -o（输出路径）。不要使用--input或--input_path等选项参数。",
                user_prompt=prompt,
                json_format=True,
                model='claude-sonnet-4-20250514',
                max_tokens=2000
            )
            
            if response and "test_cases" in response:
                test_cases = response["test_cases"][:2]  # 最多2个
                logger.info(f"成功生成 {len(test_cases)} 个测试用例")
                return test_cases
            else:
                logger.warning("LLM未返回有效测试用例")
                return []
                
        except Exception as e:
            logger.error(f"测试用例生成失败: {e}")
            return []
    
    
    def _scan_project_files(self, project_path: str) -> str:
        """扫描项目文件，为测试用例生成提供文件列表"""
        try:
            from pathlib import Path
            
            # 处理虚拟路径 (N/A:project-name)
            if project_path.startswith("N/A:"):
                return "项目路径为虚拟路径，无实际文件可扫描"
            
            project_path = Path(project_path).resolve()
            if not project_path.exists():
                return f"项目路径不存在: {project_path}"
            
            # 收集文件信息
            files_info = []
            file_count = 0
            max_files = 20  # 限制文件数量避免prompt过长
            
            # 优先收集常见的测试文件类型
            priority_patterns = [
                "*.txt", "*.md", "*.pdf", "*.json", "*.csv", 
                "*.xml", "*.yaml", "*.yml", "*.py", "*.js"
            ]
            
            for pattern in priority_patterns:
                if file_count >= max_files:
                    break
                for file_path in project_path.glob(f"**/{pattern}"):
                    if file_count >= max_files:
                        break
                    if file_path.is_file():
                        # 跳过隐藏文件和常见忽略目录
                        if any(part.startswith('.') for part in file_path.parts):
                            continue
                        if any(ignore_dir in file_path.parts 
                               for ignore_dir in ['__pycache__', 'node_modules', '.git']):
                            continue
                        
                        relative_path = file_path.relative_to(project_path)
                        file_size = file_path.stat().st_size
                        files_info.append(f"{relative_path} ({file_size} bytes)")
                        file_count += 1
            
            if files_info:
                return "项目文件列表:\n" + "\n".join(files_info)
            else:
                return "未找到合适的测试文件"
                
        except Exception as e:
            logger.warning(f"项目文件扫描失败: {e}")
            return "文件扫描失败，无可用文件信息"
    
    async def _call_llm_for_test_cases(self, function_info: FunctionInfo, script_path: str,
                                     script_content: str, project_analysis: ProjectAnalysis,
                                     available_files: str, base_command: str) -> Optional[Dict[str, Any]]:
        """调用 LLM 生成测试用例"""
        try:
            from .prompts import GENERATE_TEST_CASES_PROMPT
            
            # 准备 prompt 参数
            prompt = GENERATE_TEST_CASES_PROMPT.format(
                function_name=function_info.name,
                script_type="python",  # 固定为 python
                script_path=script_path,
                base_command=base_command,
                script_content=script_content,
                project_path=project_analysis.project_path,
                function_description=function_info.description,
                function_parameters=json.dumps(function_info.parameters, indent=2, ensure_ascii=False),
                available_files=available_files
            )
            
            logger.debug(f"调用LLM生成测试用例: {function_info.name}")
            
            # 调用 LLM
            response = await self.llm_provider.generate_completion_async(
                system_prompt="你是专业的Python测试用例生成专家。分析Python脚本内容，生成高质量的可执行测试用例。",
                user_prompt=prompt,
                json_format=True,
                model='claude-sonnet-4-20250514',
                max_tokens=4000
            )
            
            return response
            
        except Exception as e:
            logger.error(f"LLM测试用例生成调用失败: {e}")
            return None
    
    


# 工厂函数
def create_script_generator(llm_provider) -> ScriptGenerator:
    """
    创建脚本生成器实例
    
    Args:
        llm_provider: LLM提供者实例（必传）
        
    Returns:
        ScriptGenerator: 脚本生成器实例
    """
    return ScriptGenerator(llm_provider)