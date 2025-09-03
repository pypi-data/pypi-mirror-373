# AIDLC MCP Tools API Documentation

## Overview

The AIDLC MCP Tools provide a set of Model Context Protocol (MCP) tools that enable AI agents to interact with the AIDLC Dashboard service. This document describes the available tools and their usage.

## MCP Tools

### 1. aidlc_create_project

Create a new project in the AIDLC Dashboard.

**Parameters:**
- `name` (string, required): The name of the project to create

**Returns:**
```json
{
  "success": true,
  "data": {
    "project": {
      "id": "project-123",
      "name": "Project Name",
      "created_at": "2024-08-14T08:43:39Z",
      "progress": 0.0,
      "artifacts": {
        "epics": "not-started",
        "user_stories": "not-started",
        "domain_model": "not-started",
        "model_code_plan": "not-started",
        "ui_code_plan": "not-started"
      }
    }
  }
}
```

**Example Usage:**
```json
{
  "name": "aidlc_create_project",
  "arguments": {
    "name": "E-commerce Platform"
  }
}
```

### 2. aidlc_upload_artifact

Upload an artifact to an existing project.

**Parameters:**
- `project_id` (string, required): The ID of the project
- `artifact_type` (string, required): Type of artifact. One of:
  - `epics`
  - `user_stories`
  - `domain_model`
  - `model_code_plan`
  - `ui_code_plan`
- `content` (object, required): The artifact content (structure depends on artifact type)

**Returns:**
```json
{
  "success": true,
  "data": {
    "artifact": {
      "type": "epics",
      "status": "not-started",
      "content": { ... },
      "uploaded_at": "2024-08-14T08:43:39Z"
    },
    "project_progress": 20.0
  }
}
```

**Example Usage:**
```json
{
  "name": "aidlc_upload_artifact",
  "arguments": {
    "project_id": "project-123",
    "artifact_type": "epics",
    "content": {
      "title": "User Management System",
      "description": "Complete user authentication and profile management",
      "priority": "high"
    }
  }
}
```

### 3. aidlc_update_status

Update the status of an artifact in a project.

**Parameters:**
- `project_id` (string, required): The ID of the project
- `artifact_type` (string, required): Type of artifact to update
- `status` (string, required): New status. One of:
  - `not-started`
  - `in-progress`
  - `completed`

**Returns:**
```json
{
  "success": true,
  "data": {
    "artifact_type": "epics",
    "old_status": "not-started",
    "new_status": "completed",
    "project_progress": 40.0
  }
}
```

**Example Usage:**
```json
{
  "name": "aidlc_update_status",
  "arguments": {
    "project_id": "project-123",
    "artifact_type": "epics",
    "status": "completed"
  }
}
```

### 4. aidlc_get_project

Retrieve details about a specific project.

**Parameters:**
- `project_id` (string, required): The ID of the project

**Returns:**
```json
{
  "success": true,
  "data": {
    "project": {
      "id": "project-123",
      "name": "E-commerce Platform",
      "created_at": "2024-08-14T08:00:00Z",
      "progress": 60.0,
      "artifacts": {
        "epics": {
          "status": "completed",
          "content": { ... }
        },
        "user_stories": {
          "status": "in-progress",
          "content": { ... }
        }
      }
    }
  }
}
```

**Example Usage:**
```json
{
  "name": "aidlc_get_project",
  "arguments": {
    "project_id": "project-123"
  }
}
```

### 5. aidlc_list_projects

List all projects in the dashboard.

**Parameters:** None

**Returns:**
```json
{
  "success": true,
  "data": {
    "projects": [
      {
        "id": "project-123",
        "name": "E-commerce Platform",
        "progress": 60.0,
        "created_at": "2024-08-14T08:00:00Z",
        "artifacts": { ... }
      }
    ],
    "total": 1
  }
}
```

**Example Usage:**
```json
{
  "name": "aidlc_list_projects",
  "arguments": {}
}
```

### 6. aidlc_health_check

Check if the AIDLC Dashboard service is healthy and accessible.

**Parameters:** None

