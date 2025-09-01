"""
API Client for making HTTP requests with retries and rate limiting.
"""

import time
import logging
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class APIClient:
    """A reusable API client with retry and rate limiting capabilities."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the API client with configuration.

        Args:
            config: Configuration dictionary with the following keys:
                - base_url: Base URL for the API
                - headers: Dictionary of headers to include in requests
                - retry_attempts: Number of retry attempts
                - timeout: Request timeout in seconds
                - rate_limit: Optional, requests per minute
        """
        self.base_url = config.get("base_url", "")
        self.headers = config.get("headers", {})
        self.retry_attempts = config.get("retry_attempts", 3)
        self.timeout = config.get("timeout", 10)
        self.rate_limit = config.get("rate_limit")
        self.last_request_time = 0

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.retry_attempts,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )

        # Create a session with retry strategy
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
        self.session.mount("http://", HTTPAdapter(max_retries=retry_strategy))

    def _handle_rate_limit(self):
        """Handle rate limiting if rate_limit is set."""
        if self.rate_limit:
            min_interval = (
                60.0 / self.rate_limit
            )  # Minimum time between requests in seconds
            elapsed = time.time() - self.last_request_time
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
        **kwargs,
    ) -> Optional[Dict]:
        """Make an HTTP request with retries and rate limiting.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (appended to base_url)
            params: Query parameters
            json: JSON payload for POST requests
            **kwargs: Additional arguments to pass to requests.request()

        Returns:
            Parsed JSON response or None if the request failed
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        # Handle rate limiting
        self._handle_rate_limit()

        # Set default timeout if not provided
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout

        # Set default headers if not provided
        headers = self.headers.copy()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                headers=headers,
                **kwargs,
            )

            # Update last request time
            self.last_request_time = time.time()

            # Check for successful response
            response.raise_for_status()

            # Return JSON if content exists
            if response.content:
                return response.json()
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            return None


def create_alpha_vantage_client(api_key: str) -> APIClient:
    """Create an API client for Alpha Vantage.

    Args:
        api_key: Alpha Vantage API key

    Returns:
        Configured APIClient instance
    """
    from config.config import APIConfig

    config = {
        "base_url": APIConfig.ALPHA_VANTAGE["base_url"],
        "params": {"apikey": api_key, "datatype": "json"},
        "retry_attempts": APIConfig.ALPHA_VANTAGE["retry_attempts"],
        "timeout": APIConfig.ALPHA_VANTAGE["timeout"],
        "rate_limit": APIConfig.ALPHA_VANTAGE["rate_limit"],
    }

    return APIClient(config)


def create_screener_client() -> APIClient:
    """Create an API client for Screener.in.

    Returns:
        Configured APIClient instance
    """
    from config.config import APIConfig

    config = {
        "base_url": APIConfig.SCREENER["base_url"],
        "headers": APIConfig.SCREENER["headers"],
        "retry_attempts": APIConfig.SCREENER["retry_attempts"],
        "timeout": APIConfig.SCREENER["timeout"],
        "delay_between_requests": APIConfig.SCREENER["delay_between_requests"],
    }

    return APIClient(config)
