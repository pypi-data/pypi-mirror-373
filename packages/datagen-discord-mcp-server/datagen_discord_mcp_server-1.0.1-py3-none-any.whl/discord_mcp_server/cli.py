#!/usr/bin/env python3
"""
Command line interface for Discord MCP Server.
"""

import argparse
import logging
import os
import sys
from typing import Optional

from dotenv import load_dotenv

from .server import DiscordMCPServer


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info >= (3, 13):
        print(
            f"ERROR: Python {sys.version_info.major}.{sys.version_info.minor} is not supported.",
            file=sys.stderr
        )
        print(
            "This package requires Python 3.8-3.12 due to discord.py compatibility issues.", 
            file=sys.stderr
        )
        print(
            "Please use Python 3.8-3.12 or install with a different Python version:", 
            file=sys.stderr
        )
        print("  uvx --python python3.11 datagen-discord-mcp-server", file=sys.stderr)
        sys.exit(1)
    elif sys.version_info < (3, 8):
        print(
            f"ERROR: Python {sys.version_info.major}.{sys.version_info.minor} is not supported.",
            file=sys.stderr
        )
        print("This package requires Python 3.8 or newer.", file=sys.stderr)
        sys.exit(1)


def setup_logging(debug: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def validate_token(token: Optional[str]) -> str:
    """
    Validate and return Discord token.

    Args:
        token: Token to validate

    Returns:
        Valid token

    Raises:
        ValueError: If token is invalid or not found
    """
    if not token:
        raise ValueError(
            "Discord token is required. Set DISCORD_TOKEN environment variable "
            "or pass --token argument."
        )

    if not token.strip():
        raise ValueError("Discord token cannot be empty.")

    # Basic token format validation (Discord bot tokens are typically 59 characters)
    if len(token.strip()) < 50:
        raise ValueError("Discord token appears to be invalid (too short).")

    return token.strip()


def main():
    """Main CLI entry point."""
    # Check Python version compatibility first
    check_python_version()
    
    parser = argparse.ArgumentParser(
        description="Discord MCP Server - Provides Discord integration for Model Context Protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  DISCORD_TOKEN    Discord bot token (required)

Examples:
  datagen-discord-mcp-server
  datagen-discord-mcp-server --debug
  datagen-discord-mcp-server --token YOUR_BOT_TOKEN
  
Configuration for Claude Desktop:
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
        """,
    )

    parser.add_argument(
        "--token", type=str, help="Discord bot token (overrides DISCORD_TOKEN env var)"
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.1")

    args = parser.parse_args()

    # Set up logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)

    # Load environment variables
    load_dotenv()

    try:
        # Get and validate token
        token = args.token or os.getenv("DISCORD_TOKEN")
        token = validate_token(token)

        # Create and run server
        logger.info("Starting Discord MCP Server...")
        server = DiscordMCPServer(token=token)
        server.run()

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
