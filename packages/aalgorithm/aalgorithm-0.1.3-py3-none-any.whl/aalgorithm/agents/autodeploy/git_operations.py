"""
Git repository operations for deployment processes.

This module provides functions to interact with Git repositories,
including cloning, validating, and extracting information.
"""
import os
import re
import shutil
import time
from pathlib import Path
from typing import Tuple, Optional, Callable, List, Dict

import requests
import trafilatura
from loguru import logger

from .command import create_command_executor
from .react_search import ReactSearchAgent
from ...content import ContentCleaner
from ...llm import LLMProvider


def _parse_command_output_with_llm(command_output: str, command_description: str,
                                   llm_provider: Optional[LLMProvider] = None) -> str:
    """
    Parse command output using LLM to extract clean result.
    
    Args:
        command_output: Raw command output
        command_description: Description of what the command does
        llm_provider: Optional LLM provider for parsing
        
    Returns:
        Clean parsed result
    """
    if not command_output or not command_output.strip():
        return ""

    # If no LLM provider available, fall back to simple strip
    if not llm_provider:
        return command_output.strip()

    try:
        system_prompt = """You are a command output parser. Your task is to extract the clean, relevant result from command output.

Command output may contain:
- Extra whitespace
- Warning messages
- Status messages
- ANSI color codes
- Multiple lines where only one line is the actual result

Extract only the essential result that the command was meant to return."""

        user_prompt = f"""Please extract the clean result from this command output.

Command description: {command_description}

Raw output:
```
{command_output}
```

Return only the clean result without any explanations or additional text."""

        response = llm_provider.generate_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=100
        )

        if response and isinstance(response, str):
            clean_result = response.strip()
            # Basic validation - if the LLM result seems reasonable, use it
            if clean_result and len(clean_result) < len(command_output) * 2:  # Sanity check
                return clean_result

        # If LLM parsing fails or seems unreasonable, fall back to simple strip
        logger.warning(f"LLM parsing failed for command output, falling back to simple strip")
        return command_output.strip()

    except Exception as e:
        logger.error(f"Error using LLM for command output parsing: {e}")
        return command_output.strip()


def _parse_git_branch_output(branch_output: str, llm_provider: Optional[LLMProvider] = None) -> str:
    """
    Parse git branch --show-current output to get clean branch name.
    
    Args:
        branch_output: Raw git branch output
        llm_provider: Optional LLM provider for parsing
        
    Returns:
        Clean branch name or "main" as fallback
    """
    if not branch_output or not branch_output.strip():
        return "main"

    clean_branch = _parse_command_output_with_llm(
        branch_output,
        "git branch --show-current (should return current branch name)",
        llm_provider
    )

    # Additional validation for branch names
    if clean_branch and clean_branch.replace("-", "").replace("_", "").replace("/", "").isalnum():
        return clean_branch

    return "main"


def _parse_git_remote_url_output(remote_url_output: str, llm_provider: Optional[LLMProvider] = None) -> str:
    """
    Parse git remote get-url output to get clean URL.
    
    Args:
        remote_url_output: Raw git remote URL output
        llm_provider: Optional LLM provider for parsing
        
    Returns:
        Clean remote URL
    """
    if not remote_url_output or not remote_url_output.strip():
        return ""

    return _parse_command_output_with_llm(
        remote_url_output,
        "git remote get-url origin (should return repository URL)",
        llm_provider
    )


def _check_git_status_clean(status_output: str, llm_provider: Optional[LLMProvider] = None) -> bool:
    """
    Check if git status --porcelain output indicates a clean working directory.
    
    Args:
        status_output: Raw git status --porcelain output
        llm_provider: Optional LLM provider for parsing
        
    Returns:
        True if working directory is clean, False otherwise
    """
    if not status_output:
        return True

    if not llm_provider:
        return not status_output.strip()

    try:
        system_prompt = """You are a git status parser. Your task is to determine if a git working directory is clean based on git status --porcelain output.

git status --porcelain output format:
- Empty output = clean working directory
- Any lines with file changes = dirty working directory
- Lines starting with M, A, D, R, C, U, ??, etc. indicate changes

Return only "clean" or "dirty" based on the output."""

        user_prompt = f"""Is this git working directory clean or dirty based on the git status --porcelain output?

Output:
```
{status_output}
```

Answer with only "clean" or "dirty"."""

        response = llm_provider.generate_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=10
        )

        if response and isinstance(response, str):
            response_lower = response.strip().lower()
            return "clean" in response_lower

        # Fall back to simple check
        return not status_output.strip()

    except Exception as e:
        logger.error(f"Error using LLM for git status parsing: {e}")
        return not status_output.strip()


