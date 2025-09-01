.PHONY: help install test lint format clean start-loxilb stop-loxilb setup-openstack test-e2e test-e2e-simple test-kolla-integration

# Variables
VENV_PYTHON := ./venv/bin/python
ARCH := $(shell uname -m)

help:  ## Show this help
	@echo "🚀 LoxiLB Octavia Driver Development ($(ARCH))"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $1, $2}'

install:  ## Install package in development mode
	$(VENV_PYTHON) -m pip install -e .

install-dev:  ## Install development dependencies
	$(VENV_PYTHON) -m pip install -r requirements-dev.txt

test:  ## Run all tests
	$(VENV_PYTHON) -m pytest octavia_loxilb_driver/tests/ -v

test-unit:  ## Run unit tests only
	$(VENV_PYTHON) -m pytest octavia_loxilb_driver/tests/unit/ -v

test-integration:  ## Run integration tests (requires LoxiLB)
	$(VENV_PYTHON) -m pytest octavia_loxilb_driver/tests/functional/ -v

test-coverage:  ## Run tests with coverage report
	$(VENV_PYTHON) -m pytest --cov=octavia_loxilb_driver --cov-report=html --cov-report=term

lint:  ## Run linting
	$(VENV_PYTHON) -m flake8 octavia_loxilb_driver/
	$(VENV_PYTHON) -m pylint octavia_loxilb_driver/ --errors-only

format:  ## Format code
	$(VENV_PYTHON) -m black octavia_loxilb_driver/
	$(VENV_PYTHON) -m isort octavia_loxilb_driver/

format-check:  ## Check code formatting
	$(VENV_PYTHON) -m black --check octavia_loxilb_driver/
	$(VENV_PYTHON) -m isort --check-only octavia_loxilb_driver/

security:  ## Run security checks
	$(VENV_PYTHON) -m bandit -r octavia_loxilb_driver/

clean:  ## Clean up build artifacts
	rm -rf build/ dist/ *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	find . -name ".pytest_cache" -delete

start-loxilb:  ## Start LoxiLB test environment
	cd docker && docker-compose up -d
	@echo "Waiting for LoxiLB to start..."
	@sleep 15
	@$(VENV_PYTHON) scripts/test-loxilb-connection.py

stop-loxilb:  ## Stop LoxiLB test environment
	cd docker && docker-compose down

restart-loxilb:  ## Restart LoxiLB test environment
	cd docker && docker-compose restart

logs-loxilb:  ## Show LoxiLB logs
	cd docker && docker-compose logs -f

status-loxilb:  ## Show LoxiLB status
	cd docker && docker-compose ps
	@echo ""
	@echo "🔍 LoxiLB API Status:"
	@curl -s http://localhost:8080/netlox/v1/version 2>/dev/null | jq . || echo "LoxiLB not responding"

# OpenStack Integration Commands
setup-openstack:  ## Setup OpenStack with MicroStack (macOS only)
	@if [[ "$$OSTYPE" == "darwin"* ]]; then \
		chmod +x scripts/setup-microstack-macos.sh; \
		./scripts/setup-microstack-macos.sh; \
	else \
		echo "❌ This command is for macOS only. Use setup-devstack for other platforms."; \
	fi

install-octavia: ## Install Octavia in existing MicroStack VM
	@echo "🔧 Installing Octavia in MicroStack VM..."
	@if ! multipass list | grep -q "openstack-loxilb.*Running"; then \
		echo "❌ OpenStack VM not running. Run 'make setup-openstack' first."; \
		exit 1; \
	fi
	@echo "� Creating clean driver package..."
	@rm -rf /tmp/octavia-loxilb-driver-clean
	@mkdir -p /tmp/octavia-loxilb-driver-clean
	@rsync -av --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.pytest_cache' --exclude='venv' --exclude='MagicMock' --exclude='build' --exclude='dist' --exclude='*.egg-info' . /tmp/octavia-loxilb-driver-clean/
	@echo "�📦 Transferring driver code to VM..."
	multipass transfer --recursive /tmp/octavia-loxilb-driver-clean openstack-loxilb:/home/ubuntu/octavia-loxilb-driver || echo "Transfer failed, continuing without driver"
	@echo "🔧 Running Octavia installation script..."
	chmod +x scripts/install-octavia-manual.sh
	multipass transfer scripts/install-octavia-manual.sh openstack-loxilb:/home/ubuntu/
	multipass exec openstack-loxilb -- chmod +x /home/ubuntu/install-octavia-manual.sh
	multipass exec openstack-loxilb -- /home/ubuntu/install-octavia-manual.sh
	@echo "🧹 Cleaning up temporary files..."
	@rm -rf /tmp/octavia-loxilb-driver-clean

