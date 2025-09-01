# Health Monitoring Coordination

The health monitoring system coordinates between Octavia's health monitoring requirements and LoxiLB's health checking capabilities, ensuring proper lifecycle management and resource cleanup.

## Overview

Health monitoring in the LoxiLB Octavia Driver involves:

1. **Cross-Driver Coordination**: Synchronization between member and health monitor drivers
2. **Endpoint Lifecycle Management**: Proper creation and cleanup of health check endpoints
3. **State Consistency**: Maintaining health status consistency between Octavia and LoxiLB
4. **Resource Cleanup**: Preventing orphaned health monitoring resources

## Architecture

### Component Interaction

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Health Monitor │    │     Member      │    │     LoxiLB      │
│     Driver      │◄───┤     Driver      ├───►│  Health Checks  │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Coordination Flow

```
Member Operation → Health Monitor Coordination → LoxiLB Update → Status Sync
```

## Health Monitor Driver

### Core Responsibilities

1. **Health Monitor Lifecycle**: Create, update, and delete health monitors
2. **Endpoint Probe Management**: Individual endpoint health checking
3. **Cross-Driver Coordination**: Respond to member driver events
4. **Status Reporting**: Maintain health status consistency

### Key Methods

#### Health Monitor Management
```python
def create(self, health_monitor):
    """Create a new health monitor with endpoint probes for all pool members."""
    
def update(self, old_health_monitor, new_health_monitor):
    """Update health monitor configuration and recreate endpoint probes."""
    
def delete(self, health_monitor):
    """Delete health monitor and all associated endpoint probes."""
```

#### Cross-Driver Coordination
```python
def remove_member_endpoint_probe(self, pool_id, member_address, member_port):
    """Remove health monitor endpoint probe for a specific member.
    
    Called by member driver when a member is deleted to ensure
    proper cleanup of associated health monitoring resources.
    """
```

#### Internal Helpers
```python
def _get_pool_health_monitors(self, pool_id):
    """Find all health monitors associated with a specific pool."""
    
def _create_endpoint_probe(self, health_monitor, member):
    """Create individual endpoint health probe in LoxiLB."""
    
def _remove_endpoint_probe(self, health_monitor_id, member_address, member_port):
    """Remove specific endpoint probe from LoxiLB."""
```

## Member Driver Coordination

### Enhanced Member Operations

The member driver includes health monitor coordination in its operations:

#### Member Deletion with Health Monitor Cleanup
```python
def delete(self, member):
    """Delete a pool member and clean up associated health monitoring."""
    # Standard member deletion
    result = self._delete_member(member)
    
    # Health monitor coordination
    self._cleanup_health_monitor_endpoints(
        member.get('pool_id'),
        member.get('address'),
        member.get('protocol_port')
    )
    
    return result
```

#### Health Monitor Endpoint Cleanup
```python
def _cleanup_health_monitor_endpoints(self, pool_id, member_address, member_port):
    """Clean up health monitor endpoints for a deleted member."""
    try:
        health_monitor_driver = self.resource_mapper.get_health_monitor_driver()
        health_monitor_driver.remove_member_endpoint_probe(
            pool_id, member_address, member_port
        )
    except Exception as e:
        self.logger.warning(f"Health monitor cleanup failed: {e}")
```

## Health Check Configuration

### LoxiLB Health Check Mapping

Octavia health monitor parameters are mapped to LoxiLB health check configuration:

| Octavia Parameter | LoxiLB Configuration | Description |
|-------------------|---------------------|-------------|
| `type` | `probetype` | Health check protocol (HTTP, TCP, etc.) |
| `delay` | `probeinterval` | Interval between health checks |
| `timeout` | `probetimeout` | Timeout for individual checks |
| `max_retries` | `proberetries` | Number of retries before marking unhealthy |
| `http_method` | `probereq` | HTTP method for HTTP health checks |
| `url_path` | `probereq` | URL path for HTTP health checks |
| `expected_codes` | `proberesp` | Expected response codes |

### Configuration Example

```python
# Octavia Health Monitor
octavia_health_monitor = {
    "id": "hm-12345",
    "type": "HTTP",
    "delay": 30,
    "timeout": 10,
    "max_retries": 3,
    "http_method": "GET",
    "url_path": "/health",
    "expected_codes": "200,202"
}

# LoxiLB Health Check Configuration
loxilb_health_check = {
    "probetype": "http",
    "probeinterval": 30,
    "probetimeout": 10,
    "proberetries": 3,
    "probereq": "GET /health",
    "proberesp": "200,202"
}
```

## Endpoint Probe Management

### Probe Creation

When a health monitor is created or a member is added to a monitored pool:

1. **Retrieve Pool Members**: Get all current members of the pool
2. **Create Individual Probes**: Create LoxiLB endpoint probe for each member
3. **Store Metadata**: Track created probes for cleanup purposes
4. **Update Status**: Initialize health status for new probes

### Probe Removal

When a member is deleted or health monitor is removed:

1. **Identify Affected Probes**: Find all probes associated with the member
2. **Remove from LoxiLB**: Delete endpoint probes using LoxiLB API
3. **Update Metadata**: Remove probe references from stored metadata
4. **Status Cleanup**: Clear health status for removed probes

### Probe Updates

When health monitor configuration changes:

1. **Current State Analysis**: Compare old and new configurations
2. **Incremental Updates**: Apply only necessary changes where possible
3. **Full Recreation**: Recreate all probes if major changes detected
4. **Status Preservation**: Maintain existing health status where appropriate

## State Synchronization

### Health Status Flow

```
LoxiLB Health Check → Driver Status Processing → Octavia Status Update
```

