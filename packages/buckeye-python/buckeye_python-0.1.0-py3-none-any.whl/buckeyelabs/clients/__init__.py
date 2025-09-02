"""Buckeye MCP client implementations."""

from __future__ import annotations

from .base import AgentMCPClient, BaseBUCKEYEClient
from .fastmcp import FastMCPBUCKClient

# Default to FastMCP for new features
MCPClient = FastMCPBUCKClient

__all__ = [
    "AgentMCPClient",
    "BaseBUCKEYEClient",
    "FastMCPBUCKClient",
    "MCPClient",
]
