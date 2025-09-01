#!/bin/bash

# configure-loxilb-octavia.sh
# Installs the LoxiLB driver and configures both Octavia API and Worker containers
# without using kolla-ansible reconfigure which would overwrite custom settings.

set -e

# Configuration
OCTAVIA_API_CONF="${1:-/etc/kolla/octavia-api/octavia.conf}"
OCTAVIA_WORKER_CONF="${2:-/etc/kolla/octavia-worker/octavia.conf}"
BACKUP_SUFFIX=".backup-$(date +%Y%m%d-%H%M%S)"
LOXILB_ENDPOINT="${3:-http://192.168.20.130:11111}"
LOXILB_RPC_TOPIC="${4:-loxilb_octavia}"
LOXILB_RPC_NAMESPACE="${5:-loxilb_controller}"

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
Usage: $0 [API_CONF_PATH] [WORKER_CONF_PATH] [LOXILB_ENDPOINT] [RPC_TOPIC] [RPC_NAMESPACE] [INSTALL_SOURCE] [SOURCE_PATH]

Directly modifies the Octavia API and Worker configuration files to add LoxiLB provider
without using kolla-ansible reconfigure which would overwrite custom settings.

Arguments:
    API_CONF_PATH       Path to octavia-api.conf file (default: /etc/kolla/octavia-api/octavia.conf)
    WORKER_CONF_PATH    Path to octavia-worker.conf file (default: /etc/kolla/octavia-worker/octavia.conf)
    LOXILB_ENDPOINT     LoxiLB API endpoint (default: http://192.168.20.130:11111)
    RPC_TOPIC           LoxiLB RPC topic (default: loxilb_octavia)
    RPC_NAMESPACE       LoxiLB RPC namespace (default: loxilb_controller)
    INSTALL_SOURCE      Source for driver installation: 'pip' or 'source' (default: pip)
    SOURCE_PATH         Path to source directory when INSTALL_SOURCE is 'source' (default: /opt/octavia-loxilb-driver)

Examples:
    $0                                                                # Use defaults (pip install)
    $0 /etc/kolla/octavia-api/octavia.conf /etc/kolla/octavia-worker/octavia.conf http://10.0.0.100:11111    # Custom paths and endpoint
    $0 /etc/kolla/octavia-api/octavia.conf /etc/kolla/octavia-worker/octavia.conf http://10.0.0.100:11111 loxilb_octavia loxilb_controller source /opt/loxilb-driver  # Full custom config

The script:
- Installs the LoxiLB driver package (from PyPI or source) in both API and Worker containers
- Modifies octavia.conf files to add LoxiLB provider configuration
- Configures RPC settings for the LoxiLB controller worker
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

# Check if octavia configuration files exist and are readable (with sudo if needed)
if ! sudo test -f "$OCTAVIA_API_CONF"; then
    print_error "Octavia API configuration file not found: $OCTAVIA_API_CONF"
    exit 1
fi

if ! sudo test -f "$OCTAVIA_WORKER_CONF"; then
    print_warning "Octavia Worker configuration file not found: $OCTAVIA_WORKER_CONF"
    print_warning "Will only configure the API container"
    WORKER_ENABLED=false
else
    WORKER_ENABLED=true
fi

# Print header
print_info "LoxiLB Octavia Direct Configuration Updater"
print_info "=========================================="
print_info "Directly modifies octavia.conf without kolla-ansible reconfigure"

# Check if we have sudo access
if ! sudo -n true 2>/dev/null; then
    print_warning "This script requires sudo privileges to modify configuration files"
    print_info "You may be prompted for your password"
fi

# Installation options
INSTALL_SOURCE="${6:-source}"
SOURCE_PATH="${7:-/opt/octavia-loxilb-driver}"

# Function to install the LoxiLB driver in the API container
install_loxilb_driver_api() {
    container_name="octavia_api"
    local_source=${1:-false}
    
    print_info "Checking if LoxiLB driver package is installed in $container_name..."
    if ! docker exec $container_name pip list | grep -q octavia-loxilb-driver; then
        print_info "LoxiLB driver package not found in $container_name."
        
        if [[ "$INSTALL_SOURCE" == "source" ]] || [ "$local_source" = true ]; then
            print_info "Installing from source in $container_name..."
            
            # Check if current directory is the driver directory
            if [ -f "./setup.py" ] && grep -q "octavia-loxilb-driver" "./setup.py"; then
                # Create a temporary directory for the source code
                TMP_DIR="/tmp/octavia-loxilb-driver-src-$(date +%s)"
                mkdir -p "$TMP_DIR"
                
                # Copy all Python files to the temp directory
                print_info "Preparing source files..."
                cp -r ./octavia_loxilb_driver "$TMP_DIR/"
                cp ./setup.py "$TMP_DIR/"
                cp ./setup.cfg "$TMP_DIR/" 2>/dev/null || true
                cp ./requirements.txt "$TMP_DIR/" 2>/dev/null || true
                
                # Create a simple setup.py if it doesn't exist
                if [ ! -f "$TMP_DIR/setup.py" ]; then
                    print_info "Creating minimal setup.py..."
                    cat > "$TMP_DIR/setup.py" << EOF
from setuptools import setup, find_packages
setup(
    name="octavia-loxilb-driver",
    version="1.0.0",
    packages=find_packages(),
)
EOF
                fi
                
                # Create a source distribution without using egg-info
                print_info "Creating source archive..."
                cd "$TMP_DIR"
                tar -czf /tmp/octavia-loxilb-driver.tar.gz .
                cd - > /dev/null
                
                print_info "Copying archive to $container_name:/tmp/"
                # Copy the archive to the container
                docker cp /tmp/octavia-loxilb-driver.tar.gz "$container_name:/tmp/"
                
                print_info "Installing package in $container_name..."
                # Clean up any previous installations
                docker exec $container_name pip uninstall -y octavia-loxilb-driver || true
                docker exec $container_name pip cache purge || true
                
                # Create a temporary directory in the container and extract the archive
                docker exec $container_name mkdir -p /tmp/octavia-loxilb-driver-install
                docker exec $container_name tar -xzf /tmp/octavia-loxilb-driver.tar.gz -C /tmp/octavia-loxilb-driver-install
                
                # Install the package with --no-deps to avoid building wheels
                if docker exec $container_name pip install --no-deps /tmp/octavia-loxilb-driver-install; then
                    print_success "Successfully installed LoxiLB driver from local source in $container_name"
                    # Clean up
                    docker exec $container_name rm -rf /tmp/octavia-loxilb-driver-install /tmp/octavia-loxilb-driver.tar.gz
                    rm -rf "$TMP_DIR" /tmp/octavia-loxilb-driver.tar.gz
                else
                    print_error "Failed to install LoxiLB driver from local source in $container_name"
                    exit 1
                fi
            elif [ -n "$SOURCE_PATH" ] && [ -d "$SOURCE_PATH" ]; then
                # If SOURCE_PATH is specified and exists
                # Create a temporary directory for the source code
                TMP_DIR="/tmp/octavia-loxilb-driver-src-$(date +%s)"
                mkdir -p "$TMP_DIR"
                
                print_info "Preparing source files from $SOURCE_PATH..."
                # Copy all Python files to the temp directory
                cp -r "$SOURCE_PATH/octavia_loxilb_driver" "$TMP_DIR/" 2>/dev/null || true
                cp "$SOURCE_PATH/setup.py" "$TMP_DIR/" 2>/dev/null || true
                cp "$SOURCE_PATH/setup.cfg" "$TMP_DIR/" 2>/dev/null || true
                cp "$SOURCE_PATH/requirements.txt" "$TMP_DIR/" 2>/dev/null || true
                
                # Create a simple setup.py if it doesn't exist
                if [ ! -f "$TMP_DIR/setup.py" ]; then
                    print_info "Creating minimal setup.py..."
                    cat > "$TMP_DIR/setup.py" << EOF
from setuptools import setup, find_packages
setup(
    name="octavia-loxilb-driver",
    version="1.0.0",
    packages=find_packages(),
)
EOF
                fi
                
                # Create a source distribution without using egg-info
                print_info "Creating source archive..."
                cd "$TMP_DIR"
                tar -czf /tmp/octavia-loxilb-driver.tar.gz .
                cd - > /dev/null
                
                print_info "Copying archive to $container_name:/tmp/"
                # Copy the archive to the container
                docker cp /tmp/octavia-loxilb-driver.tar.gz "$container_name:/tmp/"
                
                print_info "Installing package in $container_name..."
                # Clean up any previous installations
                docker exec $container_name pip uninstall -y octavia-loxilb-driver || true
                docker exec $container_name pip cache purge || true
                
                # Create a temporary directory in the container and extract the archive
                docker exec $container_name mkdir -p /tmp/octavia-loxilb-driver-install
                docker exec $container_name tar -xzf /tmp/octavia-loxilb-driver.tar.gz -C /tmp/octavia-loxilb-driver-install
                
                # Install the package with --no-deps to avoid building wheels
                if docker exec $container_name pip install --no-deps /tmp/octavia-loxilb-driver-install; then
                    print_success "Successfully installed LoxiLB driver from source in $container_name"
                    # Clean up
                    docker exec $container_name rm -rf /tmp/octavia-loxilb-driver-install /tmp/octavia-loxilb-driver.tar.gz
                    rm -rf "$TMP_DIR" /tmp/octavia-loxilb-driver.tar.gz
                else
                    print_error "Failed to install LoxiLB driver from source in $container_name"
                    exit 1
                fi
            else
                print_error "Source directory not found. Please specify a valid source path."
                print_info "Current directory does not appear to be the octavia-loxilb-driver source."
                exit 1
            fi
        else
            print_info "Installing from PyPI in $container_name..."
            
            # Install from PyPI
            if docker exec $container_name pip install octavia-loxilb-driver; then
                print_success "Successfully installed LoxiLB driver from PyPI in $container_name"
            else
                print_warning "Failed to install LoxiLB driver from PyPI in $container_name"
                print_info "PyPI installation failed. Trying to install from local source..."
                install_loxilb_driver $container_name true
            fi
        fi
    else
        print_success "LoxiLB driver package already installed in $container_name"
    fi
}

# Function to install the LoxiLB driver in the Worker container
install_loxilb_driver_worker() {
    container_name="octavia_worker"
    local_source=${1:-true}
    
    print_info "Checking if LoxiLB driver package is installed in $container_name..."
    if ! docker exec $container_name pip list | grep -q octavia-loxilb-driver; then
        print_info "LoxiLB driver package not found in $container_name."
        
        if [[ "$INSTALL_SOURCE" == "source" ]] || [ "$local_source" == true ]; then
            print_info "Installing from source in $container_name..."
            
            # Check if current directory is the driver directory
            if [ -f "./setup.py" ] && grep -q "octavia-loxilb-driver" "./setup.py"; then
                # Create a temporary directory for the source code
                TMP_DIR="/tmp/octavia-loxilb-driver-src-$(date +%s)"
                mkdir -p "$TMP_DIR"
                
                # Copy all Python files to the temp directory
                print_info "Preparing source files..."
                cp -r ./octavia_loxilb_driver "$TMP_DIR/"
                cp ./setup.py "$TMP_DIR/"
                cp ./setup.cfg "$TMP_DIR/" 2>/dev/null || true
                cp ./requirements.txt "$TMP_DIR/" 2>/dev/null || true
                
                # Create a simple setup.py if it doesn't exist
                if [ ! -f "$TMP_DIR/setup.py" ]; then
                    print_info "Creating minimal setup.py..."
                    cat > "$TMP_DIR/setup.py" << EOF
from setuptools import setup, find_packages
setup(
    name="octavia-loxilb-driver",
    version="1.0.0",
    packages=find_packages(),
)
EOF
                fi
                
                # Create a source distribution without using egg-info
                print_info "Creating source archive..."
                cd "$TMP_DIR"
                tar -czf /tmp/octavia-loxilb-driver.tar.gz .
                cd - > /dev/null
                
                print_info "Copying archive to $container_name:/tmp/"
                # Copy the archive to the container
                docker cp /tmp/octavia-loxilb-driver.tar.gz "$container_name:/tmp/"
                
                print_info "Installing package in $container_name..."
                # Clean up any previous installations
                docker exec $container_name pip uninstall -y octavia-loxilb-driver || true
                docker exec $container_name pip cache purge || true
                
                # Create a temporary directory in the container and extract the archive
                docker exec $container_name mkdir -p /tmp/octavia-loxilb-driver-install
                docker exec $container_name tar -xzf /tmp/octavia-loxilb-driver.tar.gz -C /tmp/octavia-loxilb-driver-install
                
                # Install the package as root user with -e option
                # print_info "Installing as root user with -e option..."
                # if docker exec -u root $container_name bash -c "cd /tmp/octavia-loxilb-driver-install && /var/lib/kolla/venv/bin/pip install -e ."; then
                #     print_success "Successfully installed LoxiLB driver from local source in $container_name"
                #     # Clean up
                #     docker exec $container_name rm -rf /tmp/octavia-loxilb-driver-install /tmp/octavia-loxilb-driver.tar.gz
                #     rm -rf "$TMP_DIR" /tmp/octavia-loxilb-driver.tar.gz
                # else
                #     print_error "Failed to install LoxiLB driver from local source in $container_name"
                #     exit 1
                # fi
            elif [ -n "$SOURCE_PATH" ] && [ -d "$SOURCE_PATH" ]; then
                # If SOURCE_PATH is specified and exists
                # Create a temporary directory for the source code
                TMP_DIR="/tmp/octavia-loxilb-driver-src-$(date +%s)"
                mkdir -p "$TMP_DIR"
                
                print_info "Preparing source files from $SOURCE_PATH..."
                # Copy all Python files to the temp directory
                cp -r "$SOURCE_PATH/octavia_loxilb_driver" "$TMP_DIR/" 2>/dev/null || true
                cp "$SOURCE_PATH/setup.py" "$TMP_DIR/" 2>/dev/null || true
                cp "$SOURCE_PATH/setup.cfg" "$TMP_DIR/" 2>/dev/null || true
                cp "$SOURCE_PATH/requirements.txt" "$TMP_DIR/" 2>/dev/null || true
                
                # Create a simple setup.py if it doesn't exist
                if [ ! -f "$TMP_DIR/setup.py" ]; then
                    print_info "Creating minimal setup.py..."
                    cat > "$TMP_DIR/setup.py" << EOF
from setuptools import setup, find_packages
setup(
    name="octavia-loxilb-driver",
    version="1.0.0",
    packages=find_packages(),
)
EOF
                fi
                
                # Create a source distribution without using egg-info
                print_info "Creating source archive..."
                cd "$TMP_DIR"
                tar -czf /tmp/octavia-loxilb-driver.tar.gz .
                cd - > /dev/null
                
                print_info "Copying archive to $container_name:/tmp/"
                # Copy the archive to the container
                docker cp /tmp/octavia-loxilb-driver.tar.gz "$container_name:/tmp/"
                
                print_info "Installing package in $container_name..."
                # Clean up any previous installations
                docker exec $container_name pip uninstall -y octavia-loxilb-driver || true
                docker exec $container_name pip cache purge || true
                
                # Create a temporary directory in the container and extract the archive
                docker exec $container_name mkdir -p /tmp/octavia-loxilb-driver-install
                docker exec $container_name tar -xzf /tmp/octavia-loxilb-driver.tar.gz -C /tmp/octavia-loxilb-driver-install
                
                # Install the package as root user with -e option
                print_info "Installing as root user with -e option..."
                # if docker exec -u root $container_name bash -c "cd /tmp/octavia-loxilb-driver-install && /var/lib/kolla/venv/bin/pip install -e ."; then
                #     print_success "Successfully installed LoxiLB driver from source in $container_name"
                #     Clean up
                #     docker exec $container_name rm -rf /tmp/octavia-loxilb-driver-install /tmp/octavia-loxilb-driver.tar.gz
                #     rm -rf "$TMP_DIR" /tmp/octavia-loxilb-driver.tar.gz
                # else
                #     print_error "Failed to install LoxiLB driver from source in $container_name"
                #     exit 1
                # fi
            else
                print_error "Source directory not found. Please specify a valid source path."
                print_info "Current directory does not appear to be the octavia-loxilb-driver source."
                exit 1
            fi
        else
            print_info "Installing from PyPI in $container_name..."
            
            # Install from PyPI as root user
            if docker exec -u root $container_name /var/lib/kolla/venv/bin/pip install octavia-loxilb-driver; then
                print_success "Successfully installed LoxiLB driver from PyPI in $container_name"
            else
                print_warning "Failed to install LoxiLB driver from PyPI in $container_name"
                print_info "PyPI installation failed. Trying to install from local source..."
                install_loxilb_driver_worker true
            fi
        fi
    else
        print_success "LoxiLB driver package already installed in $container_name"
    fi
}

# Install LoxiLB driver in API container
install_loxilb_driver_api

# Install LoxiLB driver in Worker container if enabled
if [ "$WORKER_ENABLED" = true ]; then
    install_loxilb_driver_worker
fi

print_info "Using API config: $OCTAVIA_API_CONF"
print_info "Using LoxiLB endpoint: $LOXILB_ENDPOINT"
if [ "$WORKER_ENABLED" = true ]; then
    print_info "Using Worker config: $OCTAVIA_WORKER_CONF"
    print_info "Using LoxiLB RPC topic: $LOXILB_RPC_TOPIC"
    print_info "Using LoxiLB RPC namespace: $LOXILB_RPC_NAMESPACE"
fi

# Create backups
API_BACKUP_FILE="${OCTAVIA_API_CONF}${BACKUP_SUFFIX}"
print_info "Creating API backup: $API_BACKUP_FILE"
sudo cp "$OCTAVIA_API_CONF" "$API_BACKUP_FILE"

if [ "$WORKER_ENABLED" = true ]; then
    WORKER_BACKUP_FILE="${OCTAVIA_WORKER_CONF}${BACKUP_SUFFIX}"
    print_info "Creating Worker backup: $WORKER_BACKUP_FILE"
    sudo cp "$OCTAVIA_WORKER_CONF" "$WORKER_BACKUP_FILE"
fi

# Function to configure a specific octavia.conf file
configure_octavia_conf() {
    conf_file=$1
    is_worker=$2
    
    print_info "Configuring $conf_file..."
    
    # Check if LoxiLB is already configured
    if sudo grep -q "\[loxilb\]" "$conf_file"; then
        print_info "LoxiLB section already exists in $conf_file."
        # We'll keep existing configuration but ensure required settings are present
    else
        print_info "Adding LoxiLB section to $conf_file..."
    fi

    # Check if LoxiLB is already in enabled_provider_drivers (only for API config)
    if [ "$is_worker" != "true" ]; then
        if sudo grep -q "loxilb:" "$conf_file"; then
            print_info "LoxiLB provider already enabled in configuration."
        else
            print_info "Adding LoxiLB to enabled_provider_drivers..."
            # Update enabled_provider_drivers to include loxilb
            sudo sed -i '/^enabled_provider_drivers[[:space:]]*=/ s/$/,loxilb:LoxiLB driver/' "$conf_file"
            
            # If no enabled_provider_drivers line exists, add it to [api_settings]
            if ! sudo grep -q "^enabled_provider_drivers" "$conf_file"; then
                if sudo grep -q "\[api_settings\]" "$conf_file"; then
                    sudo sed -i '/\[api_settings\]/a enabled_provider_drivers = amphora:Amphora provider,loxilb:LoxiLB driver' "$conf_file"
                else
                    # Add [api_settings] section if it doesn't exist
                    echo -e "\n[api_settings]\nenabled_provider_drivers = amphora:Amphora provider,loxilb:LoxiLB driver" | sudo tee -a "$conf_file" > /dev/null
                fi
            fi
        fi
    fi

    # Check if LoxiLB is already in enabled_provider_agents
    if sudo grep -q "^enabled_provider_agents" "$conf_file"; then
        if sudo grep -q "enabled_provider_agents.*loxilb" "$conf_file"; then
            print_info "LoxiLB agent already enabled in configuration."
            
            # Check for duplicate loxilb entries and fix if found
            if sudo grep -q "enabled_provider_agents.*loxilb.*loxilb" "$conf_file"; then
                print_warning "Found duplicate loxilb entries in enabled_provider_agents, fixing..."
                
                # Create a temporary file
                TEMP_FILE=$(mktemp)
                sudo cp "$conf_file" "$TEMP_FILE"
                
                # Fix duplicate entries using awk
                sudo awk '{
                    if ($0 ~ /^enabled_provider_agents[[:space:]]*=/) {
                        # Split the line by commas
                        split($0, parts, "=")
                        key = parts[1]
                        value = parts[2]
                        
                        # Process the value to remove duplicate loxilb entries
                        gsub(/^[[:space:]]+/, "", value)
                        split(value, agents, ",")
                        
                        # Rebuild the list without duplicates
                        new_agents = ""
                        found_loxilb = 0
                        for (i in agents) {
                            if (agents[i] == "loxilb") {
                                if (found_loxilb == 0) {
                                    if (new_agents != "") new_agents = new_agents ","
                                    new_agents = new_agents agents[i]
                                    found_loxilb = 1
                                }
                            } else {
                                if (new_agents != "") new_agents = new_agents ","
                                new_agents = new_agents agents[i]
                            }
                        }
                        
                        # Print the fixed line
                        print key "=" new_agents
                    } else {
                        print $0
                    }
                }' "$TEMP_FILE" | sudo tee "$conf_file" > /dev/null
                
                # Clean up
                rm -f "$TEMP_FILE"
            fi
        else
            print_info "Adding LoxiLB to enabled_provider_agents..."
            
            # Create a temporary file
            TEMP_FILE=$(mktemp)
            sudo cp "$conf_file" "$TEMP_FILE"
            
            # Add loxilb to enabled_provider_agents
            sudo awk '{
                if ($0 ~ /^enabled_provider_agents[[:space:]]*=/) {
                    print $0 ",loxilb"
                } else {
                    print $0
                }
            }' "$TEMP_FILE" | sudo tee "$conf_file" > /dev/null
            
            # Clean up
            rm -f "$TEMP_FILE"
        fi
    else
        # No enabled_provider_agents found, check if [driver_agent] section exists
        if sudo grep -q "\[driver_agent\]" "$conf_file"; then
            print_info "Adding enabled_provider_agents to [driver_agent] section..."
            sudo sed -i '/\[driver_agent\]/a enabled_provider_agents = amphora_agent,loxilb' "$conf_file"
        else
            # Add [driver_agent] section if it doesn't exist
            print_info "Adding [driver_agent] section with enabled_provider_agents..."
            echo -e "\n[driver_agent]\nenabled_provider_agents = amphora_agent,loxilb" | sudo tee -a "$conf_file" > /dev/null
        fi
    fi

    # Add or update the LoxiLB section
    print_info "Adding/updating LoxiLB configuration section in $conf_file..."
    
    # Check if [loxilb] section exists
    if ! sudo grep -q "\[loxilb\]" "$conf_file"; then
        # Add [loxilb] section with configuration
        if [ "$is_worker" = "true" ]; then
            # Worker-specific configuration with RPC settings
            sudo tee -a "$conf_file" << EOF

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
use_rpc = true
rpc_topic = $LOXILB_RPC_TOPIC
rpc_namespace = $LOXILB_RPC_NAMESPACE
EOF
        else
            # API configuration
            sudo tee -a "$conf_file" << EOF

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
use_rpc = true
rpc_namespace = $LOXILB_RPC_NAMESPACE

