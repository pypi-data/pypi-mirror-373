"""
Lazy language package installer for Docker containers.
"""

import logging
from typing import Set, List, Dict, Optional
from threading import Lock

from ..exceptions import ExecutionError
from .docker_manager import get_docker_manager

logger = logging.getLogger(__name__)


class LazyLanguageInstaller:
    """Manages lazy installation of language packages in Docker containers."""
    
    def __init__(self):
        """Initialize the lazy installer."""
        self._installed_languages: Set[str] = set()
        self._installation_lock = Lock()
        self._docker_manager = get_docker_manager()
        
        # Language installation configurations
        self._language_configs = {
            "python": {
                "packages": [],  # Python is pre-installed in base image
                "test_command": ["python3", "--version"],
                "description": "Python 3"
            },
            "java": {
                "packages": ["default-jdk"],
                "test_command": ["javac", "-version"],
                "description": "Java Development Kit"
            },
            "javascript": {
                "packages": ["nodejs", "npm"],
                "test_command": ["node", "--version"],
                "description": "Node.js"
            },
            "cpp": {
                "packages": ["build-essential", "g++"],
                "test_command": ["g++", "--version"],
                "description": "C++ compiler"
            },
            "c": {
                "packages": ["build-essential", "gcc"],
                "test_command": ["gcc", "--version"],
                "description": "C compiler"
            },
            "go": {
                "packages": ["golang-go"],
                "test_command": ["go", "version"],
                "description": "Go programming language"
            },
            "rust": {
                "packages": [],  # Rust requires special installation
                "test_command": ["rustc", "--version"],
                "description": "Rust programming language",
                "custom_install": True
            }
        }
    
    def ensure_language_available(self, language: str) -> None:
        """
        Ensure the specified language is available in the container.
        Install if not already installed.
        
        Args:
            language: Programming language to ensure availability
        """
        language = language.lower()
        
        if language in self._installed_languages:
            logger.debug(f"Language {language} already installed")
            return
        
        with self._installation_lock:
            # Double-check after acquiring lock
            if language in self._installed_languages:
                return
            
            if language not in self._language_configs:
                raise ExecutionError(f"Unsupported language: {language}")
            
            self._install_language(language)
            self._installed_languages.add(language)
    
    def pre_install_languages(self, languages: List[str]) -> None:
        """
        Pre-install multiple languages.
        
        Args:
            languages: List of languages to pre-install
        """
        print(f"[INFO] Pre-installing languages: {', '.join(languages)}")
        
        for language in languages:
            try:
                self.ensure_language_available(language)
                print(f"[SUCCESS] {language} ready")
            except Exception as e:
                print(f"[ERROR] Failed to install {language}: {e}")
                logger.error(f"Failed to pre-install {language}: {e}")
    
    def _install_language(self, language: str) -> None:
        """Install a specific language in the container."""
        config = self._language_configs[language]
        
        print(f"[INFO] Installing {config['description']} for first-time use...")
        
        try:
            # Get container
            container = self._docker_manager.get_or_create_container()
            
            # Check if already installed
            if self._test_language_availability(container, language):
                print(f"[INFO] {config['description']} already available")
                return
            
            # Install packages
            if config["packages"]:
                self._install_packages(container, config["packages"])
            
            # Handle custom installations
            if config.get("custom_install"):
                self._custom_install(container, language)
            
            # Verify installation
            if self._test_language_availability(container, language):
                print(f"[SUCCESS] {config['description']} installed successfully")
            else:
                raise ExecutionError(f"Installation verification failed for {language}")
                
        except Exception as e:
            error_msg = f"Failed to install {config['description']}: {e}"
            print(f"[ERROR] {error_msg}")
            raise ExecutionError(error_msg)
    
    def _install_packages(self, container, packages: List[str]) -> None:
        """Install packages using apt-get."""
        # Update package list first
        update_cmd = "apt-get update -qq"
        exit_code, stdout, stderr = self._docker_manager.execute_in_container(
            container, ["bash", "-c", update_cmd]
        )
        if exit_code != 0:
            logger.warning(f"Package update failed: {stderr}")
        
        # Install packages
        packages_str = " ".join(packages)
        install_cmd = f"DEBIAN_FRONTEND=noninteractive apt-get install -y -qq {packages_str}"
        exit_code, stdout, stderr = self._docker_manager.execute_in_container(
            container, ["bash", "-c", install_cmd]
        )
        
        if exit_code != 0:
            raise ExecutionError(f"Package installation failed: {stderr}")
    
    def _custom_install(self, container, language: str) -> None:
        """Handle custom installation procedures."""
        if language == "rust":
            # Install Rust using rustup
            rust_install_cmd = (
                "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | "
                "sh -s -- -y --default-toolchain stable"
            )
            exit_code, stdout, stderr = self._docker_manager.execute_in_container(
                container, ["bash", "-c", rust_install_cmd]
            )
            if exit_code != 0:
                raise ExecutionError(f"Rust installation failed: {stderr}")
            
            # Add Rust to PATH
            path_cmd = "echo 'source ~/.cargo/env' >> ~/.bashrc"
            self._docker_manager.execute_in_container(
                container, ["bash", "-c", path_cmd]
            )
    
    def _test_language_availability(self, container, language: str) -> bool:
        """Test if a language is available in the container."""
        config = self._language_configs[language]
        test_command = config["test_command"]
        
        try:
            exit_code, stdout, stderr = self._docker_manager.execute_in_container(
                container, test_command
            )
            return exit_code == 0
        except Exception:
            return False
    
    def get_installed_languages(self) -> Set[str]:
        """Get the set of currently installed languages."""
        return self._installed_languages.copy()
    
    def is_language_installed(self, language: str) -> bool:
        """Check if a language is already installed."""
        return language.lower() in self._installed_languages


# Global lazy installer instance
_lazy_installer: Optional[LazyLanguageInstaller] = None
_installer_lock = Lock()


def get_lazy_installer() -> LazyLanguageInstaller:
    """Get the global lazy installer instance."""
    global _lazy_installer
    
    if _lazy_installer is None:
        with _installer_lock:
            if _lazy_installer is None:
                _lazy_installer = LazyLanguageInstaller()
    
    return _lazy_installer


def cleanup_lazy_installer() -> None:
    """Cleanup the global lazy installer."""
    global _lazy_installer
    _lazy_installer = None
