"""
MySQL MCP Server

A Model Context Protocol (MCP) server for MySQL/MariaDB/TiDB/OceanBase databases.
"""

from typing import TYPE_CHECKING
# Package metadata
__version__ = "0.1.2"
__author__ = "Frank Jin"
__email__ = "j00131120@163.com"
__description__ = "A Model Context Protocol (MCP) server that enables secure interaction with MySQL/MariaDB/TiDB/AWS OceanBase/RDS/Aurora MySQL DataBases."
__license__ = "MIT"
__url__ = "https://github.com/j00131120/mcp_database_server/tree/main/multidb_mcp_client"

# Conditional imports for type checking
if TYPE_CHECKING:
    from .server import mcp
    from .utils import (
        DatabaseInstance,
        DatabaseInstanceConfig,
        DatabaseInstanceConfigLoader,
        load_activate_db_config,
        execute_sql,
        logger
    )

# Public API
__all__ = [
    # Package metadata
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "__license__",
    "__url__",

    # Core modules (available via explicit import)
    "server",
    "utils",
    "resources",
    "tools",
]


def get_version() -> str:
    """Get the current version of the MySQL MCP Server."""
    return __version__


def get_package_info() -> dict[str, str]:
    """Get comprehensive package information."""
    return {
        "name": "mysql-mcp-server3",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "description": __description__,
        "license": __license__,
        "url": __url__,
    }