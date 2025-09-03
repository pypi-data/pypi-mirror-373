# Contributing to KHX Colory

Thank you for your interest in contributing to KHX Colory! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of terminal/console programming

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/khx-colory.git
   cd khx-colory
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux  
   source .venv/bin/activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e .[dev]
   ```

4. **Verify installation**
   ```bash
   pytest
   colory demo
   ```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=khx_colory --cov-report=html

# Run specific test file
pytest tests/test_text.py -v

# Run specific test
pytest tests/test_text.py::TestColorText::test_basic_text_creation -v
```

### Writing Tests

- Use pytest for all tests
- Test files should be named `test_*.py`
- Test classes should be named `Test*`
- Test methods should be named `test_*`
- Aim for >90% test coverage
- Include both unit tests and integration tests

Example test:
```python
def test_colored_text():
    """Test basic colored text functionality."""
    result = colored("Hello", "red")
    assert "\033[31m" in result
    assert "Hello" in result
    assert "\033[0m" in result
```

## 🎨 Code Style

### Formatting

We use `black` and `isort` for code formatting:

```bash
# Format code
black src tests
isort src tests

# Check formatting
black --check src tests
isort --check-only src tests
```

### Type Checking

We use `mypy` for type checking:

```bash
mypy src
```

### Code Quality Guidelines

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write descriptive docstrings for all public functions and classes
- Keep functions focused and small
- Use meaningful variable and function names
- Add comments for complex logic

## 📝 Documentation

### Docstring Style

Use Google-style docstrings:

```python
def colored(text: str, color: Optional[str] = None) -> str:
    """
    Create colored text with ANSI escape sequences.
    
    Args:
        text: Text to colorize
        color: Color name or specification
        
    Returns:
        Text with ANSI color codes
        
    Examples:
        >>> colored("Hello", "red")
        '\033[31mHello\033[0m'
    """
```

### README Updates

- Update README.md for new features
- Include examples for new functionality
- Update API documentation section
- Add any new dependencies to installation instructions

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment information**
   - Python version
   - Operating system
   - Terminal/console type
   - KHX Colory version

2. **Reproduction steps**
   - Minimal code to reproduce the issue
   - Expected behavior
   - Actual behavior

3. **Error messages**
   - Full traceback
   - Any relevant logs

## ✨ Feature Requests

When requesting features:

1. **Describe the use case**
   - What problem does it solve?
   - How would it be used?

2. **Provide examples**
   - Show proposed API usage
   - Include expected output

3. **Consider backwards compatibility**
   - Will it break existing code?
   - Can it be implemented as optional?

## 🔄 Pull Request Process

### Before Submitting

1. **Create an issue first** (for non-trivial changes)
2. **Fork the repository**
3. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

### Development Process

1. **Write tests first** (TDD approach)
2. **Implement the feature**
3. **Ensure all tests pass**
   ```bash
   pytest
   ```
4. **Check code quality**
   ```bash
   black --check src tests
   isort --check-only src tests
   mypy src
   ```
5. **Update documentation**

### Submitting the PR

1. **Write a clear title and description**
2. **Reference related issues**
3. **Include screenshots/examples** (if applicable)
4. **Ensure CI passes**

### PR Review Process

- All PRs require at least one review
- Address review feedback promptly
- Maintain up-to-date branches
- Be responsive to maintainer requests

## 🏗️ Architecture Guidelines

### Package Structure

```
khx_colory/
├── __init__.py      # Main exports
├── core.py          # Main Colory class
├── colors.py        # Color definitions
├── styles.py        # Style definitions
├── text.py          # Text functionality
└── cli.py           # Command-line interface
```

### Design Principles

1. **Minimal Dependencies**: Keep external dependencies to a minimum
2. **Performance First**: Optimize for speed and memory usage
3. **User-Friendly API**: Make it easy for users to accomplish common tasks
4. **Backwards Compatibility**: Don't break existing user code
5. **Cross-Platform**: Ensure compatibility across different operating systems

### Adding New Features

When adding new features:

1. **Consider the API design carefully**
2. **Maintain consistency with existing patterns**
3. **Add comprehensive tests**
4. **Update documentation**
5. **Consider performance implications**

## 📋 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

### Release Checklist

1. Update version in `pyproject.toml`
2. Update version in `__init__.py`
3. Update CHANGELOG.md
4. Create git tag
5. Build and publish to PyPI
6. Create GitHub release

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Assume good intentions

### Communication

- Use GitHub issues for bug reports and feature requests
- Use GitHub discussions for general questions
- Be clear and concise in communications
- Provide context and examples

## 🙋‍♀️ Getting Help

If you need help with development:

1. **Check existing documentation**
2. **Search existing issues**
3. **Create a new issue** with the "question" label
4. **Join discussions** in GitHub Discussions

## 🎉 Recognition

Contributors will be:

- Listed in the AUTHORS file
- Mentioned in release notes
- Credited in the documentation

Thank you for contributing to KHX Colory! 🌈
