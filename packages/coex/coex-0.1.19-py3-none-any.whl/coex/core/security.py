"""
Security module for validating and sanitizing code before execution.
"""

import re
import ast
import logging
from typing import List, Set, Optional, Union
from ..config.settings import settings
from ..exceptions import SecurityError

logger = logging.getLogger(__name__)


class SecurityValidator:
    """Validates code for security threats before execution."""
    
    def __init__(self):
        """Initialize the security validator."""
        self.blocked_commands = set(settings.security["blocked_commands"])
        self.blocked_patterns = [re.compile(pattern, re.IGNORECASE) 
                               for pattern in settings.security["blocked_patterns"]]
    
    def validate_code(self, code: str, language: str = "python") -> None:
        """
        Validate code for security threats.
        
        Args:
            code: The code to validate
            language: Programming language of the code
            
        Raises:
            SecurityError: If dangerous code is detected
        """
        if not settings.security["enable_security_checks"]:
            return
        
        logger.debug(f"Validating {language} code for security threats")
        
        # Check for blocked commands
        self._check_blocked_commands(code)
        
        # Check for blocked patterns
        self._check_blocked_patterns(code)
        
        # Language-specific validation
        if language.lower() == "python":
            self._validate_python_code(code)
        elif language.lower() in ["javascript", "js"]:
            self._validate_javascript_code(code)
        elif language.lower() in ["bash", "sh", "shell"]:
            self._validate_shell_code(code)
    
    def _check_blocked_commands(self, code: str) -> None:
        """Check for blocked commands in the code."""
        code_lower = code.lower()
        words = re.findall(r'\b\w+\b', code_lower)
        
        for word in words:
            if word in self.blocked_commands:
                raise SecurityError(f"Blocked command detected: {word}")
    
    def _check_blocked_patterns(self, code: str) -> None:
        """Check for blocked patterns in the code."""
        for pattern in self.blocked_patterns:
            if pattern.search(code):
                raise SecurityError(f"Blocked pattern detected: {pattern.pattern}")
    
    def _validate_python_code(self, code: str) -> None:
        """Validate Python-specific security threats."""
        try:
            # Parse the AST to check for dangerous constructs
            tree = ast.parse(code)
            
            # Check for dangerous imports
            dangerous_imports = {
                'os', 'subprocess', 'sys', 'shutil', 'glob',
                'socket', 'urllib', 'requests', 'http',
                'ftplib', 'smtplib', 'telnetlib', 'paramiko'
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in dangerous_imports:
                            raise SecurityError(f"Dangerous import detected: {alias.name}")
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module in dangerous_imports:
                        raise SecurityError(f"Dangerous import detected: {node.module}")
                
                # Check for dangerous function calls
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['eval', 'exec', 'compile', '__import__']:
                            raise SecurityError(f"Dangerous function call detected: {node.func.id}")
                    
                    elif isinstance(node.func, ast.Attribute):
                        # Check for os.system, subprocess.call, etc.
                        if (isinstance(node.func.value, ast.Name) and 
                            node.func.value.id == 'os' and 
                            node.func.attr in ['system', 'popen', 'spawn']):
                            raise SecurityError(f"Dangerous function call detected: os.{node.func.attr}")
                
                # Check for file operations
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == 'open':
                        # Check if opening files in write mode
                        if len(node.args) > 1:
                            if isinstance(node.args[1], ast.Constant) and 'w' in str(node.args[1].value):
                                logger.warning("File write operation detected")
        
        except SyntaxError:
            # If code has syntax errors, let the execution engine handle it
            pass
    
    def _validate_javascript_code(self, code: str) -> None:
        """Validate JavaScript-specific security threats."""
        dangerous_patterns = [
            r'require\s*\(\s*["\']fs["\']',
            r'require\s*\(\s*["\']child_process["\']',
            r'require\s*\(\s*["\']os["\']',
            r'require\s*\(\s*["\']path["\']',
            r'process\.exit',
            r'process\.kill',
            r'eval\s*\(',
            r'Function\s*\(',
            r'setTimeout\s*\(',
            r'setInterval\s*\(',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                raise SecurityError(f"Dangerous JavaScript pattern detected: {pattern}")
    
    def _validate_shell_code(self, code: str) -> None:
        """Validate shell script security threats."""
        # Shell scripts are inherently dangerous, so we're very restrictive
        dangerous_shell_patterns = [
            r'rm\s+',
            r'mv\s+',
            r'cp\s+',
            r'chmod\s+',
            r'chown\s+',
            r'sudo\s+',
            r'su\s+',
            r'wget\s+',
            r'curl\s+',
            r'nc\s+',
            r'netcat\s+',
            r'ssh\s+',
            r'scp\s+',
            r'>\s*/',
            r'>>\s*/',
            r'\|\s*sh',
            r'\|\s*bash',
        ]
        
        for pattern in dangerous_shell_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                raise SecurityError(f"Dangerous shell pattern detected: {pattern}")


class CodeSanitizer:
    """Sanitizes code by removing or modifying dangerous constructs."""
    
    def __init__(self):
        """Initialize the code sanitizer."""
        pass
    
    def sanitize_code(self, code: str, language: str = "python") -> str:
        """
        Sanitize code by removing dangerous constructs.
        
        Args:
            code: The code to sanitize
            language: Programming language of the code
            
        Returns:
            Sanitized code
        """
        if not settings.security["enable_security_checks"]:
            return code
        
        sanitized = code
        
        # Remove comments that might contain dangerous commands
        if language.lower() == "python":
            sanitized = re.sub(r'#.*$', '', sanitized, flags=re.MULTILINE)
        elif language.lower() in ["javascript", "js"]:
            sanitized = re.sub(r'//.*$', '', sanitized, flags=re.MULTILINE)
            sanitized = re.sub(r'/\*.*?\*/', '', sanitized, flags=re.DOTALL)
        
        # Remove excessive whitespace
        sanitized = re.sub(r'\n\s*\n', '\n', sanitized)
        sanitized = sanitized.strip()
        
        return sanitized


# Global instances
security_validator = SecurityValidator()
code_sanitizer = CodeSanitizer()


def validate_code(code: str, language: str = "python") -> None:
    """
    Validate code for security threats.
    
    Args:
        code: The code to validate
        language: Programming language of the code
        
    Raises:
        SecurityError: If dangerous code is detected
    """
    security_validator.validate_code(code, language)


def sanitize_code(code: str, language: str = "python") -> str:
    """
    Sanitize code by removing dangerous constructs.
    
    Args:
        code: The code to sanitize
        language: Programming language of the code
        
    Returns:
        Sanitized code
    """
    return code_sanitizer.sanitize_code(code, language)