debug-vm-mysql: ## Debug MySQL issues in VM
	@echo "🔍 Debugging MySQL in OpenStack VM..."
	@if ! multipass list | grep -q "openstack-loxilb.*Running"; then \
		echo "❌ OpenStack VM not running. Run 'make setup-openstack' first."; \
		exit 1; \
	fi
	@echo "MySQL Service Status:"
	multipass exec openstack-loxilb -- sudo systemctl status mysql || echo "MySQL not found"
	multipass exec openstack-loxilb -- sudo systemctl status mariadb || echo "MariaDB not found"
	@echo "MicroStack MySQL Status:"
	multipass exec openstack-loxilb -- snap services microstack.mysql || echo "MicroStack MySQL not found"
	@echo "MySQL Socket Files:"
	multipass exec openstack-loxilb -- find /var -name "*mysql*.sock" 2>/dev/null || echo "No MySQL sockets found"
	@echo "MySQL Processes:"
	multipass exec openstack-loxilb -- ps aux | grep mysql || echo "No MySQL processes"

install-driver-vm: ## Install LoxiLB driver in existing Octavia VM
	@echo "📦 Installing LoxiLB driver in Octavia VM..."
	@if ! multipass list | grep -q "openstack-loxilb.*Running"; then \
		echo "❌ OpenStack VM not running. Run 'make setup-openstack' first."; \
		exit 1; \
	fi
	@echo "📁 Creating clean driver package..."
	@rm -rf /tmp/octavia-loxilb-driver-clean
	@mkdir -p /tmp/octavia-loxilb-driver-clean
	@rsync -av --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.pytest_cache' --exclude='venv' --exclude='MagicMock' --exclude='build' --exclude='dist' --exclude='*.egg-info' . /tmp/octavia-loxilb-driver-clean/
	@echo "📁 Transferring clean driver code..."
	multipass transfer --recursive /tmp/octavia-loxilb-driver-clean openstack-loxilb:/home/ubuntu/octavia-loxilb-driver
	@echo "🔧 Installing driver..."
	multipass exec openstack-loxilb -- bash -c "cd /home/ubuntu/octavia-loxilb-driver && sudo python3 setup.py develop"
	@echo "🔄 Restarting Octavia services..."
	multipass exec openstack-loxilb -- sudo systemctl restart octavia-api octavia-worker
	@echo "🧹 Cleaning up temporary files..."
	@rm -rf /tmp/octavia-loxilb-driver-clean
	@echo "✅ Driver installation complete!"

test-octavia-vm: ## Test Octavia installation in VM
	@echo "🧪 Testing Octavia installation..."
	@if ! multipass list | grep -q "openstack-loxilb.*Running"; then \
		echo "❌ OpenStack VM not running. Run 'make setup-openstack' first."; \
		exit 1; \
	fi
	@echo "1. Checking Octavia services:"
	multipass exec openstack-loxilb -- sudo systemctl is-active octavia-api || echo "❌ Octavia API not running"
	multipass exec openstack-loxilb -- sudo systemctl is-active octavia-worker || echo "❌ Octavia Worker not running"
	@echo "2. Testing Octavia API:"
	multipass exec openstack-loxilb -- curl -s http://192.168.64.9:9876/ | head -3 || echo "❌ Octavia API not accessible"
	@echo "3. Listing load balancer providers:"
	multipass exec openstack-loxilb -- /snap/bin/microstack.openstack loadbalancer provider list || echo "❌ Provider list failed"

setup-devstack:  ## Setup DevStack for OpenStack (Linux/WSL)
	chmod +x scripts/setup-devstack.sh
	./scripts/setup-devstack.sh

