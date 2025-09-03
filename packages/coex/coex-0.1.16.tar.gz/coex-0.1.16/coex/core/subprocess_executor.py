"""
Subprocess-based code executor that runs language tools on the host system.
"""

import os
import tempfile
import subprocess
import shutil
from typing import List, Optional, Any, Tuple
from pathlib import Path

from ..config.settings import settings
from ..exceptions import ExecutionError, TimeoutError
import logging
from .languages import language_manager
from .security import validate_code, sanitize_code

logger = logging.getLogger(__name__)


class SubprocessExecutor:
    """Execute code using subprocess on the host system."""
    
    def __init__(self):
        """Initialize subprocess executor."""
        self.temp_dir = None
        self._create_temp_dir()
    
    def _create_temp_dir(self) -> None:
        """Create temporary directory for code execution."""
        try:
            self.temp_dir = tempfile.mkdtemp(prefix="coex_")
            logger.debug(f"Created temporary directory: {self.temp_dir}")
        except Exception as e:
            raise ExecutionError(f"Failed to create temporary directory: {e}")
    
    def execute_code(self, code: str, language: str, input_val: Any = None, 
                    timeout: Optional[int] = None) -> str:
        """
        Execute code using subprocess on host system.
        
        Args:
            code: Code to execute
            language: Programming language
            input_val: Input value for testing
            timeout: Execution timeout
            
        Returns:
            Execution output
        """
        if timeout is None:
            timeout = settings.execution["timeout"]
        
        try:
            # Validate and sanitize code
            validate_code(code, language)
            sanitized_code = sanitize_code(code, language)
            
            # Prepare code for execution
            if input_val is not None:
                prepared_code = self._prepare_test_code(sanitized_code, input_val, language)
            else:
                prepared_code = sanitized_code
            
            # Prepare code file
            file_path = self._write_code_file(prepared_code, language)

            # Execute command directly based on language
            result = self._execute_language_specific(file_path, language, timeout)
            
            return result
            
        except Exception as e:
            logger.error(f"Code execution failed: {e}")
            raise ExecutionError(f"Code execution failed: {e}")
    
    def _prepare_test_code(self, code: str, input_val: Any, language: str) -> str:
        """Prepare code with input value for testing."""
        if language.lower() == "python":
            # Simple Python test code generation
            if input_val is not None:
                # Input/output mode
                test_code = f"""
{code}

# Test execution
import sys
import inspect

try:
    # Get all globals first to avoid dictionary change during iteration
    all_globals = dict(globals())

    # Find all user-defined functions
    functions = []
    for name, obj in all_globals.items():
        if (inspect.isfunction(obj) and
            not name.startswith('_') and
            name not in ['inspect', 'sys', 'all_globals']):
            functions.append(name)

    if functions:
        func_name = functions[0]  # Use first function found
        func = all_globals[func_name]

        # Call function with input
        result = func({repr(input_val)})
        print(result)
    else:
        print("Error: No function found to test")
        sys.exit(1)

except Exception as e:
    print(f"Error: {{e}}")
    sys.exit(1)
"""
            else:
                # Simple execution mode
                test_code = f"""
{code}

# Test execution
import sys
import inspect

try:
    # Get all globals first to avoid dictionary change during iteration
    all_globals = dict(globals())

    # Find all user-defined functions
    functions = []
    for name, obj in all_globals.items():
        if (inspect.isfunction(obj) and
            not name.startswith('_') and
            name not in ['inspect', 'sys', 'all_globals']):
            functions.append(name)

    if functions:
        func_name = functions[0]  # Use first function found
        func = all_globals[func_name]

        # Call function without parameters
        result = func()
        print(result)
    else:
        print("Error: No function found to test")
        sys.exit(1)

except Exception as e:
    print(f"Error: {{e}}")
    sys.exit(1)
"""
            return test_code
        else:
            # For other languages, use language handler's prepare_code method
            handler = language_manager.get_handler(language)
            if handler and hasattr(handler, 'prepare_code'):
                return handler.prepare_code(code)
            return code

    def _execute_language_specific(self, file_path: str, language: str, timeout: int) -> str:
        """Execute code file using language-specific commands."""
        work_dir = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        name_without_ext = os.path.splitext(filename)[0]

        try:
            if language.lower() == "python":
                # Python: python3 script.py
                result = subprocess.run(
                    ["python3", filename],
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

            elif language.lower() == "java":
                # Java: javac Hello.java && java Hello
                # First compile
                compile_result = subprocess.run(
                    ["javac", filename],
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                if compile_result.returncode != 0:
                    raise ExecutionError(f"Java compilation failed: {compile_result.stderr}")

                # Then run
                result = subprocess.run(
                    ["java", name_without_ext],
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

            elif language.lower() == "javascript":
                # JavaScript: node script.js
                result = subprocess.run(
                    ["node", filename],
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

            elif language.lower() == "cpp":
                # C++: g++ -o program program.cpp && ./program
                compile_result = subprocess.run(
                    ["g++", "-o", name_without_ext, filename],
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                if compile_result.returncode != 0:
                    raise ExecutionError(f"C++ compilation failed: {compile_result.stderr}")

                result = subprocess.run(
                    [f"./{name_without_ext}"],
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

            elif language.lower() == "c":
                # C: gcc -o program program.c && ./program
                compile_result = subprocess.run(
                    ["gcc", "-o", name_without_ext, filename],
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                if compile_result.returncode != 0:
                    raise ExecutionError(f"C compilation failed: {compile_result.stderr}")

                result = subprocess.run(
                    [f"./{name_without_ext}"],
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

            else:
                raise ExecutionError(f"Unsupported language: {language}")

            # Check result
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                stdout_msg = result.stdout.strip() if result.stdout else ""
                full_error = f"Return code: {result.returncode}, stderr: {error_msg}, stdout: {stdout_msg}"
                logger.error(f"Execution failed: {full_error}")
                raise ExecutionError(f"Execution failed: {full_error}")

            output = result.stdout.strip()
            logger.debug(f"Execution output: {output}")
            return output

        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Code execution timed out after {timeout} seconds")
        except Exception as e:
            if isinstance(e, (ExecutionError, TimeoutError)):
                raise
            raise ExecutionError(f"Failed to execute {language} code: {e}")

    def _write_code_file(self, code: str, language: str) -> str:
        """Write code to temporary file."""
        try:
            # Get file extension
            lang_config = settings.languages.get(language.lower())
            if not lang_config:
                raise ExecutionError(f"Unsupported language: {language}")
            
            extension = lang_config["extension"]
            
            # Create unique filename
            import random
            filename = f"code_{random.randint(10000, 99999)}{extension}"
            file_path = os.path.join(self.temp_dir, filename)
            
            # Write code to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            logger.debug(f"Code written to: {file_path}")
            return file_path
            
        except Exception as e:
            raise ExecutionError(f"Failed to write code file: {e}")
    

    
    def cleanup(self) -> None:
        """Clean up temporary directory."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.debug(f"Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temporary directory: {e}")
            finally:
                self.temp_dir = None
    
    def __del__(self):
        """Cleanup on destruction."""
        self.cleanup()


# Global subprocess executor instance
_subprocess_executor: Optional[SubprocessExecutor] = None


def get_subprocess_executor() -> SubprocessExecutor:
    """Get global subprocess executor instance."""
    global _subprocess_executor
    if _subprocess_executor is None:
        _subprocess_executor = SubprocessExecutor()
    return _subprocess_executor


def cleanup_subprocess_executor() -> None:
    """Cleanup global subprocess executor."""
    global _subprocess_executor
    if _subprocess_executor is not None:
        _subprocess_executor.cleanup()
        _subprocess_executor = None
