"""
End-to-end smoke tests for Lovable MCP Gateway.

These tests verify the gateway is functioning without requiring
actual Lovable credentials or browser automation.
"""

import pytest
from fastapi.testclient import TestClient

from src.server import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "version" in data
        assert "concurrency" in data


class TestAuthenticationMiddleware:
    """Test authentication middleware."""

    def test_missing_auth_header(self, client):
        """Test request without auth header is rejected."""
        response = client.post(
            "/tools/run_browser_agent",
            json={"task": "test"},
        )
        assert response.status_code == 401

    def test_invalid_bearer_token(self, client):
        """Test request with invalid token is rejected."""
        response = client.post(
            "/tools/run_browser_agent",
            json={"task": "test"},
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401

    def test_health_endpoint_no_auth(self, client):
        """Test health endpoint doesn't require auth."""
        response = client.get("/health")
        assert response.status_code == 200


class TestRequestValidation:
    """Test request validation."""

    def test_missing_task_field(self, client):
        """Test request without task field is rejected."""
        response = client.post(
            "/tools/run_browser_agent",
            json={},
            headers={"Authorization": "Bearer test-token"},
        )
        assert response.status_code in [400, 422]

    def test_valid_request_structure(self, client):
        """Test valid request structure is accepted."""
        # Note: This will fail at execution but should pass validation
        response = client.post(
            "/tools/run_browser_agent",
            json={"task": "test task", "context": {}},
            headers={"Authorization": "Bearer test-token"},
        )
        # Should not be 422 (validation error)
        assert response.status_code != 422


class TestResponseStructure:
    """Test response structure compliance."""

    def test_response_has_required_fields(self, client):
        """Test response includes required fields."""
        # This test verifies the response model structure
        # even if execution fails
        from src.server import RunBrowserAgentResponse

        response = RunBrowserAgentResponse(
            ok=True,
            run_id="test-id",
            raw="test output",
            elapsed_sec=1.0,
        )

        assert hasattr(response, "ok")
        assert hasattr(response, "run_id")
        assert hasattr(response, "raw")
        assert hasattr(response, "elapsed_sec")
        assert hasattr(response, "preview_url")
        assert hasattr(response, "status")


class TestErrorHandling:
    """Test error handling."""

    def test_error_response_structure(self, client):
        """Test error response has correct structure."""
        from src.server import ErrorResponse

        error = ErrorResponse(
            ok=False,
            run_id="test-id",
            error_code="TIMEOUT_BUILD",
            message="Test error",
            elapsed_sec=1.0,
        )

        assert error.ok is False
        assert error.error_code == "TIMEOUT_BUILD"
        assert error.message == "Test error"
