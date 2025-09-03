"""
AIDLC MCP Tools Configuration Management

Handles configuration loading from environment variables and config files.
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class MCPConfig:
    """Configuration for AIDLC MCP Tools."""
    dashboard_url: str = "http://localhost:8000/api"
    timeout: int = 30
    retry_attempts: int = 3
    log_level: str = "INFO"


def load_config(config_file: Optional[str] = None) -> MCPConfig:
    """
    Load configuration from environment variables and optional config file.
    
    Args:
        config_file: Path to JSON configuration file
        
    Returns:
        MCPConfig instance with loaded configuration
    """
    config = MCPConfig()
    
    # Load from config file if provided
    if config_file and Path(config_file).exists():
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                
            config.dashboard_url = file_config.get('dashboard_url', config.dashboard_url)
            config.timeout = file_config.get('timeout', config.timeout)
            config.retry_attempts = file_config.get('retry_attempts', config.retry_attempts)
            config.log_level = file_config.get('log_level', config.log_level)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load config file {config_file}: {e}")
    
    # Override with environment variables
    config.dashboard_url = os.environ.get('AIDLC_DASHBOARD_URL', config.dashboard_url)
    config.timeout = int(os.environ.get('AIDLC_TIMEOUT', str(config.timeout)))
    config.retry_attempts = int(os.environ.get('AIDLC_RETRY_ATTEMPTS', str(config.retry_attempts)))
    config.log_level = os.environ.get('AIDLC_LOG_LEVEL', config.log_level)
    
    return config


def save_config(config: MCPConfig, config_file: str) -> None:
    """
    Save configuration to a JSON file.
    
    Args:
        config: MCPConfig instance to save
        config_file: Path to save the configuration file
    """
    config_data = {
        'dashboard_url': config.dashboard_url,
        'timeout': config.timeout,
        'retry_attempts': config.retry_attempts,
        'log_level': config.log_level
    }
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        print(f"Configuration saved to {config_file}")
    except IOError as e:
        print(f"Failed to save config file {config_file}: {e}")


def get_default_config_path() -> str:
    """Get the default configuration file path."""
    home_dir = Path.home()
    config_dir = home_dir / '.aidlc'
    config_dir.mkdir(exist_ok=True)
    return str(config_dir / 'mcp-config.json')


def create_sample_config(config_file: Optional[str] = None) -> None:
    """
    Create a sample configuration file.
    
    Args:
        config_file: Path to create the config file, defaults to default path
    """
    if config_file is None:
        config_file = get_default_config_path()
    
    sample_config = MCPConfig()
    save_config(sample_config, config_file)
    print(f"Sample configuration created at {config_file}")
    print("You can edit this file to customize your settings.")