**Returns:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "uptime": "2h 15m 30s"
  }
}
```

**Example Usage:**
```json
{
  "name": "aidlc_health_check",
  "arguments": {}
}
```

## Artifact Content Schemas

### Epics Content Schema

```json
{
  "title": "Epic Title",
  "description": "Detailed description of the epic",
  "user_stories": ["US-001", "US-002", "US-003"],
  "priority": "high|medium|low",
  "acceptance_criteria": [
    "Criteria 1",
    "Criteria 2"
  ]
}
```

### User Stories Content Schema

```json
{
  "stories": [
    {
      "id": "US-001",
      "title": "Story Title",
      "description": "As a [user], I want [goal] so that [benefit]",
      "acceptance_criteria": [
        "Given [context], when [action], then [outcome]"
      ],
      "priority": "high|medium|low",
      "story_points": 5
    }
  ],
  "total_count": 1,
  "epics": ["Epic-001"]
}
```

### Domain Model Content Schema

```json
{
  "entities": [
    {
      "name": "EntityName",
      "attributes": ["id", "name", "created_at"],
      "description": "Description of the entity"
    }
  ],
  "relationships": [
    {
      "from": "EntityA",
      "to": "EntityB",
      "type": "one-to-many|many-to-one|many-to-many",
      "description": "Description of the relationship"
    }
  ],
  "value_objects": [
    {
      "name": "ValueObjectName",
      "attributes": ["attribute1", "attribute2"]
    }
  ]
}
```

### Model Code Plan Content Schema

```json
{
  "components": [
    {
      "name": "ComponentName",
      "type": "service|repository|entity|controller",
      "dependencies": ["Dependency1", "Dependency2"],
      "methods": ["method1", "method2"]
    }
  ],
  "implementation_steps": [
    "Step 1: Create entities",
    "Step 2: Implement repositories",
    "Step 3: Add business logic"
  ],
  "architecture": {
    "pattern": "Domain-Driven Design|MVC|Layered",
    "layers": ["Domain", "Application", "Infrastructure"]
  }
}
```

### UI Code Plan Content Schema

```json
{
  "pages": [
    {
      "name": "PageName",
      "route": "/path",
      "components": ["Component1", "Component2"]
    }
  ],
  "components": [
    {
      "name": "ComponentName",
      "props": ["prop1", "prop2"],
      "state": ["state1", "state2"]
    }
  ],
  "navigation": {
    "type": "SPA|MPA",
    "router": "React Router|Vue Router|Angular Router"
  },
  "styling": {
    "framework": "Bootstrap|Tailwind|Material-UI",
    "theme": "Light|Dark|Custom"
  }
}
```

## Error Handling

All MCP tools return a consistent response format:

**Success Response:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error description",
  "details": "Additional error details (optional)"
}
```

### Common Error Types

1. **Connection Error**: Dashboard service is not accessible
2. **Validation Error**: Invalid input parameters
3. **Not Found Error**: Project or resource not found
4. **Server Error**: Internal server error in dashboard service

## Python Library API

### AIDLCDashboardMCPTools Class

```python
from aidlc_mcp_tools import AIDLCDashboardMCPTools

# Initialize
tools = AIDLCDashboardMCPTools(
    base_url="http://localhost:8000/api",
    timeout=30,
    retry_attempts=3
)

# Create project
result = tools.create_project("Project Name")

# Upload artifact
result = tools.upload_artifact(project_id, "epics", content)

# Update status
result = tools.update_status(project_id, "epics", "completed")

# Get project
result = tools.get_project(project_id)

# List projects
result = tools.list_projects()

# Health check
result = tools.health_check()
```

### MCPToolResult Class

```python
@dataclass
class MCPToolResult:
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
```

## Configuration

### Environment Variables

- `AIDLC_DASHBOARD_URL`: Dashboard service URL (default: http://localhost:8000/api)
- `AIDLC_TIMEOUT`: Request timeout in seconds (default: 30)
- `AIDLC_RETRY_ATTEMPTS`: Number of retry attempts (default: 3)
- `AIDLC_LOG_LEVEL`: Logging level (default: INFO)

### Configuration File

Create `~/.aidlc/mcp-config.json`:

```json
{
  "dashboard_url": "http://localhost:8000/api",
  "timeout": 30,
  "retry_attempts": 3,
  "log_level": "INFO"
}
```

## Integration Examples

### Amazon Q Integration

When using with Amazon Q, the tools are automatically available. Users can make natural language requests:

- "Create a project for an e-commerce platform"
- "Upload the epics for user authentication features"
- "Mark the user stories as completed"
- "Show me the current project status"

### Direct MCP Server Usage

```bash
# Start MCP server
aidlc-mcp-server

# The server will respond to MCP protocol messages
```

### Command Line Usage

```bash
# Create project
python -m aidlc_mcp_tools.cli create-project "My Project"

# Upload artifact
python -m aidlc_mcp_tools.cli upload-artifact PROJECT_ID epics '{"title": "Epic"}'

# Update status
python -m aidlc_mcp_tools.cli update-status PROJECT_ID epics completed

# Health check
python -m aidlc_mcp_tools.cli health-check
```
