# Contributing to gspace

First off, thank you for considering contributing to `gspace`! It's people like you that make `gspace` such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to dev@sentivs.com.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

**How Do I Submit a (Good) Bug Report?**

Bugs are tracked as [GitHub issues](https://github.com/Sentivs-co/gspace/issues). Create an issue and provide the following information:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Describe the behavior you observed**
- **Describe the behavior you expected**
- **Include screenshots or code examples if applicable**
- **List your environment details:**
  - Python version
  - gspace version
  - Operating system
- **Provide error messages and stack traces** if available

Example:

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Initialize client with '...'
2. Call method '...'
3. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Environment:**
- Python: 3.12.0
- gspace: 0.1.0
- OS: macOS 14.0

**Additional context**
Add any other context about the problem here.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as [GitHub issues](https://github.com/Sentivs-co/gspace/issues). When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and explain which behavior you expected to see instead**
- **Explain why this enhancement would be useful**

### Pull Requests

1. **Fork the repository** and create your branch from `develop` (or `main` if develop doesn't exist):
   ```bash
   git checkout develop
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes** following our coding standards:
   - Follow PEP 8 style guide
   - Write clear, self-documenting code
   - Add docstrings to functions and classes
   - Add type hints where appropriate

3. **Write or update tests**:
   - Add tests for new functionality
   - Ensure all tests pass
   ```bash
   pytest
   ```

4. **Run linting and formatting**:
   ```bash
   # Format code
   black .
   isort .

   # Lint code
   ruff check .
   ```

5. **Update documentation** if needed:
   - Update docstrings
   - Update README if adding new features
   - Add examples if applicable

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add amazing feature"
   ```

   **Commit message guidelines:**
   - Use the present tense ("Add feature" not "Added feature")
   - Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
   - Limit the first line to 72 characters or less
   - Reference issues and pull requests liberally

7. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```

8. **Open a Pull Request**:
   - Use a clear title and description
   - Reference any related issues
   - Wait for review and address feedback

## Development Setup

### Prerequisites

- Python 3.12 or higher
- Git
- Poetry (optional, for dependency management)

### Setting Up Your Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Sentivs-co/gspace.git
   cd gspace
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e .[dev]
   ```

   Or with Poetry:
   ```bash
   poetry install
   poetry shell
   ```

4. **Install pre-commit hooks** (optional but recommended):
   ```bash
   pre-commit install
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gspace --cov-report=html

# Run specific test file
pytest tests/test_basic.py

# Run with verbose output
pytest -v
```

### Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **Ruff** for linting
- **isort** for import sorting

Run all checks:
```bash
black .
isort .
ruff check .
```

Or use pre-commit (if installed):
```bash
pre-commit run --all-files
```

## Project Structure

```
gspace/
├── gspace/              # Main package
│   ├── auth/           # Authentication modules
│   ├── calendar/       # Calendar service
│   ├── gmail/          # Gmail service
│   ├── drive/          # Drive service
│   ├── sheets/         # Sheets service
│   ├── docs/           # Docs service
│   ├── utils/          # Utility modules
│   └── client/         # Main client
├── tests/              # Test files
├── examples/           # Example scripts
└── docs/              # Documentation (if applicable)
```

## Coding Guidelines

### Python Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Use meaningful variable and function names

### Docstring Format

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of the function.

    More detailed description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When something goes wrong

    Example:
        >>> example_function("test", 42)
        True
    """
    pass
```

### Type Hints

Use type hints for function signatures:

```python
from typing import Optional, List, Dict

def process_items(items: List[str], options: Optional[Dict[str, str]] = None) -> bool:
    ...
```

### Error Handling

- Use specific exception types
- Include helpful error messages
- Log errors appropriately
- Don't swallow exceptions unless necessary

```python
try:
    # operation
except SpecificError as e:
    logger.error(f"Failed to do something: {e}")
    raise CustomError("Helpful message") from e
```

## Adding New Features

1. **Check existing issues** to see if the feature is already planned
2. **Create an issue** first to discuss the feature
3. **Get approval** before starting significant work
4. **Follow the pull request process** above

## Documentation

- Update docstrings when adding/changing functionality
- Update README if adding major features
- Add examples in the `examples/` directory for complex features
- Keep comments clear and concise

## Questions?

- Open an issue for questions about the codebase
- Email dev@sentivs.com for private inquiries
- Check existing documentation and issues first

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

Thank you for contributing to gspace! 🎉
