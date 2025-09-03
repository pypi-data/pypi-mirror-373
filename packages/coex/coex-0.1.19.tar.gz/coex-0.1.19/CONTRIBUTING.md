# Contributing to coex

Thank you for your interest in contributing to coex! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Docker installed and running
- Git for version control

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/torchtorchkimtorch/coex.git
   cd coex
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Verify installation:**
   ```bash
   python -c "import coex; print('coex installed successfully')"
   ```

5. **Run tests to ensure everything works:**
   ```bash
   pytest
   ```

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-new-language-support`
- `bugfix/fix-docker-timeout-issue`
- `docs/update-api-documentation`
- `refactor/improve-error-handling`

### Commit Messages

Follow conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(languages): add support for Ruby language execution

fix(docker): resolve container cleanup timeout issue

docs(readme): update installation instructions
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_executor.py

# Run with coverage
pytest --cov=coex --cov-report=html

# Run only integration tests
pytest -m integration

# Run tests in parallel
pytest -n auto
```

### Writing Tests

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **Security Tests**: Test security features and protections

Test file structure:
```
tests/
├── test_executor.py          # Core execution engine tests
├── test_security.py          # Security validation tests
├── test_docker_manager.py    # Docker management tests
├── test_languages.py         # Language support tests
├── test_integration.py       # Integration tests
└── conftest.py               # Shared test fixtures
```

### Test Guidelines

- Use descriptive test names: `test_execute_python_code_with_valid_input`
- Include both positive and negative test cases
- Mock external dependencies (Docker, network calls)
- Test edge cases and error conditions
- Maintain test isolation (no shared state between tests)

## Code Style

### Python Code Style

We use the following tools for code quality:

```bash
# Format code
black coex/ tests/

# Sort imports
isort coex/ tests/

# Lint code
flake8 coex/ tests/

# Type checking
mypy coex/
```

### Style Guidelines

- Follow PEP 8 for Python code style
- Use type hints for all public APIs
- Write docstrings for all public functions and classes
- Keep line length to 88 characters (Black default)
- Use meaningful variable and function names

### Documentation Style

- Use Google-style docstrings
- Include parameter types and return types
- Provide usage examples for complex functions
- Document exceptions that may be raised

Example:
```python
def execute(inputs: Optional[List[Any]] = None,
           outputs: Optional[List[Any]] = None,
           code: Optional[str] = None,
           language: str = "python") -> List[int]:
    """
    Execute code snippets in isolated Docker environments.
    
    Args:
        inputs: List of input values for testing
        outputs: List of expected output values
        code: Code to execute
        language: Programming language (default: "python")
        
    Returns:
        List of integers (0 or 1) indicating pass/fail for each test case
        
    Raises:
        SecurityError: If dangerous code is detected
        ValidationError: If input validation fails
        
    Example:
        >>> result = execute(inputs=[1, 2], outputs=[2, 4], 
        ...                  code="def double(x): return x * 2")
        >>> print(result)
        [1, 1]
    """
```

## Submitting Changes

### Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and commit:**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

3. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request:**
   - Use a descriptive title
   - Fill out the PR template
   - Link any related issues
   - Add appropriate labels

### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Integration tests pass

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings introduced
```

### Review Process

1. Automated checks must pass (tests, linting, type checking)
2. At least one maintainer review required
3. All conversations must be resolved
4. Branch must be up to date with main

## Adding New Features

### Adding Language Support

To add support for a new programming language:

1. **Create language handler:**
   ```python
   # In coex/core/languages.py
   class NewLanguageHandler(LanguageHandler):
       def __init__(self):
           super().__init__("newlang")
       
       def prepare_code(self, code: str, function_name: Optional[str] = None) -> str:
           # Language-specific code preparation
           return code
   ```

2. **Update configuration:**
   ```python
   # In coex/config/settings.py
   "newlang": {
       "image": "newlang:latest",
       "extension": ".newlang",
       "command": ["newlang"],
       "timeout": 30,
   }
   ```

3. **Add tests:**
   ```python
   # In tests/test_languages.py
   def test_newlang_handler():
       handler = NewLanguageHandler()
       # Test language-specific functionality
   ```

4. **Update documentation:**
   - Add to supported languages table in README
   - Add usage examples
   - Update API documentation

### Adding Security Rules

To add new security validation rules:

1. **Update security patterns:**
   ```python
   # In coex/config/settings.py
   "blocked_patterns": [
       # Add new dangerous patterns
       r"new_dangerous_pattern",
   ]
   ```

2. **Add language-specific validation:**
   ```python
   # In coex/core/security.py
   def _validate_newlang_code(self, code: str) -> None:
       # Language-specific security checks
   ```

3. **Add security tests:**
   ```python
   # In tests/test_security.py
   def test_newlang_security_validation():
       # Test new security rules
   ```

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes (backward compatible)

### Release Checklist

1. Update version in `setup.py` and `coex/__init__.py`
2. Update `CHANGELOG.md` with new features and fixes
3. Run full test suite: `pytest`
4. Update documentation if needed
5. Create release PR and get approval
6. Tag release: `git tag v1.0.0`
7. Push tag: `git push origin v1.0.0`
8. Create GitHub release with changelog
9. Publish to PyPI (maintainers only)

## Getting Help

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/torchtorchkimtorch/coex/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/torchtorchkimtorch/coex/discussions)
- **Documentation**: Check the docs/ directory for detailed guides
- **Examples**: See examples/ directory for usage patterns

## Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` file
- GitHub contributors page
- Release notes for significant contributions

Thank you for contributing to coex!
