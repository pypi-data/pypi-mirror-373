from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from fatum.client import ClientError, PermanentError, RetryableError
from tests.fixtures.httpbin_client import HTTPBinClient
from tests.fixtures.httpbin_models import HTTPBinResponse


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[HTTPBinClient, None]:
    async with HTTPBinClient(timeout=10.0) as client:
        yield client


@pytest.mark.asyncio
async def test_generic_request_pattern_type_safety(client: HTTPBinClient) -> None:
    test_data = {"test": "data", "number": 42}
    response = await client.echo_json(test_data)

    assert isinstance(response, HTTPBinResponse)
    assert response.json_data == {"data": test_data}
    assert response.url == "https://httpbin.org/post"


@pytest.mark.asyncio
async def test_retry_configuration_precedence() -> None:
    client = HTTPBinClient(
        timeout=5.0,
        max_retries=3,
        retry_min_wait=0.1,
        retry_max_wait=0.5,
    )

    mock_http_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.status_code = 503
    mock_response.text = "Service Unavailable"
    mock_response.headers = {}

    mock_http_client.request.return_value = mock_response

    call_count = 0

    async def mock_request(*_args: Any, **_kwargs: Any) -> MagicMock:
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            return mock_response
        else:
            success_response = MagicMock()
            success_response.status_code = 200
            success_response.json = lambda: {"json": {"success": True}, "data": ""}
            success_response.headers = {}
            success_response.text = '{"json": {"success": true}, "data": ""}'
            return success_response

    mock_http_client.request.side_effect = mock_request

    with patch.object(client, "_get_client", return_value=mock_http_client):
        response = await client.echo_json({"test": "retry"})
        assert response.json_data == {"success": True}
        assert call_count == 3

    mock_http_client.reset_mock()
    mock_http_client.request.side_effect = [mock_response] * 5

    with patch.object(client, "_get_client", return_value=mock_http_client):
        with pytest.raises(RetryableError) as exc_info:
            await client.echo_json({"test": "no-retry"}, max_retry_attempts=0)
        assert exc_info.value.status_code == 503
        assert mock_http_client.request.call_count == 1

    await client.close()


@pytest.mark.asyncio
async def test_error_classification(client: HTTPBinClient) -> None:
    with pytest.raises(PermanentError) as exc_info_perm:
        await client.test_status(404, max_retry_attempts=1)
    assert exc_info_perm.value.status_code == 404
    assert "Permanent error: 404" in str(exc_info_perm.value)

    with pytest.raises(RetryableError) as exc_info_retry:
        await client.test_status(503, max_retry_attempts=1)
    assert exc_info_retry.value.status_code == 503
    assert "Retryable error: 503" in str(exc_info_retry.value)


@pytest.mark.asyncio
async def test_context_manager_lifecycle() -> None:
    async with HTTPBinClient(timeout=5.0) as client:
        assert client._client is None
        response = await client.echo_json({"test": "data"})
        assert client._client is not None
        assert isinstance(response, HTTPBinResponse)
        was_closed_in_context = client._is_closed

    assert not was_closed_in_context

    client2 = HTTPBinClient(timeout=5.0)
    await client2.__aenter__()
    await client2.echo_json({"test": "data"})
    await client2.__aexit__(None, None, None)
    assert client2._is_closed is True

    with pytest.raises(ClientError) as exc_info:
        await client2.echo_json({"test": "after-close"})
    assert "Client has been closed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_concurrent_requests(client: HTTPBinClient) -> None:
    tasks = [client.echo_json({"request_id": i}) for i in range(5)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    assert all(not isinstance(r, Exception) for r in results)
    assert all(isinstance(r, HTTPBinResponse) for r in results)

    for i, result in enumerate(results):
        assert isinstance(result, HTTPBinResponse)
        assert result.json_data == {"data": {"request_id": i}}
