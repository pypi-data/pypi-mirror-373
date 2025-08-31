"""Agentic Blocks - Building blocks for agentic systems."""

from .mcp_client import MCPClient, MCPEndpointError
from .messages import Messages
from .llm import call_llm, LLMError

# Get version from package metadata
try:
    from importlib.metadata import version
    __version__ = version("agentic-blocks")
except Exception:
    __version__ = "unknown"

__all__ = ["MCPClient", "MCPEndpointError", "Messages", "call_llm", "LLMError"]