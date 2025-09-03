"""
配置管理器 - 统一管理机器特定配置和通用配置
支持配置验证、环境变量覆盖、配置热重载等功能
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from loguru import logger


@dataclass
class ProjectConfig:
    """项目配置"""
    project_key: str
    project_path: str
    environment_keys: List[str]


@dataclass
class EnvironmentConfig:
    """环境配置"""
    env_key: str
    env_type: str  # conda, venv, system
    env_name: Optional[str] = None
    env_path: Optional[str] = None
    activation_command: Optional[str] = None


@dataclass
class MachineConfig:
    """机器配置数据结构"""
    projects: Dict[str, ProjectConfig]
    environments: Dict[str, EnvironmentConfig]
    repository_root: str
    scripts_dir: str


class ConfigManager:
    """配置管理器 - 管理机器特定配置和通用功能定义"""
    
    def __init__(self, repository_root: str = None):
        """
        初始化配置管理器
        
        Args:
            repository_root: API仓库根目录
        """
        if repository_root is None:
            repository_root = os.path.join(os.getcwd(), "api_repository")
        
        self.repository_root = Path(repository_root).resolve()
        self.machine_config_path = self.repository_root / "machine_config.json"
        
        # 确保目录结构存在
        self._ensure_directory_structure()
        
        # 加载机器配置
        self.machine_config = self._load_machine_config()
        
        logger.info(f"配置管理器初始化完成: {self.repository_root}")
    
    def _ensure_directory_structure(self):
        """确保目录结构存在"""
        # 创建主要目录
        self.repository_root.mkdir(parents=True, exist_ok=True)
        (self.repository_root / "functions").mkdir(exist_ok=True)
        (self.repository_root / "scripts").mkdir(exist_ok=True)
        
        logger.debug(f"确保目录结构: {self.repository_root}")
    
    def _load_machine_config(self) -> Optional[MachineConfig]:
        """加载机器配置"""
        if not self.machine_config_path.exists():
            logger.warning(f"机器配置文件不存在: {self.machine_config_path}")
            return None
        
        try:
            with open(self.machine_config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 解析项目配置
            projects = {}
            for project_key, project_data in config_data.get('projects', {}).items():
                projects[project_key] = ProjectConfig(
                    project_key=project_key,
                    project_path=project_data.get('project_path', ''),
                    environment_keys=project_data.get('environment_keys', [f"{project_key}_env"])
                )
            
            # 解析环境配置
            environments = {}
            for env_key, env_data in config_data.get('environments', {}).items():
                environments[env_key] = EnvironmentConfig(
                    env_key=env_key,
                    env_type=env_data.get('type', 'system'),
                    env_name=env_data.get('name'),
                    env_path=env_data.get('path'),
                    activation_command=env_data.get('activation_command')
                )
            
            machine_config = MachineConfig(
                projects=projects,
                environments=environments,
                repository_root=str(self.repository_root),
                scripts_dir=config_data.get('scripts_dir', 'scripts')
            )
            
            logger.info(f"机器配置加载成功: {len(projects)} 个项目, {len(environments)} 个环境")
            return machine_config
            
        except Exception as e:
            logger.error(f"加载机器配置失败: {e}")
            return None
    
    def save_machine_config(self, machine_config: MachineConfig) -> bool:
        """保存机器配置"""
        try:
            config_data = {
                "machine_info": {
                    "created_at": "2025-08-18",
                    "description": "API Repository 机器特定配置"
                },
                "projects": {},
                "environments": {},
                "scripts_dir": machine_config.scripts_dir
            }
            
            # 序列化项目配置
            for project_key, project_config in machine_config.projects.items():
                config_data["projects"][project_key] = {
                    "project_path": project_config.project_path,
                    "environment_keys": project_config.environment_keys
                }
            
            # 序列化环境配置
            for env_key, env_config in machine_config.environments.items():
                config_data["environments"][env_key] = {
                    "type": env_config.env_type,
                    "name": env_config.env_name,
                    "path": env_config.env_path,
                    "activation_command": env_config.activation_command
                }
            
            with open(self.machine_config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.machine_config = machine_config
            logger.info(f"机器配置保存成功: {self.machine_config_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存机器配置失败: {e}")
            return False
    
    def get_project_config(self, project_key: str) -> Optional[ProjectConfig]:
        """获取项目配置"""
        if not self.machine_config:
            return None
        return self.machine_config.projects.get(project_key)
    
    def get_environment_config(self, env_key: str) -> Optional[EnvironmentConfig]:
        """获取环境配置"""
        if not self.machine_config:
            return None
        return self.machine_config.environments.get(env_key)
    
    def validate_config(self) -> Dict[str, Any]:
        """验证配置完整性和有效性"""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        if not self.machine_config:
            validation_result["is_valid"] = False
            validation_result["errors"].append("机器配置文件缺失")
            return validation_result
        
        # 验证项目路径存在性
        for project_key, project_config in self.machine_config.projects.items():
            project_path = Path(project_config.project_path)
            if not project_path.exists():
                validation_result["errors"].append(f"项目路径不存在: {project_key} -> {project_path}")
                validation_result["is_valid"] = False
        
        # 验证环境配置
        for env_key, env_config in self.machine_config.environments.items():
            if env_config.env_type == "conda":
                if not env_config.env_name:
                    validation_result["warnings"].append(f"Conda环境 {env_key} 缺少环境名称")
            elif env_config.env_type == "venv":
                if env_config.env_path and not Path(env_config.env_path).exists():
                    validation_result["warnings"].append(f"虚拟环境路径不存在: {env_key} -> {env_config.env_path}")
        
        logger.info(f"配置验证完成: {'有效' if validation_result['is_valid'] else '无效'}")
        return validation_result
    
    def generate_config_template(self, existing_projects: List[str] = None) -> Dict[str, Any]:
        """生成配置模板"""
        if existing_projects is None:
            existing_projects = []
        
        template = {
            "machine_info": {
                "created_at": "2025-08-18",
                "description": "API Repository 机器特定配置 - 请填写实际路径和环境信息"
            },
            "projects": {},
            "environments": {},
            "scripts_dir": "scripts"
        }
        
        # 为现有项目生成模板
        for project_name in existing_projects:
            project_key = project_name.lower()
            template["projects"][project_key] = {
                "project_path": f"/path/to/{project_name}",
                "environment_keys": [f"{project_key}_env"]
            }
            
            template["environments"][f"{project_key}_env"] = {
                "type": "conda",
                "name": f"{project_key}",
                "path": None,
                "activation_command": None
            }
        
        logger.info(f"生成配置模板: {len(existing_projects)} 个项目")
        return template
    
    def get_functions_dir(self) -> Path:
        """获取功能定义目录"""
        return self.repository_root / "functions"
    
    def get_scripts_dir(self) -> Path:
        """获取脚本目录"""
        scripts_dir = "scripts"
        if self.machine_config:
            scripts_dir = self.machine_config.scripts_dir
        return self.repository_root / scripts_dir
    
    def list_function_files(self) -> List[Path]:
        """列出所有功能定义文件"""
        functions_dir = self.get_functions_dir()
        return list(functions_dir.glob("*_functions.json"))
    
    def load_function_config(self, project_name: str) -> Optional[Dict[str, Any]]:
        """加载项目的功能配置"""
        function_file = self.get_functions_dir() / f"{project_name.lower()}_functions.json"
        
        if not function_file.exists():
            logger.warning(f"功能配置文件不存在: {function_file}")
            return None
        
        try:
            with open(function_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载功能配置失败 {project_name}: {e}")
            return None
    
    def save_function_config(self, project_name: str, function_config: Dict[str, Any]) -> bool:
        """保存项目的功能配置"""
        function_file = self.get_functions_dir() / f"{project_name.lower()}_functions.json"
        
        try:
            with open(function_file, 'w', encoding='utf-8') as f:
                json.dump(function_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"功能配置保存成功: {function_file}")
            return True
            
        except Exception as e:
            logger.error(f"保存功能配置失败 {project_name}: {e}")
            return False


def create_config_manager(repository_root: str = None) -> ConfigManager:
    """
    创建配置管理器实例
    
    Args:
        repository_root: API仓库根目录
        
    Returns:
        ConfigManager: 配置管理器实例
    """
    return ConfigManager(repository_root)