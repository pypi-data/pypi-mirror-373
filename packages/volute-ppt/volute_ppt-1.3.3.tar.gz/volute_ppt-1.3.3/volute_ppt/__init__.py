"""
Volute-PPT - PowerPoint Integration for AI Applications

A Model Context Protocol (MCP) server that enables AI agents to interact with
Microsoft PowerPoint presentations and local files on Windows machines.

Features:
- PowerPoint COM automation
- Comprehensive metadata extraction
- Local file system access
- Hybrid cloud/local architecture
- FastMCP-based implementation

Example Usage:
    # Install via pip
    pip install volute-ppt
    
    # Run local server for PowerPoint integration
    volute-ppt-local
    
    # Use in MCP configuration
    {
        "volute-ppt-local": {
            "command": "volute-ppt-local",
            "args": ["--transport", "stdio"],
            "env": {}
        }
    }
"""

__version__ = "1.3.0"
__author__ = "Coritan"
__email__ = "your-email@example.com"
__description__ = "MCP server for PowerPoint integration in AI applications"

from .server import main as server_main
from .server_local import main as local_main
from .sdk import VoluteMCPCloudClient, VoluteMCPClient, VoluteMCPError, create_client

__all__ = [
    "server_main", 
    "local_main", 
    "VoluteMCPCloudClient", 
    "VoluteMCPClient", 
    "VoluteMCPError", 
    "create_client"
]
