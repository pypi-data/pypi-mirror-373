# Antonnia Conversations SDK Deployment Guide

This guide explains how to build, test, and deploy the Antonnia Conversations Python SDK to PyPI.

## Prerequisites

1. **Python 3.8+** installed
2. **Build tools** installed:
   ```bash
   pip install build twine
   ```
3. **PyPI account** with API token
4. **TestPyPI account** (recommended for testing)

## Building the Package

### 1. Update Version

Update the version in `antonnia/conversations/__init__.py`:
```python
__version__ = "2.0.1"  # Increment as needed
```

### 2. Build Distributions

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build both source and wheel distributions
python -m build
```

This creates:
- `dist/antonnia-conversations-X.X.X.tar.gz` (source distribution)
- `dist/antonnia-conversations-X.X.X-py3-none-any.whl` (wheel distribution)

### 3. Verify Package Contents

```bash
# Check what's included in the wheel
python -m zipfile -l dist/antonnia-conversations-*.whl

# Check what's included in the source distribution
tar -tzf dist/antonnia-conversations-*.tar.gz
```

## Testing the Package

### 1. Test Local Installation

```bash
# Install from local wheel
pip install dist/antonnia-conversations-*.whl --force-reinstall

# Test import
python -c "from antonnia.conversations import Conversations; print(f'Version: {Conversations.__module__}')"
```

### 2. Test Package Functionality

```bash
# Run basic import test
python -c "
from antonnia.conversations import Conversations
from antonnia.conversations.types import MessageContentText
print('✅ All imports successful')
"
```

### 3. Upload to TestPyPI (Recommended)

```bash
# Upload to TestPyPI first for testing
python -m twine upload --repository testpypi dist/*

# Install from TestPyPI to test
pip install --index-url https://test.pypi.org/simple/ antonnia-conversations
```

## Production Deployment

### 1. Final Checks

- [ ] Version number updated
- [ ] CHANGELOG.md updated with new features/fixes
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Example code tested

### 2. Upload to PyPI

```bash
# Upload to production PyPI
python -m twine upload dist/*
```

### 3. Verify Deployment

```bash
# Install from PyPI
pip install antonnia-conversations

# Test installation
python -c "from antonnia.conversations import Conversations; print('✅ Installation successful')"
```

### 4. Create Git Tag

```bash
# Tag the release
git tag v2.0.0
git push origin v2.0.0
```

## Configuration Files

### PyPI Credentials

Create `~/.pypirc`:
```ini
[distutils]
index-servers = 
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-testpypi-token-here
```

### Twine Configuration

Create `~/.config/twine/configuration`:
```ini
[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-api-token-here
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Check that all dependencies are properly specified in `pyproject.toml`
2. **Version Conflicts**: Ensure version number is incremented and not already published
3. **Build Failures**: Check for syntax errors and missing files in `MANIFEST.in`
4. **Upload Failures**: Verify PyPI credentials and network connectivity

### Debug Commands

```bash
# Check package metadata
python -m build --wheel
python -m pip show antonnia-conversations

# Validate package before upload
python -m twine check dist/*

# Upload with verbose output
python -m twine upload --verbose dist/*
```

## Automation (Optional)

### GitHub Actions

Create `.github/workflows/publish.yml`:
```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## Security Notes

- **Never commit API tokens** to version control
- Use **API tokens** instead of username/password
- Store tokens in **environment variables** or secure configuration
- Use **TestPyPI** for testing before production uploads
- Enable **two-factor authentication** on PyPI account

## Versioning Guidelines

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (2.x.x): Breaking changes
- **MINOR** (x.1.x): New features (backward compatible)
- **PATCH** (x.x.1): Bug fixes (backward compatible)

Examples:
- `2.0.0` → `2.0.1`: Bug fix
- `2.0.1` → `2.1.0`: New feature
- `2.1.0` → `3.0.0`: Breaking change 