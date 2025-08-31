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

__version__ = "1.4.2"
__author__ = "Coritan"
__email__ = "your-email@example.com"
__description__ = "MCP server for PowerPoint integration in AI applications"

from .server import main as server_main
from .sdk import VoluteMCPCloudClient, VoluteMCPClient, VoluteMCPError, create_client
from .toolkit import (
    # Core Analysis Tools
    extract_powerpoint_metadata,
    analyze_powerpoint_content,
    validate_powerpoint_file,
    
    # Slide Management Tools
    manage_presentation_slides,
    bulk_slide_operations,
    
    # Visual & Multimodal Tools
    capture_slide_images,
    compare_presentation_versions,
    
    # Content Editing Tools
    edit_slide_text_content,
    apply_shape_formatting,
    manage_slide_shapes,
    
    # Utility Functions
    get_system_capabilities
)

__all__ = [
    # Server & SDK
    "server_main",
    "VoluteMCPCloudClient",
    "VoluteMCPClient",
    "VoluteMCPError",
    "create_client",
    
    # Core Analysis Tools
    "extract_powerpoint_metadata",
    "analyze_powerpoint_content",
    "validate_powerpoint_file",
    
    # Slide Management Tools
    "manage_presentation_slides",
    "bulk_slide_operations",
    
    # Visual & Multimodal Tools
    "capture_slide_images",
    "compare_presentation_versions",
    
    # Content Editing Tools
    "edit_slide_text_content",
    "apply_shape_formatting",
    "manage_slide_shapes",
    
    # Utility Functions
    "get_system_capabilities"
]
