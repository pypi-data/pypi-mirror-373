"""
ReAct (Reasoning and Acting) search agent for finding deployment guides.

This module implements a search agent that uses the ReAct pattern to find
deployment instructions by reasoning about what to search for, acting by
performing searches, and observing the results to guide further reasoning.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

from ...content import ContentCleaner
from ...llm import LLMProvider
from ...utils import logger


class ReactSearchAgent:
    """
    ReAct search agent for finding deployment guides.

    This agent uses the Reasoning-Acting-Observing cycle to intelligently
    search for deployment instructions based on project context.
    """

    def __init__(self, llm_provider: LLMProvider, max_iterations: int = 5):
        """
        Initialize the ReAct search agent.

        Args:
            llm_provider: LLM provider for reasoning
            max_iterations: Maximum number of reasoning-acting cycles
        """
        self.llm_provider = llm_provider
        self.max_iterations = max_iterations
        self.content_cleaner = ContentCleaner()
        self.search_history = []
        self.observed_results = []
        self.final_insights = {}

    def search_for_deployment_guide(self, project_name: str, readme_content: str,
                                    local_repo_path: Optional[str] = None) -> str:
        """
        Search for deployment guides using the ReAct pattern.

        Args:
            project_name: Name of the project
            readme_content: Original README content
            local_repo_path: Path to the local cloned repository

        Returns:
            Enhanced deployment guide
        """
        logger.info(f"🧠 Starting ReAct search for {project_name} deployment instructions")

        if local_repo_path:
            logger.info(f"📁 Using local repository: {local_repo_path}")

        # Initialize context with project information
        context = {
            "project_name": project_name,
            "readme_content": readme_content,
            "local_repo_path": local_repo_path,
            "search_history": [],
            "observations": [],
            "iteration": 0,
            "found_deployment_instructions": False,
            "available_files": self._scan_local_files(local_repo_path) if local_repo_path else []
        }

        collected_information = []

        # ReAct loop: Reason -> Act -> Observe -> Repeat
        while context["iteration"] < self.max_iterations and not context["found_deployment_instructions"]:
            context["iteration"] += 1
            logger.info(f"🔄 ReAct iteration {context['iteration']}/{self.max_iterations}")

            # 1. REASONING: Plan next search action
            search_plan = self._reason_next_action(context)
            if not search_plan or not search_plan.get("file_path"):
                logger.warning("⚠️ Failed to generate search plan, breaking loop")
                break

            # Add to search history
            context["search_history"].append({
                "iteration": context["iteration"],
                "file_path": search_plan.get("file_path"),
                "reasoning": search_plan.get("reasoning", ""),
                "is_local": search_plan.get("is_local", False)
            })

            # 2. ACTING: Execute search based on reasoning
            search_results = self._execute_search_action(search_plan)

            # 3. OBSERVING: Process and analyze search results
            observation = self._process_search_results(search_results, project_name)

            # Add to observations
            context["observations"].append({
                "iteration": context["iteration"],
                "observation": observation
            })

            # If valuable information was found, collect it
            if observation.get("valuable_content"):
                collected_information.append({
                    "title": observation.get("title", f"Search Result {context['iteration']}"),
                    "content": observation.get("valuable_content"),
                    "source": observation.get("source", "")
                })

            # Check if we found sufficient deployment instructions
            if observation.get("is_deployment_guide", False):
                context["found_deployment_instructions"] = True
                logger.success("✅ Found sufficient deployment instructions!")

        # Create final deployment guide from collected information
        deployment_guide = self._compile_deployment_guide(project_name, collected_information)

        # Store final insights for later analysis
        self.final_insights = {
            "project_name": project_name,
            "iterations": context["iteration"],
            "found_sufficient_instructions": context["found_deployment_instructions"],
            "search_history": context["search_history"],
            "collected_information_count": len(collected_information)
        }

        return deployment_guide

    def _scan_local_files(self, repo_path: str) -> List[Dict[str, str]]:
        """
        Scan local repository for relevant deployment files.

        Args:
            repo_path: Path to the local repository

        Returns:
            List of file information dictionaries
        """
        if not repo_path or not os.path.exists(repo_path):
            return []

        try:
            repo_root = Path(repo_path)
            relevant_files = []

            # Common deployment-related file patterns
            deployment_patterns = [
                "README*",
                "readme*",
                "INSTALL*",
                "install*",
                "DEPLOYMENT*",
                "deployment*",
                "SETUP*",
                "setup*",
                "BUILD*",
                "build*",
                "CONTRIBUTING*",
                "contributing*",
                "Dockerfile*",
                "docker-compose*",
                "Makefile*",
                "makefile*",
                "package.json",
                "requirements.txt",
                "setup.py",
                "pyproject.toml",
                "Pipfile",
                "pom.xml",
                "build.gradle",
                "CMakeLists.txt",
                "configure*",
                "*.md",
                "*.txt",
                "*.rst"
            ]

            # Search in common documentation directories
            search_dirs = [
                repo_root,
                repo_root / "docs",
                repo_root / "doc",
                repo_root / "documentation",
                repo_root / "deploy",
                repo_root / "deployment",
                repo_root / "install",
                repo_root / "setup",
                repo_root / ".github"
            ]

            for search_dir in search_dirs:
                if not search_dir.exists() or not search_dir.is_dir():
                    continue

                try:
                    for pattern in deployment_patterns:
                        for file_path in search_dir.glob(pattern):
                            if file_path.is_file():
                                relative_path = file_path.relative_to(repo_root)
                                file_info = {
                                    "absolute_path": str(file_path),
                                    "relative_path": str(relative_path),
                                    "name": file_path.name,
                                    "directory": str(relative_path.parent) if relative_path.parent != Path(
                                        ".") else "root",
                                    "size": file_path.stat().st_size if file_path.exists() else 0
                                }
                                # Avoid duplicates
                                if not any(f["absolute_path"] == file_info["absolute_path"] for f in relevant_files):
                                    relevant_files.append(file_info)

                except Exception as e:
                    logger.warning(f"⚠️ Error scanning directory {search_dir}: {e}")
                    continue

            # Sort by relevance (README files first, then others)
            def file_priority(file_info):
                name_lower = file_info["name"].lower()
                if name_lower.startswith("readme"):
                    return 0
                elif name_lower.startswith("install"):
                    return 1
                elif name_lower.startswith("deploy"):
                    return 2
                elif name_lower.startswith("setup"):
                    return 3
                elif name_lower in ["dockerfile", "docker-compose.yml", "docker-compose.yaml"]:
                    return 4
                elif name_lower in ["makefile", "package.json", "requirements.txt"]:
                    return 5
                else:
                    return 6

            relevant_files.sort(key=file_priority)

            logger.info(f"📁 Found {len(relevant_files)} relevant files in local repository")
            for f in relevant_files[:10]:  # Log first 10 files
                logger.debug(f"  - {f['relative_path']} ({f['size']} bytes)")

            return relevant_files

        except Exception as e:
            logger.error(f"❌ Error scanning local repository: {e}")
            return []

    def _reason_next_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reason about what file to check next based on context.
        Prioritizes local files when available.

        Args:
            context: Current search context including history and observations

        Returns:
            Dictionary containing file path and reasoning
        """
        try:
            local_repo_path = context.get("local_repo_path")
            available_files = context.get("available_files", [])

            # Create prompt for reasoning
            if local_repo_path and available_files:
                system_prompt = """You are an expert deployment engineer searching for deployment instructions for a software project.
Your task is to analyze the context and decide what local file to check next to find deployment instructions.

You have access to a locally cloned repository with available files. PRIORITIZE LOCAL FILES over remote URLs.

Based on what you've already searched and observed, reason about:
1. What specific deployment files haven't been checked yet from the available local files
2. What technical components likely need installation/configuration documentation  
3. Which local files are most likely to contain actionable deployment instructions
4. What specific local file path would be most valuable for deployment instructions

Focus on finding files that contain actionable deployment instructions like:
- README.md files with installation sections
- INSTALL.md or INSTALLATION.md files
- Documentation files in docs/ folder (deployment.md, setup.md, etc.)
- Docker-related files (Dockerfile, docker-compose.yml)
- Package manager files (package.json, requirements.txt, setup.py)
- Configuration examples or templates
- Build files (Makefile, build scripts)

Always prioritize checking local files first. Only suggest remote URLs if no relevant local files remain."""

                # Build available files info for prompt
                files_info = "\n".join([
                    f"- {f['relative_path']} ({f['size']} bytes) - {f['directory']}"
                    for f in available_files[:20]  # Limit to avoid prompt being too long
                ])

                context_info = f"""PROJECT: {context['project_name']}
LOCAL REPOSITORY: {local_repo_path}

AVAILABLE LOCAL FILES:
{files_info}

README EXCERPT:
{context['readme_content'][:1000]}

SEARCH HISTORY:
{json.dumps(context['search_history'], indent=2)}

OBSERVATIONS SO FAR:
{json.dumps(context['observations'], indent=2)}

CURRENT ITERATION: {context['iteration']} of {self.max_iterations}"""

                user_prompt = f"""Based on the context provided, reason about what local file to check next to find deployment instructions for {context['project_name']}.

{context_info}

Output a JSON object with these fields:
1. "reasoning": Your step-by-step reasoning about what file to check next
2. "file_path": The specific file path you recommend checking (absolute path for local files, or URL for remote)
3. "is_local": true if it's a local file, false if it's a remote URL

Example for local file:
```json
{{
  "reasoning": "The project appears to be a Node.js application. Let's check the main README.md file for installation instructions as it hasn't been examined yet.",
  "file_path": "/path/to/repo/README.md",
  "is_local": true
}}
```

IMPORTANT: Prioritize local files from the available files list. Only suggest remote URLs if absolutely necessary."""
            else:
                # Fallback to remote URL reasoning when no local repo available
                system_prompt = """You are an expert deployment engineer searching for deployment instructions for a software project.
Your task is to analyze the context and decide what GitHub raw URL to check next to find deployment instructions.

IMPORTANT: You must provide raw GitHub URLs (raw.githubusercontent.com) NOT webpage URLs (github.com).

Raw URL format examples:
- https://raw.githubusercontent.com/user/repo/main/README.md
- https://raw.githubusercontent.com/user/repo/master/docs/deployment.md
- https://raw.githubusercontent.com/user/repo/main/INSTALL.md

Based on what you've already searched and observed, reason about:
1. What specific deployment files haven't been checked yet (README.md, INSTALL.md, docs/deployment.md, etc.)
2. What technical components likely need installation/configuration documentation
3. Where deployment instructions might be found based on project structure hints
4. What specific raw GitHub URLs would be most valuable for deployment instructions

Focus on finding files that contain actionable deployment instructions."""

                context_info = f"""PROJECT: {context['project_name']}

README EXCERPT:
{context['readme_content'][:1000]}

SEARCH HISTORY:
{json.dumps(context['search_history'], indent=2)}

OBSERVATIONS SO FAR:
{json.dumps(context['observations'], indent=2)}

CURRENT ITERATION: {context['iteration']} of {self.max_iterations}"""

                user_prompt = f"""Based on the context provided, reason about what GitHub raw URL to check next to find deployment instructions for {context['project_name']}.

{context_info}

Output a JSON object with these fields:
1. "reasoning": Your step-by-step reasoning about what raw GitHub URL to check next
2. "file_path": The specific GitHub raw URL you recommend checking (must be raw.githubusercontent.com format)
3. "is_local": false

IMPORTANT: The file_path must be a raw URL (raw.githubusercontent.com) that directly serves file content."""

            # Generate completion with JSON format
            response = self.llm_provider.generate_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.2,
                max_tokens=800,
                json_format=True
            )

            # Ensure we got a valid response
            if not response or not isinstance(response, dict):
                logger.error("❌ Invalid reasoning response format")
                return self._create_fallback_response(context)

            # Ensure file_path is included
            if "file_path" not in response:
                logger.warning("⚠️ No file_path in reasoning response, using fallback")
                return self._create_fallback_response(context)

            # Validate local file path or convert to raw URL
            if response.get("is_local", False):
                file_path = response["file_path"]
                if os.path.exists(file_path):
                    logger.info(f"🔍 Next local file: {file_path}")
                    return response
                else:
                    logger.warning(f"⚠️ Local file doesn't exist: {file_path}, trying fallback")
                    return self._create_fallback_response(context)
            else:
                # Handle remote URL case
                raw_url = self._ensure_raw_github_url(response["file_path"])
                if not raw_url:
                    logger.warning("⚠️ Could not convert to valid raw URL, using fallback")
                    return self._create_fallback_response(context)

                response["file_path"] = raw_url
                logger.info(f"🔍 Next remote URL: {raw_url}")
                return response

        except Exception as e:
            logger.error(f"❌ Error during reasoning: {e}")
            return self._create_fallback_response(context)

    def _ensure_raw_github_url(self, url: str) -> str:
        """
        Convert a GitHub URL to its raw format and validate it.

        Args:
            url: GitHub URL (could be webpage or raw format)

        Returns:
            Raw GitHub URL or empty string if conversion fails
        """
        try:
            if not url or not isinstance(url, str):
                return ""

            # If it's already a raw URL, validate and return
            if "raw.githubusercontent.com" in url:
                if self._is_valid_raw_url(url):
                    return url
                else:
                    logger.warning(f"⚠️ Invalid raw URL format: {url}")
                    return ""

            # Convert github.com URLs to raw format
            if "github.com" in url:
                # Handle blob URLs: github.com/user/repo/blob/branch/file -> raw.githubusercontent.com/user/repo/branch/file
                if "/blob/" in url:
                    raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
                    if self._is_valid_raw_url(raw_url):
                        return raw_url

                # Handle tree URLs (directory views) - try to find README
                if "/tree/" in url:
                    # Convert tree URL to README.md in that directory
                    base_url = url.replace("github.com", "raw.githubusercontent.com").replace("/tree/", "/")
                    if not base_url.endswith("/"):
                        base_url += "/"
                    readme_url = base_url + "README.md"
                    if self._is_valid_raw_url(readme_url):
                        return readme_url

                # Try to construct a raw URL for common documentation files
                # Extract user/repo from URL
                parts = url.split("/")
                if len(parts) >= 5 and "github.com" in parts:
                    github_index = next(i for i, part in enumerate(parts) if "github.com" in part)
                    if github_index + 2 < len(parts):
                        user = parts[github_index + 1]
                        repo = parts[github_index + 2]

                        # Try common documentation files with main/master branches
                        for branch in ["main", "master"]:
                            for doc_file in ["README.md", "INSTALL.md", "docs/deployment.md", "docs/installation.md"]:
                                candidate_url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{doc_file}"
                                if self._is_valid_raw_url(candidate_url):
                                    return candidate_url

            logger.warning(f"⚠️ Could not convert URL to raw format: {url}")
            return ""

        except Exception as e:
            logger.error(f"❌ Error converting URL to raw format: {e}")
            return ""

    def _is_valid_raw_url(self, url: str) -> bool:
        """
        Validate if a URL is a properly formatted raw GitHub URL.

        Args:
            url: URL to validate

        Returns:
            True if valid raw GitHub URL, False otherwise
        """
        try:
            if not url or not isinstance(url, str):
                return False

            # Must be raw.githubusercontent.com
            if not url.startswith("https://raw.githubusercontent.com/"):
                return False

            # Basic URL structure validation
            parts = url.replace("https://raw.githubusercontent.com/", "").split("/")
            if len(parts) < 3:  # user/repo/branch/...
                return False

            # Check for valid characters (basic validation)
            user, repo, branch = parts[0], parts[1], parts[2]
            if not all([user, repo, branch]):
                return False

            # Must have a file path (at least one more component)
            if len(parts) < 4:
                return False

            return True

        except Exception as e:
            logger.error(f"❌ Error validating raw URL: {e}")
            return False

    def _create_fallback_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a fallback response with a local file or basic raw GitHub URL.

        Args:
            context: Current search context

        Returns:
            Dictionary with fallback reasoning and file path
        """
        # Try local files first if available
        available_files = context.get("available_files", [])
        searched_files = [item.get("file_path", "") for item in context.get("search_history", [])]

        # Find an unexamined local file
        for file_info in available_files:
            file_path = file_info["absolute_path"]
            if file_path not in searched_files and os.path.exists(file_path):
                return {
                    "reasoning": f"Error occurred during reasoning, using fallback to check unexamined local file: {file_info['relative_path']}",
                    "file_path": file_path,
                    "is_local": True
                }

        # Fallback to remote URL if no local files
        project_name = context.get("project_name", "unknown")
        fallback_urls = [
            f"https://raw.githubusercontent.com/{project_name}/{project_name}/main/README.md",
            f"https://raw.githubusercontent.com/{project_name}/{project_name}/master/README.md",
            f"https://raw.githubusercontent.com/{project_name.lower()}/{project_name.lower()}/main/README.md",
        ]

        for url in fallback_urls:
            if self._ensure_raw_github_url(url):
                return {
                    "reasoning": f"Error occurred during reasoning, using fallback URL to check main README for {project_name}",
                    "file_path": url,
                    "is_local": False
                }

        # Ultimate fallback
        return {
            "reasoning": f"Using generic fallback for {project_name}",
            "file_path": f"https://raw.githubusercontent.com/search/{project_name}/main/README.md",
            "is_local": False
        }

    def _execute_search_action(self, search_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute search action based on the reasoning output.
        Supports both local files and remote URLs.

        Args:
            search_plan: Dictionary with file path, reasoning, and type

        Returns:
            List of content results
        """
        try:
            file_path = search_plan.get("file_path", "")
            is_local = search_plan.get("is_local", False)

            if not file_path:
                return []

            if is_local:
                # Handle local file
                logger.info(f"📖 Reading local file: {file_path}")
                return self._read_local_file(file_path)
            else:
                # Handle remote URL
                logger.info(f"🌐 Fetching remote content: {file_path}")
                return self._fetch_remote_content(file_path)

        except Exception as e:
            logger.error(f"❌ Error during search action execution: {e}")
            return []

    def _read_local_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Read content from a local file.

        Args:
            file_path: Absolute path to the local file

        Returns:
            List containing file content result
        """
        try:
            if not os.path.exists(file_path):
                logger.warning(f"⚠️ Local file doesn't exist: {file_path}")
                return []

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if not content.strip():
                logger.warning(f"⚠️ Local file is empty: {file_path}")
                return []

            file_name = os.path.basename(file_path)
            relative_path = file_path  # Could be improved to show relative to repo root

            logger.success(f"✅ Successfully read local file: {file_name} ({len(content)} chars)")

            return [{
                "title": f"Local File: {file_name}",
                "content": content,
                "url": f"file://{file_path}",
                "source": "local_file"
            }]

        except Exception as e:
            logger.error(f"❌ Error reading local file {file_path}: {e}")
            return []

    def _fetch_remote_content(self, url: str) -> List[Dict[str, Any]]:
        """
        Fetch content from a remote URL.

        Args:
            url: Remote URL to fetch

        Returns:
            List containing fetched content result
        """
        try:
            # Use ContentCleaner to fetch and clean content from the URL
            title = f"Remote Content: {os.path.basename(url)}"

            content = self.content_cleaner.clean_url(url, clean=False)

            if not content:
                logger.warning(f"⚠️ Failed to fetch content from {url}")
                return []

            logger.success(f"✅ Successfully fetched remote content: {len(content)} chars")

            # Return the content in a format similar to search results
            return [{
                "title": title,
                "content": content,
                "url": url,
                "source": "remote_url"
            }]

        except Exception as e:
            logger.error(f"❌ Error fetching remote content from {url}: {e}")
            return []

    def _process_search_results(self, search_results: List[Dict[str, Any]], project_name: str) -> Dict[str, Any]:
        """
        Process and analyze search results.

        Args:
            search_results: List of search results
            project_name: Name of the project

        Returns:
            Observation dictionary with analyzed results
        """
        if not search_results:
            return {
                "found_results": False,
                "valuable_content": None,
                "is_deployment_guide": False,
                "reasoning": "No search results found."
            }

        try:
            # Combine search results for analysis
            combined_content = "\n\n---\n\n".join([
                f"Title: {result.get('title', 'Untitled')}\n\n{result.get('content', '')}"
                for result in search_results[:3]  # Limit to top 3 results
            ])

            # Clean the content using ContentCleaner
            cleaned_content = ""
            for result in search_results[:3]:
                title = result.get('title', 'Untitled')
                content = result.get('content', '')
                if content:
                    cleaned_content += f"## {title}\n\n{content}\n\n---\n\n"

            # Use LLM to analyze the search results
            system_prompt = """You are an expert at analyzing search results to identify deployment instructions.

