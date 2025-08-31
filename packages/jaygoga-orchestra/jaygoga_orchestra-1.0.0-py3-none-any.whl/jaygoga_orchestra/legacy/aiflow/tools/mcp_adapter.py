"""
Model Context Protocol (MCP) Adapter for AIFlow.

Provides seamless integration with MCP servers, allowing AIFlow agents to use
tools from external MCP servers just like Govinda does.

Supports:
- Stdio transport (local servers)
- SSE transport (Server-Sent Events for remote servers)
- Streamable HTTP transport (flexible HTTP communication)
"""

import asyncio
import json
import os
import subprocess
import aiohttp
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from .base_tool import BaseTool


@dataclass
class StdioServerParameters:
    """Parameters for Stdio MCP server connection."""
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None


@dataclass
class SSEServerParameters:
    """Parameters for SSE MCP server connection."""
    url: str
    transport: str = "sse"
    headers: Optional[Dict[str, str]] = None


@dataclass
class StreamableHTTPServerParameters:
    """Parameters for Streamable HTTP MCP server connection."""
    url: str
    transport: str = "streamable-http"
    headers: Optional[Dict[str, str]] = None


class MCPTool(BaseTool):
    """Wrapper for MCP server tools."""
    
    def __init__(self, name: str, description: str, schema: Dict[str, Any], adapter: 'MCPServerAdapter'):
        super().__init__(name, description)
        self.schema = schema
        self.adapter = adapter
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the MCP tool through the adapter."""
        try:
            result = await self.adapter.call_tool(self.name, kwargs)
            return {
                "success": True,
                "tool_name": self.name,
                "result": result,
                "source": "MCP Server"
            }
        except Exception as e:
            return {
                "success": False,
                "tool_name": self.name,
                "error": str(e),
                "source": "MCP Server"
            }
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        """Get the parameters schema for this MCP tool."""
        return self.schema.get("inputSchema", {})


class MCPServerAdapter:
    """
    Adapter for connecting to MCP servers and using their tools.
    
    Supports multiple transport mechanisms:
    - Stdio: for local servers
    - SSE: for remote servers with Server-Sent Events
    - Streamable HTTP: for flexible HTTP communication
    """
    
    def __init__(
        self,
        server_params: Union[StdioServerParameters, SSEServerParameters, StreamableHTTPServerParameters, Dict],
        *tool_names: str,
        connect_timeout: int = 30
    ):
        """
        Initialize MCP server adapter.
        
        Args:
            server_params: Server connection parameters
            *tool_names: Optional tool names to filter (if empty, all tools are loaded)
            connect_timeout: Connection timeout in seconds
        """
        self.server_params = server_params
        self.tool_filter = list(tool_names) if tool_names else None
        self.connect_timeout = connect_timeout
        
        # Connection state
        self.connected = False
        self.process = None
        self.session = None
        self.tools: Dict[str, MCPTool] = {}
        
        # Determine transport type
        if isinstance(server_params, StdioServerParameters):
            self.transport = "stdio"
        elif isinstance(server_params, (SSEServerParameters, StreamableHTTPServerParameters)):
            self.transport = server_params.transport
        elif isinstance(server_params, dict):
            self.transport = server_params.get("transport", "stdio")
        else:
            raise ValueError("Invalid server parameters")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    async def connect(self):
        """Connect to the MCP server."""
        if self.connected:
            return
        
        try:
            if self.transport == "stdio":
                await self._connect_stdio()
            elif self.transport == "sse":
                await self._connect_sse()
            elif self.transport == "streamable-http":
                await self._connect_streamable_http()
            else:
                raise ValueError(f"Unsupported transport: {self.transport}")
            
            # Load available tools
            await self._load_tools()
            self.connected = True
            
        except Exception as e:
            await self.disconnect()
            raise Exception(f"Failed to connect to MCP server: {str(e)}")
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.process:
            try:
                self.process.terminate()
                await self.process.wait()
            except:
                pass
            self.process = None
        
        if self.session:
            try:
                await self.session.close()
            except:
                pass
            self.session = None
        
        self.connected = False
        self.tools.clear()
    
    async def _connect_stdio(self):
        """Connect to stdio MCP server."""
        if isinstance(self.server_params, StdioServerParameters):
            params = self.server_params
        else:
            # Handle dict format
            params = StdioServerParameters(
                command=self.server_params["command"],
                args=self.server_params["args"],
                env=self.server_params.get("env")
            )
        
        env = os.environ.copy()
        if params.env:
            env.update(params.env)
        
        self.process = await asyncio.create_subprocess_exec(
            params.command,
            *params.args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        
        # Wait for process to start
        await asyncio.sleep(0.1)
        if self.process.returncode is not None:
            raise Exception("MCP server process failed to start")
    
    async def _connect_sse(self):
        """Connect to SSE MCP server."""
        if isinstance(self.server_params, SSEServerParameters):
            params = self.server_params
        else:
            params = SSEServerParameters(
                url=self.server_params["url"],
                transport=self.server_params.get("transport", "sse"),
                headers=self.server_params.get("headers")
            )
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.connect_timeout)
        )
        
        # Test connection
        headers = params.headers or {}
        async with self.session.get(params.url, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"SSE server returned status {response.status}")
    
    async def _connect_streamable_http(self):
        """Connect to Streamable HTTP MCP server."""
        if isinstance(self.server_params, StreamableHTTPServerParameters):
            params = self.server_params
        else:
            params = StreamableHTTPServerParameters(
                url=self.server_params["url"],
                transport=self.server_params.get("transport", "streamable-http"),
                headers=self.server_params.get("headers")
            )
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.connect_timeout)
        )
        
        # Test connection with health check
        headers = params.headers or {}
        try:
            async with self.session.get(f"{params.url}/health", headers=headers) as response:
                if response.status not in [200, 404]:  # 404 is OK if no health endpoint
                    raise Exception(f"HTTP server returned status {response.status}")
        except aiohttp.ClientError as e:
            # Try the main URL if health check fails
            async with self.session.get(params.url, headers=headers) as response:
                if response.status >= 400:
                    raise Exception(f"HTTP server returned status {response.status}")
    
    async def _load_tools(self):
        """Load available tools from the MCP server."""
        try:
            if self.transport == "stdio":
                tools_data = await self._list_tools_stdio()
            elif self.transport in ["sse", "streamable-http"]:
                tools_data = await self._list_tools_http()
            else:
                raise ValueError(f"Unsupported transport: {self.transport}")
            
            # Create MCPTool instances
            for tool_data in tools_data:
                tool_name = tool_data["name"]
                
                # Apply tool filter if specified
                if self.tool_filter and tool_name not in self.tool_filter:
                    continue
                
                tool = MCPTool(
                    name=tool_name,
                    description=tool_data.get("description", ""),
                    schema=tool_data,
                    adapter=self
                )
                self.tools[tool_name] = tool
                
        except Exception as e:
            raise Exception(f"Failed to load tools from MCP server: {str(e)}")
    
    async def _list_tools_stdio(self) -> List[Dict[str, Any]]:
        """List tools from stdio MCP server."""
        if not self.process:
            raise Exception("Not connected to stdio server")
        
        # Send list_tools request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        request_data = json.dumps(request) + "\n"
        self.process.stdin.write(request_data.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_line = await self.process.stdout.readline()
        response = json.loads(response_line.decode().strip())
        
        if "error" in response:
            raise Exception(f"MCP server error: {response['error']}")
        
        return response.get("result", {}).get("tools", [])
    
    async def _list_tools_http(self) -> List[Dict[str, Any]]:
        """List tools from HTTP MCP server."""
        if not self.session:
            raise Exception("Not connected to HTTP server")
        
        url = self.server_params["url"] if isinstance(self.server_params, dict) else self.server_params.url
        
        # Try different endpoints for tool listing
        endpoints = ["/tools/list", "/tools", "/mcp/tools"]
        
        for endpoint in endpoints:
            try:
                async with self.session.get(f"{url}{endpoint}") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("tools", [])
            except:
                continue
        
        # Fallback: return empty list if no tools endpoint found
        return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the MCP server."""
        if not self.connected:
            raise Exception("Not connected to MCP server")
        
        if tool_name not in self.tools:
            raise Exception(f"Tool '{tool_name}' not found")
        
        try:
            if self.transport == "stdio":
                return await self._call_tool_stdio(tool_name, arguments)
            elif self.transport in ["sse", "streamable-http"]:
                return await self._call_tool_http(tool_name, arguments)
            else:
                raise ValueError(f"Unsupported transport: {self.transport}")
                
        except Exception as e:
            raise Exception(f"Failed to call tool '{tool_name}': {str(e)}")
    
    async def _call_tool_stdio(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call tool via stdio."""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        request_data = json.dumps(request) + "\n"
        self.process.stdin.write(request_data.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_line = await self.process.stdout.readline()
        response = json.loads(response_line.decode().strip())
        
        if "error" in response:
            raise Exception(f"MCP server error: {response['error']}")
        
        result = response.get("result", {})
        return result.get("content", [{}])[0].get("text", result)
    
    async def _call_tool_http(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call tool via HTTP."""
        url = self.server_params["url"] if isinstance(self.server_params, dict) else self.server_params.url
        
        payload = {
            "tool": tool_name,
            "arguments": arguments
        }
        
        async with self.session.post(f"{url}/tools/call", json=payload) as response:
            if response.status != 200:
                raise Exception(f"HTTP server returned status {response.status}")
            
            result = await response.json()
            return result.get("content", result)
    
    def __iter__(self):
        """Iterate over available tools."""
        return iter(self.tools.values())
    
    def __len__(self):
        """Get number of available tools."""
        return len(self.tools)
    
    def __getitem__(self, tool_name: str) -> MCPTool:
        """Get a specific tool by name."""
        if tool_name not in self.tools:
            raise KeyError(f"Tool '{tool_name}' not found")
        return self.tools[tool_name]
    
    def get_tool_names(self) -> List[str]:
        """Get list of available tool names."""
        return list(self.tools.keys())
    
    def get_tools(self, *tool_names: str) -> List[MCPTool]:
        """Get specific tools by name."""
        if not tool_names:
            return list(self.tools.values())
        
        result = []
        for name in tool_names:
            if name in self.tools:
                result.append(self.tools[name])
        return result
