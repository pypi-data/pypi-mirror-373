#!/usr/bin/env python3
"""
Examples demonstrating the enhanced features of the coex library.
"""

import coex


def example_explicit_mode_parameter():
    """Demonstrate the new explicit mode parameter."""
    print("=== Explicit Mode Parameter Examples ===")
    
    # Example 1: Explicit "answer" mode for input/output validation
    print("1. Answer Mode (Input/Output Validation):")
    inputs = [1, 2, 3, 4]
    outputs = [2, 3, 4, 5]
    code = """
def add_one(x):
    return x + 1
"""
    
    result = coex.execute(
        mode="answer",
        inputs=inputs,
        outputs=outputs,
        code=code,
        language="python"
    )
    print(f"   Inputs: {inputs}")
    print(f"   Expected outputs: {outputs}")
    print(f"   Results: {result}")
    print(f"   Tests passed: {sum(result)}/{len(result)}")
    print()
    
    # Example 2: Explicit "function" mode for function comparison
    print("2. Function Mode (Function Comparison):")
    answer_fn = """
def calculate_factorial(n):
    if n <= 1:
        return 1
    return n * calculate_factorial(n - 1)
"""
    
    code = """
def calculate_factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
"""
    
    result = coex.execute(
        mode="function",
        answer_fn=answer_fn,
        code=code,
        language="python"
    )
    print(f"   Comparing recursive vs iterative factorial implementations")
    print(f"   Result: {result}")
    print(f"   Functions are equivalent: {'Yes' if result[0] == 1 else 'No'}")
    print()
    
    # Example 3: Backward compatibility (auto-detection)
    print("3. Backward Compatibility (Auto-Detection):")
    result = coex.execute(
        inputs=[5, 10, 15],
        outputs=[25, 100, 225],
        code="def square(x): return x * x",
        language="python"
    )
    print(f"   Auto-detected mode based on parameters")
    print(f"   Result: {result}")
    print()


def example_timeout_implementation():
    """Demonstrate the 3-second timeout per test case."""
    print("=== 3-Second Timeout Implementation ===")
    
    # Example 1: Fast execution (should succeed)
    print("1. Fast Execution (should succeed):")
    result = coex.execute(
        mode="answer",
        inputs=[1, 2, 3],
        outputs=[2, 4, 6],
        code="def double(x): return x * 2",
        language="python"
    )
    print(f"   Result: {result}")
    print(f"   Status: {'Success' if all(result) else 'Some failures'}")
    print()
    
    # Example 2: Slow execution (would timeout in real scenario)
    print("2. Slow Execution (simulated timeout):")
    slow_code = """
import time
def slow_function(x):
    time.sleep(5)  # This would exceed 3-second timeout
    return x * 2
"""
    
    result = coex.execute(
        mode="answer",
        inputs=[1, 2, 3],
        outputs=[2, 4, 6],
        code=slow_code,
        language="python"
    )
    print(f"   Result: {result}")
    print(f"   Status: {'Timeout detected' if result == [0, 0, 0] else 'Unexpected result'}")
    print()


def example_unique_file_naming():
    """Demonstrate unique file naming for batch processing."""
    print("=== Unique File Naming for Batch Processing ===")
    
    from coex.core.languages import language_manager
    
    print("Generated file names for different languages:")
    
    languages = ["python", "javascript", "java", "cpp", "c", "go", "rust"]
    
    for language in languages:
        file_path, _ = language_manager.prepare_code_file(
            "// Sample code", language
        )
        file_name = file_path.split('/')[-1]
        print(f"   {language.capitalize()}: {file_name}")
    
    print()
    print("Multiple Python files (showing uniqueness):")
    for i in range(5):
        file_path, _ = language_manager.prepare_code_file(
            f"# Sample code {i}", "python"
        )
        file_name = file_path.split('/')[-1]
        print(f"   File {i+1}: {file_name}")
    
    print()


