"""Tests for the General Analysis client initialization and configuration."""

import os
from unittest.mock import patch

import pytest

import generalanalysis
from generalanalysis import Client, AsyncClient


class TestSyncClient:
    """Tests for synchronous client."""

    def test_client_initialization_with_api_key(self):
        """Test client initialization with direct API key."""
        client = Client(api_key="test-api-key")
        assert client.api_key == "test-api-key"
        assert client.base_url == "https://redit-api-dev.generalanalysis.com"
        assert client.guards is not None

    def test_client_initialization_with_env_var(self):
        """Test client initialization with environment variable."""
        with patch.dict(os.environ, {"GA_API_KEY": "env-api-key"}):
            client = Client()
            assert client.api_key == "env-api-key"

    def test_client_initialization_without_api_key(self):
        """Test client initialization without API key shows warning."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.warns(UserWarning, match="No API key found"):
                client = Client()
                assert client.api_key is None

    def test_client_with_custom_base_url(self):
        """Test client with custom base URL."""
        client = Client(base_url="http://localhost:5001")
        assert client.base_url == "http://localhost:5001"

    def test_client_with_custom_timeout(self):
        """Test client with custom timeout."""
        client = Client(timeout=60)
        assert client._http_client.timeout == 60

    def test_client_repr(self):
        """Test client string representation."""
        client = Client()
        assert "GeneralAnalysis Client" in repr(client)
        assert client.base_url in repr(client)

    def test_client_context_manager(self):
        """Test client as context manager."""
        with Client(api_key="test-key") as client:
            assert client.api_key == "test-key"
            assert hasattr(client, "_http_client")
            assert hasattr(client._http_client, "session")
        # After context exit, session should be closed
        # We can't directly test if session is closed, but we can verify the method exists
        assert hasattr(client, "close")

    def test_client_close_method(self):
        """Test client close method."""
        client = Client(api_key="test-key")
        assert hasattr(client, "close")
        # Verify close can be called without error
        client.close()


class TestAsyncClient:
    """Tests for asynchronous client."""

    def test_async_client_initialization_with_api_key(self):
        """Test async client initialization with direct API key."""
        client = AsyncClient(api_key="test-api-key")
        assert client.api_key == "test-api-key"
        assert client.base_url == "https://redit-api-dev.generalanalysis.com"
        assert client.guards is not None

    def test_async_client_initialization_with_env_var(self):
        """Test async client initialization with environment variable."""
        with patch.dict(os.environ, {"GA_API_KEY": "env-api-key"}):
            client = AsyncClient()
            assert client.api_key == "env-api-key"

    def test_async_client_initialization_without_api_key(self):
        """Test async client initialization without API key shows warning."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.warns(UserWarning, match="No API key found"):
                client = AsyncClient()
                assert client.api_key is None

    def test_async_client_with_custom_base_url(self):
        """Test async client with custom base URL."""
        client = AsyncClient(base_url="http://localhost:5001")
        assert client.base_url == "http://localhost:5001"

    def test_async_client_with_custom_timeout(self):
        """Test async client with custom timeout."""
        client = AsyncClient(timeout=60)
        # AsyncHTTPClient uses httpx.Timeout internally
        assert client._http_client.timeout == 60

    def test_async_client_repr(self):
        """Test async client string representation."""
        client = AsyncClient()
        assert "GeneralAnalysis AsyncClient" in repr(client)
        assert client.base_url in repr(client)

    @pytest.mark.asyncio
    async def test_async_client_context_manager(self):
        """Test async client as context manager."""
        async with AsyncClient(api_key="test-key") as client:
            assert client.api_key == "test-key"
        # Client should be closed after context exit
        # (No direct way to test this without implementation details)


class TestImports:
    """Test that all public API components are importable."""

    def test_can_import_clients(self):
        """Test importing client classes."""
        from generalanalysis import Client, AsyncClient

        assert Client is not None
        assert AsyncClient is not None

    def test_can_import_exceptions(self):
        """Test importing exception classes."""
        from generalanalysis import (
            GeneralAnalysisError,
            AuthenticationError,
            GuardNotFoundError,
        )

        assert GeneralAnalysisError is not None
        assert AuthenticationError is not None
        assert GuardNotFoundError is not None

    def test_can_import_types(self):
        """Test importing type classes."""
        from generalanalysis import (
            Guard,
            GuardPolicy,
            GuardInvokeResult,
            PolicyEvaluation,
            GuardLog,
            PaginatedLogsResponse,
            PolicyItem,
        )

        assert all(
            [
                Guard,
                GuardPolicy,
                GuardInvokeResult,
                PolicyEvaluation,
                GuardLog,
                PaginatedLogsResponse,
                PolicyItem,
            ]
        )
