"""Tests for custom exceptions."""

import pytest

from generalanalysis import (
    GeneralAnalysisError,
    AuthenticationError,
    GuardNotFoundError,
)


class TestExceptions:
    """Tests for exception classes."""

    def test_general_analysis_error(self):
        """Test GeneralAnalysisError creation and attributes."""
        error = GeneralAnalysisError(
            "Test error",
            status_code=500,
            response_data={"detail": "Server error"},
        )
        assert str(error) == "Test error"
        assert error.status_code == 500
        assert error.response_data == {"detail": "Server error"}

    def test_general_analysis_error_minimal(self):
        """Test GeneralAnalysisError with minimal args."""
        error = GeneralAnalysisError("Simple error")
        assert str(error) == "Simple error"
        assert error.status_code is None
        assert error.response_data is None

    def test_authentication_error(self):
        """Test AuthenticationError creation."""
        error = AuthenticationError()
        assert "Authentication failed" in str(error)
        assert error.status_code == 401

    def test_authentication_error_custom_message(self):
        """Test AuthenticationError with custom message."""
        error = AuthenticationError("Invalid API key format")
        assert str(error) == "Invalid API key format"
        assert error.status_code == 401

    def test_guard_not_found_error(self):
        """Test GuardNotFoundError creation."""
        error = GuardNotFoundError(guard_id=123)
        assert "123" in str(error)
        assert "not found" in str(error)
        assert error.status_code == 404

    def test_exception_inheritance(self):
        """Test that all exceptions inherit from GeneralAnalysisError."""
        assert issubclass(AuthenticationError, GeneralAnalysisError)
        assert issubclass(GuardNotFoundError, GeneralAnalysisError)

    def test_exception_catching(self):
        """Test that exceptions can be caught properly."""
        # Specific exception
        with pytest.raises(GuardNotFoundError):
            raise GuardNotFoundError(guard_id=1)

        # Base exception catches derived
        with pytest.raises(GeneralAnalysisError):
            raise AuthenticationError()

        # Base exception catches all SDK errors
        with pytest.raises(GeneralAnalysisError):
            raise GuardNotFoundError(guard_id=2)
