# emta

## Overview

Unofficial EasyMoney Trading Library

## Technology Stack
  * Use UV to manage development environments and third-party dependencies.
  * Use [Pytest testing](https://github.com/pytest-dev/pytest) ensures the correctness of each module and function.

## Features

  * [x] login to eastmoney
  * [x] Modular code structure
  * [x] Error handling
  * [x] Trading agent with order placement and management
  * [x] Market data retrieval

## Installation

Ensure you are using Python 3.11 or later (but less than 4.0).

``` shell
pip install emta
```

## Usage

```python
from emta import TradingAgent, OrderType

# Create a trading agent
agent = TradingAgent("your_username", "your_password")

# Login to Eastmoney
if agent.login():
    # Place a buy order
    order_id = agent.place_order("SH600000", OrderType.BUY, 100, 12.5)

    # Get market data
    market_data = agent.get_market_data("SH600000")

    # Logout
    agent.logout()
```

See [examples/trading_example.py](examples/trading_example.py) for a complete example.

## Testing

Tests for the app are included using [pytest](https://docs.pytest.org/). To run the tests, simply execute:

```bash
uv run pytest
```

## Project Structure

```
src/emta/                  # Main source code
├── __init__.py            # Package initialization
├── py.typed               # Type hints marker
├── core/                  # Core trading agent implementation
│   └── agent.py           # Main trading agent class
├── models/                # Data models and exceptions
│   ├── trading.py         # Trading data models
│   └── exceptions.py      # Exception classes
├── auth/                  # Authentication module
│   └── client.py          # Authentication client
├── api/                   # API client for trading operations
│   └── client.py          # API client implementation
└── utils/                 # Utility functions
    ├── encryption.py      # Password encryption utilities
    └── captcha.py         # Captcha recognition utilities
tests/                     # Test files
examples/                  # Example usage scripts
```

## Contributing

Contributions are welcome! If you have ideas for improvements, bug fixes, or additional features, feel free to open an issue or submit a pull request.

## License

This App is open-source software released under the [MIT License](./LICENSE).
