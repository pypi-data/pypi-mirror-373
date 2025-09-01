#!/bin/bash
set -e

echo "🔧 Installing Octavia in MicroStack VM..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() { echo -e "${BLUE}[STEP]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

# Function to handle repository issues
fix_repositories() {
    print_warning "Fixing potential repository issues..."
    sudo apt clean
    sudo rm -rf /var/lib/apt/lists/*
    sudo apt-get clean
    return 0
}

# Pre-emptively fix repository cache
fix_repositories

print_step "Installing Octavia and dependencies"

# Fix repository cache issues
print_warning "Cleaning repository cache to fix potential hash mismatches..."
sudo apt clean
sudo rm -rf /var/lib/apt/lists/*

# Update packages with better error handling
print_step "Updating package lists..."
if ! sudo apt update --fix-missing; then
    print_warning "Initial update failed, trying alternative approach..."
    sudo apt clean
    sudo rm -rf /var/lib/apt/lists/*
    sudo apt update --fix-missing || {
        print_error "Package update failed, but continuing with installation..."
    }
fi

# Install Octavia API server
print_step "Installing Octavia packages..."
sudo apt install -y python3-octavia octavia-api octavia-worker octavia-housekeeping octavia-health-manager || {
    print_error "Failed to install some Octavia packages, trying individual installation..."
    sudo apt install -y python3-octavia || print_warning "python3-octavia failed"
    sudo apt install -y octavia-api || print_warning "octavia-api failed"
    sudo apt install -y octavia-worker || print_warning "octavia-worker failed"
    sudo apt install -y octavia-housekeeping || print_warning "octavia-housekeeping failed"
    sudo apt install -y octavia-health-manager || print_warning "octavia-health-manager failed"
}

print_step "Configuring Octavia database"

# Check if MySQL/MariaDB is running
print_step "Checking MySQL service status"
if sudo systemctl is-active --quiet mysql; then
    print_success "MySQL service is running"
elif sudo systemctl is-active --quiet mariadb; then
    print_success "MariaDB service is running"
elif snap services microstack.mysql | grep -q "active"; then
    print_success "MicroStack MySQL is running"
else
    print_warning "MySQL service not detected, attempting to start it"
    sudo systemctl start mysql || sudo systemctl start mariadb || print_warning "Could not start MySQL service"
fi

# Source OpenStack credentials
source /var/snap/microstack/common/etc/microstack.rc

# Detect the VM's IP address dynamically
VM_IP=$(ip route get 8.8.8.8 | head -1 | awk '{print $7}')
echo "Detected VM IP: $VM_IP"

# Create Octavia database using MicroStack's MySQL with better error handling
print_step "Setting up MySQL database for Octavia"

# Try different approaches to connect to MySQL
if sudo /snap/bin/microstack.mysql -u root << 'EOF'
CREATE DATABASE IF NOT EXISTS octavia;
GRANT ALL PRIVILEGES ON octavia.* TO 'octavia'@'localhost' IDENTIFIED BY 'octavia_password';
GRANT ALL PRIVILEGES ON octavia.* TO 'octavia'@'%' IDENTIFIED BY 'octavia_password';
FLUSH PRIVILEGES;
EOF
then
    print_success "Database created successfully"
else
    print_warning "Standard MySQL connection failed, trying alternative approaches..."
    
    # Try with snap run
    if sudo snap run microstack.mysql -u root << 'EOF'
CREATE DATABASE IF NOT EXISTS octavia;
GRANT ALL PRIVILEGES ON octavia.* TO 'octavia'@'localhost' IDENTIFIED BY 'octavia_password';
GRANT ALL PRIVILEGES ON octavia.* TO 'octavia'@'%' IDENTIFIED BY 'octavia_password';
FLUSH PRIVILEGES;
EOF
    then
        print_success "Database created with snap run"
    else
        print_warning "MySQL setup failed, trying to configure manually..."
        
        # Try direct mysql client with TCP connection
        if mysql -h 127.0.0.1 -P 3306 -u root << 'EOF'
CREATE DATABASE IF NOT EXISTS octavia;
GRANT ALL PRIVILEGES ON octavia.* TO 'octavia'@'localhost' IDENTIFIED BY 'octavia_password';
GRANT ALL PRIVILEGES ON octavia.* TO 'octavia'@'%' IDENTIFIED BY 'octavia_password';
FLUSH PRIVILEGES;
EOF
        then
            print_success "Database created with direct TCP connection"
        else
            print_error "All MySQL connection attempts failed"
            print_warning "Continuing installation, but database setup may be incomplete"
            print_warning "You may need to manually configure the Octavia database"
        fi
    fi
fi

print_step "Creating Octavia configuration"

# Create Octavia config directory
sudo mkdir -p /etc/octavia

# Create basic Octavia configuration
sudo tee /etc/octavia/octavia.conf > /dev/null << EOF
[DEFAULT]
debug = True

[database]
connection = mysql+pymysql://octavia:octavia_password@localhost/octavia

[keystone_authtoken]
www_authenticate_uri = http://$VM_IP:5000
auth_url = http://$VM_IP:5000
memcached_servers = $VM_IP:11211
auth_type = password
project_domain_id = default
user_domain_id = default
project_name = service
username = octavia
password = octavia_password

[service_auth]
auth_url = http://$VM_IP:5000/v3
auth_type = password
username = octavia
password = octavia_password
user_domain_name = Default
project_name = service
project_domain_name = Default

[api_settings]
bind_host = 0.0.0.0
bind_port = 9876

[oslo_messaging]
transport_url = rabbit://openstack:rabbitmq_password@$VM_IP:5672/

[oslo_policy]
policy_file = /etc/octavia/policy.yaml

[health_manager]
bind_ip = $VM_IP
bind_port = 5555
heartbeat_key = insecure

[house_keeping]
load_balancer_expiry_age = 3600
amphora_expiry_age = 3600

[amphora_agent]
admin_log_targets = $VM_IP:5555

[controller_worker]
amp_image_tag = amphora
amp_ssh_key_name = amphora-key
amp_secgroup_list = lb-mgmt-sec-grp
amp_boot_network_list = lb-mgmt-net
amp_flavor_id = 65
network_driver = allowed_address_pairs_driver
compute_driver = compute_nova_driver
amphora_driver = amphora_haproxy_rest_driver

[task_flow]
engine = parallel
max_workers = 5
EOF

print_step "Creating Octavia service user"

# Create octavia user in keystone
/snap/bin/microstack.openstack user create --domain default --password octavia_password octavia || true
/snap/bin/microstack.openstack role add --project service --user octavia admin || true

# Create octavia service
/snap/bin/microstack.openstack service create --name octavia --description "OpenStack Load Balancer" load-balancer || true

# Create octavia endpoints
/snap/bin/microstack.openstack endpoint create --region RegionOne load-balancer public http://$VM_IP:9876 || true
/snap/bin/microstack.openstack endpoint create --region RegionOne load-balancer internal http://$VM_IP:9876 || true
/snap/bin/microstack.openstack endpoint create --region RegionOne load-balancer admin http://$VM_IP:9876 || true

print_step "Setting up Octavia database schema"

# Setup database with better error handling
if sudo -u octavia octavia-db-manage --config-file /etc/octavia/octavia.conf upgrade head; then
    print_success "Database schema created successfully"
else
    print_warning "Database schema setup failed, trying alternative approach..."
    
    # Try without sudo -u octavia
    if octavia-db-manage --config-file /etc/octavia/octavia.conf upgrade head; then
        print_success "Database schema created with alternative method"
    else
        print_error "Database schema setup failed"
        print_warning "Continuing with installation, but Octavia may not work properly"
        print_warning "You may need to run: octavia-db-manage --config-file /etc/octavia/octavia.conf upgrade head"
    fi
fi

print_step "Creating systemd service files"

# Create systemd service for octavia-api
sudo tee /etc/systemd/system/octavia-api.service > /dev/null << 'EOF'
[Unit]
Description=OpenStack Load Balancer API Server
After=network.target

[Service]
Type=simple
User=octavia
Group=octavia
ExecStart=/usr/bin/octavia-api --config-file=/etc/octavia/octavia.conf
KillMode=process
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for octavia-worker
sudo tee /etc/systemd/system/octavia-worker.service > /dev/null << 'EOF'
[Unit]
Description=OpenStack Load Balancer Worker
After=network.target

[Service]
Type=simple
User=octavia
Group=octavia
ExecStart=/usr/bin/octavia-worker --config-file=/etc/octavia/octavia.conf
KillMode=process
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Create octavia user for services
sudo useradd --system --shell /bin/false octavia || true
sudo chown -R octavia:octavia /etc/octavia

print_step "Starting Octavia services"

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable octavia-api octavia-worker
sudo systemctl start octavia-api octavia-worker

print_step "Verifying Octavia installation"

# Wait a moment for services to start
sleep 5

# Check if octavia is running
if sudo systemctl is-active --quiet octavia-api; then
    print_success "Octavia API service is running"
else
    print_error "Octavia API service failed to start"
    sudo journalctl -u octavia-api --no-pager -l
fi

if sudo systemctl is-active --quiet octavia-worker; then
    print_success "Octavia Worker service is running"
else
    print_error "Octavia Worker service failed to start"
    sudo journalctl -u octavia-worker --no-pager -l
fi

# Test octavia endpoint
if curl -f -s http://$VM_IP:9876/ >/dev/null; then
    print_success "Octavia API is accessible"
else
    print_warning "Octavia API not yet accessible (may need more time to start)"
fi

print_step "Installing LoxiLB driver in Octavia environment"

# Check if driver directory exists
if [ ! -d "/home/ubuntu/octavia-loxilb-driver" ]; then
    print_warning "LoxiLB driver directory not found, skipping driver installation"
    print_warning "You can manually transfer and install the driver later"
else
    # Install the LoxiLB driver
    cd /home/ubuntu/octavia-loxilb-driver
    sudo python3 setup.py develop || {
        print_error "Failed to install LoxiLB driver"
        print_warning "Continuing without driver installation"
    }
fi

# Update octavia configuration to include LoxiLB provider
sudo tee -a /etc/octavia/octavia.conf > /dev/null << 'EOF'

[driver_agents]
enabled_provider_drivers = amphora:'Amphora driver',loxilb:'LoxiLB driver'

[loxilb]
# LoxiLB driver configuration
loxilb_endpoint = http://192.168.64.1:8080
EOF

# Restart octavia services to pick up new configuration
print_step "Restarting Octavia services"
sudo systemctl restart octavia-api octavia-worker || {
    print_error "Failed to restart some Octavia services"
    print_warning "Check service status manually"
}

print_success "Octavia installation complete!"
echo ""
echo "🎉 Next steps:"
echo "1. Test with: /snap/bin/microstack.openstack loadbalancer provider list"
echo "2. You should see both 'amphora' and 'loxilb' providers"
echo "3. Run: make test-e2e"
echo ""
