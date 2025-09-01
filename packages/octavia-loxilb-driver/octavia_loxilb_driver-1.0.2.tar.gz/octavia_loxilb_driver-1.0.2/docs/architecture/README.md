# Architecture Overview

The LoxiLB Octavia Driver integrates OpenStack Octavia with LoxiLB for high-performance eBPF/XDP-based load balancing.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenStack Octavia                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │LoadBalancer │ │  Listener   │ │    Pool     │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              LoxiLB Octavia Driver                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Provider Driver (RPC Communication)                 │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Controller Worker (TaskFlow Orchestration)          │   │
│  │ • LoadBalancer Tasks  • Network Tasks               │   │
│  │ • Compute Tasks       • LoxiLB Tasks                │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Core Components                                     │   │
│  │ • LoxiLB API Client   • OpenStack SDK Utils        │   │
│  │ • Resource Mapper     • Network Configurator       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    LoxiLB Cluster                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │   LoxiLB    │ │   LoxiLB    │ │     eBPF/XDP        │   │
│  │  Instance   │ │  Instance   │ │   Load Balancer     │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🧩 Key Components

### Provider Driver (`provider_driver.py`)
Main entry point implementing the Octavia Provider Driver interface.
- RPC communication with controller worker
- Resource operation delegation
- Error handling and status reporting

### Controller Worker (`controller_worker.py`)
TaskFlow-based orchestration engine for resource operations.
- **LoadBalancer Operations**: VM creation, VIP allocation, network setup
- **Member Operations**: Interface attachment, network configuration
- **Resource Management**: OpenStack integration, LoxiLB configuration

### Core Components

#### LoxiLB API Client (`api_client.py`)
HTTP client for LoxiLB REST API communication.
- Load balancer CRUD operations
- Connection pooling and retry logic
- Error handling and timeout management

#### OpenStack SDK Utils (`openstack_sdk_utils.py`)
OpenStack service integration utilities.
- Nova (compute), Neutron (network), Keystone (auth)
- VM management, port operations, network configuration
- Allowed Address Pairs (AAP) for VIP handling

#### Resource Mapper (`resource_mapper.py`)
Maps between Octavia and LoxiLB resource models.
- Data transformation and validation
- Resource state synchronization
- Configuration translation

#### Network Configurator (`loxilb_network_config.py`)
Secure API-based network interface configuration.
- MAC address to interface mapping
- IP address configuration via LoxiLB API
- No SSH required - uses REST API only

## 🔄 Operation Flow

### LoadBalancer Creation
1. **Octavia Request** → Provider Driver receives create request
2. **RPC Communication** → Controller Worker starts TaskFlow
3. **VM Creation** → OpenStack Nova creates LoxiLB VM
4. **VIP Allocation** → Neutron allocates VIP port with AAP
5. **Network Setup** → Attach interfaces, configure IP addresses
6. **LoxiLB Config** → API calls to configure load balancer
7. **Status Update** → Report ACTIVE status to Octavia

### Member Addition
1. **Member Request** → Add backend server to pool
2. **Interface Attachment** → Attach VM to member subnet
3. **Network Configuration** → Configure interface via LoxiLB API
4. **LoxiLB Update** → Add member to load balancer configuration
5. **Health Check** → Verify member connectivity

## 🔧 Key Design Decisions

### Security-First Approach
- **API-Only Configuration**: No SSH keys required
- **REST API Integration**: Uses LoxiLB's native REST API
- **Secure Authentication**: Token-based API authentication

### OpenStack Integration
- **Allowed Address Pairs**: VIP handling following Amphora pattern
- **TaskFlow Orchestration**: Reliable operation sequencing
- **RPC Communication**: Asynchronous operation handling

### Network Architecture
- **VM-Based Deployment**: LoxiLB runs in OpenStack VMs
- **Multiple Topologies**: SINGLE, ACTIVE_STANDBY, ACTIVE_ACTIVE
- **Subnet Integration**: Automatic interface attachment to member subnets

## 📚 Additional Documentation

- **[Driver Design](driver-design.md)** - Detailed driver implementation patterns
- **[ID Mapping System](id-mapping.md)** - Resource identifier management
- **[Health Monitoring](health-monitoring.md)** - Health check coordination
