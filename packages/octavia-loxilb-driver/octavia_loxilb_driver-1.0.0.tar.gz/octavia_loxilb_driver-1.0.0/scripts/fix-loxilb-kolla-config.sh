#!/bin/bash

# fix-loxilb-kolla-config.sh
# Directly modifies the Octavia API container configuration to add LoxiLB provider
# without using kolla-ansible reconfigure which would overwrite custom settings.

set -e

# Configuration
OCTAVIA_CONF="${1:-/etc/kolla/octavia-api/octavia.conf}"
BACKUP_SUFFIX=".backup-$(date +%Y%m%d-%H%M%S)"
LOXILB_ENDPOINT="${2:-http://192.168.20.130:11111}"

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

show_help() {
    cat << EOF
Usage: $0 [OCTAVIA_CONF_PATH] [LOXILB_ENDPOINT] [INSTALL_SOURCE] [SOURCE_PATH]

Directly modifies the Octavia API configuration file to add LoxiLB provider
without using kolla-ansible reconfigure which would overwrite custom settings.

Arguments:
    OCTAVIA_CONF_PATH   Path to octavia.conf file (default: /etc/kolla/octavia-api/octavia.conf)
    LOXILB_ENDPOINT     LoxiLB API endpoint (default: http://192.168.20.130:11111)
    INSTALL_SOURCE      Source for driver installation: 'pip' or 'source' (default: pip)
    SOURCE_PATH         Path to source directory when INSTALL_SOURCE is 'source' (default: /opt/octavia-loxilb-driver)

Examples:
    $0                                                                # Use defaults (pip install)
    $0 /etc/kolla/octavia-api/octavia.conf http://10.0.0.100:11111    # Custom path and endpoint (pip install)
    $0 /etc/kolla/octavia-api/octavia.conf http://10.0.0.100:11111 source /opt/loxilb-driver  # Install from source

The script:
- Installs the LoxiLB driver package (from PyPI or source)
- Modifies octavia.conf to add LoxiLB provider configuration
- Preserves all existing custom configuration

EOF
}

# Parse arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
esac

print_info "LoxiLB Octavia Direct Configuration Updater"
print_info "=========================================="
print_info "Directly modifies octavia.conf without kolla-ansible reconfigure"

# Check if octavia.conf exists and is readable (with sudo if needed)
if ! sudo test -f "$OCTAVIA_CONF"; then
    print_error "Octavia configuration file not found: $OCTAVIA_CONF"
    exit 1
fi

# Check if we have sudo access
if ! sudo -n true 2>/dev/null; then
    print_warning "This script requires sudo privileges to modify $OCTAVIA_CONF"
    print_info "You may be prompted for your password"
fi

# Installation options
INSTALL_SOURCE="${3:-pip}"
SOURCE_PATH="${4:-/opt/octavia-loxilb-driver}"

# Check if we need to install the LoxiLB driver package
print_info "Checking if LoxiLB driver package is installed..."
if ! docker exec octavia_api pip list | grep -q octavia-loxilb-driver; then
    print_info "LoxiLB driver package not found."
    
    if [[ "$INSTALL_SOURCE" == "source" ]]; then
        print_info "Installing from source at $SOURCE_PATH..."
        
        # Check if source directory exists
        if [[ ! -d "$SOURCE_PATH" ]]; then
            print_warning "Source directory $SOURCE_PATH not found."
            print_info "Please provide a valid source directory or use 'pip' installation method."
            print_info "Example: $0 $OCTAVIA_CONF $LOXILB_ENDPOINT pip"
            print_info "Or: $0 $OCTAVIA_CONF $LOXILB_ENDPOINT source /path/to/source"
            exit 1
        fi
        
        # Copy source to container
        print_info "Copying source to container..."
        CONTAINER_PATH="/tmp/octavia-loxilb-driver"
        docker cp "$SOURCE_PATH" "octavia_api:$CONTAINER_PATH"
        
        # Install from source
        if ! docker exec octavia_api pip install -e "$CONTAINER_PATH"; then
            print_warning "Failed to install LoxiLB driver from source."
            print_info "You may need to install it manually with:"
            print_info "docker cp $SOURCE_PATH octavia_api:/tmp/octavia-loxilb-driver"
            print_info "docker exec octavia_api pip install -e /tmp/octavia-loxilb-driver"
        else
            print_success "LoxiLB driver installed from source successfully!"
        fi
    else
        print_info "Installing from PyPI..."
        if ! docker exec octavia_api pip install octavia-loxilb-driver; then
            print_warning "Failed to install LoxiLB driver package from PyPI."
            print_info "You may need to install it manually with:"
            print_info "docker exec octavia_api pip install octavia-loxilb-driver"
        else
            print_success "LoxiLB driver package installed from PyPI successfully!"
        fi
    fi
else
    print_info "LoxiLB driver package is already installed."
fi

print_info "Using octavia.conf: $OCTAVIA_CONF"
print_info "Using LoxiLB endpoint: $LOXILB_ENDPOINT"

# Create backup
BACKUP_FILE="${OCTAVIA_CONF}${BACKUP_SUFFIX}"
print_info "Creating backup: $BACKUP_FILE"
sudo cp "$OCTAVIA_CONF" "$BACKUP_FILE"

# Check if LoxiLB is already configured
if sudo grep -q "\[loxilb\]" "$OCTAVIA_CONF"; then
    print_info "LoxiLB section already exists in configuration."
    # We'll keep existing configuration but ensure required settings are present
else
    print_info "Adding LoxiLB section to configuration..."
fi

# Check if LoxiLB is already in enabled_provider_drivers
if sudo grep -q "loxilb:" "$OCTAVIA_CONF"; then
    print_info "LoxiLB provider already enabled in configuration."
else
    print_info "Adding LoxiLB to enabled_provider_drivers..."
    # Update enabled_provider_drivers to include loxilb
    sudo sed -i '/^enabled_provider_drivers[[:space:]]*=/ s/$/,loxilb:LoxiLB driver/' "$OCTAVIA_CONF"
    
    # If no enabled_provider_drivers line exists, add it to [api_settings]
    if ! sudo grep -q "^enabled_provider_drivers" "$OCTAVIA_CONF"; then
        if sudo grep -q "\[api_settings\]" "$OCTAVIA_CONF"; then
            sudo sed -i '/\[api_settings\]/a enabled_provider_drivers = amphora:Amphora provider,loxilb:LoxiLB driver' "$OCTAVIA_CONF"
        else
            # Add [api_settings] section if it doesn't exist
            echo -e "\n[api_settings]\nenabled_provider_drivers = amphora:Amphora provider,loxilb:LoxiLB driver" | sudo tee -a "$OCTAVIA_CONF" > /dev/null
        fi
    fi
fi

# Check if LoxiLB is already in enabled_provider_agents
if sudo grep -q "loxilb" "$OCTAVIA_CONF" | grep "enabled_provider_agents"; then
    print_info "LoxiLB agent already enabled in configuration."
else
    print_info "Adding LoxiLB to enabled_provider_agents..."
    # Update enabled_provider_agents to include loxilb
    if sudo grep -q "^enabled_provider_agents" "$OCTAVIA_CONF"; then
        sudo sed -i '/^enabled_provider_agents[[:space:]]*=/ s/$/,loxilb/' "$OCTAVIA_CONF"
    else
        # Add to [driver_agent] section if it exists
        if sudo grep -q "\[driver_agent\]" "$OCTAVIA_CONF"; then
            sudo sed -i '/\[driver_agent\]/a enabled_provider_agents = amphora_agent,loxilb' "$OCTAVIA_CONF"
        else
            # Add [driver_agent] section if it doesn't exist
            echo -e "\n[driver_agent]\nenabled_provider_agents = amphora_agent,loxilb" | sudo tee -a "$OCTAVIA_CONF" > /dev/null
        fi
    fi
fi

# Add or update the LoxiLB section
print_info "Adding/updating LoxiLB configuration section..."

# Check if [loxilb] section exists
if ! sudo grep -q "\[loxilb\]" "$OCTAVIA_CONF"; then
    # Add [loxilb] section with configuration
    sudo tee -a "$OCTAVIA_CONF" << EOF

[loxilb]
api_endpoints = $LOXILB_ENDPOINT
auth_type = none
api_timeout = 30
debug_api_calls = true
default_algorithm = ROUND_ROBIN
enable_health_monitor = true
enable_persistent_mapping = true
mapping_storage_path = /var/lib/octavia/loxilb-mappings.json
enable_health_coordination = true
health_check_interval = 30
log_level = INFO
EOF
else
    # Update existing [loxilb] section
    print_info "Updating existing [loxilb] section..."
    
    # Function to update or add a configuration option
    update_config() {
        local section="$1"
        local option="$2"
        local value="$3"
        
        # Check if option exists in section
        if sudo grep -A 20 "\[$section\]" "$OCTAVIA_CONF" | grep -q "^$option[[:space:]]*="; then
            # Update existing option
            sudo sed -i "/\[$section\]/,/\[.*\]/ s/^$option[[:space:]]*=.*/$option = $value/" "$OCTAVIA_CONF"
        else
            # Add option to section
            sudo sed -i "/\[$section\]/a $option = $value" "$OCTAVIA_CONF"
        fi
    }
    
    # Update LoxiLB configuration options
    update_config "loxilb" "api_endpoints" "$LOXILB_ENDPOINT"
    update_config "loxilb" "auth_type" "none"
    update_config "loxilb" "api_timeout" "30"
    update_config "loxilb" "debug_api_calls" "true"
    update_config "loxilb" "default_algorithm" "ROUND_ROBIN"
    update_config "loxilb" "enable_health_monitor" "true"
    update_config "loxilb" "enable_persistent_mapping" "true"
    update_config "loxilb" "mapping_storage_path" "/var/lib/octavia/loxilb-mappings.json"
    update_config "loxilb" "enable_health_coordination" "true"
    update_config "loxilb" "health_check_interval" "30"
    update_config "loxilb" "log_level" "INFO"
fi

print_success "Configuration updated successfully!"
print_info ""
print_info "Next steps:"
print_info "1. Restart the Octavia API container:"
print_info "   docker restart octavia_api"
print_info "2. Verify the provider is registered:"
print_info "   openstack loadbalancer provider list"
print_info "3. If the provider is not listed, check if the driver package is installed:"
print_info "   docker exec octavia_api pip list | grep octavia-loxilb"
print_info "4. If needed, install the package manually:"
print_info "   docker exec octavia_api pip install octavia-loxilb-driver"
print_info ""
print_info "Backup saved as: $BACKUP_FILE"

# Show diff if possible
if command -v diff >/dev/null 2>&1; then
    print_info ""
    print_info "Changes made:"
    echo "=============="
    diff -u "$BACKUP_FILE" "$OCTAVIA_CONF" || true
fi

print_info ""
print_success "Ready to apply with: docker restart octavia_api"