Evaluate the provided search results and determine:
1. If they contain actual deployment instructions (not just references)
2. How relevant they are to the target project
3. What specific deployment steps are covered
4. What's most valuable to extract for a deployment guide

Focus on practical, actionable deployment steps like:
- Environment setup
- Installation commands
- Configuration options
- Running instructions
- Troubleshooting common issues"""

            user_prompt = f"""Analyze these search results about deploying {project_name}:

{cleaned_content[:8000]}  # Limit content to avoid token limits

Provide your analysis as a JSON object with these fields:
1. "is_deployment_guide": boolean - true if this contains actual deployment steps
2. "relevance_score": number (0-10) - how relevant to {project_name} deployment
4. "reasoning": string - your reasoning about the quality and relevance of these results
5. "source": string - the most valuable source URL if available
6. "title": string - a descriptive title for the valuable content

Example:
```json
{{
  "is_deployment_guide": true,
  "relevance_score": 8,
  "reasoning": "Contains specific npm commands for this Node.js project",
  "source": "https://example.com/docs/deployment",
  "title": "Official Deployment Guide"
}}
```"""

            # Generate analysis with JSON format
            analysis = self.llm_provider.generate_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
                max_tokens=1500,
                json_format=True
            )

            if not analysis or not isinstance(analysis, dict):
                logger.warning("⚠️ Invalid analysis format, using default analysis")
                return {
                    "found_results": True,
                    "valuable_content": cleaned_content,
                    "is_deployment_guide": False,
                    "reasoning": "Unable to properly analyze results.",
                    "title": f"{project_name} Deployment Information"
                }
            analysis["valuable_content"] = cleaned_content
            analysis["found_results"] = True


            # Log the analysis result
            logger.info(f"📊 Analysis - Deployment guide: {analysis.get('is_deployment_guide', False)}, " +
                        f"Relevance: {analysis.get('relevance_score', 0)}/10")

            return analysis

        except Exception as e:
            logger.error(f"❌ Error during result processing: {e}")
            return {
                "found_results": True,
                "valuable_content": "\n\n".join([r.get("content", "")[:500] for r in search_results[:2]]),
                "is_deployment_guide": False,
                "reasoning": f"Error during analysis: {e}",
                "title": f"{project_name} Search Results (Error during analysis)"
            }

    def _compile_deployment_guide(self, project_name: str, collected_information: List[Dict[str, Any]]) -> str:
        """
        Compile collected information into a comprehensive deployment guide.

        Args:
            project_name: Name of the project
            collected_information: List of collected information items

        Returns:
            Compiled deployment guide as markdown
        """
        if not collected_information:
            return f"# {project_name} Deployment Guide\n\nNo specific deployment information was found."

        try:
            # Prepare content for LLM synthesis
            content_for_synthesis = []
            for item in collected_information:
                content = item.get("content", "")
                if content:
                    # Truncate each item to avoid token limits
                    source = item.get("source", "")
                    source_info = f" (Source: {source})" if source else ""

                    content_for_synthesis.append(f"## {item.get('title', 'Information')}{source_info}\n\n{content}")

            combined_content = "\n\n---\n\n".join(content_for_synthesis)

            # Use LLM to synthesize a coherent deployment guide
            system_prompt = """You are a technical documentation expert.
