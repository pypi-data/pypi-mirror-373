#!/usr/bin/env python3
"""
AIDLC MCP Tools - Basic Usage Examples

This script demonstrates basic usage of the AIDLC MCP Tools library.
"""

import json
from aidlc_mcp_tools import AIDLCDashboardMCPTools


def main():
    """Demonstrate basic MCP tools usage."""
    print("🚀 AIDLC MCP Tools - Basic Usage Examples")
    print("=" * 50)
    
    # Initialize tools
    dashboard_url = "http://localhost:8000/api"
    tools = AIDLCDashboardMCPTools(dashboard_url)
    
    print(f"📡 Connecting to dashboard at: {dashboard_url}")
    
    # 1. Health Check
    print("\n1️⃣ Health Check")
    print("-" * 20)
    result = tools.health_check()
    if result.success:
        print("✅ Dashboard service is healthy!")
        print(f"   Status: {result.data.get('status')}")
        print(f"   Version: {result.data.get('version')}")
    else:
        print(f"❌ Health check failed: {result.error}")
        return
    
    # 2. Create a Project
    print("\n2️⃣ Create Project")
    print("-" * 20)
    project_name = "Example E-commerce Platform"
    result = tools.create_project(project_name)
    
    if result.success:
        project_id = result.data['project']['id']
        print(f"✅ Project created successfully!")
        print(f"   Project ID: {project_id}")
        print(f"   Project Name: {result.data['project']['name']}")
    else:
        print(f"❌ Failed to create project: {result.error}")
        return
    
    # 3. Upload Epics Artifact
    print("\n3️⃣ Upload Epics Artifact")
    print("-" * 30)
    epics_content = {
        "title": "User Management System",
        "description": "Complete user authentication and profile management",
        "user_stories": ["US-001", "US-002", "US-003"],
        "priority": "high",
        "acceptance_criteria": [
            "Users can register with email",
            "Users can login securely",
            "Users can update their profiles"
        ]
    }
    
    result = tools.upload_artifact(project_id, "epics", epics_content)
    if result.success:
        print("✅ Epics artifact uploaded successfully!")
        print(f"   Project Progress: {result.data.get('project_progress', 'N/A')}%")
    else:
        print(f"❌ Failed to upload epics: {result.error}")
    
    # 4. Upload User Stories Artifact
    print("\n4️⃣ Upload User Stories Artifact")
    print("-" * 35)
    user_stories_content = {
        "stories": [
            {
                "id": "US-001",
                "title": "User Registration",
                "description": "As a new user, I want to register an account so that I can access the platform",
                "acceptance_criteria": [
                    "Registration form with email and password",
                    "Email verification required",
                    "Password strength validation"
                ],
                "priority": "high",
                "story_points": 5
            },
            {
                "id": "US-002", 
                "title": "User Login",
                "description": "As a registered user, I want to login so that I can access my account",
                "acceptance_criteria": [
                    "Login form with email/password",
                    "Remember me option",
                    "Forgot password link"
                ],
                "priority": "high",
                "story_points": 3
            }
        ],
        "total_count": 2,
        "epics": ["Epic-001"]
    }
    
    result = tools.upload_artifact(project_id, "user_stories", user_stories_content)
    if result.success:
        print("✅ User stories artifact uploaded successfully!")
        print(f"   Project Progress: {result.data.get('project_progress', 'N/A')}%")
    else:
        print(f"❌ Failed to upload user stories: {result.error}")
    
    # 5. Update Status
    print("\n5️⃣ Update Artifact Status")
    print("-" * 30)
    result = tools.update_status(project_id, "epics", "completed")
    if result.success:
        print("✅ Epics status updated to completed!")
        print(f"   Project Progress: {result.data.get('project_progress', 'N/A')}%")
    else:
        print(f"❌ Failed to update status: {result.error}")
    
    # 6. Get Project Details
    print("\n6️⃣ Get Project Details")
    print("-" * 25)
    result = tools.get_project(project_id)
    if result.success:
        project = result.data['project']
        print("✅ Project details retrieved!")
        print(f"   Name: {project['name']}")
        print(f"   Progress: {project['progress']}%")
        print(f"   Artifacts: {len(project.get('artifacts', {}))}")
        
        # Show artifact statuses
        artifacts = project.get('artifacts', {})
        for artifact_type, artifact_data in artifacts.items():
            if isinstance(artifact_data, dict) and 'status' in artifact_data:
                print(f"   - {artifact_type}: {artifact_data['status']}")
    else:
        print(f"❌ Failed to get project details: {result.error}")
    
    # 7. List All Projects
    print("\n7️⃣ List All Projects")
    print("-" * 22)
    result = tools.list_projects()
    if result.success:
        projects = result.data['projects']
        print(f"✅ Found {len(projects)} projects:")
        for project in projects:
            print(f"   - {project['id']}: {project['name']} ({project['progress']}%)")
    else:
        print(f"❌ Failed to list projects: {result.error}")
    
    print("\n🎉 Basic usage examples completed!")
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Examples cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
