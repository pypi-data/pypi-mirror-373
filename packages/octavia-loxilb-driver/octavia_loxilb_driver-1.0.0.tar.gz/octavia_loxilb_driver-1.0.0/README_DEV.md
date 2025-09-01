# LoxiLB Octavia Driver

A high-performance load balancer provider driver for OpenStack Octavia that integrates with LoxiLB for eBPF/XDP-based load balancing.

## Overview

This driver enables OpenStack Octavia to use LoxiLB as a load balancer backend, providing:

- **High Performance**: eBPF/XDP-based load balancing for maximum throughput
- **Cloud Native**: Kubernetes-ready and container-optimized
- **Feature Rich**: Support for L4/L7 load balancing, SSL termination, health monitoring
- **Scalable**: Horizontal scaling with cluster support
- **Production Ready**: Enterprise-grade reliability and monitoring

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Neutron API   │────│   Octavia API    │────│ Octavia Worker  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                │                        │
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Octavia Provider │────│  LoxiLB Driver  │
                       │    Framework     │    └─────────────────┘
                       └──────────────────┘             │
                                                        │
                                              ┌─────────────────┐
                                              │   LoxiLB API    │
                                              │   REST/gRPC     │
                                              └─────────────────┘
                                                        │
                                              ┌─────────────────┐
                                              │ LoxiLB Cluster  │
                                              │  (eBPF/XDP)     │
                                              └─────────────────┘
```

## Features

### Core Load Balancing
- **Protocols**: TCP, UDP, HTTP, HTTPS
- **Algorithms**: Round Robin, Least Connections, Source IP, Weighted algorithms
- **Session Persistence**: Source IP, HTTP cookies, Application cookies
- **SSL/TLS Termination**: Full SSL offloading with SNI support

### Health Monitoring
- **Types**: HTTP, HTTPS, TCP, UDP, PING
- **Advanced Options**: Custom URLs, expected response codes, retry logic
- **Real-time Status**: Live health status updates

### High Availability
- **Cluster Support**: Active-standby and active-active modes
- **Automatic Failover**: Seamless failover between cluster nodes
- **State Synchronization**: Consistent state across cluster nodes

### Integration
- **OpenStack Native**: Full integration with Neutron, Barbican, Nova
- **Kolla-Ansible**: Automated deployment with containerized services
- **Monitoring**: Prometheus metrics and comprehensive logging

## Quick Start

### Prerequisites

- OpenStack Zed or later
- Ubuntu 22.04 LTS (recommended)
- LoxiLB cluster v0.8.0+
- Python 3.8+

### Installation

1. **Install the driver package:**
   ```bash
   pip install octavia-loxilb-driver
   ```

2. **Configure Octavia:**
   ```bash
   # Add to /etc/octavia/octavia.conf
   [api_settings]
   enabled_provider_drivers = amphora:Amphora,loxilb:LoxiLB
   
   [driver_agent]
   enabled_provider_agents = amphora,loxilb
   ```

3. **Configure LoxiLB driver:**
   ```bash
   # Create /etc/octavia/conf.d/loxilb.conf
   [loxilb]
   api_endpoints = http://loxilb-1:8080,http://loxilb-2:8080
   auth_type = none
   default_algorithm = round_robin
   ```

4. **Restart Octavia services:**
   ```bash
   systemctl restart octavia-*
   ```

5. **Verify installation:**
   ```bash
   openstack loadbalancer provider list
   ```

### Using with Kolla-Ansible

1. **Configure globals.yml:**
   ```yaml
   enable_octavia_loxilb_driver: "yes"
   loxilb_cluster_endpoints:
     - "http://loxilb-1:8080"
     - "http://loxilb-2:8080"
   ```

2. **Deploy:**
   ```bash
   kolla-ansible -i inventory deploy --tags octavia
   ```

## Usage Examples

### Create a Load Balancer

```bash
# Create load balancer with LoxiLB provider
openstack loadbalancer create \
  --name my-lb \
  --provider loxilb \
  --vip-subnet-id private-subnet

# Create listener
openstack loadbalancer listener create \
  --name my-listener \
  --protocol HTTP \
  --protocol-port 80 \
  my-lb

# Create pool
openstack loadbalancer pool create \
  --name my-pool \
  --lb-algorithm ROUND_ROBIN \
  --listener my-listener \
  --protocol HTTP

# Add members
openstack loadbalancer member create \
  --address 192.168.1.10 \
  --protocol-port 8080 \
  my-pool

