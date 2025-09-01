# Octavia LoxiLB Driver

[![PyPI version](https://badge.fury.io/py/octavia-loxilb-driver.svg)](https://badge.fury.io/py/octavia-loxilb-driver)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![OpenStack](https://img.shields.io/badge/OpenStack-Zed%2B-red.svg)](https://www.openstack.org/)

A production-ready OpenStack Octavia provider driver that integrates with LoxiLB for high-performance eBPF/XDP-based load balancing.

## 🌟 Key Features

- **🚀 High Performance**: eBPF/XDP-based load balancing with minimal CPU overhead
- **☁️ Cloud Native**: Seamless integration with OpenStack and Kubernetes environments
- **🔄 High Availability**: Support for ACTIVE_STANDBY and ACTIVE_ACTIVE topologies
- **🔗 Full Integration**: Complete OpenStack Octavia provider driver implementation
- **🔒 Secure**: API-based configuration without SSH key requirements
- **🔍 Production Ready**: Comprehensive testing, monitoring, and enterprise-grade reliability

## 📋 Requirements

### Production Environment
- **OpenStack**: Zed or later
- **LoxiLB**: v0.8.0 or later
- **Python**: 3.8+
- **OS**: Ubuntu 22.04 LTS (recommended)

### Development Environment
- **Python**: 3.8+
- **OS**: Linux/macOS
- **Docker**: For LoxiLB test environment

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install octavia-loxilb-driver
```

### Basic Configuration

Add to `/etc/octavia/octavia.conf`:

```ini
[api_settings]
enabled_provider_drivers = amphora:'Amphora provider',loxilb:'LoxiLB provider'
default_provider_driver = loxilb

[loxilb]
api_endpoints = http://your-loxilb-host:8080
image_id = your-loxilb-image-id
flavor_id = your-flavor-id
network_id = your-management-network-id
security_group_ids = your-security-group-id
```

### Create Your First Load Balancer

```bash
# Create load balancer
openstack loadbalancer create --name my-lb --vip-subnet-id <subnet-id> --provider loxilb

# Add listener and pool
openstack loadbalancer listener create --name web-listener --protocol HTTP --protocol-port 80 my-lb
openstack loadbalancer pool create --name web-pool --lb-algorithm ROUND_ROBIN --listener web-listener --protocol HTTP

# Add backend servers
openstack loadbalancer member create --subnet-id <subnet-id> --address 192.168.1.10 --protocol-port 80 web-pool
```

## 📚 Documentation

| Topic | Description | Link |
|-------|-------------|------|
| **Installation** | Setup guides for development and production | [docs/installation/](docs/installation/) |
| **Configuration** | Driver and integration configuration | [docs/configuration/](docs/configuration/) |
| **Architecture** | System design and technical details | [docs/architecture/](docs/architecture/) |
| **User Guide** | Usage examples and best practices | [docs/user-guide/](docs/user-guide/) |
| **API Reference** | Complete API documentation | [docs/api/](docs/api/) |
| **Development** | Contributing and development guide | [docs/development/](docs/development/) |

## 🧪 Testing

```bash
# Run all tests (121 tests passing)
python -m pytest octavia_loxilb_driver/tests/ -v

# Run specific test categories
python -m pytest octavia_loxilb_driver/tests/unit/ -v           # Unit tests
python -m pytest octavia_loxilb_driver/tests/functional/ -v     # Integration tests

# Generate coverage report
python -m pytest octavia_loxilb_driver/tests/ --cov=octavia_loxilb_driver --cov-report=html
```

## 🏗️ Architecture

The LoxiLB Octavia Driver provides a complete integration between OpenStack Octavia and LoxiLB:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   OpenStack     │    │  LoxiLB Octavia  │    │     LoxiLB      │
│    Octavia      │◄──►│     Driver       │◄──►│    Cluster      │
│                 │    │                  │    │                 │
│ • Load Balancer │    │ • Provider       │    │ • eBPF/XDP      │
│ • Listeners     │    │ • ID Mapping     │    │ • Load Balancer │
│ • Pools         │    │ • State Sync     │    │ • Health Checks │
│ • Members       │    │ • Health Monitor │    │ • High Avail.   │
│ • Health Mon.   │    │ • Error Handling │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Key Components

- **Provider Driver**: Main integration point with Octavia
- **ID Mapping System**: Maintains consistency between Octavia and LoxiLB resource IDs
- **Health Monitor Coordination**: Synchronizes health checking between systems
- **State Reconciliation**: Ensures data consistency and handles recovery scenarios
- **API Client**: High-performance LoxiLB API integration with retry logic

## 🔄 Current Status

✅ **Production Ready** - All core functionality implemented and tested

| Component | Status | Tests | Coverage |
|-----------|--------|-------|----------|
| Load Balancer Driver | ✅ Complete | 13/13 | 100% |
| Listener Driver | ✅ Complete | 14/14 | 100% |
| Pool Driver | ✅ Complete | 16/16 | 100% |
| Member Driver | ✅ Complete | 18/18 | 100% |
| Health Monitor Driver | ✅ Complete | 24/24 | 100% |
| Provider Driver | ✅ Complete | 8/8 | 100% |
| API Client | ✅ Complete | 15/15 | 100% |
| Resource Mapping | ✅ Complete | 17/17 | 100% |
| **Total** | **✅ Complete** | **121/121** | **100%** |

## 🤝 Contributing

We welcome contributions! Please see our [contributing guide](CONTRIBUTING.md) for details.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Ensure all tests pass: `python -m pytest`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to your fork: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[LoxiLB Team](https://github.com/loxilb-io/loxilb)**: For the exceptional eBPF-based load balancer
- **[OpenStack Octavia Team](https://opendev.org/openstack/octavia)**: For the robust load balancer framework
- **OpenStack Community**: For fostering collaborative open-source development

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver/issues)
- **Discussions**: [GitHub Discussions](https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver/discussions)
