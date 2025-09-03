"""
Prompts for Project API Platform - LLM-based analysis and script generation.
Includes prompts for project function analysis, script generation, and environment setup.
"""

# Comprehensive Project Analysis Prompt - Simplified and focused
COMPREHENSIVE_PROJECT_ANALYSIS_PROMPT = """
你是开源项目API标准化专家。分析usage_md中的功能并转换为支持标准化输入输出格式的API。

**🚨 标准化约束**
- **usage_md是功能发现的唯一来源**
- **只能分析usage_md中明确提到的功能**
- **所有API将使用统一的输入输出格式：input + output_path**
- **input参数支持文本内容或文件路径，脚本内部自动判断**
- **复杂功能参数将被硬编码，不对外暴露**

**Project Path:** {project_path}

**📋 STEP 1: USAGE DOCUMENTATION ANALYSIS (ONLY SOURCE FOR FUNCTIONS):**
```markdown
{usage_md}
```

**🔍 STEP 1.5: FUNCTION ENUMERATION (REQUIRED BEFORE CONTINUING)**
Before proceeding, list each distinct function/command found in usage_md:
1. Scan usage_md for executable commands, function calls, or operations
2. Identify unique functionalities (not setup/installation commands)
3. Each identified function MUST have a clear usage example in the documentation above

**📖 STEP 2: CONTEXT INFORMATION (IMPLEMENTATION ASSISTANCE ONLY - DO NOT EXTRACT FUNCTIONS):**

**🗂️ PROJECT STRUCTURE (FOR UNDERSTANDING PROJECT LAYOUT ONLY):**
```
{project_structure}
```

**📊 STEP 3: FUNCTION COUNT VERIFICATION**
Count the exact number of distinct functions/commands described in the usage_md above. Your JSON output MUST contain exactly this number in the functions array.

**OUTPUT REQUIREMENT: RETURN ONLY VALID JSON**
```json
{{
  "functions_count_from_usage_md": 0,
  "project_type": "inferred_type_from_usage",  
  "main_language": "python|javascript|java|go|shell|other",
  "functions": [
    {{
      "name": "function_name_from_usage_md",
      "description": "What this function does according to usage_md", 
      "parameters": [
        {{
          "name": "input",
          "type": "string",
          "description": "输入内容（文本内容或文件路径）",
          "required": true,
          "default": null
        }},
        {{
          "name": "output_path",
          "type": "string", 
          "description": "输出文件路径",
          "required": true,
          "default": null
        }}
      ],
      "command_template": "EXACT command generated from usage_md",
      "expected_output": "Brief output description from usage_md",
      "examples": ["exact example from usage_md"],
      "script_type": "python|shell|node|java|go|docker|curl|custom",
      "cli_mappings": {{
        "input": {{
          "type": "positional", 
          "flag": "",
          "description": "位置参数：输入内容或文件路径"
        }},
        "output_path": {{
          "type": "option", 
          "flag": "-o",
          "description": "输出文件路径选项"
        }}
      }}
    }}
  ],
  "runtime_environment": {{
    "type": "conda|uv|poetry|venv|system|docker",
    "name": "env_name_if_detected",
    "activation_command": "activation_command_if_found", 
    "confidence": "high|medium|low"
  }},
  "main_entry": "primary_executable",
  "confidence": "high"
}}
```

**⚠️ CRITICAL VALIDATION: Before outputting JSON, verify that:**
1. `functions_count_from_usage_md` equals the length of `functions` array
2. Every function in the array has a clear source in usage_md
3. No functions were added from README or project structure

**CLI Mapping Rules:**
- **option**: `--flag value` or `-f value`
- **positional**: arguments without flags
- **boolean_flag**: `--enable` or `--verbose` (no value)

**标准化格式示例:**
原始命令: `tts --text "hello" --voice female --output file.wav`
标准化后: `tts "hello" -o file.wav` （voice参数硬编码为female）
```json
"cli_mappings": {{
  "input": {{"type": "positional", "flag": "", "description": "输入内容"}},
  "output_path": {{"type": "option", "flag": "-o", "description": "输出文件"}}
}}
```

**核心理念**: 
- 所有复杂参数统一硬编码到生成的脚本中
- API调用者只需关心输入和输出，无需了解内部参数配置
- 选择最优默认参数确保高质量输出

**Function Filtering:**
- ✅ **INCLUDE**: Core processing, analysis, conversion, generation functions
- ❌ **EXCLUDE**: Installation, build, test, deployment commands

**Critical Rules:**
1. Copy commands EXACTLY from usage_md
2. Extract parameters ONLY from usage examples
3. Use README/structure for implementation context only
4. Focus on actual work functions, not setup commands
5. Deduplicate similar functions (choose best interface)

**🛡️ FINAL VALIDATION CHECKPOINT - MANDATORY VERIFICATION:**

Before submitting your JSON response, you MUST verify:

1. **Function Count Match**: 
   - Count functions in usage_md again
   - Verify `functions_count_from_usage_md` equals `functions` array length
   - If counts don't match, REMOVE or ADD functions to make them equal

2. **Source Verification**:
   - Every function MUST have a clear command/example in usage_md
   - NO function should come from README or project structure
   - Each function name must be traceable to usage_md content

3. **Zero Tolerance Policy**:
   - If you find any function not in usage_md, DELETE it immediately
   - If usage_md has more functions than your array, ADD the missing ones
   - Function count consistency is MANDATORY, not optional

**Remember: The returned function count MUST exactly match usage_md functions. No exceptions.**
"""

