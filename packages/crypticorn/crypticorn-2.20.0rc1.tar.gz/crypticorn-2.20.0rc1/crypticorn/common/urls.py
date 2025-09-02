from crypticorn.common.enums import ValidateEnumMixin

try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum


class ApiEnv(StrEnum):
    """The environment the API is being used with."""

    PROD = "prod"
    DEV = "dev"
    LOCAL = "local"
    DOCKER = "docker"


class BaseUrl(StrEnum):
    """The base URL to connect to the API."""

    PROD = "https://api.crypticorn.com"
    DEV = "https://api.crypticorn.dev"
    LOCAL = "http://localhost"
    DOCKER = "http://host.docker.internal"

    @classmethod
    def from_env(cls, env: ApiEnv) -> "BaseUrl":
        """Load the base URL from the API environment."""
        if env == ApiEnv.PROD:
            return cls.PROD
        elif env == ApiEnv.DEV:
            return cls.DEV
        elif env == ApiEnv.LOCAL:
            return cls.LOCAL
        elif env == ApiEnv.DOCKER:
            return cls.DOCKER


class ApiVersion(StrEnum):
    """Versions to use for the microservice APIs."""

    V1 = "v1"


class Service(ValidateEnumMixin, StrEnum):
    """The microservices available to connect to through the API"""

    HIVE = "hive"
    KLINES = "klines"
    PAY = "pay"
    TRADE = "trade"
    AUTH = "auth"
    METRICS = "metrics"
