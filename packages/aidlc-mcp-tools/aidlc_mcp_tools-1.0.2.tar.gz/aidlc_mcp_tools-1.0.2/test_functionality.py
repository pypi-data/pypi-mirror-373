#!/usr/bin/env python3
"""
Simple test script to verify AIDLC MCP Tools functionality
"""

from aidlc_mcp_tools import AIDLCDashboardMCPTools

def test_basic_functionality():
    """Test basic functionality without requiring dashboard service"""
    
    print("🧪 Testing AIDLC MCP Tools...")
    
    # Test 1: Initialize tools
    try:
        tools = AIDLCDashboardMCPTools("http://localhost:8000/api")
        print("✅ Tools initialization: SUCCESS")
    except Exception as e:
        print(f"❌ Tools initialization: FAILED - {e}")
        return False
    
    # Test 2: Check available methods
    expected_methods = [
        'aidlc_health_check',
        'aidlc_create_project', 
        'aidlc_get_project_status',
        'aidlc_upload_epics',
        'aidlc_upload_user_stories',
        'aidlc_upload_domain_model',
        'aidlc_upload_model_code_plan',
        'aidlc_upload_ui_code_plan',
        'aidlc_update_artifact_status'
    ]
    
    missing_methods = []
    for method in expected_methods:
        if not hasattr(tools, method):
            missing_methods.append(method)
    
    if missing_methods:
        print(f"❌ Method availability: FAILED - Missing: {missing_methods}")
        return False
    else:
        print("✅ Method availability: SUCCESS")
    
    # Test 3: Test health check (will fail but should not crash)
    try:
        result = tools.aidlc_health_check()
        print(f"✅ Health check method: SUCCESS (returned {type(result).__name__})")
    except Exception as e:
        print(f"❌ Health check method: FAILED - {e}")
        return False
    
    # Test 4: Test project creation (will fail but should not crash)
    try:
        result = tools.aidlc_create_project("Test Project")
        print(f"✅ Create project method: SUCCESS (returned {type(result).__name__})")
    except Exception as e:
        print(f"❌ Create project method: FAILED - {e}")
        return False
    
    print("\n🎉 All basic functionality tests passed!")
    print("📝 Note: Network operations will fail without dashboard service running")
    return True

if __name__ == "__main__":
    test_basic_functionality()
