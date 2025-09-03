"""
Centralized logging configuration for autodeploy module.

This module configures loguru for hierarchical logging that reflects
the graph structure of the deployment process.
"""

import sys
from typing import Optional
from pathlib import Path

from loguru import logger

# Remove default handler
logger.remove()


def format_record(record):
    """Format log records without hierarchy indentation."""
    # Extract node context from extra data
    node_type = record["extra"].get("node_type", "")
    node_name = record["extra"].get("node_name", "")

    # Add node type prefix with colors
    prefix = ""
    if node_type:
        prefixes = {
            "root": "<magenta>[ROOT]</magenta>",
            "core_step": "<cyan>[CORE]</cyan>",
            "method": "<blue>[METHOD]</blue>",
            "verify": "<yellow>[VERIFY]</yellow>",
            "forward": "<green>[FORWARD]</green>",
            "command": "<white>[CMD]</white>",
            "logic_command": "<light-blue>[LOGIC]</light-blue>",
            "fix": "<red>[FIX]</red>",
        }
        prefix = prefixes.get(node_type, f"<white>[{node_type.upper()}]</white>")

    # Format the message without indentation
    if node_name:
        message = f"{prefix} <bold>{node_name}</bold>: {record['message']}"
    else:
        message = record['message']

    # Return format string with color tags and proper message placeholder
    return "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> |" + message + "\n"


# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Add console handler with custom formatter
logger.add(
    sys.stderr,
    format=format_record,
    level="INFO",
    colorize=True,
    backtrace=True,
    diagnose=True
)

# Add file handler for complete logs
logger.add(
    logs_dir / "complete.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    level="DEBUG",
    rotation="10 MB",
    retention="7 days",
    colorize=False
)

# Add file handler for deployment node status logs only
deployment_logger = logger.bind(is_deployment=True)
logger.add(
    logs_dir / "deployment_nodes.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    level="DEBUG",
    rotation="10 MB",
    retention="7 days",
    colorize=False,
    filter=lambda record: record["extra"].get("is_deployment", False)
)


def log_node(node, message: str, level: str = "info", is_deployment: bool = True):
    """
    Log a simplified message with node context for user-facing deployment progress.
    
    Args:
        node: The node being executed
        message: The log message
        level: Log level (info, warning, error, debug, success)
        is_deployment: Whether this is a deployment node status log
    """
    # Get node type name
    node_type = getattr(node, 'node_type_name', 'unknown')
    
    # Skip overly verbose messages for user display
    if is_deployment and any(skip_phrase in message.lower() for skip_phrase in [
        "created", "node_details", "executing core step", "executing method",
        "executing verification", "executing forward", "executing logic"
    ]):
        return
    
    # Determine appropriate log level based on node type and status
    if node_type == "fix" and level == "info":
        level = "warning"  # Fix nodes should use warning level
    
    # Create bound logger for deployment nodes
    if is_deployment:
        bound_logger = logger.bind(
            node_type=node_type,
            node_name=node.name,
            is_deployment=True
        )
    else:
        bound_logger = logger.bind(
            node_type=node_type,
            node_name=node.name
        )
    
    # Get the appropriate log function
    log_func = getattr(bound_logger, level)
    log_func(message)


def log_node_details(node, status: str, message: str = None):
    """
    Log simplified node information for user-facing deployment progress.
    
    Args:
        node: The node to log details for
        status: Node status (created, executing, completed, failed)
        message: Optional additional message
    """
    node_name = getattr(node, 'name', 'unknown')
    node_type = getattr(node, 'node_type_name', 'unknown')
    
    # Only log important status changes for user visibility
    if status in ["executing", "completed", "failed"]:
        # Create user-friendly status messages
        status_icons = {
            "executing": "⚡",
            "completed": "✅",
            "failed": "❌"
        }
        
        status_messages = {
            "executing": "Running",
            "completed": "Completed",
            "failed": "Failed"
        }
        
        # Simplify node type names for user display
        type_names = {
            "core_step": "Step",
            "method": "Action",
            "command": "Command",
            "verify": "Verification",
            "fix": "Fix"
        }
        
        display_type = type_names.get(node_type, node_type.title())
        status_icon = status_icons.get(status, "")
        status_text = status_messages.get(status, status.title())
        
        # Create concise log message
        log_message = f"{status_icon} {display_type}: {node_name} - {status_text}"
        
        if message:
            log_message += f" | {message}"
        
        # Determine log level
        level_map = {
            "executing": "info",
            "completed": "success",
            "failed": "error"
        }
        level = level_map.get(status, "info")
        
        # Log with deployment context
        bound_logger = logger.bind(
            node_type=node_type,
            node_name=node_name,
            is_deployment=True
        )
        
        log_func = getattr(bound_logger, level)
        log_func(log_message)