# Project Classification Prompt - 区分原生结构化输出项目
PROJECT_CLASSIFICATION_PROMPT = """
Analyze the project to determine if it has native structured output capabilities.

**Project:** {project_name}

**Usage Documentation:**
```
{usage_md}
```

**Classification Criteria:**

**🟢 HAS STRUCTURED OUTPUT** - Projects with native structured data interfaces:
- Python libraries with importable APIs (from X import Y)
- REST APIs that return JSON/XML
- Tools that natively output structured formats (JSON, XML, YAML, CSV)
- Libraries with direct function calls returning objects/dictionaries

**🔴 NO STRUCTURED OUTPUT** - Projects with only CLI/text output:
- Command-line tools that only output text/logs
- Tools that mix logs with results in stdout
- Shell scripts without structured return formats
- Tools requiring text parsing to extract results

**Examples:**

**✅ HAS STRUCTURED OUTPUT:**
```python
from markitdown import MarkItDown  # Python API available
markitdown = MarkItDown()
result = markitdown.convert("file.pdf")  # Returns structured object
```

**❌ NO STRUCTURED OUTPUT:**
```bash
some-cli-tool file.pdf  # Only outputs mixed text/logs to stdout
```

Return JSON:
```json
{{
  "class": "structured_api|cli_only",
  "has_structured_output": true|false,
  "reasoning": "explanation of classification",
  "confidence": "high|medium|low",
  "recommended_approach": "direct_api_call|subprocess_with_cleanup"
}}
```
"""

# Simple API Detection Prompt
SIMPLE_API_DETECTION_PROMPT = """
Analyze whether this project has a Python API that can be called directly.

**Project Info:** {project_name}
**Usage Documentation:**
```
{usage_md}
```

Look for Python import statements like: `from paddleocr import PaddleOCR`, `import markitdown`, `from X import Y`

Return JSON:
```json
{{
  "has_python_api": true,
  "import_statement": "from markitdown import MarkItDown",
  "main_class": "MarkItDown", 
  "confidence": "high"
}}
```
"""

# Simple Script Generation Prompt  
SIMPLE_SCRIPT_GENERATION_PROMPT = """
Generate Python script for the function with original output format.

**Function:** {function_name}
**Command:** {command_template}
**Parameters:** {parameters}
**API Info:** {api_info}

Script generation requirements:
1. If Python API available, call directly and output original results
2. Otherwise use subprocess to call original command and pass through output
3. No JSON wrapping, no status objects

Return JSON:
```json
{{
  "script_content": "#!/usr/bin/env python3\n# Complete script content"
}}
```
"""

