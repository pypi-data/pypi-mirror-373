import pytest
import pytest_asyncio

from crypticorn import AsyncClient
from crypticorn.hive import Configuration as HiveConfig


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(api_key="test") as client:
        yield client


@pytest.mark.asyncio
async def test_client_config(client: AsyncClient):
    client.configure(config=HiveConfig(host="something"), service="hive")
    assert client.hive.config.host == "something"  # overriden
    assert client.hive.config.api_key == {"APIKeyHeader": "test"}  # not overriden