def _check_git_stash_list(stash_output: str, llm_provider: Optional[LLMProvider] = None) -> bool:
    """
    Check if git stash list output indicates there are stashed changes.
    
    Args:
        stash_output: Raw git stash list output
        llm_provider: Optional LLM provider for parsing
        
    Returns:
        True if there are stashed changes, False otherwise
    """
    if not stash_output:
        return False

    if not llm_provider:
        return bool(stash_output.strip())

    try:
        system_prompt = """You are a git stash parser. Your task is to determine if there are stashed changes based on git stash list output.

git stash list output format:
- Empty output = no stashed changes
- Lines like "stash@{0}: ..." = stashed changes exist

Return only "yes" or "no" based on whether stashed changes exist."""

        user_prompt = f"""Are there stashed changes based on this git stash list output?

Output:
```
{stash_output}
```

Answer with only "yes" or "no"."""

        response = llm_provider.generate_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=10
        )

        if response and isinstance(response, str):
            response_lower = response.strip().lower()
            return "yes" in response_lower

        # Fall back to simple check
        return bool(stash_output.strip())

    except Exception as e:
        logger.error(f"Error using LLM for git stash parsing: {e}")
        return bool(stash_output.strip())


def extract_project_name_from_url(git_url: str) -> str:
    """
    Extract project name from Git URL.

    Args:
        git_url: Git repository URL

    Returns:
        Project name extracted from URL
    """
    try:
        # Remove .git suffix if present
        if git_url.endswith(".git"):
            git_url = git_url[:-4]

        # Extract the last part of the URL (project name)
        project_name = git_url.split("/")[-1]

        # Clean up the project name
        project_name = project_name.replace("-", "_").replace(" ", "_")

        return project_name
    except Exception:
        return "unknown_project"


def _contains_deployment_instructions(content: str, llm_provider: Optional[LLMProvider] = None) -> bool:
    """
    Check if the content contains deployment instructions using LLM analysis.
    
    Args:
        content: The content to check
        llm_provider: Optional LLM provider for intelligent analysis
        
    Returns:
        True if deployment instructions are found, False otherwise
    """
    if not content:
        return False

    # If no LLM provider is available, fall back to keyword-based detection
    if not llm_provider:
        return _contains_deployment_instructions_fallback(content)

    try:
        # Use LLM to analyze the content
        system_prompt = """You are an expert at analyzing README files and documentation to determine if they contain ACTUAL deployment instructions. 
        
Your task is to analyze the given content and determine if it contains sufficient deployment instructions that would help someone deploy or run the project directly from this document.

Consider the following as ACTUAL deployment instructions:
- Step-by-step installation commands
- Configuration setup instructions
- Build/compile commands with specific syntax
- Environment setup with actual values or examples
- Docker commands or Dockerfile content
- Server startup commands
- Dependency installation with specific package managers

DO NOT consider the following as deployment instructions:
- Links or references to other documents for installation (e.g., "see user manual", "visit documentation")
- General mentions of installation without specific steps
- Brief statements like "For installation details, please see..."
- Video links or external resources without inline instructions
- Overview sections that mention deployment concepts without actual steps

The content must contain actionable, specific instructions that someone can follow directly to deploy/run the project.

Return only "true" or "false" (without quotes) based on whether the content contains ACTUAL deployment instructions."""

        user_prompt = f"""Please analyze the following README content and determine if it contains ACTUAL deployment instructions (not just references to other documents):

---
{content[:4000]}  # Limit content to avoid token limits
---

Does this content contain ACTUAL deployment instructions that someone can follow directly? Answer with only "true" or "false"."""

        response = llm_provider.generate_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=10
        )

        if response and isinstance(response, str):
            response_lower = response.strip().lower()
            if "true" in response_lower:
                return True
            elif "false" in response_lower:
                return False

        # If LLM response is unclear, fall back to keyword detection
        logger.warning("LLM response unclear, falling back to keyword detection")
        return _contains_deployment_instructions_fallback(content)

    except Exception as e:
        logger.error(f"Error using LLM for deployment instruction detection: {e}")
        # Fall back to keyword-based detection if LLM fails
        return _contains_deployment_instructions_fallback(content)