# LLM Smart Function Deduplication Prompt - Identify duplicate functions from product perspective
FUNCTION_DEDUPLICATION_PROMPT = """
You are a product manager analyzing software functions. Your task is to identify and eliminate duplicate functions that achieve the same business outcome, regardless of their technical implementation.

**Functions to analyze:**
```json
{functions_data}
```

**Deduplication Criteria (Product Perspective):**

🎯 **Same Business Outcome = Duplicate**
- Functions that produce the same end result for users
- Different technical paths to achieve identical goals
- Multiple interfaces for the same underlying functionality

**🚫 CRITICAL EXCEPTION: Version Difference Preservation Rule**

If usage_md explicitly mentions different versions of the same functionality, ALL versions MUST be preserved and NOT deduplicated:

**Version Identifiers Include**:
- Explicit version numbers: v1.0, v2.0, v3.0, version 1, version 2, PP-OCRv5, ChatOCRv4, etc.
- Version descriptors: old version, new version, legacy version, latest version, upgraded version, enhanced version
- Generation indicators: 1st generation, 2nd generation, next generation, new generation
- Version suffixes: _v1, _v2, _old, _new, _plus, _pro, _lite, etc.

**Version Preservation Principles**:
- Different versions may have different parameters, performance characteristics, or compatibility requirements
- Users may need to choose appropriate versions based on specific scenarios
- Even if function names are similar, ALL versions should be preserved when version identifiers are present

**Examples of Duplicates:**
- `convert_pdf_to_text()` + `pdf_text_extraction()` = Same outcome: extract text from PDF
- `analyze_document()` + `document_analysis()` = Same outcome: analyze document content  
- `process_file(type="pdf")` + `pdf_processor()` = Same outcome: process PDF files
- `api_call(endpoint="/search")` + `search_function()` = Same outcome: search functionality

**NOT Duplicates:**
- `convert_pdf_to_text()` vs `convert_pdf_to_html()` = Different outcomes
- `analyze_sentiment()` vs `analyze_grammar()` = Different types of analysis
- `upload_file()` vs `download_file()` = Opposite operations

**Version-Related Exceptions**:
- `convert_pdf_v1()` vs `convert_pdf_v2()` = Different versions, MUST preserve both
- `PP-OCRv4` vs `PP-OCRv5` = Version upgrade with enhanced functionality, MUST preserve both  
- `analyze_old()` vs `analyze_new()` = Old vs new versions, MUST preserve both
- `process_legacy()` vs `process_plus()` = Different version positioning, MUST preserve both

**Selection Rules:**
1. **Most Complete Interface**: Choose the function with more comprehensive parameters
2. **Clearest Intent**: Prefer functions with clear, business-focused names
3. **Better Integration**: Choose the most API-friendly interface
4. **User Perspective**: Which function would users naturally expect?

**Your Task:**
1. **First Check for Version Information**: Carefully analyze usage_md and function descriptions for version identifiers
2. **Version Preservation Priority**: For functions with version identifiers, preserve ALL versions regardless of name similarity
3. **Business Logic Deduplication**: Only deduplicate truly duplicate functions that have no version differences
4. **Select Best Representative**: For confirmed duplicate function groups, choose the best representative function
5. **Detailed Reasoning**: Explain why certain functions were preserved or merged

**CRITICAL OUTPUT REQUIREMENT: RESPOND ONLY WITH VALID JSON**
- Your response MUST be valid JSON format only
- NO explanatory text before or after the JSON
- NO markdown code blocks around the JSON
- NO additional commentary
- If you cannot provide JSON, return {{"error": "reason"}}

Return JSON:
```json
{{
  "deduplicated_functions": [
    {{
      "name": "selected_function_name",
      "description": "what this function does",
      "command_template": "exact_command_from_original",
      "parameters": [...],
      "examples": [...],
      "script_type": "...",
      "expected_output": "...",
      "selection_reason": "Why this function was chosen over alternatives"
    }}
  ],
  "removed_duplicates": [
    {{
      "original_name": "removed_function",
      "merged_into": "selected_function_name", 
      "reason": "Both functions achieve the same business outcome: ..."
    }}
  ],
  "deduplication_summary": {{
    "original_count": 0,
    "final_count": 0,
    "duplicates_removed": 0
  }}
}}
```

**Remember**: Focus on USER VALUE and BUSINESS OUTCOMES, not technical implementation details.
"""


# Test Case Fix Prompt - LLM intelligent fixing of failed test cases
TEST_CASE_FIX_PROMPT = """
You are an expert test case designer and fixer. A test case has failed and needs to be fixed based on the failure analysis.

**Original Script Information:**
- Script Name: {script_name}
- Script Type: {script_type}
- Function Description: {function_description}

**Script Content (for reference):**
```{script_type}
{script_content}
```

**Failed Test Case:**
```json
{original_test_case}
```

**Test Failure Information:**
- Failed Test: {test_name}
- Error Output: {error_output}
- Stdout Output: {stdout_output}
- Exit Code: {exit_code}
- Timeout: {timeout}

**Failure Diagnosis:**
```json
{diagnosis_info}
```

**Project Context:**
- Project Path: {project_path}

**Available Project Files:**
{available_files}

**Test Case Fix Guidelines:**

1. **File Path Issues**: 
   - Check if files referenced in test case actually exist
   - Use relative paths that work from the script execution directory
   - Replace non-existent files with actual available files from the project

2. **Parameter Issues**:
   - Fix command line arguments that don't match script's expected parameters
   - Correct flag names, positional arguments, and parameter formats
   - Ensure parameter values are valid and appropriate

3. **Command Structure Issues**:
   - Fix the command syntax to match the script's actual interface
   - Ensure proper shell escaping and quoting
   - Correct the command path and execution method

4. **Timeout Issues**:
   - Adjust timeout values to be more realistic for the operation
   - Consider the complexity of the task when setting timeouts

5. **Expected Output Issues**:
   - Fix expected_output_type if it doesn't match actual script behavior
   - Adjust expected_behavior (success/error/warning) based on the test scenario
   - Ensure output expectations are realistic and achievable

6. **Working Directory Issues**:
   - Ensure file paths work from the correct working directory
   - Use absolute paths when necessary

**Fix Strategy Based on Diagnosis:**
- If diagnosis suggests "test_case_issue": Focus on fixing test case parameters, file paths, and expectations
- If diagnosis suggests "script_issue": The test case might be correct, suggest minimal changes
- If diagnosis suggests "environment_issue": Fix paths and environment-related parameters in test case

**CRITICAL OUTPUT REQUIREMENT: RESPOND ONLY WITH VALID JSON**
- Your response MUST be valid JSON format only
- NO explanatory text before or after the JSON
- NO markdown code blocks around the JSON
- NO additional commentary
- If you cannot provide JSON, return {{"error": "reason"}}

Please provide the fixed test cases in the following JSON format:

```json
{{
  "fixed_test_cases": [
    {{
      "name": "descriptive_test_case_name",
      "description": "What this test case validates",
      "command": "fixed_executable_command_here",
      "input": {{
        "description": "what inputs this test case simulates"
      }},
      "expected_output_type": "any|json|text|number|boolean",
      "expected_behavior": "success|error|warning",
      "timeout": 30,
      "notes": "What was fixed and why"
    }}
  ],
  "fix_description": "Detailed description of what was changed in the test cases",
  "changes_made": [
    "List of specific changes made",
    "Another change made"
  ],
  "file_dependencies": [
    {{
      "file_path": "relative/path/to/file.pdf",
      "purpose": "Used for testing functionality",
      "exists": true,
      "changed": "replaced_with_existing_file"
    }}
  ],
  "confidence": "high|medium|low"
}}
```

**Requirements:**
- Fix the specific issues identified in the diagnosis
- Ensure all file paths point to existing files from the available files list
- Make sure commands are executable and syntactically correct
- Adjust timeout values appropriately
- Ensure expected behaviors match what the script actually does
- Provide clear explanation of changes made
- Maintain the original test intent while fixing execution issues

**Important Notes:**
- Always verify file paths against the available files list
- Test commands must be realistic and executable
- Consider the script's actual functionality when setting expectations
- Fix root causes, not just symptoms
- Make minimal changes necessary to fix the issues
"""