def log_deployment_status(node, status: str, message: str):
    """
    Log deployment node status changes.
    
    Args:
        node: The deployment node
        status: Status type (created, executing, completed, failed)
        message: Status message
    """
    level_map = {
        "created": "info",
        "executing": "info", 
        "completed": "success",
        "failed": "error"
    }
    
    level = level_map.get(status, "info")
    log_node(node, f"{status.capitalize()}: {message}", level=level, is_deployment=True)


def calculate_node_depth(node) -> int:
    """
    Calculate the depth of a node in the hierarchy.
    
    Args:
        node: The node to calculate depth for
        
    Returns:
        Depth level (0 for root, increasing for children)
    """
    depth = 0
    current = node

    # Need access to graph to traverse up to root
    # This will be called with graph context
    while hasattr(current, 'parent_id') and current.parent_id:
        depth += 1
        # The actual parent lookup will be done by the caller
        # who has access to the graph
        break

    return depth


def log_llm_evaluation(node_name: str, output: str, condition_met: bool, reasoning: Optional[str] = None):
    """
    Log LLM condition evaluation results.
    
    Args:
        node_name: Name of the node being evaluated
        output: The command output being evaluated
        condition_met: The evaluation result
        reasoning: Optional reasoning from LLM
    """
    # Truncate long outputs for logging
    output_preview = output[:200] + "..." if len(output) > 200 else output
    output_preview = output_preview.replace('\n', ' ')

    logger.info(f"LLM evaluated condition as {'TRUE' if condition_met else 'FALSE'} for '{node_name}'")
    logger.debug(f"Command output preview for '{node_name}': {output_preview}")

    if reasoning:
        logger.debug(f"LLM reasoning: {reasoning}")


def log_heuristic_evaluation(node_name: str, success_count: int, failure_count: int,
                             has_output: bool, result: bool):
    """
    Log heuristic evaluation details.
    
    Args:
        node_name: Name of the node being evaluated
        success_count: Number of success indicators found
        failure_count: Number of failure indicators found
        has_output: Whether output is non-empty
        result: The evaluation result
    """
    logger.info(f"Using heuristic evaluation for node '{node_name}'")

    if failure_count > success_count:
        logger.debug(f"Heuristic: More failure indicators ({failure_count}) than success ({success_count})")
    elif success_count > 0:
        logger.debug(f"Heuristic: Found {success_count} success indicators")
    elif failure_count > 0:
        logger.debug(f"Heuristic: Found {failure_count} failure indicators")
    else:
        logger.debug(f"Heuristic: No clear indicators, defaulting to {has_output} based on output presence")


def log_command_execution(command: str, missing_info: bool, interactive: bool):
    """
    Log command execution details.
    
    Args:
        command: The command being executed
        missing_info: Whether command needs user-provided information
        interactive: Whether command requires terminal interaction
    """
    execution_type = []
    if missing_info:
        execution_type.append("missing_info")
    if interactive:
        execution_type.append("interactive")

    if execution_type:
        logger.debug(f"Executing command with flags: {', '.join(execution_type)}")

    logger.debug(f"Command: {command}")


def log_fix_generation(failed_command_name: str, fix_count: int, confidence: str, analysis: str):
    """
    Log fix generation details.
    
    Args:
        failed_command_name: Name of the failed command
        fix_count: Number of fix commands generated
        confidence: Fix confidence level
        analysis: Failure analysis from LLM
    """
    logger.warning(f"Generated {fix_count} fix commands for '{failed_command_name}'")
    logger.warning(f"Fix confidence: {confidence}")
    logger.warning(f"Failure analysis: {analysis}")


def log_verification_skip(software_name: str):
    """
    Log when a software verification is skipped.
    
    Args:
        software_name: Name of the software already verified
    """
    logger.info(f"Software '{software_name}' already verified, skipping verification")


def log_graph_visualization_status(neo4j_enabled: bool, uri: Optional[str] = None):
    """
    Log Neo4j visualization status.
    
    Args:
        neo4j_enabled: Whether Neo4j is enabled
        uri: Neo4j connection URI
    """
    if neo4j_enabled and uri:
        logger.info(f"Connected to Neo4j at {uri}")
    elif not neo4j_enabled:
        logger.info("Neo4j visualization disabled")
    else:
        logger.warning("Neo4j visualization requested but connection failed")


# Export configured logger and utilities
__all__ = [
    "logger",
    "log_node",
    "log_node_details",
    "log_deployment_status",
    "calculate_node_depth",
    "log_llm_evaluation",
    "log_heuristic_evaluation",
    "log_command_execution",
    "log_fix_generation",
    "log_verification_skip",
    "log_graph_visualization_status"
]
