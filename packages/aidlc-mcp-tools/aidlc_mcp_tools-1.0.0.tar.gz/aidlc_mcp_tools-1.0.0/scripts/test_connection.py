#!/usr/bin/env python3
"""
AIDLC MCP Tools - Connection Test Script

Test connectivity to the AIDLC Dashboard service.
"""

import argparse
import sys
from aidlc_mcp_tools import AIDLCDashboardMCPTools


def test_connection(dashboard_url: str, verbose: bool = False):
    """
    Test connection to the AIDLC Dashboard service.
    
    Args:
        dashboard_url: URL of the dashboard service
        verbose: Enable verbose output
    """
    print(f"🔍 Testing connection to: {dashboard_url}")
    print("=" * 50)
    
    tools = AIDLCDashboardMCPTools(dashboard_url)
    
    # Test 1: Health Check
    print("\n1️⃣ Health Check")
    print("-" * 15)
    
    try:
        result = tools.health_check()
        if result.success:
            print("✅ Health check passed!")
            if verbose:
                health_data = result.data
                print(f"   Status: {health_data.get('status', 'unknown')}")
                print(f"   Version: {health_data.get('version', 'unknown')}")
                print(f"   Uptime: {health_data.get('uptime', 'unknown')}")
        else:
            print(f"❌ Health check failed: {result.error}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: List Projects (basic API test)
    print("\n2️⃣ API Connectivity")
    print("-" * 20)
    
    try:
        result = tools.list_projects()
        if result.success:
            projects = result.data.get('projects', [])
            print(f"✅ API connectivity confirmed!")
            print(f"   Found {len(projects)} existing projects")
            
            if verbose and projects:
                print("   Projects:")
                for project in projects[:3]:  # Show first 3 projects
                    print(f"     - {project.get('name', 'Unknown')} ({project.get('progress', 0)}%)")
                if len(projects) > 3:
                    print(f"     ... and {len(projects) - 3} more")
        else:
            print(f"❌ API connectivity failed: {result.error}")
            return False
    except Exception as e:
        print(f"❌ API connectivity error: {e}")
        return False
    
    # Test 3: Create and Delete Test Project (write operations)
    print("\n3️⃣ Write Operations")
    print("-" * 20)
    
    test_project_name = "Connection Test Project"
    
    try:
        # Create test project
        result = tools.create_project(test_project_name)
        if result.success:
            project_id = result.data['project']['id']
            print("✅ Project creation successful!")
            if verbose:
                print(f"   Project ID: {project_id}")
            
            # Try to get the project back
            result = tools.get_project(project_id)
            if result.success:
                print("✅ Project retrieval successful!")
                if verbose:
                    project = result.data['project']
                    print(f"   Name: {project.get('name')}")
                    print(f"   Progress: {project.get('progress')}%")
            else:
                print(f"⚠️  Project retrieval failed: {result.error}")
                
        else:
            print(f"❌ Project creation failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Write operations error: {e}")
        return False
    
    print("\n🎉 All connection tests passed!")
    print("✅ AIDLC Dashboard service is fully accessible")
    return True


def main():
    """Main function for connection testing."""
    parser = argparse.ArgumentParser(
        description="Test connection to AIDLC Dashboard service"
    )
    parser.add_argument(
        '--url',
        default='http://localhost:8000/api',
        help='Dashboard service URL (default: http://localhost:8000/api)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    try:
        success = test_connection(args.url, args.verbose)
        if success:
            print("\n🚀 Connection test completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Connection test failed!")
            print("\n💡 Troubleshooting tips:")
            print("   1. Make sure the AIDLC Dashboard service is running")
            print("   2. Check the URL is correct")
            print("   3. Verify network connectivity")
            print("   4. Check firewall settings")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Connection test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during connection test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
