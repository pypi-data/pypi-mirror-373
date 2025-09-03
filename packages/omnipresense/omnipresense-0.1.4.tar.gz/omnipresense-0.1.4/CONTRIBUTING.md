# Contributing to OmniPreSense Radar

We welcome contributions! This guide will help you get started with developing and contributing to the OmniPreSense Radar library.

## 🚀 Getting Started

### Development Environment Setup

```bash
git clone https://github.com/yourusername/OmnipresenseRadar.git
cd OmnipresenseRadar

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Development Dependencies

The development environment includes:
- **pytest** - Testing framework
- **black** - Code formatting
- **ruff** - Fast Python linter
- **mypy** - Static type checking
- **bandit** - Security analysis
- **pre-commit** - Git hooks for code quality

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=omnipresense

# Run specific test file
pytest tests/test_doppler_radar.py -v

# Run with detailed output
pytest -v --tb=short
```

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names: `test_doppler_radar_detects_motion()`
- Mock hardware interactions when possible
- Include both positive and negative test cases

Example test structure:
```python
def test_radar_configuration():
    radar = create_radar('OPS243-C', '/dev/mock')
    with radar:
        radar.set_units(Units.METERS_PER_SECOND)
        assert radar.get_config().units == Units.METERS_PER_SECOND
```

## 🔧 Code Quality

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. The following checks run automatically on each commit:

- **Code Formatting**: Black, isort for consistent style
- **Linting**: Ruff for code quality and style issues
- **Type Checking**: MyPy for static type analysis
- **Security**: Bandit for security vulnerability scanning
- **Dependencies**: Safety for known security vulnerabilities
- **Documentation**: Pydocstyle for docstring conventions
- **Import Management**: Autoflake removes unused imports
- **Syntax Upgrades**: PyUpgrade modernizes Python syntax
- **Commit Messages**: Conventional commit format validation

### Manual Code Quality Checks

```bash
# Run all pre-commit hooks on all files
pre-commit run --all-files

# Format code manually (if needed)
black omnipresense/ tests/

# Type checking
mypy omnipresense/

# Linting with ruff
ruff check omnipresense/ tests/
ruff format omnipresense/ tests/

# Security scanning
bandit -r omnipresense/
```

### Code Style Guidelines

- Follow **PEP 8** style guidelines
- Use **type hints** for all public functions
- Write **docstrings** for all public classes and methods
- Keep functions focused and small
- Use descriptive variable and function names
- Add comments for complex logic

Example function with proper style:
```python
def set_magnitude_threshold(self, threshold: int, doppler: bool = True) -> None:
    """
    Set magnitude threshold for detection.

    Args:
        threshold: Magnitude threshold value
        doppler: True for Doppler threshold, False for FMCW

    Raises:
        RadarValidationError: If threshold is negative
    """
    if threshold < 0:
        raise RadarValidationError("Threshold must be non-negative")
    
    command = f"M>{threshold}" if doppler else f"m>{threshold}"
    self.send_command(command)
```

## 📝 Documentation

### Docstring Standards

Use Google-style docstrings:

```python
def calculate_speed(self, raw_value: float, units: Units) -> float:
    """
    Calculate speed in specified units from raw radar value.
    
    Args:
        raw_value: Raw speed value from radar
        units: Target units for conversion
        
    Returns:
        Speed value in specified units
        
    Raises:
        ValueError: If raw_value is negative
        
    Example:
        >>> speed = radar.calculate_speed(10.5, Units.KILOMETERS_PER_HOUR)
        >>> print(f"Speed: {speed} km/h")
    """
```

### Example Documentation

When adding examples:
- Include clear, working code
- Add comments explaining key concepts
- Show both basic and advanced usage
- Include error handling where appropriate

## 🤝 Contribution Process

### 1. Planning Your Contribution

Before starting work:
- **Check existing issues** for similar proposals
- **Open a discussion** for new features
- **Fork the repository** to your account

### 2. Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**:
   ```bash
   pytest
   pre-commit run --all-files
   ```

4. **Commit with conventional format**:
   ```bash
   git commit -m "feat: add magnitude threshold configuration"
   git commit -m "fix: handle serial timeout gracefully"
   git commit -m "docs: update API examples"
   ```

5. **Push and create Pull Request**:
   ```bash
   git push origin feature/your-feature-name
   ```

### 3. Pull Request Guidelines

When creating a PR:
- **Use a clear title** describing the change
- **Reference related issues** (e.g., "Fixes #123")
- **Include a detailed description** of what changed and why
- **Add screenshots/examples** for UI changes
- **Update CHANGELOG.md** if applicable

### 4. Review Process

- All PRs require review before merging
- Address reviewer feedback promptly
- Keep PRs focused and reasonably sized
- Be respectful and constructive in discussions

## 🎯 Types of Contributions

### Bug Reports
- Use issue templates
- Provide minimal reproduction cases
- Include system information and error messages
- Test with latest version first

### Feature Requests
- Explain the use case and benefits
- Consider backward compatibility
- Discuss API design before implementation
- Provide examples of how it would be used

### Documentation Improvements
- Fix typos and unclear explanations
- Add missing examples
- Improve API documentation
- Update installation instructions

### Code Contributions
- Bug fixes
- New sensor support
- Performance improvements
- API enhancements

## 📋 Development Guidelines

### Adding New Sensor Support

When adding support for a new OmniPreSense sensor:

1. **Create sensor class** inheriting from `OPSRadarSensor`
2. **Implement required methods**: `_parse_radar_data()`, `_validate_units()`
3. **Add to factory function** in `create_radar()`
4. **Include comprehensive tests**
5. **Update documentation** and examples

### Error Handling

- Use specific exception types from the `radar` module
- Provide helpful error messages
- Log appropriate debug information
- Handle edge cases gracefully

### Performance Considerations

- Minimize blocking operations in data callbacks
- Use appropriate data structures
- Profile performance-critical paths
- Consider memory usage for long-running applications

## ❓ Getting Help

If you need help with development:

1. **Check documentation** and existing examples
2. **Search existing issues** for similar questions
3. **Join discussions** on GitHub
4. **Contact maintainers** via email or issues

## 🙏 Recognition

Contributors are recognized in:
- GitHub contributor list
- Release notes for significant contributions
- README acknowledgments

Thank you for contributing to the OmniPreSense Radar library!