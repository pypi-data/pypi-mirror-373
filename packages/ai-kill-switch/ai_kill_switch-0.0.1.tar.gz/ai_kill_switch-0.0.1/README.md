# AI Kill Switch SDK

A Python SDK for implementing AI safety mechanisms and kill switches.

## Installation

Install the package from PyPI:

```bash
pip install ai-kill-switch
```

Or install from source:

```bash
git clone https://github.com/ai-kill-switch/ai-kill-switch.git
cd ai-kill-switch
pip install -e .
```

## Quick Start

```python
from ai_kill_switch import hello

# Use the hello function
message = hello()
print(message)  # Output: Hello from AI Kill Switch!
```

## Features

- **Simple Interface**: Easy-to-use hello function
- **Lightweight**: Minimal dependencies and overhead
- **Well-tested**: Comprehensive test coverage

## Usage

```python
from ai_kill_switch import hello

# Get the greeting message
message = hello()
print(message)

# Use in your own functions
def greet_user():
    return f"Welcome! {hello()}"
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/ai-kill-switch/ai-kill-switch.git
cd ai-kill-switch

# Install development dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ai_kill_switch

# Run specific test file
pytest tests/test_core.py
```

### Code Quality

```bash
# Format code
black ai_kill_switch tests

# Lint code
flake8 ai_kill_switch tests

# Type checking
mypy ai_kill_switch
```

## Building and Publishing

### Build Package

```bash
# Build source distribution and wheel
python -m build

# Check package
twine check dist/*
```

### Upload to PyPI

```bash
# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/ai-kill-switch/ai-kill-switch/issues)
- **Documentation**: [Documentation](https://ai-kill-switch.github.io)
- **Email**: ai.kill.switch.contact@gmail.com

## Changelog

### 0.0.1 (Unreleased)
- Initial release
- Simple hello function
- Comprehensive test coverage
