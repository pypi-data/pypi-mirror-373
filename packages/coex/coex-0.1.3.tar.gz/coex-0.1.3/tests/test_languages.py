"""
Unit tests for the multi-language support module.
"""

import pytest
from coex.core.languages import (
    LanguageHandler, PythonHandler, JavaScriptHandler, JavaHandler,
    CppHandler, CHandler, GoHandler, RustHandler, LanguageManager, language_manager
)
from coex.exceptions import LanguageNotSupportedError


class TestLanguageHandler:
    """Test cases for base LanguageHandler class."""
    
    def test_language_handler_initialization(self):
        """Test LanguageHandler initialization with valid language."""
        handler = PythonHandler()
        assert handler.language == "python"
        assert handler.config is not None
    
    def test_language_handler_unsupported_language(self):
        """Test LanguageHandler initialization with unsupported language."""
        with pytest.raises(LanguageNotSupportedError):
            LanguageHandler("unsupported_language")
    
    def test_get_file_extension(self):
        """Test getting file extension for language."""
        handler = PythonHandler()
        assert handler.get_file_extension() == ".py"
    
    def test_get_timeout(self):
        """Test getting timeout for language."""
        handler = PythonHandler()
        timeout = handler.get_timeout()
        assert isinstance(timeout, int)
        assert timeout > 0


class TestPythonHandler:
    """Test cases for PythonHandler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = PythonHandler()
    
    def test_prepare_code_simple(self):
        """Test preparing simple Python code."""
        code = "def test(): return 42"
        result = self.handler.prepare_code(code)
        assert result == code
    
    def test_prepare_code_with_function_name(self):
        """Test preparing Python code with function wrapper."""
        code = "def test_func(): return 'hello'"
        result = self.handler.prepare_code(code, "test_func")
        
        assert "def test_func():" in result
        assert "result = test_func()" in result
        assert "print(result)" in result
        assert "__name__ == \"__main__\"" in result
    
    def test_get_execution_command(self):
        """Test getting Python execution command."""
        command = self.handler.get_execution_command("/path/to/file.py")
        assert command == ["python"]


class TestJavaScriptHandler:
    """Test cases for JavaScriptHandler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = JavaScriptHandler()
    
    def test_prepare_code_simple(self):
        """Test preparing simple JavaScript code."""
        code = "function test() { return 42; }"
        result = self.handler.prepare_code(code)
        assert result == code
    
    def test_prepare_code_with_function_name(self):
        """Test preparing JavaScript code with function wrapper."""
        code = "function testFunc() { return 'hello'; }"
        result = self.handler.prepare_code(code, "testFunc")
        
        assert "function testFunc()" in result
        assert "const result = testFunc()" in result
        assert "console.log(result)" in result
        assert "try {" in result and "} catch" in result
    
    def test_get_execution_command(self):
        """Test getting JavaScript execution command."""
        command = self.handler.get_execution_command("/path/to/file.js")
        assert command == ["node"]


class TestJavaHandler:
    """Test cases for JavaHandler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = JavaHandler()
    
    def test_prepare_code_with_existing_class(self):
        """Test preparing Java code that already has a class."""
        code = """
public class TestClass {
    public int test() { return 42; }
}
"""
        result = self.handler.prepare_code(code)
        assert "public class TestClass" in result
    
    def test_prepare_code_without_class(self):
        """Test preparing Java code without existing class."""
        code = "public int test() { return 42; }"
        result = self.handler.prepare_code(code, "test")
        
        assert "public class Main" in result
        assert "public static void main" in result
        assert "instance.test()" in result
    
    def test_get_execution_command(self):
        """Test getting Java execution command."""
        command = self.handler.get_execution_command("/path/to/TestClass.java")
        assert "javac" in command[2]
        assert "java TestClass" in command[2]


class TestCppHandler:
    """Test cases for CppHandler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = CppHandler()
    
    def test_prepare_code_with_main(self):
        """Test preparing C++ code that already has main function."""
        code = """
#include <iostream>
int main() {
    std::cout << "Hello" << std::endl;
    return 0;
}
"""
        result = self.handler.prepare_code(code)
        assert result == code
    
    def test_prepare_code_without_main(self):
        """Test preparing C++ code without main function."""
        code = "int add(int a, int b) { return a + b; }"
        result = self.handler.prepare_code(code, "add")
        
        assert "#include <iostream>" in result
        assert "int main()" in result
        assert "cout << add()" in result
    
    def test_get_execution_command(self):
        """Test getting C++ execution command."""
        command = self.handler.get_execution_command("/path/to/file.cpp")
        assert "g++" in command[2]
        assert "&&" in command[2]


class TestCHandler:
    """Test cases for CHandler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = CHandler()
    
    def test_prepare_code_without_main(self):
        """Test preparing C code without main function."""
        code = "int add(int a, int b) { return a + b; }"
        result = self.handler.prepare_code(code, "add")
        
        assert "#include <stdio.h>" in result
        assert "int main()" in result
        assert "printf" in result
    
    def test_get_execution_command(self):
        """Test getting C execution command."""
        command = self.handler.get_execution_command("/path/to/file.c")
        assert "gcc" in command[2]


class TestGoHandler:
    """Test cases for GoHandler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = GoHandler()
    
    def test_prepare_code_without_package(self):
        """Test preparing Go code without package declaration."""
        code = "func add(a, b int) int { return a + b }"
        result = self.handler.prepare_code(code, "add")
        
        assert "package main" in result
        assert "import \"fmt\"" in result
        assert "func main()" in result
        assert "fmt.Println(add())" in result


