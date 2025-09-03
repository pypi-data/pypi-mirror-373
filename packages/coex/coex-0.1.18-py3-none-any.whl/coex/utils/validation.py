"""
Input validation utilities for the coex library.
"""

import re
import json
from typing import Any, List, Optional, Union, Dict
from ..exceptions import ValidationError


def validate_inputs_outputs(inputs: Optional[List[Any]], outputs: Optional[List[Any]]) -> None:
    """
    Validate inputs and outputs lists.
    
    Args:
        inputs: List of input values
        outputs: List of expected output values
        
    Raises:
        ValidationError: If validation fails
    """
    if inputs is None and outputs is None:
        return
    
    if inputs is None or outputs is None:
        raise ValidationError("Both inputs and outputs must be provided together")
    
    if not isinstance(inputs, list) or not isinstance(outputs, list):
        raise ValidationError("Inputs and outputs must be lists")
    
    if len(inputs) != len(outputs):
        raise ValidationError(f"Inputs length ({len(inputs)}) must match outputs length ({len(outputs)})")
    
    if len(inputs) == 0:
        raise ValidationError("Inputs and outputs cannot be empty")


def validate_code(code: Optional[str]) -> None:
    """
    Validate code string.
    
    Args:
        code: Code string to validate
        
    Raises:
        ValidationError: If validation fails
    """
    if code is None:
        raise ValidationError("Code cannot be None")
    
    if not isinstance(code, str):
        raise ValidationError("Code must be a string")
    
    if not code.strip():
        raise ValidationError("Code cannot be empty")


