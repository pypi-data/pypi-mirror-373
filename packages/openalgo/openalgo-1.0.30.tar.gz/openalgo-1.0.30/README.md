# OpenAlgo Python Library

A Python library for algorithmic trading using OpenAlgo's REST APIs. This library provides a comprehensive interface for order management, market data, account operations, and strategy automation.

## Installation

```bash
pip install openalgo
```

## Quick Start

```python
from openalgo import api

# Initialize the client
client = api(
    api_key="your_api_key",
    host="http://127.0.0.1:5000"  # or your OpenAlgo server URL
)
```

## API Categories

### 1. Strategy API

#### Strategy Management Module
OpenAlgo's Strategy Management Module allows you to automate your trading strategies using webhooks. This enables seamless integration with any platform or custom system that can send HTTP requests. The Strategy class provides a simple interface to send signals that trigger orders based on your strategy configuration in OpenAlgo.

```python
from openalgo import Strategy
import requests

# Initialize strategy client
client = Strategy(
    host_url="http://127.0.0.1:5000",  # Your OpenAlgo server URL
    webhook_id="your-webhook-id"        # Get this from OpenAlgo strategy section
)

try:
    # Long entry (BOTH mode with position size)
    response = client.strategyorder("RELIANCE", "BUY", 1)
    print(f"Long entry successful: {response}")

    # Short entry
    response = client.strategyorder("ZOMATO", "SELL", 1)
    print(f"Short entry successful: {response}")

    # Close positions
    response = client.strategyorder("RELIANCE", "SELL", 0)  # Close long
    response = client.strategyorder("ZOMATO", "BUY", 0)     # Close short

except requests.exceptions.RequestException as e:
    print(f"Error sending order: {e}")
```

Strategy Modes:
- **LONG_ONLY**: Only processes BUY signals for long-only strategies
- **SHORT_ONLY**: Only processes SELL signals for short-only strategies
- **BOTH**: Processes both BUY and SELL signals with position sizing

The Strategy Management Module can be integrated with:
- Custom trading systems
- Technical analysis platforms
- Alert systems
- Automated trading bots
- Any system capable of making HTTP requests

### 2. Accounts API

#### Funds
Get funds and margin details of the trading account.
```python
result = client.funds()
# Returns:
{
    "data": {
        "availablecash": "18083.01",
        "collateral": "0.00",
        "m2mrealized": "0.00",
        "m2munrealized": "0.00",
        "utiliseddebits": "0.00"
    },
    "status": "success"
}
```

#### Orderbook
Get orderbook details with statistics.
```python
result = client.orderbook()
# Returns order details and statistics including:
# - Total buy/sell orders
# - Total completed/open/rejected orders
# - Individual order details with status
```

#### Tradebook
Get execution details of trades.
```python
result = client.tradebook()
# Returns list of executed trades with:
# - Symbol, action, quantity
# - Average price, trade value
# - Timestamp, order ID
```

#### Positionbook
Get current positions across all segments.
```python
result = client.positionbook()
# Returns list of positions with:
# - Symbol, exchange, product
# - Quantity, average price
```

#### Holdings
Get stock holdings with P&L details.
```python
result = client.holdings()
# Returns:
# - List of holdings with quantity and P&L
# - Statistics including total holding value
# - Total investment value and P&L
```

#### Analyzer Status
Get analyzer status information.
```python
result = client.analyzerstatus()
# Returns:
{
    "data": {
        "analyze_mode": false,
        "mode": "live",
        "total_logs": 2
    },
    "status": "success"
}
```

#### Analyzer Toggle
Toggle analyzer mode between analyze and live modes.
```python
# Switch to analyze mode (simulated responses)
result = client.analyzertoggle(mode=True)

# Switch to live mode (actual broker operations)
result = client.analyzertoggle(mode=False)

# Returns:
{
    "status": "success",
    "data": {
        "mode": "live/analyze",
        "analyze_mode": true/false,
        "total_logs": 2,
        "message": "Analyzer mode switched to live"
    }
}
```

### 3. Orders API

#### Place Order
Place a regular order.
```python
result = client.placeorder(
    symbol="RELIANCE",
    exchange="NSE",
    action="BUY",
    quantity=1,
    price_type="MARKET",
    product="MIS"
)
```

#### Place Smart Order
Place an order with position sizing.
```python
result = client.placesmartorder(
    symbol="RELIANCE",
    exchange="NSE",
    action="BUY",
    quantity=1,
    position_size=100,
    price_type="MARKET",
    product="MIS"
)
```

