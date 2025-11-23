"""
Tests for Lovable adapter modules (selectors and flows).
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.lovable_adapter import flows, selectors


class TestSelectors:
    """Test Lovable UI selectors."""

    def test_login_selectors_exist(self):
        """Test login selectors are defined."""
        assert hasattr(selectors, "LOGIN_EMAIL_SELECTOR")
        assert hasattr(selectors, "LOGIN_PASSWORD_SELECTOR")
        assert hasattr(selectors, "LOGIN_SUBMIT_SELECTOR")

    def test_login_selectors_are_strings(self):
        """Test login selectors are valid strings."""
        assert isinstance(selectors.LOGIN_EMAIL_SELECTOR, str)
        assert isinstance(selectors.LOGIN_PASSWORD_SELECTOR, str)
        assert isinstance(selectors.LOGIN_SUBMIT_SELECTOR, str)
        assert len(selectors.LOGIN_EMAIL_SELECTOR) > 0
        assert len(selectors.LOGIN_PASSWORD_SELECTOR) > 0
        assert len(selectors.LOGIN_SUBMIT_SELECTOR) > 0

    def test_project_selectors_exist(self):
        """Test project selectors are defined."""
        assert hasattr(selectors, "PROJECT_NAME_INPUT_SELECTOR")
        assert hasattr(selectors, "CREATE_PROJECT_BUTTON_SELECTOR")

    def test_project_selectors_are_strings(self):
        """Test project selectors are valid strings."""
        assert isinstance(selectors.PROJECT_NAME_INPUT_SELECTOR, str)
        assert isinstance(selectors.CREATE_PROJECT_BUTTON_SELECTOR, str)

    def test_prompt_build_selectors_exist(self):
        """Test prompt and build selectors are defined."""
        assert hasattr(selectors, "PROMPT_INPUT_SELECTOR")
        assert hasattr(selectors, "BUILD_BUTTON_SELECTOR")
        assert hasattr(selectors, "BUILD_STATUS_SELECTOR")
        assert hasattr(selectors, "BUILD_COMPLETE_SELECTOR")

    def test_prompt_build_selectors_are_strings(self):
        """Test prompt and build selectors are valid strings."""
        assert isinstance(selectors.PROMPT_INPUT_SELECTOR, str)
        assert isinstance(selectors.BUILD_BUTTON_SELECTOR, str)
        assert isinstance(selectors.BUILD_STATUS_SELECTOR, str)
        assert isinstance(selectors.BUILD_COMPLETE_SELECTOR, str)

    def test_preview_url_selector_exists(self):
        """Test preview URL selector is defined."""
        assert hasattr(selectors, "PREVIEW_URL_SELECTOR")
        assert isinstance(selectors.PREVIEW_URL_SELECTOR, str)

    def test_timeout_constants_exist(self):
        """Test timeout constants are defined."""
        assert hasattr(selectors, "DEFAULT_TIMEOUT")
        assert hasattr(selectors, "BUILD_TIMEOUT")
        assert hasattr(selectors, "LOGIN_TIMEOUT")

    def test_timeout_constants_are_integers(self):
        """Test timeout constants are valid integers."""
        assert isinstance(selectors.DEFAULT_TIMEOUT, int)
        assert isinstance(selectors.BUILD_TIMEOUT, int)
        assert isinstance(selectors.LOGIN_TIMEOUT, int)
        assert selectors.DEFAULT_TIMEOUT > 0
        assert selectors.BUILD_TIMEOUT > selectors.DEFAULT_TIMEOUT
        assert selectors.LOGIN_TIMEOUT > 0


class TestFlows:
    """Test Lovable automation flows."""

    @pytest.mark.asyncio
    async def test_ensure_logged_in_success(self):
        """Test ensure_logged_in returns True when logged in."""
        page = AsyncMock()
        page.url = "https://lovable.dev/projects"
        page.wait_for_selector = AsyncMock()

        result = await flows.ensure_logged_in(page)
        assert result is True

    @pytest.mark.asyncio
    async def test_ensure_logged_in_on_login_page(self):
        """Test ensure_logged_in returns False on login page."""
        page = AsyncMock()
        page.url = "https://lovable.dev/login"

        result = await flows.ensure_logged_in(page)
        assert result is False

    @pytest.mark.asyncio
    async def test_ensure_logged_in_exception(self):
        """Test ensure_logged_in returns False on exception."""
        page = AsyncMock()
        page.url = "https://lovable.dev/projects"
        page.wait_for_selector = AsyncMock(side_effect=Exception("Timeout"))

        result = await flows.ensure_logged_in(page)
        assert result is False

    @pytest.mark.asyncio
    async def test_open_or_create_project_success(self):
        """Test open_or_create_project returns True on success."""
        page = AsyncMock()
        locator_mock = AsyncMock()
        locator_mock.count = AsyncMock(return_value=1)
        locator_mock.first = AsyncMock()
        locator_mock.first.click = AsyncMock()
        page.locator = MagicMock(return_value=locator_mock)
        page.wait_for_load_state = AsyncMock()

        result = await flows.open_or_create_project(page, "TestProject")
        assert result is True

    @pytest.mark.asyncio
    async def test_open_or_create_project_exception(self):
        """Test open_or_create_project returns False on exception."""
        page = AsyncMock()
        page.locator = MagicMock(side_effect=Exception("Not found"))

        result = await flows.open_or_create_project(page, "TestProject")
        assert result is False

    @pytest.mark.asyncio
    async def test_paste_prompt_success(self):
        """Test paste_prompt returns True on success."""
        page = AsyncMock()
        locator_mock = AsyncMock()
        locator_mock.count = AsyncMock(return_value=1)
        locator_mock.first = AsyncMock()
        locator_mock.first.fill = AsyncMock()
        page.locator = MagicMock(return_value=locator_mock)

        result = await flows.paste_prompt(page, "Build a todo app")
        assert result is True

    @pytest.mark.asyncio
    async def test_paste_prompt_exception(self):
        """Test paste_prompt returns False on exception."""
        page = AsyncMock()
        page.locator = MagicMock(side_effect=Exception("Not found"))

        result = await flows.paste_prompt(page, "Build a todo app")
        assert result is False

    @pytest.mark.asyncio
    async def test_trigger_build_success(self):
        """Test trigger_build returns True on success."""
        page = AsyncMock()
        locator_mock = AsyncMock()
        locator_mock.count = AsyncMock(return_value=1)
        locator_mock.click = AsyncMock()
        page.locator = MagicMock(return_value=locator_mock)

        result = await flows.trigger_build(page)
        assert result is True

    @pytest.mark.asyncio
    async def test_trigger_build_exception(self):
        """Test trigger_build returns False on exception."""
        page = AsyncMock()
        page.locator = MagicMock(side_effect=Exception("Not found"))

        result = await flows.trigger_build(page)
        assert result is False

    @pytest.mark.asyncio
    async def test_wait_for_build_success(self):
        """Test wait_for_build returns True on success."""
        page = AsyncMock()
        page.wait_for_selector = AsyncMock()

        result = await flows.wait_for_build(page, timeout=5000)
        assert result is True

    @pytest.mark.asyncio
    async def test_wait_for_build_timeout(self):
        """Test wait_for_build returns False on timeout."""
        page = AsyncMock()
        page.wait_for_selector = AsyncMock(side_effect=Exception("Timeout"))

        result = await flows.wait_for_build(page, timeout=1000)
        assert result is False

    @pytest.mark.asyncio
    async def test_extract_preview_url_success(self):
        """Test extract_preview_url returns URL on success."""
        page = AsyncMock()
        locator_mock = AsyncMock()
        locator_mock.count = AsyncMock(return_value=1)
        locator_mock.first = AsyncMock()
        locator_mock.first.get_attribute = AsyncMock(return_value="https://abc123.lovable.dev")
        page.locator = MagicMock(return_value=locator_mock)

        result = await flows.extract_preview_url(page)
        assert result is not None
        assert "lovable.dev" in result

    @pytest.mark.asyncio
    async def test_extract_preview_url_none(self):
        """Test extract_preview_url returns None when not found."""
        page = AsyncMock()
        page.locator = MagicMock(return_value=AsyncMock())
        page.locator.return_value.get_attribute = AsyncMock(return_value=None)

        result = await flows.extract_preview_url(page)
        assert result is None

    @pytest.mark.asyncio
    async def test_extract_preview_url_from_content(self):
        """Test extract_preview_url extracts from page content."""
        page = AsyncMock()
        locator_mock = AsyncMock()
        locator_mock.count = AsyncMock(return_value=0)
        page.locator = MagicMock(return_value=locator_mock)
        page.content = AsyncMock(return_value="Visit https://myapp.lovable.dev for preview")

        result = await flows.extract_preview_url(page)
        assert result is not None
        assert "lovable.dev" in result

    @pytest.mark.asyncio
    async def test_open_or_create_project_create_new(self):
        """Test open_or_create_project creates new project."""
        page = AsyncMock()
        project_link = AsyncMock()
        project_link.count = AsyncMock(return_value=0)
        create_btn = AsyncMock()
        create_btn.count = AsyncMock(return_value=1)
        create_btn.click = AsyncMock()
        page.locator = MagicMock(side_effect=[project_link, create_btn])
        page.fill = AsyncMock()
        page.click = AsyncMock()
        page.wait_for_load_state = AsyncMock()

        result = await flows.open_or_create_project(page, "NewProject")
        assert result is True
