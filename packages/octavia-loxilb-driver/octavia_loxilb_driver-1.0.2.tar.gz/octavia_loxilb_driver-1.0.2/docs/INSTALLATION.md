# LoxiLB Octavia Driver Installation Guide

This guide provides comprehensive instructions for installing and configuring the LoxiLB Octavia Driver in your OpenStack environment.

## Prerequisites

- **OpenStack Version**: Zed or later
- **Working OpenStack**: Functioning OpenStack cloud with Octavia service
- **Administrator Access**: OpenStack admin credentials and system access
- **Python Environment**: Python 3.8+ with pip
- **Network Setup**: Available networks for Octavia management

## Quick Start

For users who want to get started immediately:

```bash
# 1. Install the driver
pip install octavia-loxilb-driver

# 2. Run automated setup (creates all required resources)
octavia-loxilb-setup

# 3. Follow the configuration prompts
```

The automated setup will handle resource creation and configuration generation.

## Installation Methods

### Method 1: PyPI Installation (Recommended)

```bash
# Install from PyPI
pip install octavia-loxilb-driver

# Verify installation
octavia-loxilb-setup --help
octavia-loxilb-health-check --help
```

### Method 2: Development Installation

```bash
# Clone repository
git clone https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver.git
cd octavia-loxilb-driver

# Install in development mode
pip install -e .
```

## Deployment Profiles

The setup script supports three pre-configured deployment profiles:

### DevStack Profile
- **Purpose**: Development and testing
- **Resources**: 1 vCPU, 4GB RAM, 20GB disk
- **Usage**: `octavia-loxilb-setup --deployment-type devstack`

### Standard Profile (Default)
- **Purpose**: Standard production deployment
- **Resources**: 2 vCPUs, 8GB RAM, 40GB disk  
- **Usage**: `octavia-loxilb-setup --deployment-type standard`

### Production Profile
- **Purpose**: High-performance production environments
- **Resources**: 4 vCPUs, 16GB RAM, 80GB disk
- **Usage**: `octavia-loxilb-setup --deployment-type production`

## Kolla-Ansible Deployment

For kolla-ansible environments where Octavia runs as containers, follow these steps to add LoxiLB provider alongside existing Amphora provider:

### Option 1: Extend Existing Octavia Containers (Recommended)

#### Step 1: Install Driver in Running Containers
```bash
# Install LoxiLB driver in all Octavia containers
for container in octavia_api octavia_worker octavia_controller_worker; do
  if docker ps --format "table {{.Names}}" | grep -q "^$container$"; then
    echo "Installing driver in $container..."
    docker exec $container pip install octavia-loxilb-driver
  fi
done
```

#### Step 2: Update Octavia Configuration
Add LoxiLB configuration to your kolla-ansible Octavia config:

```bash
# Create kolla config override
mkdir -p /etc/kolla/config/octavia
cat > /etc/kolla/config/octavia.conf << EOF
[api_settings]
enabled_provider_drivers = amphora:The Amphora driver,loxilb:LoxiLB driver

[driver_agent]
enabled_provider_agents = amphora_agent,loxilb

[loxilb]
# LoxiLB API Configuration (REQUIRED)
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

# Network Configuration (REQUIRED)
use_mgmt_network = true
mgmt_network_id = YOUR_OCTAVIA_MGMT_NETWORK_ID

# VM Configuration (REQUIRED for LoxiLB VM creation)
image_id = YOUR_LOXILB_IMAGE_ID
flavor_id = YOUR_LOXILB_FLAVOR_ID
security_group_ids = YOUR_SECURITY_GROUP_ID

# OpenStack Authentication (REQUIRED for API calls to OpenStack services)
auth_url = YOUR_KEYSTON_AUTH_URL
auth_type = password
username = octavia
password = YOUR_OCTAVIA_ACCOUNT_PASSWORD
user_domain_name = Default
project_name = service
project_domain_name = Default

# SSL Configuration
api_use_ssl = false
EOF
```

#### Step 3: Setup OpenStack Resources
```bash
# Run setup to create required OpenStack resources
octavia-loxilb-setup --deployment-type production
```

#### Step 4: Restart Octavia Services
```bash
# Restart to pick up new configuration and driver
docker restart octavia_api octavia_worker octavia_controller_worker
```

#### Step 5: Verify Installation
```bash
# Check that LoxiLB provider is available
docker exec octavia_api openstack loadbalancer provider list

# Expected output should include:
# | loxilb | False   |
```

### Option 2: Build Custom Kolla Images

For production environments, build custom images with the driver pre-installed:

#### Step 1: Create Custom Kolla Build Config
```bash
cat > /etc/kolla/kolla-build.conf << EOF
[octavia-base]
type = url
location = https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver/archive/main.tar.gz

[octavia-api]
type = local
install_type = pip
location = /path/to/octavia-loxilb-driver

[octavia-worker] 
type = local
install_type = pip
location = /path/to/octavia-loxilb-driver
EOF
```

