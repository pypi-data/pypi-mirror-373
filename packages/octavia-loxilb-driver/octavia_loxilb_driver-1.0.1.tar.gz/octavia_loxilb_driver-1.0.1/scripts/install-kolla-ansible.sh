#!/bin/bash
# Copyright 2025 LoxiLB
# Licensed under the Apache License, Version 2.0

# Automated installation script for LoxiLB Octavia Driver on Kolla-Ansible deployments

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
OCTAVIA_CONTAINERS=("octavia_api" "octavia_worker")
KOLLA_CONFIG_DIR="/etc/kolla/config/octavia"


echo "=== LoxiLB Octavia Driver Installation for Kolla-Ansible ==="
echo

# Function to check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "ERROR: Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        echo "ERROR: Cannot connect to Docker daemon. Are you in the docker group?"
        exit 1
    fi
    
    echo "✓ Docker is available"
}

# Function to check if containers exist
check_containers() {
    echo "Checking for Octavia containers..."
    local missing_containers=()
    
    for container in "${OCTAVIA_CONTAINERS[@]}"; do
        if ! docker ps --format "table {{.Names}}" | grep -q "^$container$"; then
            missing_containers+=("$container")
        else
            echo "✓ Found container: $container"
        fi
    done
    
    if [ ${#missing_containers[@]} -ne 0 ]; then
        echo "WARNING: Missing containers: ${missing_containers[*]}"
        echo "This script will only install in available containers"
    fi
}

# Function to install driver in containers
install_driver() {
    echo
    echo "Installing LoxiLB driver in Octavia containers..."
    
    for container in "${OCTAVIA_CONTAINERS[@]}"; do
        if docker ps --format "table {{.Names}}" | grep -q "^$container$"; then
            echo "Installing driver in $container..."
            docker exec "$container" pip install --upgrade octavia-loxilb-driver
            if [ $? -eq 0 ]; then
                echo "✓ Driver installed successfully in $container"
            else
                echo "✗ Failed to install driver in $container"
                exit 1
            fi
        else
            echo "⚠ Skipping $container (not running)"
        fi
    done
}

# Function to create kolla configuration
create_kolla_config() {
    echo
    echo "Creating Kolla-Ansible configuration..."
    
    # Create config directory
    sudo mkdir -p "$KOLLA_CONFIG_DIR"
    
    # Create Octavia configuration override
    cat > /tmp/octavia.conf << EOF
[api_settings]
enabled_provider_drivers = amphora:The Amphora driver,loxilb:LoxiLB driver

[driver_agent]  
enabled_provider_agents = amphora_agent,loxilb

[loxilb]
# LoxiLB API Configuration
api_timeout = 30
api_retries = 3
api_retry_interval = 5
debug_api_calls = true

# LoxiLB Authentication (for LoxiLB API)
loxilb_auth_type = none

# Load Balancer Configuration
default_algorithm = ROUND_ROBIN
default_topology = SINGLE

# Health Monitoring
enable_health_monitor = true
enable_health_coordination = true
health_check_interval = 30

# Persistent Mapping
enable_persistent_mapping = true
mapping_storage_path = /var/lib/octavia/loxilb-mappings.json

# Network Configuration
use_mgmt_network = true
mgmt_network_id = ${MGMT_NETWORK_ID:-MGMT_NETWORK_ID_HERE}

# VM Configuration (Required for LoxiLB VM creation)
image_id = ${LOXILB_IMAGE_ID:-IMAGE_ID_HERE}
flavor_id = ${LOXILB_FLAVOR_ID:-FLAVOR_ID_HERE}
security_group_ids = ${SECURITY_GROUP_ID:-SECURITY_GROUP_ID_HERE}

# OpenStack Authentication (for API calls to OpenStack services)
auth_url = ${AUTH_URL:-http://KEYSTONE_IP:5000}
auth_type = password
username = octavia
password = ${OCTAVIA_PASSWORD:-PASSWORD_HERE}
user_domain_name = Default
project_name = service
project_domain_name = Default

# SSL Configuration
api_use_ssl = false
EOF

    sudo cp /tmp/octavia.conf "$KOLLA_CONFIG_DIR/octavia.conf"
    rm /tmp/octavia.conf
    
    echo "✓ Configuration created at $KOLLA_CONFIG_DIR/octavia.conf"
}

# Function to get OpenStack resource IDs for configuration
get_openstack_resources() {
    echo "Detecting OpenStack resources..."
    
    # Extract octavia password from kolla passwords file
    KOLLA_PASSWORDS_FILE="/etc/kolla/passwords.yml"
    if [ -f "$KOLLA_PASSWORDS_FILE" ]; then
        OCTAVIA_PASSWORD=$(grep "octavia_keystone_password:" "$KOLLA_PASSWORDS_FILE" 2>/dev/null | awk '{print $2}')
        if [ -n "$OCTAVIA_PASSWORD" ]; then
            echo "✓ Found octavia password from kolla passwords file"
        else
            echo "⚠ Could not extract octavia password from $KOLLA_PASSWORDS_FILE"
            OCTAVIA_PASSWORD="PASSWORD_HERE"
        fi
    else
        echo "⚠ Kolla passwords file not found at $KOLLA_PASSWORDS_FILE"
        OCTAVIA_PASSWORD="PASSWORD_HERE"
    fi
    
    # Extract Keystone auth_url from kolla admin-openrc.sh
    KOLLA_OPENRC_FILE="/etc/kolla/admin-openrc.sh"
    if [ -f "$KOLLA_OPENRC_FILE" ]; then
        AUTH_URL=$(grep "export OS_AUTH_URL=" "$KOLLA_OPENRC_FILE" 2>/dev/null | sed "s/export OS_AUTH_URL='\([^']*\)'.*/\1/")
        if [ -n "$AUTH_URL" ]; then
            echo "✓ Found auth_url from kolla admin-openrc: $AUTH_URL"
        else
            echo "⚠ Could not extract auth_url from $KOLLA_OPENRC_FILE"
            AUTH_URL="http://KEYSTONE_IP:5000"
        fi
    else
        echo "⚠ Kolla admin-openrc file not found at $KOLLA_OPENRC_FILE"
        AUTH_URL="http://KEYSTONE_IP:5000"
    fi
    
    # Try to get resource IDs if openstack CLI is available
    if command -v openstack &> /dev/null; then
        echo "OpenStack CLI detected, attempting to auto-detect resources..."
        
        # Get LoxiLB image ID
        LOXILB_IMAGE_ID=$(openstack image list --name "*loxilb*" -f value -c ID 2>/dev/null | head -n1)
        if [ -n "$LOXILB_IMAGE_ID" ]; then
            echo "✓ Found LoxiLB image: $LOXILB_IMAGE_ID"
        else
            echo "⚠ LoxiLB image not found - you'll need to create it"
            LOXILB_IMAGE_ID="LOXILB_IMAGE_ID_HERE"
        fi
        
        # Get management network ID  
        MGMT_NETWORK_ID=$(openstack network list --name "*octavia*mgmt*" -f value -c ID 2>/dev/null | head -n1)
        if [ -z "$MGMT_NETWORK_ID" ]; then
            MGMT_NETWORK_ID=$(openstack network list --name "*mgmt*" -f value -c ID 2>/dev/null | head -n1)
        fi
        if [ -n "$MGMT_NETWORK_ID" ]; then
            echo "✓ Found management network: $MGMT_NETWORK_ID"
        else
            echo "⚠ Management network not found - you'll need to create it"
            MGMT_NETWORK_ID="MGMT_NETWORK_ID_HERE"
        fi
        
        # Get LoxiLB flavor ID
        LOXILB_FLAVOR_ID=$(openstack flavor list --name "*loxilb*" -f value -c ID 2>/dev/null | head -n1)
        if [ -n "$LOXILB_FLAVOR_ID" ]; then
            echo "✓ Found LoxiLB flavor: $LOXILB_FLAVOR_ID"
        else
            echo "⚠ LoxiLB flavor not found - you'll need to create it"
            LOXILB_FLAVOR_ID="LOXILB_FLAVOR_ID_HERE"
        fi
        
        # Get security group ID
        SECURITY_GROUP_ID=$(openstack security group list --name "*loxilb*" -f value -c ID 2>/dev/null | head -n1)
        if [ -n "$SECURITY_GROUP_ID" ]; then
            echo "✓ Found LoxiLB security group: $SECURITY_GROUP_ID"
        else
            echo "⚠ LoxiLB security group not found - you'll need to create it"
            SECURITY_GROUP_ID="SECURITY_GROUP_ID_HERE"
        fi
        
    else
        echo "OpenStack CLI not available - using placeholders"
        LOXILB_IMAGE_ID="LOXILB_IMAGE_ID_HERE"
        MGMT_NETWORK_ID="MGMT_NETWORK_ID_HERE"
        LOXILB_FLAVOR_ID="LOXILB_FLAVOR_ID_HERE"
        SECURITY_GROUP_ID="SECURITY_GROUP_ID_HERE"
    fi
}

# Function to setup OpenStack resources
setup_openstack_resources() {
    echo
    echo "Setting up OpenStack resources..."
    
    # Get resource IDs first
    get_openstack_resources
    
    if command -v octavia-loxilb-setup &> /dev/null; then
        octavia-loxilb-setup --deployment-type production
        echo "✓ OpenStack resources created"
        
        # Re-detect resources after setup
        get_openstack_resources
    else
        echo "⚠ octavia-loxilb-setup not found in PATH"
        echo "Please run 'octavia-loxilb-setup --deployment-type production' manually"
        echo "Or install the driver first: pip install octavia-loxilb-driver"
    fi
}



# Function to restart Octavia services
restart_services() {
    echo
    echo "Restarting Octavia services..."
    
    for container in "${OCTAVIA_CONTAINERS[@]}"; do
        if docker ps --format "table {{.Names}}" | grep -q "^$container$"; then
            echo "Restarting $container..."
            docker restart "$container"
            if [ $? -eq 0 ]; then
                echo "✓ $container restarted successfully"
            else
                echo "✗ Failed to restart $container"
            fi
        fi
    done
}

# Function to verify installation
verify_installation() {
    echo
    echo "Verifying installation..."
    
    # Wait a bit for services to start
    sleep 10
    
    # Check if providers are available
    if docker exec octavia_api openstack loadbalancer provider list 2>/dev/null | grep -q "loxilb"; then
        echo "✓ LoxiLB provider is available"
    else
        echo "⚠ LoxiLB provider not found - check logs for issues"
    fi
    
    # Check container status
    echo
    echo "Container status:"
    docker ps --format "table {{.Names}}\t{{.Status}}" | grep octavia
}

# Function to show next steps
show_next_steps() {
    echo
    echo "=== Installation Complete ==="
    echo
    echo "⚠️  IMPORTANT: Configuration Review Required"
    echo "Please edit $KOLLA_CONFIG_DIR/octavia.conf and update the following:"
    echo
    
    # Check what needs to be configured
    
    if grep -q "KEYSTONE_IP" "$KOLLA_CONFIG_DIR/octavia.conf" 2>/dev/null; then
        echo "1. Update auth_url with your Keystone endpoint:"
        echo "   auth_url = http://YOUR_KEYSTONE_IP:5000"
    fi
    
    if grep -q "PASSWORD_HERE" "$KOLLA_CONFIG_DIR/octavia.conf" 2>/dev/null; then
        echo "2. Update password with the octavia service password"
    fi
    
    if grep -q "_ID_HERE" "$KOLLA_CONFIG_DIR/octavia.conf" 2>/dev/null; then
        echo "3. Update missing resource IDs (marked as *_ID_HERE)"
        echo "   Run 'octavia-loxilb-setup --deployment-type production' to create them"
    fi
    
    echo
    echo "Next steps after configuration:"
    echo "1. Restart Octavia containers:"
    echo "   docker restart octavia_api octavia_worker"
    echo
    echo "2. Verify providers are available:"
    echo "   docker exec octavia_api openstack loadbalancer provider list"
    echo
    echo "3. Test LoxiLB provider:"
    echo "   openstack loadbalancer create --provider loxilb \"
    echo "     --subnet-id <SUBNET_ID> test-loxilb-lb"
    echo
    echo "4. Check logs if needed:"
    echo "   tail -f /var/log/kolla/octavia/octavia-api.log"
    echo "   tail -f /var/log/kolla/octavia/octavia-worker.log"
    echo
    echo "Configuration files:"
    echo "- Kolla config: $KOLLA_CONFIG_DIR/octavia.conf"
    echo "- Container logs: /var/log/kolla/octavia/"
    echo
    echo "For reference, see your working configuration with proper values."
}

# Main execution
main() {
    echo "Starting LoxiLB Octavia Driver installation for Kolla-Ansible..."
    echo
    
    # Check prerequisites
    check_docker
    check_containers
    
    # Confirm with user
    echo
    read -p "Continue with installation? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled"
        exit 0
    fi
    
    # Run installation steps
    install_driver
    get_openstack_resources  # Get resource IDs first
    create_kolla_config
    setup_openstack_resources
    restart_services
    verify_installation
    show_next_steps
    
    echo
    echo "✓ LoxiLB Octavia Driver installation completed!"
}

# Run main function
main "$@"