Your task is to synthesize scattered deployment information into a clear, comprehensive deployment guide.

Create a well-structured Markdown document with:
1. A clear introduction
2. Prerequisites section listing all requirements
3. Pre-installation verification steps - IMPORTANT: Always include commands/steps to check if components are already installed
4. Step-by-step installation instructions that begin with verifying if the software is already installed
5. Configuration details with examples
6. Running/deployment instructions
7. Troubleshooting section for common issues
8. References section citing sources

For every software component or dependency:
- ALWAYS include verification commands to check if it's already installed (e.g., `command --version`, `which command`, `npm list -g package`)
- Include expected output from verification commands
- Only proceed with installation if the verification shows the component is missing or outdated
- Provide clear instructions on what to do if different versions are detected

Use proper Markdown formatting:
- Clear section headings (##, ###)
- Code blocks with language specification (```bash, ```yaml)
- Lists for sequential steps
- Bold for important notes

Focus on being practical, accurate and comprehensive."""

            user_prompt = f"""Synthesize the following information into a complete deployment guide for {project_name}.
Resolve any contradictions and create a coherent guide that someone could follow to deploy the project.

{combined_content}

Create a comprehensive deployment guide with:
1. Introduction to deploying {project_name}
2. Prerequisites and dependencies
3. Pre-installation verification checks for all components
4. Step-by-step installation 
5. Configuration
6. Running/deployment steps
7. Troubleshooting common issues
8. References to information sources

Format the output as a well-structured Markdown document."""

            # Generate deployment guide
            try:
                synthesized_guide = self.llm_provider.generate_completion(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=0.2,
                    # max_tokens=4000
                )

                if synthesized_guide and len(synthesized_guide) > 200:
                    logger.success("✅ Successfully synthesized deployment guide")
                    return f"# {project_name} Deployment Guide\n\n{synthesized_guide}"
            except Exception as synth_error:
                logger.error(f"❌ Error synthesizing guide: {synth_error}")

            # If synthesis fails, fall back to simple concatenation
            logger.warning("⚠️ Guide synthesis failed, falling back to simple compilation")
            simple_guide = f"# {project_name} Deployment Guide\n\n"
            simple_guide += "## Introduction\n\n"
            simple_guide += f"This guide provides instructions for deploying {project_name}.\n\n"

            for item in collected_information:
                simple_guide += f"## {item.get('title', 'Deployment Information')}\n\n"
                source = item.get("source", "")
                if source:
                    simple_guide += f"*Source: {source}*\n\n"
                simple_guide += f"{item.get('content', '')}\n\n"

            return simple_guide

        except Exception as e:
            logger.error(f"❌ Error compiling deployment guide: {e}")

            # Create a very basic guide with whatever we have
            basic_guide = f"# {project_name} Deployment Guide\n\n"
            basic_guide += "## Deployment Information\n\n"

            for item in collected_information:
                basic_guide += f"### {item.get('title', 'Information')}\n\n"
                basic_guide += f"{item.get('content', '')[:1000]}\n\n"

            return basic_guide
