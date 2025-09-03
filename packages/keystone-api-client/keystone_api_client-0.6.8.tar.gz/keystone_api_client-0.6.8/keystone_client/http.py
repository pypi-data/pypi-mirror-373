"""Lower level HTTP clients with automatic header/cookie handling.

The `http` module provides a lower-level interface for users needing
to perform synchronous and asynchronous HTTP requests against the Keystone
API. It offers streamlined support for common HTTP methods with automatic
URL normalization, session management, and CSRF token handling.
"""

import abc
import atexit
import logging
import re
import uuid
from typing import Literal, Optional, Union
from urllib.parse import urljoin, urlparse

import httpx
from httpx._types import QueryParamTypes, RequestContent, RequestData, RequestFiles

from .log import DefaultContextAdapter

DEFAULT_TIMEOUT = 15
DEFAULT_REDIRECTS = 10
DEFAULT_VERIFY = True
DEFAULT_FOLLOW = True
DEFAULT_LIMITS = httpx.Limits(max_connections=100, max_keepalive_connections=20)

HttpMethod = Literal["get", "post", "put", "patch", "delete"]

logger = logging.getLogger('kclient')


class HTTPBase(abc.ABC):
    """Base HTTP class with shared HTTP constants and helpers."""

    CSRF_COOKIE = "csrftoken"
    CSRF_HEADER = "X-CSRFToken"
    CID_HEADER = "X-KEYSTONE-CID"

    def __init__(
        self,
        base_url: str,
        *,
        verify_ssl: bool = DEFAULT_VERIFY,
        follow_redirects: bool = DEFAULT_FOLLOW,
        max_redirects: int = DEFAULT_REDIRECTS,
        timeout: Optional[int] = DEFAULT_TIMEOUT,
        limits: httpx.Limits = DEFAULT_LIMITS,
        transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        """Initialize a new HTTP session.

        Args:
            base_url: Base URL for all requests.
            verify_ssl: Whether to verify SSL certificates.
            follow_redirects: Whether to follow HTTP redirects.
            max_redirects: Maximum number of redirects to follow.
            limits: Connection pooling limits.
            timeout: Request timeout in seconds.
            transport: Optional custom HTTPX transport.
        """

        self._cid = str(uuid.uuid4())
        self._base_url = self.normalize_url(base_url)
        self._log = DefaultContextAdapter(logger, extra={"cid": self._cid, "baseurl": self._base_url})

        self._client = self._client_factory(
            base_url=self._base_url,
            verify=verify_ssl,
            follow_redirects=follow_redirects,
            max_redirects=max_redirects,
            timeout=timeout,
            limits=limits,
            transport=transport,
        )

        atexit.register(self.close)

    @property
    def base_url(self) -> str:
        """Return the normalized server URL."""

        return self._base_url

    @property
    def cid(self) -> str:
        """Return the current session's correlation ID."""

        return self._cid

    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize a URL with an enforced trailing slash.

        Args:
            url: The URL to normalize.

        Returns:
            A normalized URL with a trailing slash.
        """

        parts = urlparse(url)
        path = re.sub(r"/{2,}", "/", parts.path).rstrip("/") + "/"
        return parts._replace(path=path).geturl()

    def get_application_headers(self, overrides: Union[dict, None] = None) -> dict[str, str]:
        """Return application-specific headers for the current session."""

        headers = {self.CID_HEADER: self._cid}
        if csrf_token := self._client.cookies.get(self.CSRF_COOKIE):
            headers[self.CSRF_HEADER] = csrf_token

        if overrides is not None:
            headers.update(overrides)

        return headers

    @abc.abstractmethod
    def _client_factory(self, **kwargs) -> Union[httpx.Client, httpx.AsyncClient]:
        """Create a new HTTP client instance with the provided settings."""

    @abc.abstractmethod
    def close(self) -> None:
        """Close any open server connections."""

    @abc.abstractmethod
    def send_request(
        self,
        method: HttpMethod,
        endpoint: str,
        *,
        headers: Optional[dict] = None,
        json: Optional[RequestContent] = None,
        files: Optional[RequestFiles] = None,
        params: Optional[QueryParamTypes] = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send an HTTP request (sync or async depending on the implementation)."""

    @abc.abstractmethod
    def http_get(
        self,
        endpoint: str,
        params: Optional[QueryParamTypes] = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send a GET request."""

    @abc.abstractmethod
    def http_post(
        self,
        endpoint: str,
        json: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send a POST request."""

    @abc.abstractmethod
    def http_patch(
        self,
        endpoint: str,
        json: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send a PATCH request."""

    @abc.abstractmethod
    def http_put(
        self,
        endpoint: str,
        json: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send a PUT request."""

    @abc.abstractmethod
    def http_delete(
        self,
        endpoint: str,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send a DELETE request."""


class HTTPClient(HTTPBase):
    """Synchronous HTTP Client."""

    def __enter__(self) -> 'HTTPClient':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def _client_factory(self, **kwargs) -> httpx.Client:
        """Create a new HTTP client instance with the provided settings."""

        self._log.info("Initializing a new HTTP session")
        return httpx.Client(**kwargs)

    def close(self) -> None:
        """Close any open server connections."""

        self._log.info("Closing HTTP session")
        self._client.close()

    def send_request(
        self,
        method: HttpMethod,
        endpoint: str,
        *,
        headers: dict = None,
        json: Optional[RequestContent] = None,
        files: Optional[RequestFiles] = None,
        params: Optional[QueryParamTypes] = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send an HTTP request.

        Args:
            method: The HTTP method to use.
            endpoint: API endpoint relative to the base URL.
            headers: Extends application headers with custom values.
            json: Optional JSON data to include in the request body.
            files: Optional file data to include in the request.
            params: Optional query parameters to include in the request URL.
            timeout: Seconds before the request times out.

        Returns:
            The HTTP response.
        """

        url = self.normalize_url(urljoin(self.base_url, endpoint))
        self._log.info("Sending HTTP request", extra={"method": method, "endpoint": endpoint, "url": url})

        application_headers = self.get_application_headers(headers)
        return self._client.request(
            method=method,
            url=url,
            headers=application_headers,
            json=json,
            files=files,
            params=params,
            timeout=timeout,
        )

    def http_get(
        self,
        endpoint: str,
        params: Optional[QueryParamTypes] = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send a GET request to an API endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            params: Query parameters to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            The HTTP response.
        """

        return self.send_request("get", endpoint, params=params, timeout=timeout)

    def http_post(
        self,
        endpoint: str,
        json: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send a POST request to an API endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            json: JSON data to include in the request body.
            files: File data to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            The HTTP response.
        """

        return self.send_request("post", endpoint, json=json, files=files, timeout=timeout)

    def http_patch(
        self,
        endpoint: str,
        json: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send a PATCH request to an API endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            json: JSON data to include in the request body.
            files: File data to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            The HTTP response.
        """

        return self.send_request("patch", endpoint, json=json, files=files, timeout=timeout)

    def http_put(
        self,
        endpoint: str,
        json: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send a PUT request to an API endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            json: JSON data to include in the request body.
            files: File data to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            The HTTP response.
        """

        return self.send_request("put", endpoint, json=json, files=files, timeout=timeout)

    def http_delete(self, endpoint: str, timeout: int = httpx.USE_CLIENT_DEFAULT) -> httpx.Response:
        """Send a DELETE request to an endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            timeout: Seconds before the request times out.

        Returns:
            The HTTP response.
        """

        return self.send_request("delete", endpoint, timeout=timeout)


class AsyncHTTPClient(HTTPBase):
    """Asynchronous HTTP Client."""

    async def __aenter__(self) -> 'AsyncHTTPClient':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    def _client_factory(self, **kwargs) -> httpx.AsyncClient:
        """Create a new HTTP client instance with the provided settings."""

        self._log.info("Initializing a new asynchronous HTTP session")
        return httpx.AsyncClient(**kwargs)

    async def close(self) -> None:
        """Close any open server connections."""

        self._log.info("Closing asynchronous HTTP session")
        await self._client.aclose()

    async def send_request(
        self,
        method: HttpMethod,
        endpoint: str,
        *,
        headers: dict = None,
        json: Optional[dict] = None,
        files: Optional[RequestFiles] = None,
        params: Optional[QueryParamTypes] = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send an HTTP request.

        Args:
            method: The HTTP method to use.
            endpoint: API endpoint relative to the base URL.
            headers: Extends application headers with custom values.
            json: Optional JSON data to include in the request body.
            files: Optional file data to include in the request.
            params: Optional query parameters to include in the request URL.
            timeout: Seconds before the request times out.

        Returns:
            The awaitable HTTP response.
        """

        url = self.normalize_url(urljoin(self.base_url, endpoint))
        self._log.info("Sending asynchronous HTTP request", extra={"method": method, "endpoint": endpoint, "url": url})

        application_headers = self.get_application_headers(headers)
        return await self._client.request(
            method=method,
            url=url,
            headers=application_headers,
            json=json,
            files=files,
            params=params,
            timeout=timeout
        )

    async def http_get(
        self,
        endpoint: str,
        params: Optional[QueryParamTypes] = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send an asynchronous GET request to an API endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            params: Query parameters to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            The awaitable HTTP response.
        """

        return await self.send_request("get", endpoint, params=params, timeout=timeout)

    async def http_post(
        self,
        endpoint: str,
        json: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send an asynchronous POST request to an API endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            json: JSON data to include in the request body.
            files: File data to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            The awaitable HTTP response.
        """

        return await self.send_request("post", endpoint, json=json, files=files, timeout=timeout)

    async def http_patch(
        self,
        endpoint: str,
        json: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send an asynchronous PATCH request to an API endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            json: JSON data to include in the request body.
            files: File data to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            The awaitable HTTP response.
        """

        return await self.send_request("patch", endpoint, json=json, files=files, timeout=timeout)

    async def http_put(
        self,
        endpoint: str,
        json: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        timeout: int = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        """Send an asynchronous PUT request to an API endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            json: JSON data to include in the request body.
            files: File data to include in the request.
            timeout: Seconds before the request times out.

        Returns:
            The awaitable HTTP response.
        """

        return await self.send_request("put", endpoint, json=json, files=files, timeout=timeout)

    async def http_delete(self, endpoint: str, timeout: int = httpx.USE_CLIENT_DEFAULT) -> httpx.Response:
        """Send an asynchronous DELETE request to an endpoint.

        Args:
            endpoint: API endpoint relative to the base URL.
            timeout: Seconds before the request times out.

        Returns:
            The awaitable HTTP response.
        """

        return await self.send_request("delete", endpoint, timeout=timeout)
