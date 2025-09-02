import warnings

from crypticorn._internal.warnings import CrypticornDeprecatedSince219
from crypticorn.cli.init import init_group
from crypticorn.cli.version import version

__all__ = ["init_group", "version"]

warnings.warn(
    "The CLI is deprecated and will be removed in the next major release. To continue using the CLI, use the `crypticorn_utils` package.",
    CrypticornDeprecatedSince219,
)
# TODO: remove folder in next major release
