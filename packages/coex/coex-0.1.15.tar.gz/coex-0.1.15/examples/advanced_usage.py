#!/usr/bin/env python3
"""
Advanced usage examples for the coex library.
"""

import coex
from coex.config.settings import settings
from coex.exceptions import SecurityError, ValidationError, ExecutionError, DockerError


def example_custom_configuration():
    """Example: Custom configuration settings."""
    print("=== Custom Configuration Example ===")
    
    # Show current settings
    print("Current settings:")
    print(f"Execution timeout: {settings.execution['timeout']} seconds")
    print(f"Docker memory limit: {settings.docker['memory_limit']}")
    print(f"Security enabled: {settings.security['enable_security_checks']}")
    print()
    
    # Modify settings
    print("Modifying settings...")
    original_timeout = settings.execution["timeout"]
    settings.set("execution.timeout", 60)  # Increase timeout to 60 seconds
    settings.set("docker.memory_limit", "1g")  # Increase memory limit
    
    print(f"New execution timeout: {settings.get('execution.timeout')} seconds")
    print(f"New memory limit: {settings.get('docker.memory_limit')}")
    
    # Test with new settings
    code = """
import time
print("Starting long computation...")
time.sleep(2)  # Simulate long computation
print("Computation completed!")
"""
    
    result = coex.execute(code=code, language="python", timeout=60)
    print(f"Execution result: {result}")
    
    # Restore original settings
    settings.set("execution.timeout", original_timeout)
    print("Settings restored to original values")
    print()


def example_comprehensive_testing():
    """Example: Comprehensive testing of a complex function."""
    print("=== Comprehensive Testing Example ===")
    
    # Test a more complex function with edge cases
    inputs = [
        0,      # Edge case: zero
        1,      # Edge case: one
        2,      # Small number
        10,     # Medium number
        -1,     # Negative number
        -5,     # Negative number
        100,    # Large number
    ]
    
    # Expected outputs for fibonacci function
    expected_fibonacci = [0, 1, 1, 55, 1, 5, 354224848179261915075]
    
    fibonacci_code = """
def fibonacci(n):
    if n < 0:
        # For negative numbers, use the formula F(-n) = (-1)^(n+1) * F(n)
        return (-1) ** (-n + 1) * fibonacci(-n)
    elif n <= 1:
        return n
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
"""
    
    print(f"Testing Fibonacci function with inputs: {inputs}")
    print(f"Expected outputs: {expected_fibonacci}")
    print(f"Code:\n{fibonacci_code}")
    
    result = coex.execute(
        inputs=inputs, 
        outputs=expected_fibonacci, 
        code=fibonacci_code, 
        language="python"
    )
    
    print(f"Results: {result}")
    
    # Analyze results
    passed = sum(result)
    total = len(result)
    print(f"Test summary: {passed}/{total} tests passed")
    
    for i, (inp, expected, passed) in enumerate(zip(inputs, expected_fibonacci, result)):
        status = "PASS" if passed else "FAIL"
        print(f"  Test {i+1}: fibonacci({inp}) -> expected {expected} [{status}]")
    
    print()


def example_algorithm_comparison():
    """Example: Comparing different algorithm implementations."""
    print("=== Algorithm Comparison Example ===")
    
    # Compare sorting algorithms
    reference_sort = """
def sort_array(arr):
    # Built-in sort (reference implementation)
    return sorted(arr)
"""
    
    bubble_sort = """
def sort_array(arr):
    # Bubble sort implementation
    arr = arr.copy()
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
"""
    
    quick_sort = """
def sort_array(arr):
    # Quick sort implementation
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return sort_array(left) + middle + sort_array(right)
"""
    
    algorithms = [
        ("Bubble Sort", bubble_sort),
        ("Quick Sort", quick_sort)
    ]
    
    for name, algorithm_code in algorithms:
        print(f"Testing {name}:")
        result = coex.execute(
            answer_fn=reference_sort,
            code=algorithm_code,
            language="python"
        )
        
        status = "EQUIVALENT" if result[0] == 1 else "DIFFERENT"
        print(f"Comparison result: {status}")
        print("-" * 40)
    
    print()


def example_multi_language_comparison():
    """Example: Comparing implementations across languages."""
    print("=== Multi-Language Comparison Example ===")
    
    # Implement the same function in different languages
    implementations = [
        ("Python", """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(5))
"""),
        ("JavaScript", """
function factorial(n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

console.log(factorial(5));
"""),
        ("Java", """
public class Factorial {
    public static int factorial(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }
    
    public static void main(String[] args) {
        System.out.println(factorial(5));
    }
}
"""),
        ("C++", """
#include <iostream>

int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main() {
    std::cout << factorial(5) << std::endl;
    return 0;
}
""")
    ]
    
    results = {}
    
    for language, code in implementations:
        print(f"Testing {language}:")
        try:
            result = coex.execute(code=code, language=language.lower())
            results[language] = result[0]
            status = "SUCCESS" if result[0] == 1 else "FAILED"
            print(f"Result: {status}")
        except Exception as e:
            results[language] = 0
            print(f"Error: {e}")
        print("-" * 30)
    
    print("Summary:")
    for language, success in results.items():
        print(f"  {language}: {'✓' if success else '✗'}")
    
    print()


