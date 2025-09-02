"""Tests for guards resource operations."""

from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import pytest

from generalanalysis import (
    Client,
    AsyncClient,
    Guard,
    GuardInvokeResult,
    PolicyEvaluation,
    GuardNotFoundError,
    AuthenticationError,
    GeneralAnalysisError,
    PaginatedLogsResponse,
    GuardLog,
    PolicyItem,
)
from generalanalysis.resources.guards import Guards
from generalanalysis.resources.async_guards import AsyncGuards


class TestSyncGuards:
    """Tests for synchronous guards operations."""

    def test_list_guards(self):
        """Test listing guards."""
        # Setup mock HTTP client
        mock_client = Mock()
        mock_client.get.return_value = [
            {
                "id": 1,
                "name": "Guard 1",
                "description": "First guard",
                "endpoint": "/guards/1",
                "policies": [],
            },
            {
                "id": 2,
                "name": "Guard 2",
                "description": "Second guard",
                "endpoint": "/guards/2",
                "policies": [],
            },
        ]

        # Create Guards instance with mocked client
        guards_resource = Guards(mock_client)
        guards = guards_resource.list()

        # Assertions
        assert len(guards) == 2
        assert guards[0].id == 1
        assert guards[0].name == "Guard 1"
        assert guards[1].id == 2
        assert guards[1].name == "Guard 2"
        mock_client.get.assert_called_once_with("/guards")

    def test_get_guard(self):
        """Test getting a specific guard."""
        # Setup mock HTTP client
        mock_client = Mock()
        mock_client.get.return_value = {
            "id": 1,
            "name": "Test Guard",
            "description": "A test guard",
            "endpoint": "/guards/1",
            "policies": [{"id": 1, "name": "Policy 1", "definition": "Test policy definition"}],
        }

        # Create Guards instance and call
        guards_resource = Guards(mock_client)
        guard = guards_resource.get(guard_id=1)

        # Assertions
        assert guard.id == 1
        assert guard.name == "Test Guard"
        assert guard.description == "A test guard"
        assert len(guard.policies) == 1
        assert guard.policies[0].name == "Policy 1"
        mock_client.get.assert_called_once_with("/guards/1")

    def test_get_guard_not_found(self):
        """Test getting a guard that doesn't exist."""
        # Setup mock HTTP client
        mock_client = Mock()
        mock_client.get.side_effect = GeneralAnalysisError("Guard not found", status_code=404)

        # Create Guards instance and test
        guards_resource = Guards(mock_client)
        with pytest.raises(GuardNotFoundError) as exc_info:
            guards_resource.get(guard_id=999)

        assert "999" in str(exc_info.value)

    def test_invoke_guard(self):
        """Test invoking a guard."""
        # Setup mock HTTP client
        mock_client = Mock()
        mock_client.post.return_value = {
            "block": False,
            "latency_ms": 123.45,
            "policies": [
                {
                    "name": "Policy 1",
                    "definition": "Policy 1 definition",
                    "pass": True,
                    "violation_prob": 0.1,
                },
                {
                    "name": "Policy 2",
                    "definition": "Policy 2 definition",
                    "pass": False,
                    "violation_prob": 0.9,
                },
            ],
            "raw": {"model_output": "test output"},
        }

        # Create Guards instance and call
        guards_resource = Guards(mock_client)
        result = guards_resource.invoke(guard_id=1, text="Test text")

        # Assertions
        assert result.block is False
        assert result.latency_ms == 123.45
        assert len(result.policies) == 2
        assert result.policies[0].name == "Policy 1"
        assert result.policies[0].passed is True
        assert result.policies[1].name == "Policy 2"
        assert result.policies[1].passed is False
        mock_client.post.assert_called_once_with(
            "/guards/invoke", data={"guard_id": 1, "text": "Test text"}
        )

    def test_invoke_guard_not_found(self):
        """Test invoking a guard that doesn't exist."""
        # Setup mock HTTP client
        mock_client = Mock()
        mock_client.post.side_effect = GeneralAnalysisError("Guard not found", status_code=404)

        # Create Guards instance and test
        guards_resource = Guards(mock_client)
        with pytest.raises(GuardNotFoundError) as exc_info:
            guards_resource.invoke(guard_id=999, text="test")

        assert "999" in str(exc_info.value)

    def test_generate_policies_from_job(self):
        """Test generating policies from a job."""
        # Setup mock HTTP client
        mock_client = Mock()
        mock_client.get.return_value = [
            {"policy_name": "Policy 1", "policy_description": "Description 1"},
            {"policy_name": "Policy 2", "policy_description": "Description 2"},
        ]

        # Create Guards instance and call
        guards_resource = Guards(mock_client)
        policies = guards_resource.generate_policies_from_job(job_id=123)

        # Assertions
        assert len(policies) == 2
        assert policies[0].policy_name == "Policy 1"
        assert policies[0].policy_description == "Description 1"
        assert policies[1].policy_name == "Policy 2"
        assert policies[1].policy_description == "Description 2"
        mock_client.get.assert_called_once_with("/guards/generate-policies-from-job/123")

    def test_list_logs(self):
        """Test listing guard logs."""
        # Setup mock HTTP client
        mock_client = Mock()
        mock_client.get.return_value = {
            "items": [
                {
                    "id": 1,
                    "user_id": "user-123",
                    "guard_id": 1,
                    "input_text": "Test text",
                    "result": {"raw": "output"},
                    "latency_ms": 100.0,
                    "blocked": False,
                    "created_at": "2024-01-01T00:00:00",
                    "policies": [],
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 50,
            "total_pages": 1,
        }

        # Create Guards instance and call
        guards_resource = Guards(mock_client)
        logs = guards_resource.list_logs(guard_id=1, page=1, page_size=10)

        # Assertions
        assert isinstance(logs, PaginatedLogsResponse)
        assert logs.total == 1
        assert logs.page == 1
        assert logs.page_size == 50
        assert logs.total_pages == 1
        assert len(logs.items) == 1
        assert logs.items[0].id == 1
        assert logs.items[0].blocked is False
        mock_client.get.assert_called_once_with(
            "/guards/logs", params={"guard_id": 1, "page": 1, "page_size": 10}
        )


class TestAsyncGuards:
    """Tests for asynchronous guards operations."""

    @pytest.mark.asyncio
    async def test_list_guards_async(self):
        """Test listing guards asynchronously."""
        # Setup mock HTTP client
        mock_client = MagicMock()

        async def mock_get(*args, **kwargs):
            return [
                {
                    "id": 1,
                    "name": "Guard 1",
                    "description": "First guard",
                    "endpoint": "/guards/1",
                    "policies": [],
                },
                {
                    "id": 2,
                    "name": "Guard 2",
                    "description": "Second guard",
                    "endpoint": "/guards/2",
                    "policies": [],
                },
            ]

        mock_client.get = mock_get

        # Create AsyncGuards instance and call
        guards_resource = AsyncGuards(mock_client)
        guards = await guards_resource.list()

        # Assertions
        assert len(guards) == 2
        assert guards[0].id == 1
        assert guards[0].name == "Guard 1"
        # Can't use assert_called_once_with on async functions directly

    @pytest.mark.asyncio
    async def test_get_guard_async(self):
        """Test getting a guard asynchronously."""
        # Setup mock HTTP client
        mock_client = MagicMock()

        async def mock_get(*args, **kwargs):
            return {
                "id": 1,
                "name": "Test Guard",
                "description": "A test guard",
                "endpoint": "/guards/1",
                "policies": [],
            }

        mock_client.get = mock_get

        # Create AsyncGuards instance and call
        guards_resource = AsyncGuards(mock_client)
        guard = await guards_resource.get(guard_id=1)

        # Assertions
        assert guard.id == 1
        assert guard.name == "Test Guard"

    @pytest.mark.asyncio
    async def test_invoke_guard_async(self):
        """Test invoking a guard asynchronously."""
        # Setup mock HTTP client
        mock_client = MagicMock()

        async def mock_post(*args, **kwargs):
            return {
                "block": True,
                "latency_ms": 200.0,
                "policies": [
                    {
                        "name": "Policy 1",
                        "pass": False,
                        "definition": "No harmful content",
                        "violation_prob": 0.95,
                    },
                ],
                "raw": {"model_output": "blocked content"},
            }

        mock_client.post = mock_post

        # Create AsyncGuards instance and call
        guards_resource = AsyncGuards(mock_client)
        result = await guards_resource.invoke(guard_id=1, text="Blocked text")

        # Assertions
        assert result.block is True
        assert result.latency_ms == 200.0
        assert len(result.policies) == 1
        assert result.policies[0].name == "Policy 1"
        assert result.policies[0].passed is False
        assert result.policies[0].definition == "No harmful content"

    @pytest.mark.asyncio
    async def test_guard_not_found_async(self):
        """Test handling guard not found error asynchronously."""
        # Setup mock HTTP client
        mock_client = MagicMock()

        async def mock_get(*args, **kwargs):
            raise GeneralAnalysisError("Guard not found", status_code=404)

        mock_client.get = mock_get

        # Create AsyncGuards instance and test
        guards_resource = AsyncGuards(mock_client)
        with pytest.raises(GuardNotFoundError) as exc_info:
            await guards_resource.get(guard_id=999)

        assert "999" in str(exc_info.value)
