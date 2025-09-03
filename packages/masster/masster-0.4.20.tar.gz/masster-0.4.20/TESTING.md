# Testing Guide for MASSter

This document describes the testing strategy and procedures for the MASSter package deployment to PyPI.

## Test Structure

The test suite is organized into several categories:

### Unit Tests
- `test_imports.py` - Package import validation
- `test_version.py` - Version consistency checks  
- `test_spectrum.py` - Core Spectrum class functionality
- `test_parameters.py` - Parameter module validation

### Integration Tests
- `test_integration.py` - End-to-end workflow testing

## Running Tests

### Local Development

#### Using UV (Recommended)
```bash
# Install with development dependencies
uv sync --all-extras --dev

# Run all tests
uv run pytest tests/ -v

# Run tests with coverage
uv run pytest tests/ -v --cov=masster --cov-report=term-missing --cov-report=html

# Run specific test file
uv run pytest tests/test_spectrum.py -v

# Run with specific markers
uv run pytest tests/ -m "not slow" -v
```

#### Using Make (Convenient shortcuts)
```bash
# Run basic tests
make test

# Run tests with coverage
make test-cov

# Run all quality checks
make test-all

# Run CI-like checks locally
make ci-test
```

#### Using Tox (Multi-version testing)
```bash
# Install tox
pip install tox

# Run tests across all supported Python versions
tox

# Run specific environments
tox -e py311
tox -e lint
tox -e type
tox -e security
```

### Continuous Integration

The project uses GitHub Actions for automated testing:

#### Test Workflow (`.github/workflows/test.yml`)
- **Triggers**: Push to main/develop, Pull requests to main
- **Matrix**: Tests across Python 3.8-3.12 on Ubuntu, Windows, macOS
- **Checks**: Linting, type checking, unit tests, coverage
- **Artifacts**: Test coverage reports, build artifacts

#### Security Workflow (`.github/workflows/security.yml`)
- **Triggers**: Push to main, PRs, weekly schedule
- **Checks**: Safety (dependency vulnerabilities), Bandit (security issues)
- **Artifacts**: Security scan reports

#### Publish Workflow (`.github/workflows/publish.yml`)
- **Triggers**: Release creation, manual dispatch
- **Actions**: Build package, run tests, publish to PyPI/Test PyPI
- **Security**: Uses trusted publishing with OpenID Connect

## Test Categories

### Import Tests
Verify that all package components can be imported correctly:
- Main package imports
- Version accessibility  
- Class imports from submodules
- Parameter module imports

### Functionality Tests
Test core functionality:
- Spectrum creation and manipulation
- Data processing workflows
- Serialization/deserialization
- Parameter usage

### Integration Tests
End-to-end testing:
- Complete processing workflows
- Peak combination algorithms
- Data format conversions
- Parameter integration

## Coverage Requirements

- **Minimum Coverage**: 70% overall
- **Target Coverage**: 85% for core modules
- **Exclusions**: Version files, test files, example data

Coverage reports are generated in:
- Terminal output (term-missing)
- HTML format (htmlcov/index.html)
- XML format (coverage.xml) for CI integration

## Quality Checks

### Code Formatting
```bash
# Check formatting
make lint

# Auto-format code
make format
```

### Type Checking
```bash
# Run mypy type checking
make type-check
```

### Security Scanning
```bash
# Run security checks
make security
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks
uv run pre-commit install

# Run hooks on all files
make pre-commit
```

## PyPI Deployment Testing

### Test PyPI
Before releasing to PyPI, test the package on Test PyPI:

```bash
# Build package
make build

# Check package
make check-build

# Upload to Test PyPI
make publish-test

# Install from Test PyPI to verify
pip install --index-url https://test.pypi.org/simple/ masster
```

### Production PyPI
Production deployment is automated via GitHub Actions:

1. **Manual Testing**: Use `workflow_dispatch` with Test PyPI
2. **Release Deployment**: Create a GitHub release
3. **Verification**: Check package on PyPI

## Local Release Testing

Before creating a release:

```bash
# Complete release check
make release-check

# This runs:
# - Clean build artifacts
# - Run all tests and quality checks  
# - Build package
# - Verify build
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure package is installed in development mode
   ```bash
   uv sync --all-extras --dev
   ```

2. **Missing Dependencies**: Update lock file
   ```bash
   uv sync --upgrade
   ```

3. **Test Failures**: Check for missing test data or environment issues
   ```bash
   uv run pytest tests/ -v -s
   ```

4. **Coverage Issues**: Ensure all code paths are tested
   ```bash
   uv run pytest tests/ --cov=masster --cov-report=html
   # Open htmlcov/index.html to see detailed coverage
   ```

### Development Workflow

1. **Setup**: `make dev-setup`
2. **Development**: Make changes, tests run automatically via pre-commit
3. **Testing**: `make test-all` before committing
4. **Release**: `make release-check` before tagging

## Continuous Deployment

The package uses trusted publishing to PyPI:

1. **Configure PyPI**: Set up trusted publisher for the repository
2. **Release**: Create GitHub release with semantic version tag
3. **Automatic**: GitHub Actions builds and publishes to PyPI
4. **Verification**: Package appears on PyPI within minutes

## Monitoring

- **GitHub Actions**: Monitor workflow runs
- **Codecov**: Track coverage trends  
- **PyPI Stats**: Monitor download statistics
- **Security**: Weekly automated security scans
