#!/bin/bash

# diagnose-octavia-loxilb.sh
# Diagnostic script for LoxiLB Octavia integration issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info "🔍 Octavia LoxiLB Diagnostic Tool"
print_info "================================="

# Check container status
print_info "1. Checking Octavia container status..."
docker ps | grep octavia | while read line; do
    if echo "$line" | grep -q "unhealthy"; then
        print_error "Unhealthy container: $(echo "$line" | awk '{print $NF}')"
    elif echo "$line" | grep -q "healthy"; then
        print_success "Healthy container: $(echo "$line" | awk '{print $NF}')"
    else
        print_warning "Unknown status: $(echo "$line" | awk '{print $NF}')"
    fi
done

# Check driver installation
print_info "2. Checking LoxiLB driver installation..."
docker exec octavia_api python -c "import octavia_loxilb_driver; print('✅ Driver installed successfully')" 2>/dev/null || print_error "❌ Driver not installed or not importable"

# Check configuration sections
print_info "3. Checking configuration sections..."
sections=$(docker exec octavia_api cat /etc/octavia/octavia.conf | grep "^\[" | tr -d '[]' | tr '\n' ' ')
print_info "Available sections: $sections"

if docker exec octavia_api grep -q "^\[loxilb\]" /etc/octavia/octavia.conf; then
    print_success "✅ [loxilb] section found"
    print_info "LoxiLB configuration:"
    docker exec octavia_api sed -n '/^\[loxilb\]/,/^$/p' /etc/octavia/octavia.conf | head -20
else
    print_error "❌ [loxilb] section missing"
fi

# Check enabled_provider_drivers
print_info "4. Checking enabled_provider_drivers setting..."
provider_drivers=$(docker exec octavia_api grep "^enabled_provider_drivers" /etc/octavia/octavia.conf | head -1)
if echo "$provider_drivers" | grep -q "loxilb"; then
    print_success "✅ LoxiLB provider found in configuration"
    print_info "$provider_drivers"
else
    print_warning "⚠️ LoxiLB provider not found in enabled_provider_drivers"
    print_info "$provider_drivers"
fi

# Check recent API logs for errors
print_info "5. Checking recent API logs for errors..."
error_count=$(docker logs octavia_api --tail 50 2>&1 | grep -i -c -E "(error|exception|traceback|failed)" || echo "0")
if [ "$error_count" -gt 0 ]; then
    print_error "Found $error_count error(s) in recent logs:"
    docker logs octavia_api --tail 50 2>&1 | grep -i -E "(error|exception|traceback|failed)" | tail -10
else
    print_success "No obvious errors in recent logs"
fi

# Check LoxiLB connectivity
print_info "6. Testing LoxiLB connectivity..."
loxilb_endpoint=$(docker exec octavia_api grep "^api_endpoints" /etc/octavia/octavia.conf 2>/dev/null | cut -d'=' -f2 | tr -d ' ' || echo "http://192.168.20.130:11111")
if docker exec octavia_api curl -s --connect-timeout 5 "$loxilb_endpoint" >/dev/null 2>&1; then
    print_success "✅ LoxiLB endpoint reachable: $loxilb_endpoint"
else
    print_error "❌ LoxiLB endpoint unreachable: $loxilb_endpoint"
fi

# Test provider list
print_info "7. Testing provider list API..."
if openstack loadbalancer provider list >/dev/null 2>&1; then
    print_success "✅ Provider list API working"
    openstack loadbalancer provider list
else
    print_error "❌ Provider list API failed"
    print_info "This is likely due to configuration issues found above"
fi

print_info ""
print_info "🔧 Recommended Actions:"
print_info "======================"

# Provide recommendations based on findings
if ! docker exec octavia_api grep -q "^\[loxilb\]" /etc/octavia/octavia.conf; then
    print_warning "1. Add missing [loxilb] section to configuration"
fi

if [ "$error_count" -gt 0 ]; then
    print_warning "2. Check and resolve errors in API logs"
fi

if docker ps | grep octavia_api | grep -q "unhealthy"; then
    print_warning "3. Fix configuration issues and restart octavia_api container"
fi

print_info ""
print_info "For automatic fixes, run: ./scripts/fix-loxilb-kolla-config.sh"
