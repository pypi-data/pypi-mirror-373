"""
Controller for executing deployment flows based on the deployment graph.

This module provides the main execution logic for traversing and executing
the deployment graph, handling errors, and implementing fallback strategies.
"""

import asyncio
import os
import pprint
import re
from enum import Enum, auto
from typing import List, Dict, Optional, Callable, Any

from .command import ItermCommandExecutor, CommandResult, create_command_executor
from .graph import DeploymentGraph
from .log_config import (
    logger,
    log_llm_evaluation,
    log_heuristic_evaluation,
    log_fix_generation,
    log_verification_skip,
    log_node_details
)
from .nodes import (
    Node,
    CoreStepNode,
    MethodNode,
    CommandNode,
    FixNode,
    LogicCommandNode,
    VerifyNode,
    ForwardNode,
)
from .prompts import (
    LOGIC_CONDITION_EVALUATION_PROMPT,
    CORE_STEPS_EXTRACTION_PROMPT,
    SINGLE_METHOD_GENERATION_PROMPT,
    COMMAND_GENERATION_PROMPT,
    FIX_COMMAND_GENERATION_PROMPT,
)
from ... import utils
from ...llm import LLMProvider


class ExecutionStatus(Enum):
    """Status of execution for steps in the deployment process."""

    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    SKIPPED = auto()


