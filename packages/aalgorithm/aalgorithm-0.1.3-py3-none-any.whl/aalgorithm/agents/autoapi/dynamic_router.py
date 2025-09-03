"""
动态路由器 - 热部署路由管理器
支持运行时动态添加、移除和更新API路由，无需重启服务
"""

import asyncio
import json
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from pydantic import BaseModel, Field

from .environment_manager import create_environment_registry
from .script_repository import ScriptRepository, ProjectRepository, RouteFunction




@dataclass
class RouteInfo:
    """路由信息"""
    project_name: str
    function_name: str
    route_path: str
    route_function: RouteFunction
    created_at: str
    parameters: Dict[str, Any] = None
    last_used: Optional[str] = None
    usage_count: int = 0


class DynamicFunctionRequest(BaseModel):
    """标准化功能调用请求模型"""
    input: str = Field(..., description="输入内容（文本内容或文件路径）")
    output_path: str = Field(..., description="输出文件路径")
    timeout: int = Field(30, description="超时时间（秒）", ge=1, le=300)
    async_execution: bool = Field(False, description="是否异步执行")


class DynamicFunctionResponse(BaseModel):
    """动态功能调用响应模型"""
    success: bool
    output: Optional[str] = None  # 功能脚本的原始stdout输出，保持原始格式
    stderr: Optional[str] = None  # 功能脚本的stderr输出
    error: Optional[str] = None   # 执行错误信息（通常为stderr内容）
    execution_time: float
    exit_code: Optional[int] = None
    async_task_id: Optional[str] = None


class AsyncTaskStatus(BaseModel):
    """异步任务状态"""
    task_id: str
    status: str  # pending, running, completed, failed
    result: Optional[DynamicFunctionResponse] = None
    created_at: str
    completed_at: Optional[str] = None


