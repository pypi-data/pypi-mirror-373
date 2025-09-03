#!/usr/bin/env python3
"""
Test MCP server functionality
"""

import asyncio
import sys
import os

# Add the package to path
sys.path.insert(0, os.path.dirname(__file__))

async def test_mcp_server():
    """Test MCP server initialization"""
    
    print("🧪 Testing MCP Server...")
    
    try:
        from aidlc_mcp_tools.server import AIDLCMCPServer
        
        # Test server initialization
        server = AIDLCMCPServer()
        print("✅ MCP Server initialization: SUCCESS")
        
        # Test tools availability
        if hasattr(server, 'tools'):
            print("✅ MCP Server tools: SUCCESS")
        else:
            print("❌ MCP Server tools: MISSING")
            
        print("\n🎉 MCP Server tests completed!")
        return True
        
    except ImportError as e:
        print(f"❌ MCP Server import: FAILED - {e}")
        return False
    except Exception as e:
        print(f"❌ MCP Server test: FAILED - {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
