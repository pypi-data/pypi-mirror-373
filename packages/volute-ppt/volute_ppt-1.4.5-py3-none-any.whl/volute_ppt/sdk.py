#!/usr/bin/env python3
"""
VoluteMCP SDK - Simple client library for cloud-to-cloud integration.

This SDK makes it easy for cloud-deployed AI agents to integrate with
VoluteMCP cloud services without dealing with MCP protocol details.
"""

import httpx
import asyncio
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import json


class VoluteMCPError(Exception):
    """VoluteMCP API error."""
    pass


class ToolResult(BaseModel):
    """Result from a tool call."""
    success: bool
    result: Any
    error: Optional[str] = None


class VoluteMCPCloudClient:
    """
    Simple client for VoluteMCP cloud services.
    
    Perfect for cloud-deployed AI agents that need PowerPoint processing
    and other VoluteMCP tools without MCP protocol complexity.
    """
    
    def __init__(self, base_url: str = "https://volutemcp-server.onrender.com"):
        """
        Initialize the VoluteMCP client.
        
        Args:
            base_url: VoluteMCP server URL (default: official cloud server)
        """
        self.base_url = base_url.rstrip('/')
        self.session = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close the HTTP session."""
        await self.session.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def health_check(self) -> bool:
        """
        Check if the VoluteMCP server is healthy.
        
        Returns:
            True if server is healthy, False otherwise
        """
        try:
            response = await self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
    
    async def list_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of available tools from the server.
        
        Returns:
            List of tool definitions with names, descriptions, and parameters
        """
        try:
            response = await self.session.post(
                f"{self.base_url}/mcp/tools/list",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if "result" in data and "tools" in data["result"]:
                return data["result"]["tools"]
            return []
        
        except Exception as e:
            raise VoluteMCPError(f"Failed to list tools: {e}")
    
    async def call_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """
        Call a VoluteMCP tool with the given arguments.
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Tool arguments
            
        Returns:
            ToolResult with success status and result data
        """
        try:
            response = await self.session.post(
                f"{self.base_url}/mcp/tools/call",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": kwargs
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if "result" in data:
                return ToolResult(success=True, result=data["result"])
            elif "error" in data:
                return ToolResult(success=False, error=data["error"]["message"])
            else:
                return ToolResult(success=False, error="Unknown response format")
        
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    # Convenience methods for common operations
    async def calculate(self, expression: str) -> float:
        """
        Perform a mathematical calculation.
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            Calculation result
            
        Raises:
            VoluteMCPError: If calculation fails
        """
        result = await self.call_tool("calculate", expression=expression)
        if not result.success:
            raise VoluteMCPError(f"Calculation failed: {result.error}")
        return result.result
    
    async def echo(self, message: str) -> str:
        """
        Echo a message (useful for testing connectivity).
        
        Args:
            message: Message to echo
            
        Returns:
            Echoed message
        """
        result = await self.call_tool("echo", message=message)
        if not result.success:
            raise VoluteMCPError(f"Echo failed: {result.error}")
        return result.result
    
    async def get_server_info(self) -> Dict[str, Any]:
        """
        Get information about the VoluteMCP server.
        
        Returns:
            Server information dictionary
        """
        result = await self.call_tool("get_server_info")
        if not result.success:
            raise VoluteMCPError(f"Failed to get server info: {result.error}")
        return result.result


# Synchronous wrapper for non-async applications
class VoluteMCPClient:
    """
    Synchronous wrapper for VoluteMCP cloud services.
    """
    
    def __init__(self, base_url: str = "https://volutemcp-server.onrender.com"):
        self.async_client = VoluteMCPCloudClient(base_url)
    
    def health_check(self) -> bool:
        """Check server health."""
        return asyncio.run(self.async_client.health_check())
    
    def list_available_tools(self) -> List[Dict[str, Any]]:
        """List available tools."""
        return asyncio.run(self.async_client.list_available_tools())
    
    def call_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Call a tool."""
        return asyncio.run(self.async_client.call_tool(tool_name, **kwargs))
    
    def calculate(self, expression: str) -> float:
        """Perform calculation."""
        return asyncio.run(self.async_client.calculate(expression))
    
    def echo(self, message: str) -> str:
        """Echo message."""
        return asyncio.run(self.async_client.echo(message))
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server info."""
        return asyncio.run(self.async_client.get_server_info())
    
    def close(self):
        """Close the client."""
        asyncio.run(self.async_client.close())
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Factory function for easy instantiation
def create_client(async_mode: bool = True, base_url: str = "https://volutemcp-server.onrender.com"):
    """
    Create a VoluteMCP client.
    
    Args:
        async_mode: If True, returns async client. If False, returns sync client.
        base_url: VoluteMCP server URL
        
    Returns:
        VoluteMCP client instance
    """
    if async_mode:
        return VoluteMCPCloudClient(base_url)
    else:
        return VoluteMCPClient(base_url)
