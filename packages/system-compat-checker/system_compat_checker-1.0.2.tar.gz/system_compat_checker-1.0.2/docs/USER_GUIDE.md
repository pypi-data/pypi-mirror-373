# System Compatibility Checker - Complete User Guide

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Detailed Usage](#detailed-usage)
5. [Configuration](#configuration)
6. [Requirements File Format](#requirements-file-format)
7. [Examples](#examples)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Usage](#advanced-usage)
10. [API Reference](#api-reference)

## Overview

The System Compatibility Checker is a powerful cross-platform CLI tool that helps you determine if your system meets the requirements to run specific applications. It collects detailed system information and provides intelligent compatibility analysis using AI-powered insights.

### Key Features
- **Cross-platform support**: Works on Windows, Linux, and macOS
- **Comprehensive system analysis**: CPU, memory, storage, GPU, and performance metrics
- **AI-powered compatibility analysis**: Uses Groq API for intelligent assessments
- **Multiple output formats**: Console tables, JSON, and file output
- **Secure credential management**: Safe API key storage using system keyring
- **Rich terminal interface**: Beautiful, colorized output with tables and panels

### System Requirements
- Python 3.8 or higher
- Internet connection (for AI-powered analysis)
- Groq API key (free registration at https://console.groq.com/)

## Installation

### Method 1: From PyPI (Recommended)
```bash
pip install system-compat-checker
```

### Method 2: From Source
```bash
# Clone the repository
git clone https://github.com/yourusername/system-compat-checker.git
cd system-compat-checker

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

# Install the package
pip install -e .
```

### Verify Installation
```bash
syscheck version
```

## Quick Start

### 1. Setup (First Time Only)
```bash
syscheck setup
```
Enter your Groq API key when prompted. Get a free API key at https://console.groq.com/

### 2. Check Your System Information
```bash
syscheck system-info
```

### 3. Check Compatibility with an Application
```bash
syscheck check "Adobe Photoshop"
```

## Detailed Usage

### Command Structure
```
syscheck [COMMAND] [OPTIONS] [ARGUMENTS]
```

### Available Commands

#### `version`
Display the current version of the tool.
```bash
syscheck version
```

#### `setup`
Configure your Groq API key for AI-powered analysis.
```bash
syscheck setup [--force]
```
- `--force`: Overwrite existing API key

#### `system-info`
Display detailed information about your system.
```bash
syscheck system-info [--json]
```
- `--json`: Output in JSON format instead of formatted tables

#### `check`
Analyze system compatibility with a specific application.
```bash
syscheck check APP_NAME [OPTIONS]
```
- `APP_NAME`: Name of the application to check compatibility for
- `--requirements, -r PATH`: Path to JSON requirements file
- `--output, -o PATH`: Save analysis result to file
- `--json`: Output in JSON format

#### `reset`
Remove stored API key and reset configuration.
```bash
syscheck reset
```

## Configuration

### API Key Management
The tool securely stores your Groq API key using your system's keyring service:
- **Windows**: Windows Credential Manager
- **macOS**: Keychain
- **Linux**: Secret Service (GNOME Keyring, KDE Wallet, etc.)

### Configuration Files
No manual configuration files are needed. All settings are managed through the CLI commands.

## Requirements File Format

Create custom application requirements using JSON format:

```json
{
  "application": "My Application",
  "requirements": {
    "cpu": {
      "cores": 4,
      "frequency": 2.5,
      "architecture": 64
    },
    "memory": {
      "ram": 8,
      "available": 6
    },
    "storage": {
      "free": 10,
      "total": 50
    },
    "gpu": {
      "required": true,
      "memory": 4,
      "vendor": "NVIDIA"
    },
    "os": {
      "supported_systems": ["Windows", "Linux"],
      "min_version": {
        "Windows": "10",
        "Linux": "5.0"
      }
    }
  }
}
```

### Field Descriptions

#### CPU Requirements
- `cores`: Minimum number of physical CPU cores
- `frequency`: Minimum CPU frequency in GHz
- `architecture`: Required architecture (32 or 64 bit)

#### Memory Requirements
- `ram`: Minimum total RAM in GB
- `available`: Minimum available RAM in GB

#### Storage Requirements
- `free`: Minimum free storage space in GB
- `total`: Minimum total storage capacity in GB

#### GPU Requirements
- `required`: Whether a dedicated GPU is required (boolean)
- `memory`: Minimum GPU memory in GB
- `vendor`: Preferred GPU vendor (e.g., "NVIDIA", "AMD", "Intel")

#### OS Requirements
- `supported_systems`: Array of supported operating systems
- `min_version`: Minimum version for each OS

## Examples

### Basic System Information
```bash
# View system info in formatted tables
syscheck system-info

# Export system info as JSON
syscheck system-info --json > my_system.json
```

### Simple Compatibility Check
```bash
# Check compatibility with popular applications
syscheck check "Adobe Photoshop"
syscheck check "Blender"
syscheck check "Visual Studio Code"
```

### Advanced Compatibility Check with Custom Requirements
```bash
# Create requirements file
cat > game_requirements.json << EOF
{
  "application": "AAA Game",
  "requirements": {
    "cpu": {
      "cores": 6,
      "frequency": 3.0
    },
    "memory": {
      "ram": 16
    },
    "storage": {
      "free": 50
    },
    "gpu": {
      "required": true,
      "memory": 8
    }
  }
}
EOF

# Check compatibility
syscheck check "AAA Game" --requirements game_requirements.json

# Save results to file
syscheck check "AAA Game" --requirements game_requirements.json --output results.json
```

### Batch Processing
```bash
# Check multiple applications and save results
for app in "Photoshop" "Blender" "Unity"; do
    syscheck check "$app" --output "${app}_compatibility.json"
done
```

## Troubleshooting

### Common Issues

#### "No API key found" Error
**Problem**: You haven't set up your Groq API key.
**Solution**: 
```bash
syscheck setup
```

#### "Failed to store API key" Error
**Problem**: Permission issues with system keyring.
**Solution**: 
- Run as administrator (Windows) or with sudo (Linux/macOS)
- Check if keyring service is running

#### "Connection Error" During Analysis
**Problem**: Network connectivity issues.
**Solution**: 
- Check internet connection
- Verify firewall settings
- Try again later (API might be temporarily unavailable)

#### Inaccurate System Information
**Problem**: Some hardware details appear incorrect.
**Solution**: 
- Update system drivers
- Run as administrator for better hardware access
- Check if virtualization affects detection

### Debug Mode
For detailed error information, run commands with Python's verbose flag:
```bash
python -m src.cli system-info --json
```

### Getting Help
- Use `--help` with any command for detailed usage information
- Check the project's GitHub issues page
- Review the troubleshooting section in this guide

## Advanced Usage

### Integration with Other Tools

#### PowerShell Integration (Windows)
```powershell
# Get system info and process with PowerShell
$systemInfo = syscheck system-info --json | ConvertFrom-Json
Write-Host "CPU Cores: $($systemInfo.cpu.cores.physical)"
Write-Host "RAM: $([math]::Round($systemInfo.memory.total / 1GB, 2)) GB"
```

#### Bash Integration (Linux/macOS)
```bash
#!/bin/bash
# Automated compatibility checking script
SYSTEM_INFO=$(syscheck system-info --json)
RAM_GB=$(echo $SYSTEM_INFO | jq '.memory.total / 1073741824 | floor')

if [ $RAM_GB -ge 16 ]; then
    echo "System has sufficient RAM for development work"
else
    echo "Consider upgrading RAM for better performance"
fi
```

#### Python Integration
```python
import subprocess
import json

# Get system information programmatically
result = subprocess.run(['syscheck', 'system-info', '--json'], 
                       capture_output=True, text=True)
system_info = json.loads(result.stdout)

print(f"CPU: {system_info['cpu']['model']}")
print(f"RAM: {system_info['memory']['total'] / (1024**3):.1f} GB")
```

### Custom Requirements Templates

#### Gaming PC Requirements
```json
{
  "application": "Gaming PC",
  "requirements": {
    "cpu": {"cores": 6, "frequency": 3.5},
    "memory": {"ram": 16},
    "storage": {"free": 100},
    "gpu": {"required": true, "memory": 8}
  }
}
```

#### Development Workstation
```json
{
  "application": "Development Workstation",
  "requirements": {
    "cpu": {"cores": 8, "frequency": 2.8},
    "memory": {"ram": 32},
    "storage": {"free": 200}
  }
}
```

#### Video Editing Setup
```json
{
  "application": "Video Editing",
  "requirements": {
    "cpu": {"cores": 12, "frequency": 3.0},
    "memory": {"ram": 64},
    "storage": {"free": 500},
    "gpu": {"required": true, "memory": 16}
  }
}
```

## API Reference

### System Information Structure

The system information is returned as a JSON object with the following structure:

```json
{
  "os": {
    "system": "Windows|Linux|Darwin",
    "release": "version_string",
    "version": "detailed_version",
    "architecture": "32-bit|64-bit",
    "hostname": "computer_name",
    "platform": "platform_identifier"
  },
  "cpu": {
    "model": "processor_name",
    "manufacturer": "vendor_name",
    "architecture": 32|64,
    "cores": {
      "physical": number,
      "logical": number
    },
    "frequency": {
      "current": mhz,
      "min": mhz,
      "max": mhz
    }
  },
  "memory": {
    "total": bytes,
    "available": bytes,
    "used": bytes,
    "percent_used": percentage,
    "swap": {
      "total": bytes,
      "used": bytes,
      "free": bytes,
      "percent_used": percentage
    }
  },
  "storage": {
    "partitions": [
      {
        "device": "device_name",
        "mountpoint": "mount_path",
        "filesystem": "fs_type",
        "total": bytes,
        "used": bytes,
        "free": bytes,
        "percent_used": percentage
      }
    ]
  },
  "gpu": {
    "devices": [
      {
        "name": "gpu_name",
        "vendor": "manufacturer",
        "memory": "memory_info",
        "driver_version": "version"
      }
    ]
  },
  "performance": {
    "cpu_percent": percentage,
    "memory_percent": percentage,
    "boot_time": timestamp,
    "uptime_seconds": seconds
  }
}
```

### Compatibility Analysis Result Structure

```json
{
  "compatible": boolean,
  "confidence": percentage,
  "issues": ["list", "of", "issues"],
  "recommendations": ["list", "of", "recommendations"],
  "detailed_analysis": "comprehensive_text_analysis"
}
```

---

## Support and Contributing

### Getting Support
- **Documentation**: This user guide and README.md
- **Issues**: Report bugs on GitHub Issues
- **Community**: Join discussions in GitHub Discussions

### Contributing
We welcome contributions! See CONTRIBUTING.md for guidelines on:
- Code style and standards
- Testing requirements
- Pull request process
- Development setup

### License
This project is licensed under the MIT License. See LICENSE file for details.

---

*Last updated: January 2025*
*Version: 1.0.0*