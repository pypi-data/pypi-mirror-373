#!/usr/bin/env python3
"""
Test MCP server with proper sync entry point
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, '/home/ec2-user/mcp-tools')

def sync_main():
    """Synchronous entry point for MCP server"""
    from aidlc_mcp_tools.server import main
    asyncio.run(main())

if __name__ == "__main__":
    sync_main()
