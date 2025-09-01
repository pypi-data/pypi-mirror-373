"""Main client classes for the Llama Search SDK"""

import asyncio
import os
import time
from typing import Dict, Literal, Optional

import httpx

from ._constants import BASE_URL, DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT, ENDPOINTS, USER_AGENT
from ._exceptions import (
    AuthenticationError,
    InsufficientCreditsError,
    LlamaSearchError,
    NetworkError,
    PaymentCancelledError,
    PaymentError,
    PaymentFailedError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
)
from ._retry import RetryManager, RetryConfig, create_default_retry_manager
from ._logging import RequestLogger, setup_logging
from .types.search import SearchTypesResponse, WebSearchResult
from .types.account import UsageStats, SearchHistory
from .types.billing import CreditPackagesResponse, PurchaseHistory


class AsyncLlamaSearch:
    """Asynchronous client for Llama Search API"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Optional[Dict[str, str]] = None,
        debug: bool = False,
        retry_config: Optional[RetryConfig] = None,
    ):
        """
        Initialize the async Llama Search client.

        Args:
            api_key: Your Llama Search API key (if not provided, will look for LLAMA_SEARCH_API_KEY env var)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts (used if retry_config not provided)
            default_headers: Additional headers to include in all requests
            debug: Enable debug logging
            retry_config: Custom retry configuration
        """
        # Auto-load API key from environment if not provided
        if api_key is None:
            api_key = os.getenv("LLAMA_SEARCH_API_KEY")

        if not api_key:
            raise ValueError(
                "API key is required. Provide it as a parameter or set LLAMA_SEARCH_API_KEY environment variable."
            )

        self._api_key = api_key
        self._base_url = BASE_URL
        self._timeout = timeout
        self._debug = debug
        self._default_headers = default_headers or {}

        # Setup logging
        if debug:
            setup_logging(level="DEBUG", enable_debug=True)
        self._request_logger = RequestLogger(debug=debug)

        # Setup retry manager
        if retry_config:
            self._retry_manager: Optional[RetryManager] = RetryManager(retry_config)
        else:
            # Use default retry manager with custom max_retries
            default_manager = create_default_retry_manager()
            default_manager.retry_config.max_retries = max_retries
            self._retry_manager = default_manager

        # HTTP client setup
        headers = {
            "Authorization": f"Bearer {api_key}",
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
            **self._default_headers,
        }

        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers=headers,
            base_url=self._base_url,
        )

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def close(self):
        """Close the HTTP client"""
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> httpx.Response:
        """Make HTTP request with advanced retry logic and error handling"""

        if self._retry_manager:
            return await self._retry_manager.execute_with_retry(  # type: ignore
                self._make_single_request, method, endpoint, **kwargs
            )
        else:
            return await self._make_single_request(method, endpoint, **kwargs)

    async def _make_single_request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> httpx.Response:
        """Make a single HTTP request with error handling"""

        start_time = time.time()
        request_id = None

        try:
            # Log request
            full_url = f"{self._base_url}{endpoint}"
            request_id = self._request_logger.log_request(
                method=method,
                url=full_url,
                headers=dict(self._client.headers),
                body=kwargs.get("json"),
            )

            # Make the request
            response = await self._client.request(method, endpoint, **kwargs)
            duration_ms = int((time.time() - start_time) * 1000)

            # Log response
            self._request_logger.log_response(request_id, response, duration_ms)

            # Handle HTTP errors
            self._handle_http_errors(response)

            return response

        except httpx.TimeoutException:
            duration_ms = int((time.time() - start_time) * 1000)
            timeout_error = TimeoutError(
                message=f"Request timed out after {self._timeout}s",
                timeout_duration=self._timeout,
            )
            if request_id:
                self._request_logger.log_error(request_id, timeout_error, duration_ms)
            raise timeout_error

        except httpx.RequestError as e:
            duration_ms = int((time.time() - start_time) * 1000)
            network_error = NetworkError(
                message=f"Connection error: {str(e)}",
                original_error=e,
            )
            if request_id:
                self._request_logger.log_error(request_id, network_error, duration_ms)
            raise network_error

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            if request_id:
                self._request_logger.log_error(request_id, e, duration_ms)
            raise

    def _handle_http_errors(self, response: httpx.Response):
        """Handle HTTP error status codes"""

        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")

        elif response.status_code == 402:
            try:
                error_data = response.json()
                # Handle payment-specific 402 errors
                if "payment" in error_data.get("error_type", "").lower():
                    if "cancelled" in error_data.get("message", "").lower():
                        raise PaymentCancelledError(
                            error_data.get("message", "Payment was cancelled"),
                            session_id=error_data.get("session_id"),
                        )
                    elif "failed" in error_data.get("message", "").lower():
                        raise PaymentFailedError(
                            error_data.get("message", "Payment failed"),
                            session_id=error_data.get("session_id"),
                            failure_reason=error_data.get("failure_reason"),
                        )
                    else:
                        raise PaymentError(
                            error_data.get("message", "Payment error"),
                            session_id=error_data.get("session_id"),
                        )
                else:
                    # Standard insufficient credits error
                    raise InsufficientCreditsError(
                        error_data.get("message", "Insufficient credits"),
                        credits_required=error_data.get("credits_required"),
                        credits_available=error_data.get("credits_available"),
                    )
            except ValueError:
                raise InsufficientCreditsError("Insufficient credits")

        elif response.status_code == 422:
            try:
                error_data = response.json()
                detail = error_data.get("detail", "Validation error")
                if isinstance(detail, list) and len(detail) > 0:
                    field = detail[0].get("loc", [])[-1] if detail[0].get("loc") else None
                    message = detail[0].get("msg", "Validation error")
                    raise ValidationError(message, field=field)
                raise ValidationError(str(detail))
            except ValueError:
                raise ValidationError("Invalid request parameters")

        elif response.status_code == 429:
            retry_after = None
            if "retry-after" in response.headers:
                try:
                    retry_after = int(response.headers["retry-after"])
                except ValueError:
                    pass

            raise RateLimitError(
                message="Rate limit exceeded",
                retry_after=retry_after,
            )

        elif response.status_code >= 500:
            raise ServerError(
                message=f"Server error: {response.status_code}",
                status_code=response.status_code,
            )

        elif response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("message", f"HTTP {response.status_code} error")
                raise LlamaSearchError(message)
            except ValueError:
                raise LlamaSearchError(f"HTTP {response.status_code} error")

    async def web_search(
        self,
        query: str,
        search_depth: Literal["basic", "standard", "extensive"] = "standard",
        domain: str = "",
        with_full_content: bool = False,
    ) -> WebSearchResult:
        """
        Perform intelligent web search using AI.

        Args:
            query: The search query to execute
            search_depth: Search depth level affecting cost and quality
                - "basic": 5 credits, 2 tool calls, low context
                - "standard": 8 credits, 3 tool calls, medium context
                - "extensive": 15 credits, 5 tool calls, high context
            domain: Optional domain filter (e.g., "reddit.com")
            with_full_content: Whether to fetch full content from URLs

        Returns:
            WebSearchResult containing sources and metadata

        Raises:
            InsufficientCreditsError: When account lacks required credits
            ValidationError: When query parameters are invalid
            AuthenticationError: When API key is invalid

        Example:
            >>> result = await client.web_search("Tesla Model 3 specs")
            >>> print(f"Found {len(result.sources)} sources")
            >>> for source in result.sources:
            ...     print(f"- {source.url}: {source.content[:100]}...")
        """
        if not query or not query.strip():
            raise ValidationError("Query cannot be empty")

        if len(query.strip()) > 500:
            raise ValidationError("Query too long (max 500 characters)")

        request_data = {
            "query": query.strip(),
            "search_depth": search_depth,
            "domain": domain,
            "with_full_content": with_full_content,
        }

        response = await self._request("POST", ENDPOINTS["web_search"], json=request_data)

        try:
            data = response.json()
            return WebSearchResult.model_validate(data)
        except Exception as e:
            raise LlamaSearchError(f"Failed to parse response: {str(e)}")

    async def get_search_types(self) -> SearchTypesResponse:
        """
        Get available search types and their costs.

        Returns:
            SearchTypesResponse containing available search types

        Example:
            >>> types = await client.get_search_types()
            >>> for search_type in types.search_types:
            ...     print(f"{search_type.name}: {search_type.credits} credits")
        """
        response = await self._request("GET", ENDPOINTS["search_types"])

        try:
            data = response.json()
            return SearchTypesResponse.model_validate(data)
        except Exception as e:
            raise LlamaSearchError(f"Failed to parse response: {str(e)}")

    async def get_usage_stats(self) -> UsageStats:
        """
        Get current usage statistics for the authenticated user.

        Returns:
            UsageStats containing search counts, credits used/remaining, etc.

        Example:
            >>> stats = await client.get_usage_stats()
            >>> print(f"Credits remaining: {stats.credits_remaining}")
            >>> print(f"Searches this month: {stats.searches_this_month}")
        """
        response = await self._request("GET", ENDPOINTS["usage_stats"])

        try:
            data = response.json()
            return UsageStats.model_validate(data)
        except Exception as e:
            raise LlamaSearchError(f"Failed to parse response: {str(e)}")

    async def get_search_history(self, limit: int = 10) -> SearchHistory:
        """
        Get search history for the authenticated user.

        Args:
            limit: Maximum number of search history items to return (default: 10)

        Returns:
            SearchHistory containing list of recent searches

        Raises:
            ValidationError: When limit is invalid

        Example:
            >>> history = await client.get_search_history(limit=20)
            >>> for search in history.searches:
            ...     print(f"{search.created_at}: {search.query} ({search.credits_consumed} credits)")
        """
        if limit <= 0:
            raise ValidationError("Limit must be greater than 0")
        if limit > 100:
            raise ValidationError("Limit cannot exceed 100")

        params = {"limit": limit}
        response = await self._request("GET", ENDPOINTS["search_history"], params=params)

        try:
            data = response.json()
            return SearchHistory.model_validate(data)
        except Exception as e:
            raise LlamaSearchError(f"Failed to parse response: {str(e)}")

    async def get_credit_packages(self) -> CreditPackagesResponse:
        """
        Get available credit packages for purchase.

        Returns:
            CreditPackagesResponse containing available credit packages

        Example:
            >>> packages = await client.get_credit_packages()
            >>> for package in packages.packages:
            ...     print(f"{package.name}: {package.credits} credits for {package.price_display}")
        """
        response = await self._request("GET", ENDPOINTS["credit_packages"])

        try:
            data = response.json()
            return CreditPackagesResponse.model_validate(data)
        except Exception as e:
            raise LlamaSearchError(f"Failed to parse response: {str(e)}")

    async def get_purchase_history(self, limit: int = 10) -> PurchaseHistory:
        """
        Get credit purchase history for the authenticated user.

        Args:
            limit: Maximum number of purchase records to return (default: 10, max: 50)

        Returns:
            PurchaseHistory containing list of purchases and totals

        Raises:
            ValidationError: When limit is invalid

        Example:
            >>> history = await client.get_purchase_history(limit=20)
            >>> print(f"Total spent: ${history.total_spent_cents / 100:.2f}")
            >>> print(f"Total credits purchased: {history.total_credits_purchased}")
            >>> for purchase in history.purchases:
            ...     print(f"{purchase.created_at}: {purchase.package_name} - {purchase.credits} credits")
        """
        if limit <= 0:
            raise ValidationError("Limit must be greater than 0", field="limit")
        if limit > 50:
            raise ValidationError("Limit cannot exceed 50", field="limit")

        params = {"limit": limit}
        response = await self._request("GET", ENDPOINTS["purchase_history"], params=params)

        try:
            data = response.json()
            return PurchaseHistory.model_validate(data)
        except Exception as e:
            raise LlamaSearchError(f"Failed to parse response: {str(e)}")


class LlamaSearch:
    """Synchronous client for Llama Search API"""

    def __init__(self, **kwargs):
        """
        Initialize the sync Llama Search client.

        Args:
            **kwargs: Same arguments as AsyncLlamaSearch
        """
        self._async_client = AsyncLlamaSearch(**kwargs)

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    def close(self):
        """Close the underlying async client"""
        asyncio.run(self._async_client.close())

    def web_search(
        self,
        query: str,
        search_depth: Literal["basic", "standard", "extensive"] = "standard",
        domain: str = "",
        with_full_content: bool = False,
    ) -> WebSearchResult:
        """
        Synchronous version of web_search.

        See AsyncLlamaSearch.web_search for full documentation.
        """
        return asyncio.run(
            self._async_client.web_search(
                query=query,
                search_depth=search_depth,
                domain=domain,
                with_full_content=with_full_content,
            )
        )

    def get_search_types(self) -> SearchTypesResponse:
        """
        Synchronous version of get_search_types.

        See AsyncLlamaSearch.get_search_types for full documentation.
        """
        return asyncio.run(self._async_client.get_search_types())

    def get_usage_stats(self) -> UsageStats:
        """
        Synchronous version of get_usage_stats.

        See AsyncLlamaSearch.get_usage_stats for full documentation.
        """
        return asyncio.run(self._async_client.get_usage_stats())

    def get_search_history(self, limit: int = 10) -> SearchHistory:
        """
        Synchronous version of get_search_history.

        Args:
            limit: Maximum number of search history items to return (default: 10)

        See AsyncLlamaSearch.get_search_history for full documentation.
        """
        return asyncio.run(self._async_client.get_search_history(limit=limit))

    def get_credit_packages(self) -> CreditPackagesResponse:
        """
        Synchronous version of get_credit_packages.

        See AsyncLlamaSearch.get_credit_packages for full documentation.
        """
        return asyncio.run(self._async_client.get_credit_packages())

    def get_purchase_history(self, limit: int = 10) -> PurchaseHistory:
        """
        Synchronous version of get_purchase_history.

        Args:
            limit: Maximum number of purchase records to return (default: 10, max: 50)

        See AsyncLlamaSearch.get_purchase_history for full documentation.
        """
        return asyncio.run(self._async_client.get_purchase_history(limit))
