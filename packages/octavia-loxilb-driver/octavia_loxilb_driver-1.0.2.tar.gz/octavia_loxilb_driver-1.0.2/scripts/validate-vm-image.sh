#!/bin/bash
# Copyright 2025 LoxiLB
# Licensed under the Apache License, Version 2.0

# VM Image Validation Script for LoxiLB

set -e

IMAGE_PATH="$1"

if [ -z "$IMAGE_PATH" ]; then
    echo "Usage: $0 <path-to-qcow2-image>"
    echo
    echo "This script validates a LoxiLB VM image for release readiness."
    echo
    echo "Checks performed:"
    echo "  - File format validation"
    echo "  - Size constraints"
    echo "  - Image integrity"
    echo "  - Basic structure validation"
    exit 1
fi

echo "=== LoxiLB VM Image Validation ==="
echo "Image: $IMAGE_PATH"
echo

# Check if file exists
if [ ! -f "$IMAGE_PATH" ]; then
    echo "❌ Error: Image file not found: $IMAGE_PATH"
    exit 1
fi

# Check required tools
if ! command -v qemu-img &> /dev/null; then
    echo "❌ Error: qemu-img not found"
    echo "Install with: sudo apt install qemu-utils (Ubuntu/Debian)"
    echo "           or: brew install qemu (macOS)"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "❌ Error: jq not found"
    echo "Install with: sudo apt install jq (Ubuntu/Debian)"
    echo "           or: brew install jq (macOS)"
    exit 1
fi

echo "🔍 Starting validation..."
echo

# Get image information
echo "📊 Image Information:"
IMAGE_INFO=$(qemu-img info --output json "$IMAGE_PATH")

# Extract key information
FORMAT=$(echo "$IMAGE_INFO" | jq -r '.format')
VIRTUAL_SIZE=$(echo "$IMAGE_INFO" | jq -r '.["virtual-size"]')
ACTUAL_SIZE=$(echo "$IMAGE_INFO" | jq -r '.["actual-size"]')
DIRTY_FLAG=$(echo "$IMAGE_INFO" | jq -r '.["dirty-flag"]' 2>/dev/null || echo "null")

# Calculate sizes in human readable format
VIRTUAL_SIZE_GB=$((VIRTUAL_SIZE / 1024 / 1024 / 1024))
ACTUAL_SIZE_MB=$((ACTUAL_SIZE / 1024 / 1024))

echo "   Format: $FORMAT"
echo "   Virtual Size: ${VIRTUAL_SIZE_GB}GB"
echo "   Actual Size: ${ACTUAL_SIZE_MB}MB"
echo "   Compression Ratio: $(( (VIRTUAL_SIZE - ACTUAL_SIZE) * 100 / VIRTUAL_SIZE ))%"

# Validation checks
ERRORS=0
WARNINGS=0

echo
echo "🧪 Running validation checks..."

# Check 1: QCOW2 format
echo -n "   Format validation... "
if [ "$FORMAT" = "qcow2" ]; then
    echo "✅ PASS"
else
    echo "❌ FAIL - Expected QCOW2, found $FORMAT"
    ((ERRORS++))
fi

# Check 2: Reasonable virtual size
echo -n "   Virtual size check... "
if [ "$VIRTUAL_SIZE_GB" -ge 8 ] && [ "$VIRTUAL_SIZE_GB" -le 100 ]; then
    echo "✅ PASS (${VIRTUAL_SIZE_GB}GB)"
elif [ "$VIRTUAL_SIZE_GB" -lt 8 ]; then
    echo "❌ FAIL - Too small (${VIRTUAL_SIZE_GB}GB, minimum 8GB)"
    ((ERRORS++))
else
    echo "⚠️  WARNING - Very large (${VIRTUAL_SIZE_GB}GB)"
    ((WARNINGS++))
fi

