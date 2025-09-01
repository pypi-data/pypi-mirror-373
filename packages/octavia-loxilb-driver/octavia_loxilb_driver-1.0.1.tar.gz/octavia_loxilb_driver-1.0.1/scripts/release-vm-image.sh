#!/bin/bash
# Copyright 2025 LoxiLB  
# Licensed under the Apache License, Version 2.0

# VM Image Release Script for LoxiLB

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

echo "=== LoxiLB VM Image Release ==="
echo

# Parse arguments
IMAGE_PATH="$1"
VERSION="$2"
DEPLOYMENT_TYPE="${3:-production}"

if [ -z "$IMAGE_PATH" ] || [ -z "$VERSION" ]; then
    echo "Usage: $0 <image-path> <version> [deployment-type]"
    echo
    echo "Arguments:"
    echo "  image-path      Path to the LoxiLB QCOW2 image file"
    echo "  version         Release version (e.g., 1.2.3)"
    echo "  deployment-type Deployment type: production, standard, or devstack (default: production)"
    echo
    echo "Examples:"
    echo "  $0 loxilb-vm.qcow2 1.2.3 production"
    echo "  $0 loxilb-dev.qcow2 1.2.3 devstack"
    exit 1
fi

# Validate deployment type
case "$DEPLOYMENT_TYPE" in
    production|standard|devstack)
        ;;
    *)
        echo "❌ Error: Invalid deployment type '$DEPLOYMENT_TYPE'"
        echo "   Valid types: production, standard, devstack"
        exit 1
        ;;
esac

echo "📦 Releasing LoxiLB VM image"
echo "   Image: $IMAGE_PATH"
echo "   Version: $VERSION"  
echo "   Deployment type: $DEPLOYMENT_TYPE"
echo

# Validate image file exists
if [ ! -f "$IMAGE_PATH" ]; then
    echo "❌ Error: Image file not found: $IMAGE_PATH"
    exit 1
fi

# Check required tools
echo "🔍 Checking required tools..."

if ! command -v qemu-img &> /dev/null; then
    echo "❌ Error: qemu-img not found. Install with:"
    echo "   Ubuntu/Debian: sudo apt install qemu-utils"
    echo "   RHEL/CentOS: sudo yum install qemu-img"
    echo "   macOS: brew install qemu"
    exit 1
fi

if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI not found. Install with:"
    echo "   Ubuntu/Debian: sudo apt install gh"
    echo "   RHEL/CentOS: sudo yum install gh"
    echo "   macOS: brew install gh"
    exit 1
fi

# Check GitHub authentication
if ! gh auth status >/dev/null 2>&1; then
    echo "❌ Error: Not authenticated with GitHub"
    echo "   Run: gh auth login"
    exit 1
fi

# Check if we're in a git repository
if ! git status >/dev/null 2>&1; then
    echo "❌ Error: Not in a git repository or git is not configured properly"
    echo "   Please run this script from the project root directory"
    echo "   Current directory: $(pwd)"
    echo "   Git status: $(git status --porcelain 2>&1 || echo 'Git not available')"
    exit 1
fi

# Try to detect the GitHub repository URL for the release
REPO_URL=$(git config --get remote.origin.url 2>/dev/null || echo "")
if [ -z "$REPO_URL" ]; then
    echo "⚠️  Warning: Could not detect GitHub repository URL"
    echo "   Make sure you have a GitHub remote configured"
    echo "   You can add it with: git remote add origin https://github.com/USERNAME/REPO.git"
    echo
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted"
        exit 1
    fi
fi

echo "✅ All required tools available"
echo

# Validate VM image
echo "🔍 Validating VM image..."

# Check QCOW2 format
IMAGE_INFO=$(qemu-img info --output json "$IMAGE_PATH")
IMAGE_FORMAT=$(echo "$IMAGE_INFO" | jq -r '.format')

if [ "$IMAGE_FORMAT" != "qcow2" ]; then
    echo "❌ Error: Image is not in QCOW2 format (found: $IMAGE_FORMAT)"
    exit 1
fi

