"""
通用Python环境管理系统
支持多种Python环境管理工具：conda、uv、poetry、venv、pipenv、pyenv、docker等
提供统一的环境检测和命令执行接口
"""

import os
import shlex
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from loguru import logger


@dataclass
class EnvironmentInfo:
    """环境信息数据结构"""
    env_type: str  # conda, uv, poetry, venv, docker, system
    env_name: Optional[str] = None  # 环境名称
    env_path: Optional[str] = None  # 环境路径
    python_path: Optional[str] = None  # Python解释器路径
    activation_command: Optional[str] = None  # 激活命令
    metadata: Optional[Dict[str, Any]] = None  # 额外元数据
    priority: int = 100  # 优先级（数字越小优先级越高）
    is_available: bool = True  # 环境是否可用


class EnvironmentManager(ABC):
    """抽象环境管理器接口"""
    
    @property
    @abstractmethod
    def env_type(self) -> str:
        """环境类型标识"""
        pass
    
    @property
    @abstractmethod
    def priority(self) -> int:
        """环境优先级（数字越小优先级越高）"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查环境管理工具是否可用"""
        pass
    
    @abstractmethod
    def detect_environment(self, project_path: str, metadata: Dict[str, Any]) -> Optional[EnvironmentInfo]:
        """
        检测项目是否使用此环境管理工具
        
        Args:
            project_path: 项目路径
            metadata: 项目元数据
            
        Returns:
            EnvironmentInfo: 环境信息，如果不匹配则返回None
        """
        pass
    
    @abstractmethod
    def build_execution_command(self, env_info: EnvironmentInfo, base_command: str) -> str:
        """
        构建在指定环境中执行的完整命令
        
        Args:
            env_info: 环境信息
            base_command: 基础命令
            
        Returns:
            str: 完整的执行命令
        """
        pass
    
    def validate_environment(self, env_info: EnvironmentInfo) -> bool:
        """验证环境是否有效（可选重写）"""
        return env_info.is_available