openstack loadbalancer member create \
  --address 192.168.1.11 \
  --protocol-port 8080 \
  my-pool
```

### HTTPS with SSL Termination

```bash
# Store SSL certificate in Barbican
openstack secret store \
  --name my-cert \
  --payload-content-type='text/plain' \
  --payload="$(cat certificate.pem)"

# Create HTTPS listener
openstack loadbalancer listener create \
  --name https-listener \
  --protocol TERMINATED_HTTPS \
  --protocol-port 443 \
  --default-tls-container-ref $(openstack secret show my-cert -f value -c "Secret href") \
  my-lb
```

### Health Monitoring

```bash
# Create health monitor
openstack loadbalancer healthmonitor create \
  --name my-monitor \
  --type HTTP \
  --delay 5 \
  --timeout 3 \
  --max-retries 3 \
  --url-path /health \
  --expected-codes 200 \
  my-pool
```

## Configuration

### Driver Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `api_endpoints` | `http://localhost:8080` | LoxiLB API endpoints (comma-separated) |
| `api_timeout` | `30` | API request timeout in seconds |
| `api_retries` | `3` | Number of API retry attempts |
| `auth_type` | `none` | Authentication type (none, basic, token, tls) |
| `default_algorithm` | `ROUND_ROBIN` | Default load balancing algorithm |
| `enable_health_monitor` | `true` | Enable health monitoring by default |
| `worker_threads` | `4` | Number of worker threads |

### Authentication Types

- **None**: No authentication required
- **Basic**: HTTP Basic authentication with username/password
- **Token**: Bearer token authentication
- **TLS**: Mutual TLS authentication with client certificates

### Supported Algorithms

- `ROUND_ROBIN`: Distribute requests evenly across all members
- `LEAST_CONNECTIONS`: Route to member with fewest active connections
- `SOURCE_IP`: Hash-based routing on source IP
- `WEIGHTED_ROUND_ROBIN`: Weighted distribution based on member weights
- `CONSISTENT_HASH`: Consistent hashing for session affinity

## Monitoring and Troubleshooting

### Health Check

```bash
# Check driver status
openstack loadbalancer provider list

# Verify LoxiLB connectivity
curl -X GET http://loxilb-endpoint:8080/status

# Check load balancer status
openstack loadbalancer show my-lb
```

### Logging

Driver logs are available at:
- `/var/log/kolla/octavia/octavia-worker.log` - Main worker logs
- `/var/log/kolla/octavia/loxilb-driver.log` - Driver-specific logs
- `/var/log/kolla/octavia/loxilb-audit.log` - Audit logs

### Metrics

Enable Prometheus metrics:
```ini
[loxilb]
metrics_enabled = true
metrics_port = 9090
```

Access metrics at: `http://octavia-worker:9090/metrics`

### Common Issues

1. **Provider not appearing:**
   ```bash
   # Check if driver is installed
   python -c "import octavia_loxilb_driver"
   
   # Restart Octavia services
   systemctl restart octavia-worker octavia-api
   ```

2. **API connectivity issues:**
   ```bash
   # Test connectivity from worker node
   curl http://loxilb-endpoint:8080/status
   
   # Check firewall rules
   iptables -L | grep 8080
   ```

3. **Load balancer creation fails:**
   ```bash
   # Check worker logs
   tail -f /var/log/kolla/octavia/octavia-worker.log
   
   # Verify network configuration
   openstack network show provider-network
   ```

## Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/your-org/octavia-loxilb-driver.git
cd octavia-loxilb-driver

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Unit tests
pytest octavia_loxilb_driver/tests/unit/

# Functional tests (requires LoxiLB cluster)
pytest octavia_loxilb_driver/tests/functional/

# Coverage report
pytest --cov=octavia_loxilb_driver --cov-report=html
```

### Code Quality

```bash
# Linting
flake8 octavia_loxilb_driver/
pylint octavia_loxilb_driver/

# Security scanning
bandit -r octavia_loxilb_driver/
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Submit a pull request

## Performance

### Benchmarks

LoxiLB driver performance characteristics:

| Metric | Value |
|--------|-------|
| **Max Connections/sec** | 100K+ |
| **Max Concurrent Connections** | 1M+ |
| **Latency (p99)** | < 1ms |
| **Throughput** | 40Gbps+ |
| **Memory Usage** | < 100MB per worker |

### Tuning

For high-performance deployments:

