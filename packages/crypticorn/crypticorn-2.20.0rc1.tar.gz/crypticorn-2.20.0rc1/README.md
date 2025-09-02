![Crypticorn Logo](https://crypticorn-public.s3.eu-west-1.amazonaws.com/logo-full.svg)

## What is Crypticorn?

Crypticorn is at the forefront of cutting-edge crypto trading with Machine Learning.

Use this API Client to access valuable data sources, contribute to the Hive AI - a community driven AI Meta Model for predicting the
crypto market - and programmatically interact with the entire Crypticorn ecosystem.

## Installation

You need Python 3.9+ installed to be able to use this library.

You can install the latest stable version from [PyPi](https://pypi.org/project/crypticorn/):
```bash
pip install crypticorn
```

If you want the latest version, which could be a pre release, run:
```bash
pip install --pre crypticorn
```

You can install extra dependencies grouped in the extras `extra`, `dev` (development) and `test` (testing). The `extra` dependencies include heavy libraries like `pandas`, which is only used in a few custom API operations (see [data processing](#data-preprocessing)), which preprocess the response data as a pandas Dataframe for convenience.

## Structure

Our API is available as both an asynchronous and synchronous Python SDK. The main entry points are:

- `AsyncClient` - Asynchronous client for async/await usage
- `SyncClient` - Synchronous client for traditional blocking calls

```python
from crypticorn import AsyncClient, SyncClient
```
Both clients serve as the central interface for API operations and instantiate multiple API wrappers corresponding to our micro services. These are structured the following:

<img src="https://crypticorn-public.s3.eu-west-1.amazonaws.com/api-client-python-structure.svg" alt="pip package structure" />

You can either explore each API by clicking through the library or checkout the [API Documentation](https://docs.crypticorn.com/api).

Request and response models for API operations should be accessed through the sub package you are using for an operation. All symbols are re-exported at the sub package level for convenience.

```python
from crypticorn.trade import BotCreate
from crypticorn.klines import MarketType
```

## Versioning

The SDK major version tracks the highest supported API version. A new API major bump always triggers a new major release of this package. Minor and patch versions only add non-breaking changes. We follow [Semantic Versioning](https://semver.org/).

| SDK Version | Auth | Trade | Klines | Metrics | Hive | Dex | Pay | Notification |
| ----------------- | ---- | ----- | ------ | ------- | ---- | --- | --- | ------------ |
| v2.x                 | v1   | v1    | v1     | v1      | v1   | v1  | v1  | v1           |

## Authentication

To get started, [create an API key in your dashboard](https://app.crypticorn.com/account/developer).

The scopes you can assign, resemble the [package structure](#structure). The first part defines if the scopes is for reading or writing a ressource, the second matches the API, the third the ROUTER being used. `read` scopes gives access to GET, `write` to PUT, PATCH, POST, DELETE endpoints.

There are scopes which don't follow this structure. Those are either scopes that must be purchased (e.g. `read:predictions`), give access to endpoints existing in all APIs (e.g. `read:admin`) or provide access to an entire service (e.g. `read:sentiment`).


## Basic Usage

### Asynchronous Client

You can use the async client with the context manager protocol...
```python
async with AsyncClient(api_key="your-api-key") as client:
    await client.pay.products.get_products()
```
...or without it like this...
```python
client = AsyncClient(api_key="your-api-key")
asyncio.run(client.pay.products.get_products())
asyncio.run(client.close())
```
...or this.
```python
client = AsyncClient(api_key="your-api-key")

async def main():
    await client.pay.products.get_products()

asyncio.run(main())
asyncio.run(client.close())
```

### Synchronous Client

For traditional synchronous usage without async/await, use the `SyncClient`:

```python
from crypticorn import SyncClient

# With context manager (recommended)
with SyncClient(api_key="your-api-key") as client:
    products = client.pay.products.get_products()
    status = client.trade.status.ping()

# Or without context manager
client = SyncClient(api_key="your-api-key")
try:
    products = client.pay.products.get_products()
    status = client.trade.status.ping()
finally:
    client.close()  # Manual cleanup required
```

The sync client provides the same API surface as the async client, but all methods return results directly instead of coroutines. Under the hood, it uses `asgiref.async_to_sync` to bridge async operations to synchronous calls, ensuring reliable operation without requiring async/await syntax.

## Response Types

There are three different available output formats you can choose from:

### Serialized Response
You can get fully serialized responses as pydantic models. Using this, you get the full benefits of pydantic's type checking.
```python
# Async client
res = await client.pay.products.get_products()
# Sync client
res = client.pay.products.get_products()
print(res)
```
The output would look like this:
```python
[ProductModel(id='67e8146e7bae32f3838fe36a', name='Awesome Product', price=5.0, scopes=None, duration=30, description='You need to buy this', is_active=True)]
```

### Serialized Response with HTTP Info
```python
# Async client
res = await client.pay.products.get_products_with_http_info()
# Sync client
res = client.pay.products.get_products_with_http_info()
print(res)
```
The output would look like this:
```python
status_code=200 headers={'Date': 'Wed, 09 Apr 2025 19:15:19 GMT', 'Content-Type': 'application/json'} data=[ProductModel(id='67e8146e7bae32f3838fe36a', name='Awesome Product', price=5.0, scopes=None, duration=30, description='You need to buy this', is_active=True)] raw_data=b'[{"id":"67e8146e7bae32f3838fe36a","name":"Awesome Product","price":5.0,"duration":30,"description":"You need to buy this","is_active":true}]'
```
You can then access the data of the response (as serialized output (1) or as JSON string in bytes (2)) with:
```python
print(res.data)
print(res.raw_data)
```
On top of that you get some information about the request:
```python
print(res.status_code)
print(res.headers)
```

### JSON Response
You can receive a classical JSON response by suffixing the function name with `_without_preload_content`
```python
# Async client
response = await client.pay.products.get_products_without_preload_content()
print(await response.json())

# Sync client - Note: use regular methods instead as response.json() returns a coroutine
response = client.pay.products.get_products_without_preload_content()
```
The output would look like this:
```python
[{'id': '67e8146e7bae32f3838fe36a', 'name': 'Awesome Product', 'price': 5.0, 'duration': 30, 'description': 'You need to buy this', 'is_active': True}]
```

## Wrapper Utilities

Our SDK provides a collection of wrapper utilities designed to make interacting with the API more efficient and user-friendly.

### Data Preprocessing
Some API operations allow to get the returned data formatted as a pandas Dataframe. These operations are suffixed with `_fmt` and take the same inputs as the non-formatted function. They live alongside the other functions with the default [response types](#response-types). To use this functionality you have to install `pandas`, which is available in the [`extra` dependency group](#installation).

### Data Downloads
This utility allows direct data streaming to your local disk, instead of only returning download links. It is being used in the following functions:
- `client.hive.data.download_data()` (overrides the [default response](https://docs.crypticorn.com/api/?api=hive-ai-api#tag/data/GET/data))

## Advanced Usage

### Sub Client Configuration

You can override some configuration for specific services. If you just want to use the API as is, you don't need to configure anything.
This might be of use if you are testing a specific API locally.

To override e.g. the host for the Hive client to connect to localhost:8000 instead of the default proxy, you would do:
```python
from crypticorn.hive import Configuration as HiveConfig

# Async client
async with AsyncClient() as client:
    client.configure(config=HiveConfig(host="http://localhost:8000"), service='hive')

# Sync client
with SyncClient() as client:
    client.configure(config=HiveConfig(host="http://localhost:8000"), service='hive')
```

### Session Management

By default, `AsyncClient` manages a single shared `aiohttp.ClientSession` for all service wrappers.
However, you can pass your own pre-configured `aiohttp.ClientSession` if you need advanced control — for example, to add retries, custom headers, logging, or mocking behavior.

When you inject a custom session, you are responsible for managing its lifecycle, including closing when you're done.

```python
import aiohttp
from crypticorn import AsyncClient

async def main():
    custom_session = aiohttp.ClientSession()
    async with AsyncClient(api_key="your-key", http_client=custom_session) as client:
        await client.trade.status.ping()
    await custom_session.close()

```
If you don’t pass a session, `AsyncClient` will create and manage one internally. In that case, it will be automatically closed when using `async with` or when calling `await client.close()` manually.

**Note on Sync Client**: The `SyncClient` uses per-operation sessions (creates and closes a session for each API call) to ensure reliable synchronous behavior. Custom sessions are accepted but not used. This approach prevents event loop conflicts at the cost of slightly higher overhead per operation.