# Script Fix Prompt - LLM intelligent fixing of failed scripts
SCRIPT_FIX_PROMPT = """
You are an expert script debugger and fixer. A generated script has failed during testing and needs to be fixed.

**Original Script Information:**
- Script Name: {script_name}
- Script Type: {script_type}
- Function Description: {function_description}

**Original Script Content:**
```{script_type}
{script_content}
```

**Test Failure Information:**
- Failed Test: {test_name}
- Error Output: {error_output}
- Exit Code: {exit_code}
- Timeout: {timeout}

**Project Context:**
- Project Path: {project_path}

{additional_context}

**Analysis Guidelines:**
1. **Error Analysis**: Identify the root cause of the failure
2. **Environment Issues**: Check for missing dependencies, paths, permissions
3. **Logic Errors**: Fix any programming errors in the script
4. **Timeout Issues**: Optimize performance or add proper timeouts
5. **Compatibility**: Ensure script works in the target environment

**Common Fix Strategies:**
- Add missing error handling
- Fix file paths and permissions
- Install missing dependencies
- Improve script performance
- Add proper environment setup
- Fix syntax errors
- Handle edge cases

**CRITICAL OUTPUT REQUIREMENT: RESPOND ONLY WITH VALID JSON**
- Your response MUST be valid JSON format only
- NO explanatory text before or after the JSON
- NO markdown code blocks around the JSON
- NO additional commentary
- If you cannot provide JSON, return {{"error": "reason"}}

Please provide the fixed script in the following JSON format:

```json
{{
  "fixed_script_content": "Complete fixed script content as a string",
  "script_type": "python|shell|node|java|go|docker|curl|custom",
  "fix_description": "Detailed description of what was fixed and why",
  "test_cases": [
    {{
      "name": "test_case_name",
      "input": {{"parameter1": "value1"}},
      "expected_output_type": "json|string|number",
      "timeout": 30
    }}
  ],
  "additional_dependencies": ["any additional dependencies needed"],
  "environment_setup": ["any additional setup steps required"],
  "confidence": "high|medium|low"
}}
```

**Requirements:**
- The fixed script must address the specific failure
- Include comprehensive error handling
- Ensure the script is robust and handles edge cases
- Maintain the original functionality while fixing the issues
- Provide clear explanation of changes made
"""


