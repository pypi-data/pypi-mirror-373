# Codebase Structure

## Main Package: `octavia_loxilb_driver/`

### Core Driver Components
- **`driver/`** - Octavia provider driver implementations
  - `provider_driver.py` - Main provider driver and operational metrics
  - `loadbalancer_driver.py` - Load balancer operations
  - `listener_driver.py` - Listener operations  
  - `pool_driver.py` - Pool operations
  - `member_driver.py` - Member operations
  - `healthmonitor_driver.py` - Health monitor operations
  - `utils/type_utils.py` - Type utilities

### API Client
- **`api/`** - LoxiLB API integration
  - `loxilb_client.py` - HTTP API client with retry logic and authentication

### Common Utilities
- **`common/`** - Shared components
  - `config.py` - Configuration management (Oslo config)
  - `constants.py` - Application constants and mappings
  - `exceptions.py` - Custom exception hierarchy
  - `utils.py` - General utilities and helper functions
  - `network_utils.py` - Network connectivity utilities
  - `state_reconciler.py` - State synchronization
  - `openstack_sdk_utils.py` - OpenStack SDK operations

### Controller/Worker System
- **`controller/`** - Asynchronous processing system
  - `controller_worker.py` - Main controller worker
  - `queue/` - Message queue handling
  - `worker/tasks/` - Individual task implementations
  - `worker/flows/` - Workflow orchestration

### Resource Mapping
- **`resource_mapping/`** - ID mapping between Octavia and LoxiLB
  - `mapper.py` - Resource ID translation

### Command Line Interface
- **`cmd/`** - CLI entry points
  - `loxilb_controller_worker.py` - Controller worker CLI
  - `loxilb_worker.py` - Worker CLI
  - `health_check.py` - Health check utility

### Testing
- **`tests/`** - Complete test suite (121 tests)
  - `unit/` - Unit tests with mocking
  - `functional/` - Integration tests with real LoxiLB
  - `unit/base.py` - Common test utilities

## Key Files in Root
- **`pyproject.toml`** - Modern Python packaging configuration
- **`Makefile`** - Development workflow automation
- **`.pre-commit-config.yaml`** - Git hooks configuration
- **`requirements*.txt`** - Dependency specifications
- **`setup.py`** - Legacy setup script (still needed for some tools)

## Documentation Structure
- **`docs/`** - Comprehensive documentation
- **`scripts/`** - Development and deployment scripts
- **`docker/`** - LoxiLB test environment setup