import gc
import time
import warnings

from aiohttp import ClientSession

from crypticorn.client import SyncClient


def test_custom_http_client_injection():
    """Test that custom sessions are accepted but not used in sync mode since we use per-operation sessions."""
    import asyncio

    async def _test():
        custom_session = ClientSession()

        try:
            # For sync client, custom sessions are accepted but not used since we create sessions per operation
            client = SyncClient(http_client=custom_session)

            # In sync mode, services should not have the custom session since sessions are created per operation
            subclient = client._services["trade"]
            # Should be None since sync clients don't persist sessions
            assert subclient.base_client.rest_client.pool_manager is None

            client.close()
        finally:
            await custom_session.close()

    asyncio.run(_test())


def test_lazy_http_client_creation():
    """Test that sync client doesn't create persistent sessions."""
    client = SyncClient()
    assert client._http_client is None

    # _ensure_session does nothing in sync mode
    client._ensure_session()

    # Should still be None since sync clients don't persist sessions
    assert client._http_client is None

    subclient = client._services["trade"]
    # Should be None since sessions are created per operation
    assert subclient.base_client.rest_client.pool_manager is None

    client.close()
    assert client._http_client is None


def test_close_custom_http_client_not_owned():
    """Test that custom sessions are not affected by sync client close."""
    import asyncio

    async def _test():
        custom_session = ClientSession()

        try:
            client = SyncClient(http_client=custom_session)

            client.close()
            # Custom session should still be open since sync client doesn't use it
            assert not custom_session.closed
        finally:
            await custom_session.close()

    asyncio.run(_test())


def test_close_owned_http_client():
    """Test that sync client close doesn't affect non-existent persistent sessions."""
    client = SyncClient()

    # Trigger some operation that would create sessions
    client.trade.status.ping()

    # Should still be None since sessions are created and closed per operation
    assert client._http_client is None

    client.close()
    assert client._http_client is None


def test_no_persistent_sessions_in_sync_mode():
    """Test that sync client creates sessions per operation, not persistent ones."""
    client = SyncClient()

    # Make multiple calls
    for _ in range(3):
        response = client.trade.status.ping()
        assert response is not None
        # Should still be None after each call
        assert client._http_client is None

    # All services should still have None for pool_manager
    subclient = client._services["trade"]
    assert subclient.base_client.rest_client.pool_manager is None

    client.close()


def test_sync_client_operations_work():
    """Test that basic operations work with per-operation session management."""
    client = SyncClient()

    try:
        # Multiple operations should all work
        responses = []
        for _ in range(3):
            responses.append(client.trade.status.ping())

        # All responses should be valid
        assert len(responses) == 3
        for response in responses:
            assert response is not None

        # No persistent session should exist
        assert client._http_client is None

    finally:
        client.close()


def test_context_manager_usage():
    """Test context manager usage with sync client."""
    with SyncClient() as client:
        # Should not have persistent session
        assert client._http_client is None

        # Operations should work
        response = client.trade.status.ping()
        assert response is not None

        # Still no persistent session
        assert client._http_client is None

        subclient = client._services["trade"]
        # Should be None since sessions are per-operation
        assert subclient.base_client.rest_client.pool_manager is None

    # After context manager, client should be clean
    assert client._http_client is None


def test_concurrent_operations():
    """Test that multiple operations work correctly without session conflicts."""
    client = SyncClient()

    try:
        # Run multiple operations that would each create their own session
        responses = []
        for i in range(5):
            response = client.trade.status.ping()
            responses.append(response)
            # Verify no session persistence
            assert client._http_client is None

        # All responses should be valid
        assert len(responses) == 5
        for response in responses:
            assert response is not None

    finally:
        client.close()


def test_no_session_warnings_in_sync_mode():
    """Test that sync client doesn't generate unclosed session warnings."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        client = SyncClient()
        client.trade.status.ping()

        # Intentionally don't close manually to test cleanup
        del client
        time.sleep(0.1)  # Let cleanup happen
        gc.collect()
        time.sleep(0.1)

        # Should not have unclosed session warnings since sessions are cleaned per operation
        unclosed_warnings = [
            warn for warn in w if "Unclosed client session" in str(warn.message)
        ]
        # Sync client should not generate these warnings due to per-operation cleanup
        assert len(unclosed_warnings) == 0
