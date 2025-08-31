"""Setup script for the system compatibility checker."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="system-compat-checker",
    version="1.0.0",
    author="System Compatibility Checker Team",
    author_email="contact@system-compat-checker.dev",
    description="A cross-platform CLI tool for checking system compatibility with AI-powered analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/system-compat-checker",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/system-compat-checker/issues",
        "Source": "https://github.com/yourusername/system-compat-checker",
        "Documentation": "https://github.com/yourusername/system-compat-checker/tree/main/docs",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Environment :: Console",
    ],
    keywords="system compatibility checker hardware requirements analysis CLI",
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.28.0",
        "keyring>=24.0.0",
        "rich>=13.0.0",
        "psutil>=5.9.0",
        "platformdirs>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "black>=22.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "syscheck=system_compat_checker.cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.ps1"],
    },
)