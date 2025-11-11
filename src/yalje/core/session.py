"""HTTP session management with retry logic."""

import time
from typing import Any, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from yalje.core.config import YaljeConfig
from yalje.core.exceptions import APIError


class HTTPSession:
    """Wrapper around requests.Session with retry logic and rate limiting."""

    def __init__(self, config: YaljeConfig):
        """Initialize HTTP session.

        Args:
            config: Configuration object
        """
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": config.user_agent})
        self._last_request_time = 0.0

    def _rate_limit(self) -> None:
        """Apply rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.config.request_delay:
            time.sleep(self.config.request_delay - elapsed)
        self._last_request_time = time.time()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def get(
        self,
        url: str,
        params: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Make a GET request with retry logic.

        Args:
            url: URL to request
            params: Query parameters
            **kwargs: Additional arguments for requests

        Returns:
            Response object

        Raises:
            APIError: If request fails after retries
        """
        self._rate_limit()

        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.config.request_timeout,
                **kwargs,
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise APIError(f"GET request failed: {url}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def post(
        self,
        url: str,
        data: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Make a POST request with retry logic.

        Args:
            url: URL to request
            data: POST data
            **kwargs: Additional arguments for requests

        Returns:
            Response object

        Raises:
            APIError: If request fails after retries
        """
        self._rate_limit()

        try:
            response = self.session.post(
                url,
                data=data,
                timeout=self.config.request_timeout,
                **kwargs,
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise APIError(f"POST request failed: {url}") from e

    def set_cookies(self, cookies: dict[str, str]) -> None:
        """Set cookies on the session.

        Args:
            cookies: Dictionary of cookie name-value pairs
        """
        for name, value in cookies.items():
            self.session.cookies.set(name, value, domain=".livejournal.com")

    def get_cookie(self, name: str) -> Optional[str]:
        """Get a cookie value by name.

        Args:
            name: Cookie name

        Returns:
            Cookie value or None if not found
        """
        return self.session.cookies.get(name, domain=".livejournal.com")

    def close(self) -> None:
        """Close the session."""
        self.session.close()

    def __enter__(self) -> "HTTPSession":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
