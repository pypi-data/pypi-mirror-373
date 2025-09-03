"""
coex - Execute code snippets in isolated Docker environments.

A Python library for safely executing code snippets in isolated Docker containers
with support for multiple programming languages, input/output validation, and
security protection against destructive operations.
"""

from .core.executor import execute, get_ready
from .core.docker_manager import rm_docker
from .exceptions import CoexError, SecurityError, ExecutionError, DockerError

__version__ = "0.1.6"
__author__ = "torchtorchkimtorch"
__email__ = "torchtorchkimtorch@users.noreply.github.com"

# Main API exports
__all__ = [
    "execute",
    "get_ready",
    "rm_docker",
    "CoexError",
    "SecurityError",
    "ExecutionError",
    "DockerError",
]
