#!/usr/bin/env python3
"""
Volute-PPT Local Server - PowerPoint-focused MCP server for local COM access.

This server runs locally on Windows machines with PowerPoint installed,
providing COM-based PowerPoint manipulation tools and multimodal slide capture.

Run with: python server_local.py
"""

import os
import sys
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Server configuration
SERVER_NAME = os.getenv("LOCAL_SERVER_NAME", "Volute-PPT-Local")
SERVER_HOST = os.getenv("LOCAL_SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("LOCAL_SERVER_PORT", "8001"))

# Create FastMCP server instance
mcp = FastMCP(
    name=SERVER_NAME,
    instructions=f"""
        This is a LOCAL Volute-PPT server providing PowerPoint and local file tools.
        
        🖥️ **Local Access Features**:
        - PowerPoint COM integration (requires PowerPoint installed)
        - Local file system access
        - Windows-specific functionality
        
        🌐 **Companion Cloud Server**: https://volutemcp-server.onrender.com
        - Use cloud server for general tools (calculate, echo, etc.)
        - Use this local server for PowerPoint and local file operations
        
        ⚠️ **Requirements**:
        - Windows operating system
        - Microsoft PowerPoint installed
        - Local file access permissions
    """,
    on_duplicate_tools="warn",
    on_duplicate_resources="warn", 
    on_duplicate_prompts="replace",
    include_fastmcp_meta=True,
)

# ============================================================================
# POWERPOINT TOOLS REGISTRATION (LOCAL COM ACCESS)
# ============================================================================

try:
    # Import from the relative package module
    from .powerpoint_tools import register_powerpoint_tools
    register_powerpoint_tools(mcp)
    print("✅ PowerPoint COM tools registered (local access)", file=sys.stderr)
except ImportError as e:
    print(f"⚠️ PowerPoint tools not available: {e}", file=sys.stderr)
except Exception as e:
    print(f"❌ Error registering PowerPoint tools: {e}", file=sys.stderr)

# Register slide capture tools for multimodal analysis
try:
    from .slide_capture_tools import register_slide_capture_tools
    register_slide_capture_tools(mcp)
    print("✅ Slide image capture tools registered (multimodal support)", file=sys.stderr)
except ImportError as e:
    print(f"⚠️ Slide capture tools not available: {e}", file=sys.stderr)
except Exception as e:
    print(f"❌ Error registering slide capture tools: {e}", file=sys.stderr)

# Register advanced PowerPoint tools
try:
    from .advanced_powerpoint_tools import register_advanced_powerpoint_tools
    register_advanced_powerpoint_tools(mcp)
    print("✅ Advanced PowerPoint tools registered (bulk operations & analysis)", file=sys.stderr)
except ImportError as e:
    print(f"⚠️ Advanced PowerPoint tools not available: {e}", file=sys.stderr)
except Exception as e:
    print(f"❌ Error registering advanced PowerPoint tools: {e}", file=sys.stderr)

# Register shape editing tools
try:
    from .shape_editing_tools import register_shape_editing_tools
    register_shape_editing_tools(mcp)
    print("✅ Shape editing tools registered (content manipulation)", file=sys.stderr)
except ImportError as e:
    print(f"⚠️ Shape editing tools not available: {e}", file=sys.stderr)
except Exception as e:
    print(f"❌ Error registering shape editing tools: {e}", file=sys.stderr)

# ============================================================================
# LOCAL TOOLS - Functions that require local access
# ============================================================================

# @mcp.tool(tags={"local", "files"})
def list_local_files(directory: str = ".", pattern: str = "*.pptx") -> list:
    """
    List PowerPoint files in a local directory.
    
    Args:
        directory: Local directory to search (default: current directory)
        pattern: File pattern to match (default: *.pptx)
    
    Note: This function is available internally but not exposed as an MCP tool.
    """
    import glob
    import os
    
    if not os.path.exists(directory):
        raise ValueError(f"Directory not found: {directory}")
    
    search_path = os.path.join(directory, pattern)
    files = glob.glob(search_path)
    
    return [
        {
            "path": file,
            "name": os.path.basename(file),
            "size": os.path.getsize(file),
            "modified": os.path.getmtime(file)
        }
        for file in files
    ]

@mcp.tool(tags={"local", "system"})
def get_local_system_info() -> dict:
    """Get information about the local system and PowerPoint availability."""
    import platform
    import subprocess
    
    info = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "server_type": "LOCAL",
        "powerpoint_available": False,
        "com_available": False
    }
    
    # Check if PowerPoint is installed
    try:
        import win32com.client
        info["com_available"] = True
        
        # Try to connect to PowerPoint
        try:
            ppt = win32com.client.Dispatch("PowerPoint.Application")
            info["powerpoint_available"] = True
            info["powerpoint_version"] = ppt.Version
            ppt.Quit()
        except:
            pass
    except ImportError:
        pass
    
    return info

