"""
路径解析服务 - 动态解析项目路径、脚本路径和环境路径
基于配置管理器提供的机器特定配置解析实际路径
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from loguru import logger

from .config_manager import ConfigManager, ProjectConfig, EnvironmentConfig


@dataclass
class ResolvedPaths:
    """解析后的路径信息"""
    project_path: str
    script_path: str
    script_dir: str
    function_config_path: str


@dataclass
class ResolvedEnvironment:
    """解析后的环境信息"""
    env_type: str
    env_name: Optional[str]
    env_path: Optional[str]
    activation_command: Optional[str]
    execution_command_template: str


class PathResolver:
    """路径解析器 - 基于配置动态解析路径"""
    
    def __init__(self, config_manager: ConfigManager):
        """
        初始化路径解析器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        logger.info("路径解析器初始化完成")
    
    def resolve_project_paths(self, project_key: str, script_file: str) -> Optional[ResolvedPaths]:
        """
        解析项目相关路径 - 支持虚拟/占位符项目路径
        
        Args:
            project_key: 项目配置键
            script_file: 脚本文件名
            
        Returns:
            ResolvedPaths: 解析后的路径信息
        """
        # 获取项目配置
        project_config = self.config_manager.get_project_config(project_key)
        if not project_config:
            logger.error(f"项目配置不存在: {project_key}")
            return None
        
        # 处理虚拟/占位符项目路径
        if self._is_virtual_project_path(project_config.project_path):
            logger.debug(f"检测到虚拟项目路径: {project_config.project_path}")
            # 使用虚拟路径，不进行实际路径解析
            project_path = project_config.project_path
        else:
            # 解析真实项目路径
            project_path = str(Path(project_config.project_path).resolve())
        
        # 解析脚本路径（这些总是真实路径）
        scripts_dir = self.config_manager.get_scripts_dir()
        script_path = scripts_dir / script_file
        
        # 解析功能配置文件路径
        function_config_path = self.config_manager.get_functions_dir() / f"{project_key}_functions.json"
        
        resolved_paths = ResolvedPaths(
            project_path=project_path,
            script_path=str(script_path.resolve()),
            script_dir=str(scripts_dir.resolve()),
            function_config_path=str(function_config_path.resolve())
        )
        
        logger.debug(f"路径解析完成 {project_key}: 项目={project_path}, 脚本={script_path}")
        return resolved_paths
    
    def resolve_environment(self, env_key: str) -> Optional[ResolvedEnvironment]:
        """
        解析环境配置
        
        Args:
            env_key: 环境配置键
            
        Returns:
            ResolvedEnvironment: 解析后的环境信息
        """
        # 获取环境配置
        env_config = self.config_manager.get_environment_config(env_key)
        if not env_config:
            logger.error(f"环境配置不存在: {env_key}")
            return None
        
        # 根据环境类型生成执行命令模板
        execution_template = self._build_execution_template(env_config)
        
        resolved_env = ResolvedEnvironment(
            env_type=env_config.env_type,
            env_name=env_config.env_name,
            env_path=env_config.env_path,
            activation_command=env_config.activation_command,
            execution_command_template=execution_template
        )
        
        logger.debug(f"环境解析完成 {env_key}: {env_config.env_type}")
        return resolved_env
    
    def _build_execution_template(self, env_config: EnvironmentConfig) -> str:
        """
        根据环境配置构建执行命令模板
        
        Args:
            env_config: 环境配置
            
        Returns:
            str: 执行命令模板，{command} 为占位符
        """
        if env_config.env_type == "conda":
            if env_config.env_name:
                return f"conda run -n {env_config.env_name} {{command}}"
            else:
                return "conda run {command}"
        
        elif env_config.env_type == "venv":
            if env_config.activation_command:
                return f"{env_config.activation_command} && {{command}}"
            elif env_config.env_path:
                # 自动构建激活命令
                activate_script = Path(env_config.env_path) / "bin" / "activate"
                if activate_script.exists():
                    return f"source {activate_script} && {{command}}"
                else:
                    # Windows环境
                    activate_script = Path(env_config.env_path) / "Scripts" / "activate.bat"
                    if activate_script.exists():
                        return f"{activate_script} && {{command}}"
            return "{command}"
        
        elif env_config.env_type == "poetry":
            return "poetry run {command}"
        
        elif env_config.env_type == "system":
            return "{command}"
        
        else:
            logger.warning(f"未知环境类型: {env_config.env_type}")
            return "{command}"
    
    def _is_virtual_project_path(self, project_path: str) -> bool:
        """
        判断是否为虚拟/占位符项目路径
        
        Args:
            project_path: 项目路径
            
        Returns:
            bool: 是否为虚拟路径
        """
        return project_path == "N/A" or project_path.startswith("N/A:")
    
    def resolve_script_execution_command(self, project_key: str, script_file: str, 
                                       env_key: str, base_command: str) -> Optional[str]:
        """
        解析脚本执行命令
        
        Args:
            project_key: 项目配置键
            script_file: 脚本文件名
            env_key: 环境配置键
            base_command: 基础命令
            
        Returns:
            str: 完整的执行命令
        """
        # 解析路径
        paths = self.resolve_project_paths(project_key, script_file)
        if not paths:
            return None
        
        # 解析环境
        env = self.resolve_environment(env_key)
        if not env:
            return None
        
        # 构建完整命令
        # 将脚本路径替换到基础命令中
        if "python" in base_command and script_file.endswith(".py"):
            # Python脚本的情况
            full_command = base_command.replace("python", f"python {paths.script_path}")
        else:
            # 其他情况直接使用脚本路径
            full_command = f"{base_command} {paths.script_path}"
        
        # 应用环境执行模板
        final_command = env.execution_command_template.format(command=full_command)
        
        logger.debug(f"执行命令解析完成: {final_command}")
        return final_command
    
    def validate_paths(self, project_key: str, script_file: str) -> Dict[str, Any]:
        """
        验证路径有效性 - 支持虚拟路径
        
        Args:
            project_key: 项目配置键
            script_file: 脚本文件名
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # 解析路径
        paths = self.resolve_project_paths(project_key, script_file)
        if not paths:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"无法解析项目路径: {project_key}")
            return validation_result
        
        # 验证项目路径（虚拟路径跳过物理存在性检查）
        if self._is_virtual_project_path(paths.project_path):
            validation_result["warnings"].append(f"使用虚拟项目路径: {paths.project_path}")
        elif not Path(paths.project_path).exists():
            validation_result["errors"].append(f"项目路径不存在: {paths.project_path}")
            validation_result["is_valid"] = False
        
        # 验证脚本文件
        if not Path(paths.script_path).exists():
            validation_result["warnings"].append(f"脚本文件不存在: {paths.script_path}")
        
        # 验证脚本目录
        if not Path(paths.script_dir).exists():
            validation_result["warnings"].append(f"脚本目录不存在: {paths.script_dir}")
        
        return validation_result
    
    def get_portable_config(self, project_key: str) -> Optional[Dict[str, Any]]:
        """
        获取可迁移的配置信息（不包含机器特定路径）
        
        Args:
            project_key: 项目配置键
            
        Returns:
            Dict[str, Any]: 可迁移的配置
        """
        # 加载功能配置
        function_config = self.config_manager.load_function_config(project_key)
        if not function_config:
            return None
        
        # 获取项目配置以获取环境键
        project_config = self.config_manager.get_project_config(project_key)
        if not project_config:
            return None
        
        portable_config = {
            "project_name": function_config.get("project_name"),
            "project_key": project_key,
            "functions": function_config.get("functions", {}),
            "environment_keys": project_config.environment_keys,
            "created_at": function_config.get("created_at"),
            "updated_at": function_config.get("updated_at")
        }
        
        return portable_config
    
    def create_migration_package(self, project_keys: list = None) -> Dict[str, Any]:
        """
        创建迁移包（包含所有可迁移内容）
        
        Args:
            project_keys: 要包含的项目键列表，None表示所有项目
            
        Returns:
            Dict[str, Any]: 迁移包信息
        """
        migration_package = {
            "metadata": {
                "created_at": "2025-08-18",
                "description": "API Repository 迁移包",
                "version": "1.0"
            },
            "projects": {},
            "scripts": {},
            "config_template": {}
        }
        
        # 如果未指定项目，包含所有项目
        if project_keys is None:
            function_files = self.config_manager.list_function_files()
            project_keys = [f.stem.replace("_functions", "") for f in function_files]
        
        # 收集项目配置和脚本
        for project_key in project_keys:
            portable_config = self.get_portable_config(project_key)
            if portable_config:
                migration_package["projects"][project_key] = portable_config
                
                # 收集脚本文件
                functions = portable_config.get("functions", {})
                for func_name, func_data in functions.items():
                    script_file = func_data.get("script_file")
                    if script_file:
                        script_path = self.config_manager.get_scripts_dir() / script_file
                        if script_path.exists():
                            with open(script_path, 'r', encoding='utf-8') as f:
                                migration_package["scripts"][script_file] = f.read()
        
        # 生成配置模板
        migration_package["config_template"] = self.config_manager.generate_config_template(
            [self.config_manager.load_function_config(pk).get("project_name", pk) 
             for pk in project_keys]
        )
        
        logger.info(f"迁移包创建完成: {len(project_keys)} 个项目")
        return migration_package


def create_path_resolver(config_manager: ConfigManager) -> PathResolver:
    """
    创建路径解析器实例
    
    Args:
        config_manager: 配置管理器实例
        
    Returns:
        PathResolver: 路径解析器实例
    """
    return PathResolver(config_manager)