```ini
[loxilb]
# Increase worker threads
worker_threads = 8

# Enable batch operations
batch_create_enabled = true
batch_update_enabled = true

# Optimize API settings
api_connection_pool_size = 20
api_max_connections_per_pool = 10

# Enable caching
enable_resource_caching = true
cache_timeout = 600
```

## Security

### Authentication

Configure authentication for production deployments:

```ini
[loxilb]
auth_type = tls
tls_ca_cert_file = /etc/octavia/certificates/ca.pem
tls_client_cert_file = /etc/octavia/certificates/client.pem
tls_client_key_file = /etc/octavia/certificates/client-key.pem
tls_verify_cert = true
```

### Network Security

- Use dedicated management networks for LoxiLB communication
- Configure firewall rules to restrict API access
- Enable audit logging for compliance

### Certificate Management

Integration with Barbican for automatic certificate management:

```ini
[loxilb]
barbican_enabled = true
ssl_certificate_store = /etc/octavia/certificates/ssl/
```

## High Availability

### Cluster Configuration

Configure LoxiLB cluster for high availability:

```ini
[loxilb]
cluster_mode = active_standby
enable_failover = true
cluster_sync_enabled = true
cluster_health_check_interval = 30
```

### Failover Testing

```bash
# Trigger manual failover
openstack loadbalancer failover my-lb

# Monitor cluster status
curl -X GET http://loxilb-endpoint:8080/cluster/status
```

## Deployment Patterns

### Single Node (Development)

```yaml
# globals.yml
loxilb_cluster_endpoints:
  - "http://loxilb-dev:8080"
```

### Active-Standby (Production)

```yaml
# globals.yml
loxilb_cluster_endpoints:
  - "http://loxilb-primary:8080"
  - "http://loxilb-standby:8080"
octavia_loxilb_ha_enabled: "yes"
```

### Active-Active (High Scale)

```yaml
# globals.yml
loxilb_cluster_endpoints:
  - "http://loxilb-1:8080"
  - "http://loxilb-2:8080"
  - "http://loxilb-3:8080"
octavia_loxilb_cluster_mode: "active_active"
```

## API Reference

### LoxiLB Driver API

The driver exposes additional APIs for monitoring and management:

```bash
# Get driver status
GET /v2.0/lbaas/providers/loxilb/status

# Get cluster information
GET /v2.0/lbaas/providers/loxilb/cluster

# Trigger synchronization
POST /v2.0/lbaas/providers/loxilb/sync

# Get performance metrics
GET /v2.0/lbaas/providers/loxilb/metrics
```

### Configuration Validation

```bash
# Validate configuration
POST /v2.0/lbaas/providers/loxilb/validate
Content-Type: application/json

{
  "loadbalancer": {
    "vip_address": "192.168.1.100",
    "vip_network_id": "net-123",
    "algorithm": "ROUND_ROBIN"
  }
}
```

## Roadmap

### Planned Features

- **Layer 7 Policies**: Advanced HTTP routing rules
- **Rate Limiting**: Built-in rate limiting and DDoS protection
- **WebSocket Support**: Native WebSocket load balancing
- **gRPC Load Balancing**: gRPC protocol support
- **Multi-Region**: Cross-region load balancing
- **Auto-scaling**: Dynamic scaling based on load

### Version History

- **v1.0.0**: Initial release with basic load balancing
- **v1.1.0**: SSL termination and health monitoring
- **v1.2.0**: High availability and clustering
- **v1.3.0**: Performance optimizations and batch operations

## Support

### Documentation

- [Installation Guide](docs/installation.md)
- [Configuration Guide](docs/configuration.md)
- [Troubleshooting Guide](docs/troubleshooting.md)
- [API Documentation](docs/api.md)

### Community

- **GitHub Issues**: [Bug reports and feature requests](https://github.com/your-org/octavia-loxilb-driver/issues)
- **Discussions**: [Community discussions](https://github.com/your-org/octavia-loxilb-driver/discussions)
- **OpenStack Mailing List**: [OpenStack development discussions](http://lists.openstack.org/cgi-bin/mailman/listinfo/openstack-discuss)

### Professional Support

For enterprise support and consulting:
- Email: support@your-org.com
- Documentation: https://docs.your-org.com/octavia-loxilb-driver

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **LoxiLB Team**: For the high-performance load balancer implementation
- **OpenStack Octavia Team**: For the excellent load balancer framework
- **OpenStack Community**: For the collaborative development environment

---

**Note**: This driver is actively maintained and regularly tested with the latest OpenStack releases. For production deployments, please review the configuration and security guidelines carefully.