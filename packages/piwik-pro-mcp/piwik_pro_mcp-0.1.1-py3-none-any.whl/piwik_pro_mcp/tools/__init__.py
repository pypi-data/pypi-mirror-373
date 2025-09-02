"""
MCP Tools Registration and Exports

This module provides a clean interface for registering all MCP tools
with the FastMCP server, organized by functional area.
"""

from mcp.server.fastmcp import FastMCP

from .apps import register_app_tools
from .cdp import register_cdp_tools
from .container_settings import register_container_settings_tools
from .parameters import register_parameter_discovery_tool
from .tag_manager import (
    register_tag_tools,
    register_template_tools,
    register_trigger_tools,
    register_variable_tools,
    register_version_tools,
)
from .tracker_settings import register_tracker_settings_tools


def register_all_tools(mcp: FastMCP) -> None:
    """Register all MCP tools with the server."""
    register_parameter_discovery_tool(mcp)
    # Register app management tools
    register_app_tools(mcp)

    # Register CDP tools
    register_cdp_tools(mcp)

    # Register Tag Manager tools
    register_tag_tools(mcp)
    register_trigger_tools(mcp)
    register_variable_tools(mcp)
    register_version_tools(mcp)
    register_template_tools(mcp)

    # Register tracker settings tools
    register_tracker_settings_tools(mcp)

    # Register container settings tools
    register_container_settings_tools(mcp)


__all__ = [
    "register_all_tools",
    # Individual registration functions (for selective registration if needed)
    "register_app_tools",
    "register_cdp_tools",
    "register_tag_tools",
    "register_trigger_tools",
    "register_variable_tools",
    "register_version_tools",
    "register_template_tools",
    "register_tracker_settings_tools",
    "register_container_settings_tools",
    "register_parameter_discovery_tool",
]
