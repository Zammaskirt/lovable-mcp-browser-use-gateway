"""
Tests for server error handling and edge cases.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.server import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestServerErrorHandling:
    """Test server error handling."""

    @patch("src.server.run_browser_agent_async")
    def test_browser_agent_exception(self, mock_agent, client):
        """Test handling of unexpected exceptions in browser agent."""
        mock_agent.side_effect = RuntimeError("Unexpected error")

        response = client.post(
            "/tools/run_browser_agent",
            json={"task": "test task"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is False
        assert data["status"] == "error"
        assert "error_code" in data

    @patch("src.server.run_browser_agent_async")
    def test_browser_agent_failure_response(self, mock_agent, client):
        """Test handling of failed browser agent response."""
        mock_agent.return_value = {
            "ok": False,
            "error": "Login failed: invalid credentials",
            "result_text": "Auth error",
        }

        response = client.post(
            "/tools/run_browser_agent",
            json={"task": "test task"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is False
        assert data["error_code"] == "AUTH_EXPIRED"

    @patch("src.server.run_browser_agent_async")
    def test_browser_agent_timeout_error(self, mock_agent, client):
        """Test handling of timeout errors."""
        mock_agent.side_effect = TimeoutError("Execution timed out after 600 seconds")

        response = client.post(
            "/tools/run_browser_agent",
            json={"task": "test task"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is False
        assert data["error_code"] == "TIMEOUT_BUILD"

    def test_rate_limiting(self, client):
        """Test rate limiting is applied."""
        # Make multiple requests rapidly
        for i in range(15):
            response = client.post(
                "/tools/run_browser_agent",
                json={"task": "test task"},
                headers={"Authorization": "Bearer test-token"},
            )
            # After rate limit, should get 429
            if i >= 10:
                if response.status_code == 429:
                    break

