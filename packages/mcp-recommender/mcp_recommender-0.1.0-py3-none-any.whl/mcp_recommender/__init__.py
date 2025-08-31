"""MCP Recommender - A smart MCP server to recommend other MCPs based on your needs."""

import asyncio
from .server import create_server

def main():
    """Main entry point for the MCP Recommender server."""
    server = create_server()
    asyncio.run(server.run())

__version__ = "0.1.0"