# Get image size info
VIRTUAL_SIZE=$(echo "$IMAGE_INFO" | jq -r '.["virtual-size"]')
ACTUAL_SIZE=$(echo "$IMAGE_INFO" | jq -r '.["actual-size"]')
VIRTUAL_SIZE_GB=$((VIRTUAL_SIZE / 1024 / 1024 / 1024))
ACTUAL_SIZE_MB=$((ACTUAL_SIZE / 1024 / 1024))

echo "   Format: $IMAGE_FORMAT"
echo "   Virtual size: ${VIRTUAL_SIZE_GB}GB"
echo "   Actual size: ${ACTUAL_SIZE_MB}MB"

# Size warnings based on deployment type
case "$DEPLOYMENT_TYPE" in
    devstack)
        if [ "$VIRTUAL_SIZE_GB" -gt 20 ]; then
            echo "⚠️  Warning: DevStack image is quite large (${VIRTUAL_SIZE_GB}GB)"
        fi
        ;;
    standard)
        if [ "$VIRTUAL_SIZE_GB" -gt 40 ]; then
            echo "⚠️  Warning: Standard image is quite large (${VIRTUAL_SIZE_GB}GB)"
        fi
        ;;
    production)
        if [ "$VIRTUAL_SIZE_GB" -gt 80 ]; then
            echo "⚠️  Warning: Production image is quite large (${VIRTUAL_SIZE_GB}GB)"
        fi
        ;;
esac

# Check if image is readable
if ! qemu-img check "$IMAGE_PATH" >/dev/null 2>&1; then
    echo "❌ Error: Image file appears corrupted"
    exit 1
fi

echo "✅ Image validation completed"
echo

# Generate release filename
IMAGE_NAME="loxilb-vm-${DEPLOYMENT_TYPE}-v${VERSION}.qcow2"
TEMP_DIR=$(mktemp -d)
RELEASE_IMAGE="$TEMP_DIR/$IMAGE_NAME"

# Copy and prepare image
echo "📦 Preparing release image..."
cp "$IMAGE_PATH" "$RELEASE_IMAGE"

# Compress image
echo "🗜️  Compressing image..."
COMPRESSED_IMAGE="${RELEASE_IMAGE}.gz"
gzip "$RELEASE_IMAGE"

# Get compressed size
COMPRESSED_SIZE_MB=$(( $(stat -c%s "$COMPRESSED_IMAGE" 2>/dev/null || stat -f%z "$COMPRESSED_IMAGE") / 1024 / 1024))
echo "   Compressed size: ${COMPRESSED_SIZE_MB}MB"

# Generate checksums
echo "🔐 Generating checksums..."
ORIGINAL_DIR=$(pwd)
cd "$TEMP_DIR"

sha256sum "$IMAGE_NAME.gz" > "${IMAGE_NAME}.gz.sha256"
md5sum "$IMAGE_NAME.gz" > "${IMAGE_NAME}.gz.md5"

echo "✅ Files prepared:"
ls -lh "$TEMP_DIR"
echo

# Return to original directory for git/gh commands
cd "$ORIGINAL_DIR"

# Create release tag
RELEASE_TAG="vm-v$VERSION"

# Check if release already exists
if gh release view "$RELEASE_TAG" >/dev/null 2>&1; then
    echo "📋 Release $RELEASE_TAG exists, uploading additional assets..."
    
    # Upload assets to existing release
    gh release upload "$RELEASE_TAG" \
        "$TEMP_DIR/${IMAGE_NAME}.gz" \
        "$TEMP_DIR/${IMAGE_NAME}.gz.sha256" \
        "$TEMP_DIR/${IMAGE_NAME}.gz.md5" \
        --clobber
        
    echo "✅ Assets uploaded to existing release"
