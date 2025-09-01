# Octavia LoxiLB Provider Driver

This package provides a provider driver for Octavia that enables integration with LoxiLB for load balancing services.

## Installation

### Development Installation

For development purposes, you can install the driver in development mode:

```bash
# Clone the repository
git clone https://github.com/loxilb-io/octavia-loxilb-driver.git
cd octavia-loxilb-driver

# Install in development mode
pip install -e .
```

### Production Installation

For production deployment, you can install the package using pip:

```bash
pip install octavia-loxilb-driver
```

Or build and install a wheel package:

```bash
# Build the wheel
python setup.py bdist_wheel

# Install the wheel
pip install dist/octavia_loxilb_driver-*.whl
```

## Integration with Octavia

### API Integration

The LoxiLB provider driver is automatically registered with Octavia's API service when the package is installed. To enable it, add the following to your `octavia.conf` file:

```ini
[api_settings]
enabled_provider_drivers = loxilb:LoxiLB Provider,amphora:Amphora Provider
```

### Worker Integration

The LoxiLB controller worker is automatically registered with Octavia's worker service when the package is installed. No additional configuration is needed beyond the general LoxiLB configuration.

### Configuration

Add the following section to your `octavia.conf` file:

```ini
[loxilb]
use_rpc = True
rpc_topic = loxilb_octavia
rpc_namespace = loxilb_controller
# Add other LoxiLB-specific configuration options here
```

## Deployment in Containerized Environments

### Kolla-Ansible Deployment

For Kolla-Ansible deployments, you can install the driver by:

1. Creating a custom Dockerfile that extends the base Octavia images
2. Using volume mounts to install the driver at runtime

#### Example Dockerfile for octavia-api:

```dockerfile
FROM kolla/ubuntu-binary-octavia-api:latest
COPY octavia_loxilb_driver /opt/octavia_loxilb_driver
RUN cd /opt/octavia_loxilb_driver && pip install -e .
```

#### Example Dockerfile for octavia-worker:

```dockerfile
FROM kolla/ubuntu-binary-octavia-worker:latest
COPY octavia_loxilb_driver /opt/octavia_loxilb_driver
RUN cd /opt/octavia_loxilb_driver && pip install -e .
```

### Runtime Installation

You can also install the driver at runtime by:

1. SSH into the octavia-api and octavia-worker containers
2. Install the driver package
3. Restart the services

```bash
# SSH into container
docker exec -it octavia_api /bin/bash

# Install driver
pip install octavia-loxilb-driver

# Restart service
systemctl restart octavia-api
```

Repeat the same steps for the octavia-worker container.

## License

Apache License 2.0
