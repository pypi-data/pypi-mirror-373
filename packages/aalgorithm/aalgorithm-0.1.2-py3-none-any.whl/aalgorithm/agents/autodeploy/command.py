"""
Command execution module with multiple backend support.

This module provides classes for executing commands through different backends:
- iTerm2 using AppleScript integration
- Subprocess with persistent session support

All executors share a common interface through the base CommandExecutor class.
"""

import asyncio
import os
import re
import subprocess
import threading
import time
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, List, Tuple

import psutil
from loguru import logger

from aalgorithm.llm import LLMProvider  # Import LLMProvider for LLM analysis

# Initialize LLM provider
llm_provider = LLMProvider()


class CommandResult:
    """Result of executing a command."""

    def __init__(
            self,
            success: Optional[bool],
            output: str,
            error: Optional[str] = None,
            exit_code: Optional[int] = 0,
    ):
        self.success = success
        self.output = output
        self.error = error
        self.exit_code = exit_code

    def __repr__(self) -> str:
        return f"<CommandResult success={self.success} exit_code={self.exit_code}>"


class CommandExecutor(ABC):
    """
    Abstract base class for command executors.

    Provides common interface and shared functionality for different command execution backends.
    """

    def __init__(self, working_dir: Optional[str] = None, env: Optional[Dict[str, str]] = None):
        """
        Initialize the command executor.

        Args:
            working_dir: Working directory for command execution
            env: Environment variables for command execution
        """
        working_dir_obj = Path(working_dir) if working_dir else Path(os.getcwd())
        if not working_dir_obj.is_absolute():
            self.working_dir = str(working_dir_obj.resolve())
        else:
            self.working_dir = str(working_dir_obj)
        self.env = env or os.environ.copy()

        # Session management
        self._session_initialized = False

    @abstractmethod
    def _ensure_session_initialized(self):
        """Ensure the session is initialized. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def _initialize_session(self):
        """Initialize the session. Must be implemented by subclasses."""
        pass

    @abstractmethod
    async def execute_command_async(self, command: str, timeout: int = 600) -> CommandResult:
        """Execute a command asynchronously. Must be implemented by subclasses."""
        pass

    def execute_command(self, command: str, timeout: int = 600) -> CommandResult | None:
        """
        Execute a command and capture the result (synchronous wrapper).

        Args:
            command: Shell command to execute
            timeout: Maximum time to wait for command completion in seconds

        Returns:
            CommandResult object with execution results
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures

                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(self.execute_command_async(command, timeout))
                    finally:
                        new_loop.close()

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    return future.result()
            else:
                return loop.run_until_complete(self.execute_command_async(command, timeout))
        except RuntimeError:
            return asyncio.run(self.execute_command_async(command, timeout))

    @staticmethod
    async def _parse_command_output(output: str, command: str) -> Tuple[bool, int, Optional[str]]:
        """
        Parse command output to determine success, exit code, and errors using LLM.

        Args:
            output: Raw output from command execution
            command: Original command that was executed

        Returns:
            Tuple of (success, exit_code, error_message)
        """
        system_prompt = """
        You are an expert system administrator analyzing command execution results.
        Determine if a shell command executed successfully based on its output.
        Respond with a JSON containing: 
        - "success": boolean indicating if the command succeeded
        - "exit_code": integer (0 for success, non-zero for failure)
        - "error_message": string with error details if failed, null if succeeded
        """

        user_prompt = f"""
        Command: {command}
        
        Output:
        ```
        {output}
        ```
        
        Analyze the command output and determine if it executed successfully.
        Look for error messages, success indicators, and standard patterns.
        Common error indicators include: "command not found", "permission denied", 
        "no such file or directory", "error:", "failed", "exception", "traceback".
        Common success indicators include: "successfully", "complete", "done", 
        "installed", "finished".
        
        For ambiguous cases, assume success if there's no clear error.
        """

        try:
            result = await llm_provider.generate_completion_async(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0,
                json_format=True,
            )

            success = result.get("success", True)
            exit_code = result.get("exit_code", 0)
            error_message = result.get("error_message", None)

            logger.debug(f"LLM analysis: success={success}, exit_code={exit_code}")
            return success, exit_code, error_message

        except Exception as e:
            logger.warning(f"LLM analysis failed: {e}. Falling back to default judgment.")

            # Fallback to simple heuristic
            has_error_indicator = any(
                indicator in output.lower()
                for indicator in ["error:", "failed", "exception", "not found", "denied"]
            )

            if has_error_indicator:
                return False, 1, output
            else:
                return True, 0, None

    @staticmethod
    def complete_missing_info_command(command: str) -> str:
        """
        Complete a command that requires missing information from user.

        Args:
            command: Command with missing info wrapped in <>

        Returns:
            Completed command with user input filled in
        """
        safe_command = command.replace("{", "{{").replace("}", "}}")
        logger.info(f"Completing command with missing info: {safe_command}")

        try:
            rep = re.compile(r"<(.*?)>")
            params = rep.findall(command)

            if params:
                for param in params:
                    value = os.getenv(param, "")
                    if not value:
                        value = input(f"Please provide value for {param}: ")
                    command = command.replace(f"<{param}>", value)
            else:
                logger.warning("No missing parameters found in command, executing as is.")
            return command
        except Exception as e:
            logger.exception(f"Exception while completing missing info command: {e}")
            return command

    # Abstract methods that subclasses should implement
    @abstractmethod
    async def execute_interactive_command_async(
            self,
            command: str,
            timeout: int = 600,
            expected_prompts: Optional[List[str]] = None,
            responses: Optional[List[str]] = None,
    ) -> CommandResult:
        """Execute an interactive command asynchronously."""
        pass

    @abstractmethod
    async def send_input_async(self, text: str):
        """Send input to the session asynchronously."""
        pass

    @abstractmethod
    async def read_terminal_output_async(self, lines: int = 10) -> str:
        """Read terminal output asynchronously."""
        pass

    @abstractmethod
    async def close_session_async(self):
        """Close the session asynchronously."""
        pass

    # Synchronous wrapper methods
    def execute_interactive_command(
            self,
            command: str,
            timeout: int = 600,
            expected_prompts: Optional[List[str]] = None,
            responses: Optional[List[str]] = None,
    ) -> CommandResult | None:
        """Execute an interactive command (synchronous wrapper)."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures

                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(
                            self.execute_interactive_command_async(command, timeout, expected_prompts, responses)
                        )
                    finally:
                        new_loop.close()

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    return future.result()
            else:
                return loop.run_until_complete(
                    self.execute_interactive_command_async(command, timeout, expected_prompts, responses)
                )
        except RuntimeError:
            return asyncio.run(
                self.execute_interactive_command_async(command, timeout, expected_prompts, responses)
            )

    def send_input(self, text: str):
        """Send input to the session (synchronous wrapper)."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures

                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(self.send_input_async(text))
                    finally:
                        new_loop.close()

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    return future.result()
            else:
                return loop.run_until_complete(self.send_input_async(text))
        except RuntimeError:
            asyncio.run(self.send_input_async(text))

    def read_terminal_output(self, lines: int = 10) -> str | None:
        """Read terminal output (synchronous wrapper)."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures

                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(self.read_terminal_output_async(lines))
                    finally:
                        new_loop.close()

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    return future.result()
            else:
                return loop.run_until_complete(self.read_terminal_output_async(lines))
        except RuntimeError:
            return asyncio.run(self.read_terminal_output_async(lines))

    def close_session(self):
        """Close the session (synchronous wrapper)."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures

                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(self.close_session_async())
                    finally:
                        new_loop.close()

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    return future.result()
            else:
                return loop.run_until_complete(self.close_session_async())
        except RuntimeError:
            asyncio.run(self.close_session_async())

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_session()


