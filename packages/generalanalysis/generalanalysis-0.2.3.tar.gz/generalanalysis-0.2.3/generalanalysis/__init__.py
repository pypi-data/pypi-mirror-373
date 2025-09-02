"""
General Analysis - Python SDK for AI Guardrails

A simple and intuitive SDK for invoking and managing AI guardrails,
modeled after the design patterns of OpenAI and Anthropic SDKs.

Basic usage:
    >>> import generalanalysis
    >>> client = generalanalysis.Client()
    >>> guards = client.guards.list()
    >>> result = client.guards.invoke(guard_id=1, text="Check this text")

Async usage:
    >>> import asyncio
    >>> import generalanalysis
    >>>
    >>> async def main():
    ...     client = generalanalysis.AsyncClient()
    ...     result = await client.guards.invoke(guard_id=1, text="Check this text")
    ...     await client.close()
    >>>
    >>> asyncio.run(main())
"""

from .__version__ import __version__
from .async_client import AsyncClient
from .client import Client
from .exceptions import (
    AuthenticationError,
    GeneralAnalysisError,
    GuardNotFoundError,
)
from .types import (
    Guard,
    GuardInvokeResult,
    GuardLog,
    GuardPolicy,
    PaginatedLogsResponse,
    PolicyEvaluation,
    PolicyItem,
)

__all__ = [
    # Version
    "__version__",
    # Clients
    "Client",
    "AsyncClient",
    # Types
    "Guard",
    "GuardPolicy",
    "GuardInvokeResult",
    "PolicyEvaluation",
    "GuardLog",
    "PaginatedLogsResponse",
    "PolicyItem",
    # Exceptions
    "GeneralAnalysisError",
    "AuthenticationError",
    "GuardNotFoundError",
]
