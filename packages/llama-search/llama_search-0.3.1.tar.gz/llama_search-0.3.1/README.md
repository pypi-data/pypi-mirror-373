# Llama Search Python SDK

The official Python SDK for the Llama Search AI Platform. This SDK provides a simple, intuitive interface for integrating AI-powered web search capabilities into your applications.

## Installation

```bash
pip install llama-search
```

## Quick Start

### Async Usage (Recommended)

```python
from llama_search import AsyncLlamaSearch

async def main():
    async with AsyncLlamaSearch(api_key="your_api_key_here") as client:
        # Perform a web search
        result = await client.web_search(
            query="Tesla Model 3 battery specifications",
            search_depth="standard"
        )

        print(f"Found {len(result.sources)} sources")
        for source in result.sources:
            print(f"- {source.url}: {source.content[:100]}...")

        # Get available search types
        search_types = await client.get_search_types()
        for search_type in search_types.search_types:
            print(f"{search_type.name}: {search_type.credits} credits")

        # Check account status
        balance = await client.get_credit_balance()
        stats = await client.get_usage_stats()
        print(f"Credits remaining: {balance.balance}")
        print(f"Total searches: {stats.total_searches}")

        # Purchase more credits if needed
        if balance.balance < 50:  # Low credit threshold
            packages = await client.get_credit_packages()
            print("Available credit packages:")
            for package in packages.packages:
                print(f"- {package.name}: {package.credits} credits for {package.price_display}")

        # Get search history
        history = await client.get_search_history(limit=5)
        for search in history.searches:
            print(f"Recent: {search.query} ({search.credits_consumed} credits)")

import asyncio
asyncio.run(main())
```

### Sync Usage

```python
from llama_search import LlamaSearch

with LlamaSearch(api_key="your_api_key_here") as client:
    # Check account status and purchase credits if needed
    balance = client.get_credit_balance()
    stats = client.get_usage_stats()
    print(f"Credits: {balance.balance}, Total searches: {stats.total_searches}")

    # Get available credit packages
    if balance.balance < 20:
        packages = client.get_credit_packages()
        print(f"Low credits! Available packages:")
        for package in packages.packages[:2]:
            print(f"- {package.name}: {package.credits} credits for {package.price_display}")

    # Perform a web search
    result = client.web_search(
        query="Tesla Model 3 battery specifications",
        search_depth="standard"
    )

    print(f"Found {len(result.sources)} sources")
    for source in result.sources:
        print(f"- {source.url}: {source.content[:100]}...")

    # View recent searches and purchases
    history = client.get_search_history(limit=3)
    purchases = client.get_purchase_history(limit=2)
    print(f"Recent searches: {len(history.searches)}")
    print(f"Recent purchases: ${purchases.total_spent_cents / 100:.2f} spent")
```

## API Reference

### Search Methods

#### `web_search(query, search_depth="standard", domain="", with_full_content=False)`

Perform intelligent web search using AI.

**Parameters:**
- `query` (str): The search query to execute
- `search_depth` (str): Search depth level affecting cost and quality
  - `"basic"`: 5 credits, 2 tool calls, low context
  - `"standard"`: 8 credits, 3 tool calls, medium context (default)
  - `"extensive"`: 15 credits, 5 tool calls, high context
- `domain` (str): Optional domain filter (e.g., "reddit.com")
- `with_full_content` (bool): Whether to fetch full content from URLs

**Returns:** `WebSearchResult` containing sources and metadata

#### `get_search_types()`

Get available search types and their costs.

**Returns:** `SearchTypesResponse` containing available search types

### Account Management Methods

#### `get_usage_stats()`

Get current usage statistics for your account.

**Returns:** `UsageStats` containing search counts, credits used/remaining, monthly usage

```python
stats = await client.get_usage_stats()
print(f"Credits remaining: {stats.credits_remaining}")
print(f"Searches this month: {stats.searches_this_month}")
```

#### `get_search_history(limit=10)`

Get your recent search history.

**Parameters:**
- `limit` (int): Maximum number of searches to return (1-100, default: 10)

**Returns:** `SearchHistory` containing list of recent searches

```python
history = await client.get_search_history(limit=20)
for search in history.searches:
    print(f"{search.created_at}: {search.query} ({search.credits_consumed} credits)")
```

#### `get_credit_balance()`

Get current credit balance and purchase history.

**Returns:** `CreditBalance` containing balance, total purchased, last update

```python
balance = await client.get_credit_balance()
print(f"Balance: {balance.balance} credits")
print(f"Total purchased: {balance.total_purchased} credits")
```


## Requirements

- Python 3.10+
- httpx >= 0.24.0
- pydantic >= 2.0.0

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=llama_search
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy llama_search
```

## License

MIT License - see LICENSE file for details.

## Support

- Documentation: https://llama-search.com/docs
- GitHub Issues: https://github.com/llama-search/llama-search/issues
- Email: support@llama-search.com
