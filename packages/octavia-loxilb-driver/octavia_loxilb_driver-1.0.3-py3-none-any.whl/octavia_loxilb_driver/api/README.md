# LoxiLB API Client

This module provides a Python client for interacting with the LoxiLB API. The client is designed to be used by the Octavia LoxiLB provider driver to manage load balancers.

## Features

- Connection pooling and automatic retries with exponential backoff
- Multiple authentication methods (None, Basic, Token, TLS)
- Endpoint health checking and failover
- Comprehensive error handling and logging
- Strict alignment with LoxiLB API specification

## API Client Methods

The API client provides the following methods for interacting with LoxiLB:

### Load Balancer Management

- `create_loadbalancer(lb_data)`: Create a new load balancer
- `list_loadbalancers()`: List all load balancers
- `get_loadbalancer_by_service(ip_address, port, protocol)`: Get a load balancer by its service properties
- `get_loadbalancer_by_name(name)`: Get a load balancer by its name
- `delete_loadbalancer_rule(ip_address, port, protocol)`: Delete a load balancer by its service properties
- `delete_loadbalancer_by_name(name)`: Delete a load balancer by its name
- `delete_all_loadbalancers()`: Delete all load balancers

### Metrics and Statistics

- `get_metrics()`: Get general Prometheus-formatted metrics
- `get_lb_rule_count_metrics()`: Get load balancer rule count metrics
- `get_lb_processed_traffic_metrics()`: Get load balancer processed traffic metrics
- `get_endpoint_distribution_traffic_metrics()`: Get endpoint distribution traffic metrics per service
- `get_service_distribution_traffic_metrics()`: Get service distribution traffic metrics

### Status and Health

- `get_status()`: Get the LoxiLB status
- `health_check()`: Perform a health check on the LoxiLB API

## Configuration

The API client is configured using the following Oslo config options in the `loxilb` group:

```ini
[loxilb]
api_endpoints = http://localhost:11111
auth_type = none
username =
password =
api_token =
tls_verify_cert = True
tls_ca_cert_file =
tls_client_cert_file =
tls_client_key_file =
api_timeout = 30
api_retries = 3
api_retry_interval = 1.0
api_connection_pool_size = 10
api_max_connections_per_pool = 10
debug_api_calls = False
```

## Usage Example

```python
from oslo_config import cfg
from oslo_log import log as logging

from octavia_loxilb_driver.api.loxilb_client import LoxiLBAPIClient
from octavia_loxilb_driver.common import constants

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

# Configure the client
CONF.register_opts([
    cfg.ListOpt('api_endpoints', default=['http://localhost:8080']),
    cfg.StrOpt('auth_type', default='none'),
    # ... other options
], group='loxilb')

# Create the client
client = LoxiLBAPIClient()

# Create a load balancer
lb_data = {
    'serviceArguments': {
        'externalIP': '192.168.1.100',
        'port': 80,
        'protocol': 'tcp',
        'name': 'test-lb',
        'mode': constants.LB_MODE_DNAT,
        'monitor': True,
        'monitorArgs': {
            'port': 80,
            'interval': 5,
            'timeout': 3,
            'retries': 3,
            'type': 'tcp'
        }
    },
    'endpoints': [
        {
            'endpointIP': '10.0.0.10',
            'targetPort': 8080,
            'weight': 1
        },
        {
            'endpointIP': '10.0.0.11',
            'targetPort': 8080,
            'weight': 1
        }
    ],
    'lbAttrArguments': {
        'selectors': {
            'app': 'web'
        },
        'secureMode': constants.LB_SECURITY_PLAIN,
        'lbMode': constants.LB_MODE_DNAT,
        'method': constants.LB_ALGORITHM_ROUND_ROBIN
    }
}

try:
    result = client.create_loadbalancer(lb_data)
    LOG.info(f"Created load balancer: {result}")
except Exception as e:
    LOG.error(f"Failed to create load balancer: {e}")
```

## Testing

### Unit Tests

Run the unit tests with:

```bash
cd octavia-loxilb-driver
python -m unittest discover octavia_loxilb_driver/tests/unit/api
```

### Integration Tests

To run integration tests, first start the LoxiLB containers:

```bash
cd octavia-loxilb-driver/docker
docker-compose up -d
```

The Docker setup configures two LoxiLB instances with the following port mappings:
- LoxiLB API port 11111 inside containers
- First instance mapped to host port 8080
- Second instance mapped to host port 8081

Then run the integration tests:

```bash
cd octavia-loxilb-driver
python -m unittest discover octavia_loxilb_driver/tests/functional/api
```

Note: The integration tests are configured to connect to the LoxiLB API on port 11111.

## Notes

- The API client follows a strict alignment with the LoxiLB swagger.yml API specification
- LoxiLB treats load balancers as atomic units with no separate API endpoints for listeners, pools, members, or health monitors
- The driver must translate Octavia's granular resource model into LoxiLB's unified load balancer configuration
- Updates are implemented using a delete-then-create pattern to ensure atomic updates
