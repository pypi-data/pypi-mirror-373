from __future__ import annotations

from typing import TYPE_CHECKING, Any, Coroutine, Optional, Union

from crypticorn._internal.utils import optional_import
from crypticorn.klines import (
    ApiClient,
    Configuration,
    FundingRatesApi,
    OHLCVDataApi,
    StatusApi,
    SymbolsApi,
    UDFApi,
)

try:
    import pandas as pd
except ImportError:
    pd = None

if TYPE_CHECKING:
    from aiohttp import ClientSession


class KlinesClient:
    """
    A client for interacting with the Crypticorn Klines API.
    """

    config_class = Configuration

    def __init__(
        self,
        config: Configuration,
        http_client: Optional[ClientSession] = None,
        is_sync: bool = False,
    ):
        self.config = config
        self.base_client = ApiClient(configuration=self.config)
        if http_client is not None:
            self.base_client.rest_client.pool_manager = http_client
        # Pass sync context to REST client for proper session management
        self.base_client.rest_client.is_sync = is_sync
        # Instantiate all the endpoint clients
        self.funding = FundingRatesApiWrapper(self.base_client, is_sync=is_sync)
        self.ohlcv = OHLCVDataApiWrapper(self.base_client, is_sync=is_sync)
        self.symbols = SymbolsApiWrapper(self.base_client, is_sync=is_sync)
        self.udf = UDFApi(self.base_client, is_sync=is_sync)
        self.status = StatusApi(self.base_client, is_sync=is_sync)


class FundingRatesApiWrapper(FundingRatesApi):
    """
    A wrapper for the FundingRatesApi class.
    """

    def get_funding_rates_fmt(
        self, *args, **kwargs
    ) -> Union["pd.DataFrame", Coroutine[Any, Any, "pd.DataFrame"]]:
        """
        Get the funding rates in a pandas DataFrame.
        Works in both sync and async contexts.
        """
        if self.is_sync:
            return self._get_funding_rates_fmt_sync(*args, **kwargs)
        else:
            return self._get_funding_rates_fmt_async(*args, **kwargs)

    def _get_funding_rates_fmt_sync(self, *args, **kwargs) -> "pd.DataFrame":
        """
        Get the funding rates in a pandas DataFrame (sync version).
        """
        pd = optional_import("pandas", "extra")
        response = self._get_funding_rates_sync(*args, **kwargs)
        result = [
            {
                "timestamp": int(m.timestamp.timestamp()),
                "symbol": m.symbol,
                "funding_rate": m.funding_rate,
            }
            for m in response
        ]
        return pd.DataFrame(result)

    async def _get_funding_rates_fmt_async(self, *args, **kwargs) -> "pd.DataFrame":
        """
        Get the funding rates in a pandas DataFrame (async version).
        """
        pd = optional_import("pandas", "extra")
        response = await self._get_funding_rates_async(*args, **kwargs)
        result = [
            {
                "timestamp": int(m.timestamp.timestamp()),
                "symbol": m.symbol,
                "funding_rate": m.funding_rate,
            }
            for m in response
        ]
        return pd.DataFrame(result)


class OHLCVDataApiWrapper(OHLCVDataApi):
    """
    A wrapper for the OHLCVDataApi class.
    """

    def get_ohlcv_data_fmt(
        self, *args, **kwargs
    ) -> Union["pd.DataFrame", Coroutine[Any, Any, "pd.DataFrame"]]:
        """
        Get the OHLCV data in a pandas DataFrame.
        Works in both sync and async contexts.
        """
        if self.is_sync:
            return self._get_ohlcv_data_fmt_sync(*args, **kwargs)
        else:
            return self._get_ohlcv_data_fmt_async(*args, **kwargs)

    def _get_ohlcv_data_fmt_sync(self, *args, **kwargs) -> "pd.DataFrame":  # noqa: F821
        """
        Get the OHLCV data in a pandas DataFrame (sync version).
        """
        pd = optional_import("pandas", "extra")
        response = self._get_ohlcv_sync(*args, **kwargs)
        rows = []
        for item in response:
            row = {
                "timestamp": item.timestamp,
                "open": item.open,
                "high": item.high,
                "low": item.low,
                "close": item.close,
                "volume": item.volume,
            }
            rows.append(row)
        df = pd.DataFrame(rows)
        return df

    async def _get_ohlcv_data_fmt_async(self, *args, **kwargs) -> "pd.DataFrame":
        """
        Get the OHLCV data in a pandas DataFrame (async version).
        """
        pd = optional_import("pandas", "extra")
        response = await self._get_ohlcv_async(*args, **kwargs)
        rows = []
        for item in response:
            row = {
                "timestamp": item.timestamp,
                "open": item.open,
                "high": item.high,
                "low": item.low,
                "close": item.close,
                "volume": item.volume,
            }
            rows.append(row)
        df = pd.DataFrame(rows)
        return df


class SymbolsApiWrapper(SymbolsApi):
    """
    A wrapper for the SymbolsApi class.
    """

    def get_symbols_fmt(
        self, *args, **kwargs
    ) -> Union["pd.DataFrame", Coroutine[Any, Any, "pd.DataFrame"]]:
        """
        Get the symbols in a pandas DataFrame.
        Works in both sync and async contexts.
        """
        if self.is_sync:
            return self._get_symbols_fmt_sync(*args, **kwargs)
        else:
            return self._get_symbols_fmt_async(*args, **kwargs)

    def _get_symbols_fmt_sync(self, *args, **kwargs) -> "pd.DataFrame":
        """
        Get the symbols in a pandas DataFrame (sync version).
        """
        pd = optional_import("pandas", "extra")
        response = self._get_klines_symbols_sync(*args, **kwargs)
        return pd.DataFrame(response, columns=["symbol"])

    async def _get_symbols_fmt_async(self, *args, **kwargs) -> "pd.DataFrame":
        """
        Get the symbols in a pandas DataFrame (async version).
        """
        pd = optional_import("pandas", "extra")
        response = await self._get_klines_symbols_async(*args, **kwargs)
        return pd.DataFrame(response, columns=["symbol"])
