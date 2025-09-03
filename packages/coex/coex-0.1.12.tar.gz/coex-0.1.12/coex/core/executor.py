"""
Main execution engine for running code snippets in Docker containers.
"""

import logging
import time
import json
import ast
import traceback
from typing import List, Optional, Union, Any, Dict, Tuple
from .docker_manager import get_docker_manager
from .docker_subprocess_executor import get_docker_subprocess_executor, cleanup_docker_subprocess_executor
from .lazy_installer import get_lazy_installer, cleanup_lazy_installer
from .languages import language_manager
from .security import validate_code, sanitize_code
from ..config.settings import settings
from ..exceptions import ExecutionError, SecurityError, ValidationError, TimeoutError, DockerError
from ..utils.validation import (
    validate_inputs_outputs, validate_code as validate_code_util,
    validate_language, validate_timeout, validate_execution_mode,
    compare_values, extract_error_message
)

logger = logging.getLogger(__name__)


class CodeExecutor:
    """Main code execution engine."""
    
    def __init__(self):
        """Initialize the code executor."""
        self.docker_manager = get_docker_manager()
        self.docker_subprocess_executor = get_docker_subprocess_executor()
    
    def execute(self,
                inputs: Optional[List[Any]] = None,
                outputs: Optional[List[Any]] = None,
                code: Optional[str] = None,
                answer_fn: Optional[str] = None,
                language: str = "python",
                timeout: Optional[int] = None,
                mode: Optional[str] = None) -> List[int]:
        """
        Execute code with various validation modes.

        Args:
            inputs: List of input values for testing
            outputs: List of expected output values
            code: Code to execute
            answer_fn: Reference function code for comparison
            language: Programming language
            timeout: Execution timeout in seconds
            mode: Execution mode ("answer" for input/output validation,
                  "function" for function comparison, None for auto-detection)

        Returns:
            List of integers (0 or 1) indicating pass/fail for each test case
        """
        try:
            # Validate inputs with comprehensive error handling
            self._validate_inputs(inputs, outputs, code, answer_fn, language, mode)

            # Normalize language
            language = validate_language(language)

            # Validate timeout
            timeout = validate_timeout(timeout)

            # Determine execution mode and execute
            execution_mode = self._determine_execution_mode(inputs, outputs, code, answer_fn, mode)

            if execution_mode == "answer":
                return self._execute_input_output_mode_docker(inputs, outputs, code, language, timeout)
            elif execution_mode == "function":
                return self._execute_function_comparison_mode_docker(answer_fn, code, language, timeout)
            else:
                # Simple execution mode
                return self._execute_simple_mode_docker(code, language, timeout)

        except SecurityError as e:
            # Return all failures for security violations
            logger.warning(f"Security violation detected: {e}")
            num_tests = len(inputs) if inputs else 1
            return [0] * num_tests
        except ValidationError as e:
            # Return all failures for validation errors
            logger.error(f"Validation error: {e}")
            num_tests = len(inputs) if inputs else 1
            return [0] * num_tests
        except DockerError as e:
            # Return all failures for Docker errors
            logger.error(f"Docker error: {e}")
            num_tests = len(inputs) if inputs else 1
            return [0] * num_tests
        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Unexpected execution error: {e}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            num_tests = len(inputs) if inputs else 1
            return [0] * num_tests
    
    def _validate_inputs(self, inputs: Optional[List[Any]], outputs: Optional[List[Any]],
                        code: Optional[str], answer_fn: Optional[str], language: str, mode: Optional[str]) -> None:
        """Validate input parameters with comprehensive error handling."""
        try:
            # Validate mode parameter if provided
            if mode is not None and mode not in ["answer", "function"]:
                raise ValidationError(f"Invalid mode '{mode}'. Must be 'answer' or 'function'")

            # Validate execution mode and parameters
            execution_mode = validate_execution_mode(inputs, outputs, code, answer_fn)

            # Validate mode consistency
            if mode == "answer" and (inputs is None or outputs is None):
                raise ValidationError("Mode 'answer' requires both inputs and outputs parameters")
            if mode == "function" and answer_fn is None:
                raise ValidationError("Mode 'function' requires answer_fn parameter")

            # Validate language
            normalized_language = validate_language(language)

            # Validate inputs and outputs if provided
            if inputs is not None and outputs is not None:
                validate_inputs_outputs(inputs, outputs)

            # Validate code strings
            if code:
                validate_code_util(code)
                validate_code(code, normalized_language)

            if answer_fn:
                validate_code_util(answer_fn)
                validate_code(answer_fn, normalized_language)

        except ValidationError:
            raise
        except SecurityError:
            raise
        except Exception as e:
            logger.error(f"Unexpected validation error: {e}")
            raise ValidationError(f"Validation failed: {e}")

    def _determine_execution_mode(self, inputs: Optional[List[Any]], outputs: Optional[List[Any]],
                                 code: Optional[str], answer_fn: Optional[str], mode: Optional[str]) -> str:
        """Determine the execution mode based on parameters."""
        # If mode is explicitly specified, use it
        if mode is not None:
            return mode

        # Auto-detect mode based on parameters (backward compatibility)
        if inputs is not None and outputs is not None:
            return "answer"
        elif answer_fn is not None:
            return "function"
        else:
            return "simple"
    
    def _execute_input_output_mode(self, inputs: List[Any], outputs: List[Any],
                                  code: str, language: str,
                                  timeout: Optional[int]) -> List[int]:
        """
        Execute code with input/output validation.

        Mode 1: Test code against input/output pairs.
        Each test case has a 3-second timeout limit.
        """
        logger.info(f"Executing in input/output mode with {len(inputs)} test cases")

        results = []

        # Get container
        container = self.docker_manager.get_or_create_container()

        try:
            for i, (input_val, expected_output) in enumerate(zip(inputs, outputs)):
                try:
                    # Prepare test code
                    test_code = self._prepare_test_code(code, input_val, language)

                    # Execute with 3-second timeout per test case
                    actual_output = self._execute_code_in_container(
                        container, test_code, language, 3  # 3-second timeout per test
                    )

                    # Compare results
                    if self._compare_outputs(actual_output, expected_output):
                        results.append(1)
                        logger.debug(f"Test case {i+1}: PASS")
                    else:
                        results.append(0)
                        logger.debug(f"Test case {i+1}: FAIL - Expected: {expected_output}, Got: {actual_output}")

                except Exception as e:
                    logger.warning(f"Test case {i+1} failed with error: {e}")
                    # If any test case times out or fails, return all zeros
                    if "timeout" in str(e).lower() or "timed out" in str(e).lower():
                        logger.warning(f"Timeout detected in test case {i+1}, returning all zeros")
                        return [0] * len(inputs)
                    results.append(0)

        finally:
            # Keep container running (don't clean up until rm_docker() is called)
            pass

        return results
    
    def _execute_function_comparison_mode(self, answer_fn: str, code: str, 
                                        language: str, timeout: Optional[int]) -> List[int]:
        """
        Execute code with function comparison.
        
        Mode 2: Compare function outputs.
        """
        logger.info("Executing in function comparison mode")
        
        # Get container
        container = self.docker_manager.get_or_create_container()
        
        try:
            # Extract function names
            answer_func_name = self._extract_function_name(answer_fn, language)
            code_func_name = self._extract_function_name(code, language)
            
            if not answer_func_name or not code_func_name:
                logger.warning("Could not extract function names")
                return [0]
            
            # Execute answer function
            answer_result = self._execute_function_in_container(
                container, answer_fn, answer_func_name, language, timeout
            )
            
            # Execute test function
            code_result = self._execute_function_in_container(
                container, code, code_func_name, language, timeout
            )
            
            # Compare results
            if self._compare_outputs(answer_result, code_result):
                return [1]
            else:
                logger.debug(f"Function comparison failed - Answer: {answer_result}, Code: {code_result}")
                return [0]
                
        except Exception as e:
            logger.error(f"Function comparison failed: {e}")
            return [0]
        
        finally:
            # Keep container running (don't clean up until rm_docker() is called)
            pass
    
    def _execute_simple_mode(self, code: str, language: str, 
                           timeout: Optional[int]) -> List[int]:
        """
        Execute code in simple mode.
        
        Mode 3: Simple execution without comparison.
        """
        logger.info("Executing in simple mode")
        
        container = self.docker_manager.get_or_create_container()
        
        try:
            result = self._execute_code_in_container(container, code, language, timeout)
            # If execution succeeds without error, return success
            return [1]
            
        except Exception as e:
            logger.error(f"Simple execution failed: {e}")
            return [0]
        
        finally:
            # Keep container running (don't clean up until rm_docker() is called)
            pass
    
    def _prepare_test_code(self, code: str, input_val: Any, language: str) -> str:
        """Prepare code with input value for testing."""
        if language.lower() == "python":
            # For Python, we assume the code defines a function and we call it with input
            test_code = f"""
{code}

# Test execution
import sys
import inspect

try:
    # Find all user-defined functions
    functions = []
    for name, obj in globals().items():
        if (inspect.isfunction(obj) and
            not name.startswith('_') and
            name not in ['inspect', 'sys']):
            functions.append(name)

    if functions:
        func_name = functions[0]  # Use first function found
        func = globals()[func_name]

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
            return test_code
        else:
            # For other languages, basic execution
            return code
    
    def _execute_code_in_container(self, container, code: str, language: str, 
                                  timeout: Optional[int]) -> str:
        """Execute code in Docker container and return output."""
        # Sanitize code
        sanitized_code = sanitize_code(code, language)
        
        # Prepare file
        file_path, prepared_code = language_manager.prepare_code_file(
            sanitized_code, language
        )
        
        # Copy code to container
        self.docker_manager.copy_to_container(container, prepared_code, file_path)
        
        # Get execution command
        command = language_manager.get_execution_command(file_path, language)
        
        # Set timeout
        if timeout is None:
            timeout = language_manager.get_timeout(language)
        
        # Execute code
        exit_code, stdout, stderr = self.docker_manager.execute_in_container(
            container, command, timeout
        )
        
        if exit_code != 0:
            error_msg = stderr.strip() if stderr else "Unknown execution error"
            raise ExecutionError(f"Code execution failed: {error_msg}")
        
        return stdout.strip()
    
    def _execute_function_in_container(self, container, code: str, function_name: str,
                                     language: str, timeout: Optional[int]) -> str:
        """Execute specific function in container."""
        # Prepare code with function call
        file_path, prepared_code = language_manager.prepare_code_file(
            code, language, function_name
        )
        
        # Copy and execute
        self.docker_manager.copy_to_container(container, prepared_code, file_path)
        command = language_manager.get_execution_command(file_path, language)
        
        if timeout is None:
            timeout = language_manager.get_timeout(language)
        
        exit_code, stdout, stderr = self.docker_manager.execute_in_container(
            container, command, timeout
        )
        
        if exit_code != 0:
            error_msg = stderr.strip() if stderr else "Unknown execution error"
            raise ExecutionError(f"Function execution failed: {error_msg}")
        
        return stdout.strip()
    
    def _extract_function_name(self, code: str, language: str) -> Optional[str]:
        """Extract function name from code."""
        if language.lower() == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        return node.name
            except:
                pass
        elif language.lower() in ["javascript", "js"]:
            import re
            # Look for function declarations
            match = re.search(r'function\s+(\w+)\s*\(', code)
            if match:
                return match.group(1)
        
        return None
    
    def _compare_outputs(self, actual: str, expected: Any) -> bool:
        """Compare actual output with expected output using robust comparison."""
        try:
            return compare_values(actual, expected)
        except Exception as e:
            logger.warning(f"Output comparison failed: {e}")
            # Fallback to string comparison
            return str(actual).strip() == str(expected).strip()

    def _compare_function_outputs(self, answer_output: str, code_output: str) -> bool:
        """Compare outputs from two functions, handling print statements."""
        try:
            logger.debug(f"Comparing outputs: '{answer_output}' vs '{code_output}'")

            # Normalize outputs by stripping whitespace (but preserve case!)
            answer_normalized = str(answer_output).strip()
            code_normalized = str(code_output).strip()

            logger.debug(f"Normalized: '{answer_normalized}' vs '{code_normalized}'")

            # Direct string comparison for print outputs (case-sensitive)
            if answer_normalized == code_normalized:
                logger.debug("Direct string comparison: MATCH")
                return True

            logger.debug("Direct string comparison: NO MATCH")

            # Try to parse as numbers if they look numeric
            try:
                answer_num = float(answer_normalized)
                code_num = float(code_normalized)
                numeric_match = abs(answer_num - code_num) < 1e-9
                logger.debug(f"Numeric comparison: {numeric_match}")
                return numeric_match
            except (ValueError, TypeError):
                logger.debug("Not numeric values")
                pass

            # Try to compare as structured data (lists, dicts, etc.)
            try:
                import ast
                answer_parsed = ast.literal_eval(answer_output.strip())
                code_parsed = ast.literal_eval(code_output.strip())
                structured_match = answer_parsed == code_parsed
                logger.debug(f"Structured data comparison: {structured_match}")
                return structured_match
            except (ValueError, SyntaxError):
                logger.debug("Not structured data")
                pass

            logger.debug("All comparisons failed - returning False")
            return False

        except Exception as e:
            logger.warning(f"Function output comparison failed: {e}")
            return False

    def _execute_input_output_mode_docker(self, inputs: List[Any], outputs: List[Any],
                                         code: str, language: str,
                                         timeout: Optional[int]) -> List[int]:
        """Execute code with input/output validation using Docker subprocess."""
        results = []

        print(f"[INFO] Executing {len(inputs)} test cases using Docker {language}")

        for i, (input_val, expected_output) in enumerate(zip(inputs, outputs)):
            try:
                # Execute code with input using Docker subprocess
                actual_output = self.docker_subprocess_executor.execute_code(
                    code, language, input_val, timeout
                )

                # Compare outputs
                if self._compare_outputs(actual_output, expected_output):
                    results.append(1)
                    logger.debug(f"Test case {i+1} passed")
                else:
                    results.append(0)
                    logger.debug(f"Test case {i+1} failed - Expected: {expected_output}, Got: {actual_output}")

            except Exception as e:
                results.append(0)
                logger.error(f"Test case {i+1} failed with error: {e}")

        return results

    def _execute_function_comparison_mode_docker(self, answer_fn: str, code: str,
                                               language: str, timeout: Optional[int]) -> List[int]:
        """Execute function comparison mode using Docker subprocess."""
        try:
            print(f"[INFO] Executing function comparison using Docker {language}")

            # Prepare function code with automatic function calls
            answer_fn_with_call = self._add_function_call_if_needed(answer_fn, language)
            code_with_call = self._add_function_call_if_needed(code, language)

            # Execute both functions and compare their outputs
            answer_output = self.docker_subprocess_executor.execute_code(answer_fn_with_call, language, None, timeout)
            code_output = self.docker_subprocess_executor.execute_code(code_with_call, language, None, timeout)

            # Debug output
            logger.debug(f"Function comparison - Answer: '{answer_output}', Code: '{code_output}'")

            # Compare the outputs (including print statements)
            comparison_result = self._compare_function_outputs(answer_output, code_output)
            logger.debug(f"Comparison result: {comparison_result}")

            if comparison_result:
                return [1]
            else:
                logger.debug(f"Function comparison failed - Answer: {answer_output}, Code: {code_output}")
                return [0]

        except Exception as e:
            logger.error(f"Function comparison failed: {e}")
            return [0]

    def _add_function_call_if_needed(self, code: str, language: str) -> str:
        """Add function call if the code only contains function definition."""
        if language.lower() == "python":
            # Check if code already has function calls
            lines = code.strip().split('\n')
            has_function_call = False
            function_name = None

            # Find function definition and check for calls
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('def ') and '(' in stripped:
                    # Extract function name
                    func_def = stripped[4:].split('(')[0].strip()
                    if function_name is None:
                        function_name = func_def
                elif function_name and (stripped == f"{function_name}()" or
                                      stripped.startswith(f"{function_name}(")):
                    has_function_call = True
                    break

            # If no function call found, add one
            if function_name and not has_function_call:
                return f"{code}\n{function_name}()"

        return code

    def _execute_simple_mode_docker(self, code: str, language: str,
                                  timeout: Optional[int]) -> List[int]:
        """Execute simple mode using Docker subprocess."""
        try:
            print(f"[INFO] Executing code using Docker {language}")

            # Execute code without input
            self.docker_subprocess_executor.execute_code(code, language, None, timeout)
            return [1]

        except Exception as e:
            logger.error(f"Simple execution failed: {e}")
            return [0]


# Global executor instance
_executor: Optional[CodeExecutor] = None


def get_executor() -> CodeExecutor:
    """Get global executor instance."""
    global _executor
    if _executor is None:
        _executor = CodeExecutor()
    return _executor


def execute(inputs: Optional[List[Any]] = None,
           outputs: Optional[List[Any]] = None,
           code: Optional[str] = None,
           answer_fn: Optional[str] = None,
           language: str = "python",
           timeout: Optional[int] = None,
           mode: Optional[str] = None) -> List[int]:
    """
    Execute code snippets in isolated Docker environments.

    Args:
        inputs: List of input values for testing
        outputs: List of expected output values
        code: Code to execute
        answer_fn: Reference function code for comparison
        language: Programming language (default: "python")
        timeout: Execution timeout in seconds
        mode: Execution mode ("answer" for input/output validation,
              "function" for function comparison, None for auto-detection)

    Returns:
        List of integers (0 or 1) indicating pass/fail for each test case

    Examples:
        # Method 1: Input/Output validation (explicit mode)
        result = execute(mode="answer", inputs=[0, 1, 2], outputs=[1, 2, 3],
                        code="def add_one(x): return x + 1")

        # Method 2: Function comparison (explicit mode)
        result = execute(mode="function", answer_fn="def hello(): return 'world'",
                        code="def hello(): return 'world'")

        # Backward compatibility (auto-detection)
        result = execute(inputs=[1, 2], outputs=[2, 4], code="def double(x): return x * 2")
    """
    executor = get_executor()
    return executor.execute(inputs, outputs, code, answer_fn, language, timeout, mode)


def rm_docker() -> None:
    """Remove all Docker containers and cleanup resources."""
    try:
        docker_manager = get_docker_manager()
        docker_manager.cleanup_all_containers()

        # Also cleanup Docker subprocess executor and lazy installer
        cleanup_docker_subprocess_executor()
        cleanup_lazy_installer()

        # Reset global executor instance to ensure fresh start
        global _executor
        _executor = None

        logger.info("All Docker containers and subprocess resources cleaned up")
    except Exception as e:
        logger.error(f"Failed to cleanup resources: {e}")
        raise


def get_ready(*languages: str) -> None:
    """
    Pre-install language packages in the Docker container.

    Args:
        *languages: Variable number of language names to pre-install

    Example:
        get_ready("java", "javascript")  # Pre-install Java and JavaScript
        get_ready("python", "cpp", "go")  # Pre-install multiple languages
    """
    try:
        lazy_installer = get_lazy_installer()
        lazy_installer.pre_install_languages(list(languages))
        logger.info(f"Pre-installed languages: {', '.join(languages)}")
    except Exception as e:
        logger.error(f"Failed to pre-install languages: {e}")
        raise
