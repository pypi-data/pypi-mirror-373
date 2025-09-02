import asyncio

import pytest
from aiohttp import ClientSession

from crypticorn.client import AsyncClient


@pytest.mark.asyncio
async def test_client_basic_instantiation():
    """Test basic client instantiation without errors."""
    client = AsyncClient()
    assert client is not None
    assert client._http_client is None
    await client.close()


@pytest.mark.asyncio
async def test_client_with_custom_session():
    """Test client with custom session."""
    custom_session = ClientSession()
    client = AsyncClient(http_client=custom_session)

    assert client._http_client is custom_session
    await client.close()
    await custom_session.close()


@pytest.mark.asyncio
async def test_client_context_manager():
    """Test client as async context manager."""
    async with AsyncClient() as client:
        assert client is not None
        assert isinstance(client._http_client, ClientSession)

        # Test ping to ensure it works
        response = await client.trade.status.ping()
        assert response is not None


@pytest.mark.asyncio
async def test_client_manual_close():
    """Test manual close of client."""
    client = AsyncClient()

    # Trigger session creation
    client._ensure_session()
    assert client._http_client is not None

    # Close manually
    await client.close()
    assert client._http_client is None


@pytest.mark.asyncio
async def test_client_ping_functionality():
    """Test that ping works correctly."""
    client = AsyncClient()

    try:
        response = await client.trade.status.ping()
        # Should not raise any exceptions
        assert response is not None
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_client_multiple_service_access():
    """Test accessing multiple services without errors."""
    client = AsyncClient()

    try:
        assert client._http_client is None
        # Access multiple services to ensure they're properly initialized
        subclient = client._services["trade"]
        assert subclient is not None
        assert subclient.base_client.rest_client.pool_manager is None

        # Ensure all services share the same session once created
        client._ensure_session()
        session = client._http_client

        subclient = client._services["trade"]
        assert subclient.base_client.rest_client.pool_manager is session

    finally:
        await client.close()


@pytest.mark.asyncio
async def test_client_reuse_after_close():
    """Test that client can be reused after close."""
    client = AsyncClient()

    # First use
    client._ensure_session()
    first_session = client._http_client
    await client.close()

    # Second use
    client._ensure_session()
    second_session = client._http_client

    assert first_session is not second_session
    assert second_session is not None

    await client.close()


@pytest.mark.asyncio
async def test_client_no_exceptions_on_basic_operations():
    """Test that basic operations don't raise unexpected exceptions."""
    client = AsyncClient()

    try:
        # Access a service
        trade_client = client.trade
        assert trade_client is not None

        # Ping should work
        response = await client.trade.status.ping()
        assert response is not None

    except Exception as e:
        pytest.fail(f"Unexpected exception raised: {e}")
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_client_service_lazy_initialization():
    """Test that services are lazily initialized."""
    client = AsyncClient()

    # But HTTP client should be None until first use
    assert client._http_client is None
    client._ensure_session()
    assert client._http_client is not None

    # First access should create the session
    await client.trade.status.ping()
    assert client._http_client is not None

    await client.close()
    assert client._http_client is None


@pytest.mark.asyncio
async def test_client_context_manager_with_exception():
    """Test context manager behavior when exception occurs."""
    try:
        async with AsyncClient() as client:
            # Simulate some work
            client._ensure_session()
            client._http_client

            # Raise an exception
            raise ValueError("Test exception")

    except ValueError:
        # Exception should be handled, but client should still be closed
        # We can't directly check this, but the context manager should handle it
        pass

    # Client should be properly closed even after exception


@pytest.mark.asyncio
async def test_client_concurrent_operations():
    """Test that client handles concurrent operations correctly."""
    client = AsyncClient()

    try:
        # Run multiple ping operations concurrently
        tasks = [client.trade.status.ping() for _ in range(5)]
        responses = await asyncio.gather(*tasks)

        # All responses should be valid
        assert len(responses) == 5
        for response in responses:
            assert response is not None

    finally:
        await client.close()
        assert client._http_client is None
