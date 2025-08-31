"""Configuration management for AI-Mem."""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
from platformdirs import user_config_dir, user_data_dir


class Config:
    """AI-Mem configuration manager."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize configuration manager."""
        self.config_dir = Path(config_dir) if config_dir else Path(user_config_dir("ai-mem"))
        self.data_dir = Path(user_data_dir("ai-mem"))
        self.config_file = self.config_dir / "config.yaml"
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except (yaml.YAMLError, IOError):
                pass
        
        # Return default configuration
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'workspace': {
                'default_template': 'default',
                'auto_sync': True,
                'sync_interval': 300,  # 5 minutes
            },
            'shared': {
                'default_location': str(self._get_default_shared_location()),
                'symlink_support': True,
                'network_drive_support': True,
            },
            'claude_code': {
                'integration_enabled': True,
                'auto_detect_workspace': True,
                'memory_hierarchy': ['enterprise', 'project', 'user', 'local'],
            },
            'sync': {
                'conflict_resolution': 'prompt',  # prompt, local, shared, newest
                'backup_before_sync': True,
                'exclude_patterns': ['.git', '__pycache__', '*.pyc', '.DS_Store'],
            },
            'search': {
                'index_enabled': True,
                'index_content': True,
                'index_metadata': True,
            },
        }
    
    def _get_default_shared_location(self) -> Path:
        """Get platform-appropriate default shared location."""
        if os.name == 'nt':  # Windows
            # Try common Windows shared locations
            possible_paths = [
                Path.home() / "Documents" / "AI-Mem-Shared",
                Path("C:/AI-Mem-Shared"),
                Path.home() / "AI-Mem-Shared",
            ]
        else:  # Unix-like systems
            possible_paths = [
                Path.home() / "AI-Mem-Shared",
                Path("/shared/ai-mem"),
                Path("/mnt/shared/ai-mem"),
            ]
        
        # Return the first writable location
        for path in possible_paths:
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                if path.parent.is_dir() and os.access(path.parent, os.W_OK):
                    return path
            except (OSError, PermissionError):
                continue
        
        # Fallback to user documents
        return Path.home() / "Documents" / "AI-Mem-Shared"
    
    def get(self, key: str, default=None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self._save_config()
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, indent=2)
        except (yaml.YAMLError, IOError) as e:
            print(f"Warning: Could not save configuration: {e}")
    
    @property
    def workspace_dir(self) -> Path:
        """Get current workspace directory."""
        return Path.cwd()
    
    @property
    def claude_dir(self) -> Path:
        """Get .claude directory path."""
        return self.workspace_dir / ".claude"
    
    @property
    def thoughts_dir(self) -> Path:
        """Get thoughts directory path."""
        return self.workspace_dir / "thoughts"
    
    @property
    def shared_dir(self) -> Optional[Path]:
        """Get configured shared directory path."""
        shared_path = self.get('shared.default_location')
        if shared_path:
            path = Path(shared_path)
            # Resolve symlinks if needed
            if path.is_symlink() and self.get('shared.symlink_support', True):
                return path.resolve()
            return path
        return None