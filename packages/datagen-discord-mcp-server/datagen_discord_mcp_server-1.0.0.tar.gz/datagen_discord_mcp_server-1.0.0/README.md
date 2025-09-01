# Discord MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that provides Discord integration, allowing AI assistants like Claude to retrieve messages and attachments from Discord channels.

[![PyPI version](https://badge.fury.io/py/datagen-discord-mcp-server.svg)](https://pypi.org/project/datagen-discord-mcp-server/)
[![Python Support](https://img.shields.io/pypi/pyversions/datagen-discord-mcp-server.svg)](https://pypi.org/project/datagen-discord-mcp-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🔍 **Retrieve recent messages** from Discord channels
- 📅 **Time-based message queries** (get messages from last N hours/days)
- 📎 **Find messages with attachments** (images, files, etc.)
- 🔎 **Search messages by content** with flexible text matching
- ℹ️ **Get channel information** and metadata
- 🔒 **Secure authentication** using Discord bot tokens
- 🚀 **Easy installation** via uvx or pip

## Quick Start

### Installation

#### Option 1: Using uvx (Recommended)
```bash
uvx datagen-discord-mcp-server
```

#### Option 2: Using pip
```bash
pip install datagen-discord-mcp-server
```

### Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and bot
3. Copy the bot token
4. Invite the bot to your server with these permissions:
   - Read Messages
   - Read Message History
   - View Channels

### Configuration

#### For Claude Desktop
Add to your Claude Desktop MCP settings (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "discord": {
      "command": "uvx",
      "args": ["datagen-discord-mcp-server"],
      "env": {
        "DISCORD_TOKEN": "your_bot_token_here"
      }
    }
  }
}
```

#### For other MCP clients
```json
{
  "mcpServers": {
    "discord": {
      "command": "datagen-discord-mcp-server",
      "env": {
        "DISCORD_TOKEN": "your_bot_token_here"
      }
    }
  }
}
```

## Usage

Once configured, you can use natural language to query Discord messages through your MCP client:

- *"Get the last 10 messages from channel 123456789"*
- *"Show me messages with attachments from yesterday"*
- *"Search for messages containing 'bug report' from the past week"*
- *"What's the info for channel 123456789?"*

## Available Tools

### `get_recent_messages`
Retrieve the most recent messages from a channel.
- **Parameters**: `channel_id` (string), `limit` (int, max 100)
- **Returns**: List of formatted message objects

### `get_messages_by_date` 
Get messages from a specific time period.
- **Parameters**: `channel_id` (string), `hours_ago` (int), `limit` (int, max 500)  
- **Returns**: List of messages within the time range

### `get_messages_with_attachments`
Find messages containing attachments.
- **Parameters**: `channel_id` (string), `limit` (int, max 200), `hours_ago` (optional)
- **Returns**: List of messages with attachments

### `search_messages`
Search for messages containing specific text.
- **Parameters**: `channel_id` (string), `query` (string), `limit` (int, max 200), `hours_ago` (optional)
- **Returns**: List of matching messages

### `get_channel_info`
Get channel information and metadata.
- **Parameters**: `channel_id` (string)
- **Returns**: Channel information object

## Message Format

Each message is returned with the following structure:

```json
{
  "id": "message_id",
  "content": "message text",
  "author": {
    "id": "user_id", 
    "name": "username",
    "display_name": "display name",
    "bot": false
  },
  "channel": {
    "id": "channel_id",
    "name": "channel_name"
  },
  "timestamp": "2025-01-01T12:00:00+00:00",
  "edited_timestamp": null,
  "attachments": [
    {
      "filename": "image.png",
      "url": "https://cdn.discordapp.com/...",
      "size": 1024,
      "content_type": "image/png"
    }
  ],
  "embeds": 0,
  "reactions": 0
}
```

## Development

### Local Development
```bash
# Clone the repository
git clone https://github.com/yourusername/discord-mcp-server.git
cd discord-mcp-server

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run the server
datagen-discord-mcp-server --debug
```

### Building and Publishing
```bash
# Build the package
python -m build

# Upload to PyPI
twine upload dist/*
```

## Getting Channel IDs

To get Discord channel IDs:
1. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
2. Right-click on the channel you want
3. Select "Copy Channel ID"

## Troubleshooting

### Common Issues

**"Channel not found" errors:**
- Verify the channel ID is correct
- Ensure your bot has access to the channel
- Check that the bot has "Read Message History" permission

**"Authentication failed":**
- Verify your Discord bot token is correct
- Make sure the token is set in the environment variable
- Ensure the bot is added to the Discord server

**Import or installation errors:**
- Try using Python 3.8-3.12 (avoid 3.13 due to discord.py compatibility)
- Reinstall with `pip install --upgrade datagen-discord-mcp-server`

### Debug Mode
Run with debug logging to troubleshoot issues:
```bash
datagen-discord-mcp-server --debug
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://github.com/yourusername/discord-mcp-server#readme)
- 🐛 [Bug Reports](https://github.com/yourusername/discord-mcp-server/issues)
- 💬 [Discussions](https://github.com/yourusername/discord-mcp-server/discussions) 