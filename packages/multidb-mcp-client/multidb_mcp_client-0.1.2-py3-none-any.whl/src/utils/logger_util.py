"""
Logging Utility Module

Unified logging configuration module. All other modules should import logger from here.
"""

import json
import os
import sys
from loguru import logger

project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
loglevel_array = ['TRACE', 'DEBUG', 'INFO', 'SUCCESS', 'WARNING', 'ERROR', 'CRITICAL']


def get_db_config_file() -> str:
    """
    Get database configuration file path
    Priority: Environment variable config_file > Default dbconfig.json

    Returns:
        str: Path to the database configuration file
    """
    config_file = os.getenv("config_file")
    if config_file and os.path.isfile(config_file):
        logger.info(f"Get database configuration path from environment variable config_file: {config_file}")
        return config_file
    else:
        default_config = os.path.join(project_path, "dbconfig.json")
        logger.warning(f"Using default database configuration path: {default_config}")
        return default_config


db_config_path = get_db_config_file()


def normalize_log_path(log_path: str) -> str:
    """
    Normalize log path to ensure it ends with appropriate log directory suffix

    Args:
        log_path (str): The base log path from configuration

    Returns:
        str: Normalized log path with appropriate log directory suffix
    """
    if not log_path:
        return log_path

    # Optimized one-liner: Check if path ends with log/logs (with or without trailing slash)
    return log_path if log_path.rstrip(os.sep).endswith(('logs', 'log')) else os.path.join(log_path, "logs")


def get_log_config() -> tuple[str, str]:
    """Get log path and log level from configuration file

    Returns:
        tuple[str, str]: A tuple containing (log_path, log_level)
            - log_path (str): Path to the log directory
            - log_level (str): Log level (TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL)
    """
    config_file = db_config_path
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Get log path
        log_path = config.get('logPath')
        if log_path is None or len(log_path.strip()) == 0:
            log_path = os.path.join(project_path, "logs")
        else:
            log_path = normalize_log_path(log_path)

        # Get log level
        log_level = config.get('logLevel')
        if log_level is None or len(log_level.strip()) == 0:
            log_level = "INFO"
        else:
            log_level = log_level.upper()
            if log_level not in loglevel_array:
                log_level = "INFO"

        return log_path, log_level
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        # If configuration file doesn't exist or parsing fails, use default values
        return os.path.join(project_path, "logs"), "INFO"


log_path, log_level = get_log_config()
log_file = os.path.join(log_path, "mcp_server.log")


def setup_logger(log_file: str, log_level: str):
    """Configure logging output"""
    # Remove default logger configuration
    logger.remove()

    # Output to stderr so MCP can see logs
    logger.add(
        sys.stderr,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    )

    # Also output to file
    if not os.path.exists(log_path):
        os.makedirs(log_path, exist_ok=True)

    logger.add(
        log_file,
        rotation="10 MB",
        retention="7 days",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    )

    logger.info(f"Logging configuration completed, log level: {log_level}, log file path: {log_file}")
    return logger


# Initialize logging configuration
setup_logger(log_file, log_level)

# Export logger for use by other modules
__all__ = ['logger']