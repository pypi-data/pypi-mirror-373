"""
Entry points for deployment processes.

This module provides different entry points for starting deployment processes,
including Git repository deployment and direct instruction-based deployment.
"""

import asyncio
import os
from abc import abstractmethod
from pathlib import Path
from typing import Optional, Callable, List, Tuple, Dict, Any

from loguru import logger

from .controller import DeploymentController
from .git_operations import extract_project_name_from_url, read_readme_from_repo, clone_repository
from .graph import DeploymentGraph
from ...llm import LLMProvider


class BaseEntry:
    """
    Base class for deployment entry points.

    Provides common functionality for different deployment entry methods.
    """

    def __init__(
            self,
            llm_provider: LLMProvider,
            working_dir: Optional[str] = None,
            max_fix_depth: int = 2,
            interaction_handler: Optional[Callable[[str, List[str]], str]] = None,
            enable_autoapi: bool = False,
            autoapi_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the base entry.

        Args:
            llm_provider: LLM provider instance
            working_dir: Working directory for deployment
            max_fix_depth: Maximum depth of FixNode layers under CommandNode
            interaction_handler: Optional callback for handling user interactions
            enable_autoapi: Whether to enable AutoAPI integration after deployment
            autoapi_config: Configuration for AutoAPI integration
        """
        if llm_provider is None:
            raise ValueError("llm_provider must be provided")

        self.llm_provider = llm_provider
        self.working_dir = working_dir or os.getcwd()
        working_dir_obj = Path(self.working_dir)

        if not working_dir_obj.exists():
            logger.info(f"Creating working directory: {self.working_dir}")
            working_dir_obj.mkdir(parents=True, exist_ok=True)
        elif not working_dir_obj.is_dir():
            raise ValueError(f"Working directory path is not a directory: {self.working_dir}")
        else:
            logger.info(f"Using existing working directory: {self.working_dir}")

        self.max_fix_depth = max_fix_depth
        self.interaction_handler = interaction_handler

        # AutoAPI 集成相关配置
        self.enable_autoapi = enable_autoapi
        self.autoapi_config = autoapi_config or {}

    async def _deploy_from_readme_content(
            self,
            readme_content: str,
            project_name: str,
            working_dir: str,
            repository_url: Optional[str] = None,
            save_visualization: bool = True,
            visualization_filename: str = "deployment_graph.graphml",
    ) -> Tuple[bool, str]:
        """
        Core deployment logic that works with README content.

        Args:
            readme_content: README content to analyze and deploy from
            project_name: Name of the project
            working_dir: Working directory for deployment
            repository_url: Optional URL of the repository if it was cloned
            save_visualization: Whether to save graph visualization
            visualization_filename: Name of the visualization file

        Returns:
            Tuple of (success, execution_report)
        """
        async with DeploymentController(
                graph=None,  # No pre-built graph
                working_dir=working_dir,
                llm_provider=self.llm_provider,
                max_fix_depth=self.max_fix_depth,
                interaction_handler=self.interaction_handler,
        ) as controller:
            # Set deployment info
            # controller.deploy_info["readme_content"] = readme_content
            controller.deploy_info["project_name"] = project_name
            
            # Track if this deployment is from a cloned repository
            if repository_url:
                if repository_url not in controller.deploy_info["cloned_repositories"]:
                    controller.deploy_info["cloned_repositories"].append(repository_url)
            
            # Check if any repository has been cloned
            has_cloned_repo = len(controller.deploy_info["cloned_repositories"]) > 0

            # Analyze README structure
            deployment_content = await controller.analyze_readme_structure_async(readme_content)
            controller.deploy_info["deployment_content"] = deployment_content

            # Extract core steps from deployment content
            core_steps = await controller.extract_core_steps_async(
                deployment_content, git_cloned=has_cloned_repo
            )

            # Create deployment graph
            graph_name = f"{project_name} Deployment"
            controller.graph = DeploymentGraph(graph_name)

            # Create root node
            controller.graph.create_root(
                name=graph_name,
                description=f"Deployment process for {project_name}",
            )

            # Create core step nodes
            core_step_nodes = []
            for step_data in core_steps:
                core_step_node = controller.graph.add_core_step(
                    parent_id=controller.graph.root.id,
                    name=step_data.get("name", "Unknown Step"),
                    description=step_data.get("description", ""),
                )
                core_step_nodes.append(core_step_node)



            # Execute each core step in sequence, generating methods on-the-fly
            overall_success = True

            if not core_step_nodes:
                logger.warning("No core steps found in analysis")
                return True, "No core steps found in analysis"

            for core_step_node in core_step_nodes:
                step_success = await controller.execute_core_step_reactive(core_step_node)

                # If a core step fails, handle it based on interaction settings
                if not step_success:
                    if self.interaction_handler:
                        message = (
                            f"Core step '{core_step_node.name}' failed. "
                            f"Would you like to retry, skip, or abort?"
                        )
                        options = ["retry", "skip", "abort"]
                        choice = self.interaction_handler(message, options)

                        if choice == "retry":
                            # Retry this core step
                            logger.info(f"Retrying core step: {core_step_node.name}")
                            step_success = await controller.execute_core_step_reactive(
                                core_step_node
                            )
                            if step_success:
                                continue

                        elif choice == "skip":
                            # Skip this core step and continue
                            logger.info(f"Skipping core step: {core_step_node.name}")
                            controller.execution_status[core_step_node.id] = (
                                controller.ExecutionStatus.SKIPPED
                            )
                            continue

                        else:  # abort
                            logger.info("Deployment aborted by user")
                            overall_success = False
                            break
                    else:
                        # No interaction handler, so abort deployment
                        logger.error(f"Deployment failed at core step: {core_step_node.name}")
                        overall_success = False
                        break

            # Save visualization if requested and we have a graph
            if save_visualization and controller.graph:
                viz_path = os.path.join(self.working_dir, visualization_filename)
                graphml_content = controller.graph.to_graphml()
                with open(viz_path, "w", encoding="utf-8") as f:
                    f.write(graphml_content)
                logger.info(f"Deployment graph visualization saved to: {viz_path}")

            # Generate execution report
            report = controller.generate_execution_report()

            # After successful deployment, check if user wants to start the service
            if overall_success and not controller.auto_start_service:
                # Check if there's any startup-related content in the deployment
                has_startup_info = any(
                    keyword in deployment_content.lower()
                    for keyword in ["start", "run", "launch", "execute", "serve"]
                )

                if has_startup_info and self.interaction_handler:
                    message = (
                        "Deployment completed successfully! The project appears to have startup instructions. "
                        "Would you like to start the service now?"
                    )
                    options = ["yes", "no"]
                    choice = self.interaction_handler(message, options)

                    if choice == "yes":
                        logger.info("User chose to start the service after deployment")
                        # Set the flag temporarily for service startup
                        controller.auto_start_service = True
                        controller.deploy_info["auto_start_service"] = True

                        # Create and execute a service startup step
                        startup_step = controller.graph.add_core_step(
                            parent_id=controller.graph.root.id,
                            name="Service Startup",
                            description="Start the deployed service based on README instructions"
                        )

                        # Execute the startup step
                        startup_success = await controller.execute_core_step_reactive(startup_step)

                        if startup_success:
                            report += "\n\nService startup completed successfully."
                        else:
                            report += "\n\nService startup failed. Please check the logs."
                    else:
                        logger.info("User chose not to start the service")
                        report += "\n\nDeployment completed. Service not started (user choice)."

        # AutoAPI 集成处理
        if overall_success and self.enable_autoapi:
            overall_success, report = await self._handle_autoapi_integration(
                overall_success, report, readme_content, project_name
            )

            return overall_success, report
        else:
            logger.info("AutoAPI integration not enabled or deployment failed")
            return overall_success, report

    async def _handle_autoapi_integration(self,
                                          success: bool,
                                          report: str,
                                          readme_content: str,
                                          project_name: str) -> Tuple[bool, str]:
        """
        处理 AutoAPI 集成
        
        Args:
            success: 部署是否成功
            report: 部署报告
            readme_content: 原始README内容，用作LLM上下文
            project_name: 项目名称
            
        Returns:
            Tuple[bool, str]: 更新后的成功状态和报告
        """
        if not success:
            return success, report

        try:
            # 延迟导入 AutoAPI 客户端
            from ..autoapi.client import create_autoapi_client

            # 获取 AutoAPI 配置
            api_host = self.autoapi_config.get('api_host', '127.0.0.1')
            api_port = self.autoapi_config.get('api_port', 8081)

            # 创建 AutoAPI 客户端
            autoapi_client = create_autoapi_client(api_host=api_host, api_port=api_port)

            # 检查 AutoAPI 服务器是否运行
            if not autoapi_client.is_server_running():
                error_report = f"\n\n❌ AutoAPI 服务器未运行 (http://{api_host}:{api_port})，请先启动 AutoAPI 服务器"
                report += error_report
                logger.warning(f"AutoAPI 服务器未运行: http://{api_host}:{api_port}")
                return success, report

            # 从配置中获取参数
            service_name = self.autoapi_config.get('service_name', project_name)
            service_description = self.autoapi_config.get('service_description',
                                                          f"{project_name} - 通过 AutoDeploy 部署")
            auto_start_service = self.autoapi_config.get('auto_start_service', False)

            # 构造部署报告
            deployment_report = {
                "project_name": project_name,
                "deployment_success": success,
                "report": report
            }

            # 注册服务到 AutoAPI
            register_result = autoapi_client.register_service_from_deployment(
                deployment_report=deployment_report,
                readme_content=readme_content,
                service_name=service_name,
                service_description=service_description,
                auto_start=auto_start_service
            )

            # 更新报告
            if register_result["success"]:
                service_id = register_result["service_id"]
                autoapi_report = f"\n\n🤖 AutoAPI 集成成功:\n"
                autoapi_report += f"   服务ID: {service_id}\n"
                autoapi_report += f"   服务名称: {register_result.get('name', service_name)}\n"

                if register_result.get("auto_start", {}).get("success"):
                    autoapi_report += f"   服务状态: 自动启动成功\n"

                # 显示 AutoAPI 服务器信息
                autoapi_report += f"   AutoAPI 服务器: http://{api_host}:{api_port}\n"
                autoapi_report += f"   API 文档: http://{api_host}:{api_port}/docs\n"
                autoapi_report += f"\n💡 您可以通过以下方式管理服务:\n"
                autoapi_report += f"   • 启动服务: curl -X POST http://{api_host}:{api_port}/services/{service_id}/start\n"
                autoapi_report += f"   • 停止服务: curl -X POST http://{api_host}:{api_port}/services/{service_id}/stop\n"
                autoapi_report += f"   • 获取状态: curl http://{api_host}:{api_port}/services/{service_id}/status\n"

                report += autoapi_report
                logger.info(f"AutoAPI 集成成功，服务ID: {service_id}")

            else:
                error_report = f"\n\n❌ AutoAPI 集成失败: {register_result['error']}"
                report += error_report
                logger.warning(f"AutoAPI 集成失败: {register_result['error']}")

        except ImportError as e:
            error_report = f"\n\n⚠️  AutoAPI 模块不可用: {str(e)}"
            report += error_report
            logger.warning(f"AutoAPI 模块不可用: {e}")

        except Exception as e:
            error_report = f"\n\n❌ AutoAPI 集成过程出错: {str(e)}"
            report += error_report
            logger.error(f"AutoAPI 集成过程出错: {e}")

        return success, report

    @abstractmethod
    async def deploy(self, **kwargs) -> Tuple[bool, str]:
        """
        Deploy using this entry method.

        Returns:
            Tuple of (success, execution_report)
        """
        pass

    def deploy_sync(self, **kwargs) -> Tuple[bool, str]:
        """
        Synchronous wrapper for deploy method.

        Returns:
            Tuple of (success, execution_report)
        """
        return asyncio.run(self.deploy(**kwargs))

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass


class GitRepositoryEntry(BaseEntry):
    """
    Entry point for deploying from a Git repository.

    This entry point clones a Git repository, extracts its README content,
    and delegates to the base README deployment logic.
    """

    async def deploy(
            self, git_url: str, project_name: Optional[str] = None, save_visualization: bool = True
    ) -> Tuple[bool, str]:
        """
        Deploy a project directly from Git repository.

        This method clones the repository, extracts README content, then delegates
        to the base README deployment logic.

        Args:
            git_url: Git repository URL
            project_name: Optional name for the project
            save_visualization: Whether to save graph visualization

        Returns:
            Tuple of (success, execution_report)
        """
        logger.info(f"Starting Git repository deployment: {git_url}")

        try:
            # Extract project name if not provided
            if not project_name:
                project_name = extract_project_name_from_url(git_url)

            # Clone the repository with robust checks
            clone_success, clone_message, repo_dir = clone_repository(
                git_url, project_name, self.working_dir, self.interaction_handler, self.llm_provider
            )

            if not clone_success:
                return False, clone_message

            # Read README content
            readme_content = read_readme_from_repo(repo_dir, self.llm_provider)
            if not readme_content:
                logger.warning("No README content found, continuing with minimal analysis")
                readme_content = f"Repository: {git_url}\nProject: {project_name}"

            # Delegate to base README deployment logic
            return await self._deploy_from_readme_content(
                readme_content=readme_content,
                project_name=project_name,
                working_dir=repo_dir,  # Use cloned repository as working directory
                repository_url=git_url,  # Pass the repository URL
                save_visualization=save_visualization,
                visualization_filename="deployment_graph_git.graphml",
            )

        except Exception as e:
            logger.error(f"Git repository deployment failed: {e}")
            return False, f"Error: {str(e)}"


class DirectDeploymentEntry(BaseEntry):
    """
    Entry point for direct deployment with user-provided instructions.

    This entry point allows users to provide deployment instructions directly,
    bypassing the need for Git repositories or README files.
    """

    async def deploy(
            self, instructions: str, project_name: Optional[str] = None, save_visualization: bool = True
    ) -> Tuple[bool, str]:
        """
        Deploy based on direct user instructions.

        Args:
            instructions: Direct deployment instructions from user
            project_name: Optional name for the project
            save_visualization: Whether to save graph visualization

        Returns:
            Tuple of (success, execution_report)
        """
        logger.info("Starting direct deployment")

        try:
            # Validate instructions
            if not instructions or not instructions.strip():
                raise ValueError("Instructions cannot be empty")

            # Use project name or default
            project_name = project_name or "Direct Deployment"

            # Treat instructions as README content and delegate to base logic
            return await self._deploy_from_readme_content(
                readme_content=instructions,
                project_name=project_name,
                working_dir=self.working_dir,
                repository_url=None,  # No repository cloned for direct deployment
                save_visualization=save_visualization,
                visualization_filename="deployment_graph_direct.graphml",
            )

        except Exception as e:
            logger.error(f"Direct deployment failed: {e}")
            return False, f"Error: {str(e)}"


# Convenience function for backward compatibility and ease of use
def deploy_from_git(
        git_url: str,
        llm_provider: LLMProvider,
        project_name: Optional[str] = None,
        working_dir: Optional[str] = None,
        save_visualization: bool = True,
        max_fix_depth: int = 2,
        interaction_handler: Optional[Callable[[str, List[str]], str]] = None,
        enable_autoapi: bool = False,
        autoapi_config: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, str]:
    """
    Convenience function to deploy from Git repository.

    Args:
        git_url: Git repository URL
        llm_provider: LLM provider instance
        project_name: Optional project name
        working_dir: Working directory for deployment
        save_visualization: Whether to save graph visualization
        max_fix_depth: Maximum depth of FixNode layers under CommandNode
        interaction_handler: Optional callback for handling user interactions
        enable_autoapi: Whether to enable AutoAPI integration after deployment
        autoapi_config: Configuration for AutoAPI integration
            - service_name: 服务名称
            - service_description: 服务描述
            - auto_start_service: 是否自动启动服务
            - start_api_server: 是否启动 API 服务器
            - api_host: API 主机地址 (默认: 127.0.0.1)
            - api_port: API 端口 (默认: 8080)
            - registry_path: 服务注册表路径
            - enable_monitoring: 是否启用监控 (默认: True)

    Returns:
        Tuple of (success, execution_report)
    """
    entry = GitRepositoryEntry(
        llm_provider=llm_provider,
        working_dir=working_dir,
        max_fix_depth=max_fix_depth,
        interaction_handler=interaction_handler,
        enable_autoapi=enable_autoapi,
        autoapi_config=autoapi_config,
    )

    return entry.deploy_sync(
        git_url=git_url, project_name=project_name, save_visualization=save_visualization
    )


def deploy_from_instructions(
        instructions: str,
        llm_provider: LLMProvider,
        project_name: Optional[str] = None,
        working_dir: Optional[str] = None,
        save_visualization: bool = True,
        max_fix_depth: int = 2,
        interaction_handler: Optional[Callable[[str, List[str]], str]] = None,
        enable_autoapi: bool = False,
        autoapi_config: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, str]:
    """
    Convenience function to deploy from direct instructions.

    Args:
        instructions: Direct deployment instructions
        llm_provider: LLM provider instance
        project_name: Optional project name
        working_dir: Working directory for deployment
        save_visualization: Whether to save graph visualization
        max_fix_depth: Maximum depth of FixNode layers under CommandNode
        interaction_handler: Optional callback for handling user interactions
        enable_autoapi: Whether to enable AutoAPI integration after deployment
        autoapi_config: Configuration for AutoAPI integration (same as deploy_from_git)

    Returns:
        Tuple of (success, execution_report)
    """
    entry = DirectDeploymentEntry(
        llm_provider=llm_provider,
        working_dir=working_dir,
        max_fix_depth=max_fix_depth,
        interaction_handler=interaction_handler,
        enable_autoapi=enable_autoapi,
        autoapi_config=autoapi_config,
    )

    return entry.deploy_sync(
        instructions=instructions, project_name=project_name, save_visualization=save_visualization
    )
