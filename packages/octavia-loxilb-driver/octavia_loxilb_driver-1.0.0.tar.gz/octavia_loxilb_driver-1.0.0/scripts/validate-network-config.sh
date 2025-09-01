#!/bin/bash
# validate-network-config.sh - Validate networking configuration for DevStack

echo "🔍 Validating Network Configuration for DevStack"
echo "================================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_test() { echo -e "${BLUE}[CHECK]${NC} $1"; }
print_success() { echo -e "${GREEN}[PASS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[FAIL]${NC} $1"; }

# Test 1: Interface Detection
print_test "Detecting primary network interface..."
PRIMARY_INTERFACE=$(ip route get 8.8.8.8 2>/dev/null | head -1 | awk '{print $5}' 2>/dev/null)
if [[ -z "$PRIMARY_INTERFACE" ]]; then
    PRIMARY_INTERFACE=$(ip link show | grep -E '^[0-9]+:' | grep -v 'lo:' | head -1 | awk -F: '{print $2}' | sed 's/^ *//')
fi
if [[ -z "$PRIMARY_INTERFACE" ]]; then
    PRIMARY_INTERFACE="eth0"
fi

print_success "Primary interface: $PRIMARY_INTERFACE"

# Test 2: Host IP Detection  
print_test "Detecting host IP address..."
HOST_IP=$(ip route get 8.8.8.8 2>/dev/null | head -1 | awk '{print $7}' 2>/dev/null || echo "")
if [[ -z "$HOST_IP" ]]; then
    HOST_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "")
fi
if [[ -z "$HOST_IP" ]]; then
    HOST_IP=$(ip addr show | grep -E "inet [0-9]" | grep -v 127.0.0.1 | head -1 | awk '{print $2}' | cut -d/ -f1 || echo "")
fi

if [[ -n "$HOST_IP" && "$HOST_IP" != "127.0.0.1" ]]; then
    print_success "Host IP: $HOST_IP"
else
    print_error "Could not detect valid host IP"
    exit 1
fi

# Test 3: Interface Status
print_test "Checking interface status..."
if ip link show "$PRIMARY_INTERFACE" >/dev/null 2>&1; then
    INTERFACE_STATUS=$(ip link show "$PRIMARY_INTERFACE" | grep 'state' | awk '{print $9}')
    if [[ "$INTERFACE_STATUS" == "UP" ]]; then
        print_success "Interface $PRIMARY_INTERFACE is UP"
    else
        print_warning "Interface $PRIMARY_INTERFACE is $INTERFACE_STATUS"
    fi
    
    # Check if interface has an IP
    INTERFACE_IP=$(ip addr show "$PRIMARY_INTERFACE" | grep 'inet ' | head -1 | awk '{print $2}' | cut -d'/' -f1)
    if [[ -n "$INTERFACE_IP" ]]; then
        print_success "Interface IP: $INTERFACE_IP"
        if [[ "$INTERFACE_IP" == "$HOST_IP" ]]; then
            print_success "Interface IP matches detected host IP"
        else
            print_warning "Interface IP ($INTERFACE_IP) differs from detected host IP ($HOST_IP)"
        fi
    else
        print_warning "No IP address on interface $PRIMARY_INTERFACE"
    fi
else
    print_error "Interface $PRIMARY_INTERFACE not found"
fi

# Test 4: Network Connectivity
print_test "Testing network connectivity..."
if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
    print_success "Internet connectivity working"
else
    print_warning "No internet connectivity (may affect DevStack installation)"
fi

# Test 5: Generate test configuration
print_test "Generating test DevStack network configuration..."
cat > /tmp/test-devstack-network.conf << EOF
# Network configuration for DevStack
HOST_IP=$HOST_IP
HOST_IP_IFACE=$PRIMARY_INTERFACE
SERVICE_HOST=$HOST_IP
MYSQL_HOST=$HOST_IP
RABBIT_HOST=$HOST_IP
GLANCE_HOSTPORT=$HOST_IP:9292

# Force traditional networking (disable OVN auto-detection)
Q_PLUGIN=ml2
Q_ML2_TENANT_NETWORK_TYPE=vxlan
Q_ML2_PLUGIN_MECHANISM_DRIVERS=linuxbridge,l2population
NEUTRON_AGENT=linuxbridge

# Explicitly disable OVN to avoid conflicts with q-agt
disable_service ovn-controller
disable_service ovn-northd
disable_service q-ovn-metadata-agent

# Networking
FIXED_RANGE=10.1.0.0/24
FLOATING_RANGE=192.168.100.0/24
PUBLIC_NETWORK_GATEWAY=192.168.100.1
PUBLIC_INTERFACE=$PRIMARY_INTERFACE
EOF

print_success "Test configuration generated: /tmp/test-devstack-network.conf"

echo ""
echo "📋 Configuration Summary:"
echo "========================="
echo "HOST_IP: $HOST_IP"
echo "PRIMARY_INTERFACE: $PRIMARY_INTERFACE"
echo "NETWORKING: Traditional ML2 with LinuxBridge (OVN disabled)"
echo "STATUS: Ready for DevStack installation"

echo ""
echo "🚀 To proceed with DevStack installation:"
echo "cd /path/to/octavia-loxilb-driver"
echo "make setup-devstack"

# Clean up
rm -f /tmp/test-devstack-network.conf
