# Contributing to Fast.BI Replication Control

Thank you for your interest in contributing to Fast.BI Replication Control! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** for your changes
4. **Make your changes** following our coding standards
5. **Test your changes** thoroughly
6. **Submit a pull request** with a clear description

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Apache Airflow 2.6.0 or higher
- Access to Airbyte instance for testing

### Local Development

```bash
# Clone the repository
git clone https://github.com/your-username/data-replication-control.git
cd data-replication-control

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Testing Environment

Set up a local Airflow instance with Airbyte connection:

```bash
# Set Airflow home
export AIRFLOW_HOME=~/airflow

# Initialize Airflow database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# Start Airflow webserver
airflow webserver --port 8080

# Start Airflow scheduler
airflow scheduler
```

## Code Style

We use several tools to maintain code quality:

### Black (Code Formatting)

```bash
# Format code
black fast_bi_replication_control/

# Check formatting
black --check fast_bi_replication_control/
```

### Flake8 (Linting)

```bash
# Run linting
flake8 fast_bi_replication_control/
```

### MyPy (Type Checking)

```bash
# Run type checking
mypy fast_bi_replication_control/
```

### Pre-commit Hooks

Install pre-commit hooks to automatically check code quality:

```bash
pre-commit install
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=fast_bi_replication_control --cov-report=html

# Run specific test file
python -m pytest tests/test_airbyte_operator.py
```

### Test Structure

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test interactions between components
- **Airflow Tests**: Test Airflow operator behavior
- **Mock Tests**: Test with mocked external dependencies

## Submitting Changes

### Pull Request Guidelines

1. **Clear Title**: Use descriptive titles that explain the change
2. **Detailed Description**: Explain what, why, and how
3. **Related Issues**: Link to any related issues
4. **Testing**: Describe how you tested your changes
5. **Breaking Changes**: Note any breaking changes clearly

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

### Example

```
feat(operator): add dry run mode to job monitor

- Add dry_run parameter to AirbyteJobMonitorOperator
- Default to True for safety
- Add comprehensive logging for dry run operations

Closes #123
```

## Release Process

### Version Bumping

1. **Update version** in `pyproject.toml`
2. **Update version** in `__init__.py`
3. **Update CHANGELOG.md** with new version
4. **Create git tag** with version number
5. **Push tag** to trigger GitHub Actions

### Release Checklist

- [ ] All tests passing
- [ ] Code quality checks passing
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version bumped
- [ ] Tag created and pushed
- [ ] GitHub Actions workflow successful
- [ ] PyPI package published
- [ ] GitHub release created manually

## Getting Help

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check our wiki and documentation
- **Email**: Contact support@fast.bi for urgent issues

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Fast.BI Replication Control! 🚀
