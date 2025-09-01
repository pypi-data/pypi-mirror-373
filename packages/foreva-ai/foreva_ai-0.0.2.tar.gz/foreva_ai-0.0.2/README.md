# Foreva AI Partner SDK

The official Python SDK for Foreva AI partners. Add voice AI to restaurants with just a few lines of code.

## Installation

```bash
pip install foreva-ai
```

## Quick Start

```python
from foreva_ai import ForevaAgent, MenuBuilder

# Create agent (get API key from partner dashboard)
agent = ForevaAgent("YOUR_API_KEY", "+14155551234")

# Configure restaurant
agent.set_store(
    name="Restaurant Name",
    address="123 Main St, City, State 12345",
    timezone="America/Los_Angeles"
)

# Set menu
menu = (MenuBuilder()
    .add_category(1, "Main Dishes")
    .add_item(101, "Pasta Special", 15.99, 1)
    .build())
agent.set_menu(menu)

# Activate
result = agent.activate()
print(f"Forward calls to: {result['data']['routing_number']}")
```

## Test vs Live Mode

- **Test Mode**: `foreva_test_xxx...` - Free for development
- **Live Mode**: `foreva_live_xxx...` - Requires subscription

## Documentation

Complete documentation and examples:
**https://foreva.ai/partners/docs**

## Support

- **Email**: support@foreva.ai
- **Dashboard**: https://foreva.ai/partners/dashboard
- **Support Portal**: https://foreva.ai/partners/support

## License

This SDK is proprietary software for authorized Foreva AI partners only.
