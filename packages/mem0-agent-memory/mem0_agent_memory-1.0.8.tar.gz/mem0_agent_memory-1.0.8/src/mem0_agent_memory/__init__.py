"""Mem0 Agent Memory - MCP server for Mem0 agent memory management."""

from .server import run_server

__version__ = "1.0.6"
__author__ = "Arunkumar Selvam"
__email__ = "aruninfy123@gmail.com"

def main():
    """Entry point for the MCP server."""
    run_server()

if __name__ == "__main__":
    main()
