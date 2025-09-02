import logging
import warnings

from crypticorn.client import ApiClient, AsyncClient, SyncClient
from crypticorn.common.logging import configure_logging

warnings.filterwarnings("default", "", DeprecationWarning)
configure_logging()
logging.captureWarnings(True)
# TODO: remove logging in next major release

__all__ = ["AsyncClient", "SyncClient", "ApiClient"]
