"""Windows system information collector module.

This module uses PowerShell to collect system information on Windows.
"""

import json
import os
import subprocess
from typing import Dict, Any


class WindowsInfoCollector:
    """Windows system information collector."""
    
    def __init__(self):
        """Initialize the Windows info collector."""
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Path to the PowerShell script (in the same directory as this script)
        self.ps_script_path = os.path.join(current_dir, "optimized_system_info.ps1")
    
    def collect(self) -> Dict[str, Any]:
        """Collect system information using PowerShell.
        
        Returns:
            Dict[str, Any]: A dictionary containing system information.
        """
        try:
            # Run the PowerShell script and capture its output
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", self.ps_script_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse the JSON output
            raw_info = json.loads(result.stdout)
            
            # Transform to expected format
            system_info = self._transform_to_standard_format(raw_info)
            return system_info
        
        except subprocess.CalledProcessError as e:
            # Handle PowerShell execution errors
            error_message = f"PowerShell script execution failed: {e.stderr}"
            return {"error": error_message}
        
        except json.JSONDecodeError as e:
            # Handle JSON parsing errors
            error_message = f"Failed to parse PowerShell output as JSON: {e}"
            return {"error": error_message}
        
        except Exception as e:
            # Handle any other errors
            error_message = f"An unexpected error occurred: {str(e)}"
            return {"error": error_message}
    
    def _transform_to_standard_format(self, raw_info: Dict[str, Any]) -> Dict[str, Any]:
        """Transform PowerShell output to standard format expected by CLI.
        
        Args:
            raw_info: Raw system information from PowerShell script
            
        Returns:
            Dict[str, Any]: Transformed system information
        """
        transformed = {}
        
        # Transform OS information
        if "OperatingSystem" in raw_info:
            os_data = raw_info["OperatingSystem"]
            transformed["os"] = {
                "system": "Windows",
                "name": os_data.get("Name", "Unknown"),
                "version": os_data.get("Version", "Unknown"),
                "architecture": os_data.get("Architecture", "Unknown"),
                "build_number": os_data.get("BuildNumber", "Unknown"),
                "total_memory": os_data.get("TotalVisibleMemorySize", "Unknown"),
                "free_memory": os_data.get("FreePhysicalMemory", "Unknown")
            }
        
        # Transform CPU information
        if "CPU" in raw_info:
            cpu_data = raw_info["CPU"]
            transformed["cpu"] = {
                "processor": cpu_data.get("Name", "Unknown"),
                "manufacturer": cpu_data.get("Manufacturer", "Unknown"),
                "architecture": cpu_data.get("Architecture", "Unknown"),
                "cores": {
                    "physical": cpu_data.get("NumberOfCores", 0),
                    "logical": cpu_data.get("NumberOfLogicalProcessors", 0)
                },
                "frequency": {
                    "current": self._parse_frequency(cpu_data.get("CurrentClockSpeed", "0 MHz")),
                    "max": self._parse_frequency(cpu_data.get("MaxClockSpeed", "0 MHz"))
                },
                "cache": {
                    "l2": cpu_data.get("L2CacheSize", "Unknown"),
                    "l3": cpu_data.get("L3CacheSize", "Unknown")
                }
            }
        
        # Transform Memory information
        if "Memory" in raw_info:
            memory_data = raw_info["Memory"]
            total_bytes = self._parse_memory_size(memory_data.get("TotalPhysicalMemory", "0 GB"))
            
            transformed["memory"] = {
                "total": total_bytes,
                "modules": memory_data.get("NumberOfModules", 0),
                "module_details": memory_data.get("Modules", [])
            }
        
        # Transform Graphics information
        if "Graphics" in raw_info:
            graphics_data = raw_info["Graphics"]
            gpu_devices = []
            
            cards = graphics_data.get("Cards", [])
            if isinstance(cards, dict):
                cards = [cards]
            
            for card in cards:
                gpu_devices.append({
                    "name": card.get("Name", "Unknown"),
                    "memory": card.get("AdapterRAM", "Unknown"),
                    "driver": card.get("DriverVersion", "Unknown"),
                    "processor": card.get("VideoProcessor", "Unknown")
                })
            
            transformed["gpu"] = {"devices": gpu_devices}
        
        # Transform Storage information
        if "Storage" in raw_info:
            storage_data = raw_info["Storage"]
            partitions_data = storage_data.get("partitions", [])
            if isinstance(partitions_data, dict):
                partitions_data = [partitions_data]
            
            partitions = []
            for partition in partitions_data:
                partitions.append({
                    "device": partition.get("device", "Unknown"),
                    "mountpoint": partition.get("mountpoint", "Unknown"),
                    "total": partition.get("total", 0),
                    "used": partition.get("used", 0),
                    "free": partition.get("free", 0),
                    "percent_used": partition.get("percent_used", 0),
                    "filesystem": partition.get("filesystem", "Unknown"),
                    "volume_label": partition.get("volume_label", "Unknown")
                })
            
            transformed["storage"] = {"partitions": partitions}
        
        # Transform Network information
        if "Network" in raw_info:
            network_data = raw_info["Network"]
            transformed["network"] = {
                "adapters": network_data.get("Adapters", [])
            }
        
        # Transform System information
        if "System" in raw_info:
            system_data = raw_info["System"]
            transformed["system"] = {
                "manufacturer": system_data.get("Manufacturer", "Unknown"),
                "model": system_data.get("Model", "Unknown"),
                "system_type": system_data.get("SystemType", "Unknown"),
                "domain": system_data.get("Domain", "Unknown"),
                "username": system_data.get("UserName", "Unknown")
            }
        
        return transformed
    
    def _parse_frequency(self, freq_str: str) -> float:
        """Parse frequency string to float value in MHz.
        
        Args:
            freq_str: Frequency string like "3600 MHz"
            
        Returns:
            float: Frequency in MHz
        """
        try:
            return float(freq_str.replace(" MHz", "").replace(",", ""))
        except (ValueError, AttributeError):
            return 0.0
    
    def _parse_memory_size(self, size_str: str) -> int:
        """Parse memory size string to bytes.
        
        Args:
            size_str: Size string like "16 GB"
            
        Returns:
            int: Size in bytes
        """
        try:
            size_str = size_str.upper().replace(",", "")
            if "GB" in size_str:
                return int(float(size_str.replace(" GB", "")) * 1024 ** 3)
            elif "MB" in size_str:
                return int(float(size_str.replace(" MB", "")) * 1024 ** 2)
            elif "KB" in size_str:
                return int(float(size_str.replace(" KB", "")) * 1024)
            else:
                return int(size_str.replace(" B", ""))
        except (ValueError, AttributeError):
            return 0