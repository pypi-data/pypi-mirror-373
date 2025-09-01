# Octavia LoxiLB Driver User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Configuration Reference](#configuration-reference)
4. [Load Balancer Operations](#load-balancer-operations)
5. [Advanced Features](#advanced-features)
6. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
7. [Best Practices](#best-practices)
8. [FAQ](#faq)

## Introduction

The Octavia LoxiLB Driver integrates LoxiLB's high-performance load balancing capabilities with OpenStack Octavia, providing:

- **High Performance**: Hardware-accelerated load balancing with eBPF
- **Scalability**: Support for thousands of concurrent connections
- **Flexibility**: Multiple load balancing algorithms and health checking
- **Integration**: Seamless integration with OpenStack networking

### Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Octavia API   │    │  LoxiLB Driver  │    │   LoxiLB VM     │
│                 │◄──►│                 │◄──►│                 │
│  Load Balancer  │    │   Controller    │    │  Load Balancer  │
│   Management    │    │     Worker      │    │     Engine      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

### 1. Installation

```bash
# Install from PyPI
pip install octavia-loxilb-driver

# Or install from source
git clone https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver.git
cd octavia-loxilb-driver
pip install -e .
```

### 2. Basic Configuration

Edit `/etc/octavia/octavia.conf`:

```ini
[api_settings]
enabled_provider_drivers = amphora:The Amphora driver,loxilb:LoxiLB driver

[loxilb]
# LoxiLB API Configuration
api_timeout = 30
api_retries = 3
debug_api_calls = true

# OpenStack Authentication (for VM provisioning)
auth_url = http://YOUR_KEYSTONE_IP:5000
auth_type = password
username = octavia
password = YOUR_OCTAVIA_PASSWORD
user_domain_name = Default
project_name = service
project_domain_name = Default

# VM Configuration (Required for LoxiLB VM creation)
image_id = YOUR_LOXILB_IMAGE_ID
flavor_id = YOUR_LOXILB_FLAVOR_ID
security_group_ids = YOUR_SECURITY_GROUP_ID

# Network Configuration
mgmt_network_id = YOUR_OCTAVIA_MGMT_NETWORK_ID
```

### 3. Run Automated Setup

```bash
# Run automated setup to create required resources
octavia-loxilb-setup --deployment-type production

# Follow the configuration prompts to update /etc/octavia/octavia.conf
# Then restart services
sudo systemctl restart octavia-api octavia-worker
```

### 4. Create Your First Load Balancer

```bash
# Create load balancer
openstack loadbalancer create --name my-first-lb --vip-subnet-id <subnet-id> --provider loxilb

# Add listener
openstack loadbalancer listener create --name web-listener --protocol HTTP --protocol-port 80 my-first-lb

# Create pool
openstack loadbalancer pool create --name web-pool --lb-algorithm ROUND_ROBIN --listener web-listener --protocol HTTP

# Add backend servers
openstack loadbalancer member create --subnet-id <subnet-id> --address 192.168.1.10 --protocol-port 80 web-pool
openstack loadbalancer member create --subnet-id <subnet-id> --address 192.168.1.11 --protocol-port 80 web-pool
```

## Configuration Reference

### Core Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `auth_url` | string | Required | OpenStack Keystone authentication URL |
| `username` | string | Required | OpenStack service username (typically 'octavia') |
| `password` | string | Required | OpenStack service password |
| `image_id` | string | Required | LoxiLB VM image ID |
| `flavor_id` | string | Required | OpenStack flavor for LoxiLB VMs |
| `mgmt_network_id` | string | Required | Management network ID |
| `security_group_ids` | list | Required | Security group IDs |
| `api_timeout` | int | 30 | API request timeout in seconds |
| `api_retries` | int | 3 | Number of API retry attempts |

### Advanced Configuration

```ini
[loxilb]
# Performance tuning
api_timeout = 30
api_retries = 3
api_retry_interval = 5

# Health Monitoring
enable_health_monitor = true
enable_health_coordination = true
health_check_interval = 30

# Persistent Mapping
enable_persistent_mapping = true
mapping_storage_path = /var/lib/octavia/loxilb-mappings.json

# Load Balancer Configuration
default_algorithm = ROUND_ROBIN
default_topology = SINGLE

# Logging
debug_api_calls = true
```

## Load Balancer Operations

### Creating Load Balancers

#### Basic HTTP Load Balancer
```bash
openstack loadbalancer create \
  --name web-lb \
  --vip-subnet-id <subnet-id> \
  --provider loxilb

openstack loadbalancer listener create \
  --name http-listener \
  --protocol HTTP \
  --protocol-port 80 \
  web-lb

openstack loadbalancer pool create \
  --name web-pool \
  --lb-algorithm ROUND_ROBIN \
  --listener http-listener \
  --protocol HTTP
```

#### HTTPS Load Balancer with SSL Termination
```bash
# Create certificate
openstack secret store --name my-cert --payload-content-type "application/octet-stream" --payload-content-encoding base64 --payload "$(base64 < cert.pem)"

# Create HTTPS listener
openstack loadbalancer listener create \
  --name https-listener \
  --protocol TERMINATED_HTTPS \
  --protocol-port 443 \
  --default-tls-container-ref <secret-ref> \
  web-lb
```

#### TCP Load Balancer
```bash
openstack loadbalancer listener create \
  --name tcp-listener \
  --protocol TCP \
  --protocol-port 3306 \
  db-lb

openstack loadbalancer pool create \
  --name db-pool \
  --lb-algorithm LEAST_CONNECTIONS \
  --listener tcp-listener \
  --protocol TCP
```

### Managing Pool Members

#### Add Members
```bash
# Add single member
openstack loadbalancer member create \
  --subnet-id <subnet-id> \
  --address 192.168.1.10 \
  --protocol-port 80 \
  --weight 100 \
  web-pool

# Batch add members
openstack loadbalancer member set \
  --name "web-servers" \
  web-pool \
  --member subnet-id=<subnet-id>,address=192.168.1.10,protocol-port=80 \
  --member subnet-id=<subnet-id>,address=192.168.1.11,protocol-port=80
```

#### Update Member Weights
```bash
openstack loadbalancer member set \
  --weight 200 \
  web-pool <member-id>
```

#### Disable/Enable Members
```bash
# Disable member (graceful)
openstack loadbalancer member set \
  --admin-state-up False \
  web-pool <member-id>

# Enable member
openstack loadbalancer member set \
  --admin-state-up True \
  web-pool <member-id>
```

### Health Monitoring

#### HTTP Health Check
```bash
openstack loadbalancer healthmonitor create \
  --name http-health \
  --delay 5 \
  --timeout 3 \
  --max-retries 3 \
  --type HTTP \
  --url-path /health \
  --expected-codes 200 \
  web-pool
```

#### TCP Health Check
```bash
openstack loadbalancer healthmonitor create \
  --name tcp-health \
  --delay 10 \
  --timeout 5 \
  --max-retries 2 \
  --type TCP \
  db-pool
```

## Advanced Features

### Load Balancing Algorithms

| Algorithm | Description | Use Case |
|-----------|-------------|----------|
| `ROUND_ROBIN` | Requests distributed evenly | General purpose |
| `LEAST_CONNECTIONS` | Route to server with fewest connections | Long-lived connections |
| `SOURCE_IP` | Hash based on client IP | Session persistence |
| `SOURCE_IP_PORT` | Hash based on client IP and port | Enhanced session persistence |

### Session Persistence

```bash
# Create pool with session persistence
openstack loadbalancer pool create \
  --name sticky-pool \
  --lb-algorithm ROUND_ROBIN \
  --listener web-listener \
  --protocol HTTP \
  --session-persistence type=HTTP_COOKIE,cookie-name=JSESSIONID
```

### SSL/TLS Configuration

#### Multiple Certificates (SNI)
```bash
# Add additional certificates
openstack loadbalancer listener set \
  --sni-container-refs <cert-ref-1> <cert-ref-2> \
  https-listener
```

#### Custom SSL Policies
```bash
# Create custom SSL policy
openstack loadbalancer listener set \
  --tls-ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256 \
  --tls-versions TLSv1.2:TLSv1.3 \
  https-listener
```

## Monitoring and Troubleshooting

### Status Monitoring

```bash
# Check load balancer status
openstack loadbalancer show my-lb

# Check all components
openstack loadbalancer status show my-lb

# Monitor member health
openstack loadbalancer member list web-pool
```

### Log Analysis

#### Octavia Logs
```bash
# API logs
tail -f /var/log/octavia/octavia-api.log

# Worker logs
tail -f /var/log/octavia/octavia-worker.log

# Health manager logs
tail -f /var/log/octavia/octavia-health-manager.log
```

#### LoxiLB VM Logs
```bash
# Check LoxiLB VM status
openstack server list --name loxilb-vm

# Get VM console logs
openstack console log show <loxilb-vm-id>

# SSH to LoxiLB VM (if SSH key configured)
ssh ubuntu@<loxilb-vm-ip>

# Check LoxiLB service inside VM
sudo systemctl status loxilb

# View LoxiLB logs
sudo journalctl -u loxilb -f
```

### Common Issues and Solutions

#### Issue: Load Balancer Stuck in PENDING_CREATE
```bash
# Check worker logs
grep ERROR /var/log/octavia/octavia-worker.log

# Common causes:
# - LoxiLB VM image not found
# - Flavor not available
# - Management network/security group issues
# - OpenStack authentication problems
# - Insufficient quotas

# Check quotas
openstack quota show

# Verify resources exist
openstack image show <image-id>
openstack flavor show <flavor-id>
openstack network show <network-id>
```

#### Issue: Members Showing as DOWN
```bash
# Check health monitor configuration
openstack loadbalancer healthmonitor show <monitor-id>

# Verify member connectivity
# SSH to LoxiLB VM and test connectivity
ping <member-ip>
telnet <member-ip> <member-port>
```

#### Issue: VIP Not Responding
```bash
# Check VIP port status
openstack port list | grep <vip-ip>

# Verify security groups
openstack security group rule list <security-group-id>

# Check LoxiLB VM status
openstack server show <loxilb-vm-id>

# Test LoxiLB API connectivity
curl http://<loxilb-vm-ip>:8091/config/loadbalancer/all

# Run health check
octavia-loxilb-health-check
```

## Best Practices

### Security

1. **Network Isolation**: Use dedicated networks for management and data traffic
2. **Security Groups**: Configure minimal required access
3. **SSL/TLS**: Always use HTTPS for sensitive applications
4. **Regular Updates**: Keep LoxiLB images updated

### Performance

1. **Resource Sizing**: Choose appropriate flavors for expected load
2. **Health Checks**: Configure reasonable intervals to avoid overhead
3. **Connection Limits**: Set appropriate connection limits
4. **Monitoring**: Implement comprehensive monitoring

### High Availability

1. **Multiple AZs**: Deploy across multiple availability zones
2. **Backup Strategy**: Regular configuration backups
3. **Disaster Recovery**: Document recovery procedures
4. **Testing**: Regular failover testing

### Operational

1. **Naming Conventions**: Use consistent naming for resources
2. **Tagging**: Tag resources for organization and billing
3. **Documentation**: Document custom configurations
4. **Change Management**: Use version control for configurations

## FAQ

### Q: Can I migrate from Amphora to LoxiLB?
A: Yes, but it requires recreating load balancers. Plan for maintenance windows.

### Q: What's the maximum number of members per pool?
A: LoxiLB supports thousands of members, but practical limits depend on your infrastructure.

### Q: Can I use custom LoxiLB images?
A: Yes, but we recommend using official images from GitHub releases. For custom images, ensure they include LoxiLB software and proper cloud-init configuration.

### Q: How do I backup load balancer configurations?
A: Use OpenStack CLI to export configurations and store them in version control.

### Q: Is IPv6 supported?
A: Yes, LoxiLB supports both IPv4 and IPv6 configurations.

### Q: Can I use LoxiLB with other OpenStack services?
A: Yes, LoxiLB integrates with Nova, Neutron, and other OpenStack services.

### Q: What monitoring tools are recommended?
A: Prometheus, Grafana, and OpenStack telemetry services work well with LoxiLB.

### Q: How do I scale load balancers?
A: Use flavor resize or implement active-standby topologies for scaling.

## Support and Community

- **GitHub Repository**: https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver
- **Bug Reports**: https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver/issues
- **Documentation**: [Installation Guide](INSTALLATION.md) | [Quick Start](QUICKSTART.md) | [Troubleshooting](TROUBLESHOOTING.md)
- **LoxiLB Community**: https://github.com/loxilb-io/loxilb
- **VM Images**: Check GitHub releases for pre-built LoxiLB VM images
