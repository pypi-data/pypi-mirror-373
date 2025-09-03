#!/bin/bash

# AIDLC MCP Tools Setup Script

set -e

echo "🚀 AIDLC MCP Tools Setup"
echo "========================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python version: $python_version"

# Check if uv is available
if command -v uv &> /dev/null; then
    echo "📦 Using uv for package management..."
    
    # Install with uv
    echo "🔧 Installing AIDLC MCP Tools with uv..."
    uv pip install -e .
    
    echo "✅ Installation completed with uv!"
else
    echo "📦 Using pip for package management..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "🔧 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    echo "📥 Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    
    # Install in development mode
    echo "🔧 Installing AIDLC MCP Tools..."
    pip install -e .
    
    echo "✅ Installation completed with pip!"
fi

# Create sample configuration
echo "⚙️  Creating sample configuration..."
python3 -c "
from aidlc_mcp_tools.config import create_sample_config
create_sample_config()
"

# Test installation
echo "🧪 Testing installation..."
if python3 -c "import aidlc_mcp_tools; print('✅ Import successful')" 2>/dev/null; then
    echo "✅ AIDLC MCP Tools installed successfully!"
else
    echo "❌ Installation test failed"
    exit 1
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "📖 Usage Examples:"
echo "  # As MCP Server (for Amazon Q):"
echo "  aidlc-mcp-server"
echo ""
echo "  # Command Line Interface:"
echo "  python -m aidlc_mcp_tools.cli health-check"
echo "  python -m aidlc_mcp_tools.cli create-project 'My Project'"
echo ""
echo "  # Python Library:"
echo "  python3 -c \"from aidlc_mcp_tools import AIDLCDashboardMCPTools; print('Ready!')\""
echo ""
echo "📁 Configuration file created at: ~/.aidlc/mcp-config.json"
echo ""
echo "🔗 Make sure the AIDLC Dashboard service is running:"
echo "  cd ../dashboard-service && python run.py"
echo ""
echo "📚 For more information, see README.md"
