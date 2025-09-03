#!/usr/bin/env python3
"""
AIDLC MCP Tools - Amazon Q Integration Workflow Examples

This script demonstrates how AIDLC MCP Tools integrate with Amazon Q workflows.
"""

from aidlc_mcp_tools import AIDLCDashboardMCPTools


def simulate_amazon_q_workflow():
    """Simulate a typical Amazon Q + AIDLC workflow."""
    print("🤖 Amazon Q + AIDLC Integration Workflow")
    print("=" * 50)
    
    tools = AIDLCDashboardMCPTools("http://localhost:8000/api")
    
    # Step 1: Amazon Q creates a project based on user request
    print("\n📝 Step 1: User asks Amazon Q to create a project")
    print("User: 'Create a project for a task management application'")
    print("Amazon Q: Using MCP tools to create project...")
    
    result = tools.create_project("Task Management Application")
    if not result.success:
        print(f"❌ Failed to create project: {result.error}")
        return
    
    project_id = result.data['project']['id']
    print(f"✅ Project created: {project_id}")
    
    # Step 2: Amazon Q generates and uploads epics
    print("\n📝 Step 2: Amazon Q generates epics based on requirements")
    print("Amazon Q: Analyzing requirements and generating epics...")
    
    epics_content = {
        "title": "Task Management Core Features",
        "description": "Core functionality for creating, managing, and tracking tasks",
        "user_stories": ["US-001", "US-002", "US-003", "US-004"],
        "priority": "high",
        "acceptance_criteria": [
            "Users can create tasks with title and description",
            "Users can mark tasks as complete",
            "Users can organize tasks into categories",
            "Users can set due dates for tasks"
        ]
    }
    
    result = tools.upload_artifact(project_id, "epics", epics_content)
    if result.success:
        print("✅ Epics uploaded successfully!")
        print(f"   Progress: {result.data.get('project_progress')}%")
    
    # Step 3: Amazon Q generates detailed user stories
    print("\n📝 Step 3: Amazon Q breaks down epics into user stories")
    print("Amazon Q: Creating detailed user stories...")
    
    user_stories_content = {
        "stories": [
            {
                "id": "US-001",
                "title": "Create New Task",
                "description": "As a user, I want to create a new task so that I can track my work",
                "acceptance_criteria": [
                    "Task creation form with title and description fields",
                    "Optional due date selection",
                    "Category assignment dropdown",
                    "Save and cancel buttons"
                ],
                "priority": "high",
                "story_points": 5
            },
            {
                "id": "US-002",
                "title": "Mark Task as Complete",
                "description": "As a user, I want to mark tasks as complete so that I can track my progress",
                "acceptance_criteria": [
                    "Checkbox or button to mark completion",
                    "Visual indication of completed tasks",
                    "Completed tasks move to separate section"
                ],
                "priority": "high",
                "story_points": 3
            },
            {
                "id": "US-003",
                "title": "Organize Tasks by Category",
                "description": "As a user, I want to organize tasks by category so that I can group related work",
                "acceptance_criteria": [
                    "Category creation and management",
                    "Assign tasks to categories",
                    "Filter tasks by category"
                ],
                "priority": "medium",
                "story_points": 8
            }
        ],
        "total_count": 3,
        "epics": ["Epic-001"]
    }
    
    result = tools.upload_artifact(project_id, "user_stories", user_stories_content)
    if result.success:
        print("✅ User stories uploaded successfully!")
        print(f"   Progress: {result.data.get('project_progress')}%")
    
    # Step 4: Amazon Q creates domain model
    print("\n📝 Step 4: Amazon Q designs the domain model")
    print("Amazon Q: Analyzing domain and creating entity model...")
    
    domain_model_content = {
        "entities": [
            {
                "name": "Task",
                "attributes": [
                    "id", "title", "description", "completed", 
                    "created_at", "due_date", "category_id"
                ],
                "description": "Main task entity representing a single task"
            },
            {
                "name": "Category",
                "attributes": ["id", "name", "color", "created_at"],
                "description": "Category for organizing tasks"
            },
            {
                "name": "User",
                "attributes": ["id", "username", "email", "created_at"],
                "description": "User who owns and manages tasks"
            }
        ],
        "relationships": [
            {
                "from": "User",
                "to": "Task",
                "type": "one-to-many",
                "description": "User can have multiple tasks"
            },
            {
                "from": "Category",
                "to": "Task", 
                "type": "one-to-many",
                "description": "Category can contain multiple tasks"
            }
        ],
        "value_objects": [
            {
                "name": "TaskStatus",
                "attributes": ["pending", "completed", "archived"]
            }
        ]
    }
    
    result = tools.upload_artifact(project_id, "domain_model", domain_model_content)
    if result.success:
        print("✅ Domain model uploaded successfully!")
        print(f"   Progress: {result.data.get('project_progress')}%")
    
    # Step 5: Amazon Q updates progress as work is completed
    print("\n📝 Step 5: Amazon Q updates progress as development proceeds")
    print("Amazon Q: Marking epics as completed...")
    
    result = tools.update_status(project_id, "epics", "completed")
    if result.success:
        print("✅ Epics marked as completed!")
        print(f"   Progress: {result.data.get('project_progress')}%")
    
    result = tools.update_status(project_id, "user_stories", "in-progress")
    if result.success:
        print("✅ User stories marked as in-progress!")
        print(f"   Progress: {result.data.get('project_progress')}%")
    
    # Step 6: Final project status
    print("\n📝 Step 6: Amazon Q provides project summary")
    print("Amazon Q: Retrieving final project status...")
    
    result = tools.get_project(project_id)
    if result.success:
        project = result.data['project']
        print("✅ Project Summary:")
        print(f"   Name: {project['name']}")
        print(f"   Overall Progress: {project['progress']}%")
        print("   Artifact Status:")
        
        artifacts = project.get('artifacts', {})
        for artifact_type, artifact_data in artifacts.items():
            if isinstance(artifact_data, dict) and 'status' in artifact_data:
                status = artifact_data['status']
                status_emoji = {"completed": "✅", "in-progress": "🔄", "not-started": "⏳"}
                print(f"     {status_emoji.get(status, '❓')} {artifact_type}: {status}")
    
    print("\n🎉 Amazon Q workflow simulation completed!")
    print("=" * 50)