test-devstack:  ## Test DevStack installation
	@echo "🧪 Testing DevStack installation..."
	@if [ -f /opt/stack/test-loxilb-integration.sh ]; then \
		echo "Running DevStack integration test..."; \
		sudo /opt/stack/test-loxilb-integration.sh; \
	else \
		echo "❌ DevStack not found. Run 'make setup-devstack' first."; \
		exit 1; \
	fi

test-devstack-fixes:  ## Test DevStack setup fixes (IP detection, OVN conflicts)
	@echo "🧪 Testing DevStack fixes..."
	@chmod +x scripts/test-devstack-fixes.sh
	@scripts/test-devstack-fixes.sh

restart-devstack:  ## Restart DevStack services
	@echo "🔄 Restarting DevStack..."
	@if [ -d "$$HOME/devstack" ]; then \
		cd "$$HOME/devstack" && ./unstack.sh && ./stack.sh; \
	else \
		echo "❌ DevStack not found. Run 'make setup-devstack' first."; \
		exit 1; \
	fi

stop-devstack:  ## Stop DevStack services
	@echo "🛑 Stopping DevStack..."
	@if [ -d "$$HOME/devstack" ]; then \
		cd "$$HOME/devstack" && ./unstack.sh; \
	else \
		echo "❌ DevStack not found."; \
		exit 1; \
	fi

check-devstack:  ## Check DevStack status
	@echo "🔍 Checking DevStack status..."
	@if command -v openstack >/dev/null 2>&1 && [ -f /opt/stack/devstack/openrc ]; then \
		echo "✅ DevStack appears to be installed"; \
		echo "Services status:"; \
		sudo systemctl --no-pager status devstack@* | grep -E "(devstack@|Active:|Main PID)" || echo "Some services may not be running"; \
		echo ""; \
		echo "OpenStack services:"; \
		source /opt/stack/devstack/openrc admin admin && openstack service list; \
	else \
		echo "❌ DevStack not found or not properly configured."; \
	fi

logs-devstack:  ## Show DevStack logs
	@echo "📋 DevStack logs..."
	@if [ -f /opt/stack/logs/stack.sh.log ]; then \
		tail -50 /opt/stack/logs/stack.sh.log; \
	else \
		echo "❌ DevStack logs not found."; \
	fi

docs:  ## Build documentation
	cd docs && make html

serve-docs:  ## Serve documentation locally
	cd docs/build/html && python -m http.server 8000

pre-commit:  ## Run pre-commit hooks
	pre-commit run --all-files

setup-hooks:  ## Setup pre-commit hooks
	pre-commit install

check-arch:  ## Check system architecture
	@echo "🔍 Architecture Information:"
	@echo "   System: $(shell uname -m)"
	@echo "   Python: $(shell $(VENV_PYTHON) -c 'import platform; print(platform.machine())' 2>/dev/null || echo 'venv not active')"
	@echo "   Docker: $(shell docker --version 2>/dev/null || echo 'not available')"

shell:  ## Start development shell
	@echo "🚀 Starting development shell..."
	@bash --init-file <(echo "source venv/bin/activate; echo '🚀 Development environment activated'")

# Quick commands for common workflows
quick-test:  ## Quick test: start LoxiLB + run simple E2E test
	make start-loxilb
	make test-e2e-simple

full-test:  ## Full test: OpenStack + LoxiLB integration
	@echo "🚀 Full integration test workflow"
	@echo "1. Make sure OpenStack is set up..."
	@make setup-openstack || (echo "OpenStack setup failed"; exit 1)
	@echo "2. Starting LoxiLB..."
	@make start-loxilb
	@echo "3. Running full E2E test..."
	@make test-e2e-full

status:  ## Show status of all components
	@echo "🔍 Component Status Check"
	@echo "1. Docker:"
	@docker --version 2>/dev/null || echo "❌ Docker not available"
	@echo "2. LoxiLB Containers:"
	@docker ps --filter "name=loxilb" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "❌ No LoxiLB containers"
	@echo "3. LoxiLB API:"
	@curl -s http://localhost:8080/netlox/v1/version 2>/dev/null | jq -r '.version // "API Error"' || echo "❌ LoxiLB API not responding"
	@echo "4. OpenStack VM (if using MicroStack):"
	@if command -v multipass >/dev/null 2>&1; then \
		multipass list 2>/dev/null | grep -E "openstack|State" || echo "❌ No OpenStack VM found"; \
	else \
		echo "ℹ️  Multipass not installed"; \
	fi
	@echo "5. Python Environment:"
	@$(VENV_PYTHON) --version 2>/dev/null || echo "❌ Virtual environment not active"