# Test Case Generation Prompt - Intelligent generation of test cases based on project files (limited to 2)
GENERATE_TEST_CASES_PROMPT = """
You are an expert test case generator. Based on a generated script and the actual project structure, generate exactly 2 comprehensive test cases with complete executable commands.

**Generated Script Information:**
- **Function Name:** {function_name}
- **Script Type:** {script_type}
- **Script Path:** {script_path}
- **Base Command:** {base_command}
- **Script Content:**
```{script_type}
{script_content}
```

**Project Information:**
- **Project Path:** {project_path}
- **Function Description:** {function_description}
- **Function Parameters:** {function_parameters}

**Available Project Files:**
{available_files}

**Test Case Generation Guidelines:**

1. **Generate Exactly 2 Test Cases**: One for happy path and one for edge/error case
2. **Analyze Script Content**: Carefully read the script to understand what parameters it accepts
3. **Generate Complete Commands**: Create full executable commands based on the script's actual functionality
4. **File-Based Testing**: Prioritize using actual project files found in the file structure
5. **Smart File Selection**: 
   - For PDF processing functions: Use actual PDF files found in the project
   - For text processing: Use actual text/markdown files
   - For data processing: Use actual CSV/JSON files
   - For configuration: Use actual config files (.yml, .json, .ini)

6. **Path Resolution Strategy**:
   - Use relative paths when files are within the project directory
   - Use absolute paths for files outside the project (parent directories)
   - Ensure paths work from the script execution context

7. **Test Case Variety**:
   - **Test Case 1 (Happy Path)**: Normal successful execution with valid files/parameters
   - **Test Case 2 (Edge/Error Case)**: Error handling, edge cases, or parameter validation

8. **Realistic Scenarios**:
   - Base test cases on actual project usage patterns
   - Use realistic parameter combinations
   - Consider common user workflows

**CRITICAL: Command Generation Rules - CLEAN WRAPPER SCRIPT CALLS ONLY**
- You MUST generate commands that call the WRAPPER SCRIPT at {script_path}
- DO NOT call original project commands - only call the wrapper script
- Use the base_command as starting point: {base_command}
- Example CORRECT format: "python /path/to/wrapper_script.py --param value"
- Example WRONG format: "conda run -n env python script.py" (DO NOT ADD ENVIRONMENT COMMANDS)
- Example WRONG format: "/original/python markitdown file.pdf" (DO NOT DO THIS)
- The wrapper script is what we're testing, not the original project
- Analyze the wrapper script content to understand what parameters it accepts
- Test commands must be realistic and executable with the wrapper script
- **CRITICAL**: DO NOT include environment activation commands (conda run, poetry run, etc.) in test commands
- Environment activation is handled externally by the caller

**CRITICAL OUTPUT REQUIREMENT: RESPOND ONLY WITH VALID JSON**
- Your response MUST be valid JSON format only
- NO explanatory text before or after the JSON
- NO markdown code blocks around the JSON
- NO additional commentary
- If you cannot provide JSON, return {{"error": "reason"}}

Please provide exactly 2 test cases in the following JSON format:

```json
{{
  "test_cases": [
    {{
      "name": "descriptive_test_case_name",
      "description": "What this test case validates",
      "command": "complete_executable_command_here",
      "input": {{
        "description": "what inputs this test case simulates"
      }},
      "expected_output_type": "any|json|text|number|boolean",
      "expected_behavior": "success|error|warning",
      "timeout": 30,
      "notes": "Additional context about this test case"
    }},
    {{
      "name": "second_test_case_name", 
      "description": "What the second test case validates",
      "command": "complete_executable_command_for_second_test",
      "input": {{
        "description": "what inputs this test case simulates"
      }},
      "expected_output_type": "any|json|text|number|boolean", 
      "expected_behavior": "success|error|warning",
      "timeout": 30,
      "notes": "Additional context about this test case"
    }}
  ],
  "file_dependencies": [
    {{
      "file_path": "relative/path/to/file.pdf",
      "purpose": "Used for testing PDF processing functionality",
      "exists": true
    }}
  ],
  "estimated_success_rate": "high|medium|low"
}}
```

**Important Notes**:
- Generate exactly 2 test cases, no more, no less
- Each test case MUST have a complete `command` field that can be executed directly
- Analyze the script content carefully to understand what parameters it accepts
- If no suitable project files are found, generate test cases that create temporary files or use standard inputs
- Always include one test case that should succeed (happy path)
- Include one edge case or error handling test case
- Make sure file paths are correct and accessible from the script execution context
- Commands must be based on actual script functionality, not assumed parameters
- Consider the script's actual functionality when designing test cases
"""