class ItermCommandExecutor(CommandExecutor):
    """
    Command executor that uses direct iTerm2 AppleScript integration for command execution.

    This class manages iTerm2 sessions through AppleScript and provides methods
    for executing both regular and interactive commands.
    """

    def __init__(self, working_dir: Optional[str] = None, env: Optional[Dict[str, str]] = None):
        """Initialize the iTerm2 command executor."""
        super().__init__(working_dir, env)

        # iTerm2 control properties
        self.shell_names = {"bash", "zsh", "sh", "fish", "csh", "tcsh"}
        self.repl_names = {
            "irb", "pry", "rails", "node", "python", "ipython", "scala",
            "ghci", "iex", "lein", "clj", "julia", "R", "php", "lua"
        }

    def _ensure_session_initialized(self):
        """Ensure the iTerm2 session is initialized with proper working directory and environment."""
        if not self._session_initialized:
            self._initialize_session()
            self._session_initialized = True

    def _initialize_session(self):
        """Initialize the iTerm2 session with working directory and environment."""
        try:
            # Change to working directory
            self._execute_applescript_command(f"cd '{self.working_dir}'")
            logger.info(f"Changed directory to: {self.working_dir}")

            # Set environment variables if needed
            for key, value in self.env.items():
                if key not in os.environ or os.environ[key] != value:
                    self._execute_applescript_command(f"export {key}='{value}'")

            logger.info("Initialized iTerm2 session")

        except Exception as e:
            logger.warning(f"Failed to fully initialize session: {e}")

    def _escape_for_applescript(self, text: str) -> str:
        """Escape text for AppleScript."""
        if "\n" in text:
            return self._prepare_multiline_command(text)

        # For single line commands, we need to escape quotes properly
        # AppleScript uses backslash escaping for quotes within strings
        escaped_text = text.replace('\\', '\\\\')  # Escape backslashes first
        escaped_text = escaped_text.replace('"', '\\"')  # Escape double quotes

        return escaped_text

    def _prepare_multiline_command(self, text: str) -> str:
        """Prepare multiline text for AppleScript."""
        lines = text.split("\n")

        # Create AppleScript string concatenation
        applescript_string = f'"{self._escape_applescript_string(lines[0])}"'

        for line in lines[1:]:
            applescript_string += f' & return & "{self._escape_applescript_string(line)}"'

        return applescript_string

    def _escape_applescript_string(self, text: str) -> str:
        """Escape a single line for AppleScript string."""
        # Escape backslashes first, then quotes
        escaped = text.replace('\\', '\\\\')
        escaped = escaped.replace('"', '\\"')
        escaped = escaped.replace('\t', '\\t')
        return escaped

    def _execute_applescript_command(self, command: str) -> str:
        """
        Execute a command in iTerm2 using AppleScript.

        Args:
            command: The command to execute

        Returns:
            Terminal output after command execution
        """
        try:
            if "\n" in command:
                # Multiline command
                escaped_command = self._prepare_multiline_command(command)
                applescript = f"""
                tell application "iTerm2"
                    tell current session of current window
                        write text ({escaped_command})
                    end tell
                end tell
                """
            else:
                # Single line command - escape and wrap in quotes
                escaped_command = self._escape_for_applescript(command)
                applescript = f"""
                tell application "iTerm2"
                    tell current session of current window
                        write text "{escaped_command}"
                    end tell
                end tell
                """

            subprocess.run(["osascript", "-e", applescript], check=True)

            # Wait for command to complete
            while self._is_processing():
                time.sleep(0.1)

            # Wait for user input state
            tty_path = self._get_tty_path()
            while not self._is_waiting_for_user_input(tty_path):
                time.sleep(0.1)

            time.sleep(0.2)  # Small delay for output to settle

            return self._read_terminal_output(command=command)

        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to execute command: {e}")

    def _read_terminal_output(self, lines_of_output: int | None = None, command: str | None = None) -> str:
        """
        Read output from the active iTerm2 terminal.

        Args:
            lines_of_output: Number of lines to read (None for all)

        Returns:
            Terminal output as string
        """
        buffer = self._retrieve_buffer()

        lines = buffer.split("\n")

        if lines_of_output:
            return "\n".join(lines[-(lines_of_output + 1):])
        elif command:
            command_line_idx = next((i for i in range(len(lines) - 1, -1, -1) if command in lines[i]), -1)
            if command_line_idx == -1:
                logger.warning(f"Command '{command}' not found in terminal output. Default return last 100 lines.")
                return "\n".join(lines[-100:])
            else:
                return "\n".join(lines[command_line_idx:])
        else:
            # If no specific lines requested, return the entire buffer
            logger.info("Returning last 100 lines of terminal output")
            return "\n".join(lines[-100:])

    def _retrieve_buffer(self) -> str:
        """Retrieve the terminal buffer content."""
        applescript = """
        tell application "iTerm2"
            tell front window
                tell current session of current tab
                    set allContent to contents
                    return allContent
                end tell
            end tell
        end tell
        """

        try:
            result = subprocess.run(
                ["osascript", "-e", applescript], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to retrieve buffer: {e}")
            return ""

    def _get_tty_path(self) -> str:
        """Get the TTY path of the current terminal session."""
        applescript = """
        tell application "iTerm2"
            tell current session of current window
                get tty
            end tell
        end tell
        """

        try:
            result = subprocess.run(
                ["osascript", "-e", applescript], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get TTY path: {e}")
            return ""

    def _is_processing(self) -> bool:
        """Check if the terminal is currently processing a command."""
        applescript = """
        tell application "iTerm2"
            tell current session of current window
                get is processing
            end tell
        end tell
        """

        try:
            result = subprocess.run(
                ["osascript", "-e", applescript], capture_output=True, text=True, check=True
            )
            return result.stdout.strip() == "true"
        except subprocess.CalledProcessError:
            return False

    def _is_waiting_for_user_input(self, tty_path: str) -> bool:
        """Check if the terminal is waiting for user input."""
        try:
            processes = self._get_processes_for_tty(os.path.basename(tty_path))
            if not processes:
                return True

            total_cpu = sum(p.cpu_percent() for p in processes)
            return total_cpu < 1.0

        except Exception:
            return True

    def _get_processes_for_tty(self, tty_name: str) -> list:
        """Get all processes associated with a TTY."""
        try:
            processes = []
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    if hasattr(proc, "terminal") and proc.terminal() == tty_name:
                        processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return processes
        except Exception:
            return []

    async def execute_command_async(self, command: str, timeout: int = 60) -> CommandResult:
        """Execute a command and capture the result."""
        safe_command = command.replace("{", "{{").replace("}", "}}").replace("<", "\\<").replace(">", "\\>")
        logger.info(f"Executing command via iTerm2: {safe_command}")

        try:
            self._ensure_session_initialized()

            # Execute command and capture output
            output = self._execute_applescript_command(command)

            # Parse the output to determine success/failure using LLM
            success, exit_code, error = await self._parse_command_output(output, command)

            return CommandResult(success=success, output=output, error=error, exit_code=exit_code)

        except Exception as e:
            logger.exception(f"Exception while executing command via iTerm2: {e}")
            return CommandResult(success=False, output="", error=str(e), exit_code=-1)

    async def execute_interactive_command_async(
            self,
            command: str,
            timeout: int = 600,
            expected_prompts: Optional[List[str]] = None,
            responses: Optional[List[str]] = None,
    ) -> CommandResult:
        """Execute an interactive command that requires direct terminal interaction."""
        safe_command = command.replace("{", "{{").replace("}", "}}").replace("<", "\\<").replace(">", "\\>")
        logger.info(f"Executing interactive command via iTerm2: {safe_command}")

        try:
            self._ensure_session_initialized()

            # Execute the command
            self._execute_applescript_command(command)

            # For interactive commands, we need to wait for user to complete the interaction
            input(
                "Command has been sent to terminal. Please complete the interaction in the terminal, then press Enter to continue..."
            )

            # Read the output after user interaction is complete
            output = self._read_terminal_output(command=command)

            # For interactive commands, assume success unless there's clear error
            success = True
            error = None

            # Check for common error patterns
            error_patterns = ["error:", "failed", "cannot", "permission denied"]
            if any(pattern in output.lower() for pattern in error_patterns):
                success = False
                error = output

            return CommandResult(
                success=success, output=output, error=error, exit_code=0 if success else 1
            )

        except Exception as e:
            logger.exception(f"Exception while executing interactive command via iTerm2: {e}")
            return CommandResult(success=False, output="", error=str(e), exit_code=-1)

    async def send_input_async(self, text: str):
        """Send input to the session asynchronously."""
        try:
            self._execute_applescript_command(text)
        except Exception as e:
            logger.warning(f"Failed to send input via iTerm2: {e}")

    def send_control_character(self, control_char: str):
        """Send a control character to iTerm."""
        try:
            # Handle special cases
            if control_char.upper() == "]":
                control_code = 29  # GS - Group Separator (telnet escape)
            elif control_char.upper() in ["ESCAPE", "ESC"]:
                control_code = 27  # ESC - Escape
            else:
                # Standard control characters
                control_char = control_char.upper()
                if not control_char.isalpha() or len(control_char) != 1:
                    raise ValueError("Invalid control character letter")
                control_code = ord(control_char) - 64

            applescript = f"""
            tell application "iTerm2"
                tell current session of current window
                    write text (ASCII character {control_code})
                end tell
            end tell
            """

            subprocess.run(["osascript", "-e", applescript], check=True)
            logger.info(f"Sent control character: Ctrl+{control_char}")
        except Exception as e:
            logger.warning(f"Failed to send control character via iTerm2: {e}")

    async def read_terminal_output_async(self, lines: int = 10) -> str:
        """Read output from the terminal."""
        try:
            return self._read_terminal_output(lines)
        except Exception as e:
            logger.warning(f"Failed to read terminal output via iTerm2: {e}")
            return ""

    def expect_output(self, patterns: List[str], timeout: int = 300) -> int | None:
        """Wait for specific output patterns from iTerm."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures

                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(self.expect_output_async(patterns, timeout))
                    finally:
                        new_loop.close()

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    return future.result()
            else:
                return loop.run_until_complete(self.expect_output_async(patterns, timeout))
        except RuntimeError:
            return asyncio.run(self.expect_output_async(patterns, timeout))

    async def expect_output_async(self, patterns: List[str], timeout: int = 30) -> int:
        """Wait for specific output patterns from iTerm (async)."""
        try:
            start_time = asyncio.get_event_loop().time()

            while (asyncio.get_event_loop().time() - start_time) < timeout:
                # Read current output
                output = await self.read_terminal_output_async(20)

                # Check for pattern matches
                for i, pattern in enumerate(patterns):
                    if pattern.lower() in output.lower():
                        return i

                # Wait before next check
                await asyncio.sleep(1)

            return -1  # Timeout

        except Exception as e:
            logger.warning(f"Error waiting for output patterns: {e}")
            return -1

    def get_active_process(self) -> Optional[Dict[str, any]]:
        """Get information about the active process in the terminal."""
        try:
            tty_path = self._get_tty_path()
            if not os.path.exists(tty_path):
                return None

            tty_name = os.path.basename(tty_path)
            processes = self._get_processes_for_tty(tty_name)

            if not processes:
                return None

            # Find the most interesting process
            active_process = max(processes, key=self._calculate_process_score)

            return {
                "pid": active_process.pid,
                "name": active_process.name(),
                "command": " ".join(active_process.cmdline()),
                "cpu_percent": active_process.cpu_percent(),
                "memory_info": active_process.memory_info(),
                "status": active_process.status(),
            }

        except Exception:
            return None

    def _calculate_process_score(self, process) -> float:
        """Calculate how interesting a process is."""
        try:
            name = process.name()
            score = 0.0

            # Base score for CPU usage
            score += process.cpu_percent() / 10.0

            # Penalize shell processes
            if name in self.shell_names:
                score -= 1.0

            # Bonus for REPL processes
            if name in self.repl_names:
                score += 3.0

            # Bonus for package managers
            if name in ["brew", "npm", "yarn"] and process.cpu_percent() > 0:
                score += 2.0

            return score

        except Exception:
            return 0.0

    async def close_session_async(self):
        """Close the iTerm2 session."""
        try:
            logger.info("Closed iTerm2 session")
        except Exception as e:
            logger.warning(f"Error closing iTerm2 session: {e}")
        finally:
            self._session_initialized = False

    # Legacy methods for backward compatibility
    @staticmethod
    def get_output_lines_from_write_result(write_result) -> int:
        """Legacy method for backward compatibility."""
        return 10

    @staticmethod
    def get_output_lines_from_read_result(read_result) -> str:
        """Legacy method for backward compatibility."""
        return read_result if isinstance(read_result, str) else str(read_result)


class SubprocessCommandExecutor(CommandExecutor):
    """
    Command executor that uses a persistent subprocess shell for command execution.

    This class manages a persistent shell process and provides methods
    for executing both regular and interactive commands while maintaining session state.
    """

    def __init__(self, working_dir: Optional[str] = None, env: Optional[Dict[str, str]] = None,
                 shell: str = "/bin/bash"):
        """Initialize the subprocess command executor."""
        super().__init__(working_dir, env)
        self.shell = shell

        # Session management
        self._process: Optional[subprocess.Popen] = None
        self._output_buffer = []
        self._lock = threading.Lock()

        # Command tracking with UUID-based markers for better isolation
        self._command_id_counter = 0

    def _ensure_session_initialized(self):
        """Ensure the subprocess session is initialized."""
        if not self._session_initialized:
            self._initialize_session()
            self._session_initialized = True

    def _initialize_session(self):
        """Initialize a persistent shell subprocess."""
        try:
            session_env = self.env.copy()
            session_env['PS1'] = '$ '

            self._process = subprocess.Popen(
                [self.shell, "-i"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=self.working_dir,
                env=session_env,
                text=True,
                bufsize=0,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )

            time.sleep(0.5)

            # Initialize shell with better settings
            self._send_command_to_shell(f"cd '{self.working_dir}'", track_execution=False)
            self._send_command_to_shell("set +H", track_execution=False)  # Disable history expansion
            self._send_command_to_shell("set -m", track_execution=False)  # Enable job control

            # Define a helper function for command execution tracking
            self._send_command_to_shell('''
_exec_cmd_with_tracking() {
    local cmd_id="$1"
    shift
    echo "CMD_START_${cmd_id}"
    eval "$@"
    local exit_code=$?
    echo "CMD_END_${cmd_id}_${exit_code}"
    return $exit_code
}
            '''.strip(), track_execution=False)

            for key, value in self.env.items():
                if key not in os.environ or os.environ[key] != value:
                    self._send_command_to_shell(f"export {key}='{value}'", track_execution=False)

            logger.info(f"Initialized subprocess session with shell: {self.shell}")
            logger.info(f"Working directory: {self.working_dir}")

        except Exception as e:
            logger.error(f"Failed to initialize subprocess session: {e}")
            raise

    def _generate_command_id(self) -> str:
        """Generate a unique command ID using UUID and counter."""
        self._command_id_counter += 1
        return f"{uuid.uuid4().hex}_{self._command_id_counter}"

    def _send_command_to_shell(self, command: str, track_execution: bool = True) -> str:
        """Send a command to the shell process with optional execution tracking."""
        if not self._process or self._process.poll() is not None:
            raise RuntimeError("Shell process is not running")

        try:
            if track_execution:
                # Generate unique command ID
                cmd_id = self._generate_command_id()

                # Escape command for safe execution
                escaped_command = command.replace("'", "'\"'\"'")
                full_command = f"_exec_cmd_with_tracking '{cmd_id}' '{escaped_command}'\n"

                self._process.stdin.write(full_command)
                self._process.stdin.flush()
                return cmd_id
            else:
                # Direct command execution without tracking (for initialization)
                self._process.stdin.write(f"{command}\n")
                self._process.stdin.flush()
                return ""
        except Exception as e:
            logger.error(f"Failed to send command to shell: {e}")
            raise

    def _read_command_output(self, cmd_id: str, timeout: int = 600) -> Tuple[str, int]:
        """Read output from the shell until command completion markers are found."""
        try:
            start_time = time.time()
            output_lines = []
            exit_code = 0
            command_started = False
            command_finished = False

            start_marker = f"CMD_START_{cmd_id}"
            end_marker_prefix = f"CMD_END_{cmd_id}_"

            # Read output line by line until we find the end marker
            while time.time() - start_time < timeout and not command_finished:
                try:
                    # Use select or polling to avoid blocking
                    ready = self._process.stdout.readable()
                    if not ready:
                        time.sleep(0.01)
                        continue

                    line = self._process.stdout.readline()

                    if not line:  # EOF or no data
                        time.sleep(0.01)
                        continue

                    line = line.rstrip('\r\n')

                    # Check for start marker
                    if line == start_marker:
                        command_started = True
                        logger.debug(f"Command {cmd_id} started")
                        continue

                    # Check for end marker
                    if line.startswith(end_marker_prefix):
                        try:
                            exit_code_str = line[len(end_marker_prefix):]
                            exit_code = int(exit_code_str)
                            command_finished = True
                            logger.debug(f"Command {cmd_id} finished with exit code: {exit_code}")
                            break
                        except ValueError:
                            logger.warning(f"Failed to parse exit code from: {line}")
                            exit_code = 1
                            command_finished = True
                            break

                    # Collect output lines only after command started
                    if command_started:
                        # Skip empty lines and common shell prompts
                        if line and not line.strip() in ['$', '> ', '# ', '']:
                            output_lines.append(line)

                except Exception as e:
                    if "timed out" not in str(e).lower():
                        logger.debug(f"Read error: {e}")
                    time.sleep(0.01)

            if not command_finished:
                logger.error(f"Command {cmd_id} did not complete within {timeout} seconds")
                return "Command execution timed out", 124  # Standard timeout exit code

            # Join output lines
            output = '\n'.join(output_lines)

            # Log for debugging
            if not output.strip():
                logger.debug(f"Command {cmd_id} produced no output (this is normal for some commands)")

            return output, exit_code

        except Exception as e:
            logger.error(f"Error reading command output: {e}")
            return f"Error reading output: {str(e)}", 1

    async def execute_command_async(self, command: str, timeout: int = 600) -> CommandResult:
        """Execute a command and capture the result."""
        safe_command = command.replace("{", "{{").replace("}", "}}")
        logger.info(f"Executing command via subprocess: {safe_command}")

        try:
            with self._lock:
                self._ensure_session_initialized()
                cmd_id = self._send_command_to_shell(command, track_execution=True)

                loop = asyncio.get_event_loop()
                output, exit_code = await loop.run_in_executor(
                    None, self._read_command_output, cmd_id, timeout
                )

            success = exit_code == 0
            error = None if success else f"Command failed with exit code {exit_code}"

            if not success or "error" in output.lower():
                success, _, llm_error = await self._parse_command_output(output, command)
                if llm_error and not error:
                    error = llm_error

            return CommandResult(
                success=success,
                output=output,
                error=error,
                exit_code=exit_code
            )

        except Exception as e:
            logger.exception(f"Exception while executing command via subprocess: {e}")
            return CommandResult(success=False, output="", error=str(e), exit_code=-1)

    async def execute_interactive_command_async(
            self,
            command: str,
            timeout: int = 600,
            expected_prompts: Optional[List[str]] = None,
            responses: Optional[List[str]] = None,
    ) -> CommandResult:
        """Execute an interactive command with automated responses."""
        safe_command = command.replace("{", "{{").replace("}", "}}")
        logger.info(f"Executing interactive command via subprocess: {safe_command}")

        try:
            with self._lock:
                self._ensure_session_initialized()

                # For interactive commands, we don't use tracking as it might interfere
                self._process.stdin.write(f"{command}\n")
                self._process.stdin.flush()

                if expected_prompts and responses:
                    await self._handle_interactive_prompts(expected_prompts, responses, timeout)

                # Read output for interactive commands differently
                output = await self._read_interactive_output(timeout)

                # For interactive commands, assume success unless there are clear error indicators
                success, exit_code, error = await self._parse_command_output(output, command)

            return CommandResult(
                success=success,
                output=output,
                error=error,
                exit_code=exit_code
            )

        except Exception as e:
            logger.exception(f"Exception while executing interactive command: {e}")
            return CommandResult(success=False, output="", error=str(e), exit_code=-1)

    async def _read_interactive_output(self, timeout: int) -> str:
        """Read output from interactive command execution."""
        try:
            start_time = time.time()
            output_lines = []

            while time.time() - start_time < timeout:
                try:
                    line = self._process.stdout.readline()
                    if not line:
                        break

                    line = line.rstrip('\r\n')
                    if line and not line.strip() in ['$', '> ', '# ']:
                        output_lines.append(line)

                except Exception:
                    break

                # Stop reading if we detect the command has likely finished
                if len(output_lines) > 0 and time.time() - start_time > 2:
                    # Check if process is idle
                    time.sleep(0.5)
                    try:
                        # Non-blocking check for more output
                        import select
                        if select.select([self._process.stdout], [], [], 0.1)[0]:
                            recent_line = self._process.stdout.readline()
                            if recent_line and recent_line.strip() not in ['$', '> ', '# ']:
                                output_lines.append(recent_line.rstrip('\r\n'))
                            else:
                                break
                        else:
                            break
                    except:
                        break

            return '\n'.join(output_lines)

        except Exception as e:
            logger.warning(f"Failed to read interactive output: {e}")
            return ""

    async def send_input_async(self, text: str):
        """Send input to the subprocess session asynchronously."""
        try:
            with self._lock:
                self._ensure_session_initialized()
                if self._process and self._process.stdin:
                    self._process.stdin.write(f"{text}\n")
                    self._process.stdin.flush()
                    logger.debug(f"Sent input to subprocess: {text}")
                else:
                    logger.error("Cannot send input: subprocess session not active")
        except Exception as e:
            logger.error(f"Failed to send input to subprocess: {e}")
            raise

    async def read_terminal_output_async(self, lines: int = 10) -> str:
        """Read output from the subprocess session asynchronously."""
        try:
            with self._lock:
                self._ensure_session_initialized()
                if not self._process or not self._process.stdout:
                    logger.warning("Cannot read output: subprocess session not active")
                    return ""

                # Read available output without blocking
                output_lines = []
                lines_read = 0
                
                # Use a timeout to avoid blocking indefinitely
                import select
                
                while lines_read < lines:
                    # Check if data is available to read
                    ready, _, _ = select.select([self._process.stdout], [], [], 0.1)
                    if not ready:
                        break
                    
                    try:
                        line = self._process.stdout.readline()
                        if not line:
                            break
                        
                        line = line.rstrip('\r\n')
                        if line:  # Only add non-empty lines
                            output_lines.append(line)
                            lines_read += 1
                    except Exception as e:
                        logger.debug(f"Error reading line: {e}")
                        break

                result = '\n'.join(output_lines)
                logger.debug(f"Read {lines_read} lines from subprocess output")
                return result

        except Exception as e:
            logger.error(f"Failed to read terminal output from subprocess: {e}")
            return ""

    async def _handle_interactive_prompts(self, expected_prompts: List[str], responses: List[str], timeout: int):
        """Handle interactive prompts during command execution."""
        if not expected_prompts or not responses or len(expected_prompts) != len(responses):
            logger.warning("Mismatched prompts and responses for interactive command")
            return

        try:
            start_time = time.time()
            prompt_index = 0

            while prompt_index < len(expected_prompts) and (time.time() - start_time) < timeout:
                # Read current output to check for prompts
                current_output = await self.read_terminal_output_async(5)
                
                if current_output and expected_prompts[prompt_index].lower() in current_output.lower():
                    # Found the expected prompt, send the response
                    response = responses[prompt_index]
                    logger.info(f"Responding to prompt '{expected_prompts[prompt_index]}' with '{response}'")
                    
                    await self.send_input_async(response)
                    prompt_index += 1
                    
                    # Brief delay after sending response
                    await asyncio.sleep(0.5)
                else:
                    # Wait a bit before checking again
                    await asyncio.sleep(0.5)

            if prompt_index < len(expected_prompts):
                logger.warning(f"Not all prompts were handled: {prompt_index}/{len(expected_prompts)}")

        except Exception as e:
            logger.error(f"Error handling interactive prompts: {e}")

    async def close_session_async(self):
        """Close the subprocess session."""
        try:
            if self._process and self._process.poll() is None:
                self._process.stdin.write("exit\n")
                self._process.stdin.flush()

                try:
                    self._process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self._process.terminate()
                    try:
                        self._process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        self._process.kill()

            logger.info("Closed subprocess session")
        except Exception as e:
            logger.warning(f"Error closing subprocess session: {e}")
        finally:
            self._session_initialized = False
            self._process = None

    def is_session_active(self) -> bool:
        """Check if the session is active."""
        return (self._session_initialized and
                self._process is not None and
                self._process.poll() is None)

    def get_session_info(self) -> Dict[str, any]:
        """Get information about the current session."""
        return {
            "initialized": self._session_initialized,
            "process_id": self._process.pid if self._process else None,
            "working_directory": self.working_dir,
            "shell": self.shell,
            "active": self.is_session_active()
        }


def create_command_executor(working_dir: Optional[str] = None, env: Optional[Dict[str, str]] = None) -> CommandExecutor:
    """
    Factory function to create the appropriate command executor based on environment variable.

    Environment variable COMMAND_EXECUTOR can be set to:
    - "iterm" or "iterm2": Use ItermCommandExecutor (default on macOS)
    - "subprocess": Use SubprocessCommandExecutor

    If not set, defaults to ItermCommandExecutor on macOS, SubprocessCommandExecutor elsewhere.

    Args:
        working_dir: Working directory for command execution
        env: Environment variables for command execution

    Returns:
        Appropriate CommandExecutor instance
    """
    import platform

    # Get environment variable setting
    executor_type = os.environ.get("COMMAND_EXECUTOR", "").lower()

    # Determine which executor to use
    if executor_type in ["iterm", "iterm2"]:
        use_iterm = True
    elif executor_type == "subprocess":
        use_iterm = False
    else:
        # Default behavior: use iterm on macOS, subprocess elsewhere
        use_iterm = platform.system() == "Darwin"

    if use_iterm:
        logger.info("Using ItermCommandExecutor for command execution")
        return ItermCommandExecutor(working_dir=working_dir, env=env)
    else:
        logger.info("Using SubprocessCommandExecutor for command execution")
        return SubprocessCommandExecutor(working_dir=working_dir, env=env)
