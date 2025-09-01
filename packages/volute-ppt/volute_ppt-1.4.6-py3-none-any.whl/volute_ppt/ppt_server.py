#!/usr/bin/env python3
"""
Volute-PPT Server - Comprehensive PowerPoint MCP Server

This server provides advanced PowerPoint analysis, editing, and automation tools
for AI agents with multimodal capabilities and local COM access.

Run with: python -m volute_ppt.ppt_server [stdio|http]
"""

import os
import sys
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Server configuration
SERVER_NAME = os.getenv("SERVER_NAME", "Volute-PPT")
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8001"))

# Create FastMCP server instance
mcp = FastMCP(
    name=SERVER_NAME,
    instructions=f"""
        This is the Volute-PPT MCP server providing comprehensive PowerPoint automation tools.
        
        🚀 **PowerPoint Capabilities**:
        - Complete metadata extraction and analysis
        - Smart text editing with intelligent bullet conversion
        - Shape management and formatting operations
        - Slide management with DSL commands
        - Multimodal slide image capture for AI analysis
        - Template extraction and design system management
        - Version comparison and change tracking
        
        🖥️ **Local Features**:
        - COM integration with Microsoft PowerPoint
        - Local file system access
        - Windows-specific functionality
        - Real-time slide image capture
        
        ⚠️ **Requirements**:
        - Windows operating system
        - Microsoft PowerPoint installed
        - pywin32 package for COM automation
        - Local file access permissions
        
        📚 **Tool Categories**:
        - Core Analysis: extract_powerpoint_metadata, analyze_powerpoint_content, analyze_slide_text
        - Slide Management: manage_presentation_slides, bulk_slide_operations
        - Content Editing: edit_slide_text_content, apply_shape_formatting
        - Visual Tools: capture_slide_images, compare_presentation_versions
        - Advanced: extract_presentation_templates
    """,
    on_duplicate_tools="warn",
    on_duplicate_resources="warn", 
    on_duplicate_prompts="replace",
    include_fastmcp_meta=True,
)

# ============================================================================
# POWERPOINT TOOLS REGISTRATION
# ============================================================================

# Register core PowerPoint tools (analysis, validation, etc.)
try:
    from volute_ppt.powerpoint_tools import register_powerpoint_tools
    register_powerpoint_tools(mcp)
    logger.info("Core PowerPoint tools registered")
except ImportError as e:
    logger.warning(f"Core PowerPoint tools not available: {e}")
except Exception as e:
    logger.error(f"Error registering core PowerPoint tools: {e}")

# Register slide capture tools for multimodal analysis
try:
    from volute_ppt.slide_capture_tools import register_slide_capture_tools
    register_slide_capture_tools(mcp)
    logger.info("Slide image capture tools registered")
except ImportError as e:
    logger.warning(f"Slide capture tools not available: {e}")
except Exception as e:
    logger.error(f"Error registering slide capture tools: {e}")

# Register advanced PowerPoint tools (bulk operations, comparison, etc.)
try:
    from volute_ppt.advanced_powerpoint_tools import register_advanced_powerpoint_tools
    register_advanced_powerpoint_tools(mcp)
    logger.info("Advanced PowerPoint tools registered")
except ImportError as e:
    logger.warning(f"Advanced PowerPoint tools not available: {e}")
except Exception as e:
    logger.error(f"Error registering advanced PowerPoint tools: {e}")

# Register shape editing tools (content manipulation)
try:
    from volute_ppt.shape_editing_tools import register_shape_editing_tools
    register_shape_editing_tools(mcp)
    logger.info("Shape editing tools registered")
except ImportError as e:
    logger.warning(f"Shape editing tools not available: {e}")
except Exception as e:
    logger.error(f"Error registering shape editing tools: {e}")

# ============================================================================
# CORE UTILITY TOOLS
# ============================================================================

@mcp.tool(tags={"utility", "public"})
def echo(message: str) -> str:
    """Echo back a message. Useful for testing server connectivity."""
    return f"Echo: {message}"

@mcp.tool(tags={"math", "utility"})
def calculate(expression: str) -> float:
    """
    Safely evaluate a mathematical expression.
    
    Args:
        expression: A mathematical expression like "2 + 3 * 4"
        
    Returns:
        The result of the calculation
    """
    # Simple safe evaluation - only allow basic math operations
    allowed_chars = set("0123456789+-*/.() ")
    if not all(c in allowed_chars for c in expression):
        raise ValueError("Expression contains invalid characters")
    
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return float(result)
    except Exception as e:
        raise ValueError(f"Invalid mathematical expression: {e}")