class DeploymentController:
    """
    Controls the execution of deployment steps based on a deployment graph.

    This class handles the actual execution of commands, verification of results,
    error handling, and fallback to alternative methods when needed.
    """

    def __init__(
            self,
            graph: Optional[DeploymentGraph] = None,
            interaction_handler: Optional[Callable[[str, List[str]], str]] = None,
            working_dir: Optional[str] = None,
            env: Optional[Dict[str, str]] = None,
            llm_provider: Optional[LLMProvider] = None,
            max_fix_depth: int = 2,
    ):
        """
        Initialize the deployment controller.

        Args:
            graph: The deployment graph to execute (optional in reactive mode)
            interaction_handler: Optional callback for handling user interactions
            working_dir: Working directory for command execution
            env: Environment variables for command execution
            llm_provider: LLM provider for generating steps and analysis
            max_fix_depth: Maximum depth of FixNode layers under CommandNode (default: 2)
        """
        if llm_provider is None:
            raise ValueError("llm_provider must be provided")

        self.graph = graph
        self.llm_provider = llm_provider
        self.interaction_handler = interaction_handler
        self.working_dir = working_dir or os.getcwd()
        self.env = env or os.environ.copy()
        self.execution_status: Dict[str, ExecutionStatus] = {}
        self.command_results: Dict[str, CommandResult] = {}

        # Initialize command executor using factory function
        self.command_executor = create_command_executor(working_dir=self.working_dir, env=self.env)
        self.max_fix_depth = max_fix_depth
        self.user_knowledge_base: list = [
            "默认情况下配置文件优先使用默认设置，只填写必要参数",
            "一切 Python 的项目全部用 Conda 来管理环境。"]  # User knowledge base
        self.deploy_info: dict = {}  # The information related to the deployment of the current project that needs to be conveyed in LLM Calling
        self.deploy_info.update(utils.get_environment_info())
        # Initialize current working directory in deploy_info
        self.deploy_info["current_working_directory"] = os.path.abspath(self.working_dir)
        # Initialize verified software and git status tracking
        self.deploy_info["verified_software"] = []  # List of verified software/dependencies
        self.deploy_info["cloned_repositories"] = []  # List of cloned repository URLs

        # Service startup configuration
        self.auto_start_service = os.environ.get("AUTO_START_SERVICE", "false").lower() == "true"
        self.deploy_info["auto_start_service"] = self.auto_start_service

    def _escape_for_logging(self, text: str) -> str:
        """
        Escape braces in text to prevent loguru format string conflicts.
        
        Args:
            text: Text that may contain braces that need escaping
            
        Returns:
            Text with braces properly escaped for loguru
        """
        return text.replace("{", "{{").replace("}", "}}")

    async def analyze_readme_structure_async(self, readme_content: str) -> str:
        """
        Asynchronously extract deployment-related content from README using LLM.

        Args:
            readme_content: Content of README file

        Returns:
            Extracted deployment-related content as string
        """
        logger.info("Extracting deployment-related content from README with LLM asynchronously...")

        system_prompt = """You are an expert system administrator and deployment specialist. Your task is to extract deployment-related content from README files.

Given README content, extract and return ONLY the deployment-related information including:
1. Installation instructions
2. Setup procedures
3. Configuration steps
4. Build/compilation instructions
5. Environment setup
6. Dependency installation
7. Service startup procedures
8. Deployment procedures
9. Quick start guides
10. Getting started sections

Focus on extracting the actual deployment content, not analyzing it. Return the extracted content as plain text, preserving the original formatting and structure where possible.

If no deployment-related content is found, return a brief summary of what the project appears to be about based on the README content.

Do not add analysis, commentary, or additional information. Only extract the relevant deployment sections."""

        user_prompt = f"README Content:\n\n{readme_content}"

        response = await self.llm_provider.generate_completion_async(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_format=False,  # Changed to False since we want plain text
            temperature=0.1,  # Lower temperature for more consistent extraction
        )

        if not response:
            logger.warning("Failed to extract deployment content from README")
            return "No deployment-related content found in README"

        logger.info("Deployment content extraction completed")
        return str(response)

    async def extract_core_steps_async(
            self, deployment_analysis: Dict | str, git_cloned: bool = False
    ) -> List[Dict]:
        """
        Asynchronously extract core deployment steps from repository analysis.

        Args:
            deployment_analysis: Structured analysis from analyze_readme_structure_async
            git_cloned: Whether the repository was cloned from Git

        Returns:
            List of core steps with metadata
        """
        logger.info("Extracting core deployment steps asynchronously...")

        analysis_text = str(deployment_analysis)

        if git_cloned:
            git_prompt = "The repository has been cloned, please do not generate any Core Steps about cloning the repository"
        else:
            git_prompt = "The repository has not been cloned, please generate Core Steps about cloning the repository first"

        # Add startup configuration to the prompt
        startup_prompt = ""
        if self.auto_start_service:
            startup_prompt = "\n\nService startup is enabled (AUTO_START_SERVICE=true). Include service startup steps if documented in the README."
        else:
            startup_prompt = "\n\nService startup is disabled (AUTO_START_SERVICE=false). Do NOT include service startup steps."

        response = await self.llm_provider.generate_completion_async(
            system_prompt=CORE_STEPS_EXTRACTION_PROMPT,
            user_prompt=f"Repository Analysis:\n\n{analysis_text}\n\n{git_prompt}{startup_prompt}",
            json_format=True,
        )

        if not response:
            raise ValueError("Failed to extract core steps")

        # Handle both old and new response formats for backward compatibility
        if "core_steps" in response:
            core_steps = response["core_steps"]

            # Log the deployment reasoning if available
            if "deployment_reasoning" in response:
                logger.info(f"Deployment reasoning: {response['deployment_reasoning']}")

            # Log excluded steps if available
            if "excluded_steps" in response:
                logger.info(f"Excluded steps: {response['excluded_steps']}")

        else:
            # Fallback for old format
            core_steps = response.get("core_steps", [])

        logger.info(f"Extracted {len(core_steps)} core steps")
        return core_steps

    async def generate_single_method_for_step_async(
            self, core_step: Dict, other_info: str = None, failed_context: str = ""
    ) -> Dict:
        """
        Asynchronously generate a single optimal method for a core step.

        Args:
            core_step: Core step information
            other_info: Additional information, such as environment details
            failed_context: Context about previously failed methods

        Returns:
            Single method option for the core step
        """
        logger.info(
            f"Generating single method for core step asynchronously: {core_step.get('name', 'Unknown')}"
        )

        step_text = str(core_step)

        # Use the single method generation prompt with failed context
        prompt_with_context = SINGLE_METHOD_GENERATION_PROMPT.replace("{failed_context}", failed_context)

        response = await self.llm_provider.generate_completion_async(
            system_prompt=prompt_with_context,
            user_prompt=f"Core Step:\n{step_text}\n\n{other_info}",
            json_format=True,
        )

        if not response or "method" not in response:
            logger.warning(f"Failed to generate method for step: {core_step.get('name')}")
            return {}

        method = response["method"]
        logger.info(f"Generated single method for core step")
        return method

    async def generate_commands_for_method_async(
            self, method: Dict, other_info: str = None
    ) -> List[Dict]:
        """
        Asynchronously generate specific commands for a method.

        Args:
            method: Method information
            other_info: Additional information, such as environment details

        Returns:
            List of commands with verification
        """
        logger.info(
            f"Generating commands for method asynchronously: {method.get('name', 'Unknown')}"
        )

        method_text = str(method)

        response = await self.llm_provider.generate_completion_async(
            system_prompt=COMMAND_GENERATION_PROMPT,
            user_prompt=f"Method:\n{method_text}\n\n{other_info}",
            json_format=True,
        )

        if not response or "commands" not in response:
            logger.warning(f"Failed to generate commands for method: {method.get('name')}")
            return []

        commands = response["commands"]
        logger.info(f"Generated {len(commands)} commands for method")
        return commands

    async def execute_command(
            self, command: str, missing_info: bool = False, interactive: bool = False
    ) -> CommandResult:
        """
        Execute a shell command and return the result.

        Args:
            command: Shell command to execute
            missing_info: Whether this command needs user-provided information
            interactive: Whether this command requires direct terminal interaction

        Returns:
            CommandResult object with execution results
        """
        if missing_info:
            command = self.command_executor.complete_missing_info_command(command)
        if interactive:
            command_result = self.command_executor.execute_interactive_command(command)
        else:
            command_result = self.command_executor.execute_command(command)

        # Handle git clone commands specially - switch to cloned directory after execution
        if "git clone" in command.lower() and command_result.success:
            cloned_dir = self._extract_git_clone_directory(command)
            if cloned_dir and os.path.exists(cloned_dir):
                # Update the current working directory in deploy_info
                self.deploy_info["current_working_directory"] = cloned_dir
                self.command_executor.working_dir = cloned_dir
                self.command_executor._session_initialized = False
                logger.info(f"Changed working directory to git repository: {cloned_dir}")

                # Track the cloned repository
                await self._track_cloned_repository(command, cloned_dir)
        elif new_working_dir := self._extract_new_directory_path(command):
            # Handle regular cd commands
            if not "git clone" in command.lower():
                # Update the current working directory in deploy_info
                self.deploy_info["current_working_directory"] = new_working_dir
                self.command_executor.working_dir = new_working_dir
                self.command_executor._session_initialized = False
                logger.info(f"Changed working directory to: {new_working_dir}")

        return command_result


    def _extract_new_directory_path(self, command: str) -> Optional[str]:
        """
        Extract the new working directory from a cd or git clone command and its output.

        Args:
            command: The command that was executed

        Returns:
            Extracted directory path or None if not found
        """
        # Try to extract directory from 'cd' command
        cd_match = re.search(r'cd\s+(["\']?)([^\n\r&;]+?)\1(?=\s*(&&|;|\||$))', command)
        if cd_match:
            path = cd_match.group(2).strip()
            # Handle relative paths
            if not os.path.isabs(path):
                current_dir = self.deploy_info.get("current_working_directory", self.working_dir)
                path = os.path.normpath(os.path.join(current_dir, path))
            return path

        return None

    def _extract_git_clone_directory(self, command: str) -> Optional[str]:
        """
        Extract the target directory from a git clone command.
        
        Args:
            command: The git clone command that was executed
            
        Returns:
            The directory path where the repository was cloned, or None if not found
        """
        # Try to extract directory from 'git clone' command
        git_clone_match = re.search(r"git\s+clone\s+(?:\S+)(?:\s+(\S+))?", command)
        if git_clone_match:
            clone_dir = git_clone_match.group(1)
            if clone_dir:
                # Handle relative paths
                if not os.path.isabs(clone_dir):
                    current_dir = self.deploy_info.get(
                        "current_working_directory", self.working_dir
                    )
                    clone_dir = os.path.normpath(os.path.join(current_dir, clone_dir))
                return clone_dir
            else:
                # If no directory is specified, try to extract repo name from URL
                url_match = re.search(r"git\s+clone\s+(\S+)", command)
                if url_match:
                    repo_url = url_match.group(1)
                    repo_name = os.path.splitext(os.path.basename(repo_url.rstrip("/")))[0]
                    current_dir = self.deploy_info.get(
                        "current_working_directory", self.working_dir
                    )
                    return os.path.normpath(os.path.join(current_dir, repo_name))

        return None

    async def execute_command_node(self, node: CommandNode | None) -> bool:
        """
        Execute a command node in the deployment graph.

        Args:
            node: The command node to execute

        Returns:
            True if node executed successfully, False otherwise
        """
        # Handle LogicCommandNode specifically
        if isinstance(node, LogicCommandNode):
            return await self.execute_logic_command_node(node)

        self.graph.log_node(node, f"Executing command node ({node.node_type_name})")

        self.execution_status[node.id] = ExecutionStatus.RUNNING

        # Log detailed node information when execution starts
        log_node_details(node, "executing", "Command execution started")

        # Determine execution type
        missing_info = getattr(node, "missing_info", False)
        interactive = getattr(node, "interactive", False)

        # Execute the command
        if node.command:
            result = await self.execute_command(
                node.command, missing_info=missing_info, interactive=interactive
            )
        else:
            result = CommandResult(success=True, output="")

        self.command_results[node.id] = result

        # Store the output on the node and update in graph
        self.graph.update_node_status(
            node_id=node.id, succeeded=result.success, output=result.output, error=result.error
        )

        self.execution_status[node.id] = (
            ExecutionStatus.SUCCESS if result.success else ExecutionStatus.FAILED
        )

        # Log detailed node information when execution completes
        status = "completed" if result.success else "failed"
        log_node_details(node, status, f"Command execution {status}")

        return result.success

    async def evaluate_logic_condition_with_llm(self, node: LogicCommandNode, output: str) -> bool:
        """
        Use LLM to evaluate if the logical condition in a LogicCommandNode is met.

        Args:
            node: The logic command node
            output: The output from command execution

        Returns:
            True if condition is met, False otherwise
        """
        # Input validation
        if not node:
            logger.error("evaluate_logic_condition_with_llm: node parameter is None")
            return False

        if not isinstance(node, LogicCommandNode):
            logger.error(f"evaluate_logic_condition_with_llm: Expected LogicCommandNode, got {type(node)}")
            return False

        if output is None:
            logger.warning(f"evaluate_logic_condition_with_llm: output is None for node '{node.name}'")
            output = ""

        # Truncate extremely long outputs to avoid token limits
        max_output_length = 4000  # Reserve space for prompt
        if len(output) > max_output_length:
            logger.warning(
                f"Output truncated from {len(output)} to {max_output_length} characters for node '{node.name}'")
            output = output[:max_output_length] + "\n... (truncated)"

        # Retry mechanism for LLM calls
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                logger.info(
                    f"Evaluating logic condition for node '{node.name}' using LLM (attempt {retry_count + 1}/{max_retries})")

                # Create a well-formatted prompt
                user_prompt = f"""Analyze the following command execution output to determine if the logical condition is met.

Command: {node.command}
Command Description: {node.name}

Command Output:
```
{output}
```

Based on the output above, determine if the logical condition is met.
- If the command succeeded or found what it was looking for, return true
- If the command failed or did not find what it was looking for, return false

Remember to return your response in the required JSON format with a "result" field containing a boolean value."""

                response = await self.llm_provider.generate_completion_async(
                    system_prompt=LOGIC_CONDITION_EVALUATION_PROMPT,
                    user_prompt=user_prompt,
                    json_format=True,
                    temperature=0,  # Use deterministic response
                    max_tokens=100,  # We only need a simple true/false response
                )

                # Validate response structure
                if not isinstance(response, dict):
                    logger.error(f"LLM response is not a dictionary: {type(response)}")
                    retry_count += 1
                    continue

                if "result" not in response:
                    response_str = self._escape_for_logging(str(response))
                    logger.error(f"LLM response missing 'result' field: {response_str}")
                    retry_count += 1
                    continue

                # Extract and validate the result
                result = response.get("result")

                # Handle various representations of boolean values
                if isinstance(result, bool):
                    condition_met = result
                elif isinstance(result, str):
                    # Handle string representations
                    result_lower = result.lower().strip()
                    if result_lower in ["true", "yes", "1", "success"]:
                        condition_met = True
                    elif result_lower in ["false", "no", "0", "failure"]:
                        condition_met = False
                    else:
                        logger.error(f"Unexpected string result value: '{result}'")
                        retry_count += 1
                        continue
                elif isinstance(result, (int, float)):
                    # Handle numeric representations
                    condition_met = bool(result)
                else:
                    logger.error(f"Unexpected result type: {type(result)}, value: {result}")
                    retry_count += 1
                    continue

                # Log the evaluation result
                log_llm_evaluation(node.name, output, condition_met, response.get("reasoning"))

                return condition_met

            except asyncio.TimeoutError:
                logger.exception(
                    f"Timeout evaluating logic condition for '{node.name}' (attempt {retry_count + 1}/{max_retries})")
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(1)  # Brief delay before retry

            except Exception:
                logger.exception(
                    f"Error evaluating logic condition with LLM for '{node.name}' (attempt {retry_count + 1}/{max_retries})")
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(1)  # Brief delay before retry

        # If all retries failed, fall back to heuristic evaluation
        logger.warning(f"All LLM attempts failed for '{node.name}', falling back to heuristic evaluation")
        return self._heuristic_condition_evaluation(node, output)

    def _heuristic_condition_evaluation(self, node: LogicCommandNode, output: str) -> bool:
        """
        Fallback heuristic evaluation when LLM fails.
        
        Args:
            node: The logic command node
            output: The command output
            
        Returns:
            Boolean evaluation based on heuristics
        """
        logger.info(f"Using heuristic evaluation for node '{node.name}'")

        # Convert output to lowercase for case-insensitive matching
        output_lower = output.lower()

        # Common success indicators
        success_indicators = [
            "true",
            "success",
            "ok",
            "found",
            "exists",
            "running",
            "active",
            "installed",
            "available",
            "yes",
            "1",
            "enabled",
            "connected",
            "healthy",
            "ready",
        ]

        # Common failure indicators
        failure_indicators = [
            "false",
            "error",
            "fail",
            "not found",
            "does not exist",
            "doesn't exist",
            "missing",
            "stopped",
            "inactive",
            "not installed",
            "unavailable",
            "no",
            "0",
            "disabled",
            "disconnected",
            "unhealthy",
            "not ready",
            "command not found",
            "permission denied",
            "no such file",
            "cannot find",
            "unable to",
        ]

        # Check for explicit boolean outputs (common in check commands)
        if output_lower.strip() == "true":
            return True
        elif output_lower.strip() == "false":
            return False

        # Count indicators
        success_count = sum(1 for indicator in success_indicators if indicator in output_lower)
        failure_count = sum(1 for indicator in failure_indicators if indicator in output_lower)

        # Special handling for specific command patterns
        if "which" in node.command.lower() or "command -v" in node.command.lower():
            # For 'which' or 'command -v' commands, non-empty output usually means success
            if output.strip() and not any(fail in output_lower for fail in ["not found", "no "]):
                return True
        elif "test" in node.command.lower() or "[ " in node.command:
            # For test commands, check exit code indicators
            if "echo true" in node.command.lower() or "echo false" in node.command.lower():
                return output_lower.strip() == "true"

        # Make decision based on indicator counts
        has_output = bool(output.strip())

        if failure_count > success_count:
            result = False
        elif success_count > 0:
            result = True
        elif failure_count > 0:
            result = False
        else:
            # Default: if output is non-empty and no error indicators, assume success
            result = has_output

        log_heuristic_evaluation(node.name, success_count, failure_count, has_output, result)
        return result

    async def execute_logic_command_node(self, node: LogicCommandNode) -> bool:
        """
        Execute a logic command node and then execute the appropriate child based on the result.

        Args:
            node: The logic command node to execute

        Returns:
            True if logic command and selected child executed successfully, False otherwise
        """
        self.graph.log_node(node, "Executing logic command node")

        # Check if node has both required children
        if not node.is_complete():
            logger.error(f"LogicCommandNode '{node.name}' does not have exactly 2 children")
            self.execution_status[node.id] = ExecutionStatus.FAILED
            return False

        self.execution_status[node.id] = ExecutionStatus.RUNNING

        # Log detailed node information when logic command execution starts
        log_node_details(node, "executing", "Logic command execution started")

        # Execute the logic command first
        missing_info = getattr(node, "missing_info", False)
        interactive = getattr(node, "interactive", False)
        result = await self.execute_command(
            node.command, missing_info=missing_info, interactive=interactive
        )
        self.command_results[node.id] = result

        # Store the output on the node
        self.graph.update_node_status(
            node_id=node.id,
            succeeded=None,  # Don't set success yet, wait for child execution
            output=result.output,
            error=result.error,
        )

        # Evaluate the condition using LLM
        try:
            condition_result = await self.evaluate_logic_condition_with_llm(node, result.output)
            logger.info(f"Logic command condition evaluated to: {condition_result}")

            # Select which child to execute based on condition
            selected_child = node.true_child if condition_result else node.false_child
            child_name = "true" if condition_result else "false"

            self.graph.log_node(selected_child, f"Executing {child_name} child")

            # Execute the selected child
            child_success = await self.execute_command_node(selected_child)

            # Logic command succeeds if both the condition evaluation and child execution succeed
            success = result.success and child_success

            # Update node status in graph
            self.graph.update_node_status(
                node_id=node.id, succeeded=success, output=result.output, error=result.error
            )

            self.execution_status[node.id] = (
                ExecutionStatus.SUCCESS if success else ExecutionStatus.FAILED
            )

            # Log detailed node information when logic command execution completes
            status = "completed" if success else "failed"
            log_node_details(node, status, f"Logic command execution {status}")

            return success

        except Exception as e:
            self.graph.log_node(node, "Error during logic command execution", level="error")
            logger.exception("Exception details:")

            # Update node status in graph
            self.graph.update_node_status(
                node_id=node.id, succeeded=False, output=result.output, error=str(e)
            )

            self.execution_status[node.id] = ExecutionStatus.FAILED

            return False

    async def execute_fix_node(self, fix_node: FixNode, fix_confidence: str = "unknown") -> bool:
        """
        Execute a fix node by trying its fix commands.

        Args:
            fix_node: The fix node to execute
            fix_confidence: Confidence level of the fix (high/medium/low)

        Returns:
            True if any fix command succeeded, False otherwise
        """
        self.graph.log_node(fix_node, f"Executing fix node (depth: {fix_node.fix_depth}, confidence: {fix_confidence})")

        # Execute each fix command in sequence
        success = False
        for command_node in fix_node.children:
            if not isinstance(command_node, CommandNode):
                logger.warning(
                    f"Expected CommandNode as child of FixNode, got {command_node.__class__.__name__}"
                )
                continue

            command_success = await self.execute_command_node(command_node)

            # If any fix command succeeds, the fix is successful
            if command_success:
                success = True
            else:
                # If this fix command failed, try to create another fix based on confidence
                should_continue_fixing = not self._should_limit_fix_depth(fix_confidence, fix_node.fix_depth + 1)

                if should_continue_fixing:
                    logger.info(
                        f"Fix command failed, attempting deeper fix (depth {fix_node.fix_depth + 1}, "
                        f"confidence: {fix_confidence})"
                    )
                    deeper_fix_success = await self.create_and_execute_fix(
                        command_node, fix_node.fix_depth + 1, fix_confidence
                    )
                    if deeper_fix_success:
                        success = True
                        break
                else:
                    logger.info(
                        f"Fix command failed but depth limit reached for confidence '{fix_confidence}' "
                        f"at depth {fix_node.fix_depth + 1}"
                    )

        # Update fix node status in graph
        self.graph.update_node_status(
            node_id=fix_node.id, succeeded=success, error=None if success else "Fix attempt failed"
        )

        self.execution_status[fix_node.id] = (
            ExecutionStatus.SUCCESS if success else ExecutionStatus.FAILED
        )

        return success

    async def create_and_execute_fix(self, failed_command: CommandNode, fix_depth: int,
                                     fix_confidence: str = "unknown") -> bool:
        """
        Create and execute a fix node for a failed command.

        Args:
            failed_command: The command that failed
            fix_depth: Depth level for the fix
            fix_confidence: Confidence level of the fix (high/medium/low)

        Returns:
            True if fix was created and executed successfully, False otherwise
        """
        # Check depth limits based on confidence
        should_limit_depth = self._should_limit_fix_depth(fix_confidence, fix_depth)
        if should_limit_depth:
            logger.warning(
                f"Fix depth limit reached for confidence '{fix_confidence}' at depth {fix_depth}, "
                f"not creating deeper fix"
            )
            return False

        logger.info(f"Creating fix for failed command: {failed_command.name} at depth {fix_depth} "
                    f"(confidence: {fix_confidence})")

        try:
            # Create fix node
            fix_node = self.graph.add_fix_node(
                parent_command_id=failed_command.id,
                name=f"Fix for {failed_command.name}",
                fix_depth=fix_depth,
                description=f"Auto-generated fix attempt for failed command (confidence: {fix_confidence})",
            )

            # Generate fix commands using LLM
            fix_result = await self.generate_fix_commands(failed_command)

            # Extract confidence and commands from the result
            if isinstance(fix_result, dict):
                fix_commands = fix_result.get("commands", [])
                current_confidence = fix_result.get("confidence", fix_confidence)
            else:
                # Fallback for old format (shouldn't happen with new implementation)
                fix_commands = fix_result if isinstance(fix_result, list) else []
                current_confidence = fix_confidence

            # Add fix commands to the fix node
            for cmd_data in fix_commands:
                self.graph.add_fix_command(
                    parent_fix_id=fix_node.id,
                    name=cmd_data.get("name", "Fix Command"),
                    command=cmd_data.get("command", ""),
                    interactive=cmd_data.get("interactive", False),
                    description=cmd_data.get("description", ""),
                    missing_info=cmd_data.get("missing_info", False),
                )

            # Execute the fix node with confidence information
            return await self.execute_fix_node(fix_node, current_confidence)

        except Exception as e:
            logger.exception(f"Error creating fix for command {failed_command.name}")
            return False

    async def create_and_execute_initial_fix(self, failed_command: CommandNode, fix_depth: int = 1) -> bool:
        """
        Create and execute the initial fix for a failed command, generating confidence on the first attempt.
        
        Args:
            failed_command: The command that failed
            fix_depth: Depth level for the fix (default: 1)
            
        Returns:
            True if fix was created and executed successfully, False otherwise
        """
        # Generate fix commands to get initial confidence
        fix_result = await self.generate_fix_commands(failed_command)

        if isinstance(fix_result, dict):
            initial_confidence = fix_result.get("confidence", "unknown")
        else:
            initial_confidence = "unknown"

        # Now create and execute the fix with the determined confidence
        return await self.create_and_execute_fix(failed_command, fix_depth, initial_confidence)

    def _should_limit_fix_depth(self, fix_confidence: str, current_depth: int) -> bool:
        """
        Determine if fix depth should be limited based on confidence level.
        
        This implements confidence-based depth limiting:
        - High confidence fixes: Can continue indefinitely until success (no depth limit)
        - Non-high confidence fixes: Limited by max_fix_depth parameter
        
        This prevents infinite loops for uncertain fixes while allowing reliable 
        fixes to persist until they succeed.
        
        Args:
            fix_confidence: The confidence level (high/medium/low/unknown)
            current_depth: Current fix depth
            
        Returns:
            True if depth should be limited, False otherwise
        """
        # High confidence fixes can continue indefinitely
        if fix_confidence.lower() == "high":
            logger.debug(f"High confidence fix at depth {current_depth}: allowing to continue")
            return False

        # Non-high confidence fixes are limited by max_fix_depth
        should_limit = current_depth > self.max_fix_depth
        if should_limit:
            logger.info(f"Non-high confidence ({fix_confidence}) fix at depth {current_depth}: "
                        f"limiting (max_fix_depth={self.max_fix_depth})")
        return should_limit

    async def generate_fix_commands(self, failed_command: CommandNode) -> Dict:
        """
        Generate fix commands for a failed command using LLM.

        Args:
            failed_command: The command node that failed

        Returns:
            Dictionary containing fix commands and metadata including confidence
        """
        try:
            # Get the command result for error analysis
            command_result = self.command_results.get(failed_command.id)
            if not command_result:
                logger.warning(f"No command result found for failed command: {failed_command.id}")
                return {"commands": [], "confidence": "unknown"}

            # Prepare context for fix generation
            failure_context = {
                "command": failed_command.command,
                "command_name": failed_command.name,
                "command_description": failed_command.description,
                "error_output": command_result.error or "",
                "stdout_output": command_result.output or "",
                "exit_code": command_result.exit_code,
                "missing_info": getattr(failed_command, "missing_info", False),
                "interactive": getattr(failed_command, "interactive", False),
            }

            # Add environment and deployment context
            context_info = self.addition_info_llm_format()

            # Get MethodNode context for better fix generation
            method_node_context = self._get_method_node_context(failed_command)

            user_prompt = f"""Failed Command Analysis:
Command: {failure_context["command"]}
Command Name: {failure_context["command_name"]}
Description: {failure_context["command_description"]}
Exit Code: {failure_context["exit_code"]}
Error Output: {failure_context["error_output"]}
Standard Output: {failure_context["stdout_output"]}
Missing Info: {failure_context["missing_info"]}
Interactive: {failure_context["interactive"]}

Environment Context:
{context_info}

MethodNode Deployment Context:
{method_node_context}

Please analyze the failure and generate specific fix commands to resolve the issue."""

            response = await self.llm_provider.generate_completion_async(
                system_prompt=FIX_COMMAND_GENERATION_PROMPT,
                user_prompt=user_prompt,
                json_format=True,
                temperature=0.1,  # Lower temperature for more consistent fixes
            )

            if not response or "fix_commands" not in response:
                logger.warning("Failed to generate fix commands from LLM")
                return {"commands": [], "confidence": "unknown"}

            fix_commands = response["fix_commands"]
            failure_analysis = response.get("failure_analysis", "No analysis provided")
            fix_confidence = response.get("fix_confidence", "unknown")
            context_utilization = response.get("context_utilization", "No context utilization provided")

            log_fix_generation(failed_command.name, len(fix_commands), fix_confidence, failure_analysis)

            # Log the context utilization for debugging
            logger.info(f"MethodNode context utilization for {failed_command.name}: {context_utilization}")

            # Return the fix commands without adding the original command
            # The fix commands should be complete and self-contained
            if not fix_commands:
                logger.warning("No fix commands were generated from LLM")
                return {"commands": [], "confidence": fix_confidence}

            return {
                "commands": fix_commands,
                "confidence": fix_confidence,
                "analysis": failure_analysis,
                "context_utilization": context_utilization
            }

        except Exception:
            logger.exception("Error generating fix commands")
            return {"commands": [], "confidence": "unknown"}

    def _get_method_node_context(self, failed_command: CommandNode) -> str:
        """
        Get context about all nodes in the MethodNode that contains the failed command.
        This helps the LLM understand what has already been deployed/executed in this method.
        
        Args:
            failed_command: The command node that failed
            
        Returns:
            Formatted string with MethodNode context information
        """
        try:
            # Find the parent MethodNode
            method_node = self._find_parent_method_node(failed_command)
            if not method_node:
                return "No parent MethodNode found for the failed command."

            # Collect all nodes under this MethodNode
            all_nodes = self._collect_all_nodes_under_method(method_node)

            # Generate context summary
            context_lines = []
            context_lines.append(f"MethodNode: {method_node.name}")
            if method_node.description:
                context_lines.append(f"Description: {method_node.description}")
            if method_node.working_directory:
                context_lines.append(f"Working Directory: {method_node.working_directory}")

            context_lines.append(f"\nNodes and their execution status in this method:")

            for node in all_nodes:
                if node.id == method_node.id:
                    continue  # Skip the method node itself

                # Get execution status
                status = self.execution_status.get(node.id, ExecutionStatus.PENDING)
                status_str = self._get_status_display(status)

                # Get node info
                node_info = f"  - [{status_str}] {node.name} (Type: {node.node_type_name})"
                if node.description:
                    node_info += f" - {node.description}"

                # Add command details for CommandNode
                if isinstance(node, CommandNode) and node.command:
                    node_info += f"\n    Command: {node.command}"

                # Add execution results if available
                if node.id in self.command_results:
                    result = self.command_results[node.id]
                    if result.output:
                        node_info += f"\n    Output: {result.output[:200]}..."  # Truncate long output
                    if result.error:
                        node_info += f"\n    Error: {result.error[:200]}..."  # Truncate long error

                context_lines.append(node_info)

            return "\n".join(context_lines)

        except Exception as e:
            logger.warning(f"Error getting MethodNode context: {e}")
            return "Error retrieving MethodNode context information."

    def _find_parent_method_node(self, node: Node) -> Optional[MethodNode]:
        """
        Find the parent MethodNode for a given node by traversing up the hierarchy.
        
        Args:
            node: The node to find parent method for
            
        Returns:
            The parent MethodNode or None if not found
        """
        current_node = node
        while current_node.parent_id:
            parent_node = self.graph.get_node(current_node.parent_id)
            if isinstance(parent_node, MethodNode):
                return parent_node
            current_node = parent_node
        return None

    def _collect_all_nodes_under_method(self, method_node: MethodNode) -> List[Node]:
        """
        Collect all nodes under a MethodNode recursively.
        
        Args:
            method_node: The method node to traverse
            
        Returns:
            List of all nodes under the method (including the method itself)
        """
        all_nodes = [method_node]

        def traverse_node(node: Node):
            for child in node.children:
                all_nodes.append(child)
                traverse_node(child)

        traverse_node(method_node)
        return all_nodes

    def _get_status_display(self, status: ExecutionStatus) -> str:
        """
        Get a display string for an execution status.
        
        Args:
            status: The execution status
            
        Returns:
            Display string for the status
        """
        if status == ExecutionStatus.SUCCESS:
            return "✓ SUCCESS"
        elif status == ExecutionStatus.FAILED:
            return "✗ FAILED"
        elif status == ExecutionStatus.SKIPPED:
            return "⟶ SKIPPED"
        elif status == ExecutionStatus.RUNNING:
            return "⟳ RUNNING"
        else:
            return "? PENDING"

    def _is_software_already_verified(self, command_node: CommandNode) -> bool:
        """
        Check if the software/dependency in this command node has already been verified.
        
        Args:
            command_node: The command node to check
            
        Returns:
            True if already verified, False otherwise
        """
        # Try to extract software name from the command node
        software_name = None
        
        if "check" in command_node.name.lower() or "verify" in command_node.name.lower():
            # Try to extract software name from node name
            if "installed" in command_node.name.lower():
                # Pattern: "Check if X is installed"
                import re
                match = re.search(r'check if (.+?) is installed', command_node.name.lower())
                if match:
                    software_name = match.group(1).strip()
            
            # Fallback: use the command itself to infer software
            if not software_name and command_node.command:
                command = command_node.command.lower()
                if "command -v" in command:
                    # Extract from "command -v software_name"
                    software_name = command.split("command -v")[1].split()[0].strip()
                elif "which" in command:
                    # Extract from "which software_name"
                    software_name = command.split("which")[1].split()[0].strip()
                elif "--version" in command:
                    # Extract from "software_name --version"
                    software_name = command.split("--version")[0].strip()
                elif "-v" in command and "echo" not in command:
                    # Extract from "software_name -v"
                    software_name = command.split("-v")[0].strip()
        
        # Check if this software is already in verified list
        if software_name and software_name in self.deploy_info["verified_software"]:
            log_verification_skip(str(software_name))
            return True
            
        return False

    async def execute_verify_node(self, verify_node: VerifyNode) -> bool:
        """
        Execute a verify node by running all its verification commands.

        Args:
            verify_node: The verify node to execute

        Returns:
            True if all verification commands executed successfully, False otherwise
        """
        self.graph.log_node(verify_node, "Executing verify node")

        self.execution_status[verify_node.id] = ExecutionStatus.RUNNING

        # Log detailed node information when verify node execution starts
        log_node_details(verify_node, "executing", "Verification phase started")

        # Execute all command children in sequence
        success = True
        verified_items = []  # Track successfully verified items
        
        for child_node in verify_node.children:
            if not isinstance(child_node, CommandNode):
                logger.warning(
                    f"Expected CommandNode as child of VerifyNode, got {child_node.__class__.__name__}"
                )
                continue
            
            # Check if this software/dependency is already verified
            if self._is_software_already_verified(child_node):
                # Mark as successful without executing
                self.execution_status[child_node.id] = ExecutionStatus.SUCCESS
                # Update node status in graph
                self.graph.update_node_status(
                    node_id=child_node.id, 
                    succeeded=True, 
                    output="Already verified, skipped execution"
                )
                continue

            command_success = await self.execute_command_node(child_node)

            # If any command fails, try to create and execute a fix
            if not command_success:
                logger.warning(
                    f"Verification command failed: {child_node.name}, attempting to fix..."
                )

                # Only try to fix regular CommandNodes, not LogicCommandNodes
                if isinstance(child_node, CommandNode) and not isinstance(
                        child_node, LogicCommandNode
                ):
                    fix_success = await self.create_and_execute_initial_fix(child_node, fix_depth=1)

                    if fix_success:
                        logger.info(f"Fix successful for verification command: {child_node.name}")
                        # Command was fixed, continue with verification
                        self._track_verified_item(child_node, verified_items)
                        continue
                    else:
                        logger.error(f"Fix failed for verification command: {child_node.name}")
                        # Command and fix both failed, verification fails
                        success = False
                        break
                else:
                    # LogicCommandNode failed, verification fails
                    logger.error(f"Logic command failed in verification: {child_node.name}")
                    success = False
                    break
            else:
                # Command succeeded, track it as verified
                self._track_verified_item(child_node, verified_items)

        # If verification was successful, update deploy_info with verified items
        if success and verified_items:
            self.deploy_info["verified_software"].extend(verified_items)
            # Remove duplicates while preserving order
            seen = set()
            unique_verified = []
            for item in self.deploy_info["verified_software"]:
                if item not in seen:
                    seen.add(item)
                    unique_verified.append(item)
            self.deploy_info["verified_software"] = unique_verified
            logger.info(f"Updated deploy_info with verified software: {verified_items}")

        # Update git status if any git-related commands were executed
        await self._update_git_status()

        # Update verify node status in graph
        self.graph.update_node_status(
            node_id=verify_node.id,
            succeeded=success,
            error=None if success else "Verification failed",
        )

        self.execution_status[verify_node.id] = (
            ExecutionStatus.SUCCESS if success else ExecutionStatus.FAILED
        )

        # Log detailed node information when verify node execution completes
        status = "completed" if success else "failed"
        log_node_details(verify_node, status, f"Verification phase {status}")

        return success

    async def execute_forward_node(self, forward_node: ForwardNode) -> bool:
        """
        Execute a forward node by running all its execution commands.

        Args:
            forward_node: The forward node to execute

        Returns:
            True if all execution commands executed successfully, False otherwise
        """
        self.graph.log_node(forward_node, "Executing forward node")

        self.execution_status[forward_node.id] = ExecutionStatus.RUNNING

        # Log detailed node information when forward node execution starts
        log_node_details(forward_node, "executing", "Forward execution phase started")

        # Execute all command children in sequence
        success = True
        for child_node in forward_node.children:
            if not isinstance(child_node, CommandNode):
                logger.warning(
                    f"Expected CommandNode as child of ForwardNode, got {child_node.__class__.__name__}"
                )
                continue

            command_success = await self.execute_command_node(child_node)

            # If any command fails, try to create and execute a fix
            if not command_success:
                logger.warning(f"Forward command failed: {child_node.name}, attempting to fix...")

                # Only try to fix regular CommandNodes, not LogicCommandNodes
                if isinstance(child_node, CommandNode) and not isinstance(
                        child_node, LogicCommandNode
                ):
                    fix_success = await self.create_and_execute_initial_fix(child_node, fix_depth=1)

                    if fix_success:
                        logger.info(f"Fix successful for forward command: {child_node.name}")
                        # Command was fixed, continue with execution
                        continue
                    else:
                        logger.error(f"Fix failed for forward command: {child_node.name}")
                        # Command and fix both failed, forward execution fails
                        success = False
                        break
                else:
                    # LogicCommandNode failed, forward execution fails
                    logger.error(f"Logic command failed in forward execution: {child_node.name}")
                    success = False
                    break

        # Update forward node status in graph
        self.graph.update_node_status(
            node_id=forward_node.id,
            succeeded=success,
            error=None if success else "Forward execution failed",
        )

        self.execution_status[forward_node.id] = (
            ExecutionStatus.SUCCESS if success else ExecutionStatus.FAILED
        )

        # Log detailed node information when forward node execution completes
        status = "completed" if success else "failed"
        log_node_details(forward_node, status, f"Forward execution phase {status}")

        return success

    async def execute_method(self, method_node: MethodNode) -> bool:
        """
        Execute a method node by first executing its verify node, then its forward node.

        Args:
            method_node: The method node to execute

        Returns:
            True if method executed successfully, False otherwise
        """
        self.graph.log_node(method_node, "Executing method")

        # Log detailed node information when method execution starts
        log_node_details(method_node, "executing", "Method execution started")

        # Find verify and forward nodes
        verify_node = None
        forward_node = None

        for child_node in method_node.children:
            if isinstance(child_node, VerifyNode):
                verify_node = child_node
            elif isinstance(child_node, ForwardNode):
                forward_node = child_node

        if not verify_node or not forward_node:
            logger.error(f"Method '{method_node.name}' must have both VerifyNode and ForwardNode")

            # Update method node status in graph
            self.graph.update_node_status(
                node_id=method_node.id,
                succeeded=False,
                error="Method missing required verify or forward nodes",
            )

            self.execution_status[method_node.id] = ExecutionStatus.FAILED
            return False

        # Execute verify node first
        self.graph.log_node(verify_node, "Executing verification phase")
        verify_success = await self.execute_verify_node(verify_node)

        if not verify_success:
            logger.error(f"Verification failed for method: {method_node.name}")

            # Update method node status in graph
            self.graph.update_node_status(
                node_id=method_node.id, succeeded=False, error="Verification phase failed"
            )

            self.execution_status[method_node.id] = ExecutionStatus.FAILED
            return False

        # Execute forward node
        self.graph.log_node(forward_node, "Executing forward phase")
        forward_success = await self.execute_forward_node(forward_node)

        if not forward_success:
            logger.error(f"Forward execution failed for method: {method_node.name}")

            # Update method node status in graph
            self.graph.update_node_status(
                node_id=method_node.id, succeeded=False, error="Forward execution phase failed"
            )

            self.execution_status[method_node.id] = ExecutionStatus.FAILED
            return False

        # Update method node status in graph
        self.graph.update_node_status(node_id=method_node.id, succeeded=True, error=None)

        self.execution_status[method_node.id] = ExecutionStatus.SUCCESS

        # Log detailed node information when method execution completes
        log_node_details(method_node, "completed", "Method execution completed successfully")
        
        return True

    async def execute_core_step(self, core_step_node: CoreStepNode) -> bool:
        """
        Execute a core step by trying each method in sequence until one succeeds.

        Args:
            core_step_node: The core step node to execute

        Returns:
            True if any method executed successfully, False otherwise
        """
        self.graph.log_node(core_step_node, "Executing core step")

        # Log detailed node information when core step execution starts
        log_node_details(core_step_node, "executing", "Core step execution started")

        # Get all method nodes under this core step
        method_nodes = [child for child in core_step_node.children if isinstance(child, MethodNode)]

        if not method_nodes:
            logger.warning(f"No methods found for core step: {core_step_node.name}")

            # Update core step node status in graph
            self.graph.update_node_status(
                node_id=core_step_node.id,
                succeeded=True,  # Consider it succeeded since there's nothing to execute
                output="No methods to execute",
            )

            self.execution_status[core_step_node.id] = ExecutionStatus.SKIPPED
            return True

        # Try each method in sequence
        for method_node in method_nodes:
            method_success = await self.execute_method(method_node)

            # If a method succeeds, the core step succeeds
            if method_success:
                # Update core step node status in graph
                self.graph.update_node_status(node_id=core_step_node.id, succeeded=True, error=None)

                self.execution_status[core_step_node.id] = ExecutionStatus.SUCCESS

                # Log detailed node information when core step execution completes
                log_node_details(core_step_node, "completed", "Core step execution completed successfully")
                
                return True

            # If a method fails, log and try the next one
            logger.warning(f"Method '{method_node.name}' failed, trying next method if available")

        # If all methods failed, the core step failed
        logger.error(f"All methods failed for core step: {core_step_node.name}")

        # Update core step node status in graph
        self.graph.update_node_status(
            node_id=core_step_node.id, succeeded=False, error="All methods failed"
        )

        self.execution_status[core_step_node.id] = ExecutionStatus.FAILED

        # Log detailed node information when core step execution fails
        log_node_details(core_step_node, "failed", "Core step execution failed - all methods failed")
        
        return False

    def addition_info_llm_format(self):
        info_s: Dict[str, Any] = dict()
        if self.user_knowledge_base:
            info_s["User Knowledge Base"] = self.user_knowledge_base
        if self.deploy_info:
            # Create a copy to avoid modifying the original
            deploy_info_copy = self.deploy_info.copy()
            # Add service startup preference
            deploy_info_copy["service_startup_preference"] = (
                "Service startup is ENABLED - include startup commands if applicable"
                if self.auto_start_service
                else "Service startup is DISABLED - do NOT include startup commands"
            )
            info_s["Deployment Info"] = deploy_info_copy

        return f"Additional Information:\n{pprint.pformat(info_s)}" if info_s else ""

    def _generate_failed_methods_context(self, failed_methods: List[MethodNode]) -> str:
        """
        Generate context string from failed method attempts.
        
        Args:
            failed_methods: List of failed method nodes
            
        Returns:
            Context string describing failed attempts
        """
        if not failed_methods:
            return ""

        context_lines = ["**PREVIOUS FAILED ATTEMPTS:**"]

        for i, method in enumerate(failed_methods, 1):
            context_lines.append(f"\nAttempt {i}: {method.name}")
            context_lines.append(f"Description: {method.description}")

            # Find verify and forward nodes
            verify_node = None
            forward_node = None
            for child in method.children:
                if isinstance(child, VerifyNode):
                    verify_node = child
                elif isinstance(child, ForwardNode):
                    forward_node = child

            # Describe what failed
            if verify_node and self.execution_status.get(verify_node.id) == ExecutionStatus.FAILED:
                context_lines.append("Failed at: Verification phase")
                # Get failed verification commands
                for cmd_node in verify_node.children:
                    if isinstance(cmd_node, CommandNode) and self.execution_status.get(
                            cmd_node.id) == ExecutionStatus.FAILED:
                        context_lines.append(f"  - Failed command: {cmd_node.name}")
                        if cmd_node.error:
                            context_lines.append(f"    Error: {cmd_node.error}")

            elif forward_node and self.execution_status.get(forward_node.id) == ExecutionStatus.FAILED:
                context_lines.append("Failed at: Execution phase")
                # Get failed execution commands
                for cmd_node in forward_node.children:
                    if isinstance(cmd_node, CommandNode) and self.execution_status.get(
                            cmd_node.id) == ExecutionStatus.FAILED:
                        context_lines.append(f"  - Failed command: {cmd_node.name}")
                        if cmd_node.error:
                            context_lines.append(f"    Error: {cmd_node.error}")

            context_lines.append("")

        context_lines.append("\n**IMPORTANT:** Learn from these failures and try a different approach.")

        return "\n".join(context_lines)

    async def generate_method_for_core_step(self, core_step_node: CoreStepNode,
                                            failed_methods: List[MethodNode] = None) -> MethodNode:
        """
        Generate a new method for a core step using LLM.

        Args:
            core_step_node: The core step to generate a method for
            failed_methods: List of previously failed method nodes

        Returns:
            A newly created method node
        """
        # Prepare core step data for LLM
        core_step_data = {
            "name": core_step_node.name,
            "description": core_step_node.description,
        }

        # Generate failed context if there are failed methods
        failed_context = ""
        if failed_methods:
            failed_context = self._generate_failed_methods_context(failed_methods)

        # Generate a single method using the new prompt
        method_data = await self.generate_single_method_for_step_async(
            core_step_data, self.addition_info_llm_format(), failed_context
        )

        if not method_data:
            raise ValueError(f"Could not generate method for core step {core_step_node.name}")

        # Create method node
        method_node = self.graph.add_method(
            parent_id=core_step_node.id,
            name=method_data.get("name", "Generated Method"),
            description=method_data.get("description", ""),
        )

        # Create verify node
        verify_node = self.graph.add_verify_node(
            parent_id=method_node.id,
            name=f"Verify dependencies for {method_node.name}",
            description="Check and install necessary software and dependencies",
        )

        # Create forward node
        forward_node = self.graph.add_forward_node(
            parent_id=method_node.id,
            name=f"Execute {method_node.name}",
            description="Main execution commands for this method",
        )

        # Add dependency checks to verify node
        required_software = method_data.get("required_software", [])
        for software in required_software:
            software_name = software.get("name", "Unknown Software")
            check_command = software.get(
                "check_command", f"command -v {software_name} >/dev/null 2>&1"
            )
            install_command = software.get("install_command", "")

            # Create LogicCommandNode for software check
            logic_node = self.graph.add_logic_command(
                parent_id=verify_node.id,
                name=f"Check if {software_name} is installed",
                command=check_command,
                description=f"Verify if {software_name} is available in the system",
                missing_info=False,
                interactive=False,
            )

            # Add true branch (software exists)
            true_branch = self.graph.add_logic_command_child(
                parent_logic_id=logic_node.id,
                name=f"Skip {software_name} installation (already installed)",
                command=None,
                description=f"{software_name} is already installed, no action needed",
                missing_info=False,
                interactive=False,
                is_command_node=True,
                is_true_branch=True,
            )

            # Add false branch (software missing)
            if install_command:
                false_branch = self.graph.add_logic_command_child(
                    parent_logic_id=logic_node.id,
                    name=f"Install {software_name}",
                    command=install_command,
                    description=f"Install {software_name} as it's not available",
                    missing_info=False,
                    interactive=False,
                    is_command_node=True,
                    is_true_branch=False,
                )
            else:
                false_branch = self.graph.add_logic_command_child(
                    parent_logic_id=logic_node.id,
                    name=f"No installation command available for {software_name}",
                    command=f"echo 'No installation command available for {software_name}'",
                    description="Warning that no installation command was provided",
                    missing_info=False,
                    interactive=False,
                    is_command_node=True,
                    is_true_branch=False,
                )

        # Generate commands for forward node
        commands_data = await self.generate_commands_for_method_async(
            method_data, self.addition_info_llm_format()
        )

        # Create command nodes in forward node
        for cmd_data in commands_data:
            self.graph.add_command(
                parent_id=forward_node.id,
                name=cmd_data.get("name", "Command"),
                command=cmd_data.get("command", ""),
                missing_info=cmd_data.get("missing_info", False),
                interactive=cmd_data.get("interactive", False),
                description=cmd_data.get("description", ""),
            )

        return method_node

    async def execute_core_step_reactive(self, core_step_node: CoreStepNode) -> bool:
        """
        Execute a core step in reactive mode, generating methods on-the-fly.

        Args:
            core_step_node: The core step node to execute

        Returns:
            True if any method executed successfully, False otherwise
        """
        self.graph.log_node(core_step_node, "Executing core step reactively")

        # Limit the number of method attempts to avoid infinite loops
        max_method_attempts = 3
        attempts = 0
        failed_methods = []  # Track failed methods for context

        while attempts < max_method_attempts:
            # Generate a new method for this core step
            logger.info(
                f"Generating method attempt {attempts + 1} for core step: {core_step_node.name}"
            )
            method_node = await self.generate_method_for_core_step(core_step_node, failed_methods)

            # Execute the method
            method_success = await self.execute_method(method_node)

            # If method succeeds, we're done with this core step
            if method_success:
                # Update core step status in graph
                self.graph.update_node_status(node_id=core_step_node.id, succeeded=True, error=None)

                self.execution_status[core_step_node.id] = ExecutionStatus.SUCCESS
                return True

            # Method failed, add to failed methods list
            failed_methods.append(method_node)
            attempts += 1
            logger.warning(
                f"Method attempt {attempts} failed for core step: {core_step_node.name}, "
                f"{'trying again' if attempts < max_method_attempts else 'no more attempts'}"
            )

        # If all method attempts failed, mark core step as failed
        logger.error(
            f"All {max_method_attempts} method attempts failed for core step: {core_step_node.name}"
        )

        # Update core step status in graph
        self.graph.update_node_status(
            node_id=core_step_node.id,
            succeeded=False,
            error=f"All {max_method_attempts} method attempts failed",
        )

        self.execution_status[core_step_node.id] = ExecutionStatus.FAILED
        return False

    def generate_execution_report(self) -> str:
        """
        Generate a human-readable report of the deployment execution.

        Returns:
            Report string
        """
        lines = [f"Deployment Execution Report: {self.graph.name}", "=" * 50, ""]

        def node_status_str(node_id: str) -> str:
            status = self.execution_status.get(node_id, ExecutionStatus.PENDING)
            if status == ExecutionStatus.SUCCESS:
                return "✓ SUCCESS"
            elif status == ExecutionStatus.FAILED:
                return "✗ FAILED"
            elif status == ExecutionStatus.SKIPPED:
                return "⟶ SKIPPED"
            elif status == ExecutionStatus.RUNNING:
                return "⟳ RUNNING"
            else:
                return "? PENDING"

        def add_node_to_report(node: Node, level: int = 0):
            indent = "  " * level
            status = node_status_str(node.id)
            lines.append(f"{indent}- [{status}] {node.name}")

            if node.description:
                lines.append(f"{indent}  Description: {node.description}")

            if isinstance(node, CommandNode) and node.command:
                lines.append(f"{indent}  Command: {node.command}")

            if node.error:
                lines.append(f"{indent}  Error: {node.error}")

            # Add children
            for child in node.children:
                add_node_to_report(child, level + 1)

        # Add nodes to report
        if self.graph and self.graph.root:
            add_node_to_report(self.graph.root)

        # Add summary statistics
        success_count = sum(
            1 for status in self.execution_status.values() if status == ExecutionStatus.SUCCESS
        )
        failed_count = sum(
            1 for status in self.execution_status.values() if status == ExecutionStatus.FAILED
        )
        skipped_count = sum(
            1 for status in self.execution_status.values() if status == ExecutionStatus.SKIPPED
        )

        lines.extend(
            [
                "",
                "Summary:",
                f"- Success: {success_count}",
                f"- Failed: {failed_count}",
                f"- Skipped: {skipped_count}",
                f"- Total: {len(self.execution_status)}",
            ]
        )

        return "\n".join(lines)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    def _track_verified_item(self, command_node: CommandNode, verified_items: List[str]):
        """
        Track a successfully verified software or dependency.
        
        Args:
            command_node: The command node that was successfully executed
            verified_items: List to append verified items to
        """
        # Extract software name from command node
        if "check" in command_node.name.lower() or "verify" in command_node.name.lower():
            # Try to extract software name from node name
            if "installed" in command_node.name.lower():
                # Pattern: "Check if X is installed"
                import re
                match = re.search(r'check if (.+?) is installed', command_node.name.lower())
                if match:
                    software_name = match.group(1).strip()
                    verified_items.append(software_name)
                    return

            # Fallback: use the command itself to infer software
            if command_node.command:
                # Common patterns for software verification
                command = command_node.command.lower()
                if "command -v" in command:
                    # Extract from "command -v software_name"
                    software = command.split("command -v")[1].split()[0].strip()
                    verified_items.append(software)
                elif "which" in command:
                    # Extract from "which software_name"
                    software = command.split("which")[1].split()[0].strip()
                    verified_items.append(software)
                elif "--version" in command:
                    # Extract from "software_name --version"
                    software = command.split("--version")[0].strip()
                    verified_items.append(software)
                elif "-v" in command and "echo" not in command:
                    # Extract from "software_name -v"
                    software = command.split("-v")[0].strip()
                    verified_items.append(software)
                else:
                    # Generic fallback: use the node name
                    verified_items.append(command_node.name)
            else:
                # No command, use node name
                verified_items.append(command_node.name)

    async def _track_cloned_repository(self, clone_command: str, repo_path: str):
        """
        Track information about a cloned repository.
        
        Args:
            clone_command: The git clone command that was executed
            repo_path: The path where the repository was cloned
        """
        try:
            # Extract repository URL from clone command
            import re
            url_match = re.search(r"git\s+clone\s+([^\s]+)", clone_command)
            if url_match:
                repo_url = url_match.group(1)
                
                # Simply track that this repository has been cloned
                if repo_url not in self.deploy_info["cloned_repositories"]:
                    self.deploy_info["cloned_repositories"].append(repo_url)
                    logger.info(f"Tracked cloned repository: {repo_url}")

        except Exception:
            logger.exception("Failed to track cloned repository")
    
    async def _update_git_status(self):
        """
        Update git status - simplified to do nothing since we only track basic clone info.
        """
        # This method is kept for compatibility but does nothing
        # since we only track whether repositories have been cloned
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if hasattr(self, "command_executor"):
            self.command_executor.close_session()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if hasattr(self, "command_executor"):
            self.command_executor.close_session()
