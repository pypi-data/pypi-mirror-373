"""
This module is deprecated and will be removed in a future release. The functionality has been moved to the 'crypticorn_utils' package,
however not all functionality will be kept and breaking changes will occur.
"""

# TODO: remove folder in next major release
import warnings

from crypticorn._internal.warnings import CrypticornDeprecatedSince219
from crypticorn.common.ansi_colors import *
from crypticorn.common.auth import *
from crypticorn.common.decorators import *
from crypticorn.common.enums import *
from crypticorn.common.errors import *
from crypticorn.common.exceptions import *
from crypticorn.common.logging import *
from crypticorn.common.middleware import *
from crypticorn.common.mixins import *
from crypticorn.common.openapi import *
from crypticorn.common.pagination import *
from crypticorn.common.router.admin_router import router as admin_router
from crypticorn.common.router.status_router import router as status_router
from crypticorn.common.scopes import *
from crypticorn.common.urls import *
from crypticorn.common.utils import *
from crypticorn.common.warnings import *

warnings.warn(
    """The 'crypticorn.common' module is deprecated and will be removed in a future release. The functionality has been moved to the 'crypticorn_utils' package,
    however not all functionality will be kept and breaking changes will occur.""",
    CrypticornDeprecatedSince219,
)
