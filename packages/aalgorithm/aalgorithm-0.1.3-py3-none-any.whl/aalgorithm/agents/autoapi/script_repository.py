"""
脚本仓库 - 基于可迁移架构的统一脚本存储和管理
支持通用配置和机器特定配置分离，实现完全可迁移的API仓库
"""

import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
# Import types for compatibility
from typing import TYPE_CHECKING

from loguru import logger

from .config_manager import create_config_manager
from .path_resolver import create_path_resolver

if TYPE_CHECKING:
    pass


@dataclass
class FunctionDefinition:
    """功能定义（通用，可迁移）"""
    function_name: str
    script_file: str  # 相对文件名
    script_type: str
    environment_key: str  # 环境配置键
    parameters: List[Dict[str, Any]]
    command_template: str
    cli_mappings: Dict[str, Any] = None  # CLI参数映射
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "function_name": self.function_name,
            "script_file": self.script_file,
            "script_type": self.script_type,
            "environment_key": self.environment_key,
            "parameters": self.parameters,
            "command_template": self.command_template
        }
        if self.cli_mappings:
            result["cli_mappings"] = self.cli_mappings
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FunctionDefinition':
        """从字典创建"""
        return cls(
            function_name=data.get("function_name", ""),
            script_file=data.get("script_file", ""),
            script_type=data.get("script_type", "python"),
            environment_key=data.get("environment_key", ""),
            parameters=data.get("parameters", []),
            command_template=data.get("command_template", ""),
            cli_mappings=data.get("cli_mappings", {})  # 支持向后兼容
        )


@dataclass
class ProjectRepository:
    """项目仓库（通用定义）"""
    project_name: str
    project_key: str  # 机器配置中的键
    functions: Dict[str, FunctionDefinition]  # function_name -> FunctionDefinition
    created_at: str
    updated_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "project_name": self.project_name,
            "project_key": self.project_key,
            "functions": {name: func.to_dict() for name, func in self.functions.items()},
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectRepository':
        """从字典创建"""
        functions = {}
        for name, func_data in data.get("functions", {}).items():
            functions[name] = FunctionDefinition.from_dict(func_data)
        
        return cls(
            project_name=data.get("project_name", ""),
            project_key=data.get("project_key", ""),
            functions=functions,
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", "")
        )