class TestRustHandler:
    """Test cases for RustHandler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = RustHandler()
    
    def test_prepare_code_without_main(self):
        """Test preparing Rust code without main function."""
        code = "fn add(a: i32, b: i32) -> i32 { a + b }"
        result = self.handler.prepare_code(code, "add")
        
        assert "fn main()" in result
        assert "println!" in result
        assert "add()" in result
    
    def test_get_execution_command(self):
        """Test getting Rust execution command."""
        command = self.handler.get_execution_command("/path/to/file.rs")
        assert "rustc" in command[2]


class TestLanguageManager:
    """Test cases for LanguageManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = LanguageManager()
    
    def test_get_handler_valid_language(self):
        """Test getting handler for valid language."""
        handler = self.manager.get_handler("python")
        assert isinstance(handler, PythonHandler)
        
        handler = self.manager.get_handler("javascript")
        assert isinstance(handler, JavaScriptHandler)
        
        handler = self.manager.get_handler("java")
        assert isinstance(handler, JavaHandler)
    
    def test_get_handler_language_aliases(self):
        """Test getting handler for language aliases."""
        js_handler = self.manager.get_handler("js")
        assert isinstance(js_handler, JavaScriptHandler)
        
        cpp_handler = self.manager.get_handler("c++")
        assert isinstance(cpp_handler, CppHandler)
        
        cpp_handler2 = self.manager.get_handler("cxx")
        assert isinstance(cpp_handler2, CppHandler)
    
    def test_get_handler_invalid_language(self):
        """Test getting handler for invalid language."""
        with pytest.raises(LanguageNotSupportedError):
            self.manager.get_handler("invalid_language")
    
    def test_get_supported_languages(self):
        """Test getting list of supported languages."""
        languages = self.manager.get_supported_languages()
        assert "python" in languages
        assert "javascript" in languages
        assert "js" in languages
        assert "java" in languages
        assert "cpp" in languages
        assert "c" in languages
        assert "go" in languages
        assert "rust" in languages
    
    def test_is_language_supported(self):
        """Test checking if language is supported."""
        assert self.manager.is_language_supported("python") == True
        assert self.manager.is_language_supported("javascript") == True
        assert self.manager.is_language_supported("js") == True
        assert self.manager.is_language_supported("invalid") == False
    
    def test_prepare_code_file(self):
        """Test preparing code file for execution."""
        code = "def test(): return 42"
        file_path, prepared_code = self.manager.prepare_code_file(code, "python")
        
        assert file_path.startswith("/workspace/code_")
        assert file_path.endswith(".py")
        assert prepared_code == code
    
    def test_prepare_code_file_with_function(self):
        """Test preparing code file with function wrapper."""
        code = "def test_func(): return 42"
        file_path, prepared_code = self.manager.prepare_code_file(
            code, "python", "test_func"
        )
        
        assert file_path.endswith(".py")
        assert "def test_func():" in prepared_code
        assert "result = test_func()" in prepared_code
    
    def test_get_execution_command(self):
        """Test getting execution command for language."""
        command = self.manager.get_execution_command("/path/file.py", "python")
        assert command == ["python"]
        
        command = self.manager.get_execution_command("/path/file.js", "javascript")
        assert command == ["node"]
    
    def test_get_timeout(self):
        """Test getting timeout for language."""
        timeout = self.manager.get_timeout("python")
        assert isinstance(timeout, int)
        assert timeout > 0
        
        timeout = self.manager.get_timeout("rust")
        assert timeout >= 60  # Rust typically needs more time


class TestLanguageManagerGlobal:
    """Test cases for global language manager instance."""
    
    def test_global_language_manager(self):
        """Test that global language manager is properly initialized."""
        assert language_manager is not None
        assert isinstance(language_manager, LanguageManager)
        
        # Test that it works
        handler = language_manager.get_handler("python")
        assert isinstance(handler, PythonHandler)


class TestLanguageEdgeCases:
    """Test cases for language handling edge cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = LanguageManager()
    
    def test_case_insensitive_language_names(self):
        """Test that language names are case insensitive."""
        handler1 = self.manager.get_handler("Python")
        handler2 = self.manager.get_handler("PYTHON")
        handler3 = self.manager.get_handler("python")
        
        assert all(isinstance(h, PythonHandler) for h in [handler1, handler2, handler3])
    
    def test_empty_code_preparation(self):
        """Test preparing empty code."""
        file_path, prepared_code = self.manager.prepare_code_file("", "python")
        assert file_path.endswith(".py")
        assert prepared_code == ""
    
    def test_very_long_code_preparation(self):
        """Test preparing very long code."""
        long_code = "x = 1\n" * 1000
        file_path, prepared_code = self.manager.prepare_code_file(long_code, "python")
        assert file_path.endswith(".py")
        assert prepared_code == long_code
    
    def test_unicode_code_preparation(self):
        """Test preparing code with Unicode characters."""
        unicode_code = "def test(): return '你好世界'"
        file_path, prepared_code = self.manager.prepare_code_file(unicode_code, "python")
        assert file_path.endswith(".py")
        assert prepared_code == unicode_code
    
    def test_code_with_special_characters(self):
        """Test preparing code with special characters."""
        special_code = 'def test(): return "Hello\nWorld\t!"'
        file_path, prepared_code = self.manager.prepare_code_file(special_code, "python")
        assert file_path.endswith(".py")
        assert prepared_code == special_code


if __name__ == "__main__":
    pytest.main([__file__])
