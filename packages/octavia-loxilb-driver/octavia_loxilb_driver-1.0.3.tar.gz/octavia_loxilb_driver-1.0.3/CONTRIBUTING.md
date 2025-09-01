# Contributing to LoxiLB Octavia Driver

Thank you for your interest in contributing to the LoxiLB Octavia Driver! This document provides guidelines for contributing to the project.

## Quick Start

For detailed information, see our documentation in the [docs/](docs/) directory.

## How to Contribute

### 1. Set Up Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver.git
cd octavia-loxilb-driver

# Set up development environment
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### 2. Create a Feature Branch

```bash
# Create a new branch for your feature
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

### 3. Make Your Changes

- Follow PEP 8 coding standards
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 4. Test Your Changes

```bash
# Run tests (if available)
python -m pytest octavia_loxilb_driver/tests/ -v

# Check code style
python -m flake8 octavia_loxilb_driver/
python -m black octavia_loxilb_driver/

# Test installation
pip install -e . && octavia-loxilb-setup --help
```

### 5. Submit a Pull Request

- Push your changes to your fork
- Create a pull request with a clear description
- Reference any related issues
- Ensure CI checks pass

## Development Guidelines

### Code Quality

- **Testing**: All new code must include tests
- **Documentation**: Update docs for new features
- **Code Style**: Follow PEP 8 and project conventions
- **Type Hints**: Use type hints for all new code
- **Error Handling**: Include appropriate error handling

### Commit Guidelines

```bash
# Use clear, descriptive commit messages
git commit -m "Add health monitor coordination feature"

# For bug fixes
git commit -m "Fix ID mapping race condition in member deletion"

# For documentation
git commit -m "Update installation guide for production deployment"
```

### Pull Request Guidelines

- **Clear Title**: Describe what the PR does
- **Description**: Explain the changes and why they're needed
- **Testing**: Describe how the changes were tested
- **Documentation**: Note any documentation updates
- **Breaking Changes**: Clearly mark any breaking changes

## Types of Contributions

### Bug Reports

When reporting bugs, please include:

- Clear description of the issue
- Steps to reproduce
- Expected vs. actual behavior
- Environment details (OS, Python version, etc.)
- Relevant log messages

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).

### Feature Requests

For new features, please:

- Describe the feature and its benefits
- Provide use cases and examples
- Consider implementation implications
- Discuss with maintainers before large changes

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md).

### Documentation Improvements

Documentation contributions are always welcome:

- Fix typos and grammar
- Improve clarity and examples
- Add missing documentation
- Update outdated information

### Code Contributions

Code contributions should:

- Solve a real problem or add valuable functionality
- Include comprehensive tests
- Follow existing code patterns
- Include documentation updates
- Pass all quality checks

## Development Resources

### Documentation Structure

```
docs/
├── INSTALLATION.md       # Comprehensive installation guide
├── QUICKSTART.md         # Quick start guide
├── TROUBLESHOOTING.md    # Common issues and solutions
├── RELEASE.md           # Release process documentation
├── LOXILB-VM-IMAGES.md  # VM image distribution guide
├── architecture/        # Architecture and design docs
└── api/                 # API documentation
```

### Key Files

- **[README.md](README.md)**: Project overview and quick start
- **[docs/INSTALLATION.md](docs/INSTALLATION.md)**: Complete installation guide
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)**: Get started in 10 minutes
- **[docs/architecture/README.md](docs/architecture/README.md)**: Architecture documentation
- **[docs/RELEASE.md](docs/RELEASE.md)**: Release process guide

### Testing

Testing is done through:

- **Installation Testing**: Verify the package installs correctly
- **Setup Script Testing**: Test automated resource creation
- **Integration Testing**: Test with actual OpenStack environment
- **Manual Testing**: Follow the QUICKSTART.md guide

### Code Organization

```
octavia_loxilb_driver/
├── api/                  # LoxiLB API client
├── common/               # Shared utilities
├── driver/               # Octavia driver implementations
├── resource_mapping/     # ID mapping system
└── tests/               # Test suite
```

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Acknowledge different perspectives and experiences

### Communication

- **GitHub Issues**: For bug reports and feature requests
- **Pull Requests**: For code contributions and reviews
- **Discussions**: For questions and general discussion

### Getting Help

- Review existing documentation first
- Search existing issues for similar problems
- Ask questions in GitHub discussions
- Provide clear, detailed information when asking for help

## Release Process

### Version Strategy

- **Major (x.0.0)**: Breaking changes, major features
- **Minor (0.x.0)**: New features, backwards compatible
- **Patch (0.0.x)**: Bug fixes, security updates

### Release Checklist

1. Update version numbers
2. Update CHANGELOG.md
3. Run full test suite
4. Build and test packages
5. Create release tag
6. Update documentation

## Recognition

Contributors are recognized in:

- GitHub contributor list
- Release notes for significant contributions
- Special recognition for major features or improvements

## Questions?

- **Documentation**: Check [docs/](docs/) directory
- **Installation**: See [INSTALLATION.md](docs/INSTALLATION.md)
- **Issues**: Browse or create [GitHub Issues](https://github.com/NLX-SeokHwanKong/octavia-loxilb-driver/issues)
- **Quick Start**: Follow [QUICKSTART.md](docs/QUICKSTART.md)

Thank you for contributing to the LoxiLB Octavia Driver!

## Coding Standards

- Follow PEP 8 style guidelines
- Use Black for code formatting
- Write comprehensive tests
- Document your code with docstrings
- Keep commits atomic and well-described

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Add or update tests as needed
4. Update documentation if required
5. Ensure all tests pass and code quality checks succeed
6. Submit a pull request with a clear description

## Code Review

All submissions require review. We use GitHub pull requests for this purpose.
Review criteria include:

- Code quality and style
- Test coverage
- Documentation updates
- Compatibility with existing features
- Performance impact

## Reporting Issues

- Use GitHub Issues for bug reports and feature requests
- Provide detailed reproduction steps for bugs
- Include system information and logs when relevant

## Questions?

Feel free to open a Discussion on GitHub for questions about development or usage.
