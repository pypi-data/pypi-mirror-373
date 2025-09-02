# Qwen Code Context for EastmoneyTradingLibrary

## Project Overview

This is a Python package named `emta` (Easy Money Trading Agent). It's an unofficial library intended for interacting with Eastmoney trading services. The project provides functionality for authentication, placing orders, checking account status, and retrieving market data.

### Key Technologies
- **Language**: Python 3.11+
- **Dependency Management**: UV (package management and virtual environment)
- **Build System**: Hatchling
- **HTTP Client**: HTTPX
- **Testing**: Pytest
- **Logging**: Loguru
- **Code Quality**:
  - Mypy (static type checking)
  - Ruff (linting and formatting)
  - Pre-commit (git hooks)
- **Captcha Recognition**: ddddocr
- **Encryption**: cryptography
- **License**: MIT

### Project Structure
```
EastmoneyTradingLibrary/
├── examples/               # Example usage scripts
├── src/emta/               # Main source code package
│   ├── __init__.py         # Package initializer and exports
│   ├── py.typed            # PEP 561 marker for type hints
│   ├── core/               # Core trading agent implementation
│   │   └── agent.py        # Main trading agent class
│   ├── models/             # Data models and exceptions
│   │   ├── trading.py      # Trading data models (Order, OrderType, etc.)
│   │   └── exceptions.py   # Exception classes
│   ├── auth/               # Authentication module
│   │   └── client.py       # Authentication client
│   ├── api/                # API client for trading operations
│   │   └── client.py       # API client implementation
│   └── utils/              # Utility functions
│       ├── encryption.py   # Password encryption utilities
│       └── captcha.py      # Captcha recognition utilities
├── tests/                  # Test files
├── dist/                   # Distribution files (built packages)
├── .python-version         # Specifies Python version (3.11)
├── LICENSE                 # MIT license file
├── README.md               # Project documentation
├── pyproject.toml          # Project configuration (metadata, dependencies, tools)
└── uv.lock                 # UV lock file for dependencies
```

## Building and Running

### Prerequisites
- Python 3.11 or later (but less than 4.0)
- UV package manager

### Installation
```bash
pip install emta
```

### Development Setup
1. Clone the repository
2. Install dependencies using UV:
   ```bash
   uv sync
   ```

### Running Tests
Tests are written with pytest. Execute them using:
```bash
uv run pytest
```

### Type Checking
Run mypy for static type checking:
```bash
uv run mypy src/
```

### Linting
Check code style with ruff:
```bash
uv run ruff check src/
```

## Development Conventions

### Code Style
- Follow PEP 8 style guide
- Use type hints for all function signatures and variables where possible
- Ruff is configured with specific rules (E, W, F, I, B, C4, UP, ARG001) and ignores (E501, B008, W191, B904)

### Testing
- Use pytest for writing tests
- Place test files in the `tests/` directory
- Aim for comprehensive test coverage

### Dependency Management
- Runtime dependencies are defined in `pyproject.toml` under `[project.dependencies]`
- Development dependencies are defined in `pyproject.toml` under `[tool.uv.dev-dependencies]`
- Use `uv.lock` to lock dependency versions for reproducible builds

### Versioning
- Follow semantic versioning (currently at 0.1.0)
- Version is specified in `pyproject.toml`

### Commit Hooks
- Pre-commit is configured for git hooks to ensure code quality before commits

## Current Status
The project has implemented core features including:
- [x] Login to Eastmoney
- [x] Modular code structure
- [x] Error handling
- [x] Trading agent with order placement and management
- [x] Market data retrieval

However, some functionalities like actual order placement, cancellation, and status checking are still implemented as placeholders and need to be connected to the real Eastmoney API endpoints.
