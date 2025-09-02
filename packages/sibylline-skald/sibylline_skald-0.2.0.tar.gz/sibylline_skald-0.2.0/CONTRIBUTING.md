# Contributing to Skald

Thank you for your interest in contributing to Skald! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sibyllinesoft/skald.git
   cd skald
   ```

2. **Set up development environment:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev,test]"
   ```

3. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

## Code Quality Standards

### Testing
- Maintain minimum 85% test coverage
- Write tests for all new functionality
- Include both unit and integration tests
- Use meaningful test names and docstrings

### Code Style
- Use `ruff` for linting and formatting
- Follow `black` code style (100 character line length)
- Use `isort` for import sorting
- Type hints are required for all public APIs

### Documentation
- Update docstrings for all public APIs
- Follow Google-style docstrings
- Update README.md if adding new features
- Add examples for new functionality

## Development Workflow

### Running Tests
```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_core.py

# Run tests with coverage report
pytest --cov=skald --cov-report=html
```

### Code Quality Checks
```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy skald/

# Security scanning
bandit -r skald/

# Run all pre-commit checks
pre-commit run --all-files
```

## Submitting Changes

### Pull Request Process
1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Follow the coding standards above
   - Write tests for new functionality
   - Update documentation as needed

3. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

4. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a pull request:**
   - Use a descriptive title
   - Include a detailed description of changes
   - Reference any related issues
   - Ensure all CI checks pass

### Commit Messages
Use conventional commits format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for adding tests
- `refactor:` for code refactoring
- `perf:` for performance improvements

## Architecture Guidelines

### Core Principles
1. **Transparency**: Skald should be invisible to existing MCP workflows
2. **Reliability**: Never break existing functionality
3. **Performance**: Minimal overhead on tool calls
4. **Configurability**: Allow users to customize behavior

### Module Structure
- `skald/core.py`: Main SurveyingProxy class
- `skald/schema/`: Pydantic data models
- `skald/storage/`: Storage backend interfaces
- `skald/transport/`: Communication protocols
- `skald/decorators.py`: Opt-out mechanisms

### Adding New Features

#### Storage Backends
To add a new storage backend:
1. Inherit from `skald.storage.base.StorageBackend`
2. Implement all abstract methods
3. Add comprehensive tests
4. Update documentation

#### Transport Protocols
To add a new transport:
1. Inherit from `skald.transport.base.Transport`
2. Implement protocol-specific message handling
3. Add integration tests
4. Update CLI if needed

#### Redaction Strategies
To add new redaction patterns:
1. Extend `skald.redaction.default.DefaultRedactor`
2. Add pattern matching logic
3. Include test cases with sample data
4. Document the redaction behavior

## Testing Guidelines

### Test Structure
- Unit tests: `tests/test_*.py`
- Integration tests: Include real MCP server interactions
- Property tests: Use `hypothesis` for edge cases
- Performance tests: Measure latency overhead

### Mock Guidelines
- Mock external dependencies (databases, network)
- Use realistic test data
- Test both success and failure paths
- Verify all side effects

### Coverage Requirements
- Minimum 85% line coverage
- 100% coverage for critical paths
- Include edge cases and error conditions
- Test async code thoroughly

## Documentation Standards

### API Documentation
- Use Google-style docstrings
- Include parameter types and descriptions
- Provide usage examples
- Document exceptions and error conditions

### Code Comments
- Explain complex logic, not obvious operations
- Document design decisions and trade-offs
- Include references to specifications or standards
- Update comments when code changes

## Release Process

Releases are automated through GitHub Actions:

1. **Version Bumping**: Update `pyproject.toml` version
2. **Changelog**: Update `CHANGELOG.md` with new features/fixes
3. **GitHub Release**: Create a GitHub release with tag
4. **PyPI**: Automated publishing via GitHub Actions

## Getting Help

- **Issues**: Create GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Security**: Email security issues privately to maintainers

## License

By contributing to Skald, you agree that your contributions will be licensed under the MIT License.