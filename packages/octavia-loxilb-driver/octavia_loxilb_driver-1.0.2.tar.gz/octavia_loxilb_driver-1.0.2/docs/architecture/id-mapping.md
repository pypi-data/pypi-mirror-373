# ID Mapping System

The ID mapping system is a critical component that maintains the relationship between Octavia resource IDs and LoxiLB service identifiers, enabling seamless operation and recovery capabilities.

## Overview

Octavia uses UUIDs for resource identification, while LoxiLB uses service keys based on network parameters (IP:port/protocol). The ID mapping system bridges this gap by:

1. **Bidirectional Mapping**: Maintaining both Octavia-to-LoxiLB and LoxiLB-to-Octavia lookups
2. **Persistent Storage**: Optional persistence for recovery across restarts
3. **Automatic Recovery**: Rebuilding lost mappings through deterministic ID generation
4. **State Consistency**: Ensuring mapping accuracy and consistency

## Architecture

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ID Mapping    │    │   Persistent    │    │   Recovery      │
│     Cache       │◄───┤    Storage      ├───►│   System        │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Structure

The mapping cache contains:

```python
{
    "octavia_to_loxilb": {
        "octavia-uuid": "loxilb-service-key"
    },
    "loxilb_to_octavia": {
        "loxilb-service-key": "octavia-uuid"
    },
    "resource_metadata": {
        "octavia-uuid": {
            "resource_type": "loadbalancer|listener|pool|member|healthmonitor",
            "external_ip": "192.168.1.100",
            "port": 80,
            "protocol": "tcp",
            "created_at": "2023-01-01T00:00:00Z",
            "additional_metadata": {}
        }
    },
    "version": "1.0"
}
```

## Key Functions

### Core Mapping Operations

#### Storage
```python
utils.store_id_mapping(cache, octavia_id, loxilb_key, resource_type, metadata)
```
- Stores bidirectional mapping between Octavia ID and LoxiLB key
- Includes resource metadata for recovery purposes
- Automatically saves to persistent storage if configured

#### Retrieval
```python
loxilb_key = utils.get_loxilb_key_from_octavia_id(cache, octavia_id)
octavia_id = utils.get_octavia_id_from_loxilb_key(cache, loxilb_key)
metadata = utils.get_id_mapping_metadata(cache, octavia_id)
```

#### Removal
```python
utils.remove_id_mapping(cache, octavia_id)
```
- Removes all traces of the mapping from cache
- Updates persistent storage if configured

### Service Key Generation

LoxiLB service keys follow the pattern: `{external_ip}:{port}/{protocol}`

```python
service_key = utils.get_loxilb_service_key(
    external_ip="192.168.1.100",
    port=80,
    protocol="tcp"
)
# Result: "192.168.1.100:80/tcp"
```

### Deterministic ID Generation

For recovery scenarios, deterministic IDs are generated based on service parameters:

```python
deterministic_id = utils.generate_deterministic_id(
    resource_type="loadbalancer",
    external_ip="192.168.1.100",
    port=80,
    protocol="tcp"
)
# Result: "lb_192.168.1.100_80_tcp_<hash>"
```

## Recovery Mechanisms

### Startup Recovery

When the driver starts, it can recover lost mappings through:

1. **Persistent Storage Recovery**: Load mappings from saved file
2. **LoxiLB Discovery**: Scan existing LoxiLB services and generate mappings
3. **Hybrid Recovery**: Combine both approaches for maximum coverage

```python
# Automatic recovery on driver startup
recovered_count = utils.recover_id_mappings_from_loxilb(
    cache, api_client, resource_mapper
)
```

### Runtime Recovery

During operation, if a mapping is missing:

1. **Operation-Triggered Recovery**: Automatically attempt recovery when mapping not found
2. **Deterministic Reconstruction**: Use service parameters to generate expected ID
3. **Service Discovery**: Query LoxiLB for matching services

### Recovery Flow

```
Missing Mapping Detected
         ↓
Check Persistent Storage
         ↓
Query LoxiLB Services
         ↓
Generate Deterministic ID
         ↓
Recreate Mapping
         ↓
Continue Operation
```

## Persistent Storage

### Configuration

```ini
[driver_loxilb]
enable_persistent_mapping = true
mapping_storage_path = /var/lib/octavia/loxilb-mappings.json
mapping_backup_interval = 300
```

