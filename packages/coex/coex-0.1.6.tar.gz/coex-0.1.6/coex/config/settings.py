"""
Configuration settings for the coex library.
"""

import os
from typing import Dict, Any

# Default configuration
DEFAULT_CONFIG = {
    # Docker settings
    "docker": {
        "timeout": 300,  # 5 minutes
        "memory_limit": "512m",
        "cpu_limit": "1.0",
        "network_disabled": False,  # Allow network for package installation
        "remove_containers": False,  # Keep container running until rm_docker()
        "auto_remove": False,
        "image": "python:3.11-slim",  # Single multi-language image with tools
    },
    
    # Execution settings
    "execution": {
        "timeout": 30,  # 30 seconds per execution
        "max_output_size": 1024 * 1024,  # 1MB
        "temp_dir": "/tmp/coex",
        "cleanup_temp_files": True,
    },
    
    # Security settings
    "security": {
        "enable_security_checks": True,
        "blocked_commands": [
            "rm", "rmdir", "del", "delete",
            "mkdir", "touch", "mv", "cp",
            "chmod", "chown", "sudo", "su",
            "wget", "curl", "nc", "netcat",
            "ssh", "scp", "rsync", "dd",
            "format", "fdisk", "mount", "umount",
        ],
        "blocked_patterns": [
            r"rm\s+-rf",
            r"rm\s+-fr", 
            r">\s*/dev/",
            r"cat\s+/etc/",
            r"eval\s*\(",
            r"exec\s*\(",
            r"system\s*\(",
            r"subprocess\.",
            r"os\.system",
            r"os\.popen",
            r"__import__",
        ],
    },
    
    # Language-specific settings
    "languages": {
        "python": {
            "extension": ".py",
            "command": ["python3"],
            "timeout": 30,
        },
        "javascript": {
            "extension": ".js",
            "command": ["node"],
            "timeout": 30,
        },
        "java": {
            "extension": ".java",
            "command": ["bash", "-c", "javac {file} && java {class}"],
            "timeout": 60,
        },
        "cpp": {
            "extension": ".cpp",
            "command": ["bash", "-c", "g++ -o {output} {file} && ./{output}"],
            "timeout": 60,
        },
        "c": {
            "extension": ".c",
            "command": ["bash", "-c", "gcc -o {output} {file} && ./{output}"],
            "timeout": 60,
        },
        "go": {
            "extension": ".go",
            "command": ["go", "run"],
            "timeout": 45,
        },
        "rust": {
            "extension": ".rs",
            "command": ["bash", "-c", "rustc -o {output} {file} && ./{output}"],
            "timeout": 90,
        },
    }
}


class Settings:
    """Configuration settings manager."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize settings with optional custom configuration."""
        self._config = DEFAULT_CONFIG.copy()
        if config:
            self._update_config(self._config, config)
    
    def _update_config(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """Recursively update configuration dictionary."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._update_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot-separated key."""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    @property
    def docker(self) -> Dict[str, Any]:
        """Get Docker configuration."""
        return self._config["docker"]
    
    @property
    def execution(self) -> Dict[str, Any]:
        """Get execution configuration."""
        return self._config["execution"]
    
    @property
    def security(self) -> Dict[str, Any]:
        """Get security configuration."""
        return self._config["security"]
    
    @property
    def languages(self) -> Dict[str, Any]:
        """Get language configuration."""
        return self._config["languages"]


# Global settings instance
settings = Settings()


def load_config_from_env() -> None:
    """Load configuration from environment variables."""
    # Docker settings
    if os.getenv("COEX_DOCKER_TIMEOUT"):
        settings.set("docker.timeout", int(os.getenv("COEX_DOCKER_TIMEOUT")))
    
    if os.getenv("COEX_DOCKER_MEMORY_LIMIT"):
        settings.set("docker.memory_limit", os.getenv("COEX_DOCKER_MEMORY_LIMIT"))
    
    # Execution settings
    if os.getenv("COEX_EXECUTION_TIMEOUT"):
        settings.set("execution.timeout", int(os.getenv("COEX_EXECUTION_TIMEOUT")))
    
    if os.getenv("COEX_TEMP_DIR"):
        settings.set("execution.temp_dir", os.getenv("COEX_TEMP_DIR"))
    
    # Security settings
    if os.getenv("COEX_DISABLE_SECURITY"):
        settings.set("security.enable_security_checks", False)


# Load environment configuration on import
load_config_from_env()