class CondaEnvironmentManager(EnvironmentManager):
    """Conda环境管理器"""
    
    @property
    def env_type(self) -> str:
        return "conda"
    
    @property 
    def priority(self) -> int:
        return 10  # 高优先级
    
    def is_available(self) -> bool:
        """检查conda是否安装"""
        try:
            result = subprocess.run(['conda', '--version'], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def detect_environment(self, project_path: str, metadata: Dict[str, Any]) -> Optional[EnvironmentInfo]:
        """检测Conda环境"""
        project_path = Path(project_path).resolve()
        
        # 1. 检查usage_md中的明确指示
        detected_env = metadata.get('detected_environment', {})
        if detected_env.get('type') == 'conda':
            env_name = detected_env.get('name', 'base')
            return EnvironmentInfo(
                env_type='conda',
                env_name=env_name,
                activation_command=f"conda activate {env_name}",
                priority=self.priority,
                is_available=self.is_available(),
                metadata={'source': 'llm_detected', 'detected_env': detected_env}
            )
        
        # 2. 检查项目特征文件
        conda_files = [
            'environment.yml',
            'environment.yaml', 
            'conda.yml',
            'conda.yaml'
        ]
        
        for conda_file in conda_files:
            if (project_path / conda_file).exists():
                # 尝试解析环境名称
                env_name = self._parse_conda_env_name(project_path / conda_file)
                return EnvironmentInfo(
                    env_type='conda',
                    env_name=env_name or 'base',
                    env_path=str(project_path / conda_file),
                    activation_command=f"conda activate {env_name or 'base'}",
                    priority=self.priority,
                    is_available=self.is_available(),
                    metadata={'source': 'conda_file', 'config_file': conda_file}
                )
        
        # 3. 检查conda-meta目录
        if (project_path / 'conda-meta').is_dir():
            return EnvironmentInfo(
                env_type='conda',
                env_name='base',
                activation_command="conda activate base",
                priority=self.priority,
                is_available=self.is_available(),
                metadata={'source': 'conda_meta_dir'}
            )
        
        return None
    
    def build_execution_command(self, env_info: EnvironmentInfo, base_command: str) -> str:
        """构建conda执行命令 - 系统层面添加conda run包装"""
        if not env_info.env_name:
            env_name = 'base'
        else:
            env_name = env_info.env_name
            
        # 系统层面使用conda run命令在指定环境中执行
        # 注意：这不是脚本内容，而是系统调用脚本时的包装
        return f"conda run -n {shlex.quote(env_name)} {base_command}"
    
    def _parse_conda_env_name(self, env_file: Path) -> Optional[str]:
        """从conda环境文件中解析环境名称"""
        try:
            import yaml
            with open(env_file, 'r', encoding='utf-8') as f:
                env_config = yaml.safe_load(f)
                return env_config.get('name')
        except Exception:
            # 简单文本解析作为备用
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip().startswith('name:'):
                            return line.split(':', 1)[1].strip()
            except Exception:
                pass
            return None


class UvEnvironmentManager(EnvironmentManager):
    """UV环境管理器"""
    
    @property
    def env_type(self) -> str:
        return "uv"
    
    @property
    def priority(self) -> int:
        return 15  # 中高优先级
    
    def is_available(self) -> bool:
        """检查uv是否安装"""
        try:
            result = subprocess.run(['uv', '--version'], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def detect_environment(self, project_path: str, metadata: Dict[str, Any]) -> Optional[EnvironmentInfo]:
        """检测UV环境"""
        project_path = Path(project_path).resolve()
        
        # 1. 检查usage_md中的明确指示
        detected_env = metadata.get('detected_environment', {})
        if detected_env.get('type') == 'uv':
            return EnvironmentInfo(
                env_type='uv',
                activation_command="uv run",
                priority=self.priority,
                is_available=self.is_available(),
                metadata={'source': 'llm_detected', 'detected_env': detected_env}
            )
        
        # 2. 检查uv特征文件
        if (project_path / 'uv.lock').exists():
            python_version = self._get_uv_python_version(project_path)
            return EnvironmentInfo(
                env_type='uv',
                python_path=python_version,
                activation_command="uv run",
                priority=self.priority,
                is_available=self.is_available(),
                metadata={'source': 'uv_lock', 'python_version': python_version}
            )
        
        # 3. 检查pyproject.toml中的uv配置
        pyproject_path = project_path / 'pyproject.toml'
        if pyproject_path.exists():
            if self._has_uv_config(pyproject_path):
                python_version = self._get_uv_python_version(project_path)
                return EnvironmentInfo(
                    env_type='uv',
                    python_path=python_version,
                    activation_command="uv run",
                    priority=self.priority,
                    is_available=self.is_available(),
                    metadata={'source': 'pyproject_toml', 'python_version': python_version}
                )
        
        return None
    
    def build_execution_command(self, env_info: EnvironmentInfo, base_command: str) -> str:
        """构建uv执行命令 - 系统层面添加uv run包装"""
        if env_info.python_path:
            return f"uv run --python {env_info.python_path} {base_command}"
        else:
            return f"uv run {base_command}"
    
    def _get_uv_python_version(self, project_path: Path) -> Optional[str]:
        """获取UV项目的Python版本"""
        try:
            # 尝试从.python-version读取
            python_version_file = project_path / '.python-version'
            if python_version_file.exists():
                with open(python_version_file, 'r') as f:
                    return f.read().strip()
            
            # 从pyproject.toml读取
            pyproject_path = project_path / 'pyproject.toml'
            if pyproject_path.exists():
                try:
                    import tomli
                    with open(pyproject_path, 'rb') as f:
                        pyproject_data = tomli.load(f)
                        return pyproject_data.get('project', {}).get('requires-python')
                except ImportError:
                    # 简单文本解析
                    with open(pyproject_path, 'r') as f:
                        for line in f:
                            if 'requires-python' in line:
                                return line.split('=')[1].strip().strip('"\'')
        except Exception:
            pass
        return None
    
    def _has_uv_config(self, pyproject_path: Path) -> bool:
        """检查pyproject.toml是否包含uv配置"""
        try:
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return '[tool.uv' in content or 'uv' in content.lower()
        except Exception:
            return False


class PoetryEnvironmentManager(EnvironmentManager):
    """Poetry环境管理器"""
    
    @property
    def env_type(self) -> str:
        return "poetry"
    
    @property
    def priority(self) -> int:
        return 20
    
    def is_available(self) -> bool:
        """检查poetry是否安装"""
        try:
            result = subprocess.run(['poetry', '--version'], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def detect_environment(self, project_path: str, metadata: Dict[str, Any]) -> Optional[EnvironmentInfo]:
        """检测Poetry环境"""
        project_path = Path(project_path).resolve()
        
        # 1. 检查poetry.lock
        if (project_path / 'poetry.lock').exists():
            return EnvironmentInfo(
                env_type='poetry',
                env_path=str(project_path),
                activation_command="poetry shell",
                priority=self.priority,
                is_available=self.is_available(),
                metadata={'source': 'poetry_lock'}
            )
        
        # 2. 检查pyproject.toml中的poetry配置
        pyproject_path = project_path / 'pyproject.toml'
        if pyproject_path.exists() and self._has_poetry_config(pyproject_path):
            return EnvironmentInfo(
                env_type='poetry',
                env_path=str(project_path),
                activation_command="poetry shell",
                priority=self.priority,
                is_available=self.is_available(),
                metadata={'source': 'pyproject_toml'}
            )
        
        return None
    
    def build_execution_command(self, env_info: EnvironmentInfo, base_command: str) -> str:
        """构建poetry执行命令 - 系统层面添加poetry run包装"""
        return f"poetry run {base_command}"
    
    def _has_poetry_config(self, pyproject_path: Path) -> bool:
        """检查pyproject.toml是否包含poetry配置"""
        try:
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return '[tool.poetry' in content
        except Exception:
            return False


class VenvEnvironmentManager(EnvironmentManager):
    """虚拟环境管理器（venv/virtualenv）"""
    
    @property
    def env_type(self) -> str:
        return "venv"
    
    @property
    def priority(self) -> int:
        return 30
    
    def is_available(self) -> bool:
        """虚拟环境总是可用的"""
        return True
    
    def detect_environment(self, project_path: str, metadata: Dict[str, Any]) -> Optional[EnvironmentInfo]:
        """检测虚拟环境"""
        project_path = Path(project_path).resolve()
        
        # 1. 检查usage_md中的明确指示
        detected_env = metadata.get('detected_environment', {})
        if detected_env.get('type') == 'venv':
            venv_path = detected_env.get('name', '.venv')
            return EnvironmentInfo(
                env_type='venv',
                env_path=venv_path,
                activation_command=f"source {venv_path}/bin/activate",
                priority=self.priority,
                is_available=self.is_available(),
                metadata={'source': 'llm_detected', 'detected_env': detected_env}
            )
        
        # 2. 检查常见的虚拟环境目录
        venv_dirs = ['.venv', 'venv', '.env', 'env']
        
        for venv_dir in venv_dirs:
            venv_path = project_path / venv_dir
            if venv_path.is_dir():
                # 检查是否确实是虚拟环境
                if self._is_virtual_env(venv_path):
                    activation_script = self._get_activation_script(venv_path)
                    return EnvironmentInfo(
                        env_type='venv',
                        env_path=str(venv_path),
                        activation_command=f"source {activation_script}",
                        priority=self.priority,
                        is_available=self.is_available(),
                        metadata={'source': 'venv_directory', 'venv_dir': venv_dir}
                    )
        
        return None
    
    def build_execution_command(self, env_info: EnvironmentInfo, base_command: str) -> str:
        """构建虚拟环境执行命令 - 系统层面添加activation包装"""
        if env_info.activation_command:
            return f"{env_info.activation_command} && {base_command}"
        else:
            # 回退到直接执行
            return base_command
    
    def _is_virtual_env(self, venv_path: Path) -> bool:
        """检查目录是否是虚拟环境"""
        # 检查关键文件
        indicators = [
            'pyvenv.cfg',  # Python 3.3+ venv
            'bin/activate',  # Unix系统
            'Scripts/activate.bat',  # Windows系统
            'lib/python*/site-packages'  # Python包目录
        ]
        
        for indicator in indicators:
            if indicator.endswith('*'):
                # 使用glob模式匹配
                import glob
                if glob.glob(str(venv_path / indicator)):
                    return True
            else:
                if (venv_path / indicator).exists():
                    return True
        
        return False
    
    def _get_activation_script(self, venv_path: Path) -> str:
        """获取激活脚本路径"""
        # Unix系统
        unix_activate = venv_path / 'bin' / 'activate'
        if unix_activate.exists():
            return str(unix_activate)
        
        # Windows系统
        windows_activate = venv_path / 'Scripts' / 'activate.bat'
        if windows_activate.exists():
            return str(windows_activate)
        
        # 默认返回Unix路径
        return str(venv_path / 'bin' / 'activate')


class SystemEnvironmentManager(EnvironmentManager):
    """系统Python环境管理器（fallback）"""
    
    @property
    def env_type(self) -> str:
        return "system"
    
    @property
    def priority(self) -> int:
        return 100  # 最低优先级
    
    def is_available(self) -> bool:
        """系统Python总是可用的"""
        return True
    
    def detect_environment(self, project_path: str, metadata: Dict[str, Any]) -> Optional[EnvironmentInfo]:
        """系统环境总是可用作为fallback"""
        return EnvironmentInfo(
            env_type='system',
            python_path='python',
            activation_command=None,
            priority=self.priority,
            is_available=self.is_available(),
            metadata={'source': 'system_fallback'}
        )
    
    def build_execution_command(self, env_info: EnvironmentInfo, base_command: str) -> str:
        """直接执行命令"""
        return base_command


class EnvironmentRegistry:
    """环境管理器注册表"""
    
    def __init__(self, config_manager=None):
        """
        初始化所有环境管理器
        
        Args:
            config_manager: 配置管理器实例（可选），用于支持新架构
        """
        self.config_manager = config_manager
        
        self.managers = [
            CondaEnvironmentManager(),
            UvEnvironmentManager(),
            PoetryEnvironmentManager(),
            VenvEnvironmentManager(),
            SystemEnvironmentManager()  # 必须最后，作为fallback
        ]
        
        # 按优先级排序
        self.managers.sort(key=lambda m: m.priority)
        
        logger.info(f"环境管理器注册完成，共 {len(self.managers)} 个管理器")
    
    def detect_best_environment(self, project_path: str, metadata: Dict[str, Any]) -> EnvironmentInfo:
        """
        检测项目的最佳环境
        
        Args:
            project_path: 项目路径
            metadata: 项目元数据
            
        Returns:
            EnvironmentInfo: 最佳环境信息
        """
        logger.debug(f"开始检测项目环境: {project_path}")
        
        for manager in self.managers:
            try:
                if not manager.is_available():
                    logger.debug(f"{manager.env_type} 管理器不可用，跳过")
                    continue
                
                env_info = manager.detect_environment(project_path, metadata)
                if env_info and manager.validate_environment(env_info):
                    logger.info(f"检测到最佳环境: {env_info.env_type} (优先级: {manager.priority})")
                    logger.debug(f"环境详情: {env_info}")
                    return env_info
                    
            except Exception as e:
                logger.error(f"{manager.env_type} 环境检测失败: {e}")
                continue
        
        # 这种情况不应该发生，因为SystemEnvironmentManager总是返回有效结果
        logger.error("所有环境检测都失败了，这不应该发生")
        return EnvironmentInfo(
            env_type='system',
            python_path='python',
            priority=100,
            is_available=True,
            metadata={'source': 'emergency_fallback'}
        )
    
    def create_environment_from_analysis(self, runtime_env: Dict[str, Any]) -> EnvironmentInfo:
        """
        基于项目分析结果创建环境信息
        
        Args:
            runtime_env: 项目分析中的runtime_environment字段
            
        Returns:
            EnvironmentInfo: 环境信息对象
        """


        # 从规范化后的环境中获取字段值
        env_type = runtime_env.get('type', 'system')
        confidence = runtime_env.get('confidence', 'medium')
        env_name = runtime_env.get('name')
        python_interpreter = runtime_env.get('python_interpreter')
        activation_command = runtime_env.get('activation_command')
        
        # 根据置信度设置优先级
        priority_map = {'high': 10, 'medium': 30, 'low': 60}
        priority = priority_map.get(confidence, 50)
        
        return EnvironmentInfo(
            env_type=env_type,
            env_name=env_name,
            env_path=python_interpreter,  # 注意：这里使用python_interpreter作为env_path
            activation_command=activation_command,
            metadata={
                'source': 'pre_analyzed', 
                'analysis': runtime_env,
                'original_confidence': confidence
            },
            priority=priority,
            is_available=True
        )
    
    def create_environment_from_config(self, env_key: str) -> Optional[EnvironmentInfo]:
        """
        基于配置管理器创建环境信息 - 新架构支持
        
        Args:
            env_key: 环境配置键
            
        Returns:
            EnvironmentInfo: 环境信息对象
        """
        if not self.config_manager:
            logger.warning("配置管理器未设置，无法从配置创建环境")
            return None
        
        env_config = self.config_manager.get_environment_config(env_key)
        if not env_config:
            logger.error(f"环境配置不存在: {env_key}")
            return None
        
        # 根据环境类型设置优先级
        priority_map = {
            'conda': 10,
            'uv': 15,
            'poetry': 20,
            'venv': 30,
            'system': 100
        }
        priority = priority_map.get(env_config.env_type, 50)
        
        return EnvironmentInfo(
            env_type=env_config.env_type,
            env_name=env_config.env_name,
            env_path=env_config.env_path,
            activation_command=env_config.activation_command,
            metadata={'source': 'machine_config', 'env_key': env_key},
            priority=priority,
            is_available=True
        )

    def get_execution_command(self, env_info: EnvironmentInfo, base_command: str) -> str:
        """
        获取在指定环境中执行的命令
        
        Args:
            env_info: 环境信息
            base_command: 基础命令
            
        Returns:
            str: 完整的执行命令
        """
        # 找到对应的管理器
        for manager in self.managers:
            if manager.env_type == env_info.env_type:
                try:
                    command = manager.build_execution_command(env_info, base_command)
                    logger.debug(f"构建执行命令: {env_info.env_type} -> {command}")
                    return command
                except Exception as e:
                    logger.error(f"构建 {env_info.env_type} 执行命令失败: {e}")
                    break
        
        # 回退到直接执行
        logger.warning(f"无法为环境 {env_info.env_type} 构建命令，使用直接执行")
        return base_command
    
    def list_available_managers(self) -> List[Tuple[str, bool]]:
        """列出所有管理器及其可用性状态"""
        return [(manager.env_type, manager.is_available()) for manager in self.managers]


# 工厂函数
def create_environment_registry(config_manager=None) -> EnvironmentRegistry:
    """
    创建环境管理器注册表实例
    
    Args:
        config_manager: 配置管理器实例（可选），用于支持新架构
        
    Returns:
        EnvironmentRegistry: 环境管理器注册表实例
    """
    return EnvironmentRegistry(config_manager)