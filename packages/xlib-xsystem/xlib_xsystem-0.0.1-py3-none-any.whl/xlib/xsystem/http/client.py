"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025

HTTP client with retry mechanisms, connection pooling, and error handling.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    # Define dummy classes for type hints when httpx is not available
    class httpx:
        class ConnectError(Exception):
            pass
        class TimeoutException(Exception):
            pass
        class Response:
            pass
        class Client:
            pass
        class AsyncClient:
            pass
        class Limits:
            pass

from ..config.logging_setup import get_logger
from ..monitoring.error_recovery import retry_with_backoff

logger = get_logger("xsystem.http.client")


class HttpError(Exception):
    """Base exception for HTTP client errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Any] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


@dataclass
class RetryConfig:
    """Configuration for HTTP request retries."""
    
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    retry_on_status: List[int] = field(default_factory=lambda: [500, 502, 503, 504, 429])
    retry_on_exceptions: List[type] = field(default_factory=lambda: [httpx.ConnectError, httpx.TimeoutException])


class HttpClient:
    """
    High-performance HTTP client with retry mechanisms, connection pooling,
    and comprehensive error handling.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        retry_config: Optional[RetryConfig] = None,
        default_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initialize HTTP client.

        Args:
            base_url: Base URL for all requests
            timeout: Request timeout in seconds
            max_connections: Maximum number of connections
            max_keepalive_connections: Maximum keepalive connections
            retry_config: Retry configuration
            default_headers: Default headers for all requests
        """
        if not HTTPX_AVAILABLE:
            raise HttpError("httpx is required for HTTP client. Install with: pip install httpx")
            
        self.base_url = base_url
        self.retry_config = retry_config or RetryConfig()
        self.default_headers = default_headers or {}
        
        # Configure httpx client
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections
        )
        
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            limits=limits,
            headers=self.default_headers
        )
        
        self._async_client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            limits=limits,
            headers=self.default_headers
        )

    def __enter__(self) -> 'HttpClient':
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the HTTP client and cleanup connections."""
        try:
            self._client.close()
            if hasattr(self._async_client, 'aclose'):
                # Handle async client cleanup
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        loop.create_task(self._async_client.aclose())
                    else:
                        loop.run_until_complete(self._async_client.aclose())
                except RuntimeError:
                    # No event loop available
                    pass
        except Exception as e:
            logger.warning(f"Error closing HTTP client: {e}")

    def _should_retry(self, response: Optional[httpx.Response], exception: Optional[Exception]) -> bool:
        """Determine if a request should be retried."""
        if exception:
            return any(isinstance(exception, exc_type) for exc_type in self.retry_config.retry_on_exceptions)
        
        if response:
            return response.status_code in self.retry_config.retry_on_status
            
        return False

    def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Any] = None,
        data: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """Make HTTP request with retry logic."""
        
        # Combine headers
        request_headers = {**self.default_headers}
        if headers:
            request_headers.update(headers)

        # Prepare request arguments
        request_kwargs = {
            'method': method,
            'url': url,
            'headers': request_headers,
            'params': params,
            'files': files,
        }
        
        if json_data is not None:
            request_kwargs['json'] = json_data
        elif data is not None:
            request_kwargs['data'] = data

        @retry_with_backoff(
            max_retries=self.retry_config.max_retries,
            base_delay=self.retry_config.base_delay,
            max_delay=self.retry_config.max_delay,
            exponential_base=self.retry_config.exponential_base
        )
        def _request() -> httpx.Response:
            try:
                response = self._client.request(**request_kwargs)
                
                if self._should_retry(response, None):
                    raise HttpError(
                        f"HTTP {response.status_code}: {response.text}",
                        status_code=response.status_code,
                        response_data=response.text
                    )
                
                return response
                
            except Exception as e:
                if self._should_retry(None, e):
                    raise HttpError(f"Request failed: {e}") from e
                raise

        return _request()

    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """Make GET request."""
        return self._make_request('GET', url, headers=headers, params=params)

    def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Any] = None,
        data: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """Make POST request."""
        return self._make_request(
            'POST', url, headers=headers, params=params,
            json_data=json_data, data=data, files=files
        )

    def put(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Any] = None,
        data: Optional[Any] = None,
    ) -> httpx.Response:
        """Make PUT request."""
        return self._make_request(
            'PUT', url, headers=headers, params=params,
            json_data=json_data, data=data
        )

    def patch(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Any] = None,
        data: Optional[Any] = None,
    ) -> httpx.Response:
        """Make PATCH request."""
        return self._make_request(
            'PATCH', url, headers=headers, params=params,
            json_data=json_data, data=data
        )

    def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """Make DELETE request."""
        return self._make_request('DELETE', url, headers=headers, params=params)

    def head(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """Make HEAD request."""
        return self._make_request('HEAD', url, headers=headers, params=params)

    def options(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """Make OPTIONS request."""
        return self._make_request('OPTIONS', url, headers=headers, params=params)

    # Convenience methods for JSON responses
    def get_json(self, url: str, **kwargs: Any) -> Any:
        """GET request returning JSON data."""
        response = self.get(url, **kwargs)
        try:
            return response.json()
        except Exception as e:
            raise HttpError(f"Failed to parse JSON response: {e}") from e

    def post_json(self, url: str, **kwargs: Any) -> Any:
        """POST request returning JSON data."""
        response = self.post(url, **kwargs)
        try:
            return response.json()
        except Exception as e:
            raise HttpError(f"Failed to parse JSON response: {e}") from e

    # Health check methods
    def health_check(self, endpoint: str = "/health") -> bool:
        """Perform health check on the service."""
        try:
            response = self.get(endpoint)
            return 200 <= response.status_code < 300
        except Exception:
            return False

    def ping(self, endpoint: str = "/ping") -> float:
        """Ping the service and return response time in seconds."""
        start_time = time.perf_counter()
        try:
            self.get(endpoint)
            return time.perf_counter() - start_time
        except Exception as e:
            raise HttpError(f"Ping failed: {e}") from e


# Async HTTP Client (if needed in the future)
class AsyncHttpClient:
    """Async version of HTTP client for high-concurrency scenarios."""
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize async HTTP client with same options as sync client."""
        if not HTTPX_AVAILABLE:
            raise HttpError("httpx is required for HTTP client. Install with: pip install httpx")
        # Implementation would mirror HttpClient but with async/await
        # Left as placeholder for future enhancement
        pass


# Convenience functions
def get(url: str, **kwargs: Any) -> httpx.Response:
    """Quick GET request with default client."""
    with HttpClient() as client:
        return client.get(url, **kwargs)


def post(url: str, **kwargs: Any) -> httpx.Response:
    """Quick POST request with default client."""
    with HttpClient() as client:
        return client.post(url, **kwargs)


def get_json(url: str, **kwargs: Any) -> Any:
    """Quick GET request returning JSON."""
    with HttpClient() as client:
        return client.get_json(url, **kwargs)