def _contains_deployment_instructions_fallback(content: str) -> bool:
    """
    Fallback method to check if content contains ACTUAL deployment instructions using keyword matching.
    
    Args:
        content: The content to check
        
    Returns:
        True if ACTUAL deployment instructions are found, False otherwise
    """
    if not content:
        return False

    content_lower = content.lower()

    # Check for references to external documents first - these should return False
    external_references = [
        "see user manual", "visit documentation", "check the documentation",
        "for installation details", "for setup instructions", "please see",
        "refer to", "visit the", "check out", "see the guide",
        "installation guide", "setup guide", "deployment guide",
        "user guide", "getting started guide"
    ]

    # If content primarily contains external references, return False
    reference_count = sum(1 for ref in external_references if ref in content_lower)
    if reference_count > 0:
        # Check if there are actual actionable instructions
        actionable_patterns = [
            "npm install", "pip install", "yarn install", "go install",
            "docker run", "docker build", "docker-compose",
            "git clone", "cd ", "mkdir", "chmod", "export ",
            "sudo ", "apt-get", "yum install", "brew install",
            "python -m", "node ", "java -jar", "mvn ", "gradle ",
            "make ", "cmake ", "cargo run", "cargo build"
        ]

        actionable_count = sum(1 for pattern in actionable_patterns if pattern in content_lower)

        # If there are more references than actionable instructions, likely just references
        if reference_count >= actionable_count:
            return False

    # Check for code blocks with actual deployment commands
    code_block_patterns = [
        "```bash", "```shell", "```sh", "```console", "```cmd",
        "```dockerfile", "```yaml", "```yml", "```json", "```makefile"
    ]

    code_block_found = any(pattern in content_lower for pattern in code_block_patterns)

    # Deployment-related sections with actual content
    deployment_sections = [
        "# installation", "## installation", "# setup", "## setup",
        "# getting started", "## getting started", "# quickstart", "## quickstart",
        "# deployment", "## deployment", "# running", "## running",
        "# usage", "## usage", "# build", "## build"
    ]

    section_found = any(section in content_lower for section in deployment_sections)

    # Strong indicators of actual deployment instructions
    strong_deployment_indicators = [
        "npm install", "pip install", "yarn install", "go install",
        "docker run", "docker build", "docker-compose up",
        "git clone", "make install", "make build",
        "python setup.py", "python -m pip install",
        "sudo apt-get", "brew install", "yum install",
        "cargo build", "cargo run", "mvn clean install",
        "gradle build", "gradle run", "cmake", "configure",
        "./configure", "make && make install"
    ]

    strong_indicators_found = any(indicator in content_lower for indicator in strong_deployment_indicators)

    # Return True only if we have strong indicators AND (sections OR code blocks)
    return strong_indicators_found and (section_found or code_block_found)


def read_readme_from_repo(repo_dir: str, llm_provider: Optional[LLMProvider] = None) -> Optional[str]:
    """
    Read README file from the cloned repository and check if it contains deployment instructions.
    If not, use ReAct search to find deployment guides.

    Args:
        repo_dir: Path to the cloned repository
        llm_provider: Optional LLM provider for intelligent analysis

    Returns:
        README content with deployment instructions or enhanced content from search agents
    """
    try:
        repo_path = Path(repo_dir)

        # Common README file names
        readme_files = [
            "README.md",
            "readme.md",
            "README.txt",
            "readme.txt",
            "README.rst",
            "readme.rst",
            "README",
            "readme",
        ]

        readme_content = None
        for readme_file in readme_files:
            readme_path = repo_path / readme_file
            if readme_path.exists() and readme_path.is_file():
                logger.info(f"Found README file: {readme_path}")
                with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
                    readme_content = f.read()
                break

        if not readme_content:
            logger.warning(f"No README file found in {repo_dir}")

            # Use LLM to analyze the directory structure and find potential documentation
            if llm_provider:
                logger.info("Using LLM to analyze repository structure for documentation files")
                readme_content = _find_docs_with_directory_analysis(repo_dir, llm_provider)

                if readme_content:
                    logger.success("Found documentation through directory structure analysis")
                else:
                    logger.warning("No documentation found through directory structure analysis")
                    return None
            else:
                return None

        # Check if README contains deployment instructions using LLM
        if _contains_deployment_instructions(readme_content, llm_provider):
            logger.info("README contains deployment instructions")
            return readme_content

        # If no deployment instructions found, start the enhanced search process
        logger.info(
            "README does not contain sufficient deployment instructions, attempting to enhance")

        try:
            # Extract project name from repository directory
            project_name = os.path.basename(repo_dir)

            # First, try the ReAct search pattern if LLM provider is available
            if llm_provider:
                logger.info(f"🧠 Using ReAct search pattern for project: {project_name}")
                react_agent = ReactSearchAgent(llm_provider=llm_provider)
                # Pass the local repository path to enable local file processing
                react_guide = react_agent.search_for_deployment_guide(
                    project_name, readme_content, local_repo_path=repo_dir
                )

                if react_guide and len(react_guide) > 200:
                    logger.success("✅ Successfully created deployment guide with ReAct search")
                    return react_guide
                else:
                    logger.warning("⚠️ ReAct search didn't find sufficient deployment information")
            else:
                logger.info("LLM provider not available, skipping ReAct search")

        except Exception as e:
            logger.error(f"Error during enhanced search process: {e}")
            logger.info("Falling back to original README content")
            return readme_content

    except Exception as e:
        logger.error(f"Error reading README from repository: {e}")
        return None


