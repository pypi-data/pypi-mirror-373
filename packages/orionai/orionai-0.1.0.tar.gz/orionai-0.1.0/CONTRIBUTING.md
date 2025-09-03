# Contributing to OrionAI

We're excited that you're interested in contributing to OrionAI! This document outlines how you can help make this project better.

## Ways to Contribute

### 🐛 Bug Reports
- Search existing issues before creating a new one
- Use the bug report template when available
- Include steps to reproduce the issue
- Mention your Python version and operating system

### 💡 Feature Requests
- Check if the feature already exists or is planned
- Clearly describe the use case and expected behavior
- Consider submitting a draft implementation

### 🔧 Code Contributions
- Fork the repository and create a feature branch
- Write clear commit messages
- Add tests for new functionality
- Update documentation when needed

## Development Setup

1. **Clone your fork:**
   ```bash
   git clone https://github.com/your-username/OrionAI.git
   cd OrionAI
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Run verification:**
   ```bash
   python verify_setup.py
   ```

## Code Style Guidelines

### Python Code
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and under 50 lines when possible

### Documentation
- Use clear, simple language
- Include practical examples
- Update README.md if adding major features
- Keep API documentation up to date

## Testing

### Running Tests
```bash
python -m pytest tests/
```

### Writing Tests
- Add tests for new features in the `tests/` directory
- Use descriptive test names
- Test both success and error cases
- Mock external API calls when testing

## Pull Request Process

1. **Before submitting:**
   - Run all tests and ensure they pass
   - Update documentation
   - Check code style compliance
   - Rebase on the latest main branch

2. **Pull request description:**
   - Clearly describe what the PR does
   - Reference any related issues
   - Include screenshots for UI changes
   - List any breaking changes

3. **Review process:**
   - Address reviewer feedback promptly
   - Keep discussions focused and respectful
   - Update tests if requirements change

## API Guidelines

### Adding New Features
- Follow the existing patterns in `AIPython` class
- Use type hints for all parameters
- Include comprehensive error handling
- Add proper logging with the verbose flag

### LLM Provider Integration
- Implement the base provider interface
- Handle rate limiting and API errors
- Include proper authentication validation
- Add configuration documentation

## Documentation Standards

### Code Documentation
```python
def example_function(param: str, optional: bool = False) -> dict:
    """
    Brief description of what the function does.
    
    Args:
        param: Description of the parameter
        optional: Description of optional parameter
        
    Returns:
        Dictionary containing the result
        
    Raises:
        ValueError: When param is invalid
        
    Example:
        >>> result = example_function("test")
        >>> print(result["status"])
        success
    """
```

### README Updates
- Keep the quick start section concise
- Include practical examples
- Update feature lists when adding new capabilities
- Maintain consistent formatting

## Community Guidelines

### Be Respectful
- Use inclusive language
- Be constructive in feedback
- Help newcomers learn the project
- Acknowledge others' contributions

### Communication
- Use GitHub issues for bug reports and feature requests
- Join discussions in a constructive manner
- Ask questions if something isn't clear
- Share your use cases and feedback

## Release Process

### Version Numbers
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Update version in `setup.py` and `__init__.py`
- Tag releases in Git

### Changelog
- Document all changes in CHANGELOG.md
- Group changes by type (Added, Changed, Fixed, Removed)
- Include migration notes for breaking changes

## Getting Help

- **Documentation:** Check `docs/` directory for detailed guides
- **Examples:** Look at the `examples/` directory for usage patterns
- **Issues:** Search existing GitHub issues
- **Questions:** Open a GitHub discussion or issue

## Recognition

Contributors are recognized in several ways:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes for significant contributions
- Invited to become maintainers for ongoing contributions

Thank you for contributing to OrionAI! Your help makes this project better for everyone.
