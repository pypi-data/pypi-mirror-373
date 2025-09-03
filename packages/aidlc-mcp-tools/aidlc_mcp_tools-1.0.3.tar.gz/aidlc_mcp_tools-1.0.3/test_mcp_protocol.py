#!/usr/bin/env python3
"""Test MCP protocol interaction"""
import json
import subprocess
import sys
import os

# Set environment
os.environ['AIDLC_DASHBOARD_URL'] = 'http://44.253.191.105:8000/api'

def test_mcp_server():
    """Test MCP server protocol"""
    
    # Start MCP server
    process = subprocess.Popen(
        ['python', '-m', 'aidlc_mcp_tools.server'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd='/home/ec2-user/mcp-tools'
    )
    
    try:
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0.0"}
            }
        }
        
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print("Initialize response:", response.strip())
        
        # Send tools/list request
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        process.stdin.write(json.dumps(tools_request) + '\n')
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print("Tools list response:", response.strip())
        
        # Parse and show tools
        try:
            tools_data = json.loads(response)
            if 'result' in tools_data and 'tools' in tools_data['result']:
                tools = tools_data['result']['tools']
                print(f"Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  - {tool['name']}: {tool['description']}")
            else:
                print("No tools found in response")
        except json.JSONDecodeError:
            print("Failed to parse tools response")
        
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_mcp_server()
