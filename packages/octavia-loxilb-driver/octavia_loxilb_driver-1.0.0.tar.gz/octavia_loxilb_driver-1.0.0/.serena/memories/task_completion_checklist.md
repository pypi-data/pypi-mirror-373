# Task Completion Checklist

## Required Commands After Code Changes
1. **Code Quality Check**: `make lint`
   - Runs flake8 and pylint
   - Must pass before completion

2. **Security Check**: `make security` 
   - Runs bandit security analysis
   - Must pass before completion

3. **Unit Tests**: `make test-unit`
   - Runs all unit tests
   - All tests must pass

4. **Coverage Check**: `make test-coverage`
   - Generates coverage report
   - Aim to maintain 100% coverage

## Optional but Recommended
5. **Format Check**: `make format-check`
   - Verify code formatting
   - Run `make format` if needed

6. **Pre-commit Hooks**: `make pre-commit`
   - Run all pre-commit hooks
   - Catches common issues

7. **Integration Tests** (if LoxiLB available): `make test-integration`
   - Tests with actual LoxiLB instance
   - Validates end-to-end functionality

## Before Committing
- Ensure all required commands pass
- Review code changes for security implications
- Update documentation if needed
- Add/update tests for new functionality

## CI Pipeline Equivalent
Run `make ci-test` to execute the same checks as CI:
- Linting
- Security checks  
- Unit tests
- Coverage analysis

## Notes
- Never commit without passing lint and tests
- The project maintains 100% test coverage
- All security checks must pass
- Pre-commit hooks are strongly recommended