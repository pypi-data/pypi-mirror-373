# System Compatibility Checker Documentation

Welcome to the System Compatibility Checker documentation. This directory contains comprehensive guides and technical documentation for the project.

## 📚 Documentation Index

### User Documentation
- **[User Guide](USER_GUIDE.md)** - Complete user manual with examples, troubleshooting, and advanced usage
- **[Quick Start Guide](#quick-start)** - Get up and running in minutes
- **[API Reference](#api-reference)** - Command-line interface reference

### Developer Documentation
- **[Project Documentation](PROJECT_DOCUMENTATION.md)** - Technical architecture and implementation details
- **[Contributing Guide](../CONTRIBUTING.md)** - Guidelines for contributors
- **[Testing Guide](#testing)** - How to run and write tests

### Examples and Tutorials
- **[Examples Directory](../examples/)** - Sample requirements files and usage examples
- **[Integration Examples](#integration)** - How to integrate with other tools

## 🚀 Quick Start

### Installation
```bash
pip install system-compat-checker
```

### Basic Usage
```bash
# Setup (first time only)
syscheck setup

# Check your system
syscheck system-info

# Check compatibility
syscheck check "Adobe Photoshop"
```

## 📖 User Guide Highlights

The [User Guide](USER_GUIDE.md) covers:

- **Installation Methods** - PyPI, source installation, virtual environments
- **Command Reference** - All CLI commands with options and examples
- **Configuration** - API key setup and management
- **Requirements Files** - Creating custom application requirements
- **Output Formats** - JSON, console tables, file output
- **Troubleshooting** - Common issues and solutions
- **Advanced Usage** - Scripting, automation, and integration
- **Examples** - Real-world usage scenarios

## 🔧 API Reference

### Core Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `syscheck version` | Show version | `syscheck version` |
| `syscheck setup` | Configure API key | `syscheck setup --force` |
| `syscheck system-info` | Display system info | `syscheck system-info --json` |
| `syscheck check` | Check compatibility | `syscheck check "App" -r req.json` |
| `syscheck reset` | Remove API key | `syscheck reset` |

### Global Options

| Option | Description | Example |
|--------|-------------|---------|
| `--help` | Show help | `syscheck --help` |
| `--version` | Show version | `syscheck --version` |

### Command-Specific Options

#### `system-info`
- `--json` - Output as JSON format

#### `check`
- `--requirements, -r` - Path to requirements file
- `--output, -o` - Save output to file
- `--json` - Output as JSON format

#### `setup`
- `--force` - Overwrite existing API key

## 🧪 Testing

### Running Tests
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_cli.py
```

### Test Structure
```
tests/
├── test_cli.py           # CLI interface tests
├── test_system_info.py   # System information tests
├── test_storage.py       # API key storage tests
└── test_groq_analyzer.py # AI analysis tests
```

## 🔗 Integration

### Python Scripts
```python
import subprocess
import json

# Get system info programmatically
result = subprocess.run(['syscheck', 'system-info', '--json'], 
                       capture_output=True, text=True)
system_info = json.loads(result.stdout)
```

### Shell Scripts
```bash
#!/bin/bash
# Automated compatibility checking
if syscheck check "My App" --json | jq -r '.compatible' | grep -q true; then
    echo "System is compatible"
else
    echo "System needs upgrades"
fi
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Check System Compatibility
  run: |
    pip install system-compat-checker
    syscheck system-info --json > system_report.json
```

## 📋 Project Structure

```
system-compat-checker/
├── src/                    # Source code
│   ├── cli.py             # CLI interface
│   ├── system_info.py     # System information collection
│   ├── groq_analyzer.py   # AI compatibility analysis
│   ├── storage.py         # Secure API key storage
│   ├── windows_info.py    # Windows-specific collectors
│   └── posix_info.py      # Linux/macOS collectors
├── tests/                 # Unit tests
├── docs/                  # Documentation (this directory)
├── examples/              # Example requirements files
├── README.md              # Project overview
├── CONTRIBUTING.md        # Contribution guidelines
├── LICENSE               # MIT license
└── setup.py              # Package configuration
```

## 🆘 Getting Help

### Documentation
1. Start with the [User Guide](USER_GUIDE.md) for comprehensive instructions
2. Check [examples](../examples/) for practical usage scenarios
3. Review [Project Documentation](PROJECT_DOCUMENTATION.md) for technical details

### Community Support
- **Issues**: Report bugs on [GitHub Issues](https://github.com/yourusername/system-compat-checker/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/yourusername/system-compat-checker/discussions)
- **Contributing**: See [Contributing Guide](../CONTRIBUTING.md) for development help

### Common Resources
- [Groq API Documentation](https://console.groq.com/docs)
- [Click Framework Docs](https://click.palletsprojects.com/)
- [Rich Terminal Library](https://rich.readthedocs.io/)

---

*Last updated: January 30, 2025*