else
    echo "📋 Creating new release $RELEASE_TAG..."
    
    # Generate release notes based on deployment type
    case "$DEPLOYMENT_TYPE" in
        production)
            DESCRIPTION="Production-ready LoxiLB VM image optimized for performance and scalability."
            RESOURCES="4 vCPU, 16GB RAM recommended"
            ;;
        standard)
            DESCRIPTION="Standard LoxiLB VM image with balanced performance and resource usage."
            RESOURCES="2 vCPU, 8GB RAM recommended"  
            ;;
        devstack)
            DESCRIPTION="Development LoxiLB VM image with debug tools and minimal resource requirements."
            RESOURCES="1 vCPU, 4GB RAM minimum"
            ;;
    esac
    
    # Capitalize deployment type for display
    case "$DEPLOYMENT_TYPE" in
        production) DEPLOYMENT_TYPE_DISPLAY="Production" ;;
        standard) DEPLOYMENT_TYPE_DISPLAY="Standard" ;;
        devstack) DEPLOYMENT_TYPE_DISPLAY="DevStack" ;;
        *) DEPLOYMENT_TYPE_DISPLAY="$DEPLOYMENT_TYPE" ;;
    esac
    
    RELEASE_NOTES="# LoxiLB VM Images v$VERSION

This release provides pre-built LoxiLB VM images for OpenStack Octavia deployment.

## $DEPLOYMENT_TYPE_DISPLAY Image

- **Description**: $DESCRIPTION
- **Resources**: $RESOURCES  
- **File**: $IMAGE_NAME.gz
- **Virtual Size**: ${VIRTUAL_SIZE_GB}GB
- **Download Size**: ${COMPRESSED_SIZE_MB}MB

## Installation

### 1. Download Image
\`\`\`bash
wget https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver/releases/download/$RELEASE_TAG/$IMAGE_NAME.gz
\`\`\`

### 2. Verify Integrity
\`\`\`bash
wget https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver/releases/download/$RELEASE_TAG/$IMAGE_NAME.gz.sha256
sha256sum -c $IMAGE_NAME.gz.sha256
\`\`\`

### 3. Extract Image
\`\`\`bash
gunzip $IMAGE_NAME.gz
\`\`\`

### 4. Upload to OpenStack
\`\`\`bash
openstack image create --disk-format qcow2 --container-format bare \\
  --public --file $IMAGE_NAME loxilb-vm-$DEPLOYMENT_TYPE
\`\`\`

### 5. Use with Octavia Driver
\`\`\`bash
# Install the driver
pip install octavia-loxilb-driver

# Setup with the uploaded image
octavia-loxilb-setup --deployment-type $DEPLOYMENT_TYPE
\`\`\`

## Default Credentials

- **Username**: ubuntu  
- **SSH**: Key-based authentication (configure via cloud-init)
- **LoxiLB API**: No authentication required (default configuration)

## Network Configuration

The image is configured with:
- DHCP client enabled
- Cloud-init for initial setup
- LoxiLB service auto-start
- OpenStack metadata service support

## Support

- **Documentation**: https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver/tree/main/docs
- **Issues**: https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver/issues
- **LoxiLB Project**: https://github.com/loxilb-io/loxilb"

    # Create GitHub release
    gh release create "$RELEASE_TAG" \
        --title "LoxiLB VM Images v$VERSION" \
        --notes "$RELEASE_NOTES" \
        "$TEMP_DIR/${IMAGE_NAME}.gz" \
        "$TEMP_DIR/${IMAGE_NAME}.gz.sha256" \
        "$TEMP_DIR/${IMAGE_NAME}.gz.md5"
    
    echo "✅ New release created"
fi

# Cleanup
rm -rf "$TEMP_DIR"

echo
echo "🎉 VM image release completed!"
echo
echo "📝 Release information:"
echo "   Tag: $RELEASE_TAG"
echo "   Image: $IMAGE_NAME.gz (${COMPRESSED_SIZE_MB}MB)"
echo "   URL: $(gh release view $RELEASE_TAG --json url -q .url)"
echo

echo "📋 Next steps:"
echo "1. Test image download and installation"
echo "2. Update documentation with new image references"  
echo "3. Announce release to community"
echo "4. Consider creating additional deployment type images"
echo

# Test download URL
echo "🧪 Testing download URL..."
DOWNLOAD_URL="$(gh release view $RELEASE_TAG --json assets -q '.assets[] | select(.name == "'$IMAGE_NAME'.gz") | .browser_download_url')"
if curl -s -I "$DOWNLOAD_URL" | grep -q "200 OK"; then
    echo "✅ Download URL is accessible"
else
    echo "⚠️  Download URL may not be immediately available"
fi

echo
echo "VM image release completed for $DEPLOYMENT_TYPE v$VERSION"