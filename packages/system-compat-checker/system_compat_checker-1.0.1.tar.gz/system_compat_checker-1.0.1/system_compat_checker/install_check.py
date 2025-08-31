"""
Installation verification and PATH setup helper.
"""

import os
import sys
import site
import subprocess
from pathlib import Path


def get_scripts_dir():
    """Get the Python Scripts directory for the current installation."""
    if hasattr(site, 'USER_BASE'):
        if sys.platform == "win32":
            scripts_dir = Path(site.USER_BASE) / "Python313" / "Scripts"
        else:
            scripts_dir = Path(site.USER_BASE) / "bin"
    else:
        # Fallback for older Python versions
        scripts_dir = Path(sys.prefix) / "Scripts" if sys.platform == "win32" else Path(sys.prefix) / "bin"
    
    return scripts_dir


def is_in_path(directory):
    """Check if a directory is in the system PATH."""
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)
    return str(directory) in path_dirs


def check_installation():
    """Check if syscheck command is properly installed and accessible."""
    scripts_dir = get_scripts_dir()
    
    print("🔍 System Compatibility Checker Installation Check")
    print("=" * 50)
    
    # Check if scripts directory exists
    if scripts_dir.exists():
        print(f"✅ Scripts directory found: {scripts_dir}")
    else:
        print(f"❌ Scripts directory not found: {scripts_dir}")
        return False
    
    # Check if syscheck executable exists
    syscheck_exe = scripts_dir / ("syscheck.exe" if sys.platform == "win32" else "syscheck")
    if syscheck_exe.exists():
        print(f"✅ syscheck executable found: {syscheck_exe}")
    else:
        print(f"❌ syscheck executable not found: {syscheck_exe}")
        return False
    
    # Check if scripts directory is in PATH
    if is_in_path(scripts_dir):
        print("✅ Scripts directory is in PATH")
        
        # Test the command
        try:
            result = subprocess.run(['syscheck', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ syscheck command works correctly")
                print(f"   Output: {result.stdout.strip()}")
                return True
            else:
                print("❌ syscheck command failed to run")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ syscheck command not accessible")
            return False
    else:
        print("⚠️  Scripts directory is NOT in PATH")
        print("\n📋 Solutions:")
        print("1. Add to PATH manually (recommended):")
        if sys.platform == "win32":
            print(f"   Add this to your PATH: {scripts_dir}")
            print("   Or run: python -m system_compat_checker")
        else:
            print(f"   export PATH=\"$PATH:{scripts_dir}\"")
        
        print("\n2. Use module syntax (always works):")
        print("   python -m system_compat_checker --help")
        
        return False


def print_usage_instructions():
    """Print usage instructions based on installation status."""
    if check_installation():
        print("\n🎉 Installation successful! You can use:")
        print("   syscheck --help")
        print("   syscheck setup YOUR_API_KEY")
        print("   syscheck check 'Application Name'")
    else:
        print("\n💡 Use this alternative (always works):")
        print("   python -m system_compat_checker --help")
        print("   python -m system_compat_checker setup YOUR_API_KEY")
        print("   python -m system_compat_checker check 'Application Name'")


if __name__ == "__main__":
    print_usage_instructions()