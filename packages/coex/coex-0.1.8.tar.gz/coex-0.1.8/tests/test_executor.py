"""
Unit tests for the code executor module.
"""

import pytest
import unittest.mock as mock
from typing import List, Any

from coex.core.executor import CodeExecutor, execute
from coex.exceptions import SecurityError, ValidationError, ExecutionError, DockerError


class TestCodeExecutor:
    """Test cases for CodeExecutor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.executor = CodeExecutor()
    
    def test_input_output_mode_success(self):
        """Test successful input/output validation mode."""
        inputs = [1, 2, 3]
        outputs = [2, 3, 4]
        code = """
def add_one(x):
    return x + 1
"""
        
        with mock.patch.object(self.executor, '_execute_input_output_mode') as mock_execute:
            mock_execute.return_value = [1, 1, 1]
            
            result = self.executor.execute(
                inputs=inputs, 
                outputs=outputs, 
                code=code, 
                language="python"
            )
            
            assert result == [1, 1, 1]
            mock_execute.assert_called_once_with(inputs, outputs, code, "python", None)
    
    def test_function_comparison_mode_success(self):
        """Test successful function comparison mode."""
        answer_fn = """
def say_hello():
    return "hello world"
"""
        code = """
def hello():
    return "hello world"
"""
        
        with mock.patch.object(self.executor, '_execute_function_comparison_mode') as mock_execute:
            mock_execute.return_value = [1]
            
            result = self.executor.execute(
                answer_fn=answer_fn,
                code=code,
                language="python"
            )
            
            assert result == [1]
            mock_execute.assert_called_once_with(answer_fn, code, "python", None)
    
    def test_simple_mode_success(self):
        """Test successful simple execution mode."""
        code = """
print("Hello, World!")
"""
        
        with mock.patch.object(self.executor, '_execute_simple_mode') as mock_execute:
            mock_execute.return_value = [1]
            
            result = self.executor.execute(code=code, language="python")
            
            assert result == [1]
            mock_execute.assert_called_once_with(code, "python", None)
    
    def test_security_error_handling(self):
        """Test security error handling."""
        code = """