def _find_docs_with_directory_analysis(repo_dir: str, llm_provider: LLMProvider) -> Optional[str]:
    """
    Analyze repository directory structure using LLM to find documentation files.

    Args:
        repo_dir: Path to the repository
        llm_provider: LLM provider for analysis

    Returns:
        Content of found documentation files or None
    """
    try:
        # Generate directory structure
        dir_structure = _generate_directory_structure(repo_dir)

        # Ask LLM to identify potential documentation files
        system_prompt = """You are an expert in software project structures. Your task is to analyze a repository's 
directory structure to identify files that might contain deployment instructions, documentation, or setup guides.

Look for files like:
1. Documentation files in /docs, /doc, /documentation directories
2. Installation or setup guides
3. Deployment configuration files (docker-compose.yml, Dockerfile, etc.)
4. Build scripts (Makefile, build.sh, etc.)
5. Configuration examples or templates

Return a JSON array of file paths relative to the repository root that are most likely to contain 
deployment or setup instructions, ranked by probability (highest first). Limit to 5 files maximum."""

        user_prompt = f"""Here's the directory structure of a repository. Please identify the most likely files 
that would contain deployment instructions or documentation on how to set up the project.

Directory structure:
```
{dir_structure}
```

Return a JSON array of relative file paths, for example:
["docs/installation.md", "deployment/README.md"]"""

        response = llm_provider.generate_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=500,
            json_format=True
        )

        # Process LLM response
        if not response or not isinstance(response, list) or len(response) == 0:
            logger.warning("LLM didn't return any file suggestions")
            return None

        # Check each suggested file
        all_content = []

        for file_path in response:
            if not isinstance(file_path, str):
                continue

            full_path = os.path.join(repo_dir, file_path)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                logger.info(f"Checking suggested file: {file_path}")

                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    if content:
                        # Add file identification header
                        file_content = f"# Documentation from {file_path}\n\n{content}\n\n"
                        all_content.append(file_content)
                        logger.success(f"Found content in {file_path}")
                except Exception as e:
                    logger.error(f"Error reading {file_path}: {e}")

        # Combine all found content
        if all_content:
            combined_content = "# Project Documentation\n\n"
            combined_content += "The following documentation was found by analyzing the repository structure:\n\n"
            combined_content += "---\n\n"
            combined_content += "\n---\n\n".join(all_content)
            return combined_content

        return None

    except Exception as e:
        logger.error(f"Error during directory analysis: {e}")
        return None


def _generate_directory_structure(root_dir: str, max_depth: int = 4, exclude_dirs: List[str] = None) -> str:
    """
    Generate a string representation of the directory structure.

    Args:
        root_dir: Repository root directory
        max_depth: Maximum depth to traverse
        exclude_dirs: Directories to exclude (e.g., .git, node_modules)

    Returns:
        String representation of the directory structure
    """
    if exclude_dirs is None:
        exclude_dirs = ['.git', 'node_modules', 'venv', '.venv', 'env', '.env',
                        '__pycache__', '.idea', '.vscode']

    structure = []
    root_path = Path(root_dir)

    def traverse_dir(path: Path, current_depth: int, prefix: str = ""):
        if current_depth > max_depth:
            return

        if path.name in exclude_dirs or path.name.startswith('.'):
            return

        try:
            entries = list(path.iterdir())
            entries.sort(key=lambda x: (not x.is_dir(), x.name.lower()))

            # Count files to avoid listing too many
            dirs = [e for e in entries if e.is_dir()]
            files = [e for e in entries if e.is_file()]

            # Limit files if there are too many
            max_files_per_dir = 10
            if len(files) > max_files_per_dir:
                files = files[:max_files_per_dir]
                too_many = True
            else:
                too_many = False

            # Process directories first, then files
            for i, entry in enumerate(dirs + files):
                is_last = (i == len(dirs) + len(files) - 1)

                if entry in dirs:
                    if is_last:
                        structure.append(f"{prefix}└── {entry.name}/")
                        traverse_dir(entry, current_depth + 1, f"{prefix}    ")
                    else:
                        structure.append(f"{prefix}├── {entry.name}/")
                        traverse_dir(entry, current_depth + 1, f"{prefix}│   ")
                else:
                    if is_last:
                        structure.append(f"{prefix}└── {entry.name}")
                    else:
                        structure.append(f"{prefix}├── {entry.name}")

            if too_many:
                structure.append(f"{prefix}└── ... (more files)")

        except PermissionError:
            structure.append(f"{prefix}└── [Permission Denied]")
        except Exception as e:
            structure.append(f"{prefix}└── [Error: {str(e)}]")

    # Start traversal from the root
    structure.append(f"{root_path.name}/")
    traverse_dir(root_path, 1)

    return "\n".join(structure)


