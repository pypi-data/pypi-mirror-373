"""
XeSQL MCP Server

A Model Context Protocol (MCP) server for XeSQL/UbiSQL/MySQL databases.
"""

from typing import TYPE_CHECKING
# Package metadata
__projectname__ = "xesql-mcp-server"
__version__ = "1.0.1"
__author__ = "Frank Jin"
__email__ = "jinzhuqing905@pingan.com"
__description__ = "A Model Context Protocol (MCP) server that enables secure interaction with XeSQL/UbiSQL/MySQL DataBases."
__license__ = "MIT"
__url__ = "https://gitee.com/frankjin/mcp-server/tree/master/xesql_mcp_server"

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
    "__projectname__",
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
        "projectname": __projectname__,
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "description": __description__,
        "license": __license__,
        "url": __url__,
    }
def get_base_package_info() -> dict[str, str]:
    """Get comprehensive package information."""
    return {
        "projectname": __projectname__,
        "version": __version__,
        "description": __description__,
        "license": __license__,
    }