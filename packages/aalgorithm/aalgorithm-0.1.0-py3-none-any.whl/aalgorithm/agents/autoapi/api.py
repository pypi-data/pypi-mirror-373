"""
FastAPI 接口层 - 项目API化平台
专注于项目功能API化的RESTful接口
"""

from datetime import datetime
from typing import Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .manager import ProjectAPIManager


# Pydantic 模型定义


class ProjectAPICreateRequest(BaseModel):
    """项目API创建请求模型"""
    usage_md: str = Field(..., description="使用说明MD内容")
    project_path: Optional[str] = Field(None, description="项目绝对路径（可选，系统将智能推断是否需要）")
    project_name: Optional[str] = Field(None, description="项目名称（可选，自动推断）")


class ProjectAPIUpdateRequest(BaseModel):
    """项目API更新请求模型"""
    project_path: Optional[str] = Field(None, description="新的项目路径")
    usage_md: Optional[str] = Field(None, description="新的使用说明MD内容")


class ProjectAPIResponse(BaseModel):
    """项目API响应模型"""
    success: bool
    project_name: str
    message: Optional[str] = None
    analysis_summary: Optional[Dict[str, Any]] = None
    script_generation: Optional[Dict[str, Any]] = None
    test_results: Optional[Dict[str, Any]] = None
    api_routes: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    timestamp: str
    version: str


class ProjectAPIServer:
    """项目API化平台 FastAPI 服务器"""

    def __init__(self, manager: ProjectAPIManager, host: str = "127.0.0.1", port: int = 8080):
        """
        初始化项目API服务器
        
        Args:
            manager: 项目API管理器实例（必需）
            host: 服务主机地址
            port: 服务端口
        """
        self.host = host
        self.port = port
        self.manager = manager
        self.dynamic_router = manager.dynamic_router

        # 创建 FastAPI 应用
        self.app = FastAPI(
            title="Project API Platform",
            description="项目功能API化平台 - 将任何项目转换为可调用的API服务",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )

        # 注册路由
        self._register_routes()

        # 集成动态路由
        self._integrate_dynamic_router()

    def _normalize_project_name(self, input_name: str) -> str:
        """
        标准化项目名称，支持大小写不敏感访问
        
        Args:
            input_name: 用户输入的项目名称（任意大小写）
            
        Returns:
            str: 标准化的项目名称，如果找不到则返回原输入
        """
        if not input_name:
            return input_name

        # 尝试解析真实的项目名称
        resolved_name = self.manager.script_repository._resolve_project_name(input_name)
        return resolved_name if resolved_name else input_name

    def _register_routes(self):
        """注册项目API化路由"""

        @self.app.post("/projects", response_model=ProjectAPIResponse, tags=["项目管理"])
        async def create_project_api(request: ProjectAPICreateRequest):
            """注册新的项目API（支持智能推断是否需要project_path）"""
            result = await self.manager.create_project_api(
                request.usage_md,
                request.project_path,
                request.project_name
            )
            if not result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result.get("error", "项目API创建失败")
                )
            return ProjectAPIResponse(**result)

        @self.app.delete("/projects/{project_name}", tags=["项目管理"])
        async def delete_project_api(project_name: str):
            """删除项目API（支持大小写不敏感）"""
            # 标准化项目名称
            normalized_name = self._normalize_project_name(project_name)
            result = self.manager.delete_project_api(normalized_name)
            if not result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result.get("error", "项目API删除失败")
                )
            return result

        @self.app.get("/projects", tags=["项目管理"])
        async def list_project_apis():
            """列出所有项目API"""
            result = self.manager.list_project_apis()
            if not result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result.get("error", "获取项目列表失败")
                )
            return result

        @self.app.get("/projects/{project_name}", tags=["项目管理"])
        async def get_project_api_info(project_name: str):
            """获取项目API详情（支持大小写不敏感）"""
            # 标准化项目名称
            normalized_name = self._normalize_project_name(project_name)
            result = self.manager.get_project_api_info(normalized_name)
            if not result["success"]:
                # 提供更好的错误信息，包括可用项目列表
                available_projects = self.manager.list_project_apis()
                available_names = [p["project_name"] for p in
                                   available_projects.get("projects", [])] if available_projects.get("success") else []

                error_detail = result.get("error", "项目不存在")
                if available_names:
                    error_detail += f". 可用项目: {', '.join(available_names)}"
                
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_detail
                )
            return result


        @self.app.get("/health", response_model=HealthResponse, tags=["健康检查"])
        async def simple_health_check():
            """简化的健康检查端点（用于客户端检测）"""
            return HealthResponse(
                status="healthy",
                timestamp=datetime.now().isoformat(),
                version="1.0.0"
            )








        # 错误处理器
        @self.app.exception_handler(404)
        async def not_found_handler(request, exc):
            return JSONResponse(
                status_code=404,
                content={"error": "接口不存在"}
            )

        @self.app.exception_handler(500)
        async def internal_error_handler(request, exc):
            return JSONResponse(
                status_code=500,
                content={"error": "内部服务器错误"}
            )

    def _integrate_dynamic_router(self):
        """集成动态路由器"""
        if not self.dynamic_router:
            return

        # 将动态路由器的路由集成到主应用中
        self.app.include_router(
            self.dynamic_router.router,
            prefix="/dynamic",
            tags=["动态功能路由"]
        )

        print(f"✅ 动态路由器已集成")

    def run(self, debug: bool = False, **kwargs):
        """启动 FastAPI 服务器"""
        print(f"启动 AutoAPI 服务管理器...")
        print(f"地址: http://{self.host}:{self.port}")
        print(f"API 文档: http://{self.host}:{self.port}/docs")
        print(f"ReDoc 文档: http://{self.host}:{self.port}/redoc")

        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="debug" if debug else "info",
            **kwargs
        )


def create_project_api_server(manager: ProjectAPIManager, host: str = "127.0.0.1",
                              port: int = 8080) -> ProjectAPIServer:
    """
    创建项目API服务器实例
    
    Args:
        manager: 项目API管理器实例（必需）
        host: API 服务主机地址
        port: API 服务端口
        
    Returns:
        ProjectAPIServer: 项目API服务器实例
    """
    return ProjectAPIServer(manager=manager, host=host, port=port)