@mcp.tool(tags={"system", "info"})
def get_server_info() -> dict:
    """Get information about the server environment and capabilities."""
    import platform
    
    info = {
        "server_name": SERVER_NAME,
        "python_version": sys.version,
        "platform": platform.platform(),
        "working_directory": os.getcwd(),
        "server_capabilities": {
            "powerpoint_tools": True,
            "com_automation": False,
            "multimodal_capture": False,
            "local_file_access": True
        },
        "environment": {
            "host": SERVER_HOST,
            "port": SERVER_PORT,
        }
    }
    
    # Check COM availability
    try:
        import win32com.client
        info["server_capabilities"]["com_automation"] = True
        info["server_capabilities"]["multimodal_capture"] = True
        
        # Test PowerPoint availability
        try:
            ppt = win32com.client.Dispatch("PowerPoint.Application")
            info["server_capabilities"]["powerpoint_installed"] = True
            info["powerpoint_version"] = ppt.Version
            ppt.Quit()
        except:
            info["server_capabilities"]["powerpoint_installed"] = False
    except ImportError:
        info["server_capabilities"]["com_automation"] = False
        info["server_capabilities"]["multimodal_capture"] = False
        info["server_capabilities"]["powerpoint_installed"] = False
    
    return info

# ============================================================================
# LOCAL FILE TOOLS
# ============================================================================

@mcp.tool(tags={"local", "files"})
def list_local_files(directory: str = ".", pattern: str = "*.pptx") -> list:
    """
    List PowerPoint files in a local directory.
    
    Args:
        directory: Local directory to search (default: current directory)
        pattern: File pattern to match (default: *.pptx)
    """
    import glob
    
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

# ============================================================================
# RESOURCES - Data sources that clients can read
# ============================================================================

@mcp.resource("config://server")
def get_server_config() -> dict:
    """Provides the current server configuration."""
    return {
        "name": SERVER_NAME,
        "host": SERVER_HOST,
        "port": SERVER_PORT,
        "type": "LOCAL_POWERPOINT",
        "features": {
            "powerpoint_tools": True,
            "slide_capture": True,
            "shape_editing": True,
            "bulk_operations": True,
            "template_extraction": True,
            "version_comparison": True
        }
    }

@mcp.resource("local://system")
def get_local_system_status() -> dict:
    """Provides local system status and PowerPoint capabilities."""
    return {
        "server_type": "LOCAL_POWERPOINT",
        "powerpoint_integration": True,
        "local_file_access": True,
        "com_automation": True,
        "multimodal_support": True
    }

@mcp.resource("local://files/{directory}")
def get_directory_listing(directory: str) -> dict:
    """Get listing of files in a local directory."""
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
# PROMPTS - Reusable message templates
# ============================================================================

@mcp.prompt(tags={"analysis", "data"})
def analyze_data(data_description: str, analysis_type: str = "general") -> str:
    """
    Create a prompt for data analysis.
    
    Args:
        data_description: Description of the data to analyze
        analysis_type: Type of analysis (general, statistical, trends)
    """
    prompt = f"""Please analyze the following data: {data_description}

Analysis type requested: {analysis_type}

Please provide:
1. Key insights and patterns
2. Notable trends or anomalies
3. Recommendations based on the findings
4. Confidence level in the analysis

Format your response clearly with headings and bullet points where appropriate."""
    
    return prompt

@mcp.prompt(tags={"coding", "help"})
def code_review_prompt(code_snippet: str, language: str = "python") -> str:
    """
    Create a prompt for code review.
    
    Args:
        code_snippet: The code to review
        language: Programming language of the code
    """
    return f"""Please review this {language} code:

```{language}
{code_snippet}
```

Please provide feedback on:
1. Code quality and best practices
2. Potential bugs or issues
3. Performance considerations
4. Readability and maintainability
5. Suggested improvements

Be constructive and specific in your feedback."""

# ============================================================================
# CUSTOM ROUTES - Additional HTTP endpoints
# ============================================================================

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """Health check endpoint for monitoring."""
    return PlainTextResponse("VOLUTE-PPT-OK")

@mcp.custom_route("/info", methods=["GET"])
async def server_info_endpoint(request: Request) -> PlainTextResponse:
    """Server information endpoint."""
    info = f"Server: {SERVER_NAME}\nType: PowerPoint MCP Server\nStatus: Running\nTransport: HTTP"
    return PlainTextResponse(info)

# ============================================================================
# SERVER STARTUP
# ============================================================================

def main():
    """Main entry point for the server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Volute-PPT Server - PowerPoint MCP Server")
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
    
    # Support legacy stdio argument for backward compatibility
    if len(sys.argv) > 1 and sys.argv[1] == "stdio":
        args = argparse.Namespace(transport="stdio", port=SERVER_PORT, host=SERVER_HOST)
    else:
        args = parser.parse_args()
    
    if args.transport == "stdio":
        # STDIO transport for MCP clients (Claude Desktop, etc.)
        logger.info(f"Starting {SERVER_NAME} with STDIO transport")
        logger.info("PowerPoint tools: Available")
        logger.info("Multimodal support: Available")
        mcp.run(transport="stdio")
    else:
        # HTTP transport for web access and testing
        logger.info(f"Starting {SERVER_NAME} server")
        logger.info(f"Server: http://{args.host}:{args.port}")
        logger.info(f"Health check: http://{args.host}:{args.port}/health")
        logger.info("PowerPoint tools: Available")
        logger.info("Multimodal support: Available")
        mcp.run(
            transport="http",
            host=args.host,
            port=args.port,
        )

if __name__ == "__main__":
    main()
