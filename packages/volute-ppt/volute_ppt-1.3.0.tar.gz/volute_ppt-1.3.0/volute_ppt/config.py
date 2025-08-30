"""
Configuration settings for the VoluteMCP server.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class ServerConfig(BaseSettings):
    """Server configuration using Pydantic settings."""
    
    # Server basic settings
    name: str = Field(default="VoluteMCP", description="Server name")
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # FastMCP settings
    log_level: str = Field(default="INFO", description="Logging level")
    mask_error_details: bool = Field(default=False, description="Mask error details from clients")
    resource_prefix_format: str = Field(default="path", description="Resource prefix format")
    include_fastmcp_meta: bool = Field(default=True, description="Include FastMCP metadata")
    
    # Component handling
    on_duplicate_tools: str = Field(default="warn", description="Handle duplicate tool registrations")
    on_duplicate_resources: str = Field(default="warn", description="Handle duplicate resource registrations") 
    on_duplicate_prompts: str = Field(default="replace", description="Handle duplicate prompt registrations")
    
    # Optional authentication settings
    api_key: Optional[str] = Field(default=None, description="API key for authentication")
    
    model_config = {
        "env_prefix": "VOLUTE_",
        "env_file": ".env",
        "case_sensitive": False
    }


# Global configuration instance
config = ServerConfig()


def get_config() -> ServerConfig:
    """Get the global configuration instance."""
    return config


def get_server_instructions() -> str:
    """Get the server instructions text."""
    return f"""
    Welcome to {config.name}!
    
    This MCP server provides various tools and resources for AI model interaction:
    
    🔧 TOOLS:
    - echo: Test server connectivity
    - calculate: Perform mathematical calculations
    - get_server_info: Get server environment information
    
    📁 RESOURCES:
    - config://server: Server configuration details
    - data://environment: Environment information
    - file://{{file_path}}: Read file contents (with safety checks)
    
    📝 PROMPTS:
    - analyze_data: Generate data analysis prompts
    - code_review_prompt: Generate code review prompts
    
    🌐 CUSTOM ROUTES:
    - GET /health: Health check endpoint
    - GET /info: Server information endpoint
    
    Use the available components to interact with the server effectively!
    """


def get_environment_info() -> dict:
    """Get current environment information."""
    return {
        "server_config": {
            "name": config.name,
            "host": config.host,
            "port": config.port,
        },
        "fastmcp_settings": {
            "log_level": config.log_level,
            "mask_error_details": config.mask_error_details,
            "resource_prefix_format": config.resource_prefix_format,
            "include_fastmcp_meta": config.include_fastmcp_meta,
        },
        "runtime_info": {
            "platform": os.name,
            "cwd": os.getcwd(),
            "python_version": os.sys.version.split()[0],
        }
    }
