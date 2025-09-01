"""
Discord MCP Server implementation.
"""

import asyncio
import logging
import os
from typing import Any, Dict, Optional

import discord
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


class DiscordMCPServer:
    """Discord MCP Server class for managing Discord API integration."""

    def __init__(self, token: Optional[str] = None):
        """
        Initialize the Discord MCP Server.

        Args:
            token: Discord bot token. If not provided, will look for DISCORD_TOKEN env var.
        """
        self.token = token or os.getenv("DISCORD_TOKEN")
        if not self.token:
            raise ValueError(
                "Discord token is required. Provide it via token parameter or DISCORD_TOKEN environment variable."
            )

        # Discord client setup
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)
        self.client_ready = False

        # Set up event handlers
        self._setup_events()

        # Initialize MCP server
        self.mcp = FastMCP("Discord Message Server")
        self._setup_tools()

    def _setup_events(self):
        """Set up Discord client event handlers."""

        @self.client.event
        async def on_ready():
            self.client_ready = True
            logger.info(f"Discord client logged in as {self.client.user}")
            logger.info(f"Bot is in {len(self.client.guilds)} servers:")
            for guild in self.client.guilds:
                logger.info(f"  - {guild.name} (ID: {guild.id})")
            logger.info("Bot is ready!")

    async def ensure_client_ready(self):
        """Ensure Discord client is logged in and ready."""
        if self.client_ready and not self.client.is_closed():
            return  # Already ready

        if not self.client_ready:
            logger.info("Starting Discord client...")
            # Start the client in background
            asyncio.create_task(self.client.start(self.token))

            # Wait for client to be ready with timeout
            timeout = 30  # 30 seconds timeout
            wait_time = 0
            while not self.client_ready and wait_time < timeout:
                await asyncio.sleep(0.1)
                wait_time += 0.1

            if not self.client_ready:
                raise RuntimeError("Failed to connect to Discord within 30 seconds")

    def _setup_tools(self):
        """Set up MCP tools."""
        from .tools import setup_tools

        setup_tools(self.mcp, self)

    def run(self):
        """Run the MCP server."""
        self.mcp.run()

    async def get_channel(self, channel_id: str) -> Optional[discord.TextChannel]:
        """
        Get a Discord channel by ID.

        Args:
            channel_id: The Discord channel ID as string

        Returns:
            Discord channel object or None if not found

        Raises:
            ValueError: If channel not found or bot doesn't have access
        """
        await self.ensure_client_ready()

        logger.debug(f"Searching for channel ID {channel_id}")
        logger.debug(f"Bot is in {len(self.client.guilds)} servers")

        for guild in self.client.guilds:
            logger.debug(f"Guild {guild.name} (ID: {guild.id}) has {len(guild.channels)} channels")

        try:
            channel_id_int = int(channel_id)
        except ValueError:
            raise ValueError(f"Invalid channel ID format: {channel_id}")

        channel = self.client.get_channel(channel_id_int)
        if not channel:
            logger.debug(f"Channel {channel_id} not found via get_channel")
            # Try to find channel in all guilds
            for guild in self.client.guilds:
                for ch in guild.channels:
                    if ch.id == channel_id_int:
                        logger.debug(f"Found channel {ch.name} in guild {guild.name}")
                        channel = ch
                        break
                if channel:
                    break

        if not channel:
            raise ValueError(f"Channel with ID {channel_id} not found or bot doesn't have access")

        if not isinstance(channel, discord.TextChannel):
            raise ValueError(f"Channel {channel_id} is not a text channel")

        logger.debug(f"Successfully found channel {channel.name} in {channel.guild.name}")
        return channel