#### Step 2: Build Custom Images
```bash
# Build images with LoxiLB driver included
kolla-build --config-file /etc/kolla/kolla-build.conf \
  octavia-api octavia-worker octavia-controller-worker
```

#### Step 3: Update Kolla-Ansible Configuration
```yaml
# In globals.yml
octavia_enable: "yes"
octavia_provider_drivers:
  - name: amphora
    description: "The Amphora driver"
  - name: loxilb  
    description: "LoxiLB driver"

# Use custom images
octavia_api_image: "{{ docker_registry }}/octavia-api:custom-latest"
octavia_worker_image: "{{ docker_registry }}/octavia-worker:custom-latest"
```

### Verification for Kolla-Ansible

```bash
# Check providers are available
docker exec octavia_api openstack loadbalancer provider list

# Expected output:
# +--------+---------+
# | name   | default |
# +--------+---------+
# | amphora| True    |
# | loxilb | False   |
# +--------+---------+

# Test LoxiLB provider
openstack loadbalancer create --provider loxilb \
  --subnet-id <SUBNET_ID> test-loxilb-lb
```

### Troubleshooting Kolla-Ansible Deployment

**Container Not Found:**
```bash
# List all containers
docker ps --format "table {{.Names}}	{{.Image}}	{{.Status}}"

# Check kolla-ansible logs
journalctl -u kolla-ansible
```

**Driver Installation Issues:**
```bash
# Check if driver is installed in container
docker exec octavia_api pip list | grep octavia-loxilb-driver

# Reinstall if needed
docker exec octavia_api pip install --force-reinstall octavia-loxilb-driver
```

## Custom Configuration

For advanced deployments, create a JSON configuration file to override defaults:

```json
{
  "flavor": {
    "name": "custom-loxilb-flavor",
    "vcpus": 2,
    "ram": 4096,
    "disk": 30
  },
  "network": {
    "name": "custom-octavia-mgmt-network", 
    "cidr": "172.16.100.0/24"
  },
  "security_group": {
    "name": "custom-loxilb-security-group"
  },
  "image": {
    "name": "loxilb-vm-image",
    "url": "https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver/releases/download/vm-v1.0.0/loxilb-vm-standard-v1.0.0.qcow2.gz"
  }
}
```

Use with: `octavia-loxilb-setup --custom-config /path/to/config.json`

## Step-by-Step Setup

### 1. Install the Package

```bash
pip install octavia-loxilb-driver
```

### 2. Download LoxiLB VM Image

The setup script can automatically download and register the LoxiLB VM image, or you can do it manually:

```bash
# Manual image registration
wget https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver/releases/download/vm-v1.0.0/loxilb-vm-standard-v1.0.0.qcow2.gz
openstack image create --disk-format qcow2 --container-format bare \
  --public --file loxilb-vm.qcow2 loxilb-vm-image
```

### 3. Run Automated Setup

```bash
# Basic setup with default (standard) profile
octavia-loxilb-setup

# Or specify deployment type
octavia-loxilb-setup --deployment-type production

# With custom configuration
octavia-loxilb-setup --custom-config /path/to/config.json
```

### 4. Manual Configuration (Alternative)

If you prefer manual configuration, the setup script can generate a configuration template:

```bash
# Generate configuration template
octavia-loxilb-setup --output-config /tmp/loxilb-octavia.conf

# Review and integrate into /etc/octavia/octavia.conf
```

## Network Requirements

The LoxiLB driver requires two types of networks:

### Management Network
- **Purpose**: Communication between Octavia controller and LoxiLB VMs
- **Default**: `octavia-mgmt-net` with CIDR `192.168.1.0/24`
- **Ports**: 8091 (LoxiLB API), 9443 (BGP), 11111/22222 (HA)

### Data Networks
- **Purpose**: User traffic load balancing
- **Configuration**: Existing tenant networks
- **Requirements**: LoxiLB VMs must have access to data networks

## Security Groups

The setup creates security groups with required rules:

**Management Security Group** (`loxilb-mgmt-sec-grp`):
- SSH (22/tcp)
- ICMP (ping)
- LoxiLB API (8091/tcp)
- BGP (9443/tcp) 
- HA Communication (11111/tcp, 22222/tcp)

## Configuration Integration

### Automatic Integration

The setup script modifies `/etc/octavia/octavia.conf`:

```ini
[api_settings]
enabled_provider_drivers = loxilb:loxilb

[loxilb]
# LoxiLB API Configuration
api_timeout = 30
api_retries = 3
debug_api_calls = true

# OpenStack Authentication (for VM provisioning)
auth_url = YOUR_KEYSTONE_AUTH_URL
auth_type = password
username = octavia
password = YOUR_OCTAVIA_PASSWORD

# OpenStack resource IDs (populated by setup script)
image_id = YOUR_LOXILB_IMAGE_ID
flavor_id = YOUR_LOXILB_FLAVOR_ID
mgmt_network_id = YOUR_OCTAVIA_MGMT_NETWORK_ID
security_group_ids = YOUR_SECURITY_GROUP_ID
```

