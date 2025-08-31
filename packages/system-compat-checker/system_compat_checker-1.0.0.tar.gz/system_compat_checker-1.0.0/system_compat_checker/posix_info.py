"""POSIX system information collector module.

This module uses psutil and platform-specific commands to collect system information on POSIX systems (Linux, macOS).
"""

import platform
import subprocess
import os
from typing import Dict, Any

import psutil


class PosixInfoCollector:
    """POSIX system information collector for Linux and macOS."""
    
    def __init__(self):
        """Initialize the POSIX info collector."""
        self.system = platform.system()
    
    def collect(self) -> Dict[str, Any]:
        """Collect system information using psutil and platform-specific commands.
        
        Returns:
            Dict[str, Any]: A dictionary containing system information.
        """
        system_info = {
            "cpu": self._get_cpu_info(),
            "memory": self._get_memory_info(),
            "storage": self._get_storage_info(),
            "os": self._get_os_info(),
            "gpu": self._get_gpu_info(),
            "performance": self._get_performance_info()
        }
        
        return system_info
    
    def _get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information.
        
        Returns:
            Dict[str, Any]: CPU information.
        """
        cpu_info = {
            "processor": platform.processor(),
            "architecture": platform.machine(),
            "cores": {
                "physical": psutil.cpu_count(logical=False) or 0,
                "logical": psutil.cpu_count(logical=True) or 0
            },
            "frequency": {
                "current": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                "min": psutil.cpu_freq().min if psutil.cpu_freq() and psutil.cpu_freq().min else 0,
                "max": psutil.cpu_freq().max if psutil.cpu_freq() and psutil.cpu_freq().max else 0
            }
        }
        
        # Add Linux-specific CPU info
        if self.system == "Linux":
            try:
                with open("/proc/cpuinfo", "r") as f:
                    cpuinfo = f.read()
                
                # Extract model name
                for line in cpuinfo.split("\n"):
                    if "model name" in line:
                        cpu_info["model"] = line.split(":")[1].strip()
                        break
            except Exception:
                cpu_info["model"] = "Unknown"
        
        # Add macOS-specific CPU info
        elif self.system == "Darwin":  # macOS
            try:
                result = subprocess.run(
                    ["sysctl", "-n", "machdep.cpu.brand_string"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                cpu_info["model"] = result.stdout.strip()
            except Exception:
                cpu_info["model"] = "Unknown"
        
        return cpu_info
    
    def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory information.
        
        Returns:
            Dict[str, Any]: Memory information.
        """
        virtual_memory = psutil.virtual_memory()
        swap_memory = psutil.swap_memory()
        
        memory_info = {
            "total": virtual_memory.total,
            "available": virtual_memory.available,
            "used": virtual_memory.used,
            "percent_used": virtual_memory.percent,
            "swap": {
                "total": swap_memory.total,
                "used": swap_memory.used,
                "free": swap_memory.free,
                "percent_used": swap_memory.percent
            }
        }
        
        return memory_info
    
    def _get_storage_info(self) -> Dict[str, Any]:
        """Get storage information.
        
        Returns:
            Dict[str, Any]: Storage information.
        """
        partitions = []
        
        for partition in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "filesystem": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent_used": usage.percent
                })
            except (PermissionError, FileNotFoundError):
                # Skip partitions that can't be accessed
                continue
        
        storage_info = {
            "partitions": partitions,
            "io_counters": self._get_disk_io_stats()
        }
        
        return storage_info
    
    def _get_disk_io_stats(self) -> Dict[str, Any]:
        """Get disk I/O statistics.
        
        Returns:
            Dict[str, Any]: Disk I/O statistics.
        """
        try:
            io_counters = psutil.disk_io_counters()
            return {
                "read_count": io_counters.read_count,
                "write_count": io_counters.write_count,
                "read_bytes": io_counters.read_bytes,
                "write_bytes": io_counters.write_bytes,
                "read_time": io_counters.read_time,
                "write_time": io_counters.write_time
            }
        except Exception:
            return {}
    
    def _get_os_info(self) -> Dict[str, Any]:
        """Get operating system information.
        
        Returns:
            Dict[str, Any]: OS information.
        """
        os_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "platform": platform.platform(),
            "hostname": platform.node()
        }
        
        # Add Linux-specific OS info
        if self.system == "Linux":
            try:
                with open("/etc/os-release", "r") as f:
                    os_release = f.read()
                
                for line in os_release.split("\n"):
                    if line.startswith("PRETTY_NAME="):
                        os_info["distribution"] = line.split("=")[1].strip('"')
                        break
            except Exception:
                os_info["distribution"] = "Unknown"
        
        # Add macOS-specific OS info
        elif self.system == "Darwin":  # macOS
            try:
                result = subprocess.run(
                    ["sw_vers", "-productVersion"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                os_info["mac_version"] = result.stdout.strip()
            except Exception:
                os_info["mac_version"] = "Unknown"
        
        return os_info
    
    def _get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information.
        
        Returns:
            Dict[str, Any]: GPU information.
        """
        gpu_info = {"devices": []}
        
        # Linux GPU detection
        if self.system == "Linux":
            try:
                # Try to get NVIDIA GPU info using nvidia-smi
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    for line in result.stdout.strip().split("\n"):
                        if line.strip():
                            name, memory, driver = [item.strip() for item in line.split(",")]
                            gpu_info["devices"].append({
                                "name": name,
                                "memory": memory,
                                "driver": driver,
                                "vendor": "NVIDIA"
                            })
            except Exception:
                pass
            
            # Try to get AMD GPU info
            try:
                if os.path.exists("/sys/class/drm"):
                    for card in os.listdir("/sys/class/drm"):
                        if card.startswith("card") and not card.endswith("dev"):
                            try:
                                with open(f"/sys/class/drm/{card}/device/vendor", "r") as f:
                                    vendor_id = f.read().strip()
                                
                                with open(f"/sys/class/drm/{card}/device/product", "r") as f:
                                    product_name = f.read().strip()
                                
                                gpu_info["devices"].append({
                                    "name": product_name,
                                    "vendor_id": vendor_id,
                                    "vendor": "AMD" if "0x1002" in vendor_id else "Unknown"
                                })
                            except Exception:
                                continue
            except Exception:
                pass
        
        # macOS GPU detection
        elif self.system == "Darwin":  # macOS
            try:
                result = subprocess.run(
                    ["system_profiler", "SPDisplaysDataType"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    current_gpu = {}
                    for line in result.stdout.split("\n"):
                        line = line.strip()
                        if "Chipset Model:" in line:
                            current_gpu["name"] = line.split(":")[1].strip()
                        elif "VRAM" in line:
                            current_gpu["memory"] = line.split(":")[1].strip()
                        elif "Vendor:" in line:
                            current_gpu["vendor"] = line.split(":")[1].strip()
                            gpu_info["devices"].append(current_gpu)
                            current_gpu = {}
            except Exception:
                pass
        
        return gpu_info
    
    def _get_performance_info(self) -> Dict[str, Any]:
        """Get performance information.
        
        Returns:
            Dict[str, Any]: Performance information.
        """
        performance_info = {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "per_cpu_percent": psutil.cpu_percent(interval=0.1, percpu=True),
            "memory_percent": psutil.virtual_memory().percent,
            "boot_time": psutil.boot_time(),
            "load_avg": os.getloadavg() if hasattr(os, "getloadavg") else [0, 0, 0]
        }
        
        return performance_info