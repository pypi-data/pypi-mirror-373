#!/usr/bin/env python3
"""
AIDLC Dashboard MCP Server - UV Package Version

Simple MCP server implementation for Amazon Q integration.
"""

import asyncio
import json
import sys
import os
from typing import Any, Dict

from .tools import AIDLCDashboardMCPTools


class AIDLCMCPServer:
    """Simple MCP Server for AIDLC Dashboard integration."""
    
    def __init__(self):
        """Initialize the MCP server."""
        dashboard_url = os.environ.get('AIDLC_DASHBOARD_URL', 'http://localhost:8000/api')
        timeout = int(os.environ.get('AIDLC_TIMEOUT', '30'))
        retry_attempts = int(os.environ.get('AIDLC_RETRY_ATTEMPTS', '3'))
        
        self.tools = AIDLCDashboardMCPTools(dashboard_url, timeout, retry_attempts)
        self.initialized = False
    
    def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request."""
        self.initialized = True
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "aidlc-dashboard",
                "version": "1.0.0",
                "description": "AIDLC Dashboard MCP Tools"
            }
        }
    
    def handle_list_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP list_tools request."""
        return {
            "tools": [
                {
                    "name": "aidlc_create_project",
                    "description": "Create a new project in the AIDLC Dashboard",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Project name"},
                            "description": {"type": "string", "description": "Optional project description"}
                        },
                        "required": ["name"]
                    }
                },
                {
                    "name": "aidlc_get_project_status",
                    "description": "Get current project status and progress",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {"type": "string", "description": "Project identifier"}
                        },
                        "required": ["project_id"]
                    }
                },
                {
                    "name": "aidlc_upload_epics",
                    "description": "Upload generated epics to a project",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {"type": "string", "description": "Target project identifier"},
                            "epics": {
                                "type": "array",
                                "description": "List of epic objects",
                                "items": {"type": "object"}
                            }
                        },
                        "required": ["project_id", "epics"]
                    }
                },
                {
                    "name": "aidlc_upload_user_stories",
                    "description": "Upload generated user stories to a project",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {"type": "string", "description": "Target project identifier"},
                            "user_stories": {"type": "array", "description": "List of user story objects"}
                        },
                        "required": ["project_id", "user_stories"]
                    }
                },
                {
                    "name": "aidlc_upload_domain_model",
                    "description": "Upload domain model entities to a project",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {"type": "string", "description": "Target project identifier"},
                            "domain_entities": {"type": "array", "description": "List of domain entity objects"}
                        },
                        "required": ["project_id", "domain_entities"]
                    }
                },
                {
                    "name": "aidlc_upload_model_code_plan",
                    "description": "Upload model code plan phases to a project",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {"type": "string", "description": "Target project identifier"},
                            "code_phases": {"type": "array", "description": "List of code plan phase objects"}
                        },
                        "required": ["project_id", "code_phases"]
                    }
                },
                {
                    "name": "aidlc_upload_ui_code_plan",
                    "description": "Upload UI code plan to a project",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {"type": "string", "description": "Target project identifier"},
                            "ui_code_plan": {"type": "object", "description": "UI code plan object"}
                        },
                        "required": ["project_id", "ui_code_plan"]
                    }
                },
                {
                    "name": "aidlc_update_artifact_status",
                    "description": "Update artifact completion status",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {"type": "string", "description": "Project identifier"},
                            "artifact_type": {"type": "string", "description": "Type of artifact to update"},
                            "status": {"type": "string", "description": "New status (not-started, in-progress, completed)"},
                            "notes": {"type": "string", "description": "Optional status update notes"}
                        },
                        "required": ["project_id", "artifact_type", "status"]
                    }
                },
                {
                    "name": "aidlc_health_check",
                    "description": "Check dashboard service health and connectivity",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            ]
        }
    
    def handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP call_tool request."""
        if not self.initialized:
            return {
                "isError": True,
                "content": [{"type": "text", "text": "Server not initialized"}]
            }
        
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            # Route to appropriate tool method
            if tool_name == "aidlc_health_check":
                result = self.tools.aidlc_health_check()
            elif tool_name == "aidlc_create_project":
                result = self.tools.aidlc_create_project(
                    arguments["name"],
                    arguments.get("description", "")
                )
            elif tool_name == "aidlc_get_project_status":
                result = self.tools.aidlc_get_project_status(arguments["project_id"])
            elif tool_name == "aidlc_upload_epics":
                result = self.tools.aidlc_upload_epics(
                    arguments["project_id"],
                    arguments["epics"]
                )
            elif tool_name == "aidlc_upload_user_stories":
                result = self.tools.aidlc_upload_user_stories(
                    arguments["project_id"],
                    arguments["user_stories"]
                )
            elif tool_name == "aidlc_upload_domain_model":
                result = self.tools.aidlc_upload_domain_model(
                    arguments["project_id"],
                    arguments["domain_entities"]
                )
            elif tool_name == "aidlc_upload_model_code_plan":
                result = self.tools.aidlc_upload_model_code_plan(
                    arguments["project_id"],
                    arguments["code_phases"]
                )
            elif tool_name == "aidlc_upload_ui_code_plan":
                result = self.tools.aidlc_upload_ui_code_plan(
                    arguments["project_id"],
                    arguments["ui_code_plan"]
                )
            elif tool_name == "aidlc_update_artifact_status":
                result = self.tools.aidlc_update_artifact_status(
                    arguments["project_id"],
                    arguments["artifact_type"],
                    arguments["status"],
                    arguments.get("notes", "")
                )
            else:
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}]
                }
            
            # Format response
            if result.success:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result.data, indent=2) if result.data else "Success"
                        }
                    ]
                }
            else:
                return {
                    "isError": True,
                    "content": [
                        {
                            "type": "text",
                            "text": f"Tool execution failed: {result.error}"
                        }
                    ]
                }
                
        except Exception as e:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Internal error: {str(e)}"}]
            }
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP message."""
        method = message.get("method")
        params = message.get("params", {})
        
        if method == "initialize":
            result = self.handle_initialize(params)
            return {"result": result}
        elif method == "tools/list":
            result = self.handle_list_tools(params)
            return {"result": result}
        elif method == "tools/call":
            result = self.handle_call_tool(params)
            return {"result": result}
        else:
            return {
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    async def run(self):
        """Run the MCP server with stdio communication."""
        try:
            while True:
                # Read message from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                try:
                    message = json.loads(line.strip())
                    response = await self.handle_message(message)
                    
                    # Add message ID if present
                    if "id" in message:
                        response["id"] = message["id"]
                    
                    # Send response to stdout
                    print(json.dumps(response), flush=True)
                    
                except json.JSONDecodeError:
                    error_response = {
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    if "id" in message:
                        error_response["id"] = message["id"]
                    print(json.dumps(error_response), flush=True)
                    
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Server error: {e}", file=sys.stderr)


async def main():
    """Main entry point."""
    server = AIDLCMCPServer()
    await server.run()


def sync_main():
    """Synchronous entry point for MCP server."""
    asyncio.run(main())


if __name__ == "__main__":
    sync_main()
