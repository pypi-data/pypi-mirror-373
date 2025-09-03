"""
Docker-based subprocess executor that runs language tools inside Docker containers.
"""

import os
import tempfile
import random
from typing import List, Optional, Any, Tuple
from pathlib import Path

from ..config.settings import settings
from ..exceptions import ExecutionError, TimeoutError
import logging
from .docker_manager import get_docker_manager
from .lazy_installer import get_lazy_installer
from .languages import language_manager
from .security import validate_code, sanitize_code

logger = logging.getLogger(__name__)


class DockerSubprocessExecutor:
    """Execute code using subprocess inside Docker containers."""
    
    def __init__(self):
        """Initialize Docker subprocess executor."""
        self.docker_manager = get_docker_manager()
        self.lazy_installer = get_lazy_installer()
        self.container = None
    
    def _get_container(self):
        """Get or create Docker container."""
        # Always get fresh container from docker manager
        # This ensures we get a new container after cleanup
        self.container = self.docker_manager.get_or_create_container()
        return self.container
    
    def execute_code(self, code: str, language: str, input_val: Any = None, 
                    timeout: Optional[int] = None) -> str:
        """
        Execute code using subprocess inside Docker container.
        
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
            
            # Ensure language is available (lazy installation)
            self.lazy_installer.ensure_language_available(language)

            # Get container
            container = self._get_container()

            # Execute code in container
            result = self._execute_in_docker(container, prepared_code, language, timeout)
            
            return result
            
        except Exception as e:
            logger.error(f"Code execution failed: {e}")
            raise ExecutionError(f"Code execution failed: {e}")
    
    def _prepare_test_code(self, code: str, input_val: Any, language: str) -> str:
        """Prepare code with input value for testing."""
        if language.lower() == "python":
            # Python test code generation
            if input_val is not None:
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

        # Call function with input and print the result
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
        # The function will handle its own output (print statements)
        func()
    else:
        print("Error: No function found to test")
        sys.exit(1)
        
except Exception as e:
    print(f"Error: {{e}}")
    sys.exit(1)
"""
            return test_code
        elif language.lower() == "java":
            # Java test code generation - auto-detect function name
            if input_val is not None:
                # Always create a simple test main method that calls the detected function
                function_name = self._detect_java_function_name(code)

                # Check if main method already exists
                if "public static void main" in code:
                    # Remove existing main method and add new test main method
                    test_code = self._replace_java_main_method(code, function_name, input_val)
                else:
                    # No main method, add one that calls the detected function
                    lines = code.strip().split('\n')
                    for i in range(len(lines) - 1, -1, -1):
                        if '}' in lines[i]:
                            main_method = f"    public static void main(String[] args) {{\n        System.out.println({function_name}({input_val}));\n    }}"
                            lines.insert(i, main_method)
                            break
                    test_code = '\n'.join(lines)
            else:
                # Simple execution mode
                if "public static void main" in code:
                    # Code already has main method, use as-is
                    test_code = code
                else:
                    # Add simple main method
                    lines = code.strip().split('\n')
                    for i in range(len(lines) - 1, -1, -1):
                        if '}' in lines[i]:
                            main_method = f"    public static void main(String[] args) {{\n        System.out.println(\"Hello from Java\");\n    }}"
                            lines.insert(i, main_method)
                            break
                    test_code = '\n'.join(lines)

            return test_code
        else:
            # For other languages, use language handler's prepare_code method
            handler = language_manager.get_handler(language)
            if handler and hasattr(handler, 'prepare_code'):
                return handler.prepare_code(code, input_val)
            return code

    def _extract_java_class_name(self, code: str) -> str:
        """Extract the main class name from Java code."""
        import re

        # Look for public class declaration
        match = re.search(r'public\s+class\s+(\w+)', code)
        if match:
            return match.group(1)

        # Look for any class declaration
        match = re.search(r'class\s+(\w+)', code)
        if match:
            return match.group(1)

        # Default fallback
        return "Main"

    def _detect_java_function_name(self, code: str) -> str:
        """Detect the main function name from Java code (excluding main method)."""
        import re

        # Look for public static methods that return a value (not void) and aren't main
        pattern = r'public\s+static\s+(?!void)\w+\s+(\w+)\s*\([^)]*\)'
        matches = re.findall(pattern, code)

        # Filter out 'main' method
        function_names = [name for name in matches if name != "main"]

        if function_names:
            # Return the first non-main function found
            return function_names[0]

        # Fallback: look for any static method (including void)
        pattern = r'public\s+static\s+\w+\s+(\w+)\s*\([^)]*\)'
        matches = re.findall(pattern, code)
        function_names = [name for name in matches if name != "main"]

        if function_names:
            return function_names[0]

        # Default fallback
        return "doubleValue"

    def _replace_java_main_method(self, code: str, function_name: str, input_val) -> str:
        """Replace existing main method with test main method."""
        lines = code.split('\n')
        result_lines = []
        in_main_method = False
        brace_count = 0
        main_method_start = -1

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if this line starts a main method
            if not in_main_method and "public static void main" in line:
                in_main_method = True
                main_method_start = i
                brace_count = line.count('{') - line.count('}')

                # If the main method is complete on one line
                if brace_count == 0:
                    # Replace with test main method
                    result_lines.append(f"    public static void main(String[] args) {{")
                    result_lines.append(f"        System.out.println({function_name}({input_val}));")
                    result_lines.append(f"    }}")
                    in_main_method = False
                else:
                    # Skip this line, we'll replace the entire method
                    pass
            elif in_main_method:
                # Count braces to find end of main method
                brace_count += line.count('{') - line.count('}')

                if brace_count == 0:
                    # End of main method found, insert test main method
                    result_lines.append(f"    public static void main(String[] args) {{")
                    result_lines.append(f"        System.out.println({function_name}({input_val}));")
                    result_lines.append(f"    }}")
                    in_main_method = False
                # Skip lines inside main method
            else:
                # Regular line, keep it
                result_lines.append(line)

            i += 1

        return '\n'.join(result_lines)

    def _execute_in_docker(self, container, code: str, language: str, timeout: int) -> str:
        """Execute code inside Docker container using subprocess."""
        try:
            # Get file extension
            lang_config = settings.languages.get(language.lower())
            if not lang_config:
                raise ExecutionError(f"Unsupported language: {language}")
            
            extension = lang_config["extension"]
            
            # Create unique filename (special handling for Java)
            if language.lower() == "java":
                # For Java, extract class name from code
                class_name = self._extract_java_class_name(code)
                filename = f"{class_name}.java"
            else:
                filename = f"code_{random.randint(10000, 99999)}{extension}"
            
            # Write code to file in container
            write_cmd = f"cat > /workspace/{filename} << 'EOF'\n{code}\nEOF"
            exit_code, stdout, stderr = self.docker_manager.execute_in_container(
                container, ["bash", "-c", write_cmd]
            )
            if exit_code != 0:
                raise ExecutionError(f"Failed to write code file: {stderr}")
            
            # Execute based on language
            result = self._execute_language_in_docker(container, filename, language, timeout)
            
            # Clean up file
            cleanup_cmd = f"rm -f /workspace/{filename} /workspace/{filename[:-len(extension)]}"
            self.docker_manager.execute_in_container(
                container, ["bash", "-c", cleanup_cmd]
            )
            
            return result
            
        except Exception as e:
            if isinstance(e, (ExecutionError, TimeoutError)):
                raise
            raise ExecutionError(f"Failed to execute {language} code in Docker: {e}")
    
    def _execute_language_in_docker(self, container, filename: str, language: str, timeout: int) -> str:
        """Execute language-specific commands using Python subprocess in Docker container."""
        name_without_ext = os.path.splitext(filename)[0]

        try:
            if language.lower() == "python":
                # Python: Use subprocess to run python3
                python_code = f"""
import subprocess
import sys

try:
    result = subprocess.run(
        ["python3", "/workspace/{filename}"],
        capture_output=True,
        text=True,
        timeout={timeout}
    )

    if result.returncode != 0:
        print(f"Error: {{result.stderr}}", file=sys.stderr)
        sys.exit(result.returncode)
    else:
        print(result.stdout.strip())

except subprocess.TimeoutExpired:
    print("Error: Execution timed out", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error: {{e}}", file=sys.stderr)
    sys.exit(1)
"""

            elif language.lower() == "java":
                # Java: Use subprocess to compile and run
                python_code = f"""
import subprocess
import sys

try:
    # Compile Java code
    compile_result = subprocess.run(
        ["javac", "/workspace/{filename}"],
        cwd="/workspace",
        capture_output=True,
        text=True,
        timeout={timeout}
    )

    if compile_result.returncode != 0:
        print(f"Compilation Error: {{compile_result.stderr}}", file=sys.stderr)
        sys.exit(1)

    # Run Java code
    run_result = subprocess.run(
        ["java", "{name_without_ext}"],
        cwd="/workspace",
        capture_output=True,
        text=True,
        timeout={timeout}
    )

    if run_result.returncode != 0:
        print(f"Runtime Error: {{run_result.stderr}}", file=sys.stderr)
        sys.exit(run_result.returncode)
    else:
        print(run_result.stdout.strip())

except subprocess.TimeoutExpired:
    print("Error: Execution timed out", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error: {{e}}", file=sys.stderr)
    sys.exit(1)
"""

            elif language.lower() == "javascript":
                # JavaScript: Use subprocess to run node
                python_code = f"""
import subprocess
import sys

try:
    result = subprocess.run(
        ["node", "/workspace/{filename}"],
        capture_output=True,
        text=True,
        timeout={timeout}
    )

    if result.returncode != 0:
        print(f"Error: {{result.stderr}}", file=sys.stderr)
        sys.exit(result.returncode)
    else:
        print(result.stdout.strip())

except subprocess.TimeoutExpired:
    print("Error: Execution timed out", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error: {{e}}", file=sys.stderr)
    sys.exit(1)
"""

            elif language.lower() == "cpp":
                # C++: Use subprocess to compile and run
                python_code = f"""
import subprocess
import sys

try:
    # Compile C++ code
    compile_result = subprocess.run(
        ["g++", "-o", "{name_without_ext}", "/workspace/{filename}"],
        cwd="/workspace",
        capture_output=True,
        text=True,
        timeout={timeout}
    )

    if compile_result.returncode != 0:
        print(f"Compilation Error: {{compile_result.stderr}}", file=sys.stderr)
        sys.exit(1)

    # Run C++ code
    run_result = subprocess.run(
        ["./{name_without_ext}"],
        cwd="/workspace",
        capture_output=True,
        text=True,
        timeout={timeout}
    )

    if run_result.returncode != 0:
        print(f"Runtime Error: {{run_result.stderr}}", file=sys.stderr)
        sys.exit(run_result.returncode)
    else:
        print(run_result.stdout.strip())

except subprocess.TimeoutExpired:
    print("Error: Execution timed out", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error: {{e}}", file=sys.stderr)
    sys.exit(1)
"""

            else:
                raise ExecutionError(f"Unsupported language: {language}")

            # Write Python subprocess script to container
            script_name = f"executor_{language}_{random.randint(10000, 99999)}.py"
            write_script_cmd = f"cat > /workspace/{script_name} << 'EOF'\n{python_code}\nEOF"
            exit_code, stdout, stderr = self.docker_manager.execute_in_container(
                container, ["bash", "-c", write_script_cmd]
            )
            if exit_code != 0:
                raise ExecutionError(f"Failed to write executor script: {stderr}")

            # Execute Python subprocess script
            exit_code, stdout, stderr = self.docker_manager.execute_in_container(
                container, ["python3", f"/workspace/{script_name}"]
            )

            # Clean up executor script
            cleanup_script_cmd = f"rm -f /workspace/{script_name}"
            self.docker_manager.execute_in_container(
                container, ["bash", "-c", cleanup_script_cmd]
            )

            # Check result
            if exit_code != 0:
                error_msg = stderr.strip() if stderr else "Unknown error"
                stdout_msg = stdout.strip() if stdout else ""
                full_error = f"Return code: {exit_code}, stderr: {error_msg}, stdout: {stdout_msg}"
                logger.error(f"Execution failed: {full_error}")
                raise ExecutionError(f"Execution failed: {full_error}")

            output = stdout.strip()
            logger.debug(f"Execution output: {output}")
            return output

        except Exception as e:
            if isinstance(e, (ExecutionError, TimeoutError)):
                raise
            raise ExecutionError(f"Failed to execute {language} code: {e}")
    
    def cleanup(self) -> None:
        """Clean up Docker container."""
        if self.container is not None:
            try:
                self.docker_manager.cleanup_container()
                self.container = None
            except Exception as e:
                logger.warning(f"Failed to cleanup Docker container: {e}")


# Global Docker subprocess executor instance
_docker_subprocess_executor: Optional[DockerSubprocessExecutor] = None


def get_docker_subprocess_executor() -> DockerSubprocessExecutor:
    """Get global Docker subprocess executor instance."""
    global _docker_subprocess_executor
    if _docker_subprocess_executor is None:
        _docker_subprocess_executor = DockerSubprocessExecutor()
    return _docker_subprocess_executor


def cleanup_docker_subprocess_executor() -> None:
    """Cleanup global Docker subprocess executor."""
    global _docker_subprocess_executor
    if _docker_subprocess_executor is not None:
        _docker_subprocess_executor.cleanup()
        _docker_subprocess_executor = None
