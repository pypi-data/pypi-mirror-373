"""
File handling utilities for the coex library.
"""

import os
import tempfile
import shutil
import uuid
import logging
from typing import Optional, Tuple, List
from pathlib import Path
from ..config.settings import settings
from ..exceptions import CoexError

logger = logging.getLogger(__name__)


class TempFileManager:
    """Manages temporary files for code execution."""
    
    def __init__(self):
        """Initialize temp file manager."""
        self.temp_dir = settings.execution["temp_dir"]
        self.cleanup_enabled = settings.execution["cleanup_temp_files"]
        self._created_files: List[str] = []
        self._created_dirs: List[str] = []
    
    def create_temp_file(self, content: str, extension: str = ".py", 
                        prefix: str = "coex_") -> str:
        """
        Create a temporary file with given content.
        
        Args:
            content: File content
            extension: File extension
            prefix: Filename prefix
            
        Returns:
            Path to created temporary file
        """
        try:
            # Ensure temp directory exists
            os.makedirs(self.temp_dir, exist_ok=True)
            
            # Generate unique filename
            file_id = str(uuid.uuid4())[:8]
            filename = f"{prefix}{file_id}{extension}"
            file_path = os.path.join(self.temp_dir, filename)
            
            # Write content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Track created file
            self._created_files.append(file_path)
            
            logger.debug(f"Created temporary file: {file_path}")
            return file_path
            
        except Exception as e:
            raise CoexError(f"Failed to create temporary file: {e}")
    
    def create_temp_dir(self, prefix: str = "coex_") -> str:
        """
        Create a temporary directory.
        
        Args:
            prefix: Directory name prefix
            
        Returns:
            Path to created temporary directory
        """
        try:
            # Generate unique directory name
            dir_id = str(uuid.uuid4())[:8]
            dir_name = f"{prefix}{dir_id}"
            dir_path = os.path.join(self.temp_dir, dir_name)
            
            # Create directory
            os.makedirs(dir_path, exist_ok=True)
            
            # Track created directory
            self._created_dirs.append(dir_path)
            
            logger.debug(f"Created temporary directory: {dir_path}")
            return dir_path
            
        except Exception as e:
            raise CoexError(f"Failed to create temporary directory: {e}")
    
    def cleanup_file(self, file_path: str) -> None:
        """
        Clean up a specific temporary file.
        
        Args:
            file_path: Path to file to clean up
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Cleaned up file: {file_path}")
            
            # Remove from tracking
            if file_path in self._created_files:
                self._created_files.remove(file_path)
                
        except Exception as e:
            logger.warning(f"Failed to cleanup file {file_path}: {e}")
    
    def cleanup_dir(self, dir_path: str) -> None:
        """
        Clean up a specific temporary directory.
        
        Args:
            dir_path: Path to directory to clean up
        """
        try:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                logger.debug(f"Cleaned up directory: {dir_path}")
            
            # Remove from tracking
            if dir_path in self._created_dirs:
                self._created_dirs.remove(dir_path)
                
        except Exception as e:
            logger.warning(f"Failed to cleanup directory {dir_path}: {e}")
    
    def cleanup_all(self) -> None:
        """Clean up all tracked temporary files and directories."""
        if not self.cleanup_enabled:
            logger.debug("Cleanup disabled, skipping")
            return
        
        # Clean up files
        for file_path in self._created_files.copy():
            self.cleanup_file(file_path)
        
        # Clean up directories
        for dir_path in self._created_dirs.copy():
            self.cleanup_dir(dir_path)
        
        logger.info("All temporary files and directories cleaned up")
    
    def get_stats(self) -> dict:
        """Get statistics about temporary files."""
        return {
            "tracked_files": len(self._created_files),
            "tracked_dirs": len(self._created_dirs),
            "temp_dir": self.temp_dir,
            "cleanup_enabled": self.cleanup_enabled
        }


def read_file_safe(file_path: str, max_size: Optional[int] = None) -> str:
    """
    Safely read file content with size limits.
    
    Args:
        file_path: Path to file
        max_size: Maximum file size in bytes
        
    Returns:
        File content
        
    Raises:
        CoexError: If file cannot be read or is too large
    """
    if max_size is None:
        max_size = settings.execution["max_output_size"]
    
    try:
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > max_size:
            raise CoexError(f"File too large: {file_size} bytes (max: {max_size})")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content
        
    except FileNotFoundError:
        raise CoexError(f"File not found: {file_path}")
    except PermissionError:
        raise CoexError(f"Permission denied reading file: {file_path}")
    except UnicodeDecodeError:
        raise CoexError(f"File encoding error: {file_path}")
    except Exception as e:
        raise CoexError(f"Failed to read file {file_path}: {e}")


def write_file_safe(file_path: str, content: str, max_size: Optional[int] = None) -> None:
    """
    Safely write content to file with size limits.
    
    Args:
        file_path: Path to file
        content: Content to write
        max_size: Maximum content size in bytes
        
    Raises:
        CoexError: If file cannot be written or content is too large
    """
    if max_size is None:
        max_size = settings.execution["max_output_size"]
    
    try:
        # Check content size
        content_bytes = content.encode('utf-8')
        if len(content_bytes) > max_size:
            raise CoexError(f"Content too large: {len(content_bytes)} bytes (max: {max_size})")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write file content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.debug(f"Wrote {len(content_bytes)} bytes to {file_path}")
        
    except PermissionError:
        raise CoexError(f"Permission denied writing file: {file_path}")
    except OSError as e:
        raise CoexError(f"OS error writing file {file_path}: {e}")
    except Exception as e:
        raise CoexError(f"Failed to write file {file_path}: {e}")


def ensure_directory(dir_path: str) -> None:
    """
    Ensure directory exists, creating it if necessary.
    
    Args:
        dir_path: Directory path
        
    Raises:
        CoexError: If directory cannot be created
    """
    try:
        os.makedirs(dir_path, exist_ok=True)
        logger.debug(f"Ensured directory exists: {dir_path}")
    except PermissionError:
        raise CoexError(f"Permission denied creating directory: {dir_path}")
    except OSError as e:
        raise CoexError(f"OS error creating directory {dir_path}: {e}")


def get_file_extension(language: str) -> str:
    """
    Get appropriate file extension for programming language.
    
    Args:
        language: Programming language name
        
    Returns:
        File extension including dot
    """
    extensions = {
        "python": ".py",
        "javascript": ".js",
        "js": ".js",
        "java": ".java",
        "cpp": ".cpp",
        "c++": ".cpp",
        "c": ".c",
        "go": ".go",
        "rust": ".rs",
        "ruby": ".rb",
        "php": ".php",
        "shell": ".sh",
        "bash": ".sh",
    }
    
    return extensions.get(language.lower(), ".txt")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove dangerous characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace dangerous characters
    import re
    
    # Replace dangerous characters with underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "file"
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255-len(ext)] + ext
    
    return sanitized


def is_safe_path(path: str, base_dir: str) -> bool:
    """
    Check if path is safe (within base directory).
    
    Args:
        path: Path to check
        base_dir: Base directory
        
    Returns:
        True if path is safe
    """
    try:
        # Resolve paths
        resolved_path = os.path.realpath(path)
        resolved_base = os.path.realpath(base_dir)
        
        # Check if path is within base directory
        return resolved_path.startswith(resolved_base)
        
    except Exception:
        return False


# Global temp file manager
_temp_manager: Optional[TempFileManager] = None


def get_temp_manager() -> TempFileManager:
    """Get global temp file manager instance."""
    global _temp_manager
    if _temp_manager is None:
        _temp_manager = TempFileManager()
    return _temp_manager


def cleanup_temp_files() -> None:
    """Clean up all temporary files."""
    manager = get_temp_manager()
    manager.cleanup_all()
