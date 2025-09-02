"""Defines common enumerations used throughout the codebase for type safety and consistency."""

try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum

import warnings

from crypticorn.common.mixins import ValidateEnumMixin
from crypticorn.common.warnings import CrypticornDeprecatedSince215


class Exchange(ValidateEnumMixin, StrEnum):
    """All exchanges used in the crypticorn ecosystem. Refer to the APIs for support for a specific usecase (data, trading, etc.)."""

    KUCOIN = "kucoin"
    BINGX = "bingx"
    BINANCE = "binance"
    BYBIT = "bybit"
    HYPERLIQUID = "hyperliquid"
    BITGET = "bitget"
    GATEIO = "gateio"
    BITSTAMP = "bitstamp"


class InternalExchange(ValidateEnumMixin, StrEnum):
    """All exchanges we are using, including public (Exchange)"""

    KUCOIN = "kucoin"
    BINGX = "bingx"
    BINANCE = "binance"
    BYBIT = "bybit"
    HYPERLIQUID = "hyperliquid"
    BITGET = "bitget"

    @classmethod
    def __getattr__(cls, name):
        warnings.warn(
            "The `InternalExchange` enum is deprecated; use `Exchange` instead.",
            category=CrypticornDeprecatedSince215,
        )
        return super().__getattr__(name)


class MarketType(ValidateEnumMixin, StrEnum):
    """
    Market types
    """

    SPOT = "spot"
    FUTURES = "futures"