### Status Mapping

| LoxiLB Status | Octavia Status | Description |
|---------------|----------------|-------------|
| `active` | `ONLINE` | Member is healthy and receiving traffic |
| `inactive` | `OFFLINE` | Member failed health checks |
| `maintenance` | `DRAINING` | Member in maintenance mode |
| `error` | `ERROR` | Health check configuration error |

### Status Update Process

1. **Periodic Polling**: Regular status updates from LoxiLB
2. **Event-Driven Updates**: Immediate updates on status changes
3. **Batch Processing**: Efficient handling of multiple status updates
4. **Error Handling**: Graceful handling of status update failures

## Error Handling and Recovery

### Common Error Scenarios

#### Health Monitor Creation Failures
```python
def _handle_creation_failure(self, health_monitor, error):
    """Handle health monitor creation failures."""
    self.logger.error(f"Health monitor creation failed: {error}")
    # Cleanup partial state
    self._cleanup_partial_health_monitor(health_monitor['id'])
    # Report error to Octavia
    raise exceptions.HealthMonitorCreationFailed(str(error))
```

#### Endpoint Probe Failures
```python
def _handle_probe_failure(self, member_address, member_port, error):
    """Handle individual endpoint probe failures."""
    self.logger.warning(f"Endpoint probe failed for {member_address}:{member_port}: {error}")
    # Mark member as error state
    self._update_member_status(member_address, member_port, "ERROR")
    # Continue with other probes
```

#### Coordination Failures
```python
def _handle_coordination_failure(self, operation, error):
    """Handle cross-driver coordination failures."""
    self.logger.warning(f"Health monitor coordination failed during {operation}: {error}")
    # Log for troubleshooting but don't fail the primary operation
    # Schedule retry for coordination cleanup
    self._schedule_cleanup_retry(operation)
```

### Recovery Mechanisms

#### Orphaned Probe Detection
```python
def detect_orphaned_probes(self):
    """Detect and clean up orphaned health check probes."""
    # Get all probes from LoxiLB
    # Compare with expected probes from ID mapping
    # Clean up orphaned probes
    # Report inconsistencies
```

#### State Reconciliation
```python
def reconcile_health_status(self):
    """Reconcile health status between LoxiLB and Octavia."""
    # Get health status from LoxiLB
    # Compare with Octavia status
    # Update inconsistent status
    # Report reconciliation results
```

## Performance Optimization

### Batch Operations

```python
def batch_endpoint_operations(self, operations):
    """Perform multiple endpoint operations efficiently."""
    # Group operations by type
    # Execute in optimal order
    # Handle partial failures
    # Return operation results
```

### Caching Strategy

```python
class HealthStatusCache:
    """Cache health status to reduce API calls."""
    
    def get_cached_status(self, member_id):
        """Get cached health status if still valid."""
        
    def update_status_cache(self, member_id, status, timestamp):
        """Update cached health status."""
        
    def invalidate_cache(self, member_id=None):
        """Invalidate cached status."""
```

### Asynchronous Processing

```python
async def async_health_check_update(self, health_updates):
    """Process health status updates asynchronously."""
    # Process updates in parallel
    # Handle rate limiting
    # Ensure order when necessary
    # Report completion status
```

## Monitoring and Debugging

### Health Monitor Metrics

- Health check success/failure rates
- Probe creation/deletion counts
- Cross-driver coordination success rates
- Status synchronization delays

### Logging

```python
# Health monitor operations
self.logger.info(f"Created health monitor {hm_id} for pool {pool_id}")
self.logger.debug(f"Created endpoint probe for {member_address}:{member_port}")

# Coordination events
self.logger.info(f"Cleaning up health probes for deleted member {member_id}")
self.logger.warning(f"Health monitor coordination failed: {error}")

# Status updates
self.logger.debug(f"Updated health status for {member_id}: {old_status} → {new_status}")
```

### Debugging Tools

```bash
# Show health monitor status
python -m octavia_loxilb_driver.tools.health_status

# Validate health monitor consistency
python -m octavia_loxilb_driver.tools.validate_health_monitors

# Force health status reconciliation
python -m octavia_loxilb_driver.tools.reconcile_health_status
```

## Best Practices

### Health Monitor Design
1. Design health checks to be lightweight and fast
2. Use appropriate timeouts and retry counts
3. Monitor health check overhead on backend systems
4. Plan for graceful degradation during health check failures

### Cross-Driver Coordination
1. Make coordination operations idempotent
2. Log all coordination events for troubleshooting
3. Handle coordination failures gracefully
4. Implement retry mechanisms for transient failures

### Performance
1. Use batch operations when possible
2. Cache health status to reduce API calls
3. Process status updates asynchronously
4. Monitor and tune health check frequencies

### Error Handling
1. Distinguish between transient and permanent failures
2. Implement appropriate retry and backoff strategies
3. Provide clear error messages for troubleshooting
4. Fail fast for configuration errors, retry for transient issues

## Configuration Examples

### Basic Health Monitor Configuration
```ini
[health_monitoring]
default_delay = 30
default_timeout = 10
default_max_retries = 3
enable_coordination = true
status_update_interval = 60
```

### Advanced Health Monitor Configuration
```ini
[health_monitoring]
# Health check settings
default_delay = 30
default_timeout = 10
default_max_retries = 3
max_concurrent_checks = 50

# Coordination settings
enable_coordination = true
coordination_timeout = 30
coordination_retries = 3

# Status management
status_update_interval = 60
status_cache_ttl = 300
enable_status_reconciliation = true
reconciliation_interval = 3600

# Performance settings
batch_size = 10
async_processing = true
rate_limit_calls = 100
```
