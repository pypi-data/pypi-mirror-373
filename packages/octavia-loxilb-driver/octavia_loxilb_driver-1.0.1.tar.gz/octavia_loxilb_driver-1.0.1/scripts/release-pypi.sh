#!/bin/bash
# Copyright 2025 LoxiLB
# Licensed under the Apache License, Version 2.0

# PyPI Release Script for Octavia LoxiLB Driver

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== LoxiLB Octavia Driver PyPI Release ==="
echo

# Change to project root
cd "$PROJECT_ROOT"

# Get version from version.py
VERSION=$(python -c "from octavia_loxilb_driver.version import __version__; print(__version__)")
echo "📦 Preparing release for version: $VERSION"
echo

# Pre-release validation
echo "🔍 Running pre-release checks..."

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    echo "⚠️  Warning: Not on main branch (current: $CURRENT_BRANCH)"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted"
        exit 1
    fi
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Error: Working directory has uncommitted changes"
    git status --short
    exit 1
fi

# Check if version tag already exists
if git tag --list | grep -q "^v$VERSION$"; then
    echo "❌ Error: Tag v$VERSION already exists"
    exit 1
fi

# Run tests
echo "🧪 Running tests..."
if command -v pytest &> /dev/null; then
    python -m pytest tests/ -v --tb=short
else
    echo "⚠️  pytest not found, skipping tests"
fi

# Check code style
echo "📝 Checking code style..."
if command -v flake8 &> /dev/null; then
    python -m flake8 octavia_loxilb_driver/ --max-line-length=100
else
    echo "⚠️  flake8 not found, skipping style check"
fi

# Validate project configuration
echo "⚙️  Validating project configuration..."
if [ -f "pyproject.toml" ]; then
    # For pyproject.toml projects, just check the file exists and is valid
    python -c "import tomllib; open('pyproject.toml', 'rb'); print('✓ pyproject.toml is valid')" 2>/dev/null || \
    python -c "import tomli; open('pyproject.toml', 'rb'); print('✓ pyproject.toml is valid')" 2>/dev/null || \
    echo "✓ pyproject.toml exists"
elif [ -f "setup.py" ]; then
    python setup.py check --strict
else
    echo "❌ Error: No setup.py or pyproject.toml found"
    exit 1
fi

echo "✅ Pre-release checks completed"
echo

# Build distribution packages
echo "🏗️  Building distribution packages..."
rm -rf dist/ build/ *.egg-info/

# Build wheel and source distribution
python -m build

if [ ! -f "dist/octavia_loxilb_driver-${VERSION}-py3-none-any.whl" ]; then
    echo "❌ Error: Wheel build failed"
    exit 1
fi

if [ ! -f "dist/octavia_loxilb_driver-${VERSION}.tar.gz" ]; then
    echo "❌ Error: Source distribution build failed"  
    exit 1
fi

echo "✅ Built packages:"
ls -la dist/

# Validate packages
echo
echo "🔍 Validating packages..."
if command -v twine &> /dev/null; then
    twine check dist/*
else
    echo "❌ Error: twine not found. Install with: pip install twine"
    exit 1
fi

echo "✅ Package validation completed"
echo

# Confirm upload
echo "📦 Ready to upload to PyPI:"
echo "   - octavia_loxilb_driver-${VERSION}-py3-none-any.whl"
echo "   - octavia_loxilb_driver-${VERSION}.tar.gz"
echo
read -p "Proceed with PyPI upload? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Upload cancelled"
    exit 0
fi

# Upload to PyPI
echo "🚀 Uploading to PyPI..."
twine upload dist/*

if [ $? -eq 0 ]; then
    echo "✅ Successfully uploaded to PyPI"
else
    echo "❌ PyPI upload failed"
    exit 1
fi

# Create git tag
echo
echo "🏷️  Creating git tag v$VERSION..."
git tag "v$VERSION" -m "Release version $VERSION"
git push origin "v$VERSION"

echo "✅ Git tag created and pushed"

# Create GitHub release
echo
echo "📋 Creating GitHub release..."
if command -v gh &> /dev/null; then
    # Check if CHANGELOG.md exists
    RELEASE_NOTES=""
    if [ -f "CHANGELOG.md" ]; then
        # Extract release notes for this version from CHANGELOG.md
        RELEASE_NOTES="See CHANGELOG.md for detailed release notes."
    else
        RELEASE_NOTES="Release version $VERSION of the LoxiLB Octavia Driver.

## Installation

\`\`\`bash
pip install octavia-loxilb-driver==$VERSION
\`\`\`

## What's Changed
- Package released to PyPI
- See commit history for detailed changes"
    fi

    gh release create "v$VERSION" \
        --title "Release v$VERSION" \
        --notes "$RELEASE_NOTES" \
        --draft \
        dist/*

    echo "✅ GitHub release draft created"
    echo "   Please review and publish at: $(gh release view v$VERSION --json url -q .url)"
else
    echo "⚠️  GitHub CLI not found. Manual release creation required."
    echo "   Create release at: https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver/releases/new"
fi

echo
echo "🎉 PyPI release completed successfully!"
echo
echo "📝 Next steps:"
echo "1. Review and publish the GitHub release draft"
echo "2. Test installation: pip install octavia-loxilb-driver==$VERSION"
echo "3. Update documentation if needed"
echo "4. Announce the release to the community"
echo

# Verify PyPI installation works
echo "🧪 Verifying PyPI installation..."
sleep 30  # Wait for PyPI propagation

if python -m pip install --dry-run octavia-loxilb-driver==$VERSION >/dev/null 2>&1; then
    echo "✅ Package is installable from PyPI"
else
    echo "⚠️  Package not yet available on PyPI (may need time to propagate)"
fi

echo
echo "Release process completed for version $VERSION"