EOF
        fi
    else
        # Update existing [loxilb] section
        print_info "Updating existing [loxilb] section in $conf_file..."
    
        # Function to update or add a configuration option
        update_config() {
            section=$1
            option=$2
            value=$3
            target_file=$4
            
            # Check if section exists
            if ! sudo grep -q "\[$section\]" "$target_file"; then
                print_info "Adding [$section] section to $target_file..."
                echo "" | sudo tee -a "$target_file" > /dev/null
                echo "[$section]" | sudo tee -a "$target_file" > /dev/null
            fi
            
            # Check if option exists in section
            if sudo grep -A 20 "\[$section\]" "$target_file" | grep -q "^$option *="; then
                print_info "Updating $option in [$section] section of $target_file..."
                # Create a temporary file with the updated content
                TEMP_FILE=$(mktemp)
                sudo cp "$target_file" "$TEMP_FILE"
                
                # Process the file with awk for safer text replacement
                sudo awk -v section="[$section]" -v option="$option" -v value="$value" '
                BEGIN { in_section=0; updated=0; }
                /^\[.*\]/ { if ($0 == section) in_section=1; else in_section=0; }
                {
                    if (in_section && $0 ~ "^"option"[ \t]*=" && !updated) {
                        print option" = "value;
                        updated=1;
                    } else {
                        print $0;
                    }
                }' "$TEMP_FILE" | sudo tee "$target_file" > /dev/null
                
                # Clean up
                rm -f "$TEMP_FILE"
            else
                # Add option to section - create a temporary file and use awk
                TEMP_FILE=$(mktemp)
                sudo cp "$target_file" "$TEMP_FILE"
                
                sudo awk -v section="[$section]" -v option="$option" -v value="$value" '
                BEGIN { in_section=0; added=0; }
                /^\[.*\]/ { 
                    if (in_section && !added) {
                        added=1;
                    }
                    if ($0 == section) in_section=1; else in_section=0;
                    print $0;
                    if (in_section) {
                        print option" = "value;
                        added=1;
                    }
                    next;
                }
                { print $0; }' "$TEMP_FILE" | sudo tee "$target_file" > /dev/null
                
                # Clean up
                rm -f "$TEMP_FILE"
            fi
        }
        
        # Update LoxiLB configuration options
        update_config "loxilb" "api_endpoints" "$LOXILB_ENDPOINT" "$conf_file"
        update_config "loxilb" "auth_type" "none" "$conf_file"
        update_config "loxilb" "api_timeout" "30" "$conf_file"
        update_config "loxilb" "debug_api_calls" "true" "$conf_file"
        update_config "loxilb" "default_algorithm" "ROUND_ROBIN" "$conf_file"
        update_config "loxilb" "enable_health_monitor" "true" "$conf_file"
        update_config "loxilb" "enable_persistent_mapping" "true" "$conf_file"
        update_config "loxilb" "mapping_storage_path" "/var/lib/octavia/loxilb-mappings.json" "$conf_file"
        update_config "loxilb" "enable_health_coordination" "true" "$conf_file"
        update_config "loxilb" "health_check_interval" "30" "$conf_file"
        update_config "loxilb" "log_level" "INFO" "$conf_file"
        update_config "loxilb" "use_rpc" "true" "$conf_file"
        
        # Add RPC configuration for worker
        if [ "$is_worker" = "true" ]; then
            update_config "loxilb" "rpc_topic" "$LOXILB_RPC_TOPIC" "$conf_file"
            update_config "loxilb" "rpc_namespace" "$LOXILB_RPC_NAMESPACE" "$conf_file"
        fi
    fi
}