# Check 3: Actual size not too large
echo -n "   Actual size check... "
if [ "$ACTUAL_SIZE_MB" -le 2048 ]; then
    echo "✅ PASS (${ACTUAL_SIZE_MB}MB)"
elif [ "$ACTUAL_SIZE_MB" -le 4096 ]; then
    echo "⚠️  WARNING - Large file (${ACTUAL_SIZE_MB}MB)"
    ((WARNINGS++))
else
    echo "❌ FAIL - File too large (${ACTUAL_SIZE_MB}MB, max recommended 4GB)"
    ((ERRORS++))
fi

# Check 4: Image integrity
echo -n "   Integrity check... "
if qemu-img check "$IMAGE_PATH" >/dev/null 2>&1; then
    echo "✅ PASS"
else
    echo "❌ FAIL - Image integrity check failed"
    ((ERRORS++))
fi

# Check 5: Dirty flag
echo -n "   Clean shutdown check... "
if [ "$DIRTY_FLAG" = "false" ] || [ "$DIRTY_FLAG" = "null" ]; then
    echo "✅ PASS"
else
    echo "⚠️  WARNING - Image may not have been cleanly shut down"
    ((WARNINGS++))
fi

# Check 6: Compression efficiency
echo -n "   Compression check... "
COMPRESSION_RATIO=$(( (VIRTUAL_SIZE - ACTUAL_SIZE) * 100 / VIRTUAL_SIZE ))
if [ "$COMPRESSION_RATIO" -ge 50 ]; then
    echo "✅ PASS (${COMPRESSION_RATIO}% compressed)"
elif [ "$COMPRESSION_RATIO" -ge 30 ]; then
    echo "⚠️  WARNING - Low compression (${COMPRESSION_RATIO}%)"
    ((WARNINGS++))
else
    echo "⚠️  WARNING - Very low compression (${COMPRESSION_RATIO}%)"
    ((WARNINGS++))
fi

# Additional checks if we can mount (Linux only with guestfs)
if command -v guestfish &> /dev/null; then
    echo -n "   Filesystem check... "
    if guestfish --ro -a "$IMAGE_PATH" -i ls / >/dev/null 2>&1; then
        echo "✅ PASS - Filesystem accessible"
        
        # Check for required directories/files
        echo -n "   System structure check... "
        STRUCTURE_OK=true
        
        # Check for essential directories
        for dir in /etc /usr /var /home; do
            if ! guestfish --ro -a "$IMAGE_PATH" -i ls "$dir" >/dev/null 2>&1; then
                STRUCTURE_OK=false
                break
            fi
        done
        
        if [ "$STRUCTURE_OK" = "true" ]; then
            echo "✅ PASS"
        else
            echo "⚠️  WARNING - Some system directories missing"
            ((WARNINGS++))
        fi
        
        # Check for LoxiLB specific files (if possible)
        echo -n "   LoxiLB installation check... "
        if guestfish --ro -a "$IMAGE_PATH" -i ls /usr/local/sbin/ 2>/dev/null | grep -q loxilb; then
            echo "✅ PASS - LoxiLB binary found"
        else
            echo "⚠️  WARNING - LoxiLB binary not found in expected location"
            ((WARNINGS++))
        fi
        
    else
        echo "⚠️  SKIP - Cannot access filesystem"
        ((WARNINGS++))
    fi
else
    echo "   ⚠️  Skipping filesystem checks (guestfs-tools not available)"
fi

echo
echo "📋 Validation Summary:"
echo "   Errors: $ERRORS"
echo "   Warnings: $WARNINGS"
echo

# Determine overall result
if [ "$ERRORS" -eq 0 ]; then
    if [ "$WARNINGS" -eq 0 ]; then
        echo "✅ VALIDATION PASSED - Image is ready for release"
        exit 0
    else
        echo "⚠️  VALIDATION PASSED WITH WARNINGS - Review warnings before release"
        exit 0
    fi
else
    echo "❌ VALIDATION FAILED - Fix errors before release"
    exit 1
fi