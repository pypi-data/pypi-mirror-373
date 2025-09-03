"""
Multi-language support module for executing code in different programming languages.
"""

import os
import uuid
import random
import logging
from typing import Dict, List, Optional, Tuple, Any
from ..config.settings import settings
from ..exceptions import LanguageNotSupportedError, ExecutionError

logger = logging.getLogger(__name__)


class LanguageHandler:
    """Base class for language-specific code execution handlers."""
    
    def __init__(self, language: str):
        """Initialize language handler."""
        self.language = language.lower()
        self.config = settings.languages.get(self.language)
        if not self.config:
            raise LanguageNotSupportedError(f"Language '{language}' is not supported")
    
    def prepare_code(self, code: str, function_name: Optional[str] = None) -> str:
        """
        Prepare code for execution.
        
        Args:
            code: Source code
            function_name: Optional function name to wrap code
            
        Returns:
            Prepared code ready for execution
        """
        return code
    
    def get_file_extension(self) -> str:
        """Get file extension for this language."""
        return self.config["extension"]
    
    def get_execution_command(self, file_path: str) -> List[str]:
        """
        Get command to execute the code file.
        
        Args:
            file_path: Path to the code file
            
        Returns:
            Command as list of strings
        """
        command_template = self.config["command"]
        
        # Replace placeholders
        command = []
        for part in command_template:
            if "{file}" in part:
                part = part.replace("{file}", file_path)
            if "{class}" in part:
                # For Java, extract class name from file
                class_name = os.path.splitext(os.path.basename(file_path))[0]
                part = part.replace("{class}", class_name)
            if "{output}" in part:
                # For compiled languages, use executable name
                output_name = os.path.splitext(file_path)[0]
                part = part.replace("{output}", output_name)
            command.append(part)
        
        return command
    
    def get_timeout(self) -> int:
        """Get execution timeout for this language."""
        return self.config.get("timeout", settings.execution["timeout"])


class PythonHandler(LanguageHandler):
    """Handler for Python code execution."""
    
    def __init__(self):
        super().__init__("python")
    
    def prepare_code(self, code: str, function_name: Optional[str] = None) -> str:
        """Prepare Python code for execution."""
        if function_name:
            # Wrap code to call specific function
            wrapper = f"""
{code}

# Call the function and print result
if __name__ == "__main__":
    try:
        result = {function_name}()
        print(result)
    except Exception as e:
        print(f"Error: {{e}}")
        exit(1)
"""
            return wrapper
        return code


class JavaScriptHandler(LanguageHandler):
    """Handler for JavaScript code execution."""
    
    def __init__(self):
        super().__init__("javascript")
    
    def prepare_code(self, code: str, function_name: Optional[str] = None) -> str:
        """Prepare JavaScript code for execution."""
        if function_name:
            # Wrap code to call specific function
            wrapper = f"""
{code}

// Call the function and print result
try {{
    const result = {function_name}();
    console.log(result);
}} catch (error) {{
    console.error('Error:', error.message);
    process.exit(1);
}}
"""
            return wrapper
        return code


class JavaHandler(LanguageHandler):
    """Handler for Java code execution."""
    
    def __init__(self):
        super().__init__("java")
    
    def prepare_code(self, code: str, function_name: Optional[str] = None) -> str:
        """Prepare Java code for execution."""
        # Extract class name or create one
        import re
        class_match = re.search(r'class\s+(\w+)', code)
        if class_match:
            class_name = class_match.group(1)
        else:
            class_name = "Main"
            # Wrap code in a class if not already
            if "class " not in code:
                code = f"""
public class {class_name} {{
    {code}
    
    public static void main(String[] args) {{
        {class_name} instance = new {class_name}();
        {f"System.out.println(instance.{function_name}());" if function_name else ""}
    }}
}}
"""
        
        return code
    
    def get_execution_command(self, file_path: str) -> List[str]:
        """Get Java execution command."""
        class_name = os.path.splitext(os.path.basename(file_path))[0]
        return ["sh", "-c", f"javac {file_path} && java {class_name}"]


class CppHandler(LanguageHandler):
    """Handler for C++ code execution."""
    
    def __init__(self):
        super().__init__("cpp")
    
    def prepare_code(self, code: str, function_name: Optional[str] = None) -> str:
        """Prepare C++ code for execution."""
        if "int main" not in code:
            # Add main function if not present
            main_code = f"""
#include <iostream>
using namespace std;

{code}

int main() {{
    {f"cout << {function_name}() << endl;" if function_name else ""}
    return 0;
}}
"""
            return main_code
        return code
    
    def get_execution_command(self, file_path: str) -> List[str]:
        """Get C++ execution command."""
        output_name = os.path.splitext(file_path)[0]
        return ["sh", "-c", f"g++ -o {output_name} {file_path} && {output_name}"]


