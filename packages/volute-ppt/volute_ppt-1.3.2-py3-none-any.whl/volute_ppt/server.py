#!/usr/bin/env python3
"""
VoluteMCP Server - A FastMCP-based Model Context Protocol server.

This server provides tools, resources, and prompts for AI model interaction.
Run with: python server.py
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
SERVER_NAME = os.getenv("SERVER_NAME", "VoluteMCP")
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
# Render uses PORT environment variable, fallback to SERVER_PORT or default 8000
SERVER_PORT = int(os.getenv("PORT", os.getenv("SERVER_PORT", "8000")))

# Create FastMCP server instance
mcp = FastMCP(
    name=SERVER_NAME,
    instructions="""
        This is a VoluteMCP server providing various tools and resources.
        
        Available functionality:
        - Data processing and analysis tools
        - System information resources
        - Interactive prompts for common tasks
        
        Use the available tools to perform operations and access resources for information.
    """,
    # Configure component handling
    on_duplicate_tools="warn",
    on_duplicate_resources="warn", 
    on_duplicate_prompts="replace",
    # Enable FastMCP metadata
    include_fastmcp_meta=True,
)

# ============================================================================
# CLOUD SERVER NOTE
# ============================================================================
# PowerPoint/COM tools are NOT registered on cloud server due to:
# - No PowerPoint installation in cloud environment
# - No access to user's local files
# - Linux environment (no Windows COM)
# 
# For PowerPoint functionality, use the companion LOCAL server:
# python server_local.py (runs on user's Windows machine)
# ============================================================================

# ============================================================================
# TOOLS - Functions that clients can call
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
    """Get information about the server environment."""
    return {
        "server_name": SERVER_NAME,
        "python_version": os.sys.version,
        "working_directory": os.getcwd(),
        "environment": {
            "host": SERVER_HOST,
            "port": SERVER_PORT,
        }
    }

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
        "features": {
            "tools": True,
            "resources": True,
            "prompts": True,
            "custom_routes": True
        }
    }

@mcp.resource("data://environment")
def get_environment_info() -> dict:
    """Provides information about the server environment."""
    return {
        "platform": os.name,
        "cwd": os.getcwd(),
        "env_vars": {k: v for k, v in os.environ.items() if k.startswith('FASTMCP_')},
    }

# ============================================================================
# RESOURCE TEMPLATES - Parameterized resources
# ============================================================================

@mcp.resource("file://{file_path}")
def read_file_content(file_path: str) -> str:
    """
    Read the content of a file (with basic safety checks).
    
    Args:
        file_path: Path to the file to read
    """
    # Basic security check - prevent directory traversal
    if ".." in file_path or file_path.startswith("/"):
        raise ValueError("Invalid file path")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Error reading file: {e}")

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
    return PlainTextResponse("OK")

@mcp.custom_route("/info", methods=["GET"])
async def server_info_endpoint(request: Request) -> PlainTextResponse:
    """Server information endpoint."""
    info = f"Server: {SERVER_NAME}\nStatus: Running\nTransport: HTTP"
    return PlainTextResponse(info)

# ============================================================================
# SERVER STARTUP
# ============================================================================

def main():
    """Main entry point for the cloud server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="VoluteMCP Cloud Server")
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
        # STDIO transport for local tools/clients
        print(f"Starting {SERVER_NAME} with STDIO transport...", file=sys.stderr)
        mcp.run(transport="stdio")
    else:
        # HTTP transport (default)
        print(f"Starting {SERVER_NAME} server...", file=sys.stderr)
        print(f"Server will be available at: http://{args.host}:{args.port}", file=sys.stderr)
        print(f"Health check: http://{args.host}:{args.port}/health", file=sys.stderr)
        mcp.run(
            transport="http",
            host=args.host,
            port=args.port,
        )

if __name__ == "__main__":
    main()