def validate_language(language: str) -> str:
    """
    Validate and normalize language string.
    
    Args:
        language: Programming language name
        
    Returns:
        Normalized language name
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(language, str):
        raise ValidationError("Language must be a string")
    
    language = language.strip().lower()
    
    if not language:
        raise ValidationError("Language cannot be empty")
    
    # Normalize common language aliases
    language_aliases = {
        "js": "javascript",
        "c++": "cpp",
        "cxx": "cpp",
        "py": "python",
        "rs": "rust",
    }
    
    return language_aliases.get(language, language)


def validate_timeout(timeout: Optional[int]) -> Optional[int]:
    """
    Validate timeout value.
    
    Args:
        timeout: Timeout in seconds
        
    Returns:
        Validated timeout value
        
    Raises:
        ValidationError: If validation fails
    """
    if timeout is None:
        return None
    
    if not isinstance(timeout, int):
        raise ValidationError("Timeout must be an integer")
    
    if timeout <= 0:
        raise ValidationError("Timeout must be positive")
    
    if timeout > 300:  # 5 minutes max
        raise ValidationError("Timeout cannot exceed 300 seconds")
    
    return timeout


def validate_function_code(code: str, language: str = "python") -> str:
    """
    Validate that code contains a function definition.
    
    Args:
        code: Code string
        language: Programming language
        
    Returns:
        Validated code
        
    Raises:
        ValidationError: If no function is found
    """
    if language.lower() == "python":
        if "def " not in code:
            raise ValidationError("Python code must contain a function definition (def)")
    elif language.lower() in ["javascript", "js"]:
        if "function " not in code and "=>" not in code:
            raise ValidationError("JavaScript code must contain a function definition")
    elif language.lower() == "java":
        if "public " not in code and "private " not in code and "protected " not in code:
            raise ValidationError("Java code must contain a method definition")
    
    return code


def sanitize_input_value(value: Any) -> Any:
    """
    Sanitize input value to ensure it's safe for execution.
    
    Args:
        value: Input value to sanitize
        
    Returns:
        Sanitized value
    """
    # Convert to JSON and back to ensure serializable
    try:
        json_str = json.dumps(value)
        return json.loads(json_str)
    except (TypeError, ValueError):
        # If not JSON serializable, convert to string
        return str(value)


def validate_execution_mode(inputs: Optional[List[Any]], outputs: Optional[List[Any]], 
                          code: Optional[str], answer_fn: Optional[str]) -> str:
    """
    Validate execution parameters and determine execution mode.
    
    Args:
        inputs: Input values
        outputs: Expected outputs
        code: Code to execute
        answer_fn: Reference function code
        
    Returns:
        Execution mode: "input_output", "function_comparison", or "simple"
        
    Raises:
        ValidationError: If parameters are invalid
    """
    if not code and not answer_fn:
        raise ValidationError("Either 'code' or 'answer_fn' must be provided")
    
    if inputs is not None and outputs is not None:
        if not code:
            raise ValidationError("Code must be provided for input/output mode")
        validate_inputs_outputs(inputs, outputs)
        return "input_output"
    
    elif answer_fn is not None:
        if not code:
            raise ValidationError("Code must be provided for function comparison mode")
        validate_code(answer_fn)
        validate_function_code(answer_fn)
        validate_function_code(code)
        return "function_comparison"
    
    elif code is not None:
        validate_code(code)
        return "simple"
    
    else:
        raise ValidationError("Invalid parameter combination")


def normalize_output(output: str, expected_type: type = str) -> Any:
    """
    Normalize output string to expected type.
    
    Args:
        output: Output string from code execution
        expected_type: Expected output type
        
    Returns:
        Normalized output value
    """
    output = output.strip()
    
    if expected_type == int:
        try:
            return int(float(output))
        except ValueError:
            return output
    
    elif expected_type == float:
        try:
            return float(output)
        except ValueError:
            return output
    
    elif expected_type == bool:
        if output.lower() in ['true', '1', 'yes']:
            return True
        elif output.lower() in ['false', '0', 'no']:
            return False
        else:
            return output
    
    elif expected_type == list or expected_type == dict:
        try:
            return json.loads(output)
        except (json.JSONDecodeError, ValueError):
            return output
    
    else:
        return output


def extract_error_message(stderr: str, language: str = "python") -> str:
    """
    Extract meaningful error message from stderr.
    
    Args:
        stderr: Standard error output
        language: Programming language
        
    Returns:
        Cleaned error message
    """
    if not stderr:
        return "Unknown error"
    
    lines = stderr.strip().split('\n')
    
    if language.lower() == "python":
        # Find the last line that looks like an error
        for line in reversed(lines):
            if any(error_type in line for error_type in 
                  ['Error:', 'Exception:', 'Traceback']):
                return line.strip()
        return lines[-1].strip() if lines else "Unknown error"
    
    elif language.lower() in ["javascript", "js"]:
        # Look for error patterns
        for line in lines:
            if 'Error:' in line or 'TypeError:' in line or 'ReferenceError:' in line:
                return line.strip()
        return lines[-1].strip() if lines else "Unknown error"
    
    elif language.lower() == "java":
        # Look for Java exception patterns
        for line in lines:
            if 'Exception' in line or 'Error' in line:
                return line.strip()
        return lines[-1].strip() if lines else "Unknown error"
    
    else:
        return lines[-1].strip() if lines else "Unknown error"


def is_numeric_output(output: str) -> bool:
    """
    Check if output string represents a numeric value.
    
    Args:
        output: Output string
        
    Returns:
        True if output is numeric
    """
    try:
        float(output.strip())
        return True
    except ValueError:
        return False


def compare_values(actual: Any, expected: Any, tolerance: float = 1e-9) -> bool:
    """
    Compare two values with appropriate tolerance for floating point numbers.
    
    Args:
        actual: Actual value
        expected: Expected value
        tolerance: Tolerance for floating point comparison
        
    Returns:
        True if values are considered equal
    """
    if type(actual) != type(expected):
        # Try to convert types
        try:
            if isinstance(expected, (int, float)):
                actual = float(actual)
            elif isinstance(expected, str):
                actual = str(actual)
            elif isinstance(expected, bool):
                actual = bool(actual)
        except (ValueError, TypeError):
            return False
    
    if isinstance(actual, float) and isinstance(expected, float):
        return abs(actual - expected) < tolerance
    elif isinstance(actual, str) and isinstance(expected, str):
        return actual.strip() == expected.strip()
    else:
        return actual == expected
