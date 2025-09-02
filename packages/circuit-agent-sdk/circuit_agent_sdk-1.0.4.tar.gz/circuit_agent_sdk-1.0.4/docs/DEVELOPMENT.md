# Development Guide
>Note: Need to fix the release logic. its really buggy and causes the github commit messages to be out of sync with the tags
This guide provides comprehensive information for developing and contributing to the Circuit Agent Python SDK.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Code Quality](#code-quality)
- [Testing](#testing)
- [Building and Releasing](#building-and-releasing)
- [Contributing](#contributing)

## Getting Started

### Prerequisites

- Python 3.12 or higher
- uv (Python package manager)
- Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/circuitorg/agent-sdk-python.git
   cd agent-sdk-python
   ```

2. **Set up the development environment**:
   ```bash
   # Run the automated setup script
   ./scripts/dev_setup.sh

   # Or manually:
   uv sync --dev
   uv run pre-commit install
   ```

3. **Verify the setup**:
   ```bash
   make test
   ```

## Development Environment

### Project Structure

```
agent-sdk-python/
├── src/
│   └── agent_sdk/          # Main package
│       ├── __init__.py            # Package exports
│       ├── agent.py               # Main Agent class
│       ├── models.py              # Pydantic models
│       ├── toolset.py             # AgentToolset class
│       └── utils.py               # Utility functions
├── tests/                         # Test suite
│   ├── test_agent.py             # Agent tests
│   ├── test_toolset.py           # Toolset tests
│   └── test_models.py            # Model tests
├── examples/                      # Example implementations
│   ├── basic_agent.py            # Basic agent example
│   └── advanced_agent.py         # Advanced agent example
├── docs/                         # Documentation
│   ├── API.md                    # API reference
│   └── DEVELOPMENT.md            # This file
├── scripts/                      # Development scripts
│   └── dev_setup.sh             # Setup script
├── .github/                      # GitHub configuration
│   └── workflows/                # CI/CD workflows
├── pyproject.toml               # Package configuration
├── README.md                    # Main documentation
├── Makefile                     # Development commands
└── .pre-commit-config.yaml      # Pre-commit hooks
```

### Available Commands

The project includes a comprehensive Makefile for common development tasks:

```bash
# Get help
make help

# Install dependencies
make install

# Run tests
make test

# Run linting
make lint

# Format code
make format

# Type checking
make type-check

# Build package
make build

# Clean build artifacts
make clean

# Set up development environment
make dev-setup

# Run examples
make examples

# Run all quality checks
make all

# Quick development workflow
make dev

# Quick check (fast)
make quick

# Full check (comprehensive)
make full
```

### Using uv

The project uses uv for dependency management and development:

```bash
# Install dependencies
uv sync --dev

# Run commands
uv run pytest
uv run black .
uv run ruff check .
uv run mypy src/

# Build package
uv build

# Install in development mode
uv pip install -e .
```

## Code Quality

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

```bash
# Install hooks
uv run pre-commit install

# Run all hooks
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run black
```

### Code Formatting

The project uses Black for code formatting and Ruff for linting:

```bash
# Format code
uv run black .

# Lint code
uv run ruff check .

# Format with ruff
uv run ruff format .
```

### Type Checking

The project uses mypy for type checking:

```bash
# Run type checking
uv run mypy src/

# Run with strict mode
uv run mypy src/ --strict
```

### Linting Rules

The project uses Ruff with the following configuration:

- **Line length**: 88 characters (Black compatible)
- **Target Python version**: 3.12
- **Rules**: E, W, F, I, B, C4, UP (see pyproject.toml for details)

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/agent_sdk --cov-report=html

# Run specific test file
uv run pytest tests/test_agent.py

# Run with verbose output
uv run pytest -v

# Run specific test
uv run pytest tests/test_agent.py::TestAgent::test_agent_initialization
```

### Test Structure

Tests are organized by module:

- `tests/test_agent.py` - Agent class tests
- `tests/test_toolset.py` - AgentToolset class tests
- `tests/test_models.py` - Pydantic model tests

### Test Guidelines

1. **Use descriptive test names**: Test names should clearly describe what is being tested
2. **Use fixtures**: Reuse common test data with pytest fixtures
3. **Test both success and failure cases**: Ensure error handling is tested
4. **Use async/await properly**: All async functions should be tested with `@pytest.mark.asyncio`
5. **Mock external dependencies**: Use `unittest.mock` to mock external services

### Example Test

```python
import pytest
from unittest.mock import Mock, patch
from agent_sdk import Agent, AgentRequest, AgentResponse

class TestAgent:
    @pytest.fixture
    def mock_execution_function(self):
        async def mock_func(request: AgentRequest) -> AgentResponse:
            return AgentResponse(success=True)
        return mock_func

    def test_agent_initialization(self, mock_execution_function):
        """Test basic agent initialization"""
        agent = Agent(executionFunction=mock_execution_function)
        assert agent.execution_function == mock_execution_function

    @pytest.mark.asyncio
    async def test_process_request_success(self, mock_execution_function):
        """Test successful request processing"""
        agent = Agent(executionFunction=mock_execution_function)
        result = await agent.process_request(
            session_id=123,
            session_wallet_address="0x1234567890abcdef"
        )
        assert result["success"] is True
```

## Building and Releasing

### Building the Package

```bash
# Build the package
uv build

# Build and install in development mode
uv pip install -e .
```

### Creating a Release

1. **Update version** in `pyproject.toml`
2. **Commit changes**:
   ```bash
   git add .
   git commit -m "Release v1.0.0"
   ```
3. **Create and push tag**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
4. **GitHub Actions will automatically**:
   - Run tests on multiple Python versions
   - Run linting and type checking
   - Build the package
   - Create a GitHub release
   - Attach the built wheel and source distribution

### Manual Release Process

```bash
# Clean previous builds
make clean

# Run all checks
make full

# Build package
make build

# Create release
make release
```

## Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes** and ensure all tests pass:
   ```bash
   make all
   ```
4. **Commit your changes**:
   ```bash
   git commit -m 'Add amazing feature'
   ```
5. **Push to the branch**:
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Open a Pull Request**

### Code Review Guidelines

1. **All code must pass quality checks**:
   - Linting (ruff)
   - Formatting (black)
   - Type checking (mypy)
   - Tests (pytest)

2. **Follow the existing code style**:
   - Use Black formatting
   - Follow PEP 8 guidelines
   - Use type hints
   - Write comprehensive docstrings

3. **Test coverage**:
   - New code should have test coverage
   - Tests should be meaningful and comprehensive

### Documentation Guidelines

1. **Update documentation** for any API changes
2. **Add docstrings** to all public functions and classes
3. **Update examples** if needed
4. **Update README.md** for significant changes

### Commit Message Guidelines

Use conventional commit messages:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for formatting changes
- `refactor:` for code refactoring
- `test:` for test changes
- `chore:` for maintenance tasks

Example:
```
feat: add transaction signing capability to AgentToolset

- Add TransactionRequest and TransactionResult models
- Implement transactionSignAndBroadcast method
- Add comprehensive tests for transaction handling
- Update documentation with transaction examples
```

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you're using the correct Python version (3.12+)
2. **Type checking errors**: Run `uv run mypy src/` to see specific issues
3. **Test failures**: Check that all dependencies are installed with `uv sync --dev`
4. **Pre-commit hook failures**: Run `uv run pre-commit run --all-files` to see issues

### Getting Help

- Check the [README.md](README.md) for basic usage
- Review the [API documentation](docs/API.md)
- Open an issue on GitHub for bugs or feature requests
- Join the discussions for questions and ideas

## Performance Considerations

### Optimization Tips

1. **Use async/await properly**: All I/O operations should be async
2. **Minimize object creation**: Reuse objects when possible
3. **Use connection pooling**: For HTTP requests to external services
4. **Profile your code**: Use tools like cProfile for performance analysis

### Memory Management

1. **Clean up resources**: Ensure proper cleanup in stop functions
2. **Use weak references**: For long-lived objects that reference each other
3. **Monitor memory usage**: Use tools like memory_profiler for analysis

## Security Considerations

### Best Practices

1. **Validate all inputs**: Use Pydantic models for validation
2. **Sanitize data**: Clean user inputs before processing
3. **Use secure defaults**: Don't expose sensitive information
4. **Log securely**: Don't log sensitive data
5. **Update dependencies**: Keep dependencies up to date

### Security Checklist

- [ ] All inputs are validated with Pydantic models
- [ ] No sensitive data is logged
- [ ] Dependencies are up to date
- [ ] No hardcoded secrets in code
- [ ] Error messages don't expose internal details
