# Octavia LoxiLB Driver Installation Guide

## Overview

The Octavia LoxiLB Driver provides high-performance load balancing capabilities for OpenStack Octavia using LoxiLB as the backend. This guide covers installation, configuration, and basic usage.

## Prerequisites

- OpenStack environment with Octavia service installed
- Python 3.8 or higher
- Administrative access to OpenStack configuration files
- LoxiLB instances available for load balancing

## Installation Methods

### Method 1: Install from PyPI (Recommended)

```bash
pip install octavia-loxilb-driver
```

### Method 2: Install from Source

```bash
git clone https://github.com/openstack/octavia-loxilb-driver.git
cd octavia-loxilb-driver
pip install -e .
```

### Method 3: Install for Development

```bash
git clone https://github.com/openstack/octavia-loxilb-driver.git
cd octavia-loxilb-driver
pip install -r requirements-dev.txt
pip install -e .
```

## Configuration

### 1. Octavia Configuration

Add the LoxiLB driver to your Octavia configuration file (`/etc/octavia/octavia.conf`):

```ini
[api_settings]
enabled_provider_drivers = amphora:'Amphora provider',loxilb:'LoxiLB provider'
default_provider_driver = loxilb

[driver_agent]
enabled_provider_agents = loxilb

[loxilb]
# LoxiLB specific configuration
loxilb_endpoint = http://your-loxilb-host:8080
default_topology = SINGLE
key_name = your-ssh-key-name  # Optional: SSH key for LoxiLB VMs
image_id = your-loxilb-image-id
flavor_id = your-flavor-id
network_id = your-management-network-id
security_group_ids = your-security-group-id
```

### 2. Required Configuration Parameters

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `loxilb_endpoint` | LoxiLB API endpoint URL | Yes | - |
| `image_id` | LoxiLB VM image ID | Yes | - |
| `flavor_id` | OpenStack flavor for LoxiLB VMs | Yes | - |
| `network_id` | Management network ID | Yes | - |
| `security_group_ids` | Security group IDs (comma-separated) | Yes | - |
| `default_topology` | Default load balancer topology | No | SINGLE |
| `key_name` | SSH key name for VM access | No | None |

### 3. Service Registration

Register the LoxiLB provider with Octavia:

```bash
# Restart Octavia services
sudo systemctl restart octavia-api
sudo systemctl restart octavia-worker
sudo systemctl restart octavia-health-manager

# Start LoxiLB controller worker
octavia-loxilb-controller-worker --config-file /etc/octavia/octavia.conf
```

## Usage

### Creating a Load Balancer

```bash
# Create a load balancer with LoxiLB provider
openstack loadbalancer create --name my-lb --vip-subnet-id <subnet-id> --provider loxilb

# Create a listener
openstack loadbalancer listener create --name my-listener --protocol HTTP --protocol-port 80 my-lb

# Create a pool
openstack loadbalancer pool create --name my-pool --lb-algorithm ROUND_ROBIN --listener my-listener --protocol HTTP

# Add members
openstack loadbalancer member create --subnet-id <member-subnet-id> --address 192.168.1.10 --protocol-port 80 my-pool
openstack loadbalancer member create --subnet-id <member-subnet-id> --address 192.168.1.11 --protocol-port 80 my-pool
```

## Verification

### Check Driver Status

```bash
# List available providers
openstack loadbalancer provider list

# Check load balancer status
openstack loadbalancer show my-lb

# Verify LoxiLB VM is created and running
openstack server list | grep loxilb
```

### Test Load Balancing

```bash
# Get VIP address
VIP=$(openstack loadbalancer show my-lb -f value -c vip_address)

# Test load balancing
curl http://$VIP
```

## Troubleshooting

### Common Issues

1. **Driver not found**: Ensure the driver is properly installed and registered in octavia.conf
2. **VM creation fails**: Check image_id, flavor_id, and network_id configuration
3. **Network connectivity issues**: Verify security groups allow required traffic
4. **LoxiLB API unreachable**: Check loxilb_endpoint configuration and network connectivity

### Log Files

- Octavia API: `/var/log/octavia/octavia-api.log`
- Octavia Worker: `/var/log/octavia/octavia-worker.log`
- LoxiLB Controller: Check systemd journal or configured log location

### Debug Mode

Enable debug logging in octavia.conf:

```ini
[DEFAULT]
debug = True
```

## Support

- Documentation: https://docs.openstack.org/octavia-loxilb-driver/
- Bug Reports: https://github.com/openstack/octavia-loxilb-driver/issues
- Mailing List: openstack-discuss@lists.openstack.org

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
