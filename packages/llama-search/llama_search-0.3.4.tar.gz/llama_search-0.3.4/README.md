# Llama Search Python SDK

The official Python SDK for the Llama Search AI Platform. This SDK provides a simple, intuitive interface for integrating AI-powered web search capabilities into your applications.

## Installation

```bash
pip install llama-search
```

## Quick Start

First, set your API key as an environment variable:
```bash
export LLAMA_SEARCH_API_KEY="your_api_key_here"
```

Or create a `.env` file:
```
LLAMA_SEARCH_API_KEY=your_api_key_here
```

### Async Usage (Recommended)

```python
from llama_search import AsyncLlamaSearch

async def main():
    # API key loaded from LLAMA_SEARCH_API_KEY environment variable
    async with AsyncLlamaSearch() as client:
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

with LlamaSearch() as client:
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