### Manual Integration

For manual configuration, add the following sections to `/etc/octavia/octavia.conf`:

```ini
[api_settings]
enabled_provider_drivers = amphora:amphora,loxilb:loxilb

[loxilb]
# LoxiLB API Configuration
api_timeout = 30
api_retries = 3
debug_api_calls = true

# OpenStack Authentication (REQUIRED for VM provisioning)
auth_url = YOUR_KEYSTONE_AUTH_URL
auth_type = password
username = octavia
password = YOUR_OCTAVIA_PASSWORD
user_domain_name = Default
project_name = service
project_domain_name = Default

# VM Configuration (REQUIRED)
image_id = YOUR_LOXILB_IMAGE_ID
flavor_id = YOUR_LOXILB_FLAVOR_ID
security_group_ids = YOUR_SECURITY_GROUP_ID

# Network Configuration (REQUIRED)
mgmt_network_id = YOUR_OCTAVIA_MGMT_NETWORK_ID
```

## Service Restart

After configuration changes, restart Octavia services:

### For Systemd Deployments
```bash
sudo systemctl restart octavia-api octavia-worker octavia-controller-worker
```

### For Kolla-Ansible Deployments
```bash
# Restart existing Octavia containers
docker restart octavia_api octavia_worker octavia_controller_worker


```

## Verification

### Health Check

```bash
# Run built-in health check
octavia-loxilb-health-check

# Check provider availability
openstack loadbalancer provider list
```

Expected output:
```
+--------+---------+
| name   | default |
+--------+---------+
| amphora| True    |
| loxilb | False   |
+--------+---------+
```

### Create Test Load Balancer

```bash
# Create a test load balancer with LoxiLB
openstack loadbalancer create --provider loxilb \
  --subnet-id <SUBNET_ID> test-loxilb-lb
```

## Troubleshooting

### Common Issues

**1. Provider Not Available**
```bash
# Check Octavia configuration
sudo grep -A 10 "enabled_provider_drivers" /etc/octavia/octavia.conf

# Verify driver installation
pip show octavia-loxilb-driver
```

**2. LoxiLB VM Issues**
```bash
# Check LoxiLB VM status
openstack server list --name loxilb-vm

# Check VM console logs
openstack console log show <LOXILB_VM_ID>

# Check security group rules
openstack security group show loxilb-mgmt-sec-grp
```

**3. Resource Creation Failures**
```bash
# Check OpenStack credentials
openstack token issue

# Verify quotas
openstack quota show
```

### Log Analysis

Check Octavia logs for detailed error information:

```bash
# Controller logs
sudo tail -f /var/log/octavia/octavia-worker.log

# API logs  
sudo tail -f /var/log/octavia/octavia-api.log
```

## Advanced Configuration

### High Availability Setup

For production deployments, the driver automatically creates and manages LoxiLB VM instances:

```ini
[loxilb]
# High Availability is handled through VM placement and health monitoring
enable_health_monitor = true
enable_health_coordination = true
health_check_interval = 30
```

### Custom Resource Names

Override default resource naming:

```json
{
  "flavor": {"name": "prod-loxilb-flavor"},
  "network": {"name": "prod-octavia-mgmt-net"},
  "security_group": {"name": "prod-loxilb-sec-grp"}
}
```

### Integration with Existing Resources

Use existing OpenStack resources:

```bash
# Use existing network
octavia-loxilb-setup --management-network existing-mgmt-net

# Use existing flavor
octavia-loxilb-setup --flavor existing-flavor
```

## Migration from Other Providers

### From Amphora

1. **Backup existing configuration**
2. **Install LoxiLB driver alongside Amphora**
3. **Test with new load balancers**
4. **Migrate existing load balancers** (contact support)

### Configuration Coexistence

Both providers can run simultaneously:

```ini
[api_settings]
enabled_provider_drivers = amphora:amphora,loxilb:loxilb
default_provider_driver = amphora
```

## Support and Resources

- **GitHub Repository**: https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver
- **LoxiLB Documentation**: https://github.com/loxilb-io/loxilb
- **Issue Reporting**: GitHub Issues
- **Community**: LoxiLB Slack/Discord

## Next Steps

After successful installation:

1. **Review Architecture Documentation** - Understanding LoxiLB integration
2. **Configure Monitoring** - Set up health checks and alerts  
3. **Plan Migration Strategy** - If migrating from existing providers
4. **Performance Tuning** - Optimize for your specific workload

---

*This guide assumes a working OpenStack environment. For OpenStack installation, refer to the official OpenStack documentation.*