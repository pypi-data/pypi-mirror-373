# Finatic Server Python SDK

A Python SDK for integrating with Finatic's server-side trading and portfolio management APIs.

## Installation

```bash
pip install finatic-server-python
```

## Quick Start

```python
import asyncio
from finatic_server import FinaticServerClient

async def main():
    # Initialize with API key
    client = FinaticServerClient("your-api-key")
    
    # Option 1: Portal Authentication
    await client.start_session()
    portal_url = await client.get_portal_url()
    print(f"User should visit: {portal_url}")
    
    # After user completes authentication in portal, get user info
    user_info = await client.get_session_user()
    print(f"Authenticated user: {user_info['user_id']}")
    
    # Option 2: Direct Authentication (if you know the user ID)
    # client = FinaticServerClient("your-api-key", user_id="user123")
    # await client.start_session()
    
    # Now you can access broker data
    brokers = await client.get_broker_list()
    print(f"Available brokers: {len(brokers)}")
    
    # Get all orders across all pages
    all_orders = await client.get_all_broker_orders()
    print(f"Total orders: {len(all_orders)}")

# Run the example
asyncio.run(main())
```

## Authentication Flow

The SDK supports two authentication methods:

### 1. Portal Authentication (User completes auth in browser)

```python
client = FinaticServerClient("your-api-key")

# Start session
await client.start_session()

# Get portal URL for user authentication
portal_url = await client.get_portal_url()
print(f"User should visit: {portal_url}")

# After user completes authentication in portal
user_info = await client.get_session_user()
print(f"User ID: {user_info['user_id']}")
print(f"Access Token: {user_info['access_token']}")

# Now you can make authenticated requests
brokers = await client.get_broker_list()
```

### 2. Direct Authentication (Server-side with known user ID)

```python
client = FinaticServerClient("your-api-key", user_id="user123")

# Start session (automatically authenticates with user ID)
await client.start_session()

# Now you can make authenticated requests immediately
brokers = await client.get_broker_list()
```

## Core Features

- **API Key Authentication**: Secure server-side authentication
- **Portal Integration**: Get portal URLs for user authentication
- **Automatic Token Management**: Handles access/refresh tokens automatically
- **Pagination Support**: Built-in pagination for large datasets
- **Type-safe API**: Full Pydantic model support
- **Async/await Support**: Non-blocking operations
- **Comprehensive Error Handling**: Detailed error types

## API Reference

### Initialization

```python
client = FinaticServerClient(
    api_key="your-api-key",
    user_id="user123",                    # Optional - for direct authentication
)
```

### Authentication Methods

- `start_session()` - Start a new session (authenticates directly if user_id provided)
- `get_portal_url()` - Get portal URL for user authentication (portal flow only)
- `get_session_user()` - Get user info and tokens after portal completion (portal flow only)

### Broker Data Methods

#### Basic Methods (with pagination support)
- `get_broker_list()` - Get list of available brokers
- `get_broker_connections()` - Get broker connections
- `get_broker_accounts(page=1, per_page=100, options=None, filters=None)` - Get broker accounts
- `get_broker_orders(page=1, per_page=100, options=None, filters=None)` - Get broker orders
- `get_broker_positions(page=1, per_page=100, options=None, filters=None)` - Get broker positions

#### Get All Methods (automatically handles pagination)
- `get_all_broker_accounts(options=None, filters=None)` - Get all broker accounts across all pages
- `get_all_broker_orders(options=None, filters=None)` - Get all broker orders across all pages
- `get_all_broker_positions(options=None, filters=None)` - Get all broker positions across all pages

### Filter Options

```python
from finatic_server.types.broker import BrokerDataOptions, OrdersFilter, PositionsFilter, AccountsFilter

# Basic filtering
options = BrokerDataOptions(
    broker_name="robinhood",
    account_id="123456",
    symbol="AAPL"
)

# Advanced filtering for orders
order_filters = OrdersFilter(
    status="filled",
    side="buy",
    asset_type="stock",
    created_after="2024-01-01T00:00:00Z"
)

# Advanced filtering for positions
position_filters = PositionsFilter(
    symbol="AAPL",
    side="long",
    asset_type="stock"
)

# Advanced filtering for accounts
account_filters = AccountsFilter(
    account_type="margin",
    status="active",
    currency="USD"
)
```

## Usage Examples

### Get All Orders with Filtering

```python
# Get all filled orders for a specific symbol
all_filled_orders = await client.get_all_broker_orders(
    filters=OrdersFilter(
        status="filled",
        symbol="AAPL"
    )
)
print(f"Found {len(all_filled_orders)} filled AAPL orders")
```

### Pagination Example

```python
# Get first page of 10 orders
first_page = await client.get_broker_orders(page=1, per_page=10)
print(f"First page: {len(first_page)} orders")

# Get second page
second_page = await client.get_broker_orders(page=2, per_page=10)
print(f"Second page: {len(second_page)} orders")
```

### Get All Data for Analysis

```python
# Get all accounts, orders, and positions
all_accounts = await client.get_all_broker_accounts()
all_orders = await client.get_all_broker_orders()
all_positions = await client.get_all_broker_positions()

print(f"Total accounts: {len(all_accounts)}")
print(f"Total orders: {len(all_orders)}")
print(f"Total positions: {len(all_positions)}")
```

### Filter by Broker

```python
# Get all orders from Robinhood
robinhood_orders = await client.get_all_broker_orders(
    options=BrokerDataOptions(broker_name="robinhood")
)

# Get all positions from Tasty Trade
tasty_positions = await client.get_all_broker_positions(
    options=BrokerDataOptions(broker_name="tasty_trade")
)
```

## Error Handling

The SDK provides comprehensive error handling:

```python
from finatic_server import AuthenticationError, ApiError, NetworkError

try:
    orders = await client.get_broker_orders()
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
except ApiError as e:
    print(f"API error: {e}")
```

## Complete Example

```python
import asyncio
from finatic_server import FinaticServerClient
from finatic_server.types.broker import OrdersFilter, BrokerDataOptions

async def main():
    # Option 1: Portal Authentication (user completes auth in browser)
    client = FinaticServerClient("your-api-key")
    
    try:
        # Start session
        await client.start_session()
        
        # Get portal URL
        portal_url = await client.get_portal_url()
        print(f"Please visit: {portal_url}")
        
        # Wait for user to complete authentication
        input("Press Enter after completing authentication...")
        
        # Get user info
        user_info = await client.get_session_user()
        print(f"Authenticated as: {user_info['user_id']}")
        
        # Option 2: Direct Authentication (if you know the user ID)
        # client = FinaticServerClient("your-api-key", user_id="user123")
        # await client.start_session()
        # print("Directly authenticated!")
        
        # Get broker information
        brokers = await client.get_broker_list()
        print(f"Available brokers: {[b.name for b in brokers]}")
        
        # Get all filled orders
        filled_orders = await client.get_all_broker_orders(
            filters=OrdersFilter(status="filled")
        )
        print(f"Total filled orders: {len(filled_orders)}")
        
        # Get all positions
        positions = await client.get_all_broker_positions()
        print(f"Total positions: {len(positions)}")
        
        # Get accounts with cash balance
        accounts = await client.get_all_broker_accounts()
        for account in accounts:
            cash = account.cash_balance or 0.0
            print(f"{account.account_name}: ${cash:,.2f}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## License

MIT License - see [LICENSE](LICENSE) file for details. 