#### Basket Order
Place multiple orders simultaneously.
```python
orders = [
    {
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "action": "BUY",
        "quantity": 1,
        "pricetype": "MARKET",
        "product": "MIS"
    },
    {
        "symbol": "INFY",
        "exchange": "NSE",
        "action": "SELL",
        "quantity": 1,
        "pricetype": "MARKET",
        "product": "MIS"
    }
]
result = client.basketorder(orders=orders)
```

#### Split Order
Split a large order into smaller ones.
```python
result = client.splitorder(
    symbol="YESBANK",
    exchange="NSE",
    action="SELL",
    quantity=105,
    splitsize=20,
    price_type="MARKET",
    product="MIS"
)
```

#### Order Status
Check status of a specific order.
```python
result = client.orderstatus(
    order_id="24120900146469",
    strategy="Test Strategy"
)
```

#### Open Position
Get current open position for a symbol.
```python
result = client.openposition(
    symbol="YESBANK",
    exchange="NSE",
    product="CNC"
)
```

#### Modify Order
Modify an existing order.
```python
result = client.modifyorder(
    order_id="24120900146469",
    symbol="RELIANCE",
    action="BUY",
    exchange="NSE",
    quantity=2,
    price="2100",
    product="MIS",
    price_type="LIMIT"
)
```

#### Cancel Order
Cancel a specific order.
```python
result = client.cancelorder(
    order_id="24120900146469"
)
```

#### Cancel All Orders
Cancel all open orders.
```python
result = client.cancelallorder()
```

#### Close Position
Close all open positions.
```python
result = client.closeposition()
```

### 4. WebSocket Feed API

The WebSocket Feed API provides real-time market data through WebSocket connections. The API supports three types of market data:

#### LTP (Last Traded Price) Feed
Get real-time LTP updates for multiple instruments:
```python
from openalgo import api
import time

# Initialize the client with explicit WebSocket URL
client = api(
    api_key="your_api_key",
    host="http://127.0.0.1:5000",  # REST API host
    ws_url="ws://127.0.0.1:8765"   # WebSocket server URL (can be different from REST API)
)

# Define instruments to subscribe to
instruments = [
    {"exchange": "MCX", "symbol": "GOLDPETAL30MAY25FUT"},
    {"exchange": "MCX", "symbol": "GOLD05JUN25FUT"}
]

# Callback function for data updates
def on_data_received(data):
    print("LTP Update:")
    print(data)

# Connect and subscribe
client.connect()
client.subscribe_ltp(instruments, on_data_received=on_data_received)

# Poll LTP data
print(client.get_ltp())
# Returns nested format:
# {"ltp": {"MCX": {"GOLDPETAL30MAY25FUT": {"timestamp": 1747761583959, "ltp": 9529.0}}}}

# Cleanup
client.unsubscribe_ltp(instruments)
client.disconnect()
```

#### Quote Feed
Get real-time quote updates with OHLC data:
```python
from openalgo import api

# Initialize the client
client = api(
    api_key="your_api_key",
    host="http://127.0.0.1:5000",
    ws_url="ws://127.0.0.1:8765"
)

# Define instruments
instruments = [
    {"exchange": "MCX", "symbol": "GOLDPETAL30MAY25FUT"}
]

# Connect and subscribe
client.connect()
client.subscribe_quote(instruments)

# Poll quote data
print(client.get_quotes())
# Returns nested format:
# {"quote": {"MCX": {"GOLDPETAL30MAY25FUT": {
#   "timestamp": 1747767126517,
#   "open": 9430.0,
#   "high": 9544.0,
#   "low": 9390.0,
#   "close": 9437.0,
#   "ltp": 9535.0
# }}}}

# Cleanup
client.unsubscribe_quote(instruments)
client.disconnect()
```

#### Market Depth Feed
Get real-time market depth (order book) data:
```python
from openalgo import api

# Initialize the client
client = api(
    api_key="your_api_key",
    host="http://127.0.0.1:5000",
    ws_url="ws://127.0.0.1:8765"
)

# Define instruments
instruments = [
    {"exchange": "MCX", "symbol": "GOLDPETAL30MAY25FUT"}
]

# Connect and subscribe
client.connect()
client.subscribe_depth(instruments)

# Poll depth data
print(client.get_depth())
# Returns nested format with order book:
# {"depth": {"MCX": {"GOLDPETAL30MAY25FUT": {
#   "timestamp": 1747767126517,
#   "ltp": 9535.0,
#   "buyBook": {"1": {"price": "9533.0", "qty": "53332", "orders": "0"}, ...},
#   "sellBook": {"1": {"price": "9535.0", "qty": "53332", "orders": "0"}, ...}
# }}}}

# Cleanup
client.unsubscribe_depth(instruments)
client.disconnect()
```

