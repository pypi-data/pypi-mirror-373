"""Logging and debugging utilities for the Llama Search SDK"""

import json
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

import httpx

# Create SDK logger
logger = logging.getLogger("llama_search")


class RequestLogger:
    """Handles request/response logging and debugging"""

    def __init__(self, debug: bool = False, sensitive_headers: Optional[set] = None):
        self.debug = debug
        self.sensitive_headers = sensitive_headers or {"authorization", "x-api-key"}
        self.logger = logger

    def log_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        body: Optional[Dict[str, Any]] = None,
        attempt: int = 1,
    ) -> str:
        """Log outgoing request details"""

        request_id = f"req_{int(time.time() * 1000)}"

        # Sanitize headers
        safe_headers = self._sanitize_headers(headers)

        if self.debug:
            log_data = {
                "request_id": request_id,
                "attempt": attempt,
                "method": method,
                "url": url,
                "headers": safe_headers,
                "body": body,
                "timestamp": datetime.now().isoformat(),
            }
            self.logger.debug(f"Request: {json.dumps(log_data, indent=2)}")
        else:
            self.logger.info(f"Request [{request_id}] {method} {url} (attempt {attempt})")

        return request_id

    def log_response(
        self,
        request_id: str,
        response: httpx.Response,
        duration_ms: int,
        attempt: int = 1,
    ):
        """Log response details"""

        status_emoji = "✅" if 200 <= response.status_code < 300 else "❌"

        if self.debug:
            try:
                response_body = response.json() if response.content else None
                # Sanitize sensitive data in response
                if response_body and isinstance(response_body, dict):
                    response_body = self._sanitize_response_body(response_body)
            except Exception:
                response_body = response.text[:200] if response.content else None

            log_data = {
                "request_id": request_id,
                "attempt": attempt,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response_body,
                "duration_ms": duration_ms,
                "timestamp": datetime.now().isoformat(),
            }
            self.logger.debug(f"Response: {json.dumps(log_data, indent=2)}")
        else:
            self.logger.info(
                f"Response [{request_id}] {status_emoji} {response.status_code} "
                f"({duration_ms}ms, attempt {attempt})"
            )

    def log_error(
        self,
        request_id: str,
        error: Exception,
        duration_ms: int,
        attempt: int = 1,
    ):
        """Log error details"""

        error_data = {
            "request_id": request_id,
            "attempt": attempt,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "duration_ms": duration_ms,
            "timestamp": datetime.now().isoformat(),
        }

        if hasattr(error, "error_code"):
            error_data["error_code"] = error.error_code

        if self.debug:
            self.logger.debug(f"Error: {json.dumps(error_data, indent=2)}")
        else:
            self.logger.warning(
                f"Error [{request_id}] {type(error).__name__}: {error} "
                f"({duration_ms}ms, attempt {attempt})"
            )

    def log_retry(
        self,
        request_id: str,
        attempt: int,
        error: Exception,
        delay: float,
    ):
        """Log retry attempt"""

        self.logger.info(
            f"Retry [{request_id}] Attempt {attempt} failed with {type(error).__name__}: {error}. "
            f"Retrying in {delay:.2f}s"
        )

    def log_circuit_breaker(
        self,
        action: str,
        failure_count: Optional[int] = None,
        next_attempt_time: Optional[datetime] = None,
    ):
        """Log circuit breaker events"""

        if action == "opened":
            self.logger.warning(
                f"Circuit breaker opened after {failure_count} failures. "
                f"Next attempt allowed at {next_attempt_time}"
            )
        elif action == "closed":
            self.logger.info("Circuit breaker closed - service recovered")
        elif action == "half_open":
            self.logger.info("Circuit breaker half-open - testing service")
        elif action == "rejected":
            self.logger.warning(
                f"Request rejected by circuit breaker. Next attempt at {next_attempt_time}"
            )

    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Remove sensitive information from headers"""
        safe_headers = {}
        for key, value in headers.items():
            if key.lower() in self.sensitive_headers:
                safe_headers[key] = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                safe_headers[key] = value
        return safe_headers

    def _sanitize_response_body(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from response body"""
        # Create a copy to avoid modifying original
        sanitized = body.copy()

        # Remove or mask sensitive fields
        sensitive_fields = {"api_key", "token", "secret", "password", "key"}
        for field in sensitive_fields:
            if field in sanitized:
                if isinstance(sanitized[field], str) and len(sanitized[field]) > 8:
                    sanitized[field] = f"{sanitized[field][:4]}...{sanitized[field][-4:]}"
                else:
                    sanitized[field] = "***"

        return sanitized


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    enable_debug: bool = False,
) -> logging.Logger:
    """Setup logging configuration for the SDK"""

    # Default format
    if not format_string:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            if not enable_debug
            else "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )

    # Configure the SDK logger
    sdk_logger = logging.getLogger("llama_search")

    # Don't add handlers if they already exist
    if not sdk_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)
        sdk_logger.addHandler(handler)

    # Set level
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    sdk_logger.setLevel(level_map.get(level.upper(), logging.INFO))

    # Prevent propagation to root logger to avoid duplicate messages
    sdk_logger.propagate = False

    return sdk_logger


def get_performance_metrics() -> Dict[str, Any]:
    """Get basic performance metrics"""
    import psutil
    import sys

    return {
        "memory_usage_mb": psutil.Process().memory_info().rss / 1024 / 1024,
        "cpu_percent": psutil.Process().cpu_percent(),
        "python_version": sys.version,
        "active_connections": len(psutil.net_connections()),
    }
