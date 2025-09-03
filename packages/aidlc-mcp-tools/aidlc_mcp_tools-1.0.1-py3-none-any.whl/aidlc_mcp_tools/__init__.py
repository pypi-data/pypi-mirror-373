"""
AIDLC MCP Tools

Model Context Protocol (MCP) tools for AIDLC Dashboard integration.
Provides AI agents with tools to interact with project management workflows.
"""

from .tools import AIDLCDashboardMCPTools, MCPToolResult
from .server import AIDLCMCPServer
from .config import MCPConfig, load_config, save_config

__version__ = "1.0.0"
__author__ = "AIDLC Team"
__email__ = "team@aidlc.dev"

__all__ = [
    "AIDLCDashboardMCPTools",
    "MCPToolResult", 
    "AIDLCMCPServer",
    "MCPConfig",
    "load_config",
    "save_config"
]