import os
os.system("rm -rf /")
"""
        
        with mock.patch('coex.core.executor.validate_code') as mock_validate:
            mock_validate.side_effect = SecurityError("Dangerous code detected")
            
            result = self.executor.execute(code=code, language="python")
            
            assert result == [0]
    
    def test_validation_error_handling(self):
        """Test validation error handling."""
        inputs = [1, 2]
        outputs = [1, 2, 3]  # Mismatched lengths
        code = "def test(): pass"
        
        result = self.executor.execute(
            inputs=inputs,
            outputs=outputs,
            code=code,
            language="python"
        )
        
        assert result == [0, 0]  # Should return failures for all inputs
    
    def test_docker_error_handling(self):
        """Test Docker error handling."""
        code = "print('test')"
        
        with mock.patch.object(self.executor, 'docker_manager') as mock_docker:
            mock_docker.get_or_create_container.side_effect = DockerError("Docker failed")
            
            result = self.executor.execute(code=code, language="python")
            
            assert result == [0]
    
    def test_invalid_language(self):
        """Test handling of invalid programming language."""
        code = "print('test')"
        
        result = self.executor.execute(code=code, language="invalid_language")
        
        assert result == [0]
    
    def test_timeout_validation(self):
        """Test timeout parameter validation."""
        code = "print('test')"
        
        # Valid timeout
        with mock.patch.object(self.executor, '_execute_simple_mode') as mock_execute:
            mock_execute.return_value = [1]
            result = self.executor.execute(code=code, language="python", timeout=30)
            assert result == [1]
        
        # Invalid timeout (too large)
        result = self.executor.execute(code=code, language="python", timeout=500)
        assert result == [0]
    
    def test_empty_code_handling(self):
        """Test handling of empty code."""
        result = self.executor.execute(code="", language="python")
        assert result == [0]
        
        result = self.executor.execute(code="   ", language="python")
        assert result == [0]
    
    def test_no_code_or_answer_fn(self):
        """Test error when neither code nor answer_fn is provided."""
        result = self.executor.execute(language="python")
        assert result == [0]


class TestExecuteFunction:
    """Test cases for the main execute function."""
    
    def test_execute_function_delegates_to_executor(self):
        """Test that execute function properly delegates to CodeExecutor."""
        inputs = [1, 2, 3]
        outputs = [2, 3, 4]
        code = "def add_one(x): return x + 1"
        
        with mock.patch('coex.core.executor.get_executor') as mock_get_executor:
            mock_executor = mock.Mock()
            mock_executor.execute.return_value = [1, 1, 1]
            mock_get_executor.return_value = mock_executor
            
            result = execute(
                inputs=inputs,
                outputs=outputs,
                code=code,
                language="python",
                timeout=30
            )
            
            assert result == [1, 1, 1]
            mock_executor.execute.assert_called_once_with(
                inputs, outputs, code, None, "python", 30
            )
    
    def test_execute_with_answer_fn(self):
        """Test execute function with answer_fn parameter."""
        answer_fn = "def test(): return 42"
        code = "def test(): return 42"
        
        with mock.patch('coex.core.executor.get_executor') as mock_get_executor:
            mock_executor = mock.Mock()
            mock_executor.execute.return_value = [1]
            mock_get_executor.return_value = mock_executor
            
            result = execute(answer_fn=answer_fn, code=code, language="python")
            
            assert result == [1]
            mock_executor.execute.assert_called_once_with(
                None, None, code, answer_fn, "python", None
            )


class TestOutputComparison:
    """Test cases for output comparison functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.executor = CodeExecutor()
    
    def test_integer_comparison(self):
        """Test comparison of integer outputs."""
        assert self.executor._compare_outputs("42", 42) == True
        assert self.executor._compare_outputs("42.0", 42) == True
        assert self.executor._compare_outputs("43", 42) == False
    
    def test_float_comparison(self):
        """Test comparison of float outputs with tolerance."""
        assert self.executor._compare_outputs("3.14159", 3.14159) == True
        assert self.executor._compare_outputs("3.141590001", 3.14159) == True
        assert self.executor._compare_outputs("3.15", 3.14159) == False
    
    def test_string_comparison(self):
        """Test comparison of string outputs."""
        assert self.executor._compare_outputs("hello", "hello") == True
        assert self.executor._compare_outputs("  hello  ", "hello") == True
        assert self.executor._compare_outputs("hello", "world") == False
    
    def test_boolean_comparison(self):
        """Test comparison of boolean outputs."""
        assert self.executor._compare_outputs("true", True) == True
        assert self.executor._compare_outputs("True", True) == True
        assert self.executor._compare_outputs("false", False) == True
        assert self.executor._compare_outputs("False", False) == True
        assert self.executor._compare_outputs("true", False) == False


class TestErrorScenarios:
    """Test cases for various error scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.executor = CodeExecutor()
    
    def test_malformed_code(self):
        """Test handling of syntactically incorrect code."""
        code = """
def broken_function(
    # Missing closing parenthesis and colon
"""
        
        with mock.patch.object(self.executor, '_execute_simple_mode') as mock_execute:
            mock_execute.side_effect = ExecutionError("Syntax error")
            
            result = self.executor.execute(code=code, language="python")
            assert result == [0]
    
    def test_runtime_error_in_code(self):
        """Test handling of runtime errors in executed code."""
        code = """
def divide_by_zero():
    return 1 / 0
"""
        
        with mock.patch.object(self.executor, '_execute_simple_mode') as mock_execute:
            mock_execute.side_effect = ExecutionError("Division by zero")
            
            result = self.executor.execute(code=code, language="python")
            assert result == [0]
    
    def test_container_creation_failure(self):
        """Test handling of Docker container creation failure."""
        code = "print('test')"
        
        with mock.patch.object(self.executor, 'docker_manager') as mock_docker:
            mock_docker.get_or_create_container.side_effect = DockerError("Container creation failed")
            
            result = self.executor.execute(code=code, language="python")
            assert result == [0]
    
    def test_execution_timeout(self):
        """Test handling of execution timeout."""
        code = """
import time
time.sleep(100)  # Long running code
"""
        
        with mock.patch.object(self.executor, '_execute_simple_mode') as mock_execute:
            mock_execute.side_effect = ExecutionError("Execution timed out")
            
            result = self.executor.execute(code=code, language="python", timeout=1)
            assert result == [0]


if __name__ == "__main__":
    pytest.main([__file__])
