import json

import httpx
import pytest
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from src.server import app


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
async def app_lifespan():
    await app.router.startup()
    yield
    await app.router.shutdown()


@pytest.fixture
def reset_mcp_transport():
    from src.server import mcp

    transport = getattr(mcp, "_http_transport", None)
    if transport is not None:
        transport._manager_started = False
        transport._session_manager = None
        transport._manager_task = None


@pytest.fixture
def httpx_app_client_factory():
    def _factory(headers=None, timeout=None, auth=None):
        return httpx.AsyncClient(
            base_url="http://testserver",
            headers=headers,
            timeout=timeout,
            auth=auth,
            transport=httpx.ASGITransport(
                app=app,
                raise_app_exceptions=False,
            ),
        )

    return _factory


@pytest.mark.asyncio
async def test_mcp_tool_discovery(
    auth_headers, httpx_app_client_factory, app_lifespan, reset_mcp_transport
):
    async with streamablehttp_client(
        "http://testserver/mcp",
        headers=auth_headers,
        httpx_client_factory=httpx_app_client_factory,
    ) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.list_tools()

    assert any(tool.name == "run_browser_agent" for tool in result.tools)


@pytest.mark.asyncio
async def test_mcp_call_matches_http(
    auth_headers, httpx_app_client_factory, monkeypatch, app_lifespan, reset_mcp_transport
):
    async def _fake_runner(task: str, context=None):
        return {
            "ok": True,
            "result_text": "Preview URL: https://example.lovable.dev",
            "steps": [{"step": "done"}],
            "debug": {"source": "fake"},
        }

    monkeypatch.setattr("src.server.run_browser_agent_async", _fake_runner)

    payload = {"task": "build a lovable demo", "context": {"foo": "bar"}}

    async with httpx_app_client_factory(headers=auth_headers) as http_client:
        http_response = await http_client.post(
            "/tools/run_browser_agent",
            json=payload,
        )
        assert http_response.status_code == 200
        http_json = http_response.json()

    async with streamablehttp_client(
        "http://testserver/mcp",
        headers=auth_headers,
        httpx_client_factory=httpx_app_client_factory,
    ) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(
                "run_browser_agent",
                {"task": payload["task"], "context": payload["context"]},
            )

    assert result.isError is False
    assert result.content, "Expected text content payload from MCP call"

    mcp_payload = json.loads(result.content[0].text)

    assert mcp_payload["ok"] == http_json["ok"]
    assert mcp_payload["status"] == http_json["status"]
    assert mcp_payload.get("preview_url") == http_json.get("preview_url")
    assert mcp_payload.get("raw") == http_json.get("raw")
