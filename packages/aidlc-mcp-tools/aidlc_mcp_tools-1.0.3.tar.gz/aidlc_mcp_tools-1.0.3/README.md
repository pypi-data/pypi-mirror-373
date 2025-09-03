# AIDLC MCP Tools

A Model Context Protocol (MCP) server implementation that provides AI agents with tools to interact with the AIDLC Dashboard service. This enables seamless integration between AI tools and project management workflows.

## 🚀 Features

- **Project Management**: Create and manage projects through MCP
- **Artifact Upload**: Upload AI-generated artifacts (epics, user stories, domain models, etc.)
- **Progress Tracking**: Update project status and track completion
- **Health Monitoring**: Check service availability and performance
- **Batch Operations**: Handle multiple artifacts efficiently
- **Amazon Q Integration**: Optimized for Amazon Q Developer workflows

## 📋 Requirements

- Python 3.11+
- requests library
- AIDLC Dashboard service running (for integration)

## 🛠️ Installation

### Option 1: Using uv (Recommended)
```bash
# Install with uv
uv pip install -e .

# Or install from PyPI (when published)
uv pip install mcp-tools
```

### Option 2: Using pip
```bash
# Install in development mode
pip install -e .

# Or install dependencies manually
pip install -r requirements.txt
```

### Option 3: Quick Setup Script
```bash
./setup.sh
```

## 🌐 Usage

### As MCP Server (Amazon Q Integration)

1. **Configure Amazon Q MCP settings:**
```json
{
  "mcpServers": {
    "aidlc-dashboard": {
      "command": "uvx",
      "args": ["--from", "aidlc-mcp-tools@latest", "aidlc-mcp-server"],
      "env": {
        "AIDLC_DASHBOARD_URL": "http://44.253.191.105:8000/api"
      }
    }
  }
}
```

2. **Start the MCP server:**
```bash
aidlc-mcp-server
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AIDLC_DASHBOARD_URL` | Dashboard API base URL | `http://localhost:8000/api` |
| `AIDLC_TIMEOUT` | Request timeout (seconds) | `30` |
| `AIDLC_RETRY_ATTEMPTS` | Number of retry attempts | `3` |
| `AIDLC_LOG_LEVEL` | Logging level | `INFO` |

## 📖 Available MCP Tools

### 1. aidlc_create_project
Create a new project in the AIDLC Dashboard.

**Parameters:**
- `name` (string): Project name

**Example:**
```json
{
  "name": "create_project",
  "arguments": {
    "name": "E-commerce Platform"
  }
}
```

### 2. aidlc_upload_artifact
Upload an artifact to a project.

**Parameters:**
- `project_id` (string): Project identifier
- `artifact_type` (string): Type of artifact (epics, user_stories, domain_model, model_code_plan, ui_code_plan)
- `content` (object): Artifact content

**Example:**
```json
{
  "name": "upload_artifact",
  "arguments": {
    "project_id": "project-123",
    "artifact_type": "epics",
    "content": {
      "title": "User Management",
      "description": "Complete user management system",
      "priority": "high"
    }
  }
}
```

### 3. aidlc_update_status
Update the status of an artifact.

**Parameters:**
- `project_id` (string): Project identifier
- `artifact_type` (string): Type of artifact
- `status` (string): New status (not-started, in-progress, completed)

### 4. aidlc_get_project
Get project details and current status.

**Parameters:**
- `project_id` (string): Project identifier

### 5. aidlc_list_projects
List all projects in the dashboard.

**Parameters:** None

### 6. aidlc_health_check
Check if the dashboard service is healthy and accessible.

**Parameters:** None

## 🎯 Artifact Types and Schemas

### Epics
```json
{
  "title": "Epic Title",
  "description": "Epic description",
  "user_stories": ["US-001", "US-002"],
  "priority": "high|medium|low",
  "acceptance_criteria": ["Criteria 1", "Criteria 2"]
}
```

### User Stories
```json
{
  "stories": [
    {
      "id": "US-001",
      "title": "Story Title",
      "description": "As a user, I want...",
      "acceptance_criteria": ["Criteria 1"],
      "priority": "high",
      "story_points": 5
    }
  ],
  "total_count": 1,
  "epics": ["Epic-001"]
}
```

### Domain Model
```json
{
  "entities": [
    {
      "name": "User",
      "attributes": ["id", "username", "email"],
      "description": "System user entity"
    }
  ],
  "relationships": [
    {
      "from": "User",
      "to": "Order",
      "type": "one-to-many"
    }
  ]
}
```

### Model Code Plan
```json
{
  "components": [
    {
      "name": "UserService",
      "type": "service",
      "dependencies": ["UserRepository"]
    }
  ],
  "implementation_steps": [
    "Create entities",
    "Implement repositories"
  ]
}
```

### UI Code Plan
```json
{
  "pages": [
    {
      "name": "LoginPage",
      "route": "/login",
      "components": ["LoginForm", "Header"]
    }
  ],
  "navigation": {
    "type": "SPA",
    "router": "React Router"
  }
}
```