class DynamicAPIRouter:
    """动态API路由器"""

    def __init__(self, script_repository: ScriptRepository):
        """
        初始化动态路由器
        
        Args:
            script_repository: 脚本仓库实例
        """
        self.script_repository = script_repository
        self.router = APIRouter()
        self.routes: Dict[str, RouteInfo] = {}  # route_path -> RouteInfo
        self.async_tasks: Dict[str, AsyncTaskStatus] = {}  # task_id -> status
        
        # 初始化环境管理器
        self.environment_registry = create_environment_registry()

        # 注册基础路由
        self._register_base_routes()
        
        # 自动注册所有已存在的项目路由
        self._auto_register_existing_routes()

        logger.info("动态API路由器初始化完成")

    def register_project_routes(self, project_name: str) -> Dict[str, Any]:
        """
        为项目注册所有功能路由
        
        Args:
            project_name: 项目名称
            
        Returns:
            Dict[str, Any]: 注册结果
        """
        logger.info(f"为项目 {project_name} 注册路由")

        repository = self.script_repository.get_project_repository(project_name)
        if not repository:
            logger.error(f"项目仓库不存在: {project_name}")
            return {
                "success": False,
                "error": f"项目 {project_name} 不存在"
            }

        registered_routes = []
        failed_routes = []

        # 先移除该项目的旧路由（如果存在）
        old_routes_to_remove = []
        for route_path, route_info in self.routes.items():
            if route_info.project_name == project_name:
                old_routes_to_remove.append(route_path)
        
        for route_path in old_routes_to_remove:
            del self.routes[route_path]
            logger.info(f"移除旧路由: {route_path}")

        # 注册新路由
        for function_name in repository.functions.keys():
            try:
                route_path = f"/{project_name}/{function_name}"
                route_info = self._create_route_info(project_name, function_name, repository)

                if route_info:
                    self._register_function_route(route_path, route_info)
                    registered_routes.append(route_path)
                    logger.info(f"注册路由: {route_path}")
                else:
                    failed_routes.append(f"{function_name}: 无法创建路由信息")

            except Exception as e:
                failed_routes.append(f"{function_name}: {str(e)}")
                logger.error(f"注册路由失败: {project_name}/{function_name} - {e}")

        # 验证路由注册状态
        final_routes_count = len([r for r in self.routes.values() if r.project_name == project_name])
        logger.info(f"项目 {project_name} 路由注册完成: {final_routes_count} 个路由，总路由数: {len(self.routes)}")

        # 强制刷新路由缓存（如果有的话）
        self._refresh_routes_cache()

        return {
            "success": len(registered_routes) > 0,
            "registered_routes": registered_routes,
            "failed_routes": failed_routes,
            "total_registered": len(registered_routes),
            "final_routes_count": final_routes_count
        }

    def unregister_project_routes(self, project_name: str) -> Dict[str, Any]:
        """
        移除项目的所有路由
        
        Args:
            project_name: 项目名称
            
        Returns:
            Dict[str, Any]: 移除结果
        """
        logger.info(f"移除项目 {project_name} 的路由")

        removed_routes = []
        route_paths_to_remove = []

        # 找到需要移除的路由
        for route_path, route_info in self.routes.items():
            if route_info.project_name == project_name:
                route_paths_to_remove.append(route_path)

        # 移除路由
        for route_path in route_paths_to_remove:
            del self.routes[route_path]
            removed_routes.append(route_path)

        # 注意：FastAPI的路由器不支持运行时删除路由
        # 这里只是从我们的跟踪字典中移除，实际的路由处理会返回404

        return {
            "success": True,
            "removed_routes": removed_routes,
            "total_removed": len(removed_routes)
        }

    def update_function_route(self, project_name: str, function_name: str) -> Dict[str, Any]:
        """
        更新单个功能路由
        
        Args:
            project_name: 项目名称
            function_name: 功能名称
            
        Returns:
            Dict[str, Any]: 更新结果
        """
        route_path = f"/{project_name}/{function_name}"

        repository = self.script_repository.get_project_repository(project_name)
        if not repository:
            return {
                "success": False,
                "error": f"项目 {project_name} 不存在"
            }

        try:
            route_info = self._create_route_info(project_name, function_name, repository)
            if route_info:
                self._register_function_route(route_path, route_info)
                logger.info(f"更新路由: {route_path}")
                return {
                    "success": True,
                    "route_path": route_path,
                    "updated_at": route_info.created_at
                }
            else:
                return {
                    "success": False,
                    "error": "无法创建路由信息"
                }

        except Exception as e:
            logger.error(f"更新路由失败: {route_path} - {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_registered_routes(self) -> List[Dict[str, Any]]:
        """获取所有已注册的路由 - 标准化格式"""
        routes = []
        
        for route_path, route_info in self.routes.items():
            # 标准化的参数格式 - 所有API都使用相同的输入输出格式
            properties = {
                "input": {
                    "type": "string",
                    "description": "输入内容（文本内容或文件路径）"
                },
                "output_path": {
                    "type": "string",
                    "description": "输出文件路径"
                }
            }
            required_params = ["input", "output_path"]
            
            # 生成函数描述
            function_description = self._generate_function_description(route_info)
            
            # 构建OpenAI Function Calling格式
            function_schema = {
                "type": "function",
                "function": {
                    "name": f"{route_info.project_name}_{route_info.function_name}",
                    "description": function_description,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required_params
                    },
                    "route_info": {
                        "route_path": route_path,
                        "method": "POST",
                        "project_name": route_info.project_name,
                        "function_name": route_info.function_name,
                        "endpoint_url": f"POST /dynamic{route_path}"
                    }
                }
            }
            
            routes.append(function_schema)
        
        return routes

    def get_route_info(self, route_path: str) -> Optional[Dict[str, Any]]:
        """获取特定路由的信息"""
        route_info = self.routes.get(route_path)
        if not route_info:
            return None

        return {
            "route_path": route_path,
            "project_name": route_info.project_name,
            "function_name": route_info.function_name,
            "script_path": route_info.route_function.script_path,
            "script_type": route_info.route_function.script_type,
            "parameters": route_info.route_function.parameters,
            "created_at": route_info.created_at,
            "usage_count": route_info.usage_count,
            "last_used": route_info.last_used
        }

    def _create_route_info(self, project_name: str, function_name: str,
                           repository: ProjectRepository) -> Optional[RouteInfo]:
        """创建路由信息"""
        route_function = self.script_repository.get_route_function(project_name, function_name)
        if not route_function:
            return None

        route_path = f"/{project_name}/{function_name}"

        return RouteInfo(
            project_name=project_name,
            function_name=function_name,
            route_path=route_path,
            route_function=route_function,
            parameters={},  # 简化：不再需要复杂参数信息
            created_at=__import__('datetime').datetime.now().isoformat()
        )

    def _register_function_route(self, route_path: str, route_info: RouteInfo):
        """注册单个功能路由"""
        # 更新路由跟踪
        self.routes[route_path] = route_info

        # 动态路由处理在_register_base_routes中的catch-all处理器中实现

    def _register_base_routes(self):
        """注册基础路由"""

        @self.router.get("/routes", response_model=List[Dict[str, Any]])
        async def list_routes():
            """列出所有已注册的路由"""
            # 强制刷新路由缓存以确保返回最新状态
            self._refresh_routes_cache()
            
            routes = self.get_registered_routes()
            logger.debug(f"返回路由列表: {len(routes)} 个路由")
            
            return routes

        @self.router.get("/routes/{project_name}")
        async def list_project_routes(project_name: str):
            """列出项目的路由（支持大小写不敏感）"""
            # 强制刷新路由缓存以确保返回最新状态
            self._refresh_routes_cache()

            # 解析真实项目名称
            resolved_project_name = self.script_repository._resolve_project_name(project_name)
            search_project_name = resolved_project_name if resolved_project_name else project_name
            
            project_routes = [
                route for route in self.get_registered_routes()
                if route["function"]["name"].startswith(f"{search_project_name}_")
            ]

            logger.debug(f"返回项目 {search_project_name} 的路由: {len(project_routes)} 个路由")
            
            return {
                "project_name": search_project_name, 
                "routes": project_routes,
                "total_routes": len(project_routes)
            }

        @self.router.post("/routes/{project_name}/refresh")
        async def refresh_project_routes(project_name: str):
            """强制刷新项目路由（用于解决同步问题）"""
            result = self.force_refresh_project_routes(project_name)
            if result["success"]:
                return {
                    "success": True,
                    "message": f"项目 {project_name} 的路由已刷新",
                    "total_registered": result["total_registered"],
                    "final_routes_count": result.get("final_routes_count", 0)
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail=result.get("error", "路由刷新失败")
                )

        @self.router.get("/async-tasks/{task_id}")
        async def get_async_task_status(task_id: str):
            """获取异步任务状态"""
            task_status = self.async_tasks.get(task_id)
            if not task_status:
                raise HTTPException(status_code=404, detail="任务不存在")
            return task_status

        # Catch-all路由处理动态功能调用 - 只支持POST方法
        @self.router.post("/{project_name}/{function_name}",
                          response_model=DynamicFunctionResponse)
        async def dynamic_function_handler(
                project_name: str,
                function_name: str,
                request: Request
        ):
            """动态功能调用处理器（POST方法）- 支持大小写不敏感"""
            # 首先尝试精确匹配（向后兼容）
            route_path = f"/{project_name}/{function_name}"
            route_info = self.routes.get(route_path)

            # 如果精确匹配失败，尝试大小写不敏感匹配
            if not route_info:
                resolved_project_name = self.script_repository._resolve_project_name(project_name)
                if resolved_project_name:
                    # 使用解析出的真实项目名称重新构建路径
                    normalized_route_path = f"/{resolved_project_name}/{function_name}"
                    route_info = self.routes.get(normalized_route_path)
                    if route_info:
                        route_path = normalized_route_path  # 更新路径用于日志记录

            # 如果仍然没有找到路由
            if not route_info:
                # 收集可用的路由用于错误提示
                available_routes = list(self.routes.keys())
                case_similar_routes = [r for r in available_routes if r.lower() == route_path.lower()]

                error_detail = f"功能路由不存在: {route_path}"
                if case_similar_routes:
                    error_detail += f". 是否您想访问: {', '.join(case_similar_routes)}"
                
                raise HTTPException(
                    status_code=404,
                    detail=error_detail
                )

            # 解析JSON请求参数
            try:
                body = await request.body()
                if body:
                    json_params = json.loads(body)
                else:
                    json_params = {}
                
                # 验证标准化参数
                validation_result = self._validate_standardized_request(json_params)
                if not validation_result["success"]:
                    raise HTTPException(
                        status_code=400,
                        detail=validation_result["error"]
                    )
                
                # 创建标准化执行请求
                func_request = DynamicFunctionRequest(
                    input=json_params['input'],
                    output_path=json_params['output_path'],
                    timeout=json_params.get('timeout', 30),
                    async_execution=json_params.get('async_execution', False)
                )
                
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"JSON格式错误: {str(e)}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"请求参数处理失败: {str(e)}"
                )

            # 更新使用统计
            route_info.usage_count += 1
            route_info.last_used = __import__('datetime').datetime.now().isoformat()

            # 执行功能
            if func_request.async_execution:
                return await self._execute_async_function(route_info, func_request)
            else:
                return await self._execute_sync_function(route_info, func_request)

    async def _execute_sync_function(self, route_info: RouteInfo,
                                     func_request: DynamicFunctionRequest) -> DynamicFunctionResponse:
        """同步执行功能"""
        start_time = __import__('time').time()

        try:
            # 构建执行命令
            command = self._build_execution_command(route_info, func_request)

            logger.info(f"执行命令: {command}")

            # 执行脚本
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Path(route_info.route_function.script_path).parent
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=func_request.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.communicate()
                return DynamicFunctionResponse(
                    success=False,
                    error=f"执行超时 ({func_request.timeout}秒)",
                    stderr=None,
                    execution_time=__import__('time').time() - start_time
                )

            execution_time = __import__('time').time() - start_time

            # 处理输出
            stdout_str = stdout.decode('utf-8', errors='ignore') if stdout else ""
            stderr_str = stderr.decode('utf-8', errors='ignore') if stderr else ""

            success = process.returncode == 0

            # 保持原始输出结构，不进行智能合并
            return DynamicFunctionResponse(
                success=success,
                output=stdout_str,  # output字段专门用于功能脚本的stdout输出
                stderr=stderr_str,
                error=stderr_str if not success else None,
                execution_time=execution_time,
                exit_code=process.returncode
            )

        except Exception as e:
            execution_time = __import__('time').time() - start_time
            logger.error(f"执行功能失败: {route_info.route_path} - {e}")

            return DynamicFunctionResponse(
                success=False,
                error=f"执行异常: {str(e)}",
                stderr=None,
                execution_time=execution_time
            )

    async def _execute_async_function(self, route_info: RouteInfo,
                                      func_request: DynamicFunctionRequest) -> DynamicFunctionResponse:
        """异步执行功能"""
        import uuid

        task_id = str(uuid.uuid4())

        # 创建异步任务状态
        task_status = AsyncTaskStatus(
            task_id=task_id,
            status="pending",
            created_at=__import__('datetime').datetime.now().isoformat()
        )

        self.async_tasks[task_id] = task_status

        # 创建异步任务
        async def execute_task():
            try:
                task_status.status = "running"

                # 执行同步功能
                result = await self._execute_sync_function(route_info, func_request)

                # 更新任务状态
                task_status.status = "completed" if result.success else "failed"
                task_status.result = result
                task_status.completed_at = __import__('datetime').datetime.now().isoformat()

            except Exception as e:
                task_status.status = "failed"
                task_status.result = DynamicFunctionResponse(
                    success=False,
                    error=f"异步执行异常: {str(e)}",
                    stderr=None,
                    execution_time=0.0
                )
                task_status.completed_at = __import__('datetime').datetime.now().isoformat()

        # 启动后台任务
        asyncio.create_task(execute_task())

        return DynamicFunctionResponse(
            success=True,
            output=f"异步任务已启动，任务ID: {task_id}",
            stderr=None,
            execution_time=0.0,
            async_task_id=task_id
        )

    def _ensure_absolute_script_path(self, script_path: str) -> str:
        """确保脚本路径为绝对路径且文件存在"""
        path = Path(script_path)
        if not path.is_absolute():
            path = Path.cwd() / script_path
        
        if not path.exists():
            raise FileNotFoundError(f"脚本文件不存在: {path}")
        
        return str(path.resolve())

    def _build_execution_command(self, route_info: RouteInfo,
                                 request: DynamicFunctionRequest) -> str:
        """构建脚本执行命令 - 使用环境管理器根据项目环境选择正确的执行方式"""
        # 确保脚本路径是绝对路径且文件存在
        script_path = self._ensure_absolute_script_path(route_info.route_function.script_path)
        script_type = route_info.route_function.script_type
        
        # 检测脚本文件扩展名
        script_extension = Path(script_path).suffix.lower()
        
        logger.debug(f"构建执行命令 - 脚本路径: {script_path}, 类型: {script_type}, 扩展名: {script_extension}")
        
        # 使用精简的环境信息
        environment_str = route_info.route_function.environment
        
        # 解析环境字符串并创建env_info对象
        env_info = self._create_env_info_from_string(environment_str)
        
        logger.info(f"使用执行环境: {environment_str} (项目: {route_info.project_name})")
        
        # 根据脚本类型构建基础执行命令
        if script_type == 'shell' or script_extension == '.sh':
            # Shell脚本：直接执行脚本文件
            base_command = f"bash {shlex.quote(script_path)}"
            
        elif script_type == 'python' or script_extension == '.py':
            # Python脚本：使用python执行
            base_command = f"python {shlex.quote(script_path)}"
            
        else:
            # 其他类型：尝试直接执行
            base_command = shlex.quote(script_path)
        
        # 添加标准化参数
        standardized_params = self._build_standardized_params(request)
        if standardized_params:
            base_command += " " + standardized_params
            logger.debug(f"添加标准化参数: {standardized_params}")
        else:
            logger.warning("没有标准化参数，脚本可能显示使用说明")
        
        # 使用环境管理器构建最终执行命令（包含环境激活）
        final_command = self.environment_registry.get_execution_command(env_info, base_command)
        
        logger.debug(f"基础命令: {base_command}")
        logger.debug(f"最终执行命令: {final_command}")
        return final_command
    
    def _create_env_info_from_string(self, environment_str: str):
        """从环境字符串创建 env_info 对象"""
        if environment_str.startswith('conda:'):
            env_name = environment_str.split(':', 1)[1]
            return self.environment_registry.create_environment_from_analysis({
                'type': 'conda',
                'name': env_name,
                'activation_command': f'conda activate {env_name}'
            })
        elif environment_str.startswith('venv:'):
            env_path = environment_str.split(':', 1)[1]
            return self.environment_registry.create_environment_from_analysis({
                'type': 'venv',
                'path': env_path,
                'activation_command': f'source {env_path}/bin/activate'
            })
        else:
            # 默认使用 python
            return self.environment_registry.create_environment_from_analysis({
                'type': 'python',
                'name': '',
                'activation_command': ''
            })

    def _build_standardized_params(self, request: DynamicFunctionRequest) -> str:
        """构建标准化参数字符串"""
        params = []
        
        # 输入参数作为位置参数
        params.append(shlex.quote(request.input))
        
        # 输出参数使用 -o 选项
        params.append(f"-o {shlex.quote(request.output_path)}")
        
        return " ".join(params)
    
    def _validate_standardized_request(self, json_params: Dict[str, Any]) -> Dict[str, Any]:
        """验证标准化请求参数"""
        errors = []
        
        # 检查必填的 input
        if not json_params.get('input'):
            errors.append("缺少必填参数: input")
        
        # 检查必填的 output_path
        if not json_params.get('output_path'):
            errors.append("缺少必填参数: output_path")
        
        if errors:
            return {
                "success": False,
                "error": "; ".join(errors)
            }
        
        return {"success": True}
    

    def cleanup_async_tasks(self, max_age_hours: int = 24):
        """清理过期的异步任务"""
        from datetime import datetime, timedelta

        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        expired_tasks = []
        for task_id, task_status in self.async_tasks.items():
            try:
                created_time = datetime.fromisoformat(task_status.created_at)
                if created_time < cutoff_time:
                    expired_tasks.append(task_id)
            except:
                expired_tasks.append(task_id)  # 无效时间戳也删除

        for task_id in expired_tasks:
            del self.async_tasks[task_id]

        if expired_tasks:
            logger.info(f"清理了 {len(expired_tasks)} 个过期异步任务")

    def _refresh_routes_cache(self):
        """刷新路由缓存（为了确保路由状态同步）"""
        # 这是一个占位方法，用于在需要时强制刷新路由状态
        # 当前实现中，self.routes 已经是实时状态，所以这里主要是日志记录
        logger.debug(f"路由缓存刷新完成，当前总路由数: {len(self.routes)}")
        
        # 可以在这里添加额外的同步逻辑，比如验证路由完整性
        for route_path, route_info in self.routes.items():
            if not route_info.project_name or not route_info.function_name:
                logger.warning(f"发现异常路由: {route_path}")
    
    def force_refresh_project_routes(self, project_name: str) -> Dict[str, Any]:
        """强制刷新项目路由（用于解决同步问题）"""
        logger.info(f"强制刷新项目 {project_name} 的路由")
        return self.register_project_routes(project_name)
    

    def _generate_function_description(self, route_info: RouteInfo) -> str:
        """生成函数描述"""
        script_type = route_info.route_function.script_type
        description = f"Execute {route_info.function_name} function from {route_info.project_name} project ({script_type} script)"
        return description
    

    def _auto_register_existing_routes(self):
        """自动注册所有已存在的项目路由"""
        logger.info("开始自动注册已存在的项目路由")
        
        try:
            existing_projects = self.script_repository.list_projects()
            logger.info(f"发现 {len(existing_projects)} 个已存在的项目")
            
            total_registered = 0
            successful_projects = 0
            
            for project_name in existing_projects:
                try:
                    logger.info(f"自动注册项目路由: {project_name}")
                    result = self.register_project_routes(project_name)
                    
                    if result["success"]:
                        registered_count = result.get("total_registered", 0)
                        total_registered += registered_count
                        successful_projects += 1
                        logger.info(f"  ✅ 项目 {project_name} 注册成功: {registered_count} 个路由")
                    else:
                        logger.warning(f"  ❌ 项目 {project_name} 注册失败: {result.get('error', '未知错误')}")
                        
                except Exception as e:
                    logger.error(f"自动注册项目 {project_name} 路由时发生异常: {e}")
                    import traceback
                    logger.debug(f"详细错误信息: {traceback.format_exc()}")
            
            logger.info(f"自动注册完成: {successful_projects}/{len(existing_projects)} 个项目成功，共注册 {total_registered} 个路由")
            
        except Exception as e:
            logger.error(f"自动注册已存在的项目路由失败: {e}")
            import traceback
            logger.debug(f"详细错误信息: {traceback.format_exc()}")


# 工厂函数
def create_dynamic_router(script_repository: ScriptRepository) -> DynamicAPIRouter:
    """
    创建动态API路由器实例
    
    Args:
        script_repository: 脚本仓库实例
        
    Returns:
        DynamicAPIRouter: 动态路由器实例
    """
    return DynamicAPIRouter(script_repository)