### 5. REST Data API

#### Quotes
Get real-time quotes for a symbol using REST API.
```python
result = client.quotes(
    symbol="RELIANCE",
    exchange="NSE"
)
# Returns bid/ask, LTP, volume and other quote data
```

#### Market Depth
Get market depth (order book) data.
```python
result = client.depth(
    symbol="RELIANCE",
    exchange="NSE"
)
# Returns market depth with top 5 bids/asks
```

#### Historical Data
Get historical price data.
```python
result = client.history(
    symbol="RELIANCE",
    exchange="NSE",
    interval="5m",  # Use intervals() to get supported intervals
    start_date="2024-01-01",
    end_date="2024-01-31"
)
# Returns pandas DataFrame with OHLC data
```

#### Intervals
Get supported time intervals for historical data.
```python
result = client.intervals()
# Returns:
{
    "status": "success",
    "data": {
        "seconds": ["1s"],
        "minutes": ["1m", "2m", "3m", "5m", "10m", "15m", "30m", "60m"],
        "hours": [],
        "days": ["D"],
        "weeks": [],
        "months": []
    }
}
```

> Note: The legacy `interval()` method is still available but will be deprecated in future versions.

#### Symbol
Get details for a specific trading symbol.
```python
result = client.symbol(
    symbol="NIFTY24APR25FUT",
    exchange="NFO"
)
# Returns:
{
    "status": "success",
    "data": {
        "brexchange": "NFO",
        "brsymbol": "NIFTY24APR25FUT",
        "exchange": "NFO",
        "expiry": "24-APR-25",
        "id": 39521,
        "instrumenttype": "FUTIDX",
        "lotsize": 75,
        "name": "NIFTY",
        "strike": -0.01,
        "symbol": "NIFTY24APR25FUT",
        "tick_size": 0.05,
        "token": "54452"
    }
}
```

#### Search
Search for symbols across exchanges.
```python
result = client.search(
    query="RELIANCE"
)
# Returns list of matching symbols with details

# Search with exchange filter
result = client.search(
    query="NIFTY",
    exchange="NFO"
)
# Supported exchanges: NSE, NFO, BSE, BFO, MCX, CDS, BCD, NCDEX, NSE_INDEX, BSE_INDEX, MCX_INDEX
# Returns:
{
    "status": "success",
    "data": [
        {
            "symbol": "NIFTY24APR25FUT",
            "name": "NIFTY",
            "exchange": "NFO",
            "token": "54452",
            "instrumenttype": "FUTIDX",
            "lotsize": 75,
            "strike": -0.01,
            "expiry": "24-APR-25"
        },
        # ... more matching symbols
    ]
}
```

#### Expiry
Get expiry dates for futures and options.
```python
# Get expiry dates for futures
result = client.expiry(
    symbol="NIFTY",
    exchange="NFO",
    instrumenttype="futures"
)
# Returns:
{
    "status": "success",
    "data": [
        "31-JUL-25",
        "28-AUG-25",
        "25-SEP-25"
    ],
    "message": "Found 3 expiry dates for NIFTY futures in NFO"
}

# Get expiry dates for options
result = client.expiry(
    symbol="NIFTY",
    exchange="NFO",
    instrumenttype="options"
)
# Returns:
{
    "status": "success",
    "data": [
        "10-JUL-25",
        "17-JUL-25",
        "24-JUL-25",
        "31-JUL-25",
        "07-AUG-25",
        "28-AUG-25",
        "25-SEP-25",
        "24-DEC-25",
        "26-MAR-26",
        "25-JUN-26"
    ],
    "message": "Found 10 expiry dates for NIFTY options in NFO"
}
```

## Examples

Check the examples directory for detailed usage:
- account_test.py: Test account-related functions
- order_test.py: Test order management functions
- data_examples.py: Test market data functions
- feed_examples.py: Test WebSocket LTP feeds
- quote_example.py: Test WebSocket quote feeds
- depth_example.py: Test WebSocket market depth feeds

## Publishing to PyPI

1. Update version in `openalgo/__init__.py`

2. Build the distribution:
```bash
python -m pip install --upgrade build
python -m build
```

3. Upload to PyPI:
```bash
python -m pip install --upgrade twine
python -m twine upload dist/*
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
