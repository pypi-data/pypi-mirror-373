"""HTTP client implementation for the Tora SDK.

This module provides a simple HTTP client that wraps the standard library
http.client with a more convenient interface similar to requests.
"""

import http.client
import json as _json
import socket
import ssl
from typing import Any
from urllib.parse import urlparse

from ._exceptions import HTTPStatusError, ToraNetworkError, ToraTimeoutError


class HttpResponse:
    """A wrapper for http.client.HTTPResponse with enhanced error handling."""

    def __init__(self, raw_response: http.client.HTTPResponse, data: bytes, url: str) -> None:
        self._raw_response = raw_response
        self.status_code = raw_response.status
        self.reason = raw_response.reason
        self.headers = dict(raw_response.getheaders())
        self._url = url
        self._data = data
        self._text: str | None = None
        self._json: Any | None = None

    @property
    def text(self) -> str:
        """Returns the text content of the response."""
        if self._text is None:
            try:
                content_type = self.headers.get("content-type", "")
                encoding = "utf-8"

                if "charset=" in content_type:
                    encoding = content_type.split("charset=")[1].split(";")[0].strip()

                self._text = self._data.decode(encoding)
            except UnicodeDecodeError:
                self._text = self._data.decode("utf-8", errors="replace")

        return self._text

    def json(self) -> Any:
        """Return the JSON-decoded content of the response."""
        if self._json is None:
            try:
                self._json = _json.loads(self.text)
            except _json.JSONDecodeError as e:
                raise ToraNetworkError(
                    f"Failed to decode JSON response: {e}",
                    status_code=self.status_code,
                    response_text=self.text[:500] + "..." if len(self.text) > 500 else self.text,
                ) from e
        return self._json

    def raise_for_status(self) -> None:
        """Raise appropriate exception for 4xx and 5xx responses."""
        if 400 <= self.status_code < 600:
            error_msg = f"HTTP {self.status_code} {self.reason} for url '{self._url}'"

            try:
                if self.headers.get("content-type", "").startswith("application/json"):
                    _ = self.json()
            except Exception:
                pass

            raise HTTPStatusError(
                message=error_msg,
                response=self,
            )


class HttpClient:
    """A simple HTTP client that wraps http.client with enhanced error handling.

    Provides an interface similar to requests or httpx with better error handling,
    timeout support, and connection management.
    """

    def __init__(
        self,
        base_url: str,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> None:
        parsed_url = urlparse(base_url)

        if not parsed_url.scheme or not parsed_url.netloc:
            raise ToraNetworkError(f"Invalid base URL: {base_url}")

        self.scheme = parsed_url.scheme
        self.netloc = parsed_url.netloc
        self.base_path = parsed_url.path.rstrip("/")
        self.timeout = timeout or 30

        self.conn_class: type[http.client.HTTPConnection | http.client.HTTPSConnection]
        if self.scheme == "https":
            self.conn_class = http.client.HTTPSConnection
        elif self.scheme == "http":
            self.conn_class = http.client.HTTPConnection
        else:
            raise ToraNetworkError(f"Unsupported URL scheme: {self.scheme}")

        self.headers = headers or {}
        self.conn: http.client.HTTPConnection | None = None

    def _get_conn(self, timeout: int | None = None) -> http.client.HTTPConnection:
        """Get or create a connection with proper error handling."""
        if self.conn:
            return self.conn

        conn_timeout = timeout or self.timeout

        try:
            return self.conn_class(self.netloc, timeout=conn_timeout)
        except (OSError, socket.gaierror) as e:
            raise ToraNetworkError(f"Failed to create connection to {self.netloc}: {e}") from e
        except Exception as e:
            raise ToraNetworkError(f"Unexpected error creating connection: {e}") from e

    def _request(
        self,
        method: str,
        path: str,
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> HttpResponse:
        """Make an HTTP request with comprehensive error handling."""
        conn = self._get_conn(timeout=timeout)
        full_path = self.base_path + path
        url = f"{self.scheme}://{self.netloc}{full_path}"

        final_headers = self.headers.copy()
        if headers:
            final_headers.update(headers)

        try:
            conn.request(method, full_path, body, headers=final_headers)
            response = conn.getresponse()
            data = response.read()

        except TimeoutError:
            if self.conn is None:
                conn.close()
            raise ToraTimeoutError(f"Request to {url} timed out after {timeout or self.timeout} seconds") from None
        except (OSError, ssl.SSLError) as e:
            if self.conn is None:
                conn.close()
            raise ToraNetworkError(f"Network error for {url}: {e}") from e
        except Exception as e:
            if self.conn is None:
                conn.close()
            raise ToraNetworkError(f"Unexpected error for {url}: {e}") from e

        if self.conn is None:
            conn.close()

        return HttpResponse(response, data, url)

    def get(
        self,
        path: str,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> HttpResponse:
        """Send a GET request."""
        return self._request("GET", path, headers=headers, timeout=timeout)

    def post(
        self,
        path: str,
        json: Any | None = None,
        data: bytes | None = None,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> HttpResponse:
        """Send a POST request with JSON or raw data."""
        body = None
        request_headers = {}
        if headers:
            request_headers.update(headers)

        if json is not None:
            try:
                body = _json.dumps(json).encode("utf-8")
                request_headers["Content-Type"] = "application/json"
            except (TypeError, ValueError) as e:
                raise ToraNetworkError(f"Failed to serialize JSON data: {e}") from e
        elif data is not None:
            if isinstance(data, str):
                body = data.encode("utf-8")
            elif isinstance(data, bytes):
                body = data
            else:
                raise ToraNetworkError(f"Invalid data type: {type(data)}")

        return self._request("POST", path, body=body, headers=request_headers, timeout=timeout)

    def close(self) -> None:
        """Close the connection."""
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass
            finally:
                self.conn = None

    def __enter__(self) -> "HttpClient":
        """Enter context manager."""
        self.conn = self._get_conn()
        return self

    def __exit__(self, _exc_type: Any, _exc_val: Any, _exc_tb: Any) -> None:
        """Exit context manager."""
        self.close()
