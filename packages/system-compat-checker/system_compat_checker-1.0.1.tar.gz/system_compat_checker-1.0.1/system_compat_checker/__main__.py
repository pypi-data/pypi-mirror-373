"""
Main entry point for system_compat_checker when run as a module.
This allows users to run: python -m system_compat_checker
"""

from .cli import cli

if __name__ == "__main__":
    cli()