# Intelligent Python Script Generation Prompt - Python-only wrapper script generation
INTELLIGENT_SCRIPT_GENERATION_PROMPT = """
You are an expert Python script generator. Your task is to create a complete, executable Python script that wraps a specific project function based on the actual usage patterns from the documentation. All wrapper scripts must be written in Python, regardless of the original tool's implementation language.

**Function Information:**
- **Function Name:** {function_name}
- **Description:** {function_description}  
- **Command Template:** {command_template}
- **Parameters:** {function_parameters}
- **Script Type:** {script_type}
- **Expected Output:** {expected_output}
- **Examples:** {function_examples}

**Project Context:**
- **Project Name:** {project_name}
- **Project Path:** {project_path}
- **Main Language:** {main_language}

**Environment Information:**
- **Environment Type:** {env_type}
- **Environment Name:** {env_name}
- **Environment Path:** {env_path}
- **Activation Command:** {activation_command}

**API Detection Results:**
{api_info}

**Original Usage Documentation:**
```
{usage_md}
```

**Runtime Environment Details:**
{runtime_environment}

**Python Script Generation Requirements:**

1. **Python-Only Implementation Strategy:**
   - **CRITICAL**: All scripts must be written in Python, regardless of the original tool type
   - If usage shows Python imports/API calls: Use direct Python imports and API calls
   - If usage shows CLI commands: Use Python's subprocess module to call commands
   - If usage shows Docker commands: Use Python subprocess to execute docker commands
   - If usage shows other tools: Wrap them using Python subprocess with proper argument handling

2. **Python Implementation Approaches:**
   - **Direct API calls**: When usage_md shows Python imports, use direct function calls
   - **Subprocess wrapping**: When usage_md shows CLI commands, use subprocess.run() or subprocess.Popen()
   - **Environment handling**: Use Python's os.environ and subprocess environment parameters
   - **Path handling**: Use pathlib.Path for cross-platform path operations

3. **Python Parameter Handling:**
   - Use argparse for professional command-line argument parsing
   - Map parameters according to original usage patterns from usage_md
   - Handle required vs optional parameters with proper argparse configuration
   - Support parameter types (str, int, float, bool, Path) with type conversion
   - Include comprehensive parameter validation and helpful error messages

4. **Python Environment Integration:**
   - Integrate with detected Python environment (conda, venv, uv, etc.)
   - For conda environments: Use subprocess with proper environment activation
   - For virtual environments: Handle activation within the Python script
   - Use os.environ to manage environment variables properly

5. **Python Output Handling:**
   - Preserve original output format using sys.stdout.write() or print()
   - Handle both text and binary output appropriately
   - Capture and forward both stdout and stderr from subprocess calls
   - Don't add JSON wrapping unless specifically requested

6. **Python Script Quality Standards:**
   - Start with proper shebang: #!/usr/bin/env python3
   - Add comprehensive docstring at module level explaining the wrapper purpose
   - Use standard library modules when possible (subprocess, pathlib, argparse, sys, os)
   - Follow PEP 8 style guidelines: 4-space indentation, line length ≤ 88 chars
   - Structure: imports → constants → helper functions → main function → if __name__ == '__main__'
   - Include docstrings for all functions with Args and Returns sections
   - Add helpful comments explaining wrapper logic and environment handling
   - Use type hints where appropriate for better code clarity

7. **Python Error Handling:**
   - Use try-except blocks for comprehensive error handling
   - Handle subprocess.CalledProcessError for command failures
   - Handle FileNotFoundError for missing files or commands
   - Provide meaningful error messages using logging or print() 
   - Exit with appropriate exit codes (0 for success, non-zero for errors)

**Python Implementation Decision Making:**

Based on the usage_md calling patterns, intelligently decide:
- Should this use direct Python API calls or subprocess wrapping?
- How to map command-line arguments to argparse parameters?
- Which Python modules are needed (subprocess, pathlib, argparse, etc.)?
- How to preserve the exact output format users expect through Python?

**CRITICAL**: DO NOT include environment activation commands (conda run, poetry run, etc.) in generated scripts. Environment activation is handled externally.

**Python Script Template Structure:**
```python
#!/usr/bin/env python3
\"\"\"
{function_name} - AutoAPI Python Wrapper
Auto-generated wrapper script for {project_name}.{function_name}
Wraps the original functionality using Python for universal compatibility.
\"\"\"

import argparse
import subprocess
import sys
import os
from pathlib import Path
from typing import Optional, List

def main() -> int:
    \"\"\"Main entry point for {function_name} wrapper.\"\"\"
    parser = create_argument_parser()
    args = parser.parse_args()
    
    try:
        return execute_function(args)
    except Exception as e:
        print(f"Error: {{e}}", file=sys.stderr)
        return 1

def create_argument_parser() -> argparse.ArgumentParser:
    \"\"\"Create and configure argument parser based on original tool parameters.\"\"\"
    # Configure based on usage_md parameters
    pass

def execute_function(args) -> int:
    \"\"\"Execute the wrapped functionality - core logic only, no environment handling.\"\"\"
    # Implementation based on usage_md calling patterns
    # Environment activation is handled externally - script contains only core functionality
    pass

if __name__ == "__main__":
    sys.exit(main())
```

**CRITICAL OUTPUT REQUIREMENT: RESPOND ONLY WITH VALID JSON**
- Your response MUST be valid JSON format only
- NO explanatory text before or after the JSON
- NO markdown code blocks around the JSON
- NO additional commentary
- If you cannot provide JSON, return {{"error": "reason"}}

Generate the complete Python script and return in this JSON format:

```json
{{
  "script_content": "Complete Python script content starting with #!/usr/bin/env python3",
  "script_type": "python",
  "implementation_approach": "api|subprocess|hybrid",
  "key_decisions": {{
    "implementation_method": "Direct API calls or subprocess wrapping based on usage_md",
    "parameter_mapping": "How argparse parameters map to original tool arguments",
    "environment_handling": "How Python script handles the detected environment",
    "error_strategy": "Python error handling strategy matching original tool behavior",
    "output_preservation": "How Python script maintains original output format"
  }},
  "estimated_reliability": "high|medium|low",
  "notes": "Important Python implementation insights and usage_md analysis"
}}
```

**Important Python Guidelines:**
- Generate production-ready, executable Python scripts only
- Use direct API calls when possible, subprocess wrapping when necessary
- Prioritize reliability and preserving original tool behavior through Python
- Make intelligent decisions based on usage_md patterns, implemented in Python
- Ensure the Python script works as a drop-in replacement matching original usage
- Handle edge cases with proper Python exception handling and meaningful error messages
- MOST IMPORTANT: Implement all functionality in Python, regardless of original tool type
- **CRITICAL**: DO NOT include environment activation commands in generated scripts (no conda run, poetry run, etc.)
- Scripts should contain only core functionality - environment activation is handled externally
"""

