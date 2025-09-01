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

        # Check account usage
        stats = await client.get_usage_stats()
        print(f"Credits remaining: {stats.credits_remaining}")
        print(f"Total searches: {stats.total_searches}")

import asyncio
asyncio.run(main())
```

### Sync Usage

```python
from llama_search import LlamaSearch

with LlamaSearch(api_key="your_api_key_here") as client:
    # Perform a web search
    result = client.web_search(
        query="Tesla Model 3 battery specifications",
        search_depth="standard"
    )

    print(f"Found {len(result.sources)} sources")
    for source in result.sources:
        print(f"- {source.url}: {source.content[:100]}...")

    # Check account usage
    stats = client.get_usage_stats()
    print(f"Credits remaining: {stats.credits_remaining}")
    print(f"Total searches: {stats.total_searches}")
```

## API Reference

### Core Search Methods

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

```python
result = await client.web_search("Python asyncio best practices", search_depth="extensive")
print(f"Credits consumed: {result.credits_consumed}")
```

#### `get_search_types()`

Get available search types and their costs.

**Returns:** `SearchTypesResponse` containing available search types

```python
types = await client.get_search_types()
for search_type in types.search_types:
    print(f"{search_type.name}: {search_type.credits} credits")
```

### Account Management

#### `get_usage_stats()`

Get current usage statistics for your account.

**Returns:** `UsageStats` containing search counts, credits used/remaining, monthly usage

```python
stats = await client.get_usage_stats()
print(f"Credits remaining: {stats.credits_remaining}")
print(f"Searches this month: {stats.searches_this_month}")
print(f"Total searches: {stats.total_searches}")
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

### Billing Information

#### `get_credit_packages()`

Get available credit packages for purchase.

**Returns:** `CreditPackagesResponse` containing available packages

```python
packages = await client.get_credit_packages()
for package in packages.packages:
    print(f"{package.name}: {package.credits} credits for {package.price_display}")
```

#### `get_purchase_history(limit=10)`

Get your credit purchase history.

**Parameters:**
- `limit` (int): Maximum number of purchases to return (1-50, default: 10)

**Returns:** `PurchaseHistory` containing purchase records and totals

```python
history = await client.get_purchase_history()
print(f"Total spent: ${history.total_spent_cents / 100:.2f}")
for purchase in history.purchases:
    print(f"{purchase.created_at}: {purchase.package_name} - {purchase.credits} credits")
```

## Error Handling

The SDK provides specific exceptions for different error scenarios:

```python
from llama_search._exceptions import (
    InsufficientCreditsError,
    ValidationError,
    AuthenticationError,
    RateLimitError
)

try:
    result = await client.web_search("example query")
except InsufficientCreditsError as e:
    print(f"Need {e.credits_required} credits, have {e.credits_available}")
except ValidationError as e:
    print(f"Invalid request: {e}")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after} seconds")
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
make test

# Run tests with coverage
pytest --cov=llama_search
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type checking
make typecheck
```

## License

MIT License - see LICENSE file for details.

## Support

- Documentation: https://llama-search.com/docs
- GitHub Issues: https://github.com/llama-search/llama-search/issues
- Email: support@llama-search.com
