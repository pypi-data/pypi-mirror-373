"""Llama Search Python SDK"""

__version__ = "1.0.0"


# Lazy imports to avoid dependency issues during development
def __getattr__(name):
    if name == "AsyncLlamaSearch":
        from .client import AsyncLlamaSearch

        return AsyncLlamaSearch
    elif name == "LlamaSearch":
        from .client import LlamaSearch

        return LlamaSearch
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = ["AsyncLlamaSearch", "LlamaSearch"]
