# Example Requirements Files

This directory contains example requirements files that demonstrate how to define system requirements for different types of applications.

## Available Examples

### Gaming Applications

#### 1. Gaming PC Setup (`gaming_pc_requirements.json`)
General high-end gaming computer requirements:
- 6+ CPU cores at 3.5+ GHz
- 16 GB RAM with 12 GB available
- 100 GB free SSD storage
- NVIDIA GPU with 8+ GB VRAM
- Windows 10+ or Linux 5.4+

#### 2. Valorant (`valorant.json`)
Riot Games Valorant competitive gaming requirements:
- 4+ CPU cores at 3.0+ GHz
- 4 GB RAM with 3 GB available
- 8 GB free SSD storage
- NVIDIA GPU with 1+ GB VRAM
- Windows 7+

#### 3. Cyberpunk 2077 (`cyberpunk_2077.json`)
CD Projekt RED Cyberpunk 2077 recommended requirements:
- 8+ CPU cores at 3.2+ GHz
- 12 GB RAM with 10 GB available
- 70 GB free SSD storage
- NVIDIA GPU with 6+ GB VRAM
- Windows 10+

#### 4. Microsoft Flight Simulator (`microsoft_flight_simulator.json`)
Microsoft Flight Simulator 2020 ideal requirements:
- 8+ CPU cores at 3.0+ GHz
- 32 GB RAM with 28 GB available
- 150 GB free SSD storage
- NVIDIA GPU with 8+ GB VRAM
- Windows 10+

### Professional Applications

#### 5. Adobe Premiere Pro (`adobe_premiere_pro.json`)
Adobe Premiere Pro 2024 professional requirements:
- 8+ CPU cores at 2.8+ GHz
- 32 GB RAM with 24 GB available
- 8 GB free SSD storage
- NVIDIA GPU with 4+ GB VRAM
- Windows 10+ or macOS 12.0+

## Usage Examples

```bash
# Test with specific requirements
python -m src.cli check "Valorant" --requirements examples/valorant.json

# Test without requirements (uses AI knowledge)
python -m src.cli check "Minecraft Java Edition"

# Get JSON output
python -m src.cli check "Cyberpunk 2077" -r examples/cyberpunk_2077.json --json

# Save results to file
python -m src.cli check "Adobe Premiere Pro" -r examples/adobe_premiere_pro.json -o results.json
```

## Creating Custom Requirements

Use this JSON structure for your own applications:

```json
{
  "application": "Your Application Name",
  "description": "Brief description of the application",
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
      "type": "SSD"
    },
    "gpu": {
      "required": true,
      "memory": 4,
      "vendor": "NVIDIA"
    },
    "os": {
      "supported_systems": ["Windows", "Linux", "macOS"],
      "min_version": {
        "Windows": "10",
        "Linux": "5.0",
        "macOS": "10.15"
      }
    }
  }
}
```

## Field Reference

- **CPU**: `cores` (physical), `frequency` (GHz), `architecture` (32/64)
- **Memory**: `ram` (total GB), `available` (free GB)
- **Storage**: `free` (GB), `type` (SSD/HDD)
- **GPU**: `required` (boolean), `memory` (GB), `vendor` (NVIDIA/AMD/Intel)
- **OS**: `supported_systems` (array), `min_version` (object)