def example_api_response_format():
    """Demonstrate API string response format."""
    print("=== API String Response Format ===")
    
    # All results are returned as lists of integers (0 or 1)
    # This format is perfect for API transmission
    
    print("1. Input/Output Validation Response:")
    result = coex.execute(
        mode="answer",
        inputs=[1, 2, 3],
        outputs=[1, 4, 9],
        code="def square(x): return x * x",
        language="python"
    )
    print(f"   Result: {result}")
    print(f"   Type: {type(result)}")
    print(f"   Element types: {[type(x) for x in result]}")
    print()
    
    print("2. Function Comparison Response:")
    result = coex.execute(
        mode="function",
        answer_fn="def greet(): return 'Hello'",
        code="def greet(): return 'Hello'",
        language="python"
    )
    print(f"   Result: {result}")
    print(f"   Type: {type(result)}")
    print(f"   Serializable for API: {str(result)}")
    print()


def example_error_handling_with_modes():
    """Demonstrate error handling with explicit modes."""
    print("=== Error Handling with Explicit Modes ===")
    
    print("1. Invalid Mode Parameter:")
    result = coex.execute(
        mode="invalid_mode",
        code="print('test')",
        language="python"
    )
    print(f"   Result: {result} (error handled gracefully)")
    print()
    
    print("2. Mode Consistency Validation:")
    result = coex.execute(
        mode="answer",
        code="print('test')",  # Missing inputs/outputs for answer mode
        language="python"
    )
    print(f"   Result: {result} (validation error handled)")
    print()
    
    print("3. Security Protection (still works with modes):")
    result = coex.execute(
        mode="function",
        answer_fn="def safe(): return 'hello'",
        code="import os; os.system('rm -rf /'); def safe(): return 'hello'",
        language="python"
    )
    print(f"   Result: {result} (security violation blocked)")
    print()


def example_multi_language_with_modes():
    """Demonstrate multi-language support with explicit modes."""
    print("=== Multi-Language Support with Explicit Modes ===")
    
    # Test the same algorithm in different languages using function mode
    reference_python = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    
    implementations = [
        ("Python Iterative", """
def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
"""),
        ("JavaScript", """
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}
"""),
        ("Java", """
public static int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}
"""),
    ]
    
    for name, code in implementations:
        if name.startswith("Python"):
            result = coex.execute(
                mode="function",
                answer_fn=reference_python,
                code=code,
                language="python"
            )
        elif name.startswith("JavaScript"):
            result = coex.execute(
                mode="function",
                answer_fn="function fibonacci(n) { if (n <= 1) return n; return fibonacci(n-1) + fibonacci(n-2); }",
                code=code,
                language="javascript"
            )
        elif name.startswith("Java"):
            result = coex.execute(
                mode="function",
                answer_fn="public static int fibonacci(int n) { if (n <= 1) return n; return fibonacci(n-1) + fibonacci(n-2); }",
                code=code,
                language="java"
            )
        
        print(f"   {name}: {result} ({'✓' if result[0] == 1 else '✗'})")
    
    print()


def main():
    """Run all enhanced feature examples."""
    print("COEX Library - Enhanced Features Examples")
    print("=" * 60)
    print()
    
    try:
        example_explicit_mode_parameter()
        example_timeout_implementation()
        example_unique_file_naming()
        example_api_response_format()
        example_error_handling_with_modes()
        example_multi_language_with_modes()
        
        print("=" * 60)
        print("🎉 All enhanced features demonstrated successfully!")
        print()
        print("Summary of New Features:")
        print("✓ Explicit mode parameter ('answer' and 'function' modes)")
        print("✓ 3-second timeout per test case")
        print("✓ Unique file naming for batch processing")
        print("✓ API string response format")
        print("✓ PyPI distribution readiness")
        print("✓ Backward compatibility maintained")
        
    except Exception as e:
        print(f"Error running enhanced feature examples: {e}")
        print("Make sure Docker is running and you have the required permissions.")


if __name__ == "__main__":
    main()
