# System Compatibility Checker

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/yourusername/system-compat-checker)

A powerful cross-platform CLI tool for checking system compatibility with various applications. This tool collects detailed system information and uses AI-powered analysis to determine if your system meets the requirements for specific software.

## ✨ Features

- 🖥️ **Cross-platform support** - Works on Windows, Linux, and macOS
- 📊 **Comprehensive system analysis** - CPU, memory, storage, GPU, and performance metrics
- 🤖 **AI-powered compatibility analysis** - Uses Groq API for intelligent assessments
- 🎨 **Rich terminal interface** - Beautiful, colorized output with tables and panels
- 🔒 **Secure credential management** - Safe API key storage using system keyring
- 📄 **Multiple output formats** - Console tables, JSON, and file output
- ⚡ **Fast performance** - Quick system information collection

## 🚀 Quick Start

### Installation

```bash
pip install system-compat-checker
```

### Setup (First Time)

```bash
# Interactive setup
syscheck setup

# Or provide API key directly
syscheck setup YOUR_API_KEY
```
Get a free API key at [console.groq.com](https://console.groq.com/)

### Check Your System

```bash
# View system information
syscheck system-info

# Check compatibility with an application
syscheck check "Adobe Photoshop"
```

## 📖 Usage

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `syscheck version` | Show version information | `syscheck version` |
| `syscheck setup` | Configure Groq API key | `syscheck setup --force` |
| `syscheck system-info` | Display system information | `syscheck system-info --json` |
| `syscheck check` | Check application compatibility | `syscheck check "Blender" -r req.json` |
| `syscheck reset` | Remove stored API key | `syscheck reset` |

### System Information

```bash
# Formatted table output
syscheck system-info

# JSON output for scripting
syscheck system-info --json > my_system.json
```

### Compatibility Analysis

```bash
# Basic compatibility check
syscheck check "Visual Studio Code"

# With custom requirements file
syscheck check "My Game" --requirements game_requirements.json

# Save results to file
syscheck check "Photoshop" --output compatibility_report.json
```

### Requirements File Format

Create custom application requirements using JSON:

```json
{
  "application": "My Application",
  "requirements": {
    "cpu": {
      "cores": 4,
      "frequency": 2.5
    },
    "memory": {
      "ram": 8
    },
    "storage": {
      "free": 10
    },
    "gpu": {
      "required": true,
      "memory": 4
    }
  }
}
```

## 🛠️ Development

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/system-compat-checker.git
cd system-compat-checker

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .

# Run tests
pytest
```

### Project Structure

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
├── docs/                  # Documentation
└── examples/              # Example files
```

## 📚 Documentation

- **[User Guide](docs/USER_GUIDE.md)** - Comprehensive usage documentation
- **[Project Documentation](docs/PROJECT_DOCUMENTATION.md)** - Technical architecture details
- **[Contributing Guide](CONTRIBUTING.md)** - Development guidelines

## 🔧 System Requirements

- Python 3.8 or higher
- Internet connection (for AI analysis)
- Groq API key (free at [console.groq.com](https://console.groq.com/))

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Code style and standards
- Testing requirements
- Pull request process
- Development setup

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [User Guide](docs/USER_GUIDE.md) for detailed instructions
- **Issues**: Report bugs on [GitHub Issues](https://github.com/yourusername/system-compat-checker/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/yourusername/system-compat-checker/discussions)

## 🏆 Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for CLI interface
- Powered by [Groq](https://groq.com/) for AI analysis
- Uses [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- System information via [psutil](https://psutil.readthedocs.io/)

---

Made with ❤️ by the System Compatibility Checker Team