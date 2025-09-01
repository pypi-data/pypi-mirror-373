# Release Guide for Octavia LoxiLB Driver

## Overview

This guide provides step-by-step instructions for releasing new versions of the octavia-loxilb-driver package.

## Pre-Release Checklist

### 1. Code Quality
- [ ] All tests pass
- [ ] Code coverage meets requirements
- [ ] Documentation is up to date
- [ ] CHANGELOG.md is updated with new features/fixes
- [ ] No critical security vulnerabilities

### 2. Version Management
- [ ] Update version in `octavia_loxilb_driver/version.py`
- [ ] Update version in any documentation that references specific versions
- [ ] Create git tag for the release

### 3. Dependencies
- [ ] Review and update `requirements.txt` if needed
- [ ] Ensure compatibility with latest OpenStack releases
- [ ] Test with supported Python versions (3.8, 3.9, 3.10, 3.11)

## Release Process

### Step 1: Prepare the Release

```bash
# 1. Update version
vim octavia_loxilb_driver/version.py

# 2. Update CHANGELOG.md
vim CHANGELOG.md

# 3. Commit changes
git add .
git commit -m "Prepare release v1.0.0"
git push origin main
```

### Step 2: Create Git Tag

```bash
# Create and push tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### Step 3: Build Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Install build tools
pip install build twine

# Build package
python -m build
```

### Step 4: Test Package Locally

```bash
# Test installation from local build
pip install dist/octavia-loxilb-driver-1.0.0.tar.gz

# Verify installation
python -c "import octavia_loxilb_driver; print(octavia_loxilb_driver.__version__)"

# Test entry points
octavia-loxilb-health-check --help
```

### Step 5: Upload to Test PyPI (Optional)

```bash
# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ octavia-loxilb-driver
```

### Step 6: Upload to PyPI

```bash
# Upload to PyPI
twine upload dist/*
```

### Step 7: Verify Release

```bash
# Install from PyPI
pip install octavia-loxilb-driver

# Verify version
python -c "import octavia_loxilb_driver; print(octavia_loxilb_driver.__version__)"
```

## Post-Release Tasks

### 1. Update Documentation
- [ ] Update installation instructions
- [ ] Update any version-specific documentation
- [ ] Announce release on mailing lists/forums

### 2. Prepare for Next Development Cycle
- [ ] Update version to next development version (e.g., 1.1.0-dev)
- [ ] Create milestone for next release

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: New functionality in backward-compatible manner
- **PATCH** version: Backward-compatible bug fixes

Examples:
- `1.0.0` - Initial stable release
- `1.0.1` - Bug fix release
- `1.1.0` - New features, backward compatible
- `2.0.0` - Breaking changes

## PyPI Configuration

### Setup PyPI Account
1. Create account at https://pypi.org/
2. Enable 2FA for security
3. Create API token for automated uploads

### Configure ~/.pypirc
```ini
[distutils]
index-servers = pypi testpypi

[pypi]
username = __token__
password = your-pypi-api-token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = your-testpypi-api-token
```

## Automated Release (GitHub Actions)

Consider setting up GitHub Actions for automated releases:

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags:
      - 'v*'
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## Rollback Procedure

If a release has critical issues:

1. **Immediate**: Remove the problematic version from PyPI (if possible)
2. **Communication**: Notify users via mailing lists/documentation
3. **Fix**: Prepare hotfix release with incremented patch version
4. **Release**: Follow normal release process for hotfix

## Security Releases

For security-related releases:
1. Follow responsible disclosure practices
2. Coordinate with OpenStack security team if needed
3. Clearly mark security releases in CHANGELOG.md
4. Consider backporting fixes to supported versions

## Support and Maintenance

- **Active Support**: Latest major version
- **Security Fixes**: Latest major + previous major version
- **End of Life**: Clearly communicate when versions will no longer be supported
