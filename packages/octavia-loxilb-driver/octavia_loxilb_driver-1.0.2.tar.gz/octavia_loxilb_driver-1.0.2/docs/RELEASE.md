# Release Guide for LoxiLB Octavia Driver

This guide covers the release process for the LoxiLB Octavia Driver, including PyPI package publishing and LoxiLB VM image releases.

## Overview

The LoxiLB Octavia Driver has two main release components:

1. **PyPI Package Release** - The driver software distributed via PyPI
2. **LoxiLB VM Image Release** - Pre-built QCOW2 images for OpenStack deployment

## Prerequisites

### Required Tools
- Python 3.8+
- `twine` for PyPI publishing
- `gh` CLI for GitHub releases
- `qemu-img` for image validation
- OpenStack credentials (for testing)

### Required Accounts & Tokens
- PyPI account with maintainer access to `octavia-loxilb-driver`
- GitHub account with write access to the repository
- GitHub Personal Access Token with `repo` permissions

### Initial Setup
```bash
# Install release tools
pip install twine build

# Install GitHub CLI
brew install gh  # macOS
# or
sudo apt install gh  # Ubuntu

# Authenticate with GitHub
gh auth login

# Configure PyPI credentials
cat > ~/.pypirc << EOF
[distutils]
index-servers = pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = YOUR_PYPI_TOKEN
EOF
```

## PyPI Package Release

### 1. Pre-Release Checklist

- [ ] All tests pass (`python -m pytest`)
- [ ] Code coverage meets requirements
- [ ] Documentation is updated
- [ ] `CHANGELOG.md` is updated with release notes
- [ ] Version is bumped in `octavia_loxilb_driver/version.py`
- [ ] No breaking changes without major version bump

### 2. Version Management

Update the version in `octavia_loxilb_driver/version.py`:

```python
__version__ = "1.2.3"
__version_info__ = (1, 2, 3)
```

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

### 3. Release Script

Create and run the PyPI release script:

```bash
#!/bin/bash
# scripts/release-pypi.sh

set -e

VERSION=$(python -c "from octavia_loxilb_driver.version import __version__; print(__version__)")
echo "Releasing version: $VERSION"

# Pre-release validation
echo "Running pre-release checks..."
python -m pytest tests/ -v
python -m flake8 octavia_loxilb_driver/
python setup.py check --strict

# Build distribution packages
echo "Building distribution packages..."
rm -rf dist/ build/ *.egg-info/
python -m build

# Validate packages
echo "Validating packages..."
twine check dist/*

# Upload to PyPI
echo "Uploading to PyPI..."
twine upload dist/*

# Create git tag
echo "Creating git tag..."
git tag "v$VERSION"
git push origin "v$VERSION"

# Create GitHub release
echo "Creating GitHub release..."
gh release create "v$VERSION" \
  --title "Release v$VERSION" \
  --notes-file CHANGELOG.md \
  --draft

echo "✓ PyPI release completed for version $VERSION"
echo "Please review and publish the GitHub release draft"
```

### 4. Testing Release

Before publishing to production PyPI, test with TestPyPI:

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ octavia-loxilb-driver==$VERSION

# Verify functionality
octavia-loxilb-setup --help
```

## LoxiLB VM Image Release

### 1. VM Image Preparation

The LoxiLB VM images should be prepared with:

- Latest LoxiLB software
- Optimized configuration for Octavia integration
- Security hardening
- Cloud-init support
- Proper sizing for different deployment profiles

### 2. Image Validation Script

```bash
#!/bin/bash
# scripts/validate-vm-image.sh

set -e

IMAGE_PATH="$1"
if [ -z "$IMAGE_PATH" ]; then
    echo "Usage: $0 <path-to-qcow2-image>"
    exit 1
fi

echo "Validating LoxiLB VM image: $IMAGE_PATH"

# Check file exists and format
if [ ! -f "$IMAGE_PATH" ]; then
    echo "ERROR: Image file not found"
    exit 1
fi

# Validate QCOW2 format
echo "Checking image format..."
qemu-img info "$IMAGE_PATH"

# Check image size (should be reasonable)
SIZE_MB=$(qemu-img info --output json "$IMAGE_PATH" | jq '.["virtual-size"]' | awk '{print int($1/1024/1024)}')
echo "Virtual size: ${SIZE_MB}MB"

if [ "$SIZE_MB" -gt 20000 ]; then
    echo "WARNING: Image is quite large (${SIZE_MB}MB)"
fi

# Check for required files (if mounted)
echo "Image validation completed"
```

### 3. VM Image Release Script

```bash
#!/bin/bash
# scripts/release-vm-image.sh

set -e

IMAGE_PATH="$1"
VERSION="$2"
DEPLOYMENT_TYPE="${3:-production}"

if [ -z "$IMAGE_PATH" ] || [ -z "$VERSION" ]; then
    echo "Usage: $0 <image-path> <version> [deployment-type]"
    echo "Example: $0 loxilb-vm.qcow2 1.2.3 production"
    exit 1
fi

echo "Releasing LoxiLB VM image version: $VERSION"
echo "Image: $IMAGE_PATH"
echo "Deployment type: $DEPLOYMENT_TYPE"

# Validate image first
scripts/validate-vm-image.sh "$IMAGE_PATH"

# Generate image name
IMAGE_NAME="loxilb-vm-${DEPLOYMENT_TYPE}-v${VERSION}.qcow2"
cp "$IMAGE_PATH" "$IMAGE_NAME"

# Compress image
echo "Compressing image..."
gzip "$IMAGE_NAME"
COMPRESSED_IMAGE="${IMAGE_NAME}.gz"

