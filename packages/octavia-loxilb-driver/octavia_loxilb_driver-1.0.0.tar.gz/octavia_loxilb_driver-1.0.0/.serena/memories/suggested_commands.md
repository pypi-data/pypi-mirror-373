# Suggested Commands

## Development Environment Setup
```bash
# Activate development environment
./activate-dev.sh
make dev-setup                  # Complete development setup
make install-dev               # Install development dependencies
make setup-hooks               # Setup pre-commit hooks
```

## Testing Commands
```bash
# Run all tests (121 tests)
make test                      # or python -m pytest octavia_loxilb_driver/tests/ -v
make test-unit                 # Unit tests only
make test-integration          # Integration tests (requires LoxiLB)
make test-coverage            # Tests with coverage report
make ci-test                  # Run all CI-style tests locally
```

## Code Quality Commands
```bash
# Linting and formatting
make lint                     # Run flake8 and pylint
make format                   # Format with black and isort
make format-check            # Check formatting without changes
make security                # Run bandit security checks
make pre-commit              # Run all pre-commit hooks
```

## LoxiLB Environment Commands
```bash
# LoxiLB test environment
make start-loxilb            # Start LoxiLB containers
make stop-loxilb             # Stop LoxiLB containers
make restart-loxilb          # Restart LoxiLB containers
make status-loxilb           # Check LoxiLB status
make logs-loxilb             # View LoxiLB logs
```

## OpenStack Integration Commands
```bash
# macOS (MicroStack)
make setup-openstack         # Setup OpenStack with MicroStack
make install-octavia         # Install Octavia in MicroStack VM
make test-octavia-vm         # Test Octavia installation

# Linux (DevStack)
make setup-devstack          # Setup DevStack
make check-devstack          # Check DevStack status
make restart-devstack        # Restart DevStack services
```

## Development Workflow Commands
```bash
# Quick testing workflow
make quick-test              # Start LoxiLB + run simple E2E test
make full-test               # Full OpenStack + LoxiLB integration

# Daily development
make shell                   # Start development shell
make status                  # Show status of all components
make cleanup-all             # Clean everything (containers, VMs, artifacts)
```

## Commands for Task Completion
When completing any development task, run these commands:
```bash
make lint                    # Check code quality
make test-unit               # Run unit tests  
make test-coverage           # Generate coverage report
make security                # Security checks
```