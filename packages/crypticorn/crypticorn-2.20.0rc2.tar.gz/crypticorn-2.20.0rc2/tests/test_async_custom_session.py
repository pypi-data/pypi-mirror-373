import asyncio
import gc
import warnings

import pytest
from aiohttp import ClientSession

from crypticorn.client import AsyncClient


@pytest.mark.asyncio
async def test_custom_http_client_injection():
    custom_session = ClientSession()

    client = AsyncClient(http_client=custom_session)

    # Subclients should have received the custom session immediately (sync context)
    subclient = client._services["trade"]
    assert subclient.base_client.rest_client.pool_manager is custom_session

    await client.close()
    assert not custom_session.closed  # Client did not own it

    await custom_session.close()


@pytest.mark.asyncio
async def test_lazy_http_client_creation():
    client = AsyncClient()
    assert client._http_client is None

    client._ensure_session()

    assert isinstance(client._http_client, ClientSession)
    subclient = client._services["trade"]
    assert subclient.base_client.rest_client.pool_manager is client._http_client

    await client.close()
    assert client._http_client is None  # It should have been closed


@pytest.mark.asyncio
async def test_close_custom_http_client_not_owned():
    custom_session = ClientSession()
    client = AsyncClient(http_client=custom_session)

    await client.close()
    assert not custom_session.closed  # Still open since it wasn't owned by us

    await custom_session.close()


@pytest.mark.asyncio
async def test_close_owned_http_client():
    client = AsyncClient()
    client._ensure_session()
    session = client._http_client

    await client.close()
    assert session.closed  # session should be closed since we own it


@pytest.mark.asyncio
async def test_unclosed_owned_session_warns():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")  # Catch all warnings

        client = AsyncClient()
        await client.trade.status.ping()

        # Intentionally forget to close
        del client
        await asyncio.sleep(0.1)  # Let __del__ run

        # Look for aiohttp's unclosed session warning
        unclosed_warnings = [
            warn for warn in w if "Unclosed client session" in str(warn.message)
        ]
        assert unclosed_warnings, "Expected unclosed client session warning"


@pytest.mark.asyncio
async def test_custom_session_not_closed_by_client():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        custom_session = ClientSession()
        client = AsyncClient(http_client=custom_session)
        await client.trade.status.ping()

        # Don't close the custom session
        del client
        del custom_session

        # Force cleanup (otherwise it's unpredicatable when the warning will be raised)
        await asyncio.sleep(0.1)
        gc.collect()
        await asyncio.sleep(0.1)

        unclosed_warnings = [
            warn
            for warn in w
            if "Unclosed client session" in str(warn.message)
            or "Unclosed connector" in str(warn.message)
        ]
        assert unclosed_warnings, "Expected unclosed client session warning"


@pytest.mark.asyncio
async def test_context_manager_usage():
    async with AsyncClient() as client:
        assert isinstance(client._http_client, ClientSession)
        subclient = client._services["trade"]
        assert subclient.base_client.rest_client.pool_manager is client._http_client

    # Confirm session is closed after context manager
    assert client._http_client is None
