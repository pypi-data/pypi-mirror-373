"""Constants for the Llama Search SDK"""

# API Configuration
BASE_URL = "https://llama-search.com"
DEFAULT_TIMEOUT = 300.0
DEFAULT_MAX_RETRIES = 3

# SDK Metadata
SDK_VERSION = "1.0.0"
USER_AGENT = f"llama-search-python/{SDK_VERSION}"

# API Endpoints
ENDPOINTS = {
    "web_search": "/search/web",
    "search_types": "/search/types",
    "usage_stats": "/search/usage-stats",
    "search_history": "/search/history",
    "credit_balance": "/billing/credits",
    "credit_packages": "/billing/packages",
    "create_purchase": "/billing/purchase",
    "payment_status": "/billing/status",
    "purchase_history": "/billing/history",
}
