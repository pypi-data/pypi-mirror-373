"""
Discord MCP Server - A Model Context Protocol server for Discord integration.

This package provides MCP tools for retrieving Discord messages and attachments
through a standardized interface compatible with Claude Desktop and other MCP clients.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .server import DiscordMCPServer
from .tools import (
    get_channel_info,
    get_messages_by_date,
    get_messages_with_attachments,
    get_recent_messages,
    search_messages,
)

__all__ = [
    "DiscordMCPServer",
    "get_recent_messages",
    "get_messages_by_date",
    "get_messages_with_attachments",
    "search_messages",
    "get_channel_info",
]
