"""
脚本测试器 - 自动化脚本测试框架
验证生成的脚本能够正确执行项目功能
"""

import asyncio
import json
import os
import shlex
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from loguru import logger

from .environment_manager import create_environment_registry
from .script_generator import GeneratedScript


@dataclass
class TestResult:
    """测试结果"""
    test_name: str
    script_name: str
    success: bool
    output: str
    error: Optional[str]
    duration: float
    timestamp: str
    exit_code: Optional[int] = None
    timeout: bool = False
    retry_count: int = 0
    fix_history: List[str] = None

    def __post_init__(self):
        if self.fix_history is None:
            self.fix_history = []


@dataclass
class ScriptFixResult:
    """脚本修复结果"""
    success: bool
    fixed_script_content: Optional[str]
    fix_description: str
    error: Optional[str] = None
    llm_response: Optional[Dict[str, Any]] = None


@dataclass
class TestCaseFixResult:
    """测试用例修复结果"""
    success: bool
    fixed_test_cases: Optional[List[Dict[str, Any]]]
    fix_description: str
    error: Optional[str] = None
    llm_response: Optional[Dict[str, Any]] = None


@dataclass
class TestRetryInfo:
    """测试重试信息"""
    attempt_number: int
    original_error: str
    fix_applied: bool
    fix_description: Optional[str] = None
    test_result: Optional[TestResult] = None




