# Technology Stack

## Language and Runtime
- **Python**: 3.8+ (supports 3.8, 3.9, 3.10, 3.11)
- **Target OS**: Linux (Ubuntu 22.04 LTS recommended for production)
- **Development OS**: Linux/macOS/Windows

## Core Dependencies
- **OpenStack**: Zed or later
- **LoxiLB**: v0.8.0 or later
- **octavia-lib**: >=2.5.0 (OpenStack Octavia library)
- **oslo.config**: >=8.0.0 (Configuration management)
- **oslo.log**: >=4.4.0 (Logging framework)
- **oslo.utils**: >=4.8.0 (Utilities)
- **requests**: >=2.25.0 (HTTP client)
- **tenacity**: >=6.2.0 (Retry logic)

## Development Tools
- **Testing**: pytest, pytest-cov, pytest-mock, mock, testtools, fixtures
- **Code Quality**: flake8, pylint, bandit, black, isort
- **Git Hooks**: pre-commit
- **Documentation**: sphinx, openstackdocstheme
- **Development**: ipython, pdbpp

## Build System
- **Build Backend**: setuptools.build_meta
- **Entry Points**: Configured for Octavia API drivers and controller workers
- **Package Management**: PyPI-ready with setuptools_scm for versioning

## Integration Points
- **OpenStack Octavia**: Provider driver integration
- **LoxiLB API**: REST API client with authentication
- **OpenStack SDK**: Compute/networking operations
- **Docker**: Test environment orchestration