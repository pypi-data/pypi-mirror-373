# SlipperPy

A Python GraphQL client library for Slipper Energy Management systems.

## Features

- 🚀 Async/await support with `httpx`
- 🔒 Type-safe with Pydantic models
- 📝 Full GraphQL query and mutation support
- 🔄 WebSocket subscription support (planned)
- 🧪 Comprehensive test coverage
- 📚 Well-documented API
- ⚡ Energy consumption tracking
- 💰 Electricity price monitoring
- 🏠 Home management
- 📱 Device management

## Installation

```bash
pip install slipperpy
```

For development dependencies:

```bash
pip install slipperpy[dev]
```

## Quick Start

```python
import asyncio
from slipperpy import SlipperClient

async def main():
    client = SlipperClient("https://api.slipper.no/graphql")
    
    # Step 1: Request SMS verification code
    success = await client.request_sms_code("+47123456789")
    if success:
        print("SMS code sent!")
        
        # Step 2: Get the SMS code from user input
        sms_code = input("Enter SMS code: ")
        
        # Step 3: Login with SMS code
        token = await client.login_with_sms_code("+47123456789", int(sms_code))
        print(f"Logged in successfully!")
    
    # Get current user
    user = await client.get_current_user()
    print(f"Welcome, {user.first_name}!")
    
    # Get all homes
    homes = await client.get_homes()
    for home in homes:
        print(f"Home: {home.name} at {home.street} {home.street_number}")
    
    # Get consumption data for the first home
    if homes:
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        consumptions = await client.get_consumptions(
            home_id=homes[0].id,
            start=start_date,
            end=end_date,
            granularity="DAY"
        )
        
        for consumption in consumptions:
            print(f"Date: {consumption.date}, kWh: {consumption.kwh}, Cost: {consumption.cost}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Usage

### Authentication

#### SMS Login (Primary Method)
```python
client = SlipperClient("https://api.slipper.no/graphql")

# Step 1: Request SMS code
success = await client.request_sms_code("+47123456789")
if success:
    print("SMS code sent to your phone")

# Step 2: Enter the code you received via SMS
sms_code = input("Enter SMS code: ")

# Step 3: Complete login
token = await client.login_with_sms_code("+47123456789", int(sms_code))
print("Logged in successfully!")
```

#### Alternative: Combined SMS Method
```python
# Request SMS code
result = await client.login_with_sms("+47123456789")
print(result["message"])  # "SMS code requested"

# Login with SMS code (after receiving it)
result = await client.login_with_sms("+47123456789", code=123456)
if result["success"]:
    print("Logged in!")
```

#### Phone and Password Login (if available)
```python
# Only use if your account supports password login
token = await client.login_with_phone_and_password("+47123456789", "password")
```

#### Using Existing Token
```python
client = SlipperClient("https://api.slipper.no/graphql")
client.set_auth_token("your-existing-jwt-token")
```

### Home Management

```python
# Get all homes
homes = await client.get_homes()

# Get a specific home
home = await client.get_home("home-id")

# Get archived homes
archived_homes = await client.get_homes(archived=True)
```

### Energy Consumption

```python
from datetime import datetime, timedelta

# Get consumption for the last month
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

consumptions = await client.get_consumptions(
    home_id="your-home-id",
    start=start_date,
    end=end_date,
    granularity="DAY"  # Options: HOUR, DAY, MONTH
)

for consumption in consumptions:
    print(f"Date: {consumption.date}")
    print(f"Consumption: {consumption.kwh} kWh")
    print(f"Cost: {consumption.cost} NOK")
    print(f"Tax: {consumption.tax} NOK")
    print("---")
```

### Electricity Prices

```python
from datetime import datetime, timedelta

# Get electricity prices for tomorrow
start_date = datetime.now() + timedelta(days=1)
end_date = start_date + timedelta(days=1)

prices = await client.get_electricity_prices(
    start=start_date,
    end=end_date,
    granularity="HOUR",
    area="NO1",  # Norwegian price area
    forecast=True
)

for price in prices:
    print(f"Time: {price.date}, Price: {price.price} øre/kWh")
```

### Plan Management

```python
# Get all available electricity plans
plans = await client.get_plans()

# Get plans from a specific provider
plans = await client.get_plans(provider_id="provider-id")

# Get only active plans
active_plans = await client.get_plans(active=True)

for plan in plans:
    print(f"Plan: {plan.name}")
    print(f"Provider: {plan.provider}")
    print(f"Price per kWh: {plan.price_per_kwh}")
    print(f"Fixed fee: {plan.fixed_fee}")
```

### Provider Information

```python
# Get all electricity providers
providers = await client.get_providers()

for provider in providers:
    print(f"Provider: {provider.name}")
    print(f"Website: {provider.website}")
    print(f"Phone: {provider.phone}")
```

### User Management

```python
# Get current user information
user = await client.get_current_user()
print(f"User: {user.first_name} {user.last_name}")
print(f"Email: {user.email}")

# Update user information
success = await client.update_user(
    first_name="New Name",
    email="new.email@example.com"
)
```

### Raw GraphQL Queries

```python
# Execute custom GraphQL queries
query = """
query CustomQuery($homeId: ID!) {
    home(id: $homeId) {
        id
        name
        estimatedYearlyConsumption
        currentPlan {
            name
            pricePerKwh
        }
    }
}
"""

result = await client.execute(query, {"homeId": "your-home-id"})
print(result.data)
```

### Error Handling

```python
from slipperpy.exceptions import GraphQLError, NetworkError, AuthenticationError

try:
    homes = await client.get_homes()
except AuthenticationError:
    print("Authentication failed - please log in")
except NetworkError as e:
    print(f"Network error: {e.message}")
except GraphQLError as e:
    print(f"GraphQL error: {e.message}")
```

### Context Manager

```python
async with SlipperClient("https://api.slipper.no/graphql") as client:
    await client.login_with_phone("+47123456789", "password")
    homes = await client.get_homes()
    # Client is automatically closed when exiting the context
```

## Data Models

The library provides typed Pydantic models for all GraphQL types:

- `HomeType` - Represents a home/property
- `UserType` - Represents a user account
- `ConsumptionType` - Energy consumption data
- `ElectricityPriceType` - Electricity price information
- `PlanType` - Electricity plans/tariffs
- `ProviderType` - Electricity providers
- `DeviceType` - User devices (mobile, web, etc.)
- And many more...

## Development

### Setup

```bash
git clone https://github.com/yourusername/slipperpy.git
cd slipperpy
pip install -e .[dev]
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src tests
isort src tests
```

### Type Checking

```bash
mypy src/slipperpy
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## API Documentation

For complete API documentation, see the [GraphQL schema](src/graphql/schema.graphql) or explore the typed models in the source code.