### Storage Format

The persistent storage uses JSON format for human readability and debugging:

```json
{
    "octavia_to_loxilb": {
        "lb-12345": "192.168.1.100:80/tcp"
    },
    "loxilb_to_octavia": {
        "192.168.1.100:80/tcp": "lb-12345"
    },
    "resource_metadata": {
        "lb-12345": {
            "resource_type": "loadbalancer",
            "external_ip": "192.168.1.100",
            "port": 80,
            "protocol": "tcp",
            "created_at": "2023-01-01T00:00:00Z"
        }
    },
    "version": "1.0",
    "last_updated": "2023-01-01T12:00:00Z"
}
```

### Backup and Rotation

- Automatic backups at configurable intervals
- Rotation of old backup files
- Corruption detection and recovery

## Usage Examples

### Basic Operations

```python
# Create mapping when resource is created
utils.store_id_mapping(
    cache=mapper.id_mapping_cache,
    octavia_id="lb-12345",
    loxilb_key="192.168.1.100:80/tcp",
    resource_type="loadbalancer",
    metadata={
        "external_ip": "192.168.1.100",
        "port": 80,
        "protocol": "tcp"
    }
)

# Retrieve mapping for API calls
loxilb_key = utils.get_loxilb_key_from_octavia_id(
    cache, "lb-12345"
)
# Call LoxiLB API with loxilb_key

# Clean up mapping when resource is deleted
utils.remove_id_mapping(cache, "lb-12345")
```

### Recovery Operations

```python
# Initialize cache with persistent storage
cache = utils.create_id_mapping_cache(
    storage_path="/var/lib/octavia/loxilb-mappings.json"
)

# Perform startup recovery
recovered = utils.recover_id_mappings_from_loxilb(
    cache, api_client, resource_mapper
)
print(f"Recovered {recovered} mappings")

# Handle missing mapping during operation
def safe_get_loxilb_key(octavia_id):
    key = utils.get_loxilb_key_from_octavia_id(cache, octavia_id)
    if key is None:
        # Attempt recovery
        recovery_attempted = attempt_mapping_recovery(octavia_id)
        if recovery_attempted:
            key = utils.get_loxilb_key_from_octavia_id(cache, octavia_id)
    return key
```

## Performance Considerations

### Memory Usage
- In-memory cache for O(1) lookup performance
- Configurable cache size limits
- Lazy loading from persistent storage

### I/O Optimization
- Asynchronous writes to persistent storage
- Batch updates to reduce I/O operations
- Compression for large mapping sets

### Concurrency
- Thread-safe operations for concurrent access
- Read-write locks for cache access
- Atomic updates to prevent corruption

## Monitoring and Debugging

### Metrics
- Mapping cache hit/miss rates
- Recovery success/failure counts
- Persistent storage I/O metrics

### Logging
- All mapping operations logged at DEBUG level
- Recovery attempts and results logged at INFO level
- Mapping inconsistencies logged at WARNING level

### Debugging Tools
```bash
# View current mappings
python -m octavia_loxilb_driver.tools.show_mappings

# Validate mapping consistency
python -m octavia_loxilb_driver.tools.validate_mappings

# Force recovery
python -m octavia_loxilb_driver.tools.force_recovery
```

## Best Practices

### Mapping Management
1. Always store mappings immediately after successful resource creation
2. Remove mappings during resource deletion, even if LoxiLB operation fails
3. Use metadata to store enough information for complete recovery

### Error Handling
1. Continue operations even if mapping storage fails
2. Attempt recovery before reporting mapping-related errors
3. Log all mapping operations for troubleshooting

### Performance
1. Use persistent storage in production environments
2. Configure appropriate backup intervals
3. Monitor cache performance and adjust sizes as needed

### Security
1. Protect persistent storage files with appropriate permissions
2. Avoid logging sensitive information in mapping metadata
3. Regularly rotate backup files to prevent accumulation

## Migration and Upgrades

### Version Compatibility
- Mapping format versioning for backward compatibility
- Automatic migration between format versions
- Validation of loaded mappings

### Upgrade Procedures
1. Backup current mappings before upgrade
2. Test mapping recovery in staging environment
3. Validate mapping consistency after upgrade
4. Monitor for mapping-related issues post-upgrade
