# Contributing to Gymix Python SDK

We welcome contributions to the Gymix Python SDK! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Git

### Setting up Development Environment

1. **Clone the repository**

   ```bash
   git clone https://github.com/mrssd/gymix-python-sdk.git
   cd python-sdk
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

Run these tools before submitting:

```bash
# Format code
black gymix tests

# Check linting
flake8 gymix tests

# Type checking
mypy gymix
```

### Testing

We use pytest for testing. Run tests with:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gymix

# Run specific test file
pytest tests/test_client.py
```

### Writing Tests

- Write tests for new features and bug fixes
- Maintain high test coverage
- Use descriptive test names
- Mock external API calls using `requests-mock`

Example test:

```python
def test_user_info_success(self, client):
    """Test successful user info retrieval."""
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.gymix.ir/users/info",
            json={"data": {"name": "John", "lastname": "Doe"}}
        )
        result = client.users.get_info()
        assert result["name"] == "John"
```

## Submitting Changes

### Pull Request Process

1. **Fork the repository** on GitHub
2. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and commit them:
   ```bash
   git commit -m "Add your descriptive commit message"
   ```
4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Create a Pull Request** on GitHub

### Pull Request Guidelines

- Provide a clear description of the changes
- Include tests for new functionality
- Update documentation if needed
- Ensure all tests pass
- Follow the existing code style

### Commit Message Format

Use clear, descriptive commit messages:

```
Add backup download functionality

- Implement backup.download() method
- Add error handling for download failures
- Include comprehensive tests
```

## Documentation

### API Documentation

When adding new features:

- Update docstrings for all public methods
- Include parameter descriptions and return types
- Add usage examples where helpful

### README Updates

Update the README.md if you:

- Add new features
- Change the API interface
- Update installation or usage instructions

## Reporting Issues

### Bug Reports

When reporting bugs, include:

- Python version
- Package version
- Minimal code example
- Expected vs actual behavior
- Error messages and stack traces

### Feature Requests

For feature requests:

- Describe the use case
- Explain the expected behavior
- Consider backward compatibility

## Code Review

All submissions go through code review. We look for:

- **Functionality**: Does the code work as intended?
- **Tests**: Are there adequate tests?
- **Documentation**: Is the code well-documented?
- **Style**: Does it follow our coding standards?
- **Performance**: Are there any performance implications?

## Release Process

Releases are handled by maintainers:

1. Update version numbers
2. Update CHANGELOG.md
3. Create a release tag
4. Build and upload to PyPI

## Getting Help

- **Issues**: Use GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact support@gymix.ir for private matters

## Code of Conduct

Please be respectful and professional in all interactions. We want to maintain a welcoming environment for all contributors.

Thank you for contributing to Gymix Python SDK!