# @mcp.tool(tags={"local", "files"})  
def read_local_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    Read content from a local file.
    
    Args:
        file_path: Path to local file
        encoding: File encoding (default: utf-8)
    
    Note: This function is available internally but not exposed as an MCP tool.
    """
    import os
    
    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()

# ============================================================================
# LOCAL RESOURCES - Local data sources
# ============================================================================

@mcp.resource("local://system")
def get_local_system_status() -> dict:
    """Provides local system status and capabilities."""
    return {
        "server_type": "LOCAL",
        "powerpoint_integration": True,
        "local_file_access": True,
        "com_objects": True,
        "companion_cloud_server": "https://volutemcp-server.onrender.com"
    }

@mcp.resource("local://files/{directory}")
def get_directory_listing(directory: str) -> dict:
    """Get listing of files in a local directory."""
    import os
    import glob
    
    if not os.path.exists(directory):
        return {"error": f"Directory not found: {directory}"}
    
    files = []
    for file_path in glob.glob(os.path.join(directory, "*")):
        if os.path.isfile(file_path):
            files.append({
                "name": os.path.basename(file_path),
                "path": file_path,
                "size": os.path.getsize(file_path),
                "extension": os.path.splitext(file_path)[1]
            })
    
    return {
        "directory": directory,
        "files": files,
        "count": len(files)
    }

# ============================================================================
# CUSTOM ROUTES
# ============================================================================

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """Health check endpoint."""
    return PlainTextResponse("LOCAL-OK")

@mcp.custom_route("/info", methods=["GET"])
async def server_info_endpoint(request: Request) -> PlainTextResponse:
    """Local server information endpoint."""
    info = f"Server: {SERVER_NAME}\\nType: LOCAL\\nPowerPoint: Available\\nStatus: Running"
    return PlainTextResponse(info)

# ============================================================================
# SERVER STARTUP
# ============================================================================

def main():
    """Main entry point for the local server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Volute-PPT Local Server")
    parser.add_argument(
        "--transport", 
        choices=["stdio", "http"], 
        default="http",
        help="Transport protocol (default: http)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=SERVER_PORT,
        help=f"Port number for HTTP transport (default: {SERVER_PORT})"
    )
    parser.add_argument(
        "--host", 
        default=SERVER_HOST,
        help=f"Host address for HTTP transport (default: {SERVER_HOST})"
    )
    
    # Support legacy stdio argument
    if len(sys.argv) > 1 and sys.argv[1] == "stdio":
        args = argparse.Namespace(transport="stdio", port=SERVER_PORT, host=SERVER_HOST)
    else:
        args = parser.parse_args()
    
    if args.transport == "stdio":
        # STDIO transport for local MCP clients
        print(f"Starting {SERVER_NAME} with STDIO transport...", file=sys.stderr)
        mcp.run(transport="stdio")
    else:
        # HTTP transport
        print(f"Starting {SERVER_NAME} LOCAL server...", file=sys.stderr)
        print(f"Local server: http://{args.host}:{args.port}", file=sys.stderr)
        print(f"Cloud companion: https://volutemcp-server.onrender.com", file=sys.stderr)
        print(f"Health check: http://{args.host}:{args.port}/health", file=sys.stderr)
        mcp.run(
            transport="http",
            host=args.host,
            port=args.port,
        )

if __name__ == "__main__":
    main()
