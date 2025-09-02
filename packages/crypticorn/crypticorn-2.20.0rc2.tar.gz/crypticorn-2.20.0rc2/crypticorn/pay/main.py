from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from crypticorn.pay import (
    AccessApi,
    ApiClient,
    Configuration,
    CouponsApi,
    InvoicesApi,
    NOWPaymentsApi,
    PaymentsApi,
    ProductsApi,
    StatusApi,
    StripeApi,
    TokenApi,
)

if TYPE_CHECKING:
    from aiohttp import ClientSession


class PayClient:
    """
    A client for interacting with the Crypticorn Pay API.
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
        self.now = NOWPaymentsApi(self.base_client, is_sync=is_sync)
        self.status = StatusApi(self.base_client, is_sync=is_sync)
        self.payments = PaymentsApi(self.base_client, is_sync=is_sync)
        self.products = ProductsApi(self.base_client, is_sync=is_sync)
        self.coupons = CouponsApi(self.base_client, is_sync=is_sync)
        self.token = TokenApi(self.base_client, is_sync=is_sync)
        self.invoices = InvoicesApi(self.base_client, is_sync=is_sync)
        self.stripe = StripeApi(self.base_client, is_sync=is_sync)
        self.access = AccessApi(self.base_client, is_sync=is_sync)
