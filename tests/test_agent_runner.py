"""
Tests for agent runner module.
"""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from src.agent_runner import run_browser_agent, run_browser_agent_async


class TestRunBrowserAgent:
    """Test browser agent execution."""

    @patch("src.agent_runner._run_saik0s_cli")
    def test_run_browser_agent_success(self, mock_cli):
        """Test successful browser agent execution."""
        mock_cli.return_value = "Build completed. Preview: https://abc123.lovable.dev"

        result = run_browser_agent("build a todo app")

        assert result["ok"] is True
        assert "lovable.dev" in result["result_text"]

    @patch("src.agent_runner._run_saik0s_cli")
    def test_run_browser_agent_empty_output(self, mock_cli):
        """Test browser agent with empty output."""
        mock_cli.return_value = ""

        result = run_browser_agent("build a todo app")

        assert result["ok"] is False
        assert "no output" in result["error"].lower()

    @patch("src.agent_runner._run_saik0s_cli")
    def test_run_browser_agent_timeout(self, mock_cli):
        """Test browser agent timeout."""
        mock_cli.side_effect = TimeoutError("Timed out after 600s")

        result = run_browser_agent("build a todo app")

        assert result["ok"] is False
        assert "timed out" in result["error"].lower()

    @patch("src.agent_runner._run_saik0s_cli")
    def test_run_browser_agent_subprocess_error(self, mock_cli):
        """Test browser agent subprocess error."""
        mock_cli.side_effect = subprocess.CalledProcessError(1, "cmd", output="error")

        result = run_browser_agent("build a todo app")

        assert result["ok"] is False
        assert "error" in result

    @pytest.mark.asyncio
    @patch("src.agent_runner.run_browser_agent")
    async def test_run_browser_agent_async(self, mock_sync):
        """Test async wrapper for browser agent."""
        mock_sync.return_value = {"ok": True, "result_text": "success"}

        result = await run_browser_agent_async("build a todo app")

        assert result["ok"] is True
        assert mock_sync.called

