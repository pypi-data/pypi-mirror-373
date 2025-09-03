#!/usr/bin/env python3
"""
AIDLC MCP Tools Command Line Interface

Provides command-line access to AIDLC Dashboard MCP tools.
"""

import argparse
import json
import sys
from typing import Any, Dict

from .tools import AIDLCDashboardMCPTools


def create_project(args):
    """Create a new project."""
    tools = AIDLCDashboardMCPTools(args.url)
    result = tools.create_project(args.name)
    
    if result.success:
        print(f"✅ Project created successfully!")
        print(f"Project ID: {result.data['project']['id']}")
        print(f"Project Name: {result.data['project']['name']}")
    else:
        print(f"❌ Failed to create project: {result.error}")
        sys.exit(1)


def upload_artifact(args):
    """Upload an artifact to a project."""
    tools = AIDLCDashboardMCPTools(args.url)
    
    try:
        content = json.loads(args.content)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON content: {e}")
        sys.exit(1)
    
    result = tools.upload_artifact(args.project_id, args.artifact_type, content)
    
    if result.success:
        print(f"✅ Artifact uploaded successfully!")
        print(f"Type: {args.artifact_type}")
        print(f"Project Progress: {result.data.get('project_progress', 'N/A')}%")
    else:
        print(f"❌ Failed to upload artifact: {result.error}")
        sys.exit(1)


def update_status(args):
    """Update artifact status."""
    tools = AIDLCDashboardMCPTools(args.url)
    result = tools.update_status(args.project_id, args.artifact_type, args.status)
    
    if result.success:
        print(f"✅ Status updated successfully!")
        print(f"Artifact: {args.artifact_type}")
        print(f"New Status: {args.status}")
        print(f"Project Progress: {result.data.get('project_progress', 'N/A')}%")
    else:
        print(f"❌ Failed to update status: {result.error}")
        sys.exit(1)


def get_project(args):
    """Get project details."""
    tools = AIDLCDashboardMCPTools(args.url)
    result = tools.get_project(args.project_id)
    
    if result.success:
        project = result.data['project']
        print(f"✅ Project Details:")
        print(f"ID: {project['id']}")
        print(f"Name: {project['name']}")
        print(f"Progress: {project['progress']}%")
        print(f"Created: {project['created_at']}")
        print(f"Artifacts: {len(project.get('artifacts', {}))}")
    else:
        print(f"❌ Failed to get project: {result.error}")
        sys.exit(1)


def list_projects(args):
    """List all projects."""
    tools = AIDLCDashboardMCPTools(args.url)
    result = tools.list_projects()
    
    if result.success:
        projects = result.data['projects']
        print(f"✅ Found {len(projects)} projects:")
        for project in projects:
            print(f"  - {project['id']}: {project['name']} ({project['progress']}%)")
    else:
        print(f"❌ Failed to list projects: {result.error}")
        sys.exit(1)


def health_check(args):
    """Check dashboard service health."""
    tools = AIDLCDashboardMCPTools(args.url)
    result = tools.health_check()
    
    if result.success:
        health = result.data
        print(f"✅ Dashboard service is healthy!")
        print(f"Status: {health.get('status', 'unknown')}")
        print(f"Version: {health.get('version', 'unknown')}")
        print(f"Uptime: {health.get('uptime', 'unknown')}")
    else:
        print(f"❌ Dashboard service is unhealthy: {result.error}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AIDLC MCP Tools Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--url', 
        default='http://localhost:8000/api',
        help='AIDLC Dashboard API URL (default: http://localhost:8000/api)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create project command
    create_parser = subparsers.add_parser('create-project', help='Create a new project')
    create_parser.add_argument('name', help='Project name')
    create_parser.set_defaults(func=create_project)
    
    # Upload artifact command
    upload_parser = subparsers.add_parser('upload-artifact', help='Upload an artifact')
    upload_parser.add_argument('project_id', help='Project ID')
    upload_parser.add_argument('artifact_type', 
                              choices=['epics', 'user_stories', 'domain_model', 'model_code_plan', 'ui_code_plan'],
                              help='Artifact type')
    upload_parser.add_argument('content', help='Artifact content (JSON string)')
    upload_parser.set_defaults(func=upload_artifact)
    
    # Update status command
    status_parser = subparsers.add_parser('update-status', help='Update artifact status')
    status_parser.add_argument('project_id', help='Project ID')
    status_parser.add_argument('artifact_type', 
                              choices=['epics', 'user_stories', 'domain_model', 'model_code_plan', 'ui_code_plan'],
                              help='Artifact type')
    status_parser.add_argument('status', 
                              choices=['not-started', 'in-progress', 'completed'],
                              help='New status')
    status_parser.set_defaults(func=update_status)
    
    # Get project command
    get_parser = subparsers.add_parser('get-project', help='Get project details')
    get_parser.add_argument('project_id', help='Project ID')
    get_parser.set_defaults(func=get_project)
    
    # List projects command
    list_parser = subparsers.add_parser('list-projects', help='List all projects')
    list_parser.set_defaults(func=list_projects)
    
    # Health check command
    health_parser = subparsers.add_parser('health-check', help='Check service health')
    health_parser.set_defaults(func=health_check)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