# 简化的脚本生成提示 - 基于README内容生成调用脚本，强制输出格式规范
ENHANCED_SCRIPT_GENERATION_PROMPT = """
为开源项目生成标准化的Python包装脚本，支持统一的输入输出格式。

**Function信息：**
- 功能名称: {function_name}
- 功能描述: {function_description}
- 调用模板: {command_template}
- 参数列表: {function_parameters}
- 预期输出: {expected_output}
- 使用示例: {function_examples}

**项目使用文档（输入输出参考）：**
```
{usage_md}
```

**项目README（核心实现参考）：**
```
{readme_content}
```

**🚨 标准化要求（强制要求）：**

### 1. **统一参数格式**
- **输入参数**: 支持位置参数（输入内容或文件路径）
- **输出参数**: 统一使用 `-o` 或 `--output` 指定输出文件路径
- **功能参数**: 全部硬编码到脚本内部，选择最佳默认值

### 2. **脚本模板要求**
生成的Python脚本必须遵循以下模板：
```python
#!/usr/bin/env python3
import argparse
import sys
import os
# 其他必要导入

def main():
    parser = argparse.ArgumentParser(description='{function_description}')
    parser.add_argument('input_source', help='输入文本内容或文件路径')
    parser.add_argument('-o', '--output', required=True, help='输出文件路径')
    args = parser.parse_args()
    
    # 判断输入是文件路径还是文本内容
    if os.path.exists(args.input_source):
        # 处理文件输入
        input_content = process_file_input(args.input_source)
    else:
        # 处理文本输入
        input_content = args.input_source
    
    # 核心功能实现（硬编码最佳参数）
    result = execute_function(input_content)
    
    # 保存结果到指定输出路径
    save_output(result, args.output)
    
if __name__ == '__main__':
    main()
```

### 3. **参数硬编码策略**
- 分析usage_md中的所有参数配置
- 选择最常用、最稳定的参数值作为默认配置
- 将复杂配置直接写入脚本，不暴露给API用户
- 优先选择高质量输出的参数组合

**🚨 自包含性要求（严格约束）：**
- 硬编码参数必须完全自包含，无需外部配置
- **严格禁止**使用需要API密钥的参数（如 --use_llm, --gemini_api_key）
- **严格禁止**使用需要外部服务的参数（如 --vertex_project_id, --ollama_base_url）
- **严格禁止**使用需要额外环境变量的参数
- **只使用项目原生功能**，不依赖第三方API或服务
- **优先级**：自包含性 > 功能质量 > 性能

### 4. **实现策略优先级**
1. **Python API直调**：如果README显示Python API，直接调用
2. **CLI包装**：如果只有CLI工具，使用subprocess包装
3. **输出清理**：确保输出纯净，无日志干扰
4. **错误处理**：规范化错误信息，便于API调用方处理

### 5. **🚨 严禁环境激活（重要约束）**
- **绝对禁止**：脚本内部不得包含任何环境激活命令
- **禁止内容**：conda activate、source activate、poetry run等
- **职责分离**：环境激活由外部系统处理，脚本只负责核心功能
- **直接调用**：subprocess.run()直接执行命令，无需环境包装

### 6. **参数选择指南**
**允许的参数类型：**
- ✅ 输出格式控制（如 --output_format markdown）
- ✅ 基础功能开关（如 --force_ocr, --paginate_output）  
- ✅ 文件处理选项（如 --strip_existing_ocr）
- ✅ 性能相关（如超时设置，但无需外部配置的）

**禁止的参数类型：**
- ❌ 需要API密钥（--use_llm, --gemini_api_key, --openai_api_key）
- ❌ 需要外部服务（--vertex_project_id, --ollama_base_url）
- ❌ 需要模型配置（--claude_model_name, --ollama_model）
- ❌ 需要环境变量（依赖GOOGLE_API_KEY等的参数）

**输出JSON格式：**
```json
{{
  "script_content": "完整的Python脚本，支持标准化输入输出格式",
  "script_type": "python", 
  "implementation_approach": "api_direct|cli_with_cleanup",
  "hardcoded_parameters": "说明哪些参数被硬编码及其选择原因，强调自包含性",
  "output_format_handling": "输出格式处理说明"
}}
```

**核心目标**: 生成支持标准化 `input + output_path` 格式的完全自包含脚本。
- **最高优先级**: 自包含性，确保无需任何外部API或服务
- **次要考虑**: 功能质量和输出格式对齐
- **严格禁止**: 任何需要额外配置的参数
- **验证要求**: 生成的脚本必须能够独立运行，无外部依赖
"""

