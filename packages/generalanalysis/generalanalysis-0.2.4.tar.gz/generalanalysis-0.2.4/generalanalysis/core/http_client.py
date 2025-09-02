"""Base HTTP client for the General Analysis SDK."""

import json
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import httpx
import requests

from ..__version__ import __version__
from ..exceptions import (
    AuthenticationError,
    GeneralAnalysisError,
)


class BaseHTTPClient:
    """Base class for HTTP clients."""

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.headers = self._get_headers()

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"generalanalysis-python/{__version__}",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        return urljoin(self.base_url, endpoint)

    def _handle_response_error(self, status_code: int, response_data: Any) -> None:
        """Handle HTTP error responses."""
        error_message = None
        if isinstance(response_data, dict):
            error_message = response_data.get("detail") or response_data.get("message")
        elif isinstance(response_data, str):
            error_message = response_data

        if status_code == 401:
            raise AuthenticationError(error_message or "Authentication failed")
        elif status_code == 404:
            # This will be caught and re-raised with specific guard_id in guards.py
            raise GeneralAnalysisError(
                error_message or "Resource not found",
                status_code=404,
                response_data=response_data if isinstance(response_data, dict) else None,
            )
        else:
            raise GeneralAnalysisError(
                error_message or f"Request failed with status {status_code}",
                status_code=status_code,
                response_data=response_data if isinstance(response_data, dict) else None,
            )


class SyncHTTPClient(BaseHTTPClient):
    """Synchronous HTTP client using requests."""

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        super().__init__(base_url, api_key, timeout)
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a synchronous HTTP request."""
        url = self._build_url(endpoint)

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                timeout=self.timeout,
            )

            if response.status_code >= 400:
                try:
                    error_data = response.json()
                except (json.JSONDecodeError, ValueError):
                    error_data = response.text
                self._handle_response_error(response.status_code, error_data)

            result = response.json()
            return result  # type: ignore[no-any-return]

        except requests.exceptions.Timeout:
            raise GeneralAnalysisError(f"Request timed out after {self.timeout} seconds") from None
        except requests.exceptions.ConnectionError:
            raise GeneralAnalysisError(f"Could not connect to {self.base_url}") from None
        except requests.exceptions.RequestException as e:
            raise GeneralAnalysisError(f"Request failed: {str(e)}") from e

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        return self.request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a POST request."""
        return self.request("POST", endpoint, json_data=data)

    def close(self) -> None:
        """Close the HTTP client."""
        self.session.close()


class AsyncHTTPClient(BaseHTTPClient):
    """Asynchronous HTTP client using httpx."""

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        super().__init__(base_url, api_key, timeout)
        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
        )

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an asynchronous HTTP request."""
        url = self._build_url(endpoint)

        try:
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
            )

            if response.status_code >= 400:
                try:
                    error_data = response.json()
                except (json.JSONDecodeError, ValueError):
                    error_data = response.text
                self._handle_response_error(response.status_code, error_data)

            result = response.json()
            return result  # type: ignore[no-any-return]

        except httpx.TimeoutException:
            raise GeneralAnalysisError(f"Request timed out after {self.timeout} seconds") from None
        except httpx.ConnectError:
            raise GeneralAnalysisError(f"Could not connect to {self.base_url}") from None
        except httpx.RequestError as e:
            raise GeneralAnalysisError(f"Request failed: {str(e)}") from e

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        return await self.request("GET", endpoint, params=params)

    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a POST request."""
        return await self.request("POST", endpoint, json_data=data)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
