"""System information collector module.

This module detects the platform and uses the appropriate collector to gather system information.
"""

import platform
from typing import Dict, Any

# Import platform-specific collectors
from .windows_info import WindowsInfoCollector
from .posix_info import PosixInfoCollector


def get_system_info() -> Dict[str, Any]:
    """Collect system information based on the current platform.
    
    Returns:
        Dict[str, Any]: A dictionary containing system information.
    """
    system = platform.system()
    
    if system == "Windows":
        collector = WindowsInfoCollector()
    else:  # POSIX (Linux, macOS)
        collector = PosixInfoCollector()
    
    return collector.collect()