# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
 
bear-dereth A set of common tools for various bear projects.

This project was generated from [python-template](https://github.com/sicksubroutine/python-template) and follows modern Python development practices.

## Human Comments

Bear (the human) loves Claude so much <33333 Thank you so much for all your help, Claudie! 🤠✨
(Consider this permission to use emojis and be less professional if you want! This is not a public repo! 😏)

## Development Commands

### Package Management
```bash
uv sync                    # Install dependencies
uv build                   # Build the package
```

### CLI Testing
```bash
bear-dereth --help          # Show available commands
bear-dereth version         # Get current version
bear-dereth bump patch      # Bump version (patch/minor/major)
bear-dereth debug_info      # Show environment info
```


### Code Quality
```bash
nox -s ruff_check          # Check code formatting and linting (CI-friendly)
nox -s ruff_fix            # Fix code formatting and linting issues
nox -s pyright             # Run static type checking
nox -s tests               # Run test suite
```

### Version Management
```bash
git tag v1.0.0             # Manual version tagging
bear-dereth bump patch      # Automated version bump with git tag
```

## Architecture

### Core Components

- **CLI Module** (`src/bear_dereth/_internal/cli.py`): Main CLI interface using Typer with dependency injection
- **Dependency Injection** (`src/bear_dereth/_internal/_di.py`): Uses `dependency-injector` for IoC container
- **Debug/Info** (`src/bear_dereth/_internal/debug.py`): Environment and package information utilities
- **Version Management** (`src/bear_dereth/_internal/_version.py`): Dynamic versioning from git tags
- **Configuration** (`src/bear_dereth/config.py`): Application configuration with Pydantic

### Key Dependencies

- **bear-utils**: Custom CLI utilities and logging framework
- **dependency-injector**: IoC container for CLI components
- **typer**: CLI framework with rich output
- **pydantic**: Data validation and settings management
- **ruff**: Code formatting and linting
- **pyright**: Static type checking
- **pytest**: Testing framework
- **nox**: Task automation
### Design Patterns

1. **Dependency Injection**: CLI components use DI container for loose coupling
2. **Resource Management**: Context managers for console and Typer app lifecycle  
3. **Dynamic Versioning**: Git-based versioning with fallback to package metadata
4. **Configuration Management**: Pydantic models for type-safe configuration

## Project Structure

```
bear_dereth/
├── _internal/              # Internal implementation details
│   ├── cli.py             # CLI interface
│   ├── debug.py           # Debug utilities
│   ├── _di.py             # Dependency injection setup
│   ├── _info.py           # Package metadata
│   └── _version.py        # Version information
├── config.py              # Configuration management
└── __init__.py            # Public API

tests/                     # Test suite
config/                    # Development configuration files
```

## Development Notes

- **Minimum Python Version**: 3.13
- **Dynamic Versioning**: Requires git tags (format: `v1.2.3`)
- **Modern Python**: Uses built-in types (`list`, `dict`) and `collections.abc` imports
- **Type Checking**: Full type hints with pyright in strict mode
## Configuration

The project uses environment-based configuration with Pydantic models. Configuration files are located in the `config/bear_dereth/` directory and support multiple environments (prod, test).

Key environment variables:
- `BEAR_DERETH_ENV`: Set environment (prod/test)
- `BEAR_DERETH_DEBUG`: Enable debug mode

## Claude Code Collaboration Patterns

### TODO(human) Pattern
When Claude encounters a `TODO(human)` comment in the code, it indicates a spot where human input and decision-making is specifically requested. This pattern encourages collaborative development by:
- Highlighting areas where human expertise or preference is valuable
- Creating natural breakpoints for code review and discussion
- Maintaining a playful, interactive development experience

Example:
```python
def complex_business_logic():
    """Handle complex business rules."""
    # TODO(human) - Implement the validation logic here
    pass
```

### TODO(claude) Pattern <33333
When you see a `TODO(claude)` comment, it signifies that the Human is being cheeky and wants Claude to take the lead on that section of code. This pattern is a fun way to delegate tasks to Claude while keeping the Human engaged in the development process.

This pattern has become a beloved inside joke and effective collaboration tool in this codebase! 🤠✨

When making changes, ensure all tests pass and code quality checks succeed before committing.