class ScriptRepository:
    """脚本仓库 - 支持可迁移架构"""
    
    def __init__(self, repository_root: str = None):
        """
        初始化脚本仓库
        
        Args:
            repository_root: 仓库根目录
        """
        # 初始化配置管理器和路径解析器
        self.config_manager = create_config_manager(repository_root)
        self.path_resolver = create_path_resolver(self.config_manager)
        
        # 仓库根目录
        self.repository_root = self.config_manager.repository_root
        
        # 索引文件
        self.index_file = self.repository_root / "routes_index.json"
        
        # 加载项目仓库
        self.repositories: Dict[str, ProjectRepository] = {}
        self._load_repositories()
        
        logger.info(f"脚本仓库初始化完成: {self.repository_root}")
    
    def create_project_repository(self, project_name: str, project_path: str,
                                 scripts: List[Any]) -> ProjectRepository:
        """
        为项目创建脚本仓库
        
        Args:
            project_name: 项目名称
            project_path: 项目路径（将写入机器配置）
            scripts: 生成的脚本列表
            
        Returns:
            ProjectRepository: 创建的项目仓库
        """
        logger.info(f"为项目 {project_name} 创建脚本仓库")
        
        project_key = project_name.lower()
        
        # 确保机器配置中有此项目
        self._ensure_project_in_machine_config(project_key, project_name, project_path, scripts)
        
        # 处理每个脚本，创建功能定义
        functions = {}
        for script in scripts:
            function_def = self._create_function_definition(script, project_key)
            if function_def:
                functions[function_def.function_name] = function_def
                # 保存脚本文件到scripts目录
                self._save_script_file(script, function_def.script_file)
        
        # 创建项目仓库对象
        repository = ProjectRepository(
            project_name=project_name,
            project_key=project_key,
            functions=functions,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # 保存项目仓库
        self.repositories[project_key] = repository
        self._save_project_repository(repository)
        self._save_index()
        
        logger.info(f"项目仓库创建成功: {len(functions)} 个功能")
        return repository
    
    def update_project_repository(self, project_name: str, 
                                 scripts: List[Any]) -> Optional[ProjectRepository]:
        """
        更新项目脚本仓库
        
        Args:
            project_name: 项目名称
            scripts: 新的脚本列表
            
        Returns:
            ProjectRepository: 更新后的项目仓库
        """
        project_key = project_name.lower()
        
        if project_key not in self.repositories:
            logger.warning(f"项目 {project_name} 不存在，创建新仓库")
            # 需要项目路径信息，从脚本元数据中获取
            first_script = scripts[0] if scripts else None
            project_path = first_script.metadata.get('project_path', '') if first_script else ''
            return self.create_project_repository(project_name, project_path, scripts)
        
        repository = self.repositories[project_key]
        
        # 更新每个脚本
        updated_count = 0
        for script in scripts:
            function_def = self._create_function_definition(script, project_key)
            if function_def:
                repository.functions[function_def.function_name] = function_def
                self._save_script_file(script, function_def.script_file)
                updated_count += 1
        
        # 更新时间戳
        repository.updated_at = datetime.now().isoformat()
        
        # 保存更新
        self._save_project_repository(repository)
        self._save_index()
        
        logger.info(f"项目仓库更新完成: {updated_count} 个功能有更新")
        return repository

    def _resolve_project_name(self, project_name: str) -> Optional[str]:
        """
        智能解析项目名称，支持大小写不敏感查找
        
        Args:
            project_name: 输入的项目名称（任意大小写）
            
        Returns:
            str: 解析出的真实项目名称，如果未找到则返回None
        """
        project_key = project_name.lower()

        # 首先尝试直接匹配project_key
        if project_key in self.repositories:
            return self.repositories[project_key].project_name

        # 如果直接匹配失败，尝试通过显示名称匹配
        for repo_key, repository in self.repositories.items():
            if repository.project_name.lower() == project_key:
                return repository.project_name

        # 都没有找到
        return None
    
    def get_project_repository(self, project_name: str) -> Optional[ProjectRepository]:
        """获取项目仓库（支持大小写不敏感）"""
        # 使用智能名称解析
        resolved_project_name = self._resolve_project_name(project_name)
        if not resolved_project_name:
            return None

        project_key = resolved_project_name.lower()
        return self.repositories.get(project_key)
    
    def list_projects(self) -> List[str]:
        """列出所有项目名称"""
        projects = [repo.project_name for repo in self.repositories.values()]
        logger.debug(f"列出项目: {projects} (总计: {len(projects)})")
        return projects
    
    def delete_project_repository(self, project_name: str) -> bool:
        """删除项目仓库"""
        project_key = project_name.lower()
        
        if project_key not in self.repositories:
            return False
        
        repository = self.repositories[project_key]
        
        try:
            # 删除功能配置文件
            function_file = self.config_manager.get_functions_dir() / f"{project_key}_functions.json"
            if function_file.exists():
                function_file.unlink()
            
            # 删除脚本文件
            for function_def in repository.functions.values():
                script_path = self.config_manager.get_scripts_dir() / function_def.script_file
                if script_path.exists():
                    script_path.unlink()
            
            # 从内存中移除
            del self.repositories[project_key]
            
            # 更新索引
            self._save_index()
            
            logger.info(f"项目仓库已删除: {project_name}")
            return True
            
        except Exception as e:
            logger.error(f"删除项目仓库失败: {project_name} - {e}")
            return False
    
    def get_function_info(self, project_name: str, function_name: str) -> Optional[Dict[str, Any]]:
        """
        获取函数信息（包含解析后的路径）
        
        Args:
            project_name: 项目名称（支持大小写不敏感）
            function_name: 函数名称
            
        Returns:
            Dict[str, Any]: 包含路径信息的函数配置
        """
        # 使用智能名称解析
        resolved_project_name = self._resolve_project_name(project_name)
        if not resolved_project_name:
            logger.debug(f"项目仓库不存在: {project_name}")
            return None

        project_key = resolved_project_name.lower()
        repository = self.repositories.get(project_key)
        
        if not repository:
            logger.debug(f"项目仓库不存在: {project_name}")
            return None
        
        function_def = repository.functions.get(function_name)
        if not function_def:
            logger.debug(f"函数不存在: {project_name}/{function_name}")
            return None
        
        # 解析路径
        resolved_paths = self.path_resolver.resolve_project_paths(project_key, function_def.script_file)
        resolved_env = self.path_resolver.resolve_environment(function_def.environment_key)
        
        if not resolved_paths or not resolved_env:
            logger.error(f"路径解析失败: {project_name}/{function_name}")
            return None
        
        # 构建完整的函数信息
        function_info = {
            "function_name": function_def.function_name,
            "script_path": resolved_paths.script_path,  # 解析后的绝对路径
            "script_type": function_def.script_type,
            "environment": f"{resolved_env.env_type}:{resolved_env.env_name or 'default'}",
            "parameters": function_def.parameters,
            "command_template": function_def.command_template,
            "cli_mappings": getattr(function_def, 'cli_mappings', {}),  # CLI参数映射，支持向后兼容
            "project_path": resolved_paths.project_path,  # 解析后的项目路径
            "execution_template": resolved_env.execution_command_template
        }
        
        logger.debug(f"✅ 找到函数: {function_name}, 脚本路径: {resolved_paths.script_path}")
        return function_info
    
    def get_route_function(self, project_name: str, function_name: str) -> Optional['RouteFunction']:
        """
        获取路由函数信息（兼容性方法，支持大小写不敏感）
        
        Args:
            project_name: 项目名称（支持大小写不敏感）
            function_name: 函数名称
            
        Returns:
            RouteFunction: 兼容的路由函数对象
        """
        function_info = self.get_function_info(project_name, function_name)
        if not function_info:
            return None
        
        return RouteFunction(function_info)
    
    def _ensure_project_in_machine_config(self, project_key: str, project_name: str, 
                                        project_path: str, scripts: List[Any]):
        """确保项目存在于机器配置中，支持占位符项目路径"""
        machine_config = self.config_manager.machine_config
        
        # 处理占位符项目路径
        is_placeholder_path = project_path.startswith("N/A:")
        effective_project_path = project_path if not is_placeholder_path else "N/A"
        
        if not machine_config:
            # 创建新的机器配置
            from .config_manager import MachineConfig, ProjectConfig, EnvironmentConfig
            
            # 从脚本中推断环境信息
            env_key = f"{project_key}_env"
            env_info = self._infer_environment_from_scripts(scripts)
            
            machine_config = MachineConfig(
                projects={
                    project_key: ProjectConfig(
                        project_key=project_key,
                        project_path=effective_project_path,
                        environment_keys=[env_key]
                    )
                },
                environments={
                    env_key: EnvironmentConfig(
                        env_key=env_key,
                        env_type=env_info.get("type", "system"),
                        env_name=env_info.get("name"),
                        env_path=env_info.get("path"),
                        activation_command=env_info.get("activation_command")
                    )
                },
                repository_root=str(self.repository_root),
                scripts_dir="scripts"
            )
            
            self.config_manager.save_machine_config(machine_config)
            logger.info(f"创建机器配置: 项目 {project_name}")
        
        elif project_key not in machine_config.projects:
            # 添加新项目到现有配置
            from .config_manager import ProjectConfig, EnvironmentConfig
            
            env_key = f"{project_key}_env"
            env_info = self._infer_environment_from_scripts(scripts)
            
            machine_config.projects[project_key] = ProjectConfig(
                project_key=project_key,
                project_path=effective_project_path,
                environment_keys=[env_key]
            )
            
            machine_config.environments[env_key] = EnvironmentConfig(
                env_key=env_key,
                env_type=env_info.get("type", "system"),
                env_name=env_info.get("name"),
                env_path=env_info.get("path"),
                activation_command=env_info.get("activation_command")
            )
            
            self.config_manager.save_machine_config(machine_config)
            logger.info(f"添加项目到机器配置: {project_name}")
    
    def _infer_environment_from_scripts(self, scripts: List[Any]) -> Dict[str, Any]:
        """从脚本元数据中推断环境信息"""
        if not scripts:
            return {"type": "system"}
        
        # 从第一个脚本中获取环境信息
        first_script = scripts[0]
        metadata = getattr(first_script, 'metadata', {})
        
        # 优先使用detected_environment
        detected_env = metadata.get('detected_environment', {})
        if detected_env:
            return {
                "type": detected_env.get("type", "system"),
                "name": detected_env.get("name"),
                "path": detected_env.get("path"),
                "activation_command": detected_env.get("activation_command")
            }
        
        # 回退到runtime_environment
        runtime_env = metadata.get('runtime_environment', {})
        if runtime_env:
            return {
                "type": runtime_env.get("type", "system"),
                "name": runtime_env.get("name"),
                "path": runtime_env.get("python_interpreter"),
                "activation_command": runtime_env.get("activation_command")
            }
        
        return {"type": "system"}
    
    def _create_function_definition(self, script: Any, project_key: str) -> Optional[FunctionDefinition]:
        """从脚本创建功能定义"""
        try:
            function_name = getattr(script, 'function_name', 'unknown')
            script_type = getattr(script, 'script_type', 'python')
            command_template = getattr(script, 'command_template', '')
            script_metadata = getattr(script, 'metadata', {})
            
            # 生成脚本文件名
            script_file = f"{function_name}.py"
            
            # 环境键
            env_key = f"{project_key}_env"
            
            # 提取参数信息
            parameters = script_metadata.get('parameters', [])
            cli_mappings = script_metadata.get('cli_mappings', {})
            
            return FunctionDefinition(
                function_name=function_name,
                script_file=script_file,
                script_type=script_type,
                environment_key=env_key,
                parameters=parameters,
                command_template=command_template,
                cli_mappings=cli_mappings if cli_mappings else {}
            )
            
        except Exception as e:
            function_name = getattr(script, 'function_name', 'unknown')
            logger.error(f"创建功能定义失败: {function_name} - {e}")
            return None
    
    def _save_script_file(self, script: Any, script_file: str):
        """保存脚本文件到scripts目录"""
        try:
            script_path = getattr(script, 'script_path', '')
            if not script_path or not Path(script_path).exists():
                logger.warning(f"源脚本文件不存在: {script_path}")
                return
            
            # 目标路径
            target_path = self.config_manager.get_scripts_dir() / script_file
            
            # 确保目录存在
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            shutil.copy2(script_path, target_path)
            logger.debug(f"脚本文件已保存: {target_path}")
            
        except Exception as e:
            logger.error(f"保存脚本文件失败 {script_file}: {e}")
    
    def _save_project_repository(self, repository: ProjectRepository):
        """保存项目仓库到功能配置文件"""
        try:
            function_config = repository.to_dict()
            success = self.config_manager.save_function_config(repository.project_key, function_config)
            
            if success:
                logger.debug(f"项目仓库保存成功: {repository.project_name}")
            else:
                logger.error(f"项目仓库保存失败: {repository.project_name}")
                
        except Exception as e:
            logger.error(f"保存项目仓库失败: {repository.project_name} - {e}")
    
    def _load_repositories(self):
        """加载所有项目仓库"""
        logger.info(f"开始加载项目仓库")
        
        function_files = self.config_manager.list_function_files()
        loaded_count = 0
        
        for function_file in function_files:
            project_key = function_file.stem.replace('_functions', '')
            if self._load_project_repository(project_key):
                loaded_count += 1
        
        logger.info(f"项目仓库加载完成: {loaded_count}/{len(function_files)} 个项目成功加载")
    
    def _load_project_repository(self, project_key: str) -> bool:
        """加载单个项目仓库"""
        try:
            function_config = self.config_manager.load_function_config(project_key)
            if not function_config:
                return False
            
            repository = ProjectRepository.from_dict(function_config)
            self.repositories[project_key] = repository
            
            logger.info(f"✅ 项目 {repository.project_name} 加载成功，函数数量: {len(repository.functions)}")
            for func_name in repository.functions.keys():
                logger.debug(f"    - {func_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"加载项目仓库失败: {project_key} - {e}")
            return False
    
    def _save_index(self):
        """保存项目索引"""
        try:
            index_data = {
                'projects': [repo.project_name for repo in self.repositories.values()],
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"保存项目索引失败: {e}")
    
    def get_repository_stats(self) -> Dict[str, Any]:
        """获取仓库统计信息"""
        total_projects = len(self.repositories)
        total_functions = sum(len(repo.functions) for repo in self.repositories.values())
        
        return {
            'total_projects': total_projects,
            'total_functions': total_functions,
            'repository_root': str(self.repository_root),
            'projects': list(self.repositories.keys()),
            'machine_config_exists': self.config_manager.machine_config is not None
        }


# 兼容性类 - 为向后兼容提供 RouteFunction
class RouteFunction:
    """兼容性类 - 将函数信息包装为旧的 RouteFunction 格式"""
    
    def __init__(self, function_info: Dict[str, Any]):
        self.function_name = function_info.get("function_name", "")
        self.script_path = function_info.get("script_path", "")
        self.script_type = function_info.get("script_type", "python")
        self.environment = function_info.get("environment", "system:default")
        self.parameters = function_info.get("parameters", [])
        self.command_template = function_info.get("command_template", "")
        self.cli_mappings = function_info.get("cli_mappings", {})  # 支持CLI映射
        self.project_path = function_info.get("project_path", "")
        self.execution_template = function_info.get("execution_template", "")


# 工厂函数
def create_script_repository(repository_root: str = None) -> ScriptRepository:
    """
    创建脚本仓库实例
    
    Args:
        repository_root: 仓库根目录
        
    Returns:
        ScriptRepository: 脚本仓库实例
    """
    return ScriptRepository(repository_root)