def clone_repository(
        git_url: str,
        project_name: str,
        working_dir: str,
        interaction_handler: Optional[Callable[[str, List[str]], str]] = None,
        llm_provider: Optional[LLMProvider] = None,
        repo_checked: bool = True
) -> Tuple[bool, str, str]:
    """
    Clone a Git repository with robust directory checks.

    Args:
        git_url: Git repository URL
        project_name: Name of the project
        working_dir: Base working directory
        interaction_handler: Optional callback for handling user interactions
        llm_provider: Optional LLM provider for parsing command outputs

    Returns:
        Tuple of (success, message, repo_dir)
    """
    # Determine repository directory
    repo_dir = working_dir
    if os.path.basename(repo_dir) != project_name:
        repo_dir = os.path.join(working_dir, project_name)

    repo_exists = os.path.exists(repo_dir)
    is_git_repo = False

    if repo_checked: #! tmp
        return True, "Repository cloned or updated successfully", repo_dir



    # Check if directory exists and is a Git repository
    if repo_exists:
        git_dir = os.path.join(repo_dir, ".git")
        is_git_repo = os.path.isdir(git_dir)

        if is_git_repo:
            # Check if existing repository matches the provided URL
            with create_command_executor(working_dir=repo_dir) as command_executor:
                # Get remote URL of existing repository
                remote_url_result = command_executor.execute_command(
                    "git remote get-url origin"
                )

                if remote_url_result.success:
                    existing_url = _parse_git_remote_url_output(remote_url_result.output, llm_provider)
                    # Normalize URLs for comparison (remove .git suffix if present)
                    normalized_existing = (
                        existing_url[:-4] if existing_url.endswith(".git") else existing_url
                    )
                    normalized_new = git_url[:-4] if git_url.endswith(".git") else git_url

                    if normalized_new in normalized_existing:
                        # Repository already exists and matches, update it
                        logger.info(f"Repository already exists at {repo_dir}, updating...")

                        # Check if working directory is clean
                        status_result = command_executor.execute_command("git status --porcelain")
                        if status_result.success and not _check_git_status_clean(status_result.output, llm_provider):
                            logger.warning("Working directory has uncommitted changes, stashing them...")
                            stash_result = command_executor.execute_command("git stash")
                            if not stash_result.success:
                                logger.error(f"Failed to stash changes: {stash_result.error}")
                                return (
                                    False,
                                    f"Failed to stash uncommitted changes: {stash_result.error}",
                                    repo_dir,
                                )

                        # Fetch latest changes
                        fetch_result = command_executor.execute_command("git fetch origin")
                        if not fetch_result.success:
                            logger.warning(f"Failed to fetch from remote: {fetch_result.error}")

                        # Get current branch
                        branch_result = command_executor.execute_command("git branch --show-current")
                        current_branch = _parse_git_branch_output(branch_result.output,
                                                                  llm_provider) if branch_result.success else "main"

                        # Try to pull with rebase to avoid merge commits
                        pull_result = command_executor.execute_command(f"git pull --rebase origin {current_branch}")
                        
                        if pull_result.success:
                            # Check if there were stashed changes and try to restore them
                            stash_list_result = command_executor.execute_command("git stash list")
                            if stash_list_result.success and _check_git_stash_list(stash_list_result.output,
                                                                                   llm_provider):
                                logger.info("Restoring stashed changes...")
                                pop_result = command_executor.execute_command("git stash pop")
                                if not pop_result.success:
                                    logger.warning(f"Failed to restore stashed changes: {pop_result.error}")
                                    return (
                                        True,
                                        "Repository updated successfully, but failed to restore stashed changes",
                                        repo_dir,
                                    )
                            
                            return (
                                True,
                                "Repository already exists and was updated successfully",
                                repo_dir,
                            )
                        else:
                            # If rebase fails, try regular pull
                            logger.warning(f"Rebase failed, trying regular pull: {pull_result.error}")
                            pull_result = command_executor.execute_command(f"git pull origin {current_branch}")

                            if pull_result.success:
                                return (
                                    True,
                                    "Repository already exists and was updated successfully",
                                    repo_dir,
                                )
                            else:
                                logger.error(f"Failed to update existing repository: {pull_result.error}")
                                return (
                                    False,
                                    f"Failed to update existing repository: {pull_result.error}",
                                    repo_dir,
                                )
                    else:
                        # Repository exists but doesn't match the URL
                        if interaction_handler:
                            message = (
                                f"Directory {repo_dir} already contains a Git repository with URL {existing_url}, "
                                f"which doesn't match the requested URL {git_url}. How would you like to proceed?"
                            )
                            options = ["backup_and_clone", "use_existing", "abort"]
                            choice = interaction_handler(message, options)

                            if choice == "backup_and_clone":
                                # Backup existing directory and clone new repository
                                backup_dir = f"{repo_dir}_backup_{int(time.time())}"
                                logger.info(f"Backing up existing repository to {backup_dir}")

                                try:
                                    os.rename(repo_dir, backup_dir)
                                except Exception as e:
                                    logger.error(f"Failed to backup repository: {e}")
                                    return False, f"Failed to backup repository: {e}", repo_dir

                                # Directory has been moved, proceed with clone
                                repo_exists = False
                            elif choice == "use_existing":
                                # Use existing repository
                                logger.info(f"Using existing repository at {repo_dir}")
                                return True, "Using existing repository", repo_dir
                            else:  # abort
                                logger.info("Operation aborted by user")
                                return False, "Operation aborted by user", repo_dir
                        else:
                            # No interaction handler, default to abort
                            return (
                                False,
                                f"Directory {repo_dir} already contains a different Git repository",
                                repo_dir,
                            )
                else:
                    logger.warning(
                        f"Failed to get remote URL of existing repository: {remote_url_result.error}"
                    )
                    return (
                        False,
                        f"Failed to verify existing repository: {remote_url_result.error}",
                        repo_dir,
                    )
        else:
            # Directory exists but is not a Git repository
            if os.listdir(repo_dir):  # Check if directory is not empty
                if interaction_handler:
                    message = f"Directory {repo_dir} already exists and is not empty. How would you like to proceed?"
                    options = ["backup_and_clone", "force_clone", "abort"]
                    choice = interaction_handler(message, options)

                    if choice == "backup_and_clone":
                        # Backup existing directory and clone new repository
                        backup_dir = f"{repo_dir}_backup_{int(time.time())}"
                        logger.info(f"Backing up existing directory to {backup_dir}")

                        try:
                            os.rename(repo_dir, backup_dir)
                        except Exception as e:
                            logger.error(f"Failed to backup directory: {e}")
                            return False, f"Failed to backup directory: {e}", repo_dir

                        # Directory has been moved, proceed with clone
                        repo_exists = False
                    elif choice == "force_clone":
                        # Force clone by removing existing directory
                        logger.info(f"Removing existing directory {repo_dir} for force clone")
                        try:
                            shutil.rmtree(repo_dir)
                            repo_exists = False
                        except Exception as e:
                            logger.error(f"Failed to remove existing directory: {e}")
                            return False, f"Failed to remove existing directory: {e}", repo_dir
                    else:  # abort
                        logger.info("Operation aborted by user")
                        return False, "Operation aborted by user", repo_dir
                else:
                    # No interaction handler, default to abort
                    return (
                        False,
                        f"Directory {repo_dir} already exists and is not empty",
                        repo_dir,
                    )

    # Clone the repository if needed
    if not repo_exists or not is_git_repo:
        # Create parent directory if needed
        parent_dir = os.path.dirname(repo_dir)
        os.makedirs(parent_dir, exist_ok=True)

        # Clone the repository using command executor factory
        with create_command_executor(working_dir=parent_dir) as command_executor:
            logger.info(f"Cloning repository from {git_url}")
            clone_result = command_executor.execute_command(
                f"git clone {git_url}"
            )

            if not clone_result.success:
                logger.error(f"Failed to clone repository: {clone_result.error}")
                return False, f"Failed to clone repository: {clone_result.error}", repo_dir

    return True, "Repository cloned or updated successfully", repo_dir


