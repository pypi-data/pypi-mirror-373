"""
项目API管理器 - AutoAPI Agent
专注于项目功能API化：分析、生成脚本、测试、路由管理
"""

from pathlib import Path
from typing import Dict, Any

from loguru import logger

from .dynamic_router import create_dynamic_router
from .script_analyzer import create_script_analyzer
from .script_generator import create_script_generator
from .script_repository import create_script_repository
from .script_tester import create_script_tester


class ProjectAPIManager:
    """项目API管理器"""

    def __init__(self, llm_provider, repository_root: str = None):
        """
        初始化项目API管理器
        
        Args:
            llm_provider: LLM 提供者实例（必传），用于智能分析
            repository_root: 脚本仓库根目录
        """
        if llm_provider is None:
            raise ValueError("llm_provider 是必传参数，AutoAPI 需要 LLM 进行智能分析")
        self.llm_provider = llm_provider

        # 初始化核心组件
        self.script_analyzer = create_script_analyzer(llm_provider)
        self.script_generator = create_script_generator(llm_provider)
        self.script_tester = create_script_tester(llm_provider=llm_provider)
        self.script_repository = create_script_repository(repository_root)
        self.dynamic_router = create_dynamic_router(self.script_repository)

        logger.info("项目API管理器初始化完成")

    async def create_project_api(self, usage_md: str, project_path: str,
                           project_name: str = None) -> Dict[str, Any]:
        """
        将项目转换为API（智能流程：分析 -> 生成脚本 -> 测试 -> 注册路由）
        
        Args:
            usage_md: 使用说明MD内容
            project_path: 项目绝对路径（必传参数）
            project_name: 项目名称（可选，自动推断）
            
        Returns:
            Dict[str, Any]: API化结果
        """
        try:
            logger.info(f"开始智能项目API化流程，路径: {project_path}")

            # 第一步：智能分析项目功能（包含执行上下文推断）
            logger.info("步骤1: 智能分析项目功能")
            analysis = await self.script_analyzer.analyze_project(usage_md, project_path)
            
            logger.info(f"项目分析完成：项目路径={analysis.project_path}")

            if not analysis.functions:
                return {
                    "success": False,
                    "error": "未分析出任何可用功能",
                    "analysis": analysis
                }

            logger.info(f"分析出 {len(analysis.functions)} 个功能")

            # 第二步：生成脚本
            logger.info("步骤2: 生成执行脚本")
            scripts = await self.script_generator.generate_scripts(
                analysis,
                str(Path(self.script_repository.repository_root) / "temp"),
                usage_md  # 传递完整的usage_md，包含环境信息
            )

            if not scripts:
                return {
                    "success": False,
                    "error": "脚本生成失败",
                    "analysis": analysis
                }

            logger.info(f"生成了 {len(scripts)} 个脚本")

            # 第三步：生成测试用例
            import os
            enable_testing = os.getenv('AUTOAPI_ENABLE_TESTING', 'true').lower() in ('true', '1', 'yes', 'on')
            
            if enable_testing:
                logger.info("步骤3: 生成测试用例")
                for script in scripts:
                    # 为每个脚本生成测试用例
                    test_cases = await self.script_generator.generate_test_cases(
                        script, analysis, usage_md
                    )
                    script.test_cases = test_cases
                    logger.info(f"为脚本 {script.function_name} 生成了 {len(test_cases)} 个测试用例")
            else:
                logger.info("步骤3: 跳过生成测试用例 (AUTOAPI_ENABLE_TESTING=false)")
                for script in scripts:
                    script.test_cases = []

            # 第四步：测试脚本功能
            if enable_testing:
                logger.info("步骤4: 测试脚本功能")
                test_results = await self.script_tester.test_scripts(scripts, parallel=True)
                successful_tests = [r for r in test_results if r.success]
                logger.info(f"测试完成: {len(successful_tests)}/{len(test_results)} 通过")
            else:
                logger.info("步骤4: 跳过测试脚本功能 (AUTOAPI_ENABLE_TESTING=false)")
                test_results = []
                successful_tests = []

            # 第五步：存储到仓库
            logger.info("步骤5: 保存到脚本仓库")
            final_project_name = project_name or analysis.project_name
            # 使用提供的项目路径
            effective_project_path = project_path
            repository = self.script_repository.create_project_repository(
                final_project_name, effective_project_path, scripts
            )

            # 第六步：注册动态路由
            logger.info("步骤6: 注册动态API路由")
            route_result = self.dynamic_router.register_project_routes(final_project_name)
            
            # 验证路由注册是否成功
            if route_result["success"]:
                logger.info(f"路由注册成功: {route_result['total_registered']} 个路由")
            else:
                logger.warning(f"路由注册失败: {route_result.get('error', '未知错误')}")
                
            # 二次验证：检查路由是否真的存在于动态路由器中
            registered_routes = self.dynamic_router.get_registered_routes()
            project_routes = [r for r in registered_routes if r["function"]["name"].startswith(f"{final_project_name}_")]
            logger.info(f"验证结果: 项目 {final_project_name} 实际注册了 {len(project_routes)} 个路由")

            # 汇总结果
            result = {
                "success": True,
                "project_name": final_project_name,
                "project_path": effective_project_path,
                "analysis_summary": {
                    "total_functions": len(analysis.functions),
                },
                "script_generation": {
                    "generated_scripts": len(scripts),
                    "script_paths": [s.script_path for s in scripts]
                },
                "test_results": {
                    "total_tests": len(test_results),
                    "successful_tests": len(successful_tests),
                    "success_rate": len(successful_tests) / len(test_results) if test_results else 0
                },
                "api_routes": route_result,
                "repository_info": {
                    "repository_path": str(self.script_repository.repository_root / f"{final_project_name}_routes.json"),
                    "functions": list(repository.functions.keys())
                }
            }

            logger.info(f"项目API化完成: {final_project_name}")
            return result

        except Exception as e:
            logger.error(f"项目API化失败: {e}")
            return {"success": False, "error": f"项目API化失败: {str(e)}"}


    def delete_project_api(self, project_name: str) -> Dict[str, Any]:
        """
        删除项目API（移除路由、清理脚本）- 支持大小写不敏感
        
        Args:
            project_name: 项目名称（支持大小写不敏感）
            
        Returns:
            Dict[str, Any]: 删除结果
        """
        try:
            # 先获取真实的项目名称
            repository = self.script_repository.get_project_repository(project_name)
            if repository:
                actual_project_name = repository.project_name
            else:
                actual_project_name = project_name  # 如果找不到，使用原输入
            
            # 移除动态路由
            route_result = self.dynamic_router.unregister_project_routes(actual_project_name)

            # 删除脚本仓库
            repo_deleted = self.script_repository.delete_project_repository(project_name)

            return {
                "success": True,
                "project_name": actual_project_name,
                "routes_removed": route_result["total_removed"],
                "repository_deleted": repo_deleted,
                "message": f"项目 {actual_project_name} API已删除"
            }

        except Exception as e:
            logger.error(f"删除项目API失败: {e}")
            return {"success": False, "error": f"删除项目API失败: {str(e)}"}

    def list_project_apis(self) -> Dict[str, Any]:
        """
        列出所有项目API
        
        Returns:
            Dict[str, Any]: 项目API列表
        """
        try:
            projects = self.script_repository.list_projects()
            project_info = []

            for project_name in projects:
                repository = self.script_repository.get_project_repository(project_name)
                if repository:
                    routes = [r for r in self.dynamic_router.get_registered_routes()
                              if r["function"]["name"].startswith(f"{project_name}_")]

                    # 使用 path_resolver 获取项目路径
                    project_key = repository.project_key
                    resolved_paths = self.script_repository.path_resolver.resolve_project_paths(project_key, "")
                    project_path = resolved_paths.project_path if resolved_paths else ""

                    project_info.append({
                        "project_name": project_name,
                        "project_path": project_path,
                        "total_functions": len(repository.functions),
                        "functions": list(repository.functions.keys()),
                        "api_routes": len(routes),
                        "created_at": repository.created_at,
                        "updated_at": repository.updated_at
                    })

            return {
                "success": True,
                "total_projects": len(projects),
                "projects": project_info,
                "repository_stats": self.script_repository.get_repository_stats()
            }

        except Exception as e:
            logger.error(f"列出项目API失败: {e}")
            return {"success": False, "error": f"列出项目API失败: {str(e)}"}

    def get_project_api_info(self, project_name: str) -> Dict[str, Any]:
        """
        获取项目API详细信息（支持大小写不敏感）
        
        Args:
            project_name: 项目名称（支持大小写不敏感）
            
        Returns:
            Dict[str, Any]: 项目API信息
        """
        try:
            repository = self.script_repository.get_project_repository(project_name)
            if not repository:
                return {"success": False, "error": f"项目 {project_name} 不存在"}

            # 使用仓库中的真实项目名称，确保一致性
            actual_project_name = repository.project_name

            # 获取路由信息（使用真实项目名称）
            routes = [r for r in self.dynamic_router.get_registered_routes()
                      if r["function"]["name"].startswith(f"{actual_project_name}_")]

            # 使用 path_resolver 获取项目路径
            project_key = repository.project_key
            resolved_paths = self.script_repository.path_resolver.resolve_project_paths(project_key, "")
            project_path = resolved_paths.project_path if resolved_paths else ""

            # 获取脚本版本信息
            # 简化的函数信息（不再包含版本管理）
            script_functions = {}
            for function_name in repository.functions.keys():
                route_function = repository.functions[function_name]
                # 获取完整的函数信息以获得解析后的环境信息
                function_info = self.script_repository.get_function_info(actual_project_name, function_name)
                if function_info:
                    environment_info = function_info.get("environment", "system:default")
                else:
                    logger.warning(f"无法获取函数信息: {actual_project_name}/{function_name}")
                    environment_info = "system:default"
                
                script_functions[function_name] = {
                    "script_type": route_function.script_type,
                    "environment": environment_info,
                    "parameters_count": len(route_function.parameters)
                }

            return {
                "success": True,
                "project_name": actual_project_name,  # 返回真实的项目名称
                "project_path": project_path,
                "repository_path": str(self.script_repository.repository_root / f"{actual_project_name}_routes.json"),
                "functions": {
                    "total": len(repository.functions),
                    "list": list(repository.functions.keys()),
                    "details": script_functions
                },
                "api_routes": {
                    "total": len(routes),
                    "routes": routes
                },
                "timestamps": {
                    "created_at": repository.created_at,
                    "updated_at": repository.updated_at
                }
            }

        except Exception as e:
            logger.error(f"获取项目API信息失败: {e}")
            return {"success": False, "error": f"获取项目API信息失败: {str(e)}"}



# 便捷函数
def create_project_api_manager(llm_provider, repository_root: str = None) -> ProjectAPIManager:
    """
    创建项目API管理器实例
    
    Args:
        llm_provider: LLM 提供者实例，用于智能分析
        repository_root: 脚本仓库根目录
        
    Returns:
        ProjectAPIManager: 项目API管理器实例
    """
    return ProjectAPIManager(llm_provider, repository_root)
