# PyPI Upload Guide for System Compatibility Checker

## ✅ Pre-Upload Checklist

### 1. Verify Project is Ready
```bash
python release.py
```
This should show "✅ All checks passed! Project is ready for release."

### 2. Install Required Tools
```bash
pip install --upgrade pip setuptools wheel twine build
```

### 3. Verify Package Information
Check that these files have correct information:
- `setup.py` - Package metadata
- `pyproject.toml` - Modern Python packaging configuration
- `README.md` - Will be used as PyPI description
- `LICENSE` - MIT license included

## 🚀 Upload Process

### Step 1: Clean Build Environment
```bash
# Remove any existing build artifacts
rm -rf build/ dist/ *.egg-info/
```

### Step 2: Build the Package
```bash
# Build using modern Python build system
python -m build

# Or using setuptools (alternative)
python setup.py sdist bdist_wheel
```

This creates:
- `dist/system-compat-checker-1.0.0.tar.gz` (source distribution)
- `dist/system_compat_checker-1.0.0-py3-none-any.whl` (wheel distribution)

### Step 3: Verify the Build
```bash
# Check the contents
twine check dist/*

# Test installation locally
pip install dist/system_compat_checker-1.0.0-py3-none-any.whl
syscheck version
```

### Step 4: Upload to Test PyPI (Recommended First)
```bash
# Upload to Test PyPI first
twine upload --repository testpypi dist/*
```

You'll need:
- TestPyPI account: https://test.pypi.org/account/register/
- API token from: https://test.pypi.org/manage/account/token/

### Step 5: Test Installation from Test PyPI
```bash
# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ system-compat-checker

# Test the installation
syscheck version
syscheck --help
```

### Step 6: Upload to Production PyPI
```bash
# Upload to production PyPI
twine upload dist/*
```

You'll need:
- PyPI account: https://pypi.org/account/register/
- API token from: https://pypi.org/manage/account/token/

## 🔐 Authentication Setup

### Option 1: API Tokens (Recommended)
1. Create API token on PyPI/TestPyPI
2. Create `~/.pypirc` file:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_API_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_API_TOKEN_HERE
```

### Option 2: Interactive Login
Twine will prompt for username/password if no config is found.

## 📋 Post-Upload Checklist

### 1. Verify PyPI Page
- Visit: https://pypi.org/project/system-compat-checker/
- Check description, metadata, and download files

### 2. Test Installation
```bash
# Fresh environment test
pip install system-compat-checker
syscheck version
```

### 3. Update Documentation
- Add PyPI badge to README
- Update installation instructions
- Create GitHub release

### 4. Tag the Release
```bash
git tag v1.0.0
git push origin v1.0.0
```

## 🛠 Troubleshooting

### Common Issues

**"Package already exists"**
- Increment version number in `setup.py` and `pyproject.toml`
- PyPI doesn't allow overwriting existing versions

**"Invalid distribution"**
- Run `twine check dist/*` to identify issues
- Ensure README.md is valid markdown

**"Authentication failed"**
- Verify API token is correct
- Check `~/.pypirc` configuration

**"Missing dependencies"**
- Ensure all dependencies are listed in `setup.py`
- Test in clean virtual environment

### Build Issues
```bash
# Clean everything and rebuild
rm -rf build/ dist/ *.egg-info/
python -m build
```

## 📊 Package Statistics

After upload, you can monitor:
- Download statistics: https://pypistats.org/packages/system-compat-checker
- Package health: https://pypi.org/project/system-compat-checker/

## 🎯 Success Criteria

✅ Package uploads without errors  
✅ PyPI page displays correctly  
✅ Installation works: `pip install system-compat-checker`  
✅ CLI works: `syscheck version`  
✅ All features functional  

## 📝 Version Management

For future releases:
1. Update version in `setup.py` and `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run `python release.py` to verify
4. Build and upload new version
5. Create GitHub release tag

---

**Current Status**: ✅ Ready for PyPI upload  
**Version**: 1.0.0  
**Last Verified**: January 30, 2025