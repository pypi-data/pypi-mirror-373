"""
项目API代理 - 项目功能API化的统一入口点
专注于项目分析、脚本生成、API路由管理
"""

import threading
from typing import Dict, Any, List

from .api import create_project_api_server
from .manager import create_project_api_manager


class ProjectAPIAgent:
    """项目API代理 - 项目功能API化的统一入口点"""

    def __init__(self,
                 llm_provider,
                 api_host: str = "127.0.0.1",
                 api_port: int = 8080,
                 repository_root: str = None):
        """
        初始化项目API代理
        
        Args:
            llm_provider: LLM 提供者实例（必传），用于智能分析
            api_host: API 服务主机地址
            api_port: API 服务端口
            repository_root: 脚本仓库根目录
        """
        if llm_provider is None:
            raise ValueError("llm_provider 是必传参数，AutoAPI 需要 LLM 进行智能分析")
        self.api_host = api_host
        self.api_port = api_port
        self.llm_provider = llm_provider

        # 初始化项目API管理器
        self.manager = create_project_api_manager(llm_provider, repository_root)

        # 初始化API服务器
        self.api_server = create_project_api_server(self.manager, api_host, api_port)

        # 运行状态
        self.api_running = False
        self.api_thread = None

    async def register_project_api(self,
                             project_path: str,
                             usage_md: str,
                             project_name: str = None) -> Dict[str, Any]:
        """
        注册项目API（主要方法：分析项目并生成API）
        
        Args:
            project_path: 项目绝对路径
            usage_md: 使用说明MD内容
            project_name: 项目名称（可选，自动推断）
            
        Returns:
            Dict[str, Any]: 注册结果
        """
        try:
            result = await self.manager.create_project_api(project_path, usage_md, project_name)

            if result["success"]:
                # 确保API服务器已启动（如果还没启动的话）
                if not self.api_running:
                    api_start_result = self.start_api_server(background=True)
                    if api_start_result["success"]:
                        result["api_server_started"] = True
                        result["api_url"] = api_start_result["url"]
                        result["docs_url"] = api_start_result["docs_url"]

            return result

        except Exception as e:
            return {"success": False, "error": f"注册项目API失败: {str(e)}"}

    def start_api_server(self, background: bool = True, **kwargs) -> Dict[str, Any]:
        """
        启动 API 服务器
        
        Args:
            background: 是否在后台运行
            **kwargs: 传递给 uvicorn 的参数
            
        Returns:
            Dict[str, Any]: 启动结果
        """
        try:
            if self.api_running:
                return {"success": False, "error": "API 服务器已在运行"}

            if background:
                # 在后台线程中启动
                def run_api():
                    self.api_server.run(**kwargs)

                self.api_thread = threading.Thread(target=run_api, daemon=True)
                self.api_thread.start()

                # 等待一下确保启动
                import time
                time.sleep(2)

                self.api_running = True

                return {
                    "success": True,
                    "message": f"API 服务器已在后台启动",
                    "url": f"http://{self.api_host}:{self.api_port}",
                    "docs_url": f"http://{self.api_host}:{self.api_port}/docs"
                }
            else:
                # 前台运行（阻塞）
                self.api_server.run(**kwargs)
                return {"success": True, "message": "API 服务器已启动"}

        except Exception as e:
            return {"success": False, "error": f"启动 API 服务器失败: {str(e)}"}

    def stop_api_server(self) -> Dict[str, Any]:
        """
        停止 API 服务器
        
        Returns:
            Dict[str, Any]: 停止结果
        """
        try:
            self.api_running = False
            return {
                "success": True,
                "message": "API 服务器已标记停止"
            }
        except Exception as e:
            return {"success": False, "error": f"停止 API 服务器失败: {str(e)}"}

    # 项目API管理方法（代理到manager）
    def list_project_apis(self) -> Dict[str, Any]:
        """列出所有项目API"""
        try:
            return self.manager.list_project_apis()
        except Exception as e:
            return {"success": False, "error": f"列出项目API失败: {str(e)}"}

    def get_project_api_info(self, project_name: str) -> Dict[str, Any]:
        """获取项目API详细信息"""
        try:
            return self.manager.get_project_api_info(project_name)
        except Exception as e:
            return {"success": False, "error": f"获取项目API信息失败: {str(e)}"}


    def delete_project_api(self, project_name: str) -> Dict[str, Any]:
        """删除项目API"""
        try:
            return self.manager.delete_project_api(project_name)
        except Exception as e:
            return {"success": False, "error": f"删除项目API失败: {str(e)}"}

    def get_dynamic_routes(self) -> List[Dict[str, Any]]:
        """获取所有动态路由"""
        try:
            if hasattr(self.manager, 'dynamic_router') and self.manager.dynamic_router:
                return self.manager.dynamic_router.get_registered_routes()
            return []
        except Exception as e:
            return []

    def get_status(self) -> Dict[str, Any]:
        """获取代理状态"""
        try:
            # 获取项目统计
            projects_info = self.manager.list_project_apis()
            routes = self.get_dynamic_routes()

            return {
                "api_server_running": self.api_running,
                "api_url": f"http://{self.api_host}:{self.api_port}" if self.api_running else None,
                "docs_url": f"http://{self.api_host}:{self.api_port}/docs" if self.api_running else None,
                "total_projects": projects_info.get("total_projects", 0) if projects_info["success"] else 0,
                "total_routes": len(routes),
                "repository_stats": projects_info.get("repository_stats") if projects_info["success"] else {}
            }
        except Exception as e:
            return {
                "error": f"获取状态失败: {str(e)}",
                "api_server_running": self.api_running
            }


# 便捷函数
def create_project_api_agent(llm_provider,
                             api_host: str = "127.0.0.1",
                             api_port: int = 8080,
                             repository_root: str = None) -> ProjectAPIAgent:
    """
    创建项目API代理实例
    
    Args:
        llm_provider: LLM 提供者实例（必传），用于智能分析
        api_host: API 服务主机地址
        api_port: API 服务端口
        repository_root: 脚本仓库根目录
        
    Returns:
        ProjectAPIAgent: 项目API代理实例
    """
    return ProjectAPIAgent(
        llm_provider=llm_provider,
        api_host=api_host,
        api_port=api_port,
        repository_root=repository_root
    )


# 简化的工厂函数
def quick_start_project_api(project_path: str,
                            usage_md: str,
                            llm_provider,
                            project_name: str = None,
                            api_port: int = 8080) -> ProjectAPIAgent:
    """
    快速启动项目API代理并注册项目
    
    Args:
        project_path: 项目路径
        usage_md: 使用说明MD内容
        project_name: 项目名称
        api_port: API 端口
        llm_provider: LLM 提供者实例
        
    Returns:
        ProjectAPIAgent: 配置完成的项目API代理
    """
    # 创建代理
    agent = create_project_api_agent(api_port=api_port, llm_provider=llm_provider)

    # 注册项目API
    result = agent.register_project_api(project_path, usage_md, project_name)

    if result["success"]:
        print(f"✅ 项目API注册成功: {result['project_name']}")
        if result.get("api_server_started"):
            print(f"✅ API服务器自动启动")
            print(f"🌐 API 地址: {result['api_url']}")
            print(f"📚 文档地址: {result['docs_url']}")

        # 显示注册的路由
        routes = result.get("api_routes", {})
        if routes.get("success") and routes.get("registered_routes"):
            print(f"🛣️  注册路由:")
            for route in routes["registered_routes"]:
                print(f"   - {route}")
    else:
        print(f"❌ 项目API注册失败: {result['error']}")

    return agent