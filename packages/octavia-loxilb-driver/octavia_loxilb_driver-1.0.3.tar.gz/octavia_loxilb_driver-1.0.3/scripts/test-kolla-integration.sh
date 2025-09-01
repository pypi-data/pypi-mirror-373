#!/bin/bash
# test-kolla-integration.sh - Integration test for kolla-ansible based OpenStack

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m' 
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_test() { echo -e "${BLUE}[TEST]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Get current directory
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$CURRENT_DIR"

# Check if OpenStack credentials are available
if [ -z "$OS_AUTH_URL" ]; then
    print_warning "OpenStack credentials not found. Please source your OpenStack RC file."
    print_status "Example: source /etc/kolla/admin-openrc.sh"
    exit 1
fi

# Check if LoxiLB is running
print_test "Checking LoxiLB availability..."
LOXILB_ENDPOINT=${LOXILB_ENDPOINT:-"http://192.168.20.130:11111"}

if ! curl -s "$LOXILB_ENDPOINT/netlox/v1/version" > /dev/null; then
    print_error "LoxiLB is not accessible at $LOXILB_ENDPOINT"
    print_status "Please ensure LoxiLB is running and accessible from this host."
    print_status "You can override the endpoint with: export LOXILB_ENDPOINT=http://your-loxilb-ip:11111"
    exit 1
fi

print_status "LoxiLB is accessible at $LOXILB_ENDPOINT"

# Check if the LoxiLB provider is registered
print_test "Checking if LoxiLB provider is registered..."
if ! openstack loadbalancer provider list | grep -q "loxilb"; then
    print_error "LoxiLB provider is not registered in Octavia"
    print_status "Please ensure you've configured Octavia to use LoxiLB provider."
    print_status "You can use the configure-loxilb-octavia.sh script to set it up."
    exit 1
fi

print_status "LoxiLB provider is registered in Octavia"

# Create test resources
print_test "Creating test resources..."

# Create a test network
print_status "Creating test network..."
NETWORK_NAME="loxilb-test-network"
SUBNET_NAME="loxilb-test-subnet"

# Check if network already exists
if openstack network show "$NETWORK_NAME" &>/dev/null; then
    print_status "Network $NETWORK_NAME already exists, reusing it."
else
    openstack network create "$NETWORK_NAME"
    openstack subnet create "$SUBNET_NAME" \
        --network "$NETWORK_NAME" \
        --subnet-range 192.168.100.0/24
fi

# Create test instances
print_status "Creating test instances..."

# Find a suitable image
IMAGE_NAME=$(openstack image list -f value -c Name | grep -i cirros | head -1)
if [ -z "$IMAGE_NAME" ]; then
    # Try to find any image
    IMAGE_NAME=$(openstack image list -f value -c Name | head -1)
    if [ -z "$IMAGE_NAME" ]; then
        print_error "No images found in OpenStack. Cannot continue."
        exit 1
    fi
    print_warning "No CirrOS image found, using $IMAGE_NAME instead"
fi

# Find a suitable flavor
FLAVOR_NAME=$(openstack flavor list -f value -c Name | grep -i tiny | head -1)
if [ -z "$FLAVOR_NAME" ]; then
    # Try to find the smallest flavor
    FLAVOR_NAME=$(openstack flavor list -f value -c Name | head -1)
    if [ -z "$FLAVOR_NAME" ]; then
        print_error "No flavors found in OpenStack. Cannot continue."
        exit 1
    fi
    print_warning "No 'tiny' flavor found, using $FLAVOR_NAME instead"
fi

# Check if instances already exist
if openstack server show "loxilb-test-server-1" &>/dev/null; then
    print_status "Test instances already exist, reusing them."
else
    # Create security group
    SG_NAME="loxilb-test-sg"
    if ! openstack security group show "$SG_NAME" &>/dev/null; then
        openstack security group create "$SG_NAME"
        openstack security group rule create "$SG_NAME" --protocol tcp --dst-port 80:80
        openstack security group rule create "$SG_NAME" --protocol icmp
    fi

    # Create keypair
    KEY_NAME="loxilb-test-key"
    if ! openstack keypair show "$KEY_NAME" &>/dev/null 2>&1; then
        # Skip keypair creation if it fails - it's not critical for the test
        if openstack keypair create "$KEY_NAME" > loxilb-test-key.pem 2>/dev/null; then
            chmod 600 loxilb-test-key.pem
            print_status "Created keypair $KEY_NAME"
        else
            print_warning "Could not create keypair, continuing without it"
            KEY_NAME=""
        fi
    fi

    # Create instances
    SERVER_CMD="openstack server create \
        --image \"$IMAGE_NAME\" \
        --flavor \"$FLAVOR_NAME\" \
        --network \"$NETWORK_NAME\" \
        --security-group \"$SG_NAME\""
    
    # Add keypair if available
    if [ -n "$KEY_NAME" ]; then
        SERVER_CMD="$SERVER_CMD --key-name \"$KEY_NAME\""
    fi
    
    # Create server 1
    eval "$SERVER_CMD \"loxilb-test-server-1\""
    
    # Create server 2
    eval "$SERVER_CMD \"loxilb-test-server-2\""

    # Wait for instances to be active
    print_status "Waiting for instances to become active..."
    for i in {1..30}; do
        STATUS1=$(openstack server show "loxilb-test-server-1" -f value -c status)
        STATUS2=$(openstack server show "loxilb-test-server-2" -f value -c status)
        if [ "$STATUS1" == "ACTIVE" ] && [ "$STATUS2" == "ACTIVE" ]; then
            break
        fi
        echo -n "."
        sleep 5
    done
    echo ""
fi

# Get server IPs
SERVER1_IP=$(openstack server show "loxilb-test-server-1" -f value -c addresses | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1)
SERVER2_IP=$(openstack server show "loxilb-test-server-2" -f value -c addresses | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1)

print_status "Server 1 IP: $SERVER1_IP"
print_status "Server 2 IP: $SERVER2_IP"

# Create load balancer with LoxiLB provider
print_test "Creating load balancer with LoxiLB provider..."
LB_NAME="loxilb-test-lb"

# Check if load balancer already exists
if openstack loadbalancer show "$LB_NAME" &>/dev/null 2>&1; then
    print_status "Load balancer $LB_NAME already exists, deleting it first..."
    openstack loadbalancer delete --cascade "$LB_NAME"
    
    # Wait for deletion to complete
    print_status "Waiting for load balancer deletion to complete..."
    for i in {1..30}; do
        if ! openstack loadbalancer show "$LB_NAME" &>/dev/null 2>&1; then
            break
        fi
        echo -n "."
        sleep 5
    done
    echo ""
    sleep 5  # Additional safety wait
fi

# Create load balancer
print_status "Creating load balancer..."
try_command() {
    local cmd="$1"
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        print_status "Attempt $attempt/$max_attempts: $cmd"
        if eval "$cmd"; then
            return 0
        fi
        print_warning "Command failed, retrying in 5 seconds..."
        sleep 5
        attempt=$((attempt + 1))
    done
    
    print_error "Command failed after $max_attempts attempts"
    return 1
}

# Try to create the load balancer with retries
if ! try_command "openstack loadbalancer create --name \"$LB_NAME\" --vip-subnet-id \"$SUBNET_NAME\" --provider loxilb"; then
    print_error "Failed to create load balancer. Exiting."
    exit 1
fi

# Wait for load balancer to be active
print_status "Waiting for load balancer to become active..."
for i in {1..30}; do
    STATUS=$(openstack loadbalancer show "$LB_NAME" -f value -c provisioning_status)
    if [ "$STATUS" == "ACTIVE" ]; then
        break
    fi
    echo -n "."
    sleep 10
done
echo ""

# Create listener
print_status "Creating listener..."
openstack loadbalancer listener create \
    --name "loxilb-test-listener" \
    --protocol HTTP \
    --protocol-port 80 \
    "$LB_NAME"

# Wait for listener to be active
print_status "Waiting for listener to become active..."
for i in {1..30}; do
    STATUS=$(openstack loadbalancer show "$LB_NAME" -f value -c provisioning_status)
    if [ "$STATUS" == "ACTIVE" ]; then
        break
    fi
    echo -n "."
    sleep 5
done
echo ""

# Create pool
print_status "Creating pool..."
openstack loadbalancer pool create \
    --name "loxilb-test-pool" \
    --lb-algorithm ROUND_ROBIN \
    --listener "loxilb-test-listener" \
    --protocol HTTP

# Wait for pool to be active
print_status "Waiting for pool to become active..."
for i in {1..30}; do
    STATUS=$(openstack loadbalancer show "$LB_NAME" -f value -c provisioning_status)
    if [ "$STATUS" == "ACTIVE" ]; then
        break
    fi
    echo -n "."
    sleep 5
done
echo ""

# Create members
print_status "Creating members..."
openstack loadbalancer member create \
    --subnet-id "$SUBNET_NAME" \
    --address "$SERVER1_IP" \
    --protocol-port 80 \
    "loxilb-test-pool"

openstack loadbalancer member create \
    --subnet-id "$SUBNET_NAME" \
    --address "$SERVER2_IP" \
    --protocol-port 80 \
    "loxilb-test-pool"

# Wait for members to be active
print_status "Waiting for members to become active..."
for i in {1..30}; do
    STATUS=$(openstack loadbalancer show "$LB_NAME" -f value -c provisioning_status)
    if [ "$STATUS" == "ACTIVE" ]; then
        break
    fi
    echo -n "."
    sleep 5
done
echo ""

# Get load balancer VIP
LB_VIP=$(openstack loadbalancer show "$LB_NAME" -f value -c vip_address)
print_status "Load balancer VIP: $LB_VIP"

# Test the load balancer
print_test "Testing load balancer..."
print_status "Note: For a complete test, you would need to configure the test servers"
print_status "to run a web server and then access the load balancer VIP."
print_status "This script only verifies that the load balancer was created successfully."

# Show the load balancer details
print_status "Load balancer details:"
openstack loadbalancer show "$LB_NAME" -f json | python3 -m json.tool || echo "Could not retrieve load balancer details"

# Check LoxiLB configuration
print_test "Checking LoxiLB configuration..."
print_status "Querying LoxiLB API for load balancer configuration..."

# Get load balancer services from LoxiLB
LOXILB_LB_SERVICES=$(curl -s "$LOXILB_ENDPOINT/netlox/v1/config/lb")
echo "$LOXILB_LB_SERVICES" | grep -q "$LB_VIP"
if [ $? -eq 0 ]; then
    print_status "✅ Load balancer configuration found in LoxiLB!"
    print_status "LoxiLB has the following configuration for this load balancer:"
    echo "$LOXILB_LB_SERVICES" | grep -A 10 "$LB_VIP"
else
    print_warning "⚠️ Load balancer configuration not found in LoxiLB."
    print_status "This might indicate an issue with the LoxiLB driver or connectivity."
fi

print_test "Test completed!"
print_status "To clean up test resources, run:"
print_status "openstack loadbalancer delete --cascade $LB_NAME"
print_status "openstack server delete loxilb-test-server-1 loxilb-test-server-2"
print_status "openstack network delete $NETWORK_NAME"
