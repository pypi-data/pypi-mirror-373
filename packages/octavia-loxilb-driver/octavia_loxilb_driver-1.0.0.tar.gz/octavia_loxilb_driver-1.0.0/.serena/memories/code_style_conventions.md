# Code Style and Conventions

## Formatting
- **Black**: Line length 88 characters, Python 3.8+ target
- **isort**: Import sorting and organization
- **Line Endings**: End-of-file fixers enforced

## Code Quality
- **flake8**: Linting with max line length 88, ignores E203,W503
- **pylint**: Additional static analysis (errors only in make targets)
- **bandit**: Security linting for the main codebase (excludes tests)
- **mypy**: Type checking with strict settings:
  - `disallow_untyped_defs = true`
  - `disallow_incomplete_defs = true`
  - `check_untyped_defs = true`
  - `no_implicit_optional = true`
  - `warn_redundant_casts = true`

## OpenStack Conventions
- **Oslo Libraries**: Uses oslo.config, oslo.log, oslo.utils for standardization
- **Logging**: Structured logging with Oslo Log framework
- **Configuration**: Oslo Config with CONF global object pattern
- **Exception Handling**: Custom exception hierarchy with HTTP status mapping

## File Organization
- **Entry Points**: Defined in pyproject.toml for Octavia integration
- **Module Structure**: 
  - `driver/` - Core Octavia driver implementations
  - `api/` - LoxiLB API client
  - `common/` - Shared utilities, exceptions, constants
  - `controller/` - Worker and flow management
  - `resource_mapping/` - ID mapping between systems
  - `tests/` - Unit and functional tests

## Naming Conventions
- **Classes**: PascalCase (e.g., `LoxiLBProviderDriver`)
- **Functions/Variables**: snake_case (e.g., `create_load_balancer`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `PROVIDER_NAME`)
- **Modules**: lowercase with underscores (e.g., `loxilb_client.py`)