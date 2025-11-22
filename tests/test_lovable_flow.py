"""
Unit tests for Lovable flow and gateway utilities.
"""

from src.server import _extract_preview_url, _map_error_code


class TestExtractPreviewUrl:
    """Test preview URL extraction."""

    def test_extract_lovable_preview_url(self):
        """Test extracting Lovable preview URL from text."""
        text = "Build completed. Preview: https://abc123.lovable.dev"
        url = _extract_preview_url(text)
        assert url is not None
        assert "lovable.dev" in url

    def test_extract_preview_url_with_path(self):
        """Test extracting preview URL with path."""
        text = "Visit https://preview.lovable.dev/project/abc123 for details"
        url = _extract_preview_url(text)
        assert url is not None
        assert "lovable.dev" in url

    def test_no_preview_url(self):
        """Test when no preview URL is present."""
        text = "Build failed due to syntax error"
        url = _extract_preview_url(text)
        assert url is None

    def test_multiple_urls_returns_first(self):
        """Test that first URL is returned when multiple present."""
        text = "https://proj1.lovable.dev and https://proj2.lovable.dev"
        url = _extract_preview_url(text)
        assert url is not None
        assert "proj1" in url


class TestErrorMapping:
    """Test error code mapping."""

    def test_timeout_error(self):
        """Test timeout error mapping."""
        error = "Execution timed out after 600 seconds"
        code = _map_error_code(error)
        assert code == "TIMEOUT_BUILD"

    def test_auth_error(self):
        """Test authentication error mapping."""
        error = "Login failed: invalid credentials"
        code = _map_error_code(error)
        assert code == "AUTH_EXPIRED"

    def test_ui_changed_error(self):
        """Test UI changed error mapping."""
        error = "Element selector not found: button.build"
        code = _map_error_code(error)
        assert code == "UI_CHANGED"

    def test_network_error(self):
        """Test network error mapping."""
        error = "Connection refused: network unreachable"
        code = _map_error_code(error)
        assert code == "NETWORK_ERROR"

    def test_unknown_error(self):
        """Test unknown error mapping."""
        error = "Something went wrong"
        code = _map_error_code(error)
        assert code == "UNKNOWN_ERROR"

    def test_case_insensitive_mapping(self):
        """Test that error mapping is case-insensitive."""
        error = "TIMEOUT: Operation timed out"
        code = _map_error_code(error)
        assert code == "TIMEOUT_BUILD"


class TestResponseModels:
    """Test response model validation."""

    def test_success_response_model(self):
        """Test success response model."""
        from src.server import RunOutput

        response = RunOutput(
            ok=True,
            status="done",
            run_id="test-123",
            preview_url="https://test.lovable.dev",
            raw="output",
            elapsed_sec=1.5,
        )
        assert response.ok is True
        assert response.run_id == "test-123"
        assert response.status == "done"

    def test_error_response_model(self):
        """Test error response model."""
        from src.server import RunOutput

        response = RunOutput(
            ok=False,
            status="error",
            run_id="test-123",
            error_code="TIMEOUT_BUILD",
            message="Build timed out",
            elapsed_sec=600.0,
        )
        assert response.ok is False
        assert response.error_code == "TIMEOUT_BUILD"