def extract_external_deployment_links(readme_content: str) -> List[Dict[str, str]]:
    """
    从README内容中提取部署相关的外部链接
    
    Args:
        readme_content: README文件内容
        
    Returns:
        包含链接信息的列表
    """
    logger.info("🔗 正在提取README中的部署相关外部链接...")

    links = []

    # 部署相关关键词
    deployment_keywords = [
        'install', 'installation', 'setup', 'deploy', 'deployment', 'manual', 'guide',
        'tutorial', 'getting started', 'quickstart', 'documentation', 'docs',
        'user manual', 'configuration', 'build', 'run', 'start', 'launch'
    ]

    # 正则表达式匹配Markdown链接格式 [text](url)
    markdown_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    markdown_links = re.findall(markdown_pattern, readme_content)

    for link_text, url in markdown_links:
        # 检查链接文本是否包含部署相关关键词
        if any(keyword.lower() in link_text.lower() for keyword in deployment_keywords):
            links.append({
                'text': link_text.strip(),
                'url': url.strip(),
                'type': 'deployment',
                'format': 'markdown'
            })
            logger.info(f"  ✅ 发现部署链接: {link_text} -> {url}")

    # 匹配HTML链接格式 <a href="url">text</a>
    html_pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>'
    html_links = re.findall(html_pattern, readme_content)

    for url, link_text in html_links:
        if any(keyword.lower() in link_text.lower() for keyword in deployment_keywords):
            links.append({
                'text': link_text.strip(),
                'url': url.strip(),
                'type': 'deployment',
                'format': 'html'
            })
            logger.info(f"  ✅ 发现部署链接 (HTML): {link_text} -> {url}")

    # 匹配裸URL（可选，但通常不是部署指南）
    url_pattern = r'https?://[^\s<>"]+(?:install|setup|deploy|manual|guide|docs|documentation)[^\s<>"]*'
    bare_urls = re.findall(url_pattern, readme_content, re.IGNORECASE)

    for url in bare_urls:
        links.append({
            'text': 'Documentation Link',
            'url': url.strip(),
            'type': 'deployment',
            'format': 'bare_url'
        })
        logger.info(f"  ✅ 发现裸部署URL: {url}")

    logger.success(f"🔗 提取完成，共发现 {len(links)} 个部署相关链接")
    return links


