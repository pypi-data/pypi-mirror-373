from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from crypticorn.trade.client import (
    ApiClient,
    APIKeysApi,
    BotsApi,
    Configuration,
    ExchangesApi,
    NotificationsApi,
    OrdersApi,
    StatusApi,
    StrategiesApi,
    TradingActionsApi,
)

if TYPE_CHECKING:
    from aiohttp import ClientSession


class TradeClient:
    """
    A client for interacting with the Crypticorn Trade API.
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
        self.bots = BotsApi(self.base_client, is_sync=is_sync)
        self.exchanges = ExchangesApi(self.base_client, is_sync=is_sync)
        self.notifications = NotificationsApi(self.base_client, is_sync=is_sync)
        self.orders = OrdersApi(self.base_client, is_sync=is_sync)
        self.status = StatusApi(self.base_client, is_sync=is_sync)
        self.strategies = StrategiesApi(self.base_client, is_sync=is_sync)
        self.actions = TradingActionsApi(self.base_client, is_sync=is_sync)
        self.keys = APIKeysApi(self.base_client, is_sync=is_sync)
