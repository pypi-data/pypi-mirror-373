# Contributing to System Compatibility Checker

Thank you for your interest in contributing to the System Compatibility Checker! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/system-compat-checker.git`
3. Create a virtual environment: `python -m venv .venv`
4. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/macOS: `source .venv/bin/activate`
5. Install development dependencies: `pip install -e ".[dev]"`

## Development Workflow

### Coding Standards

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all functions, classes, and modules
- Keep lines under 100 characters
- Use meaningful variable and function names

### Testing

We use pytest for testing. To run the tests:

```bash
pytest
```

Please ensure that all tests pass before submitting a pull request. Also, add tests for any new functionality you implement.

### Linting

We use flake8 for linting. To lint the code:

```bash
flake8 src tests
```

### Type Checking

We use mypy for type checking. To check types:

```bash
mypy src
```

## Pull Request Process

1. Create a new branch for your feature or bugfix: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Run tests, linting, and type checking to ensure your changes meet the project standards
4. Commit your changes with a descriptive commit message
5. Push your branch to your fork: `git push origin feature/your-feature-name`
6. Submit a pull request to the main repository

### Pull Request Guidelines

- Provide a clear description of the changes in your pull request
- Link any related issues
- Ensure all tests pass
- Update documentation if necessary
- Keep pull requests focused on a single topic

## Feature Requests and Bug Reports

Please use the GitHub issue tracker to submit feature requests and bug reports. When reporting a bug, please include:

- A clear description of the bug
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- System information (OS, Python version, etc.)

## Documentation

Documentation is crucial for this project. Please update the documentation when making changes to the code. This includes:

- README.md
- Docstrings
- Comments in the code
- Any other relevant documentation

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License.