def fetch_url_content_with_trafilatura(url: str, cleaner: Optional[ContentCleaner] = None) -> Optional[str]:
    """
    使用trafilatura和requests获取URL内容并清洗
    
    Args:
        url: 要获取的URL
        cleaner: 可选的内容清洗器
        
    Returns:
        清洗后的内容或None
    """
    try:
        logger.info(f"🌐 正在获取URL内容: {url}")

        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

        # 发送HTTP请求
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # 使用trafilatura提取主要内容
        html_content = response.text
        extracted_content = trafilatura.extract(html_content,
                                                include_comments=False,
                                                include_tables=True,
                                                include_links=True,
                                                include_images=False)

        if not extracted_content:
            logger.warning(f"⚠️ trafilatura无法提取内容，尝试使用cleaner...")
            # 回退到ContentCleaner
            if cleaner:
                extracted_content = cleaner.clean_with_trafilatura(url, html_content, "External Link")

            if not extracted_content:
                # 最后尝试简单的HTML标签清理
                import re
                extracted_content = re.sub(r'<[^>]+>', ' ', html_content)
                extracted_content = re.sub(r'\s+', ' ', extracted_content).strip()

                if len(extracted_content) > 10000:
                    extracted_content = extracted_content[:10000] + "..."

        if extracted_content:
            logger.success(f"✅ 成功获取内容: {len(extracted_content)} 字符")
            return extracted_content
        else:
            logger.error(f"❌ 无法提取URL内容: {url}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ 网络请求失败: {url} - {e}")
        return None
    except Exception as e:
        logger.error(f"❌ 获取URL内容时出错: {url} - {e}")
        return None


def process_github_raw_url(url: str) -> str:
    """
    处理GitHub URL，转换为raw格式以便更好地获取内容
    
    Args:
        url: GitHub URL
        
    Returns:
        处理后的URL
    """
    if 'github.com' in url and '/blob/' in url:
        # 将 github.com/user/repo/blob/branch/file 转换为 raw.githubusercontent.com/user/repo/branch/file
        raw_url = url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
        logger.info(f"🔄 GitHub URL转换为raw格式: {raw_url}")
        return raw_url
    return url