# 格式验证测试用例生成提示 - 专注于输出格式规范验证
FORMAT_VALIDATION_TEST_CASES_PROMPT = """
你是专业的输出格式验证专家。生成测试用例的主要目的是验证功能脚本的输出格式是否符合usage_md要求，确保日志与结果数据清晰分离。

**功能脚本信息:**
- **功能名称:** {function_name}
- **脚本类型:** {script_type}
- **脚本路径:** {script_path}
- **基础命令:** {base_command}
- **预期输出格式:** {expected_output_format}

**脚本内容:**
```{script_type}
{script_content}
```

**项目信息:**
- **项目路径:** {project_path}
- **功能描述:** {function_description}
- **功能参数:** {function_parameters}
- **是否有结构化输出:** {has_structured_output}

**可用项目文件:**
{available_files}

**格式验证测试策略:**

### 1. 原生结构化输出项目 (has_structured_output=True)
**验证重点**: 确保Python API调用返回清晰的结构化数据
- 测试用例应验证输出是纯净的JSON/结构化数据
- 不应包含日志、调试信息或进度提示
- 输出格式必须与usage_md中的expected_output完全对齐

### 2. CLI输出项目 (has_structured_output=False)  
**验证重点**: 确保CLI调用结果经过清理，分离日志和实际结果
- 测试用例应验证脚本能正确分离stdout中的日志和结果
- 检查是否去除了"INFO:", "DEBUG:", "Processing:", "Loading:"等日志前缀
- 确保最终输出为清晰的结果数据

**测试用例生成要求:**

1. **参数限制** (关键约束):
   - 只允许使用`text`和`file_path`两种参数类型
   - 其他复杂参数应在脚本内部固化，不对外暴露
   - 测试命令必须符合这个参数限制

2. **格式验证重点**:
   - 生成能验证输出格式是否符合expected_output的测试用例
   - 重点检查输出中是否混有日志信息
   - 验证输出结构是否规范统一

3. **实际可用性**:
   - 优先使用项目中实际存在的文件进行测试
   - 命令必须是可执行的，参数必须有效
   - 测试场景要贴近实际使用情况

**输出JSON格式:**
```json
{{
  "test_cases": [
    {{
      "name": "format_validation_basic",
      "description": "验证基础功能的输出格式是否符合expected_output要求",
      "command": "python {script_path} --text 'sample input'",
      "input": {{
        "description": "test input description"
      }},
      "expected_output_type": "json|text|structured",
      "expected_behavior": "success",
      "format_validation_focus": "检查输出是否混有日志，是否符合expected_output格式",
      "timeout": 30,
      "notes": "主要验证输出格式规范性"
    }},
    {{
      "name": "format_validation_edge_case",
      "description": "验证边界情况下的输出格式一致性",
      "command": "python {script_path} --file_path 'edge/case/file'",
      "input": {{
        "description": "edge case input"
      }},
      "expected_output_type": "json|text|structured",
      "expected_behavior": "success|error",
      "format_validation_focus": "验证错误情况下输出格式是否仍然规范",
      "timeout": 30,
      "notes": "验证异常情况的输出格式"
    }}
  ],
  "validation_strategy": "基于has_structured_output={has_structured_output}的格式验证策略",
  "parameter_constraints": "只使用text和file_path参数，其他参数内部固化"
}}
```

**关键提醒:**
- 测试用例的核心目标是格式验证，不是功能验证
- 确保生成的命令只使用text或file_path参数
- 重点关注输出的清晰度和格式规范性
- 为不同项目类型(有/无结构化输出)制定不同验证策略
"""

# 简化的测试用例生成提示
SIMPLE_TEST_CASE_PROMPT = """
为Python脚本生成2个简单的测试用例，使用真实项目文件。

**脚本信息：**
- 脚本名称: {function_name}
- 脚本路径: {script_path}
- 参数: {parameters}
- 运行环境: {runtime_environment}

**执行命令模板：**
{execution_command_template}

**可用的真实项目文件：**
{available_files}

**要求：**
1. 生成最多2个测试用例
2. 使用上面列出的真实文件（不要编造文件名）
3. 测试用例应该简单实用，验证脚本是否能正常工作
4. 使用标准化参数格式：位置参数（输入内容或文件路径）+ -o（输出路径）
5. 第一个测试用例测试基本功能，第二个测试用例可以测试帮助信息
6. 使用上面提供的执行命令模板，替换其中的参数部分

**输出JSON格式：**
```json
{{
  "test_cases": [
    {{
      "name": "basic_functionality_test",
      "description": "测试基本功能",
      "command": "基于执行命令模板，添加具体参数，如：'test input text' -o '/tmp/output_file'",
      "expected_behavior": "success",
      "timeout": 30
    }},
    {{
      "name": "help_test", 
      "description": "测试帮助信息",
      "command": "基于执行命令模板，添加 --help 参数",
      "expected_behavior": "success",
      "timeout": 10
    }}
  ]
}}
```

**重要：只使用available_files中列出的真实文件，不要编造不存在的文件名。**
"""
