"""
Custom exceptions for the coex library.
"""


class CoexError(Exception):
    """Base exception class for all coex-related errors."""
    pass


class SecurityError(CoexError):
    """Raised when potentially dangerous code is detected."""
    pass


class ExecutionError(CoexError):
    """Raised when code execution fails."""
    pass


class DockerError(CoexError):
    """Raised when Docker operations fail."""
    pass


class ValidationError(CoexError):
    """Raised when input validation fails."""
    pass


class TimeoutError(CoexError):
    """Raised when code execution times out."""
    pass


class LanguageNotSupportedError(CoexError):
    """Raised when an unsupported programming language is requested."""
    pass
