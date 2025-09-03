import os
import sys
from datetime import datetime
from typing import Dict

from dotenv import load_dotenv
from loguru import logger

# Configure logger
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
)

# Load environment variables from .env file
load_dotenv()


def get_current_date() -> str:
    """获取当前日期字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_environment_info() -> Dict:
    """
    Get current environment information for method generation.

    Returns:
        Dictionary with environment details
    """
    import platform

    return {
        "operating_system": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.architecture()[0],
        "shell": os.getenv("SHELL", "unknown"),
    }
