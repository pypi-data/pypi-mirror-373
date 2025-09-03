#!/usr/bin/env python3
"""
Basic usage examples for the coex library.
"""

import coex


def example_input_output_validation():
    """Example: Input/Output validation mode."""
    print("=== Input/Output Validation Example ===")
    
    # Test a simple addition function
    inputs = [1, 2, 3, 4, 5]
    outputs = [2, 3, 4, 5, 6]
    code = """
def add_one(x):
    return x + 1
"""
    
    print(f"Testing function with inputs: {inputs}")
    print(f"Expected outputs: {outputs}")
    print(f"Code:\n{code}")
    
    result = coex.execute(inputs=inputs, outputs=outputs, code=code, language="python")
    print(f"Results: {result}")
    print(f"Passed: {sum(result)}/{len(result)} tests")
    print()


def example_function_comparison():
    """Example: Function comparison mode."""
    print("=== Function Comparison Example ===")
    
    # Compare two implementations of factorial
    answer_fn = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
    
    code = """
def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
"""
    
    print("Comparing two factorial implementations:")
    print(f"Reference implementation:\n{answer_fn}")
    print(f"Test implementation:\n{code}")
    
    result = coex.execute(answer_fn=answer_fn, code=code, language="python")
    print(f"Result: {result}")
    print(f"Functions are equivalent: {'Yes' if result[0] == 1 else 'No'}")
    print()


def example_simple_execution():
    """Example: Simple execution mode."""
    print("=== Simple Execution Example ===")
    
    code = """
import math

def calculate_circle_area(radius):
    return math.pi * radius ** 2

# Test the function
radius = 5
area = calculate_circle_area(radius)
print(f"Area of circle with radius {radius}: {area:.2f}")
"""
    
    print(f"Code to execute:\n{code}")
    
    result = coex.execute(code=code, language="python")
    print(f"Execution result: {result}")
    print(f"Execution {'succeeded' if result[0] == 1 else 'failed'}")
    print()


def example_multi_language():
    """Example: Multi-language support."""
    print("=== Multi-Language Example ===")
    
    languages_and_code = [
        ("python", """
def greet(name):
    return f"Hello, {name} from Python!"

print(greet("World"))
"""),
        ("javascript", """
function greet(name) {
    return `Hello, ${name} from JavaScript!`;
}

console.log(greet("World"));
"""),
        ("java", """
public class Greeter {
    public static String greet(String name) {
        return "Hello, " + name + " from Java!";
    }
    
    public static void main(String[] args) {
        System.out.println(greet("World"));
    }
}
"""),
        ("cpp", """
#include <iostream>
#include <string>

std::string greet(const std::string& name) {
    return "Hello, " + name + " from C++!";
}

int main() {
    std::cout << greet("World") << std::endl;
    return 0;
}
""")
    ]
    
    for language, code in languages_and_code:
        print(f"Testing {language.upper()}:")
        print(f"Code:\n{code}")
        
        result = coex.execute(code=code, language=language)
        print(f"Result: {result}")
        print(f"Status: {'Success' if result[0] == 1 else 'Failed'}")
        print("-" * 50)


def example_security_protection():
    """Example: Security protection."""
    print("=== Security Protection Example ===")
    
    dangerous_codes = [
        ("File deletion", """
import os
os.system("rm -rf /important/files")
"""),
        ("Network access", """
import urllib.request
urllib.request.urlopen("http://malicious.com")
"""),
        ("Code evaluation", """
user_input = "malicious_code()"
eval(user_input)
"""),
        ("System access", """
import subprocess
subprocess.call(["sudo", "dangerous_command"])
""")
    ]
    
    for description, code in dangerous_codes:
        print(f"Testing: {description}")
        print(f"Code:\n{code}")
        
        result = coex.execute(code=code, language="python")
        print(f"Result: {result}")
        print(f"Security protection: {'Active' if result[0] == 0 else 'Failed'}")
        print("-" * 50)


def example_error_handling():
    """Example: Error handling."""
    print("=== Error Handling Example ===")
    
    error_scenarios = [
        ("Syntax Error", """
def broken_function(
    # Missing closing parenthesis and colon
"""),
        ("Runtime Error", """
def divide_by_zero():
    return 1 / 0

result = divide_by_zero()
"""),
        ("Import Error", """
import nonexistent_module
"""),
        ("Type Error", """
def add_numbers(a, b):
    return a + b

result = add_numbers("hello", 5)
""")
    ]
    
    for description, code in error_scenarios:
        print(f"Testing: {description}")
        print(f"Code:\n{code}")
        
        try:
            result = coex.execute(code=code, language="python")
            print(f"Result: {result}")
            print(f"Handled gracefully: {'Yes' if result[0] == 0 else 'No'}")
        except Exception as e:
            print(f"Exception caught: {type(e).__name__}: {e}")
        
        print("-" * 50)


def example_performance_testing():
    """Example: Performance testing with multiple test cases."""
    print("=== Performance Testing Example ===")
    
    # Test with many input/output pairs
    inputs = list(range(50))  # 0 to 49
    outputs = [x ** 2 for x in inputs]  # Square of each input
    
    code = """
def square(x):
    return x * x
"""
    
    print(f"Testing with {len(inputs)} test cases")
    print(f"Code:\n{code}")
    
    import time
    start_time = time.time()
    
    result = coex.execute(inputs=inputs, outputs=outputs, code=code, language="python")
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"Results: {sum(result)}/{len(result)} tests passed")
    print(f"Execution time: {execution_time:.2f} seconds")
    print(f"Average time per test: {execution_time/len(inputs)*1000:.2f} ms")
    print()


def example_cleanup():
    """Example: Docker cleanup."""
    print("=== Docker Cleanup Example ===")
    
    print("Cleaning up Docker containers...")
    coex.rm_docker()
    print("Cleanup completed!")
    print()


def main():
    """Run all examples."""
    print("COEX Library Examples")
    print("=" * 50)
    print()
    
    try:
        example_input_output_validation()
        example_function_comparison()
        example_simple_execution()
        example_multi_language()
        example_security_protection()
        example_error_handling()
        example_performance_testing()
        example_cleanup()
        
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure Docker is running and you have the required permissions.")


if __name__ == "__main__":
    main()
