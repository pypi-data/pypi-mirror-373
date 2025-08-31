#!/usr/bin/env python3
"""
Release preparation script for System Compatibility Checker.
This script performs final checks and preparations for release.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_project_structure():
    """Verify project structure is correct."""
    print("🔍 Checking project structure...")
    
    required_files = [
        "setup.py",
        "README.md",
        "LICENSE",
        "requirements.txt",
        "system_compat_checker/__init__.py",
        "system_compat_checker/cli.py",
        "system_compat_checker/system_info.py",
        "system_compat_checker/storage.py",
        "system_compat_checker/groq_analyzer.py",
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ Project structure is complete")
    return True

def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    
    success, stdout, stderr = run_command("python -m pytest tests/ -v")
    if success:
        print("✅ All tests passed")
        return True
    else:
        print(f"❌ Tests failed:\n{stderr}")
        return False

def check_installation():
    """Test installation in development mode."""
    print("📦 Testing installation...")
    
    success, stdout, stderr = run_command("pip install -e .")
    if success:
        print("✅ Installation successful")
        return True
    else:
        print(f"❌ Installation failed:\n{stderr}")
        return False

def test_cli_commands():
    """Test basic CLI functionality."""
    print("⚡ Testing CLI commands...")
    
    # Test version command
    success, stdout, stderr = run_command("python -m system_compat_checker.cli version")
    if not success:
        print(f"❌ Version command failed:\n{stderr}")
        return False
    
    # Test help command
    success, stdout, stderr = run_command("python -m system_compat_checker.cli --help")
    if not success:
        print(f"❌ Help command failed:\n{stderr}")
        return False
    
    # Test system-info command
    success, stdout, stderr = run_command("python -m system_compat_checker.cli system-info --json")
    if not success:
        print(f"❌ System-info command failed:\n{stderr}")
        return False
    
    print("✅ CLI commands working correctly")
    return True

def check_examples():
    """Verify example files are valid JSON."""
    print("📋 Checking example files...")
    
    examples_dir = Path("examples")
    if not examples_dir.exists():
        print("❌ Examples directory not found")
        return False
    
    json_files = list(examples_dir.glob("*.json"))
    if not json_files:
        print("❌ No example JSON files found")
        return False
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {json_file}: {e}")
            return False
    
    print(f"✅ All {len(json_files)} example files are valid")
    return True

def clean_build_artifacts():
    """Remove build artifacts and cache files."""
    print("🧹 Cleaning build artifacts...")
    
    patterns_to_remove = [
        "build/",
        "dist/",
        "*.egg-info/",
        "__pycache__/",
        "*.pyc",
        ".pytest_cache/",
    ]
    
    for pattern in patterns_to_remove:
        success, stdout, stderr = run_command(f"find . -name '{pattern}' -exec rm -rf {{}} + 2>/dev/null || true")
    
    print("✅ Build artifacts cleaned")

def main():
    """Main release preparation function."""
    print("🚀 System Compatibility Checker - Release Preparation")
    print("=" * 60)
    
    checks = [
        ("Project Structure", check_project_structure),
        ("Installation", check_installation),
        ("CLI Commands", test_cli_commands),
        ("Example Files", check_examples),
        ("Tests", run_tests),
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                failed_checks.append(check_name)
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
            failed_checks.append(check_name)
        print()
    
    # Clean up regardless of check results
    clean_build_artifacts()
    
    print("=" * 60)
    if failed_checks:
        print(f"❌ Release preparation failed. Issues found in: {', '.join(failed_checks)}")
        print("Please fix the issues above before releasing.")
        sys.exit(1)
    else:
        print("✅ All checks passed! Project is ready for release.")
        print("\nNext steps:")
        print("1. Update version in setup.py and src/__init__.py")
        print("2. Update CHANGELOG.md")
        print("3. Create git tag: git tag v1.0.0")
        print("4. Build package: python setup.py sdist bdist_wheel")
        print("5. Upload to PyPI: twine upload dist/*")

if __name__ == "__main__":
    main()