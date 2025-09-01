---
id: contributing
title: Contributing
sidebar_position: 12
---

# Contributing to Synapse SDK

Thank you for your interest in contributing to Synapse SDK! This guide will help you get started with contributing to the project.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Getting Started

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/synapse-sdk.git
   cd synapse-sdk
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements.test.txt
   ```

## Code Formatting and Quality

### Ruff Formatting

We use **Ruff** for code formatting and linting. All contributions must follow our formatting standards.

#### Required Commands

Before submitting any code changes, run these commands:

```bash
# Format all Python code
ruff format .

# Fix linting issues
ruff check --fix .

# Check for remaining issues
ruff check .
```

#### Formatting Workflow

1. **Make your changes** - Write or modify Python code
2. **Format with Ruff** - Run `ruff format .` to apply consistent formatting
3. **Fix linting issues** - Run `ruff check --fix .` to resolve code quality issues
4. **Verify changes** - Review the formatted code to ensure correctness
5. **Commit changes** - Create commits with properly formatted code

#### IDE Integration

Configure your IDE to run Ruff automatically:

- **VS Code**: Install the Ruff extension
- **PyCharm**: Configure Ruff as external tool
- **Vim/Neovim**: Use ruff-lsp or similar plugins

### Code Style Guidelines

- **Line length**: Follow project-specific settings in `pyproject.toml`
- **Import sorting**: Let Ruff handle import organization
- **Type hints**: Use type annotations where appropriate
- **Docstrings**: Follow Google-style docstring format
- **Comments**: Write clear, concise comments for complex logic

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/plugins/utils/test_config.py

# Run with coverage
pytest --cov=synapse_sdk
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names that explain the scenario
- Include both positive and negative test cases
- Mock external dependencies appropriately
- Maintain high test coverage

#### Test Structure

```python
class TestMyFeature:
    """Test MyFeature functionality."""
    
    def test_feature_success_case(self):
        """Test successful feature operation."""
        # Arrange
        input_data = {"key": "value"}
        
        # Act
        result = my_feature(input_data)
        
        # Assert
        assert result == expected_output
    
    def test_feature_error_case(self):
        """Test feature error handling."""
        with pytest.raises(ValueError, match="Expected error message"):
            my_feature(invalid_input)
```

## Plugin Development

### Creating New Plugin Utilities

When adding new plugin utilities:

1. **Add to appropriate module**:
   - Configuration utilities → `synapse_sdk/plugins/utils/config.py`
   - Action utilities → `synapse_sdk/plugins/utils/actions.py`
   - Registry utilities → `synapse_sdk/plugins/utils/registry.py`

2. **Include comprehensive docstrings**:
   ```python
   def my_utility_function(param: str) -> Dict[str, Any]:
       """Brief description of the function.
       
       Args:
           param: Description of the parameter.
           
       Returns:
           Description of the return value.
           
       Raises:
           ValueError: When input is invalid.
           
       Examples:
           >>> my_utility_function("example")
           {'result': 'processed'}
       """
   ```

3. **Add to `__all__` exports**
4. **Write comprehensive tests**
5. **Update documentation**

### Plugin Categories

When working with plugin categories:

- Use existing categories when possible
- Follow naming conventions: `snake_case`
- Add proper validation and error handling
- Update category enums if adding new categories

## Documentation

### API Documentation

- Update docstrings for all public functions
- Include usage examples in docstrings
- Add type hints for better IDE support
- Document error conditions and exceptions

### User Documentation

Update relevant documentation files:

- **API Reference**: `docs/api/plugins/utils.md`
- **Feature Guides**: `docs/features/plugins/index.md`
- **Changelog**: `docs/changelog.md`
- **Examples**: Add practical usage examples

### Documentation Format

Use clear, concise language with:

- Code examples for all functions
- Parameter and return value descriptions
- Error handling examples
- Migration guides for breaking changes

## Pull Request Process

### Before Submitting

1. **Run formatting and linting**:
   ```bash
   ruff format .
   ruff check --fix .
   ```

2. **Run all tests**:
   ```bash
   pytest
   ```

3. **Update documentation** as needed

4. **Add changelog entry** for significant changes

### Pull Request Guidelines

- **Clear title**: Describe what the PR accomplishes
- **Detailed description**: Explain the changes and motivation
- **Reference issues**: Link to relevant GitHub issues
- **Test coverage**: Ensure new code is tested
- **Documentation**: Update docs for user-facing changes

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Code formatted with Ruff

## Documentation
- [ ] API documentation updated
- [ ] User guide updated if needed
- [ ] Changelog entry added
```

## Code Review

### Review Criteria

- **Functionality**: Code works as intended
- **Quality**: Follows coding standards and best practices
- **Testing**: Adequate test coverage
- **Documentation**: Clear documentation for public APIs
- **Performance**: No obvious performance issues
- **Security**: No security vulnerabilities

### Responding to Feedback

- Address all reviewer comments
- Ask for clarification if feedback is unclear
- Make requested changes promptly
- Re-run formatting and tests after changes

## Project Structure

Understanding the project organization:

```
synapse_sdk/
├── plugins/
│   ├── utils/              # Plugin utilities (modular)
│   │   ├── config.py       # Configuration utilities
│   │   ├── actions.py      # Action management
│   │   └── registry.py     # Registry utilities
│   ├── categories/         # Plugin category implementations
│   └── models.py          # Core plugin models
├── clients/               # API clients
├── utils/                 # General utilities
└── devtools/             # Development tools

tests/
├── plugins/
│   └── utils/            # Plugin utility tests
└── ...                   # Other test modules

docs/                     # Documentation
├── api/                  # API reference
├── features/             # Feature guides
└── changelog.md          # Change log
```

## Getting Help

- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions or discuss ideas
- **Documentation**: Check existing docs first
- **Code Review**: Ask for clarification during review

## License

By contributing to Synapse SDK, you agree that your contributions will be licensed under the same license as the project (MIT License).