cleanup-all:  ## Clean up everything (containers, VMs, build artifacts)
	@echo "🧹 Cleaning up all resources..."
	make stop-loxilb
	make clean
	@if command -v multipass >/dev/null 2>&1; then \
		if multipass list | grep -q "openstack-loxilb"; then \
			echo "🗑️  Deleting OpenStack VM..."; \
			multipass delete openstack-loxilb; \
			multipass purge; \
		fi; \
	fi
	@echo "✅ Cleanup complete"

# Development workflow shortcuts
dev-setup:  ## Complete development setup
	@echo "🛠️  Setting up development environment..."
	make install-dev
	make setup-hooks
	make check-arch
	@echo "✅ Development environment ready!"

ci-test:  ## Run CI-style tests locally
	@echo "🔄 Running CI tests locally..."
	make lint
	make security
	make test-unit
	make test-coverage
	@echo "✅ All CI tests passed!"

ci-test-e2e:  ## Run end-to-end tests with OpenStack
	@echo "🧪 Running End-to-End Tests with OpenStack"
	@./scripts/test-e2e.sh

test-e2e-simple:  ## Run simple end-to-end tests with mock Octavia API
	@echo "🧪 Running Simple End-to-End Tests"
	@./scripts/test-e2e-simple.sh

test-kolla-integration:  ## Run integration tests with kolla-ansible OpenStack
	@echo "🧪 Running Integration Tests with kolla-ansible OpenStack"
	@chmod +x ./scripts/test-kolla-integration.sh
	@./scripts/test-kolla-integration.sh

validate-network:  ## Validate network configuration for DevStack
	@echo "🔍 Validating network configuration..."
	@chmod +x scripts/validate-network-config.sh
	@scripts/validate-network-config.sh

validate-ovn:  ## Validate OVN networking configuration for DevStack
	@echo "🔍 Validating OVN configuration..."
	@chmod +x scripts/validate-ovn-config.sh
	@scripts/validate-ovn-config.sh

# Platform-specific help
help-macos:  ## Show macOS-specific setup instructions
	@echo "🍎 macOS Setup Instructions:"
	@echo ""
	@echo "1. Initial setup:"
	@echo "   ./activate-dev.sh"
	@echo "   make dev-setup"
	@echo ""
	@echo "2. Quick test (mock OpenStack):"
	@echo "   make quick-test"
	@echo ""
	@echo "3. Full OpenStack integration:"
	@echo "   make setup-openstack   # Sets up MicroStack VM"
	@echo "   make full-test         # Complete integration test"
	@echo ""
	@echo "4. Daily development:"
	@echo "   make start-loxilb      # Start LoxiLB containers"
	@echo "   make test-unit         # Run unit tests"
	@echo "   make lint              # Check code quality"
	@echo ""
	@echo "5. Cleanup:"
	@echo "   make cleanup-all       # Remove everything"

help-examples:  ## Show example usage scenarios
	@echo "📋 Example Usage Scenarios:"
	@echo ""
	@echo "🔬 Scenario 1: Quick Driver Testing"
	@echo "   make start-loxilb"
	@echo "   make test-e2e-simple"
	@echo ""
	@echo "🏗️  Scenario 2: Full Integration Development"
	@echo "   make setup-openstack   # or setup-devstack on Linux"
	@echo "   make start-loxilb"
	@echo "   make test-e2e-full"
	@echo ""
	@echo "🧪 Scenario 3: Unit Testing & Development"
	@echo "   make test-unit"
	@echo "   make lint"
	@echo "   make format"
	@echo ""
	@echo "🚀 Scenario 4: Continuous Integration"
	@echo "   make ci-test"
	@echo ""
	@echo "🧹 Scenario 5: Clean Environment"
	@echo "   make cleanup-all"
	@echo "   make dev-setup"