# Calculate checksums
echo "Generating checksums..."
sha256sum "$COMPRESSED_IMAGE" > "${COMPRESSED_IMAGE}.sha256"
md5sum "$COMPRESSED_IMAGE" > "${COMPRESSED_IMAGE}.md5"

# Create or update release
echo "Uploading to GitHub release..."
if gh release view "vm-v$VERSION" >/dev/null 2>&1; then
    echo "Release vm-v$VERSION exists, uploading assets..."
    gh release upload "vm-v$VERSION" "$COMPRESSED_IMAGE" "${COMPRESSED_IMAGE}.sha256" "${COMPRESSED_IMAGE}.md5"
else
    echo "Creating new release vm-v$VERSION..."
    gh release create "vm-v$VERSION" \
        --title "LoxiLB VM Images v$VERSION" \
        --notes "LoxiLB VM images for OpenStack deployment

## Available Images

### Production Image
- **File**: loxilb-vm-production-v${VERSION}.qcow2.gz
- **Use Case**: Production deployments
- **Resources**: 4 vCPU, 16GB RAM recommended
- **Features**: Full feature set, optimized performance

### Standard Image  
- **File**: loxilb-vm-standard-v${VERSION}.qcow2.gz
- **Use Case**: Standard deployments
- **Resources**: 2 vCPU, 8GB RAM recommended
- **Features**: Complete functionality, balanced performance

### Development Image
- **File**: loxilb-vm-devstack-v${VERSION}.qcow2.gz  
- **Use Case**: Development and testing
- **Resources**: 1 vCPU, 4GB RAM minimum
- **Features**: Debug tools, development utilities

## Installation

Download the appropriate image for your deployment:

\`\`\`bash
# Download image
wget https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver/releases/download/vm-v${VERSION}/loxilb-vm-${DEPLOYMENT_TYPE}-v${VERSION}.qcow2.gz

# Verify checksum
sha256sum -c loxilb-vm-${DEPLOYMENT_TYPE}-v${VERSION}.qcow2.gz.sha256

# Extract
gunzip loxilb-vm-${DEPLOYMENT_TYPE}-v${VERSION}.qcow2.gz

# Upload to OpenStack
openstack image create --disk-format qcow2 --container-format bare \\
  --public --file loxilb-vm-${DEPLOYMENT_TYPE}-v${VERSION}.qcow2 \\
  loxilb-vm-${DEPLOYMENT_TYPE}
\`\`\`" \
        "$COMPRESSED_IMAGE" "${COMPRESSED_IMAGE}.sha256" "${COMPRESSED_IMAGE}.md5"
fi

# Cleanup
rm -f "$COMPRESSED_IMAGE" "${COMPRESSED_IMAGE}.sha256" "${COMPRESSED_IMAGE}.md5"

echo "✓ VM image release completed"
echo "Release URL: $(gh release view vm-v$VERSION --json url -q .url)"
```

## Release Workflow

### Complete Release Process

1. **Prepare Release**
   ```bash
   # Update version and changelog
   vim octavia_loxilb_driver/version.py
   vim CHANGELOG.md
   
   # Commit changes
   git add -A
   git commit -m "Prepare release v1.2.3"
   git push
   ```

2. **Release PyPI Package**
   ```bash
   scripts/release-pypi.sh
   ```

3. **Release VM Images**
   ```bash
   # Release production image
   scripts/release-vm-image.sh production-loxilb.qcow2 1.2.3 production
   
   # Release standard image  
   scripts/release-vm-image.sh standard-loxilb.qcow2 1.2.3 standard
   
   # Release development image
   scripts/release-vm-image.sh devstack-loxilb.qcow2 1.2.3 devstack
   ```

4. **Post-Release Tasks**
   - Update installation documentation
   - Announce release on community channels
   - Update Docker images (if applicable)
   - Monitor for issues

### Hotfix Release Process

For critical bug fixes:

1. Create hotfix branch from main
2. Apply minimal fix
3. Bump patch version
4. Release following normal process
5. Merge back to develop branch

## Release Checklist

### Pre-Release
- [ ] All tests pass
- [ ] Documentation updated  
- [ ] Version bumped
- [ ] Changelog updated
- [ ] VM images prepared and tested
- [ ] Release notes drafted

### Release
- [ ] PyPI package published
- [ ] GitHub release created
- [ ] VM images uploaded
- [ ] Git tags created
- [ ] Release notes published

### Post-Release
- [ ] Installation instructions updated
- [ ] Community notified
- [ ] Monitor for issues
- [ ] Plan next release

## Troubleshooting

### Common Issues

**PyPI Upload Fails**
```bash
# Check credentials
twine check ~/.pypirc

# Try with verbose output
twine upload --verbose dist/*
```

**GitHub Release Fails**
```bash
# Check authentication
gh auth status

# Refresh token
gh auth refresh
```

**VM Image Too Large**
```bash
# Compress more aggressively
qemu-img convert -c -O qcow2 input.qcow2 output.qcow2

# Remove unnecessary files before image creation
```

## Security Considerations

- Never commit credentials to repository
- Use environment variables for sensitive data
- Validate all images before release
- Monitor downloads for suspicious activity
- Keep release tools updated

## Automation

Consider setting up GitHub Actions for automated releases:

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags: ['v*']
jobs:
  pypi-release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build and publish
        env:
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: |
          python -m build
          twine upload dist/*
```

---

*This release guide ensures consistent, reliable releases of both the LoxiLB Octavia Driver package and associated VM images.*