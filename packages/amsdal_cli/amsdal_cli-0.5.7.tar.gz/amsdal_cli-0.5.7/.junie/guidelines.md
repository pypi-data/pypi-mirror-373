# Project Guidelines

## Project Overview

AMSDAL CLI is a command-line interface for the AMSDAL (A. Michael Salem Data Access Layer) framework. It provides tools for managing AMSDAL applications, including:

- Generating code from models
- Running a development server
- Managing migrations
- Testing and verification
- Cloud integration

The project is structured as follows:

- `src/amsdal_cli/` - Main source code
  - `commands/` - CLI commands implementation
  - `config/` - Configuration management
  - `utils/` - Utility functions and helpers
- `tests/` - Test suite
  - `async/` - Asynchronous tests
  - `e2e/` - End-to-end tests
  - `fixtures/` - Test fixtures
  - `sync/` - Synchronous tests

The CLI is built using Typer and follows a command-based structure with subcommands organized in modules.

## Code Style Guide

### Python Version
- Target Python version: 3.11+
- Code should be compatible with Python 3.10+ for development

### Formatting
- Line length: 120 characters
- Use Black for code formatting
- Use single quotes for strings, except for docstrings which use double quotes
- Imports should be on separate lines (no multi-imports)
- Imports should be ordered by type (standard library, third-party, first-party)

### Type Annotations
- All code must use type annotations
- Use `typing.TYPE_CHECKING` for import-only type dependencies
- Follow strict mypy rules:
  - No implicit reexports
  - Disallow untyped definitions
  - Disallow any generics
  - Check untyped definitions

### Linting
- Use Ruff for linting with the following rule sets enabled:
  - A: flake8-builtins
  - ARG: flake8-unused-arguments
  - B: flake8-bugbear
  - C: flake8-comprehensions
  - DTZ: flake8-datetimez
  - E: pycodestyle errors
  - EM: flake8-errmsg
  - F: pyflakes
  - FBT: flake8-boolean-trap
  - I: isort
  - ICN: flake8-import-conventions
  - ISC: flake8-implicit-str-concat
  - N: pep8-naming
  - PLC, PLE, PLR, PLW: pylint
  - Q: flake8-quotes
  - RUF: Ruff-specific rules
  - S: flake8-bandit
  - T: flake8-debugger
  - TID: flake8-tidy-imports
  - UP: pyupgrade
  - W: pycodestyle warnings
  - YTT: flake8-2020

### Imports
- No relative imports
- Group imports by source (standard library, third-party, first-party)
- Known first-party modules: amsdal_cli

### Documentation
- Use docstrings for functions, classes, and modules
- Use markdown formatting in docstrings
- Include help text for CLI commands and options

### Testing
- Write tests for all functionality
- Use pytest for testing
- Include both synchronous and asynchronous tests where appropriate
- Use fixtures for test data
- Aim for high test coverage

### Error Handling
- Use appropriate exception handling with try/except/finally blocks
- Properly clean up resources in finally blocks

### Asynchronous Code
- Support both synchronous and asynchronous execution paths where needed
- Use asyncio for asynchronous code
- Follow asyncio best practices

### Version Control
- Use towncrier for managing release notes
- Organize changes by type (security, removed, deprecated, added, changed, fixed, performance)
