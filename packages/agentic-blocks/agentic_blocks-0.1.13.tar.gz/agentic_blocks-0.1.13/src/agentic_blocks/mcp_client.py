"""
Simplified MCP Client for connecting to MCP endpoints with sync-by-default API.
"""

import asyncio
import logging
import os
from typing import List, Dict, Any
from urllib.parse import urlparse

from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client

logger = logging.getLogger(__name__)


def handle_jupyter_env():
    """Apply nest_asyncio if running in a Jupyter notebook environment."""
    try:
        # Check if we're in a running event loop (like Jupyter)
        asyncio.get_running_loop()
        try:
            import nest_asyncio
            nest_asyncio.apply()
        except ImportError:
            logger.warning(
                "nest_asyncio not available. Install with: pip install nest-asyncio"
            )
    except RuntimeError:
        # No event loop running, no need for nest_asyncio
        pass


class MCPEndpointError(Exception):
    """Exception raised when there's an error connecting to or using an MCP endpoint."""

    pass


class MCPClient:
    """
    A simplified MCP client that can connect to MCP endpoints with sync-by-default API.

    Supports:
    - SSE endpoints (e.g., 'https://example.com/mcp/server/sse')
    - Streamable HTTP endpoints (e.g., 'https://example.com/mcp/server')
    - Local StdioServer scripts (e.g., 'path/to/server.py')
    """

    def __init__(self, endpoint: str, timeout: int = 30):
        """
        Initialize the MCP client.

        Args:
            endpoint: Either a URL (for SSE/HTTP) or a file path (for StdioServer)
            timeout: Connection timeout in seconds
        """
        self.endpoint = endpoint
        self.timeout = timeout
        self.transport_type = self._detect_transport_type(endpoint)

    def _detect_transport_type(self, endpoint: str) -> str:
        """
        Detect the transport type based on the endpoint.

        Args:
            endpoint: The endpoint URL or file path

        Returns:
            Transport type: 'sse', 'streamable-http', or 'stdio'
        """
        if endpoint.startswith(("http://", "https://")):
            parsed = urlparse(endpoint)
            path = parsed.path.lower()

            if "/sse" in path:
                return "sse"
            elif "/mcp" in path:
                return "streamable-http"
            else:
                return "streamable-http"
        else:
            return "stdio"

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools from the MCP endpoint in OpenAI standard format.

        Returns:
            List of tools in OpenAI function calling format

        Raises:
            MCPEndpointError: If connection or listing fails
        """
        handle_jupyter_env()
        return asyncio.run(self.list_tools_async())

    async def list_tools_async(self) -> List[Dict[str, Any]]:
        """
        Async version of list_tools for advanced users.

        Returns:
            List of tools in OpenAI function calling format

        Raises:
            MCPEndpointError: If connection or listing fails
        """
        try:
            if self.transport_type == "sse":
                async with sse_client(url=self.endpoint, timeout=self.timeout) as (
                    read_stream,
                    write_stream,
                ):
                    return await self._get_tools_from_session(read_stream, write_stream)
            elif self.transport_type == "streamable-http":
                async with streamablehttp_client(
                    url=self.endpoint, timeout=self.timeout
                ) as (read_stream, write_stream, session_id_getter):
                    return await self._get_tools_from_session(read_stream, write_stream)
            elif self.transport_type == "stdio":
                if not os.path.exists(self.endpoint):
                    raise MCPEndpointError(
                        f"StdioServer script not found: {self.endpoint}"
                    )

                server_params = StdioServerParameters(
                    command="python", args=[self.endpoint]
                )
                async with stdio_client(server_params) as (read_stream, write_stream):
                    return await self._get_tools_from_session(read_stream, write_stream)
            else:
                raise MCPEndpointError(
                    f"Unsupported transport type: {self.transport_type}"
                )
        except Exception as e:
            logger.error(f"Failed to list tools from {self.endpoint}: {e}")
            raise MCPEndpointError(f"Failed to list tools: {e}")

    async def _get_tools_from_session(
        self, read_stream, write_stream
    ) -> List[Dict[str, Any]]:
        """Get tools from an MCP session in OpenAI standard format."""
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools_response = await session.list_tools()

            tools = []
            for tool in tools_response.tools:
                function_dict = {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema or {},
                }

                openai_tool = {
                    "type": "function",
                    "function": function_dict,
                }
                tools.append(openai_tool)

            return tools

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a specific tool on the MCP endpoint.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            Tool call result dictionary

        Raises:
            MCPEndpointError: If connection or tool call fails
        """
        handle_jupyter_env()
        return asyncio.run(self.call_tool_async(tool_name, arguments))

    async def call_tool_async(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Async version of call_tool for advanced users.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            Tool call result dictionary

        Raises:
            MCPEndpointError: If connection or tool call fails
        """
        try:
            if self.transport_type == "sse":
                async with sse_client(url=self.endpoint, timeout=self.timeout) as (
                    read_stream,
                    write_stream,
                ):
                    return await self._call_tool_from_session(
                        read_stream, write_stream, tool_name, arguments
                    )
            elif self.transport_type == "streamable-http":
                async with streamablehttp_client(
                    url=self.endpoint, timeout=self.timeout
                ) as (read_stream, write_stream, session_id_getter):
                    return await self._call_tool_from_session(
                        read_stream, write_stream, tool_name, arguments
                    )
            elif self.transport_type == "stdio":
                if not os.path.exists(self.endpoint):
                    raise MCPEndpointError(
                        f"StdioServer script not found: {self.endpoint}"
                    )

                server_params = StdioServerParameters(
                    command="python", args=[self.endpoint]
                )
                async with stdio_client(server_params) as (read_stream, write_stream):
                    return await self._call_tool_from_session(
                        read_stream, write_stream, tool_name, arguments
                    )
            else:
                raise MCPEndpointError(
                    f"Unsupported transport type: {self.transport_type}"
                )
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name} on {self.endpoint}: {e}")
            raise MCPEndpointError(f"Failed to call tool {tool_name}: {e}")

    async def _call_tool_from_session(
        self, read_stream, write_stream, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call a tool from an MCP session."""
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)

            result_dict = {
                "content": [],
                "is_error": result.isError,
            }

            for content in result.content:
                if hasattr(content, "type") and content.type == "text":
                    result_dict["content"].append(
                        {"type": "text", "text": content.text}
                    )
                else:
                    result_dict["content"].append(str(content))

            return result_dict


# Example usage
def example_usage():
    """Example of how to use the simplified MCPClient."""
    # Simple usage with sync API
    client = MCPClient("https://ai-center.se/mcp/think-mcp-server/sse")

    try:
        # List available tools
        tools = client.list_tools()
        print(f"Found {len(tools)} tools")

        # Call a tool if any are available
        if tools:
            result = client.call_tool(
                tools[0]["function"]["name"], {"query": "What is MCP"}
            )
            print(f"Tool result: {result}")
    except MCPEndpointError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    example_usage()