# Configure both API and Worker
configure_octavia_conf "$OCTAVIA_API_CONF" "false"

if [ "$WORKER_ENABLED" = true ]; then
    configure_octavia_conf "$OCTAVIA_WORKER_CONF" "true"
fi

print_success "Configuration updated successfully!"
print_info ""
print_info "Next steps:"
print_info "1. Restart the Octavia API container:"
print_info "   docker restart octavia_api"

if [ "$WORKER_ENABLED" = true ]; then
    print_info "2. Restart the Octavia Worker container:"
    print_info "   docker restart octavia_worker"
    print_info "3. Verify the provider is registered:"
    print_info "   openstack loadbalancer provider list"
    print_info "4. If the provider is not listed, check if the driver package is installed:"
    print_info "   docker exec octavia_api pip list | grep octavia-loxilb"
    print_info "   docker exec octavia_worker pip list | grep octavia-loxilb"
    print_info "5. Check the worker logs for RPC server startup:"
    print_info "   docker logs octavia_worker | grep -i loxilb"
else
    print_info "2. Verify the provider is registered:"
    print_info "   openstack loadbalancer provider list"
    print_info "3. If the provider is not listed, check if the driver package is installed:"
    print_info "   docker exec octavia_api pip list | grep octavia-loxilb"
fi

print_info ""
print_info "API backup saved as: $API_BACKUP_FILE"
if [ "$WORKER_ENABLED" = true ]; then
    print_info "Worker backup saved as: $WORKER_BACKUP_FILE"
fi

# Show diff if possible
if command -v diff >/dev/null 2>&1; then
    print_info ""
    print_info "API config changes made:"
    echo "=============="
    diff -u "$API_BACKUP_FILE" "$OCTAVIA_API_CONF" || true
    
    if [ "$WORKER_ENABLED" = true ]; then
        print_info ""
        print_info "Worker config changes made:"
        echo "=============="
        diff -u "$WORKER_BACKUP_FILE" "$OCTAVIA_WORKER_CONF" || true
    fi
fi

print_info ""
print_success "Ready to apply with: docker restart octavia_api"