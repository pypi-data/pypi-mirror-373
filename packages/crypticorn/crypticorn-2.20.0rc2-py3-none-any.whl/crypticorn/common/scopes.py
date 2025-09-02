try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum


class Scope(StrEnum):
    """
    The permission scopes for the API.
    """

    # If you update anything here, also update the scopes in the auth-service repository

    WRITE_ADMIN = "write:admin"
    READ_ADMIN = "read:admin"

    # Scopes that can be purchased - these actually exist in the jwt token
    READ_PREDICTIONS = "read:predictions"
    READ_DEX_SIGNALS = "read:dex:signals"

    # Hive scopes
    READ_HIVE_MODEL = "read:hive:model"
    READ_HIVE_DATA = "read:hive:data"
    WRITE_HIVE_MODEL = "write:hive:model"

    # Trade scopes
    READ_TRADE_BOTS = "read:trade:bots"
    WRITE_TRADE_BOTS = "write:trade:bots"
    READ_TRADE_EXCHANGEKEYS = "read:trade:exchangekeys"
    WRITE_TRADE_EXCHANGEKEYS = "write:trade:exchangekeys"
    READ_TRADE_ORDERS = "read:trade:orders"
    READ_TRADE_ACTIONS = "read:trade:actions"
    WRITE_TRADE_ACTIONS = "write:trade:actions"
    READ_TRADE_EXCHANGES = "read:trade:exchanges"
    READ_TRADE_FUTURES = "read:trade:futures"
    WRITE_TRADE_FUTURES = "write:trade:futures"
    READ_TRADE_NOTIFICATIONS = "read:trade:notifications"
    WRITE_TRADE_NOTIFICATIONS = "write:trade:notifications"
    READ_TRADE_STRATEGIES = "read:trade:strategies"
    WRITE_TRADE_STRATEGIES = "write:trade:strategies"

    # Payment scopes
    READ_PAY_PAYMENTS = "read:pay:payments"
    READ_PAY_PRODUCTS = "read:pay:products"
    WRITE_PAY_PRODUCTS = "write:pay:products"
    READ_PAY_NOW = "read:pay:now"
    WRITE_PAY_NOW = "write:pay:now"
    WRITE_PAY_COUPONS = "write:pay:coupons"
    READ_PAY_COUPONS = "read:pay:coupons"

    # Metrics scopes
    READ_METRICS_MARKETCAP = "read:metrics:marketcap"
    READ_METRICS_INDICATORS = "read:metrics:indicators"
    READ_METRICS_EXCHANGES = "read:metrics:exchanges"
    READ_METRICS_TOKENS = "read:metrics:tokens"
    READ_METRICS_MARKETS = "read:metrics:markets"

    # Sentiment scopes
    READ_SENTIMENT = "read:sentiment"

    # Klines scopes
    READ_KLINES = "read:klines"

    @classmethod
    def admin_scopes(cls) -> list["Scope"]:
        """Scopes that are only available to admins."""
        return [
            cls.WRITE_TRADE_STRATEGIES,
            cls.WRITE_PAY_PRODUCTS,
            cls.WRITE_PAY_COUPONS,
            cls.WRITE_ADMIN,
            cls.READ_ADMIN,
        ]

    @classmethod
    def internal_scopes(cls) -> list["Scope"]:
        """Scopes that are only available to internal services."""
        return [
            cls.WRITE_TRADE_ACTIONS,
        ]

    @classmethod
    def purchaseable_scopes(cls) -> list["Scope"]:
        """Scopes that can be purchased."""
        return [
            cls.READ_PREDICTIONS,
            cls.READ_METRICS_MARKETCAP,
            cls.READ_METRICS_INDICATORS,
            cls.READ_METRICS_EXCHANGES,
            cls.READ_METRICS_TOKENS,
            cls.READ_METRICS_MARKETS,
            cls.READ_KLINES,
            cls.READ_SENTIMENT,
            cls.READ_DEX_SIGNALS,
        ]