def demonstrate_mcp_tool_calls():
    """Demonstrate individual MCP tool calls as they would appear in Amazon Q."""
    print("\n🔧 Individual MCP Tool Call Examples")
    print("=" * 40)
    
    print("\n1. Tool: aidlc_create_project")
    print("   Input: {'name': 'Mobile App Project'}")
    print("   Amazon Q would call this when user says:")
    print("   'Create a new project for a mobile app'")
    
    print("\n2. Tool: aidlc_upload_artifact")
    print("   Input: {")
    print("     'project_id': 'project-123',")
    print("     'artifact_type': 'epics',")
    print("     'content': {'title': 'User Authentication', ...}")
    print("   }")
    print("   Amazon Q would call this when generating artifacts")
    
    print("\n3. Tool: aidlc_update_status")
    print("   Input: {")
    print("     'project_id': 'project-123',")
    print("     'artifact_type': 'epics',")
    print("     'status': 'completed'")
    print("   }")
    print("   Amazon Q would call this when marking work as done")
    
    print("\n4. Tool: aidlc_get_project")
    print("   Input: {'project_id': 'project-123'}")
    print("   Amazon Q would call this to check current status")
    
    print("\n5. Tool: aidlc_health_check")
    print("   Input: {}")
    print("   Amazon Q would call this to verify service availability")


def main():
    """Run the Amazon Q workflow examples."""
    try:
        simulate_amazon_q_workflow()
        demonstrate_mcp_tool_calls()
    except KeyboardInterrupt:
        print("\n👋 Workflow simulation cancelled by user")
    except Exception as e:
        print(f"\n❌ Workflow simulation failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
