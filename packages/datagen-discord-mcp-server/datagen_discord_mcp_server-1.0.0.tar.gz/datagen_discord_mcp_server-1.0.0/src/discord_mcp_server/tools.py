"""
Discord MCP Tools implementation.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import discord

logger = logging.getLogger(__name__)


def format_message(message: discord.Message) -> Dict[str, Any]:
    """Format a Discord message into a structured dictionary."""
    attachments = []
    for attachment in message.attachments:
        attachments.append(
            {
                "filename": attachment.filename,
                "url": attachment.url,
                "size": attachment.size,
                "content_type": attachment.content_type,
            }
        )

    return {
        "id": str(message.id),
        "content": message.content,
        "author": {
            "id": str(message.author.id),
            "name": message.author.name,
            "display_name": message.author.display_name,
            "bot": message.author.bot,
        },
        "channel": {"id": str(message.channel.id), "name": getattr(message.channel, "name", "DM")},
        "timestamp": message.created_at.isoformat(),
        "edited_timestamp": message.edited_at.isoformat() if message.edited_at else None,
        "attachments": attachments,
        "embeds": len(message.embeds),
        "reactions": len(message.reactions) if message.reactions else 0,
    }


def setup_tools(mcp, server):
    """Set up all MCP tools with the given server instance."""

    @mcp.tool()
    async def get_recent_messages(channel_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recent messages from a Discord channel.

        Args:
            channel_id: The Discord channel ID (as string)
            limit: Number of recent messages to retrieve (default: 10, max: 100)

        Returns:
            List of formatted message dictionaries
        """
        try:
            # Validate limit
            if limit > 100:
                limit = 100
            if limit < 1:
                limit = 1

            channel = await server.get_channel(channel_id)

            messages = []
            async for message in channel.history(limit=limit):
                messages.append(format_message(message))

            return messages

        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to retrieve recent messages: {str(e)}")
            raise RuntimeError(f"Failed to retrieve messages: {str(e)}")

    @mcp.tool()
    async def get_messages_by_date(
        channel_id: str, hours_ago: int = 24, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get messages from a Discord channel within a specific time period.

        Args:
            channel_id: The Discord channel ID (as string)
            hours_ago: Number of hours ago to look back (default: 24)
            limit: Maximum number of messages to retrieve (default: 100, max: 500)

        Returns:
            List of formatted message dictionaries
        """
        try:
            # Validate inputs
            if limit > 500:
                limit = 500
            if limit < 1:
                limit = 1
            if hours_ago < 1:
                hours_ago = 1

            channel = await server.get_channel(channel_id)

            # Calculate the cutoff time
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_ago)

            messages = []
            async for message in channel.history(limit=limit, after=cutoff_time):
                messages.append(format_message(message))

            return messages

        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to retrieve messages by date: {str(e)}")
            raise RuntimeError(f"Failed to retrieve messages: {str(e)}")

    @mcp.tool()
    async def get_messages_with_attachments(
        channel_id: str, limit: int = 50, hours_ago: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get messages that contain attachments from a Discord channel.

        Args:
            channel_id: The Discord channel ID (as string)
            limit: Maximum number of messages to scan (default: 50, max: 200)
            hours_ago: Optional time limit in hours (if not provided, scans all recent messages)

        Returns:
            List of formatted message dictionaries that contain attachments
        """
        try:
            # Validate inputs
            if limit > 200:
                limit = 200
            if limit < 1:
                limit = 1

            channel = await server.get_channel(channel_id)

            # Calculate cutoff time if specified
            after_time = None
            if hours_ago:
                after_time = datetime.now(timezone.utc) - timedelta(hours=hours_ago)

            messages_with_attachments = []
            async for message in channel.history(limit=limit, after=after_time):
                if message.attachments:
                    messages_with_attachments.append(format_message(message))

            return messages_with_attachments

        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to retrieve messages with attachments: {str(e)}")
            raise RuntimeError(f"Failed to retrieve messages with attachments: {str(e)}")

    @mcp.tool()
    async def search_messages(
        channel_id: str, query: str, limit: int = 50, hours_ago: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for messages containing specific text in a Discord channel.

        Args:
            channel_id: The Discord channel ID (as string)
            query: Text to search for in message content
            limit: Maximum number of messages to scan (default: 50, max: 200)
            hours_ago: Optional time limit in hours (if not provided, scans all recent messages)

        Returns:
            List of formatted message dictionaries containing the search query
        """
        try:
            # Validate inputs
            if limit > 200:
                limit = 200
            if limit < 1:
                limit = 1
            if not query.strip():
                raise ValueError("Search query cannot be empty")

            channel = await server.get_channel(channel_id)

            # Calculate cutoff time if specified
            after_time = None
            if hours_ago:
                after_time = datetime.now(timezone.utc) - timedelta(hours=hours_ago)

            matching_messages = []
            query_lower = query.lower()

            async for message in channel.history(limit=limit, after=after_time):
                if query_lower in message.content.lower():
                    matching_messages.append(format_message(message))

            return matching_messages

        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to search messages: {str(e)}")
            raise RuntimeError(f"Failed to search messages: {str(e)}")

    @mcp.tool()
    async def get_channel_info(channel_id: str) -> Dict[str, Any]:
        """
        Get information about a Discord channel.

        Args:
            channel_id: The Discord channel ID (as string)

        Returns:
            Dictionary containing channel information
        """
        try:
            channel = await server.get_channel(channel_id)

            channel_info = {
                "id": str(channel.id),
                "name": channel.name,
                "type": str(channel.type),
                "created_at": channel.created_at.isoformat(),
            }

            # Add additional info for text channels
            if hasattr(channel, "topic"):
                channel_info["topic"] = channel.topic
            if hasattr(channel, "category"):
                channel_info["category"] = channel.category.name if channel.category else None
            if hasattr(channel, "guild"):
                channel_info["guild"] = {"id": str(channel.guild.id), "name": channel.guild.name}

            return channel_info

        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to get channel info: {str(e)}")
            raise RuntimeError(f"Failed to get channel info: {str(e)}")


# Export the individual functions for backward compatibility
async def get_recent_messages(channel_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Standalone function version - requires server instance."""
    raise NotImplementedError("Use DiscordMCPServer instance instead")


async def get_messages_by_date(
    channel_id: str, hours_ago: int = 24, limit: int = 100
) -> List[Dict[str, Any]]:
    """Standalone function version - requires server instance."""
    raise NotImplementedError("Use DiscordMCPServer instance instead")


async def get_messages_with_attachments(
    channel_id: str, limit: int = 50, hours_ago: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Standalone function version - requires server instance."""
    raise NotImplementedError("Use DiscordMCPServer instance instead")


async def search_messages(
    channel_id: str, query: str, limit: int = 50, hours_ago: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Standalone function version - requires server instance."""
    raise NotImplementedError("Use DiscordMCPServer instance instead")


async def get_channel_info(channel_id: str) -> Dict[str, Any]:
    """Standalone function version - requires server instance."""
    raise NotImplementedError("Use DiscordMCPServer instance instead")
