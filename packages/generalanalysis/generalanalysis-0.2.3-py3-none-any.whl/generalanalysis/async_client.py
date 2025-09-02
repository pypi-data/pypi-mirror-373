"""Asynchronous client for the General Analysis SDK."""

import warnings
from typing import Any, Optional

from .core.auth import get_api_key, get_base_url
from .core.http_client import AsyncHTTPClient
from .resources.async_guards import AsyncGuards


class AsyncClient:
    """Asynchronous client for interacting with the General Analysis API.

    Example:
        >>> import asyncio
        >>> import generalanalysis
        >>>
        >>> async def main():
        ...     client = generalanalysis.AsyncClient()
        ...     guards = await client.guards.list()
        ...     result = await client.guards.invoke(guard_id=1, text="Check this text")
        ...     await client.close()
        >>>
        >>> asyncio.run(main())
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ):
        """Initialize the async General Analysis client."""
        self.api_key = get_api_key(api_key)
        self.base_url = get_base_url(base_url)

        if not self.api_key:
            warnings.warn(
                "No API key found. Please set GA_API_KEY environment variable "
                "or pass api_key parameter. Some operations may fail.",
                UserWarning,
                stacklevel=2,
            )

        self._http_client = AsyncHTTPClient(
            base_url=self.base_url, api_key=self.api_key, timeout=timeout
        )

        # Initialize resources
        self.guards = AsyncGuards(self._http_client)

    async def close(self) -> None:
        """Close the async client and cleanup resources."""
        await self._http_client.close()

    async def __aenter__(self) -> "AsyncClient":
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        await self.close()

    def __repr__(self) -> str:
        """String representation of the client."""
        return f"<GeneralAnalysis AsyncClient base_url='{self.base_url}'>"
