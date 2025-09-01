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

__version__ = "1.4.4"
__author__ = "Coritan"
__email__ = "your-email@example.com"
__description__ = "MCP server for PowerPoint integration in AI applications"

# SDK
from .sdk import VoluteMCPCloudClient, VoluteMCPClient, VoluteMCPError, create_client

# Direct toolkit functions
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

# LangChain tools (optional)
try:
    from .langchain_tools import (
        # Core Analysis
        get_powerpoint_metadata,
        get_slide_content,
        validate_powerpoint,
        
        # Slide Management
        manage_slides,
        execute_bulk_operations,
        
        # Visual & Multimodal
        capture_powerpoint_images,
        compare_presentations,
        
        # Content Editing
        edit_slide_text,
        format_shapes,
        manage_shapes,
        
        # Utilities
        get_capabilities
    )
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# CLI entrypoints
from .cli import run_ppt_server, run_local_server, run_cloud_server

__all__ = [
    # Server & SDK
    "run_ppt_server",
    "run_local_server",
    "run_cloud_server",
    "VoluteMCPCloudClient",
    "VoluteMCPClient",
    "VoluteMCPError",
    "create_client",
    
    # Direct Toolkit Functions
    "extract_powerpoint_metadata",
    "analyze_powerpoint_content",
    "validate_powerpoint_file",
    "manage_presentation_slides",
    "bulk_slide_operations",
    "capture_slide_images",
    "compare_presentation_versions",
    "edit_slide_text_content",
    "apply_shape_formatting",
    "manage_slide_shapes",
    "get_system_capabilities",
    
    # LangChain Tools
    "get_powerpoint_metadata",
    "get_slide_content",
    "validate_powerpoint",
    "manage_slides",
    "execute_bulk_operations",
    "capture_powerpoint_images",
    "compare_presentations",
    "edit_slide_text",
    "format_shapes",
    "manage_shapes",
    "get_capabilities"
]