@dataclass
class ScriptTestSuite:
    """脚本测试套件"""
    script_name: str
    script_path: str
    script_type: str
    test_cases: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class ScriptTester:
    """脚本测试器"""
    
    def __init__(self, max_workers: int = 3, default_timeout: int = 30, llm_provider=None):
        """
        初始化脚本测试器
        
        Args:
            max_workers: 最大并发测试数
            default_timeout: 默认超时时间（秒）
            llm_provider: LLM提供者实例（用于脚本修复）
        """
        self.max_workers = max_workers
        self.default_timeout = default_timeout
        self.test_results = []
        self.llm_provider = llm_provider
        
        # 初始化环境管理器
        self.environment_registry = create_environment_registry()
        
        # 从环境变量获取最大重试次数
        self.max_retry_attempts = int(os.getenv('AUTOAPI_MAX_RETRY_ATTEMPTS', '3'))
        
    async def test_scripts(self, scripts: List[GeneratedScript], 
                    parallel: bool = True) -> List[TestResult]:
        """
        测试脚本列表
        
        Args:
            scripts: 要测试的脚本列表
            parallel: 是否并行执行测试
            
        Returns:
            List[TestResult]: 测试结果列表
        """
        logger.info(f"开始测试 {len(scripts)} 个脚本")
        
        # 创建测试套件
        test_suites = []
        for script in scripts:
            test_suite = ScriptTestSuite(
                script_name=script.function_name,
                script_path=script.script_path,
                script_type=script.script_type,
                test_cases=script.test_cases,
                metadata=script.metadata
            )
            test_suites.append(test_suite)
        
        # 执行测试
        if parallel and len(test_suites) > 1:
            results = await self._parallel_test(test_suites)
        else:
            results = await self._sequential_test(test_suites)
        
        # 保存测试结果
        self.test_results.extend(results)
        
        logger.info(f"测试完成，成功率: {self._calculate_success_rate(results):.1%}")
        
        return results
    
    async def test_single_script(self, script: GeneratedScript) -> List[TestResult]:
        """
        测试单个脚本
        
        Args:
            script: 要测试的脚本
            
        Returns:
            List[TestResult]: 测试结果列表
        """
        test_suite = ScriptTestSuite(
            script_name=script.function_name,
            script_path=script.script_path,
            script_type=script.script_type,
            test_cases=script.test_cases,
            metadata=script.metadata
        )
        
        return await self._test_script_suite(test_suite)
    
    async def _parallel_test(self, test_suites: List[ScriptTestSuite]) -> List[TestResult]:
        """并行执行测试"""
        all_results = []
        
        # 创建异步任务列表
        tasks = []
        for suite in test_suites:
            task = asyncio.create_task(self._test_script_suite_with_timeout(suite))
            tasks.append(task)
        
        # 使用 gather 并行执行，返回结果
        try:
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results_list):
                suite = test_suites[i]
                if isinstance(result, Exception):
                    logger.error(f"脚本测试异常: {suite.script_name} - {result}")
                    error_result = TestResult(
                        test_name="error",
                        script_name=suite.script_name,
                        success=False,
                        output="",
                        error=str(result),
                        duration=0.0,
                        timestamp=datetime.now().isoformat()
                    )
                    all_results.append(error_result)
                else:
                    all_results.extend(result)
                    
        except Exception as e:
            logger.error(f"并行测试执行异常: {e}")
            # 为所有测试套件添加错误结果
            for suite in test_suites:
                error_result = TestResult(
                    test_name="error",
                    script_name=suite.script_name,
                    success=False,
                    output="",
                    error=f"并行执行异常: {str(e)}",
                    duration=0.0,
                    timestamp=datetime.now().isoformat()
                )
                all_results.append(error_result)
        
        return all_results
    
    async def _sequential_test(self, test_suites: List[ScriptTestSuite]) -> List[TestResult]:
        """顺序执行测试"""
        all_results = []
        
        for suite in test_suites:
            try:
                results = await self._test_script_suite(suite)
                all_results.extend(results)
            except Exception as e:
                logger.error(f"脚本测试失败: {suite.script_name} - {e}")
                error_result = TestResult(
                    test_name="error",
                    script_name=suite.script_name,
                    success=False,
                    output="",
                    error=str(e),
                    duration=0.0,
                    timestamp=datetime.now().isoformat()
                )
                all_results.append(error_result)
        
        return all_results
    
    async def _test_script_suite(self, test_suite: ScriptTestSuite) -> List[TestResult]:
        """测试单个脚本套件 - 集成重试机制"""
        logger.info(f"测试脚本: {test_suite.script_name}")

        # 如果有LLM提供者且启用重试，使用带重试的测试
        return await self._test_script_suite_with_retry(test_suite)

    async def _test_script_suite_with_timeout(self, test_suite: ScriptTestSuite, timeout_seconds: int = 300) -> List[TestResult]:
        """带超时的脚本测试套件"""
        try:
            # 使用 asyncio.wait_for 添加超时控制
            return await asyncio.wait_for(
                self._test_script_suite(test_suite), 
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            logger.error(f"脚本测试超时: {test_suite.script_name}")
            timeout_result = TestResult(
                test_name="timeout",
                script_name=test_suite.script_name,
                success=False,
                output="",
                error="测试套件执行超时",
                duration=float(timeout_seconds),
                timestamp=datetime.now().isoformat(),
                timeout=True
            )
            return [timeout_result]
        except Exception as e:
            logger.error(f"脚本测试异常: {test_suite.script_name} - {e}")
            error_result = TestResult(
                test_name="error",
                script_name=test_suite.script_name,
                success=False,
                output="",
                error=str(e),
                duration=0.0,
                timestamp=datetime.now().isoformat()
            )
            return [error_result]


    async def _test_script_suite_with_retry(self, test_suite: ScriptTestSuite) -> List[TestResult]:
        """带重试机制的脚本测试套件"""
        logger.info(f"带重试测试脚本: {test_suite.script_name} (最大重试次数: {self.max_retry_attempts})")

        results = []

        # 执行测试用例（带重试）
        for test_case in test_suite.test_cases:
            test_result = await self._execute_test_case_with_retry(test_suite, test_case)
            results.append(test_result)

            # 记录重试历史到结果中
            if test_result.retry_count > 0:
                logger.info(
                    f"测试用例 {test_result.test_name}: {'通过' if test_result.success else '失败'} (重试 {test_result.retry_count} 次)")
            else:
                logger.info(f"测试用例 {test_result.test_name}: {'通过' if test_result.success else '失败'}")

        return results

    async def _execute_test_case_with_retry(self, test_suite: ScriptTestSuite,
                                            test_case: Dict[str, Any]) -> TestResult:
        """执行单个测试用例（带重试机制）"""
        attempt = 0
        last_result = None
        retry_history = []

        while attempt <= self.max_retry_attempts:
            logger.debug(
                f"测试用例执行尝试 {attempt + 1}/{self.max_retry_attempts + 1}: {test_case.get('name', 'unknown_test')}")

            # 执行测试用例
            result = self._execute_test_case(test_suite, test_case)
            last_result = result

            # 如果测试成功或不应该重试，结束循环
            if result.success or not self._should_retry_test(result, attempt):
                break

            # 如果这不是最后一次尝试，使用LLM诊断决定修复策略
            if attempt < self.max_retry_attempts:
                logger.info(f"测试失败，开始LLM诊断 (尝试 {attempt + 1}/{self.max_retry_attempts})")

                # 1. LLM诊断失败原因
                recommendation, reason = await self._diagnose_failure_with_llm(test_suite, test_case, result)
                logger.info(f"LLM诊断建议: {recommendation} - {reason}")

                # 2. 根据LLM建议选择修复策略
                fix_applied = False
                fix_description = ""

                if recommendation == "fix_test_case":
                    # 修复测试用例
                    logger.info("执行测试用例修复")
                    test_case_fix_result = await self._fix_failed_test_case(test_suite, result, test_case, None)
                    
                    if test_case_fix_result.success and test_case_fix_result.fixed_test_cases:
                        fixed_test_case = test_case_fix_result.fixed_test_cases[0]
                        test_case.update(fixed_test_case)
                        fix_applied = True
                        fix_description = f"测试用例修复: {test_case_fix_result.fix_description}"
                        logger.info(f"修复成功: {fix_description}")
                    else:
                        logger.warning(f"测试用例修复失败: {test_case_fix_result.error}")
                        # 回退到脚本修复
                        script_fix_result = await self._fix_failed_script(test_suite, result, test_case, None)
                        if script_fix_result.success and self._apply_script_fix(test_suite, script_fix_result):
                            fix_applied = True
                            fix_description = f"回退脚本修复: {script_fix_result.fix_description}"
                            logger.info(f"回退修复成功: {fix_description}")

                elif recommendation == "fix_script":
                    # 修复脚本
                    logger.info("执行脚本修复")
                    script_fix_result = await self._fix_failed_script(test_suite, result, test_case, None)
                    
                    if script_fix_result.success and self._apply_script_fix(test_suite, script_fix_result):
                        fix_applied = True
                        fix_description = f"脚本修复: {script_fix_result.fix_description}"
                        logger.info(f"修复成功: {fix_description}")
                    else:
                        logger.warning(f"脚本修复失败: {script_fix_result.error}")

                else:
                    # 其他情况默认尝试测试用例修复
                    logger.info("默认尝试测试用例修复")
                    test_case_fix_result = await self._fix_failed_test_case(test_suite, result, test_case, None)
                    
                    if test_case_fix_result.success and test_case_fix_result.fixed_test_cases:
                        fixed_test_case = test_case_fix_result.fixed_test_cases[0]
                        test_case.update(fixed_test_case)
                        fix_applied = True
                        fix_description = f"默认测试用例修复: {test_case_fix_result.fix_description}"
                        logger.info(f"修复成功: {fix_description}")

                # 记录重试信息
                retry_history.append(f"尝试{attempt + 1}: {fix_description or '修复失败'}")

                # 如果没有成功应用修复，退出重试循环
                if not fix_applied:
                    logger.warning(f"修复失败，退出重试循环")
                    break

            attempt += 1

        # 设置最终结果的重试信息
        if last_result:
            last_result.retry_count = attempt
            last_result.fix_history = retry_history

            # 简单记录重试总结
            if attempt > 1:
                logger.info(
                    f"测试重试总结: 共{attempt}次尝试, 最终结果: {'success' if last_result.success else 'failed'}")

        return last_result or TestResult(
            test_name=test_case.get('name', 'unknown_test'),
            script_name=test_suite.script_name,
            success=False,
            output="",
            error="测试执行异常",
            duration=0.0,
            timestamp=datetime.now().isoformat(),
            retry_count=attempt,
            fix_history=retry_history
        )
    
    def _check_script_syntax(self, test_suite: ScriptTestSuite) -> Optional[TestResult]:
        """检查脚本语法 - 使用环境管理器在正确环境中检查"""
        start_time = time.time()
        
        try:
            # 获取项目路径
            project_path = test_suite.metadata.get('project_path', str(Path(test_suite.script_path).parent))
            
            # 检测执行环境
            env_info = self.environment_registry.detect_best_environment(project_path, test_suite.metadata)
            logger.debug(f"语法检查使用环境: {env_info.env_type}")
            
            if test_suite.script_type == 'python':
                # Python语法检查 - 使用环境管理器
                base_command = f"python -m py_compile {shlex.quote(test_suite.script_path)}"
                final_command = self.environment_registry.get_execution_command(env_info, base_command)
                
                result = subprocess.run(
                    final_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                success = result.returncode == 0
                error = result.stderr
                
            elif test_suite.script_type == 'shell':
                # Shell语法检查
                result = subprocess.run(
                    ['bash', '-n', test_suite.script_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                success = result.returncode == 0
                error = result.stderr
                
            elif test_suite.script_type == 'node':
                # Node.js语法检查
                result = subprocess.run(
                    ['node', '--check', test_suite.script_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                success = result.returncode == 0
                error = result.stderr
                
            else:
                # 不支持的类型，跳过语法检查
                return None
            
            duration = time.time() - start_time
            
            return TestResult(
                test_name="syntax_check",
                script_name=test_suite.script_name,
                success=success,
                output="语法检查通过" if success else "",
                error=error,
                duration=duration,
                timestamp=datetime.now().isoformat(),
                exit_code=result.returncode
            )
            
        except subprocess.TimeoutExpired:
            return TestResult(
                test_name="syntax_check",
                script_name=test_suite.script_name,
                success=False,
                output="",
                error="语法检查超时",
                duration=time.time() - start_time,
                timestamp=datetime.now().isoformat(),
                timeout=True
            )
        except Exception as e:
            return TestResult(
                test_name="syntax_check",
                script_name=test_suite.script_name,
                success=False,
                output="",
                error=f"语法检查异常: {str(e)}",
                duration=time.time() - start_time,
                timestamp=datetime.now().isoformat()
            )
    
    def _execute_test_case(self, test_suite: ScriptTestSuite, 
                          test_case: Dict[str, Any]) -> TestResult:
        """执行单个测试用例 - 确保在正确环境中执行"""
        test_name = test_case.get('name', 'unknown_test')
        timeout = test_case.get('timeout', self.default_timeout)
        
        start_time = time.time()
        
        try:
            # 直接使用测试用例中预生成的命令
            command = test_case.get('command')

            # 安全解析工作目录
            project_path = self._resolve_safe_working_directory(test_suite)
            

            logger.debug(f"执行测试命令: {command}")
            
            # 执行命令
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=project_path
            )
            
            duration = time.time() - start_time
            
            # 判断测试是否成功
            success = self._evaluate_test_result(result, test_case)
            
            return TestResult(
                test_name=test_name,
                script_name=test_suite.script_name,
                success=success,
                output=result.stdout,
                error=result.stderr if result.stderr else None,
                duration=duration,
                timestamp=datetime.now().isoformat(),
                exit_code=result.returncode
            )
            
        except subprocess.TimeoutExpired:
            return TestResult(
                test_name=test_name,
                script_name=test_suite.script_name,
                success=False,
                output="",
                error=f"测试执行超时 ({timeout}秒)",
                duration=time.time() - start_time,
                timestamp=datetime.now().isoformat(),
                timeout=True
            )
        except Exception as e:
            return TestResult(
                test_name=test_name,
                script_name=test_suite.script_name,
                success=False,
                output="",
                error=f"测试执行异常: {str(e)}",
                duration=time.time() - start_time,
                timestamp=datetime.now().isoformat()
            )
    
    def _resolve_safe_working_directory(self, test_suite: ScriptTestSuite) -> str:
        """安全解析测试工作目录，处理虚拟路径和不存在的路径"""
        # 获取原始项目路径
        original_path = test_suite.metadata.get('project_path', str(Path.cwd().resolve()))
        
        # 检测虚拟路径
        if self._is_virtual_path(original_path):
            fallback_path = Path.cwd().resolve()
            logger.warning(f"检测到虚拟路径 {original_path}，使用当前目录作为工作目录: {fallback_path}")
            return str(fallback_path)
        
        # 尝试解析路径
        try:
            resolved_path = Path(original_path).resolve()
            if resolved_path.exists() and resolved_path.is_dir():
                logger.debug(f"使用项目路径作为工作目录: {resolved_path}")
                return str(resolved_path)
            else:
                fallback_path = Path.cwd().resolve()
                logger.warning(f"项目路径不存在或不是目录 {resolved_path}，使用当前目录: {fallback_path}")
                return str(fallback_path)
        except Exception as e:
            fallback_path = Path.cwd().resolve()
            logger.error(f"路径解析失败 {original_path}: {e}，使用当前目录: {fallback_path}")
            return str(fallback_path)
    
    def _is_virtual_path(self, path: str) -> bool:
        """检测是否为虚拟路径"""
        if not path:
            return False
        # 检测虚拟路径格式：N/A:project-name 或包含冒号但不是绝对路径
        return path.startswith("N/A:") or (":" in path and not os.path.isabs(path))
    
    def _evaluate_test_result(self, result: subprocess.CompletedProcess, 
                            test_case: Dict[str, Any]) -> bool:
        """评估测试结果是否成功 - 支持正样本和负样本测试用例"""
        
        # 获取预期行为（默认为success，保持向后兼容）
        expected_behavior = test_case.get('expected_behavior', 'success')
        
        # 第一步：根据预期行为验证退出码
        if expected_behavior == 'success':
            # 正样本测试：预期成功执行（退出码应该为0）
            if result.returncode != 0:
                logger.debug(f"正样本测试失败：期望退出码0，实际{result.returncode}")
                return False
                
        elif expected_behavior == 'error':
            # 负样本测试：预期执行失败（退出码应该非0）
            if result.returncode == 0:
                logger.debug(f"负样本测试失败：期望退出码非0，实际{result.returncode}")
                return False
                
        elif expected_behavior == 'warning':
            # 警告测试：预期成功但有警告信息
            if result.returncode != 0:
                logger.debug(f"警告测试失败：期望退出码0，实际{result.returncode}")
                return False
            # 检查是否有stderr输出（警告信息）
            if not result.stderr or not result.stderr.strip():
                logger.debug("警告测试失败：期望有警告信息，但stderr为空")
                return False
                
        else:
            logger.warning(f"未知的expected_behavior: {expected_behavior}，按success处理")
            if result.returncode != 0:
                return False
        
        # 第二步：验证输出内容（如果退出码验证通过）
        expected_output_type = test_case.get('expected_output_type', 'any')
        
        if expected_output_type == 'json':
            # 期望JSON格式输出
            try:
                json.loads(result.stdout)
                logger.debug("JSON格式验证通过")
                return True
            except json.JSONDecodeError:
                logger.debug("JSON格式验证失败")
                return False
                
        elif expected_output_type == 'non_empty':
            # 期望非空输出
            has_output = bool(result.stdout.strip())
            logger.debug(f"非空输出验证：{has_output}")
            return has_output
            
        elif expected_output_type == 'contains':
            # 期望输出包含特定内容
            expected_content = test_case.get('expected_content', '')
            contains_content = expected_content in result.stdout
            logger.debug(f"内容包含验证（期望包含'{expected_content}'）：{contains_content}")
            return contains_content
            
        elif expected_output_type == 'empty':
            # 期望空输出
            is_empty = not result.stdout.strip()
            logger.debug(f"空输出验证：{is_empty}")
            return is_empty
            
        elif expected_output_type == 'error_message':
            # 期望错误信息（通常在stderr中）
            has_error_message = bool(result.stderr.strip())
            logger.debug(f"错误信息验证：{has_error_message}")
            return has_error_message
            
        else:
            # 默认情况：已通过退出码验证，直接认为成功
            logger.debug(f"使用默认验证策略，退出码验证已通过")
            return True

    async def _fix_failed_script(self, test_suite: ScriptTestSuite,
                                 failed_result: TestResult,
                                 test_case: Optional[Dict[str, Any]] = None,
                                 diagnosis: Optional[str] = None) -> ScriptFixResult:
        """使用LLM修复失败的脚本"""
        try:
            logger.info(f"开始LLM修复脚本: {test_suite.script_name}")

            # 检查是否有LLM提供者
            if not self.llm_provider:
                return ScriptFixResult(
                    success=False,
                    fixed_script_content=None,
                    fix_description="LLM提供者未配置",
                    error="无法修复脚本：LLM提供者未配置"
                )

            # 读取当前脚本内容
            try:
                with open(test_suite.script_path, 'r', encoding='utf-8') as f:
                    script_content = f.read()
            except Exception as e:
                return ScriptFixResult(
                    success=False,
                    fixed_script_content=None,
                    fix_description="无法读取脚本文件",
                    error=f"读取脚本失败: {str(e)}"
                )

            # 构建修复提示词
            from .prompts import SCRIPT_FIX_PROMPT

            # 构建额外的上下文信息
            additional_context = ""
            if test_case:
                additional_context += f"\n**Failed Test Case Context:**\n```json\n{test_case}\n```\n"
            
            if diagnosis:
                additional_context += f"\n**Diagnosis Notes:**\n{diagnosis}\n"

            prompt = SCRIPT_FIX_PROMPT.format(
                script_name=test_suite.script_name,
                script_type=test_suite.script_type,
                function_description=test_suite.metadata.get('description', 'Unknown function'),
                script_content=script_content,
                test_name=failed_result.test_name,
                error_output=failed_result.error or "No error output",
                exit_code=failed_result.exit_code or "Unknown",
                timeout=str(failed_result.timeout),
                project_path=test_suite.metadata.get('project_path', 'Unknown'),
                additional_context=additional_context
            )

            # 调用LLM修复脚本
            logger.debug(f"发送LLM修复请求")
            response = await self.llm_provider.generate_completion_async(
                system_prompt="You are an expert script debugger and fixer. Analyze the failed script and provide a fixed version.",
                user_prompt=prompt,
                model='claude-sonnet-4-20250514',
                max_tokens=8000,
                json_format=True
            )

            if not response:
                return ScriptFixResult(
                    success=False,
                    fixed_script_content=None,
                    fix_description="LLM响应为空",
                    error="LLM未返回有效响应"
                )

            # 验证LLM响应格式
            fixed_content = response.get('fixed_script_content')
            fix_description = response.get('fix_description', 'LLM修复脚本')

            if not fixed_content:
                return ScriptFixResult(
                    success=False,
                    fixed_script_content=None,
                    fix_description="LLM响应格式无效",
                    error="LLM未返回修复后的脚本内容",
                    llm_response=response
                )

            logger.info(f"LLM脚本修复成功: {fix_description}")

            return ScriptFixResult(
                success=True,
                fixed_script_content=fixed_content,
                fix_description=fix_description,
                llm_response=response
            )

        except Exception as e:
            logger.error(f"LLM脚本修复失败: {e}")
            return ScriptFixResult(
                success=False,
                fixed_script_content=None,
                fix_description="修复过程异常",
                error=f"LLM修复异常: {str(e)}"
            )

    async def _fix_failed_test_case(self, test_suite: ScriptTestSuite,
                                   failed_result: TestResult,
                                   original_test_case: Dict[str, Any],
                                    diagnosis: Optional[str] = None) -> TestCaseFixResult:
        """使用LLM修复失败的测试用例"""
        try:
            logger.info(f"开始LLM修复测试用例: {failed_result.test_name}")

            # 检查是否有LLM提供者
            if not self.llm_provider:
                return TestCaseFixResult(
                    success=False,
                    fixed_test_cases=None,
                    fix_description="LLM提供者未配置",
                    error="无法修复测试用例：LLM提供者未配置"
                )

            # 读取脚本内容用于上下文
            try:
                with open(test_suite.script_path, 'r', encoding='utf-8') as f:
                    script_content = f.read()
            except Exception as e:
                logger.warning(f"无法读取脚本内容: {e}")
                script_content = "无法读取脚本内容"

            # 构建测试用例修复提示词
            from .prompts import TEST_CASE_FIX_PROMPT

            # 构建项目文件信息
            project_path = test_suite.metadata.get('project_path', str(Path.cwd().resolve()))
            try:
                available_files = self._get_available_project_files(project_path)
            except Exception as e:
                logger.warning(f"无法获取项目文件列表: {e}")
                available_files = "无法获取项目文件列表"

            prompt = TEST_CASE_FIX_PROMPT.format(
                script_name=test_suite.script_name,
                script_type=test_suite.script_type,
                function_description=test_suite.metadata.get('description', 'Unknown function'),
                script_content=script_content,
                original_test_case=str(original_test_case),
                test_name=failed_result.test_name,
                error_output=failed_result.error or "No error output",
                stdout_output=failed_result.output or "No stdout output", 
                exit_code=failed_result.exit_code or "Unknown",
                timeout=str(failed_result.timeout),
                project_path=project_path,
                available_files=available_files,
                diagnosis_info=diagnosis or 'No diagnosis available'
            )

            # 调用LLM修复测试用例
            logger.debug(f"发送LLM测试用例修复请求")
            response = await self.llm_provider.generate_completion_async(
                system_prompt="You are an expert test case designer and fixer. Analyze the failed test case and provide fixed versions.",
                user_prompt=prompt,
                model='claude-sonnet-4-20250514',
                max_tokens=8000,
                json_format=True
            )

            if not response:
                return TestCaseFixResult(
                    success=False,
                    fixed_test_cases=None,
                    fix_description="LLM响应为空",
                    error="LLM未返回有效响应"
                )

            # 验证LLM响应格式
            fixed_test_cases = response.get('fixed_test_cases')
            fix_description = response.get('fix_description', 'LLM修复测试用例')

            if not fixed_test_cases or not isinstance(fixed_test_cases, list):
                return TestCaseFixResult(
                    success=False,
                    fixed_test_cases=None,
                    fix_description="LLM响应格式无效",
                    error="LLM未返回有效的测试用例列表",
                    llm_response=response
                )

            logger.info(f"LLM测试用例修复成功: {fix_description}")

            return TestCaseFixResult(
                success=True,
                fixed_test_cases=fixed_test_cases,
                fix_description=fix_description,
                llm_response=response
            )

        except Exception as e:
            logger.error(f"LLM测试用例修复失败: {e}")
            return TestCaseFixResult(
                success=False,
                fixed_test_cases=None,
                fix_description="修复过程异常",
                error=f"LLM修复异常: {str(e)}"
            )

    def _get_available_project_files(self, project_path: str, max_files: int = 20) -> str:
        """获取项目中可用的文件列表用于测试用例修复"""
        try:
            project_path = Path(project_path).resolve()
            files_info = []
            
            # 常用的测试文件扩展名
            test_extensions = {'.pdf', '.txt', '.md', '.json', '.csv', '.xml', '.yml', '.yaml', '.ini', '.log'}
            
            # 遍历项目目录，查找测试相关文件
            file_count = 0
            for file_path in project_path.rglob('*'):
                if file_count >= max_files:
                    break
                    
                if file_path.is_file() and file_path.suffix.lower() in test_extensions:
                    try:
                        # 获取相对路径
                        rel_path = file_path.relative_to(project_path)
                        file_size = file_path.stat().st_size
                        
                        files_info.append({
                            'path': str(rel_path),
                            'size': file_size,
                            'extension': file_path.suffix.lower(),
                            'exists': True
                        })
                        file_count += 1
                    except Exception as e:
                        logger.debug(f"跳过文件 {file_path}: {e}")
                        continue
            
            if not files_info:
                return "未找到合适的测试文件"
                
            # 格式化文件信息
            files_text = "可用的项目文件:\n"
            for file_info in files_info:
                files_text += f"- {file_info['path']} ({file_info['size']} bytes, {file_info['extension']})\n"
                
            return files_text
            
        except Exception as e:
            logger.error(f"获取项目文件列表失败: {e}")
            return f"获取文件列表失败: {str(e)}"

    def _apply_script_fix(self, test_suite: ScriptTestSuite,
                          fix_result: ScriptFixResult) -> bool:
        """应用脚本修复，替换原脚本文件"""
        try:
            if not fix_result.success or not fix_result.fixed_script_content:
                return False

            # 备份原脚本
            backup_path = f"{test_suite.script_path}.backup"
            try:
                import shutil
                shutil.copy2(test_suite.script_path, backup_path)
                logger.debug(f"原脚本已备份到: {backup_path}")
            except Exception as e:
                logger.warning(f"备份原脚本失败: {e}")

            # 写入修复后的脚本
            with open(test_suite.script_path, 'w', encoding='utf-8') as f:
                f.write(fix_result.fixed_script_content)

            # 设置执行权限（Unix系统）
            if os.name == 'posix':
                os.chmod(test_suite.script_path, 0o755)

            logger.info(f"已应用脚本修复: {test_suite.script_path}")
            return True

        except Exception as e:
            logger.error(f"应用脚本修复失败: {e}")
            return False

    def _should_retry_test(self, result: TestResult, attempt: int) -> bool:
        """判断是否应该重试测试"""
        # 达到最大重试次数
        if attempt >= self.max_retry_attempts:
            return False

        # 如果测试成功，不需要重试
        if result.success:
            return False

        # 语法错误不重试（通常LLM也难以修复）
        if result.test_name == "syntax_check":
            logger.debug(f"语法错误不重试: {result.script_name}")
            return False

        # 文件不存在不重试
        if result.test_name == "file_existence":
            logger.debug(f"文件不存在不重试: {result.script_name}")
            return False

        # 超时可能是逻辑问题，可以重试
        # 其他执行错误都可以重试
        return True

    async def _diagnose_failure_with_llm(self, test_suite: ScriptTestSuite,
                                         test_case: Dict[str, Any],
                                         result: TestResult) -> tuple[str, str]:
        """使用LLM诊断测试失败原因，返回修复建议和原因"""
        try:
            error_output = result.error or ""
            stdout_output = result.output or ""
            exit_code = result.exit_code or 0
            command = test_case.get('command', '')

            prompt = f"""分析这个脚本测试失败的原因并给出明确的修复建议。

**测试命令:** {command}
**退出码:** {exit_code}
**标准输出:** {stdout_output[:500]}
**错误输出:** {error_output[:500]}

请分析失败原因并给出建议：
- 如果是参数错误、文件路径问题、命令格式错误等测试用例问题，建议"fix_test_case"
- 如果是脚本语法错误、导入错误、逻辑错误等脚本问题，建议"fix_script"

返回JSON格式：{{"recommendation": "fix_test_case或fix_script", "reason": "简洁的原因说明"}}"""

            response = await self.llm_provider.generate_completion_async(
                system_prompt="你是测试诊断专家。分析错误信息，给出fix_test_case或fix_script的明确建议。",
                user_prompt=prompt,
                json_format=True,
                model='claude-sonnet-4-20250514',
                max_tokens=500
            )

            if response and "recommendation" in response:
                recommendation = response.get("recommendation", "fix_test_case")
                reason = response.get("reason", "未知原因")
                return recommendation, reason
            else:
                return "fix_test_case", "LLM诊断失败，默认修复测试用例"

        except Exception as e:
            logger.error(f"LLM诊断失败: {e}")
            return "fix_test_case", "诊断异常，默认修复测试用例"
    
    
    
    def _command_has_environment_activation(self, command: str, env_info) -> bool:
        """检查命令是否已经包含环境激活"""
        if not command:
            return False
        
        # 检查各种环境激活模式
        env_patterns = {
            'conda': ['conda run', 'conda activate'],
            'uv': ['uv run'],
            'poetry': ['poetry run'],
            'venv': ['source ', 'activate']
        }
        
        env_type = env_info.env_type if hasattr(env_info, 'env_type') else 'system'
        patterns = env_patterns.get(env_type, [])
        
        return any(pattern in command for pattern in patterns)

    def _calculate_success_rate(self, results: List[TestResult]) -> float:
        """计算测试成功率"""
        if not results:
            return 0.0
        
        successful = sum(1 for result in results if result.success)
        return successful / len(results)
    

    def get_test_summary(self) -> Dict[str, Any]:
        """获取测试摘要"""
        if not self.test_results:
            return {'message': '暂无测试结果'}
        
        return {
            'total_tests': len(self.test_results),
            'successful_tests': sum(1 for r in self.test_results if r.success),
            'failed_tests': sum(1 for r in self.test_results if not r.success),
            'success_rate': self._calculate_success_rate(self.test_results),
            'last_test_time': max(r.timestamp for r in self.test_results)
        }


# 工厂函数
def create_script_tester(max_workers: int = 3, default_timeout: int = 30, llm_provider=None) -> ScriptTester:
    """
    创建脚本测试器实例
    
    Args:
        max_workers: 最大并发测试数
        default_timeout: 默认超时时间（秒）
        llm_provider: LLM提供者实例（用于脚本修复）
        
    Returns:
        ScriptTester: 脚本测试器实例
    """
    return ScriptTester(max_workers, default_timeout, llm_provider)