class CHandler(LanguageHandler):
    """Handler for C code execution."""
    
    def __init__(self):
        super().__init__("c")
    
    def prepare_code(self, code: str, function_name: Optional[str] = None) -> str:
        """Prepare C code for execution."""
        if "int main" not in code:
            # Add main function if not present
            newline = "\\n"  # Define backslash outside f-string
            printf_call = f"printf(\"%d{newline}\", {function_name}());" if function_name else ""
            main_code = f"""
#include <stdio.h>

{code}

int main() {{
    {printf_call}
    return 0;
}}
"""
            return main_code
        return code
    
    def get_execution_command(self, file_path: str) -> List[str]:
        """Get C execution command."""
        output_name = os.path.splitext(file_path)[0]
        return ["sh", "-c", f"gcc -o {output_name} {file_path} && {output_name}"]


class GoHandler(LanguageHandler):
    """Handler for Go code execution."""
    
    def __init__(self):
        super().__init__("go")
    
    def prepare_code(self, code: str, function_name: Optional[str] = None) -> str:
        """Prepare Go code for execution."""
        if "package main" not in code:
            # Add package and main function if not present
            main_code = f"""
package main

import "fmt"

{code}

func main() {{
    {f"fmt.Println({function_name}())" if function_name else ""}
}}
"""
            return main_code
        return code


class RustHandler(LanguageHandler):
    """Handler for Rust code execution."""
    
    def __init__(self):
        super().__init__("rust")
    
    def prepare_code(self, code: str, function_name: Optional[str] = None) -> str:
        """Prepare Rust code for execution."""
        if "fn main" not in code:
            # Add main function if not present
            println_call = f"println!(\"{{}}\", {function_name}());" if function_name else ""
            main_code = f"""
{code}

fn main() {{
    {println_call}
}}
"""
            return main_code
        return code
    
    def get_execution_command(self, file_path: str) -> List[str]:
        """Get Rust execution command."""
        output_name = os.path.splitext(file_path)[0]
        return ["sh", "-c", f"rustc -o {output_name} {file_path} && {output_name}"]


class LanguageManager:
    """Manages language handlers and provides unified interface."""
    
    def __init__(self):
        """Initialize language manager."""
        self._handlers: Dict[str, LanguageHandler] = {}
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Register all language handlers."""
        handlers = [
            PythonHandler(),
            JavaScriptHandler(),
            JavaHandler(),
            CppHandler(),
            CHandler(),
            GoHandler(),
            RustHandler(),
        ]
        
        for handler in handlers:
            self._handlers[handler.language] = handler
            # Register common aliases
            if handler.language == "javascript":
                self._handlers["js"] = handler
            elif handler.language == "cpp":
                self._handlers["c++"] = handler
                self._handlers["cxx"] = handler
    
    def get_handler(self, language: str) -> LanguageHandler:
        """
        Get language handler for specified language.
        
        Args:
            language: Programming language name
            
        Returns:
            Language handler instance
            
        Raises:
            LanguageNotSupportedError: If language is not supported
        """
        language = language.lower()
        if language not in self._handlers:
            raise LanguageNotSupportedError(f"Language '{language}' is not supported")
        return self._handlers[language]
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported programming languages."""
        return list(self._handlers.keys())
    
    def is_language_supported(self, language: str) -> bool:
        """Check if a language is supported."""
        return language.lower() in self._handlers
    
    def prepare_code_file(self, code: str, language: str,
                         function_name: Optional[str] = None) -> Tuple[str, str]:
        """
        Prepare code file for execution with unique naming for batch processing.

        Args:
            code: Source code
            language: Programming language
            function_name: Optional function name to wrap code

        Returns:
            Tuple of (file_path, prepared_code)
        """
        handler = self.get_handler(language)

        # Prepare code
        prepared_code = handler.prepare_code(code, function_name)

        # Generate unique file name with random number for batch processing
        # Format: {prefix}_{random_number}.{extension}
        random_number = random.randint(10000, 99999)  # 5-digit random number
        extension = handler.get_file_extension()

        # Use language-specific prefixes for better identification
        prefix_map = {
            "python": "script",
            "javascript": "script",
            "java": "code",
            "cpp": "code",
            "c": "code",
            "go": "code",
            "rust": "code"
        }
        prefix = prefix_map.get(language.lower(), "code")

        file_name = f"{prefix}_{random_number:05d}{extension}"
        file_path = f"/workspace/{file_name}"

        return file_path, prepared_code
    
    def get_execution_command(self, file_path: str, language: str) -> List[str]:
        """
        Get execution command for code file.
        
        Args:
            file_path: Path to code file
            language: Programming language
            
        Returns:
            Execution command as list of strings
        """
        handler = self.get_handler(language)
        return handler.get_execution_command(file_path)
    
    def get_timeout(self, language: str) -> int:
        """
        Get execution timeout for language.
        
        Args:
            language: Programming language
            
        Returns:
            Timeout in seconds
        """
        handler = self.get_handler(language)
        return handler.get_timeout()


# Global language manager instance
language_manager = LanguageManager()