def enhance_readme_with_external_content(project_name: str, readme_content: str,
                                         llm_provider: Optional[LLMProvider] = None) -> str:
    """
    通过获取外部链接内容来增强README
    
    Args:
        project_name: 项目名称
        readme_content: 原始README内容
        llm_provider: 可选的LLM提供商，用于内容分析
        
    Returns:
        增强后的README内容
    """
    logger.info(f"🚀 开始增强项目 {project_name} 的README内容...")

    # 提取外部部署链接
    external_links = extract_external_deployment_links(readme_content)

    if not external_links:
        logger.info("📭 没有发现部署相关的外部链接")
        return readme_content

    # 初始化内容清洗器
    cleaner = ContentCleaner()

    # 存储获取的外部内容
    external_contents = []

    for link in external_links:
        url = link['url']
        link_text = link['text']

        logger.info(f"🔗 处理外部链接: {link_text}")

        # 处理相对URL
        if url.startswith('./') or url.startswith('../'):
            logger.warning(f"⚠️ 跳过相对URL: {url}")
            continue

        # 处理GitHub URL
        if 'github.com' in url:
            url = process_github_raw_url(url)

        # 获取外部内容
        external_content = fetch_url_content_with_trafilatura(url, cleaner)

        if external_content:
            external_contents.append({
                'title': link_text,
                'url': link['url'],  # 保持原始URL用于引用
                'content': external_content,
                'format': link['format']
            })
        else:
            logger.warning(f"⚠️ 无法获取链接内容: {url}")

    # 构建增强的README内容
    if not external_contents:
        logger.warning("📭 没有成功获取任何外部内容")
        return readme_content

    logger.success(f"✅ 成功获取 {len(external_contents)} 个外部内容")

    # 构建增强内容
    enhanced_content = f"# {project_name}\n\n"
    enhanced_content += "## 原始README内容\n\n"
    enhanced_content += readme_content + "\n\n"
    enhanced_content += "---\n\n"
    enhanced_content += "## 外部部署指南 (自动获取)\n\n"
    enhanced_content += "*以下内容来自README中引用的外部链接，已自动获取并整理*\n\n"

    for i, content_info in enumerate(external_contents, 1):
        enhanced_content += f"### {i}. {content_info['title']}\n\n"
        enhanced_content += f"**来源:** {content_info['url']}\n\n"

        # 使用LLM清理和结构化外部内容（如果提供了LLM）
        if llm_provider:
            try:
                system_prompt = """你是一位技术文档编辑专家。请将以下获取的外部内容整理成清晰的部署指南格式。

要求：
1. 保留所有重要的安装和部署步骤
2. 使用清晰的Markdown格式
3. 突出关键命令和配置
4. 移除无关的内容（如广告、导航等）
5. 保持信息的准确性和完整性"""

                user_prompt = f"""请整理以下部署相关内容：

标题：{content_info['title']}
来源：{content_info['url']}

原始内容：
{content_info['content'][:8000]}  # 限制长度避免token过多

请将其整理成清晰的部署指南格式。"""

                cleaned_content = llm_provider.generate_completion(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    max_tokens=2000
                )

                if cleaned_content and len(cleaned_content.strip()) > 100:
                    enhanced_content += cleaned_content + "\n\n"
                    logger.success(f"✅ 使用LLM清理外部内容: {content_info['title']}")
                else:
                    # LLM清理失败，使用原始内容
                    enhanced_content += content_info['content'] + "\n\n"

            except Exception as e:
                logger.error(f"❌ LLM清理外部内容失败: {e}")
                enhanced_content += content_info['content'] + "\n\n"
        else:
            # 没有LLM，直接使用获取的内容
            enhanced_content += content_info['content'] + "\n\n"

        enhanced_content += "---\n\n"

    # 添加总结部分
    enhanced_content += "## 部署指南总结\n\n"
    enhanced_content += f"本文档整合了 {project_name} 的原始README和 {len(external_contents)} 个外部部署资源，"
    enhanced_content += "为您提供完整的安装和部署指南。\n\n"
    enhanced_content += "**外部资源列表：**\n"

    for i, content_info in enumerate(external_contents, 1):
        enhanced_content += f"{i}. [{content_info['title']}]({content_info['url']})\n"

    logger.success(f"✅ README增强完成，最终内容长度: {len(enhanced_content)} 字符")

    return enhanced_content