def example_error_recovery():
    """Example: Error recovery and handling."""
    print("=== Error Recovery Example ===")
    
    test_cases = [
        {
            "name": "Valid Code",
            "code": "def test(): return 42",
            "should_succeed": True
        },
        {
            "name": "Syntax Error",
            "code": "def test( invalid syntax",
            "should_succeed": False
        },
        {
            "name": "Runtime Error",
            "code": "def test(): return 1/0",
            "should_succeed": False
        },
        {
            "name": "Security Violation",
            "code": "import os; os.system('rm -rf /')",
            "should_succeed": False
        }
    ]
    
    for test_case in test_cases:
        print(f"Testing: {test_case['name']}")
        
        try:
            result = coex.execute(code=test_case["code"], language="python")
            success = result[0] == 1
            expected = test_case["should_succeed"]
            
            if success == expected:
                print(f"✓ Expected behavior: {'Success' if success else 'Failure'}")
            else:
                print(f"✗ Unexpected behavior: Got {'Success' if success else 'Failure'}, expected {'Success' if expected else 'Failure'}")
                
        except SecurityError as e:
            print(f"✓ Security error caught: {e}")
        except ValidationError as e:
            print(f"✓ Validation error caught: {e}")
        except ExecutionError as e:
            print(f"✓ Execution error caught: {e}")
        except DockerError as e:
            print(f"✗ Docker error: {e}")
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
        
        print("-" * 40)
    
    print()


def example_performance_optimization():
    """Example: Performance optimization techniques."""
    print("=== Performance Optimization Example ===")
    
    import time
    
    # Test container reuse performance
    code = "def test(): return 42"
    
    print("Testing container reuse performance...")
    
    # First execution (container creation)
    start_time = time.time()
    result1 = coex.execute(code=code, language="python")
    first_execution_time = time.time() - start_time
    
    # Second execution (container reuse)
    start_time = time.time()
    result2 = coex.execute(code=code, language="python")
    second_execution_time = time.time() - start_time
    
    print(f"First execution (with container creation): {first_execution_time:.3f}s")
    print(f"Second execution (container reuse): {second_execution_time:.3f}s")
    
    if second_execution_time < first_execution_time:
        speedup = first_execution_time / second_execution_time
        print(f"Speedup from container reuse: {speedup:.2f}x")
    
    # Test batch processing
    print("\nTesting batch processing...")
    
    inputs = list(range(20))
    outputs = [x * 2 for x in inputs]
    batch_code = "def double(x): return x * 2"
    
    start_time = time.time()
    batch_result = coex.execute(
        inputs=inputs, 
        outputs=outputs, 
        code=batch_code, 
        language="python"
    )
    batch_time = time.time() - start_time
    
    print(f"Batch processing {len(inputs)} tests: {batch_time:.3f}s")
    print(f"Average time per test: {batch_time/len(inputs)*1000:.2f}ms")
    print(f"Tests passed: {sum(batch_result)}/{len(batch_result)}")
    
    print()


def example_custom_timeout_handling():
    """Example: Custom timeout handling."""
    print("=== Custom Timeout Handling Example ===")
    
    # Test with different timeout values
    timeout_tests = [
        {
            "name": "Quick execution",
            "code": "print('Hello, World!')",
            "timeout": 5,
            "should_succeed": True
        },
        {
            "name": "Medium execution",
            "code": "import time; time.sleep(2); print('Done')",
            "timeout": 5,
            "should_succeed": True
        },
        {
            "name": "Long execution with sufficient timeout",
            "code": "import time; time.sleep(3); print('Done')",
            "timeout": 10,
            "should_succeed": True
        },
        {
            "name": "Long execution with insufficient timeout",
            "code": "import time; time.sleep(10); print('Done')",
            "timeout": 2,
            "should_succeed": False
        }
    ]
    
    for test in timeout_tests:
        print(f"Testing: {test['name']}")
        print(f"Timeout: {test['timeout']}s")
        
        start_time = time.time()
        result = coex.execute(
            code=test["code"], 
            language="python", 
            timeout=test["timeout"]
        )
        execution_time = time.time() - start_time
        
        success = result[0] == 1
        expected = test["should_succeed"]
        
        print(f"Execution time: {execution_time:.2f}s")
        print(f"Result: {'Success' if success else 'Failure'}")
        print(f"Expected: {'Success' if expected else 'Failure'}")
        print(f"Status: {'✓' if success == expected else '✗'}")
        print("-" * 40)
    
    print()


def main():
    """Run all advanced examples."""
    print("COEX Library - Advanced Examples")
    print("=" * 50)
    print()
    
    try:
        example_custom_configuration()
        example_comprehensive_testing()
        example_algorithm_comparison()
        example_multi_language_comparison()
        example_error_recovery()
        example_performance_optimization()
        example_custom_timeout_handling()
        
        print("All advanced examples completed successfully!")
        
        # Final cleanup
        print("\nPerforming final cleanup...")
        coex.rm_docker()
        print("Cleanup completed!")
        
    except Exception as e:
        print(f"Error running advanced examples: {e}")
        print("Make sure Docker is running and you have the required permissions.")


if __name__ == "__main__":
    main()
