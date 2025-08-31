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
        # Path to the PowerShell script (one directory up from the current script)
        self.ps_script_path = os.path.join(os.path.dirname(current_dir), "optimized_system_info.ps1")
    
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
            system_info = json.loads(result.stdout)
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